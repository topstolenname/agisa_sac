"""
Distributed Agent with GCP Integration

This module implements a sophisticated agent system that integrates
with Google Cloud Platform
services including Firestore, Pub/Sub, and Cloud Storage. It supports:
- LLM-based agent loops with tool execution
- Budget management for tokens, tools, and costs
- Guardrail enforcement
- Agent handoffs for task delegation
- Distributed coordination via Pub/Sub
- Persistent state in Firestore
"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

try:
    from google.cloud import firestore, pubsub_v1, storage
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode

    HAS_GCP = True
except ImportError:
    HAS_GCP = False
    firestore = None
    pubsub_v1 = None
    storage = None

    # Mock trace module
    class _MockTrace:
        @staticmethod
        def get_current_span():
            # Return a mock span object
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


# ───────────────────────── Data Models ─────────────────────────


class LoopExit(Enum):
    """Exit conditions for agent execution loop"""

    SATISFIED = "satisfied"
    MAX_ITERS = "max_iters"
    ERROR = "error"
    GUARDRAIL_BLOCK = "guardrail_block"
    HANDOFF = "handoff"


@dataclass
class LoopResult:
    """Result of an agent execution loop"""

    exit: LoopExit
    payload: dict[str, Any]
    iterations: int
    total_tokens: int = 0
    tool_calls: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class IntentionMessage:
    """Message broadcast to workspace about agent intentions"""

    run_id: str
    source_agent: str
    timestamp: str
    attention_weight: float
    payload: dict[str, Any]

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        import json

        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class ToolInvocation:
    """Record of a tool execution"""

    run_id: str
    agent_id: str
    tool: str
    args: dict[str, Any]
    risk_level: str

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        import json

        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class HandoffOffer:
    """Offer to hand off a task to another agent"""

    run_id: str
    from_agent: str
    to_capabilities: list[str]
    task_signature: dict[str, Any]
    context_ref: str
    expires_at: str

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        import json

        return json.dumps(self.__dict__).encode("utf-8")


class Budget:
    """Rate limiter and budget manager for agent resources"""

    def __init__(
        self,
        max_tokens_per_run: int = 100000,
        max_tools_per_minute: int = 60,
        max_daily_cost: float = 100.0,
    ):
        self.max_tokens_per_run = max_tokens_per_run
        self.max_tools_per_minute = max_tools_per_minute
        self.max_daily_cost = max_daily_cost

        self.tokens_used = 0
        self.tools_used = 0
        self.cost_used = 0.0
        self.last_tool_refill = datetime.now(timezone.utc)

    def check_tokens(self, estimated: int) -> bool:
        """Check if token budget allows the request"""
        return self.tokens_used + estimated <= self.max_tokens_per_run

    def consume_tokens(self, amount: int):
        """Consume token budget"""
        self.tokens_used += amount

    def check_tools(self) -> bool:
        """Check if tool rate limit allows execution"""
        return self.tools_used < self.max_tools_per_minute

    def consume_tool(self):
        """Consume tool budget"""
        self.tools_used += 1

    def check_cost(self, estimated: float) -> bool:
        """Check if cost budget allows the operation"""
        return self.cost_used + estimated <= self.max_daily_cost

    def consume_cost(self, amount: float):
        """Consume cost budget"""
        self.cost_used += amount


# ───────────────────────── Main Agent Class ─────────────────────────


if HAS_GCP:
    tracer = trace.get_tracer(__name__)
else:
    # Mock tracer for when GCP is not available
    from functools import wraps

    class MockSpan:
        def set_status(self, status):
            pass

        def record_exception(self, e):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class MockTracerContextManager:
        """Context manager wrapper for mock tracer."""

        def __init__(self, name):
            self.name = name
            self.span = MockSpan()

        def __enter__(self):
            return self.span

        def __exit__(self, *args):
            pass

        def __call__(self, func):
            """Support decorator usage."""
            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self:
                        return await func(*args, **kwargs)

                return async_wrapper
            else:

                @wraps(func)
                def wrapper(*args, **kwargs):
                    with self:
                        return func(*args, **kwargs)

                return wrapper

    class MockTracer:
        def start_as_current_span(self, name):
            """Mock span that works as both decorator and context manager."""
            return MockTracerContextManager(name)

    tracer = MockTracer()


class DistributedAgent:
    """
    A distributed agent that integrates with GCP services for persistence,
    messaging, and coordination.
    """

    def __init__(
        self,
        agent_id: str,
        instructions: str,
        model: str = "gpt-4",
        tools: dict[str, Any] | None = None,
        project_id: str | None = None,
        workspace_topic: str | None = None,
        budget: Budget | None = None,
    ):
        """
        Initialize the distributed agent.

        Args:
            agent_id: Unique identifier for this agent
            instructions: System instructions for the agent
            model: LLM model to use
            tools: Dictionary of available tools
            project_id: GCP project ID
            workspace_topic: Pub/Sub topic for workspace communication
            budget: Budget manager instance
        """
        if not HAS_GCP:
            raise ImportError(
                "google-cloud-firestore, google-cloud-pubsub, and "
                "google-cloud-storage are required for DistributedAgent"
            )

        self.agent_id = agent_id
        self.instructions = instructions
        self.model = model
        self.tools = tools or {}
        self.project_id = project_id
        self.workspace_topic = workspace_topic
        self.budget = budget or Budget()

        # Initialize GCP clients
        self.db = firestore.Client(project=project_id)
        self.publisher = pubsub_v1.PublisherClient()
        self.storage_client = storage.Client(project=project_id)

        # State
        self.interaction_history: list[dict[str, Any]] = []
        self._broadcast_tokens = 10
        self._last_broadcast_refill = datetime.now(timezone.utc)

    def _refill_broadcast_bucket(self):
        """Refill broadcast token bucket for rate limiting"""
        now = datetime.now(timezone.utc)
        elapsed = (now - self._last_broadcast_refill).total_seconds()
        refill_rate = 1.0 / 60.0  # 1 token per minute
        refill = int(elapsed * refill_rate)
        if refill > 0:
            self._broadcast_tokens = min(10, self._broadcast_tokens + refill)
            self._last_broadcast_refill = now

    # ───────────────────────── Public API ─────────────────────────

    @tracer.start_as_current_span("agent_run")
    async def run(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        guardrails: dict[str, Any] | None = None,
    ) -> LoopResult:
        """
        Execute the agent with the given message and context.

        Args:
            message: User message/request
            context: Execution context including llm_client
            guardrails: Optional guardrail configuration

        Returns:
            LoopResult with execution outcome
        """
        span = trace.get_current_span()
        context = context or {}
        run_id = context.get(
            "run_id", hashlib.sha256(message.encode()).hexdigest()[:16]
        )
        context["run_id"] = run_id

        # Create run document in Firestore
        run_ref = self.db.collection("agent_runs").document(run_id)
        run_ref.set(
            {
                "agent_id": self.agent_id,
                "start_ts": firestore.SERVER_TIMESTAMP,
                "status": "running",
                "message": message[:500],
            }
        )

        try:
            # Optional guardrail check
            if guardrails:
                result = await self._check_guardrails(message, context, guardrails)
                if result.get("block"):
                    return await self._handle_guardrail_violation(result, run_ref)

            # Execute main loop
            loop_result = await self._execute_loop(message, context)

            # Broadcast satisfaction if successful
            if self.workspace_topic and loop_result.exit == LoopExit.SATISFIED:
                await self._maybe_broadcast_intention(
                    run_id=run_id,
                    intention={
                        "type": "run_satisfied",
                        "summary": loop_result.payload.get("summary", ""),
                        "outputs": loop_result.payload.get("outputs", {}),
                    },
                    weight=loop_result.payload.get("attention_weight", 0.75),
                )

            # Persist run result
            run_ref.update(
                {
                    "end_ts": firestore.SERVER_TIMESTAMP,
                    "status": loop_result.exit.value,
                    "iterations": loop_result.iterations,
                    "tool_calls": loop_result.tool_calls,
                    "total_tokens": loop_result.total_tokens,
                    "errors": loop_result.errors,
                    "payload": loop_result.payload,
                }
            )
            span.set_status(Status(StatusCode.OK))
            return loop_result

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            run_ref.update(
                {
                    "end_ts": firestore.SERVER_TIMESTAMP,
                    "status": "error",
                    "errors": [str(e)],
                }
            )
            return LoopResult(
                exit=LoopExit.ERROR, payload={"error": str(e)}, iterations=0
            )

    # ───────────────────────── internal helpers ─────────────────────────

    async def _check_guardrails(
        self, message: str, context: dict[str, Any], guardrails: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Check message against guardrails.

        Returns dict with 'block' key indicating if execution should be blocked.
        """
        # Placeholder implementation - actual guardrail logic would go here
        return {"block": False}

    async def _handle_guardrail_violation(self, result: dict[str, Any], run_ref):
        """Persist guardrail block and return standardized LoopResult"""
        detail = {
            "reason": result.get("reason", "guardrail_block"),
            "risk_level": result.get("risk_level", "high"),
            "violations": result.get("violations", []),
            "metadata": result.get("metadata", {}),
        }
        run_ref.update(
            {
                "end_ts": firestore.SERVER_TIMESTAMP,
                "status": "guardrail_block",
                "guardrail": detail,
            }
        )
        return LoopResult(exit=LoopExit.GUARDRAIL_BLOCK, payload=detail, iterations=0)

    def _record_interaction(self, entry: dict[str, Any]):
        """Append lightweight interaction row to Firestore + in-memory history"""
        self.interaction_history.append(entry)
        # Also write a compact row into Firestore for topology processing
        self.db.collection("interactions").add(
            {**entry, "agent_id": self.agent_id, "ts": firestore.SERVER_TIMESTAMP}
        )

    async def _maybe_broadcast_intention(
        self, run_id: str, intention: dict[str, Any], weight: float
    ):
        """Rate-limited global broadcast"""
        self._refill_broadcast_bucket()
        if self._broadcast_tokens <= 0:
            return
        self._broadcast_tokens -= 1

        message = IntentionMessage(
            run_id=run_id,
            source_agent=self.agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            attention_weight=weight,
            payload=intention,
        )
        topic = self.publisher.topic_path(self.project_id, self.workspace_topic)
        self.publisher.publish(topic, message.to_pubsub())

    # ───────────────────────── agent loop ─────────────────────────

    @tracer.start_as_current_span("agent_execute_loop")
    async def _execute_loop(self, message: str, context: dict[str, Any]) -> LoopResult:
        """
        OpenAI-style loop:
          - call model
          - execute tools (budgeted)
          - optional handoff
          - exit when objective is satisfied or limit reached
        """
        max_iterations = context.get("max_iterations", 20)
        iteration = 0
        total_tokens = 0
        tool_calls = 0
        errors: list[str] = []

        # Require an llm client (injected) to decouple infra
        llm = context.get("llm_client")
        if llm is None:
            return LoopResult(
                exit=LoopExit.ERROR,
                payload={"error": "Missing llm_client in context"},
                iterations=0,
            )

        working_ctx = dict(context)
        working_ctx.setdefault("messages", [])
        working_ctx["messages"].append({"role": "system", "content": self.instructions})
        working_ctx["messages"].append({"role": "user", "content": message})

        while iteration < max_iterations:
            # Budget: token prediction (coarse) before call; enforce post-hoc too
            est_tokens = self._estimate_tokens(working_ctx["messages"])
            if not self.budget.check_tokens(est_tokens):
                return LoopResult(
                    exit=LoopExit.ERROR,
                    payload={"error": "Token budget exceeded"},
                    iterations=iteration,
                    total_tokens=total_tokens,
                    tool_calls=tool_calls,
                    errors=errors,
                )

            # LLM call
            try:
                llm_resp = await self._call_model(llm, working_ctx)
            except Exception as e:
                errors.append(f"llm_call_failed: {e}")
                return LoopResult(
                    exit=LoopExit.ERROR,
                    payload={"error": "LLM call failed"},
                    iterations=iteration,
                    total_tokens=total_tokens,
                    tool_calls=tool_calls,
                    errors=errors,
                )

            used_tokens = llm_resp.get("usage", {}).get("total_tokens", est_tokens)
            self.budget.consume_tokens(used_tokens)
            total_tokens += used_tokens

            # Exit condition?
            if self._should_exit(llm_resp):
                payload = {
                    "outputs": llm_resp.get("content", {}),
                    "summary": llm_resp.get("summary", ""),
                }
                return LoopResult(
                    exit=LoopExit.SATISFIED,
                    payload=payload,
                    iterations=iteration + 1,
                    total_tokens=total_tokens,
                    tool_calls=tool_calls,
                    errors=errors,
                )

            # Tools
            if llm_resp.get("tool_calls"):
                if not self.budget.check_tools():
                    errors.append("tool_rate_limited")
                    return LoopResult(
                        exit=LoopExit.ERROR,
                        payload={"error": "Tool rate limit exceeded"},
                        iterations=iteration + 1,
                        total_tokens=total_tokens,
                        tool_calls=tool_calls,
                        errors=errors,
                    )

                try:
                    results, tool_invocations = await self._execute_tools(
                        llm_resp["tool_calls"], context=working_ctx
                    )
                    tool_calls += len(tool_invocations)
                    self.budget.consume_tool()
                except Exception as e:
                    errors.append(f"tool_exec_failed: {e}")
                    return LoopResult(
                        exit=LoopExit.ERROR,
                        payload={"error": "Tool execution failed"},
                        iterations=iteration + 1,
                        total_tokens=total_tokens,
                        tool_calls=tool_calls,
                        errors=errors,
                    )

                # Feed results back to the model
                working_ctx["messages"].append(
                    {
                        "role": "tool",
                        "name": "batched_results",
                        "content": self._format_tool_results(results),
                    }
                )
                continue  # next iteration

            # Handoff
            handoff = llm_resp.get("handoff_target")
            if handoff:
                offer_id = await self._emit_handoff_offer(
                    run_id=context["run_id"],
                    task_signature=self._task_signature_from_ctx(working_ctx),
                    to_capabilities=handoff.get("required_capabilities", []),
                    context_ref=await self._persist_context_blob(working_ctx),
                    ttl_seconds=handoff.get("ttl_seconds", 300),
                )
                return LoopResult(
                    exit=LoopExit.HANDOFF,
                    payload={
                        "offer_id": offer_id,
                        "to_capabilities": handoff.get("required_capabilities", []),
                    },
                    iterations=iteration + 1,
                    total_tokens=total_tokens,
                    tool_calls=tool_calls,
                    errors=errors,
                )

            # Default: continue conversation with assistant content if any
            assistant_msg = llm_resp.get("content")
            if assistant_msg:
                working_ctx["messages"].append(
                    {"role": "assistant", "content": assistant_msg}
                )

            iteration += 1

        # Exceeded iterations
        return LoopResult(
            exit=LoopExit.MAX_ITERS,
            payload={
                "last_message": (
                    working_ctx["messages"][-1] if working_ctx["messages"] else {}
                )
            },
            iterations=iteration,
            total_tokens=total_tokens,
            tool_calls=tool_calls,
            errors=errors,
        )

    # ───────────────────────── model / tools / handoff ─────────────────────────

    async def _call_model(self, llm_client, ctx: dict[str, Any]) -> dict[str, Any]:
        """
        Contract for llm_client:
          await llm_client({
            "model": self.model,
            "messages": [...],             # OpenAI-style messages
            "tools": [ {... mcp tool ...} ],
          }) -> {
            "content": str | dict,
            "tool_calls": [ {"name": str, "arguments": dict}, ... ]?,
            "handoff_target": {"required_capabilities": [...], "ttl_seconds": int}?,
            "usage": {"total_tokens": int}?
          }
        """
        tool_defs = [self.tools[t].to_mcp_format() for t in self.tools]
        req = {"model": self.model, "messages": ctx["messages"], "tools": tool_defs}
        return await llm_client(req)

    async def _execute_tools(
        self, tool_calls: list[dict[str, Any]], context: dict[str, Any]
    ):
        results = []
        invocations = []
        for call in tool_calls:
            name = call.get("name")
            args = call.get("arguments", {})
            tool = self.tools.get(name)
            if not tool:
                results.append({"tool": name, "error": "unknown_tool"})
                continue

            # Optional per-call cost estimation gate (you can wire real costers here)
            est_cost = 0.0
            if not self.budget.check_cost(est_cost):
                results.append({"tool": name, "error": "daily_cost_exceeded"})
                continue

            # Persist invocation row (Pub/Sub for audit)
            inv = ToolInvocation(
                run_id=context.get("run_id", ""),
                agent_id=self.agent_id,
                tool=name,
                args=args,
                risk_level=tool.risk_level,
            )
            topic = self.publisher.topic_path(
                self.project_id, f"{self.workspace_topic or 'global-workspace'}-tools"
            )
            self.publisher.publish(topic, inv.to_pubsub())
            invocations.append(inv.__dict__)

            # Execute
            try:
                out = await self._maybe_await(tool.function(**args))
                results.append({"tool": name, "ok": True, "result": out})
                self.budget.consume_cost(est_cost)
            except Exception as e:
                results.append({"tool": name, "ok": False, "error": str(e)})

        return results, invocations

    async def _emit_handoff_offer(
        self,
        run_id: str,
        task_signature: dict[str, Any],
        to_capabilities: list[str],
        context_ref: str,
        ttl_seconds: int = 300,
    ) -> str:
        offer = HandoffOffer(
            run_id=run_id,
            from_agent=self.agent_id,
            to_capabilities=to_capabilities,
            task_signature=task_signature,
            context_ref=context_ref,
            expires_at=(
                datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            ).isoformat(),
        )
        topic = self.publisher.topic_path(
            self.project_id, f"{self.workspace_topic or 'global-workspace'}-handoff"
        )
        future = self.publisher.publish(topic, offer.to_pubsub())
        offer_id = await self._await_pubsub_id(future)
        # Store in Firestore for stateful coordination
        self.db.collection("handoff_offers").document(offer_id).set(
            {**offer.__dict__, "created_at": firestore.SERVER_TIMESTAMP}
        )
        return offer_id

    async def _persist_context_blob(self, ctx: dict[str, Any]) -> str:
        """Persist a compact context snapshot to GCS and return gs:// URI"""
        bucket_name = f"{self.project_id}-agent-context"
        bucket = self.storage_client.bucket(bucket_name)
        blob_id = hashlib.sha256(str(ctx).encode("utf-8")).hexdigest()[:32]
        blob = bucket.blob(f"runs/{ctx.get('run_id', 'unknown')}/{blob_id}.json")

        import json

        data = {
            "agent_id": self.agent_id,
            "model": self.model,
            "messages": ctx.get("messages", [])[-20:],  # tail only
        }
        blob.upload_from_string(json.dumps(data), content_type="application/json")
        return f"gs://{bucket_name}/{blob.name}"

    async def _await_pubsub_id(self, future) -> str:
        # pubsub future has .result() blocking call; wrap in thread pool
        loop = asyncio.get_running_loop()
        msg_id = await loop.run_in_executor(None, future.result)
        return str(msg_id)

    def _task_signature_from_ctx(self, ctx: dict[str, Any]) -> dict[str, Any]:
        last_user = next(
            (m for m in reversed(ctx["messages"]) if m["role"] == "user"), {}
        )
        return {
            "hash": hashlib.sha256(str(last_user).encode("utf-8")).hexdigest()[:16],
            "hint": (last_user.get("content", "") or "")[:180],
        }

    def _should_exit(self, llm_resp: dict[str, Any]) -> bool:
        # Exit if model indicates completion and no tool/handoff is requested
        done = llm_resp.get("done") is True
        no_more = not llm_resp.get("tool_calls") and not llm_resp.get("handoff_target")
        return bool(done and no_more)

    def _format_tool_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        return {"batched_tool_results": results}

    async def _maybe_await(self, x):
        if asyncio.iscoroutine(x):
            return await x
        return x

    def _estimate_tokens(self, messages: list[dict[str, Any]]) -> int:
        # Conservative heuristic (~4 chars/token)
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return max(1, total_chars // 4)
