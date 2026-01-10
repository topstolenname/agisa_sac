"""Tests for the DistributedAgent implementation"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if GCP dependencies are not available
pytest.importorskip("google.cloud.firestore")
pytest.importorskip("google.cloud.pubsub_v1")
pytest.importorskip("google.cloud.storage")
pytest.importorskip("opentelemetry")

from agisa_sac.gcp.distributed_agent import (
    Budget,
    DistributedAgent,
    HandoffOffer,
    IntentionMessage,
    LoopExit,
    LoopResult,
    ToolInvocation,
)


class TestBudget:
    """Tests for Budget class"""

    def test_budget_initialization(self):
        budget = Budget(
            max_tokens_per_run=1000, max_tools_per_minute=10, max_daily_cost=50.0
        )
        assert budget.max_tokens_per_run == 1000
        assert budget.max_tools_per_minute == 10
        assert budget.max_daily_cost == 50.0
        assert budget.tokens_used == 0
        assert budget.tools_used == 0
        assert budget.cost_used == 0.0

    def test_check_and_consume_tokens(self):
        budget = Budget(max_tokens_per_run=1000)
        assert budget.check_tokens(500) is True
        budget.consume_tokens(500)
        assert budget.tokens_used == 500
        assert budget.check_tokens(600) is False

    def test_check_and_consume_tools(self):
        budget = Budget(max_tools_per_minute=5)
        assert budget.check_tools() is True
        for _ in range(5):
            budget.consume_tool()
        assert budget.check_tools() is False

    def test_check_and_consume_cost(self):
        budget = Budget(max_daily_cost=100.0)
        assert budget.check_cost(50.0) is True
        budget.consume_cost(50.0)
        assert budget.cost_used == 50.0
        assert budget.check_cost(60.0) is False


class TestDataModels:
    """Tests for data model classes"""

    def test_loop_result(self):
        result = LoopResult(
            exit=LoopExit.SATISFIED,
            payload={"test": "data"},
            iterations=5,
            total_tokens=100,
            tool_calls=3,
            errors=["error1"],
        )
        assert result.exit == LoopExit.SATISFIED
        assert result.payload == {"test": "data"}
        assert result.iterations == 5
        assert result.total_tokens == 100
        assert result.tool_calls == 3
        assert result.errors == ["error1"]

    def test_intention_message_serialization(self):
        msg = IntentionMessage(
            run_id="test-run",
            source_agent="agent-1",
            timestamp="2024-01-01T00:00:00",
            attention_weight=0.8,
            payload={"type": "test"},
        )
        serialized = msg.to_pubsub()
        assert isinstance(serialized, bytes)
        assert b"test-run" in serialized

    def test_tool_invocation_serialization(self):
        inv = ToolInvocation(
            run_id="test-run",
            agent_id="agent-1",
            tool="test_tool",
            args={"arg1": "value1"},
            risk_level="low",
        )
        serialized = inv.to_pubsub()
        assert isinstance(serialized, bytes)
        assert b"test_tool" in serialized

    def test_handoff_offer_serialization(self):
        offer = HandoffOffer(
            run_id="test-run",
            from_agent="agent-1",
            to_capabilities=["cap1", "cap2"],
            task_signature={"hash": "abc123"},
            context_ref="gs://bucket/context.json",
            expires_at="2024-01-01T00:05:00",
        )
        serialized = offer.to_pubsub()
        assert isinstance(serialized, bytes)
        assert b"agent-1" in serialized


class TestDistributedAgent:
    """Tests for DistributedAgent class"""

    @pytest.fixture
    def mock_gcp_clients(self):
        """Mock GCP client dependencies"""
        with (
            patch("agisa_sac.gcp.distributed_agent.firestore") as mock_firestore,
            patch("agisa_sac.gcp.distributed_agent.pubsub_v1") as mock_pubsub,
            patch("agisa_sac.gcp.distributed_agent.storage") as mock_storage,
        ):
            # Setup mock Firestore
            mock_db = MagicMock()
            mock_firestore.Client.return_value = mock_db

            # Setup mock Pub/Sub
            mock_publisher = MagicMock()
            mock_pubsub.PublisherClient.return_value = mock_publisher

            # Setup mock Storage
            mock_storage_client = MagicMock()
            mock_storage.Client.return_value = mock_storage_client

            yield {
                "db": mock_db,
                "publisher": mock_publisher,
                "storage": mock_storage_client,
            }

    @pytest.fixture
    def agent(self, mock_gcp_clients):
        """Create a test agent instance"""
        return DistributedAgent(
            agent_id="test-agent",
            instructions="Test instructions",
            model="gpt-4",
            tools={},
            project_id="test-project",
            workspace_topic="test-workspace",
        )

    def test_agent_initialization(self, agent):
        assert agent.agent_id == "test-agent"
        assert agent.instructions == "Test instructions"
        assert agent.model == "gpt-4"
        assert agent.project_id == "test-project"
        assert agent.workspace_topic == "test-workspace"
        assert isinstance(agent.budget, Budget)
        assert agent.interaction_history == []

    def test_broadcast_token_refill(self, agent):
        """Test that broadcast tokens are refilled over time"""
        agent._broadcast_tokens = 0
        initial_time = datetime.now(timezone.utc)
        # Mock time passing

        with patch("agisa_sac.gcp.distributed_agent.datetime") as mock_dt:
            mock_dt.now.return_value = initial_time
            agent._last_broadcast_refill = initial_time

            # Simulate 2 minutes passing
            from datetime import timedelta

            future_time = initial_time + timedelta(minutes=2)
            mock_dt.now.return_value = future_time

            agent._refill_broadcast_bucket()
            assert agent._broadcast_tokens == 2

    def test_estimate_tokens(self, agent):
        messages = [
            {"role": "user", "content": "a" * 400},  # ~100 tokens
            {"role": "assistant", "content": "b" * 400},  # ~100 tokens
        ]
        tokens = agent._estimate_tokens(messages)
        assert tokens == 200  # 800 chars / 4

    def test_task_signature_from_ctx(self, agent):
        ctx = {
            "messages": [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "test message"},
                {"role": "assistant", "content": "response"},
            ]
        }
        sig = agent._task_signature_from_ctx(ctx)
        assert "hash" in sig
        assert "hint" in sig
        assert sig["hint"] == "test message"

    def test_should_exit_true(self, agent):
        llm_resp = {"done": True, "content": "Final answer"}
        assert agent._should_exit(llm_resp) is True

    def test_should_exit_false_with_tools(self, agent):
        llm_resp = {"done": True, "tool_calls": [{"name": "test"}]}
        assert agent._should_exit(llm_resp) is False

    def test_should_exit_false_with_handoff(self, agent):
        llm_resp = {"done": True, "handoff_target": {"capabilities": ["cap1"]}}
        assert agent._should_exit(llm_resp) is False

    def test_format_tool_results(self, agent):
        results = [
            {"tool": "tool1", "ok": True, "result": "output1"},
            {"tool": "tool2", "ok": False, "error": "failed"},
        ]
        formatted = agent._format_tool_results(results)
        assert "batched_tool_results" in formatted
        assert formatted["batched_tool_results"] == results

    @pytest.mark.asyncio
    async def test_maybe_await_with_coroutine(self, agent):
        async def async_func():
            return "async_result"

        result = await agent._maybe_await(async_func())
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_maybe_await_with_value(self, agent):
        result = await agent._maybe_await("sync_result")
        assert result == "sync_result"

    def test_record_interaction(self, agent, mock_gcp_clients):
        entry = {"type": "test", "timestamp": "2024-01-01"}
        mock_collection = MagicMock()
        mock_gcp_clients["db"].collection.return_value = mock_collection

        agent._record_interaction(entry)

        assert len(agent.interaction_history) == 1
        assert agent.interaction_history[0] == entry
        mock_collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_guardrail_violation(self, agent, mock_gcp_clients):
        mock_run_ref = MagicMock()
        result = {
            "reason": "prohibited_content",
            "risk_level": "high",
            "violations": ["violence"],
            "metadata": {"score": 0.9},
        }

        loop_result = await agent._handle_guardrail_violation(result, mock_run_ref)

        assert loop_result.exit == LoopExit.GUARDRAIL_BLOCK
        assert loop_result.payload["reason"] == "prohibited_content"
        assert loop_result.payload["risk_level"] == "high"
        mock_run_ref.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_loop_missing_llm_client(self, agent):
        result = await agent._execute_loop("test message", {})
        assert result.exit == LoopExit.ERROR
        assert "Missing llm_client" in result.payload["error"]

    @pytest.mark.asyncio
    async def test_execute_loop_token_budget_exceeded(self, agent):
        agent.budget = Budget(max_tokens_per_run=10)  # Very low budget

        async def mock_llm_client(req):
            return {"content": "test", "usage": {"total_tokens": 100}}

        context = {"llm_client": mock_llm_client, "max_iterations": 5}
        result = await agent._execute_loop("test" * 100, context)  # Long message

        assert result.exit == LoopExit.ERROR
        assert "Token budget exceeded" in result.payload["error"]

    @pytest.mark.asyncio
    async def test_execute_loop_satisfied(self, agent):
        async def mock_llm_client(req):
            return {
                "done": True,
                "content": {"answer": "42"},
                "summary": "Task completed",
                "usage": {"total_tokens": 50},
            }

        context = {
            "llm_client": mock_llm_client,
            "max_iterations": 5,
            "run_id": "test-run",
        }
        result = await agent._execute_loop("What is the answer?", context)

        assert result.exit == LoopExit.SATISFIED
        assert result.iterations == 1
        assert result.total_tokens == 50

    @pytest.mark.asyncio
    async def test_execute_loop_max_iterations(self, agent):
        call_count = 0

        async def mock_llm_client(req):
            nonlocal call_count
            call_count += 1
            return {
                "done": False,
                "content": f"iteration {call_count}",
                "usage": {"total_tokens": 10},
            }

        context = {
            "llm_client": mock_llm_client,
            "max_iterations": 3,
            "run_id": "test-run",
        }
        result = await agent._execute_loop("test", context)

        assert result.exit == LoopExit.MAX_ITERS
        assert result.iterations == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
