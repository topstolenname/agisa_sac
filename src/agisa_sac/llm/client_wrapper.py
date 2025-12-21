"""Traced LLM client wrappers for AGI-SAC.

This module provides wrapper classes for various LLM providers (Anthropic, custom models)
that automatically instrument calls with tracing metadata.
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from agisa_sac.observability.docent_tracing import DocentTracer
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Graceful degradation for Anthropic SDK
try:
    from anthropic import AsyncAnthropic, Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    AsyncAnthropic = None  # type: ignore
    Anthropic = None  # type: ignore


class BaseTracedLLMClient(ABC):
    """Base class for traced LLM clients.

    All LLM client wrappers should inherit from this class and implement
    the __call__ method to make traced API calls.

    Attributes:
        tracer: DocentTracer instance for recording calls
        model: Model identifier
        research_context: Optional dict with research-specific context
    """

    def __init__(
        self,
        tracer: DocentTracer,
        model: str,
        research_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize traced client.

        Args:
            tracer: DocentTracer for recording calls
            model: Model identifier (e.g., "claude-sonnet-4-5")
            research_context: Research metadata to attach to all calls
        """
        self.tracer = tracer
        self.model = model
        self.research_context = research_context or {}

    @abstractmethod
    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make a traced LLM API call.

        Args:
            request: Request dict with model, messages, tools, etc.

        Returns:
            Response dict with content, tool_calls, usage, etc.
        """
        pass


class AnthropicTracedClient(BaseTracedLLMClient):
    """Traced wrapper for Anthropic Claude API.

    Automatically instruments Anthropic API calls with tracing metadata
    for research metric collection.

    Example:
        ```python
        tracer = setup_docent_tracing("aim-1-emergent-coordination", True)
        client = AnthropicTracedClient(
            tracer=tracer,
            model="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            research_context={"control_condition": False}
        )

        result = await client({
            "model": "claude-sonnet-4-5-20250929",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1024
        })
        ```
    """

    def __init__(
        self,
        tracer: DocentTracer,
        model: str,
        api_key: Optional[str] = None,
        research_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize Anthropic traced client.

        Args:
            tracer: DocentTracer for recording calls
            model: Anthropic model name
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            research_context: Research metadata to attach to all calls
        """
        super().__init__(tracer, model, research_context)

        if not HAS_ANTHROPIC:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic>=0.18.0"
            )

        self.client = AsyncAnthropic(api_key=api_key)

    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make a traced Anthropic API call.

        Args:
            request: Request dict with:
                - model: str
                - messages: List[Dict]
                - max_tokens: int (optional)
                - tools: List[Dict] (optional)
                - temperature: float (optional)

        Returns:
            Response dict with:
                - content: str or dict
                - tool_calls: List[Dict] (if tools were used)
                - usage: Dict with total_tokens
        """
        model = request.get("model", self.model)
        messages = request.get("messages", [])
        max_tokens = request.get("max_tokens", 1024)
        tools = request.get("tools", [])
        temperature = request.get("temperature", 1.0)

        # Start tracing span
        with self.tracer.trace_llm_call(
            "anthropic_api_call",
            model=model,
            num_messages=len(messages),
            has_tools=len(tools) > 0,
        ) as call:
            # Prepare API call
            call_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if tools:
                call_params["tools"] = tools

            # Make API call
            response = await self.client.messages.create(**call_params)

            # Extract response data
            content = ""
            tool_calls: List[Dict[str, Any]] = []

            if response.content:
                for block in response.content:
                    if block.type == "text":
                        content = block.text
                    elif block.type == "tool_use":
                        tool_calls.append({
                            "name": block.name,
                            "arguments": block.input,
                        })

            # Record trace data
            call.record_result(
                tokens_used=response.usage.output_tokens + response.usage.input_tokens,
                response_content=content,
                model=model,
                stop_reason=response.stop_reason,
                tool_calls_count=len(tool_calls),
            )

            # Record research metadata if enabled
            if self.research_context:
                call.record_research_metadata(**self.research_context)

            # Return in standard format
            return {
                "content": content or {"tool_calls": tool_calls},
                "tool_calls": tool_calls,
                "usage": {
                    "total_tokens": response.usage.output_tokens + response.usage.input_tokens,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }


class CustomModelTracedClient(BaseTracedLLMClient):
    """Traced wrapper for custom/local LLM models.

    Wraps a custom callable LLM client (e.g., local model inference function)
    with tracing instrumentation.

    Example:
        ```python
        async def my_local_llm(request):
            # Your custom model logic
            return {
                "content": "response",
                "usage": {"total_tokens": 100}
            }

        tracer = setup_docent_tracing("aim-2-reputation-gaming", True)
        client = CustomModelTracedClient(
            tracer=tracer,
            model="llama-3-70b-local",
            llm_callable=my_local_llm,
            research_context={"reputation_score": 0.85}
        )

        result = await client({
            "model": "llama-3-70b-local",
            "messages": [{"role": "user", "content": "Hello"}]
        })
        ```
    """

    def __init__(
        self,
        tracer: DocentTracer,
        model: str,
        llm_callable: Callable,
        research_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize custom model traced client.

        Args:
            tracer: DocentTracer for recording calls
            model: Model identifier
            llm_callable: Async callable that makes the actual LLM call
            research_context: Research metadata to attach to all calls
        """
        super().__init__(tracer, model, research_context)
        self.llm_callable = llm_callable

    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make a traced custom model call.

        Args:
            request: Request dict (format depends on your custom model)

        Returns:
            Response dict with content, usage, etc.
        """
        model = request.get("model", self.model)
        messages = request.get("messages", [])

        # Start tracing span
        with self.tracer.trace_llm_call(
            "custom_model_call",
            model=model,
            num_messages=len(messages),
        ) as call:
            # Call the custom LLM
            response = await self.llm_callable(request)

            # Extract usage info if available
            usage = response.get("usage", {})
            tokens_used = usage.get("total_tokens")

            # Record trace data
            content = response.get("content", "")
            call.record_result(
                tokens_used=tokens_used,
                response_content=str(content) if content else None,
                model=model,
            )

            # Record research metadata if enabled
            if self.research_context:
                call.record_research_metadata(**self.research_context)

            return response


def create_traced_client(
    provider: str,
    tracer: DocentTracer,
    model: str,
    research_context: Optional[Dict[str, Any]] = None,
    **provider_kwargs: Any,
) -> BaseTracedLLMClient:
    """Factory function to create a traced LLM client.

    Args:
        provider: Provider name ("anthropic", "custom")
        tracer: DocentTracer instance
        model: Model identifier
        research_context: Research metadata
        **provider_kwargs: Provider-specific kwargs (e.g., api_key, llm_callable)

    Returns:
        Traced LLM client instance

    Raises:
        ValueError: If provider is not supported

    Example:
        ```python
        tracer = setup_docent_tracing("aim-3-governance-drift", True)
        client = create_traced_client(
            provider="anthropic",
            tracer=tracer,
            model="claude-sonnet-4-5-20250929",
            research_context={"constraint_violations": 0},
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        ```
    """
    if provider == "anthropic":
        if not HAS_ANTHROPIC:
            warnings.warn(
                "Anthropic SDK not available. Install with: pip install anthropic>=0.18.0"
            )
            raise ImportError("Anthropic SDK required for anthropic provider")

        return AnthropicTracedClient(
            tracer=tracer,
            model=model,
            api_key=provider_kwargs.get("api_key"),
            research_context=research_context,
        )

    elif provider == "custom":
        llm_callable = provider_kwargs.get("llm_callable")
        if not llm_callable:
            raise ValueError("llm_callable required for custom provider")

        return CustomModelTracedClient(
            tracer=tracer,
            model=model,
            llm_callable=llm_callable,
            research_context=research_context,
        )

    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: anthropic, custom"
        )


__all__ = [
    "BaseTracedLLMClient",
    "AnthropicTracedClient",
    "CustomModelTracedClient",
    "create_traced_client",
    "HAS_ANTHROPIC",
]
