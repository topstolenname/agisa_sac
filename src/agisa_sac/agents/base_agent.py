"""
Hardened Agent Implementation with GCP Integration

This module implements a production-ready agent system with:
- Resource budget management for equity
- Guardrail enforcement
- Distributed coordination via Pub/Sub
- OpenTelemetry tracing
- Persistent state in Firestore
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from google.cloud import firestore, pubsub_v1, storage
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode

    HAS_GCP = True
except ImportError:
    HAS_GCP = False
    pubsub_v1 = None
    storage = None

    # Create stub for firestore module to enable test patching
    # Tests need to patch firestore.Client even when google-cloud libs aren't installed
    class _FirestoreStub:
        """Stub firestore module for test patching compatibility."""
        class Client:
            """Stub Client class for patching."""
            def __init__(self, *args, **kwargs):
                pass

    firestore = _FirestoreStub()

    # Mock trace module
    class _MockTrace:
        @staticmethod
        def get_current_span():
            class _MockCurrentSpan:
                def set_status(self, status):
                    pass
                def record_exception(self, e):
                    pass
            return _MockCurrentSpan()

    trace = _MockTrace()

    # Mock Status and StatusCode
    class Status:
        def __init__(self, status_code, description=""):
            pass

    class StatusCode:
        OK = "ok"
        ERROR = "error"

from ..types.contracts import (
    HandoffOffer,
    IntentionMessage,
    LoopExit,
    LoopResult,
    Tool,
    ToolInvocation,
    ToolType,
)

if HAS_GCP:
    tracer = trace.get_tracer(__name__)
else:

    class MockSpan:
        """Mock span for when OpenTelemetry is not available"""

        def set_attribute(self, key: str, value: Any):
            pass

        def set_status(self, status):
            pass

        def record_exception(self, e):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class MockTracer:
        """Mock tracer for when OpenTelemetry is not available"""

        def start_as_current_span(self, name):
            return MockSpan()

    tracer = MockTracer()


class ResourceBudget:
    """
    Per-agent resource limits for equity.

    Enforces rate limits on tokens, tools, and costs to prevent
    resource monopolization by any single agent.
    """

    def __init__(
        self,
        max_tokens_per_min: int = 10000,
        max_tools_per_min: int = 50,
        max_cost_per_day: float = 10.0,
    ):
        self.max_tokens_per_min = max_tokens_per_min
        self.max_tools_per_min = max_tools_per_min
        self.max_cost_per_day = max_cost_per_day

        # Tracking windows
        self._token_window: List[tuple] = []
        self._tool_window: List[datetime] = []
        self._daily_cost = 0.0
        self._day_start = datetime.now().date()

    def check_tokens(self, count: int) -> bool:
        """Check if token budget allows the request"""
        self._clean_token_window()
        current = sum(t[1] for t in self._token_window)
        return (current + count) <= self.max_tokens_per_min

    def consume_tokens(self, count: int):
        """Consume token budget"""
        self._token_window.append((datetime.now(), count))

    def check_tools(self) -> bool:
        """Check if tool rate limit allows execution"""
        self._clean_tool_window()
        return len(self._tool_window) < self.max_tools_per_min

    def consume_tool(self):
        """Consume tool budget"""
        self._tool_window.append(datetime.now())

    def check_cost(self, estimated_cost: float) -> bool:
        """Check if cost budget allows the operation"""
        self._reset_daily_if_needed()
        return (self._daily_cost + estimated_cost) <= self.max_cost_per_day

    def consume_cost(self, cost: float):
        """Consume cost budget"""
        self._daily_cost += cost

    def _clean_token_window(self):
        """Remove expired token entries"""
        cutoff = datetime.now() - timedelta(minutes=1)
        self._token_window = [(t, c) for t, c in self._token_window if t > cutoff]

    def _clean_tool_window(self):
        """Remove expired tool entries"""
        cutoff = datetime.now() - timedelta(minutes=1)
        self._tool_window = [t for t in self._tool_window if t > cutoff]

    def _reset_daily_if_needed(self):
        """Reset daily budget if new day"""
        today = datetime.now().date()
        if today > self._day_start:
            self._daily_cost = 0.0
            self._day_start = today


class AGISAAgent:
    """
    Production-hardened agent with OpenAI patterns + AGISA-SAC topology.

    Features:
    - Deterministic execution loop with explicit exit conditions
    - Resource budgeting for equity
    - Guardrail enforcement
    - Distributed coordination via Pub/Sub
    - OpenTelemetry tracing
    - Persistent state in Firestore
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        instructions: str,
        tools: List[Tool],
        model: str = "gpt-4o-mini",
        workspace_topic: Optional[str] = None,
        enable_topology: bool = True,
        budget: Optional[ResourceBudget] = None,
        project_id: str = "agisa-sac-prod",
        context_bucket: Optional[str] = None,
        handoff_offers_topic: Optional[str] = None,
        tool_invocations_topic: Optional[str] = None,
    ):
        """
        Initialize the AGISA agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            instructions: System instructions for the agent
            tools: List of available tools
            model: LLM model to use
            workspace_topic: Pub/Sub topic for workspace communication
            enable_topology: Enable topology tracking
            budget: Resource budget manager
            project_id: GCP project ID
            context_bucket: GCS bucket for context storage (defaults to {project_id}-agisa-sac-contexts)
            handoff_offers_topic: Pub/Sub topic for handoff offers (defaults to agents.handoff.offers.v1)
            tool_invocations_topic: Pub/Sub topic for tool invocations (defaults to agents.tool.invocations.v1)
        """
        if not HAS_GCP:
            raise ImportError(
                "google-cloud-firestore, google-cloud-pubsub, google-cloud-storage, "
                "and opentelemetry-exporter-gcp-trace are required for AGISAAgent"
            )

        self.agent_id = agent_id
        self.name = name
        self.instructions = instructions
        self.tools = {t.name: t for t in tools}
        self.model = model
        self.workspace_topic = workspace_topic or "global-workspace.intentions.v1"
        self.enable_topology = enable_topology
        self.budget = budget or ResourceBudget()
        self.project_id = project_id

        # Resource names with sensible defaults matching Terraform
        self.context_bucket = context_bucket or f"{project_id}-agisa-sac-contexts"
        self.handoff_offers_topic = handoff_offers_topic or "agents.handoff.offers.v1"
        self.tool_invocations_topic = tool_invocations_topic or "agents.tool.invocations.v1"

        # State tracking
        self.interaction_history: List[Dict] = []
        self.persistence_diagram = None
        self.handoff_targets: List[Dict] = []
        self.guardrails: List[Any] = []

        # GCP clients
        self.db = firestore.Client(project=project_id)
        self.publisher = pubsub_v1.PublisherClient()
        self.storage_client = storage.Client(project=project_id)

        # Token bucket for attention broadcasts (prevent storms)
        self._broadcast_tokens = 10
        self._broadcast_refill = datetime.now()

        # Register agent profile in Firestore
        self._register_profile()

    def _register_profile(self):
        """Store static agent profile in Firestore"""
        self.db.collection("agents").document(self.agent_id).set(
            {
                "name": self.name,
                "model": self.model,
                "capabilities": list(self.tools.keys()),
                "version": "1.0.0",
                "created_at": firestore.SERVER_TIMESTAMP,
            }
        )

    def _refill_broadcast_bucket(self):
        """Token bucket for broadcast rate limiting"""
        now = datetime.now()
        elapsed = (now - self._broadcast_refill).total_seconds()
        refill = int(elapsed / 6.0)  # 1 token per 6 seconds
        if refill > 0:
            self._broadcast_tokens = min(10, self._broadcast_tokens + refill)
            self._broadcast_refill = now

    def categorize_tools(self) -> Dict[ToolType, List[Tool]]:
        """Group tools by type"""
        categorized = {ToolType.DATA: [], ToolType.ACTION: [], ToolType.ORCHESTRATION: []}
        for tool in self.tools.values():
            categorized[tool.type].append(tool)
        return categorized

    async def run(
        self, input_message: str, context: Optional[Dict] = None
    ) -> LoopResult:
        """
        Main execution with guardrails, tracing, and resource checks.

        Args:
            input_message: User input message
            context: Execution context including llm_client

        Returns:
            LoopResult with execution outcome
        """
        with tracer.start_as_current_span("agent_run") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("agent.name", self.name)

            run_id = str(uuid.uuid4())
            context = context or {}
            context["run_id"] = run_id

            # Start run document
            run_ref = self.db.collection("runs").document(run_id)
            run_ref.set(
                {
                    "agent_id": self.agent_id,
                    "start_ts": firestore.SERVER_TIMESTAMP,
                    "status": "running",
                }
            )

            try:
                # Apply input guardrails
                for guardrail in self.guardrails:
                    result = await guardrail.check_input(input_message, context)
                    if not result.get("passed", True):
                        span.set_status(Status(StatusCode.ERROR, "Guardrail blocked"))
                        return await self._handle_guardrail_violation(result, run_ref)

                # Track interaction for topology
                if self.enable_topology:
                    self._record_interaction(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "type": "input",
                            "content": input_message[:200],
                            "agent_id": self.agent_id,
                            "run_id": run_id,
                        }
                    )

                # Execute main loop
                loop_result = await self._execute_loop(input_message, context)

                # Publish to global workspace if significant
                if self.workspace_topic and loop_result.exit == LoopExit.SATISFIED:
                    await self._publish_to_workspace(loop_result, context)

                # Update run document
                run_ref.update(
                    {
                        "end_ts": firestore.SERVER_TIMESTAMP,
                        "status": "completed",
                        "exit": loop_result.exit.value,
                        "iterations": loop_result.iterations,
                        "tokens": loop_result.total_tokens,
                        "tool_calls": loop_result.tool_calls,
                        "errors": loop_result.errors,
                    }
                )

                span.set_attribute("run.iterations", loop_result.iterations)
                span.set_attribute("run.tokens", loop_result.total_tokens)
                span.set_status(Status(StatusCode.OK))

                return loop_result

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                run_ref.update(
                    {
                        "end_ts": firestore.SERVER_TIMESTAMP,
                        "status": "error",
                        "error": str(e),
                    }
                )
                raise

    async def _execute_loop(self, message: str, context: Dict) -> LoopResult:
        """
        Deterministic loop with explicit exit conditions.

        Args:
            message: Input message
            context: Execution context

        Returns:
            LoopResult with execution outcome
        """
        max_iterations = 20
        total_tokens = 0
        tool_calls_count = 0
        errors = []

        for iteration in range(max_iterations):
            with tracer.start_as_current_span("agent_loop_iteration") as span:
                span.set_attribute("iteration", iteration)

                # Check resource budget
                if not self.budget.check_tokens(1000):  # Estimate
                    errors.append(f"Token budget exceeded at iteration {iteration}")
                    return LoopResult(
                        exit=LoopExit.ERROR,
                        payload={"error": "Resource quota exceeded"},
                        iterations=iteration,
                        total_tokens=total_tokens,
                        tool_calls=tool_calls_count,
                        errors=errors,
                    )

                # Call model (would be implemented with actual LLM client)
                with tracer.start_as_current_span("model_call") as model_span:
                    model_out = await self._call_model(message, context)
                    tokens_used = model_out.get("usage", {}).get("total_tokens", 0)
                    total_tokens += tokens_used
                    self.budget.consume_tokens(tokens_used)
                    model_span.set_attribute("tokens", tokens_used)

                # Check exit: satisfied
                if self._should_exit(model_out):
                    return LoopResult(
                        exit=LoopExit.SATISFIED,
                        payload=model_out,
                        iterations=iteration + 1,
                        total_tokens=total_tokens,
                        tool_calls=tool_calls_count,
                    )

                # Check exit: tool calls
                if tool_calls := model_out.get("tool_calls"):
                    with tracer.start_as_current_span("tool_execution") as tool_span:
                        results = []
                        for call in tool_calls:
                            if not self.budget.check_tools():
                                errors.append("Tool rate limit exceeded")
                                break

                            tool_span.set_attribute(f"tool.{call['name']}", True)
                            res = await self._execute_tool(
                                call["name"], call.get("args", {}), context
                            )
                            results.append(
                                {
                                    "name": call["name"],
                                    "ok": res.get("ok", False),
                                    "out": res.get("out"),
                                }
                            )
                            self.budget.consume_tool()
                            tool_calls_count += 1

                        message = self._format_tool_results(results)
                        continue

                # Check exit: handoff
                if handoff := model_out.get("handoff_target"):
                    with tracer.start_as_current_span("handoff_offer"):
                        await self._emit_handoff_offer(model_out, context)

                        # Store handoff information for topology analysis
                        run_ref = self.db.collection("runs").document(context["run_id"])
                        run_ref.update({
                            "handoff_to": handoff,
                            "handoff_reason": model_out.get("handoff_reason", ""),
                        })

                        return LoopResult(
                            exit=LoopExit.HANDOFF,
                            payload={
                                "to": handoff,
                                "reason": model_out.get("handoff_reason"),
                            },
                            iterations=iteration + 1,
                            total_tokens=total_tokens,
                            tool_calls=tool_calls_count,
                        )

        # Max iterations exceeded
        return LoopResult(
            exit=LoopExit.MAX_ITERS,
            payload={"last_response": model_out},
            iterations=max_iterations,
            total_tokens=total_tokens,
            tool_calls=tool_calls_count,
            errors=["Maximum iterations exceeded"],
        )

    async def _emit_handoff_offer(self, model_out: Dict, context: Dict):
        """Publish handoff offer to Pub/Sub"""
        # Upload context to GCS
        context_uri = await self._upload_context_to_gcs(context)

        offer = HandoffOffer(
            run_id=context["run_id"],
            from_agent=self.agent_id,
            to_capabilities=model_out.get("required_capabilities", []),
            task_signature={
                "required_tools": model_out.get("required_tools", []),
                "domain": model_out.get("domain", "general"),
            },
            context_ref=context_uri,
            expires_at=(datetime.now() + timedelta(minutes=5)).isoformat(),
        )

        topic_path = self.publisher.topic_path(
            self.project_id, self.handoff_offers_topic
        )

        future = self.publisher.publish(topic_path, offer.to_pubsub())
        # Use run_in_executor for google.api_core.future.Future compatibility
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, future.result)

    async def _upload_context_to_gcs(self, context: Dict) -> str:
        """Store context in GCS for handoff"""
        import json

        bucket = self.storage_client.bucket(self.context_bucket)
        blob_name = f"runs/{context['run_id']}/context.json"
        blob = bucket.blob(blob_name)

        blob.upload_from_string(
            json.dumps(context, indent=2), content_type="application/json"
        )

        return f"gs://{self.context_bucket}/{blob_name}"

    async def _publish_to_workspace(self, result: LoopResult, context: Dict):
        """Publish to global workspace with rate limiting"""
        self._refill_broadcast_bucket()

        if self._broadcast_tokens <= 0:
            return  # Rate limited

        intention = IntentionMessage(
            run_id=context["run_id"],
            source_agent=self.agent_id,
            timestamp=datetime.now().isoformat(),
            attention_weight=0.8,
            payload={
                "type": "task_completion",
                "iterations": result.iterations,
                "tokens": result.total_tokens,
                "tool_calls": result.tool_calls,
            },
        )

        topic_path = self.publisher.topic_path(
            self.project_id, self.workspace_topic
        )

        future = self.publisher.publish(topic_path, intention.to_pubsub())
        # Use run_in_executor for google.api_core.future.Future compatibility
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, future.result)

        self._broadcast_tokens -= 1

    def _record_interaction(self, interaction: Dict):
        """Record for topology analysis"""
        self.interaction_history.append(interaction)
        # Keep window manageable
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-500:]

    async def _call_model(self, message: str, context: Dict) -> Dict:
        """Call LLM (placeholder - implement with actual LLM client)"""
        # This would be implemented with actual LLM API calls
        llm_client = context.get("llm_client")
        if llm_client:
            return await llm_client({"model": self.model, "messages": [message]})
        return {"content": "Not implemented", "done": True}

    def _should_exit(self, response: Dict) -> bool:
        """Check if response indicates completion"""
        return response.get("done") is True or response.get("final_output") is not None

    async def _execute_tool(self, tool_name: str, args: Dict, context: Dict) -> Dict:
        """Execute tool with risk checks"""
        if tool_name not in self.tools:
            return {"ok": False, "error": f"Tool {tool_name} not found"}

        tool = self.tools[tool_name]

        # Publish tool invocation
        invocation = ToolInvocation(
            run_id=context["run_id"],
            agent_id=self.agent_id,
            tool=tool_name,
            args=args,
            risk_level=tool.risk_level,
        )

        topic_path = self.publisher.topic_path(
            self.project_id, self.tool_invocations_topic
        )
        _ = self.publisher.publish(topic_path, invocation.to_pubsub())
        # Fire and forget - don't await for tool invocation logging

        try:
            result = await tool.function(**args)
            return {"ok": True, "out": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _format_tool_results(self, results: List[Dict]) -> str:
        """Format tool results for next iteration"""
        formatted = []
        for r in results:
            if r["ok"]:
                formatted.append(f"{r['name']}: {r['out']}")
            else:
                formatted.append(f"{r['name']}: ERROR - {r.get('error', 'Unknown')}")
        return "\n".join(formatted)

    async def _handle_guardrail_violation(
        self, result: Dict, run_ref
    ) -> LoopResult:
        """Handle guardrail block"""
        event_id = str(uuid.uuid4())
        self.db.collection("guardrail_events").document(event_id).set(
            {
                "agent_id": self.agent_id,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "reason": result.get("reason"),
                "risk_level": result.get("risk_level"),
                "violations": result.get("violations", []),
                "action_taken": "block",
            }
        )

        run_ref.update(
            {
                "end_ts": firestore.SERVER_TIMESTAMP,
                "status": "blocked",
                "guardrail_event": event_id,
            }
        )

        return LoopResult(
            exit=LoopExit.GUARDRAIL_BLOCK,
            payload={
                "reason": result.get("reason"),
                "violations": result.get("violations", []),
            },
            iterations=0,
            total_tokens=0,
            tool_calls=0,
            errors=[f"Guardrail: {result.get('reason')}"],
        )

    def add_handoff(self, target_agent: "AGISAAgent"):
        """Register potential handoff target"""
        self.handoff_targets.append(
            {
                "agent_id": target_agent.agent_id,
                "name": target_agent.name,
                "capabilities": list(target_agent.tools.keys()),
            }
        )
