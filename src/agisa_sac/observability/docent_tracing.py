"""Docent-style tracing integration for AGI-SAC.

This module provides LLM call tracing capabilities integrated with the existing
OpenTelemetry infrastructure. It follows the graceful degradation pattern used
throughout the AGI-SAC codebase.
"""

from __future__ import annotations

import time
import warnings
from contextlib import contextmanager
from typing import Any, Dict, Optional
from agisa_sac import FRAMEWORK_VERSION
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Graceful degradation for OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.trace import Span
    HAS_OPENTELEMETRY = True
except ImportError:
    HAS_OPENTELEMETRY = False
    # Mock Span class
    class Span:
        def set_attribute(self, key: str, value: Any) -> None:
            pass

        def add_event(self, name: str, attributes: Optional[Dict] = None) -> None:
            pass

        def set_status(self, status: Any) -> None:
            pass


class DocentTracer:
    """Wrapper for LLM tracing with OpenTelemetry integration.

    Provides a simple interface for tracing LLM calls with research-specific
    metadata collection. Integrates with existing OpenTelemetry setup when
    available, falls back to logging when not.

    Attributes:
        collection_name: Name of the trace collection (e.g., "aim-1-emergent-coordination")
        enable_research_metrics: Whether to collect research-specific metadata
        enabled: Whether tracing is actually enabled
    """

    def __init__(
        self,
        collection_name: str = "agisa-sac-traces",
        enable_research_metrics: bool = False,
    ):
        """Initialize the Docent tracer.

        Args:
            collection_name: Name for this trace collection
            enable_research_metrics: Enable collection of research-specific metrics
        """
        self.collection_name = collection_name
        self.enable_research_metrics = enable_research_metrics
        self.enabled = HAS_OPENTELEMETRY

        if HAS_OPENTELEMETRY:
            self.tracer = trace.get_tracer(__name__)
            logger.info(
                "Docent tracer initialized with OpenTelemetry",
                extra={"collection": collection_name},
            )
        else:
            self.tracer = None
            logger.warning(
                "OpenTelemetry not available, tracing disabled. "
                "Install agisa-sac[tracing] for full tracing support."
            )

    @contextmanager
    def trace_llm_call(
        self,
        operation_name: str = "llm_call",
        **attributes: Any,
    ):
        """Context manager for tracing an LLM call.

        Args:
            operation_name: Name of the operation being traced
            **attributes: Additional attributes to attach to the span

        Yields:
            TracedLLMCall: Object for recording call results

        Example:
            ```python
            with tracer.trace_llm_call(
                "claude_completion",
                agent_id="agent-001",
                model="claude-sonnet-4-5"
            ) as call:
                result = await client.messages.create(...)
                call.record_result(
                    tokens_used=result.usage.total_tokens,
                    response_content=result.content[0].text
                )
            ```
        """
        start_time = time.time()
        span = None

        if self.enabled and self.tracer:
            span = self.tracer.start_span(operation_name)
            # Add standard attributes
            span.set_attribute("collection_name", self.collection_name)
            span.set_attribute("framework_version", FRAMEWORK_VERSION)
            for key, value in attributes.items():
                span.set_attribute(key, value)

        call = TracedLLMCall(span, start_time, self.enable_research_metrics)

        try:
            yield call
        except Exception as e:
            if span:
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
            logger.error(
                f"Error in {operation_name}",
                exc_info=True,
                extra={"collection": self.collection_name},
            )
            raise
        finally:
            duration = time.time() - start_time
            if span:
                span.set_attribute("duration_ms", duration * 1000)
                span.end()

    def trace_epoch(self, epoch: int, **attributes: Any):
        """Context manager for tracing a full simulation epoch.

        Args:
            epoch: Epoch number
            **attributes: Additional attributes

        Example:
            ```python
            with tracer.trace_epoch(5, num_agents=20) as epoch_span:
                # Run epoch logic
                pass
            ```
        """
        return self.trace_llm_call(
            operation_name="simulation_epoch",
            epoch=epoch,
            **attributes
        )


