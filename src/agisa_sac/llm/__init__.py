"""LLM client wrappers with integrated tracing.

This module provides traced wrappers for various LLM providers, ensuring
all LLM calls are properly instrumented for research metric collection.
"""

from agisa_sac.llm.client_wrapper import (
    BaseTracedLLMClient,
    AnthropicTracedClient,
    CustomModelTracedClient,
)

__all__ = [
    "BaseTracedLLMClient",
    "AnthropicTracedClient",
    "CustomModelTracedClient",
]
