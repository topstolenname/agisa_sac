"""Tests for AGISAAgent and ResourceBudget (agents/base_agent.py).

Covers:
- ResourceBudget: token/tool/cost tracking and limits
- AGISAAgent initialization (mocked GCP deps)
- Agent categorization and state management
- Error handling and budget enforcement
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from agisa_sac.agents.base_agent import ResourceBudget
from agisa_sac.types.contracts import Tool, ToolType


class TestResourceBudget:
    """Tests for ResourceBudget class."""

    def test_budget_initialization(self):
        """Test budget initializes with correct defaults."""
        budget = ResourceBudget()
        assert budget.max_tokens_per_min == 10000
        assert budget.max_tools_per_min == 50
        assert budget.max_cost_per_day == 10.0

    def test_budget_custom_limits(self):
        """Test budget with custom limits."""
        budget = ResourceBudget(
            max_tokens_per_min=5000,
            max_tools_per_min=25,
            max_cost_per_day=20.0,
        )
        assert budget.max_tokens_per_min == 5000
        assert budget.max_tools_per_min == 25
        assert budget.max_cost_per_day == 20.0

    def test_check_tokens_within_limit(self):
        """Test token check succeeds when within limit."""
        budget = ResourceBudget(max_tokens_per_min=1000)
        assert budget.check_tokens(500) is True

    def test_check_tokens_exceeds_limit(self):
        """Test token check fails when exceeding limit."""
        budget = ResourceBudget(max_tokens_per_min=1000)
        budget.consume_tokens(600)
        assert budget.check_tokens(500) is False

    def test_check_tokens_at_limit(self):
        """Test token check at exact limit."""
        budget = ResourceBudget(max_tokens_per_min=1000)
        budget.consume_tokens(1000)
        assert budget.check_tokens(1) is False

    def test_consume_tokens_tracks_usage(self):
        """Test token consumption is tracked."""
        budget = ResourceBudget(max_tokens_per_min=1000)
        budget.consume_tokens(300)
        budget.consume_tokens(200)

        # Should have consumed 500 tokens
        assert budget.check_tokens(501) is False
        assert budget.check_tokens(500) is True

    def test_check_tools_within_limit(self):
        """Test tool check succeeds when within limit."""
        budget = ResourceBudget(max_tools_per_min=10)
        assert budget.check_tools() is True

    def test_check_tools_at_limit(self):
        """Test tool check fails at limit."""
        budget = ResourceBudget(max_tools_per_min=3)
        for _ in range(3):
            budget.consume_tool()
        assert budget.check_tools() is False

    def test_consume_tool_tracks_usage(self):
        """Test tool consumption is tracked."""
        budget = ResourceBudget(max_tools_per_min=5)
        budget.consume_tool()
        assert budget.check_tools() is True
        budget.consume_tool()
        budget.consume_tool()
        budget.consume_tool()
        assert budget.check_tools() is True  # 4 tools, still under limit
        budget.consume_tool()
        assert budget.check_tools() is False  # 5 tools, at limit

    def test_check_cost_within_limit(self):
        """Test cost check succeeds when within daily limit."""
        budget = ResourceBudget(max_cost_per_day=10.0)
        assert budget.check_cost(5.0) is True

    def test_check_cost_exceeds_limit(self):
        """Test cost check fails when exceeding limit."""
        budget = ResourceBudget(max_cost_per_day=10.0)
        budget.consume_cost(8.0)
        assert budget.check_cost(3.0) is False

    def test_consume_cost_tracks_usage(self):
        """Test cost consumption is tracked."""
        budget = ResourceBudget(max_cost_per_day=10.0)
        budget.consume_cost(3.5)
        budget.consume_cost(2.5)

        # Should have consumed $6
        assert budget.check_cost(4.5) is False
        assert budget.check_cost(4.0) is True

    @patch("agisa_sac.agents.base_agent.datetime")
    def test_token_window_cleanup(self, mock_datetime):
        """Test that old token entries are cleaned up."""
        budget = ResourceBudget(max_tokens_per_min=1000)

        # Set initial time
        initial_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = initial_time

        # Consume tokens
        budget.consume_tokens(500)

        # Advance time past 1 minute
        mock_datetime.now.return_value = initial_time + timedelta(minutes=2)

        # Old tokens should be cleaned up, so we should have full budget
        assert budget.check_tokens(1000) is True

    @patch("agisa_sac.agents.base_agent.datetime")
    def test_tool_window_cleanup(self, mock_datetime):
        """Test that old tool entries are cleaned up."""
        budget = ResourceBudget(max_tools_per_min=5)

        # Set initial time
        initial_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = initial_time

        # Consume all tools
        for _ in range(5):
            budget.consume_tool()

        # Advance time past 1 minute
        mock_datetime.now.return_value = initial_time + timedelta(minutes=2)

        # Old tools should be cleaned up
        assert budget.check_tools() is True

    @patch("agisa_sac.agents.base_agent.datetime")
    def test_daily_cost_reset(self, mock_datetime_module):
        """Test that daily cost resets at midnight."""
        # Mock both datetime class and datetime instances
        day1 = datetime(2024, 1, 1, 12, 0, 0)
        day2 = datetime(2024, 1, 2, 0, 0, 1)

        # Setup mock to return our datetimes
        mock_datetime_module.now.return_value = day1

        budget = ResourceBudget(max_cost_per_day=10.0)

        # Consume most of daily budget
        budget.consume_cost(9.0)
        assert budget.check_cost(2.0) is False

        # Advance to next day
        mock_datetime_module.now.return_value = day2

        # Should reset and allow full budget again
        assert budget.check_cost(10.0) is True

    @patch("agisa_sac.agents.base_agent.datetime")
    def test_combined_budget_enforcement(self, mock_datetime_module):
        """Test all budget types together."""
        mock_datetime_module.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

        budget = ResourceBudget(
            max_tokens_per_min=100,
            max_tools_per_min=2,
            max_cost_per_day=1.0,
        )

        # Use some of each resource
        budget.consume_tokens(50)
        budget.consume_tool()
        budget.consume_cost(0.5)

        # All should still be within limits
        assert budget.check_tokens(50) is True
        assert budget.check_tools() is True
        assert budget.check_cost(0.5) is True

        # Exceed each limit
        budget.consume_tokens(51)  # Total 101 > 100
        budget.consume_tool()  # Total 2 >= 2
        budget.consume_cost(0.6)  # Total 1.1 > 1.0

        assert budget.check_tokens(1) is False
        assert budget.check_tools() is False
        assert budget.check_cost(0.1) is False


# Tests for AGISAAgent require GCP mocking
class TestAGISAAgentToolCategorization:
    """Tests for tool categorization (doesn't require GCP)."""

    @pytest.mark.skipif(
        "not config.getoption('--run-gcp-tests', default=False)",
        reason="Requires GCP dependencies or --run-gcp-tests flag",
    )
    @patch("agisa_sac.agents.base_agent.HAS_GCP", True)
    @patch("agisa_sac.agents.base_agent.firestore")
    @patch("agisa_sac.agents.base_agent.pubsub_v1")
    @patch("agisa_sac.agents.base_agent.storage")
    def test_categorize_tools_empty(self, mock_storage, mock_pubsub, mock_firestore):
        """Test categorize_tools with no tools."""
        from agisa_sac.agents.base_agent import AGISAAgent

        agent = AGISAAgent(
            agent_id="test_agent",
            name="Test Agent",
            instructions="Test instructions",
            tools=[],
        )

        categories = agent.categorize_tools()

        assert ToolType.COMMUNICATION in categories
        assert ToolType.OBSERVATION in categories
        assert ToolType.ACTION in categories
        assert all(len(tools) == 0 for tools in categories.values())

    @pytest.mark.skipif(
        "not config.getoption('--run-gcp-tests', default=False)",
        reason="Requires GCP dependencies or --run-gcp-tests flag",
    )
    @patch("agisa_sac.agents.base_agent.HAS_GCP", True)
    @patch("agisa_sac.agents.base_agent.firestore")
    @patch("agisa_sac.agents.base_agent.pubsub_v1")
    @patch("agisa_sac.agents.base_agent.storage")
    def test_categorize_tools_mixed(self, mock_storage, mock_pubsub, mock_firestore):
        """Test categorize_tools with mixed tool types."""
        from agisa_sac.agents.base_agent import AGISAAgent

        tools = [
            Tool(
                name="broadcast",
                type=ToolType.COMMUNICATION,
                description="Broadcast message",
            ),
            Tool(
                name="observe",
                type=ToolType.OBSERVATION,
                description="Observe environment",
            ),
            Tool(name="act", type=ToolType.ACTION, description="Take action"),
        ]

        agent = AGISAAgent(
            agent_id="test_agent",
            name="Test Agent",
            instructions="Test instructions",
            tools=tools,
        )

        categories = agent.categorize_tools()

        assert len(categories[ToolType.COMMUNICATION]) == 1
        assert len(categories[ToolType.OBSERVATION]) == 1
        assert len(categories[ToolType.ACTION]) == 1


class TestAGISAAgentInitialization:
    """Tests for AGISAAgent initialization."""

    @pytest.mark.skipif(
        "not config.getoption('--run-gcp-tests', default=False)",
        reason="Requires GCP dependencies or --run-gcp-tests flag",
    )
    @patch("agisa_sac.agents.base_agent.HAS_GCP", True)
    @patch("agisa_sac.agents.base_agent.firestore")
    @patch("agisa_sac.agents.base_agent.pubsub_v1")
    @patch("agisa_sac.agents.base_agent.storage")
    def test_initialization_basic(self, mock_storage, mock_pubsub, mock_firestore):
        """Test basic AGISAAgent initialization."""
        from agisa_sac.agents.base_agent import AGISAAgent

        agent = AGISAAgent(
            agent_id="test_001",
            name="Test Agent",
            instructions="Test instructions for the agent",
            tools=[],
        )

        assert agent.agent_id == "test_001"
        assert agent.name == "Test Agent"
        assert agent.instructions == "Test instructions for the agent"
        assert agent.model == "gpt-4o-mini"
        assert agent.budget is not None

    @pytest.mark.skipif(
        "not config.getoption('--run-gcp-tests', default=False)",
        reason="Requires GCP dependencies or --run-gcp-tests flag",
    )
    @patch("agisa_sac.agents.base_agent.HAS_GCP", True)
    @patch("agisa_sac.agents.base_agent.firestore")
    @patch("agisa_sac.agents.base_agent.pubsub_v1")
    @patch("agisa_sac.agents.base_agent.storage")
    def test_initialization_with_custom_budget(
        self, mock_storage, mock_pubsub, mock_firestore
    ):
        """Test initialization with custom budget."""
        from agisa_sac.agents.base_agent import AGISAAgent

        custom_budget = ResourceBudget(
            max_tokens_per_min=5000,
            max_tools_per_min=25,
            max_cost_per_day=5.0,
        )

        agent = AGISAAgent(
            agent_id="test_002",
            name="Custom Budget Agent",
            instructions="Test",
            tools=[],
            budget=custom_budget,
        )

        assert agent.budget is custom_budget
        assert agent.budget.max_tokens_per_min == 5000

    @pytest.mark.skipif(
        "not config.getoption('--run-gcp-tests', default=False)",
        reason="Requires GCP dependencies or --run-gcp-tests flag",
    )
    @patch("agisa_sac.agents.base_agent.HAS_GCP", True)
    @patch("agisa_sac.agents.base_agent.firestore")
    @patch("agisa_sac.agents.base_agent.pubsub_v1")
    @patch("agisa_sac.agents.base_agent.storage")
    def test_initialization_sets_defaults(
        self, mock_storage, mock_pubsub, mock_firestore
    ):
        """Test that initialization sets sensible defaults."""
        from agisa_sac.agents.base_agent import AGISAAgent

        agent = AGISAAgent(
            agent_id="test_003",
            name="Default Test",
            instructions="Test",
            tools=[],
        )

        # Check default values
        assert agent.workspace_topic == "global-workspace.intentions.v1"
        assert agent.handoff_offers_topic == "agents.handoff.offers.v1"
        assert agent.tool_invocations_topic == "agents.tool.invocations.v1"
        assert agent.enable_topology is True
        assert agent.project_id == "agisa-sac-prod"

    def test_initialization_fails_without_gcp(self):
        """Test that initialization fails gracefully without GCP deps."""
        with patch("agisa_sac.agents.base_agent.HAS_GCP", False):
            from agisa_sac.agents.base_agent import AGISAAgent

            with pytest.raises(ImportError) as exc_info:
                AGISAAgent(
                    agent_id="test",
                    name="Test",
                    instructions="Test",
                    tools=[],
                )

            assert "google-cloud" in str(exc_info.value).lower()