class TracedLLMCall:
    """Container for recording LLM call results within a trace span.

    This class is yielded by DocentTracer.trace_llm_call() and provides
    methods to record call results and research-specific metadata.
    """

    def __init__(
        self,
        span: Optional[Span],
        start_time: float,
        enable_research_metrics: bool = False,
    ):
        """Initialize traced call container.

        Args:
            span: OpenTelemetry span (or None if tracing disabled)
            start_time: Call start timestamp
            enable_research_metrics: Whether to collect research metrics
        """
        self.span = span
        self.start_time = start_time
        self.enable_research_metrics = enable_research_metrics
        self.metadata: Dict[str, Any] = {}

    def record_result(
        self,
        tokens_used: Optional[int] = None,
        response_content: Optional[str] = None,
        model: Optional[str] = None,
        **additional_attributes: Any,
    ) -> None:
        """Record the result of an LLM call.

        Args:
            tokens_used: Total tokens consumed
            response_content: Response text (will be truncated for storage)
            model: Model identifier
            **additional_attributes: Any other attributes to record
        """
        if self.span:
            if tokens_used is not None:
                self.span.set_attribute("usage.total_tokens", tokens_used)

            if model:
                self.span.set_attribute("model", model)

            if response_content:
                # Store truncated content
                max_len = 500
                truncated = (
                    response_content[:max_len]
                    if len(response_content) > max_len
                    else response_content
                )
                self.span.set_attribute("response.content_preview", truncated)
                self.span.set_attribute("response.content_length", len(response_content))

            for key, value in additional_attributes.items():
                self.span.set_attribute(key, value)

        # Also store in metadata for potential export
        self.metadata.update({
            "tokens_used": tokens_used,
            "model": model,
            "response_length": len(response_content) if response_content else 0,
            **additional_attributes,
        })

    def record_research_metadata(
        self,
        control_condition: Optional[bool] = None,
        peer_influence: Optional[float] = None,
        reputation_score: Optional[float] = None,
        constraint_violations: Optional[int] = None,
        **additional_metadata: Any,
    ) -> None:
        """Record research-specific metadata.

        Args:
            control_condition: Whether this is a control run (Aim 1)
            peer_influence: Peer influence value (Aim 1)
            reputation_score: Agent's reputation score (Aim 2)
            constraint_violations: Number of constraint violations (Aim 3)
            **additional_metadata: Any other research metadata
        """
        if not self.enable_research_metrics:
            return

        if self.span:
            if control_condition is not None:
                self.span.set_attribute("research.control_condition", control_condition)

            if peer_influence is not None:
                self.span.set_attribute("research.peer_influence", peer_influence)

            if reputation_score is not None:
                self.span.set_attribute("research.reputation_score", reputation_score)

            if constraint_violations is not None:
                self.span.set_attribute(
                    "research.constraint_violations", constraint_violations
                )

            for key, value in additional_metadata.items():
                self.span.set_attribute(f"research.{key}", value)

        # Store in metadata
        research_meta = {
            "control_condition": control_condition,
            "peer_influence": peer_influence,
            "reputation_score": reputation_score,
            "constraint_violations": constraint_violations,
            **additional_metadata,
        }
        self.metadata["research"] = {k: v for k, v in research_meta.items() if v is not None}

    def add_event(self, event_name: str, **attributes: Any) -> None:
        """Add a timestamped event to the trace.

        Args:
            event_name: Name of the event
            **attributes: Event attributes
        """
        if self.span:
            self.span.add_event(event_name, attributes=attributes)


def setup_docent_tracing(
    collection_name: str = "agisa-sac-traces",
    enable_research_metrics: bool = False,
) -> DocentTracer:
    """Initialize Docent tracing for the simulation.

    This function creates a DocentTracer instance with the specified configuration.
    If OpenTelemetry is not available, it returns a tracer that will log warnings.

    Args:
        collection_name: Name for this trace collection
        enable_research_metrics: Enable research-specific metric collection

    Returns:
        DocentTracer: Configured tracer instance

    Example:
        ```python
        # In your simulation setup
        tracer = setup_docent_tracing(
            collection_name="aim-1-emergent-coordination",
            enable_research_metrics=True
        )

        # Later, in your agent code
        with tracer.trace_llm_call("agent_decision", agent_id="agent-001") as call:
            result = await llm_client(request)
            call.record_result(tokens_used=result.usage.total_tokens)
            call.record_research_metadata(
                control_condition=False,
                peer_influence=0.7
            )
        ```
    """
    if not HAS_OPENTELEMETRY:
        warnings.warn(
            "OpenTelemetry not installed. Tracing will be disabled. "
            "Install with: pip install agisa-sac[tracing]",
            category=UserWarning,
        )

    return DocentTracer(
        collection_name=collection_name,
        enable_research_metrics=enable_research_metrics,
    )


__all__ = [
    "DocentTracer",
    "TracedLLMCall",
    "setup_docent_tracing",
    "HAS_OPENTELEMETRY",
]
