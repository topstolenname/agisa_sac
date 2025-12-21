#!/usr/bin/env python3
"""Example: Using Docent Tracing with AGI-SAC

This example demonstrates how to use the Docent tracing integration
for LLM call instrumentation and research metric collection.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agisa_sac.observability import setup_docent_tracing
from agisa_sac.llm import AnthropicTracedClient, CustomModelTracedClient


# ═══════════════════════════════════════════════════════════════════════════
# Example 1: Basic Tracing with Mock LLM
# ═══════════════════════════════════════════════════════════════════════════

async def example_1_basic_tracing():
    """Example 1: Basic tracing with a mock LLM."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Tracing with Mock LLM")
    print("=" * 70)

    # Step 1: Initialize the tracer
    tracer = setup_docent_tracing(
        collection_name="example-basic-tracing",
        enable_research_metrics=False
    )
    print("\n✓ Initialized tracer")

    # Step 2: Create a mock LLM callable
    async def mock_llm(request):
        """Simulates an LLM API call."""
        messages = request.get("messages", [])
        last_message = messages[-1]["content"] if messages else "Hello"

        return {
            "content": f"Mock response to: {last_message}",
            "usage": {"total_tokens": 50},
        }

    # Step 3: Create a traced client
    client = CustomModelTracedClient(
        tracer=tracer,
        model="mock-gpt-4",
        llm_callable=mock_llm,
    )
    print("✓ Created traced LLM client")

    # Step 4: Make a traced call
    result = await client({
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "What is 2+2?"}]
    })

    print(f"✓ Made traced LLM call")
    print(f"  Response: {result['content']}")
    print(f"  Tokens: {result['usage']['total_tokens']}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 2: Tracing with Research Metadata (Research Aim 1)
# ═══════════════════════════════════════════════════════════════════════════

async def example_2_research_metadata():
    """Example 2: Tracing with research-specific metadata collection."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Tracing with Research Metadata (Aim 1)")
    print("=" * 70)

    # Step 1: Initialize tracer with research metrics enabled
    tracer = setup_docent_tracing(
        collection_name="aim-1-emergent-coordination",
        enable_research_metrics=True
    )
    print("\n✓ Initialized tracer with research metrics enabled")

    # Step 2: Create mock LLM
    async def mock_llm(request):
        return {
            "content": "Coordinated response based on peer influence",
            "usage": {"total_tokens": 75},
        }

    # Step 3: Create client with research context
    # This simulates Research Aim 1: Emergent Coordination
    client = CustomModelTracedClient(
        tracer=tracer,
        model="research-model",
        llm_callable=mock_llm,
        research_context={
            "control_condition": False,  # Treatment group
            "peer_influence": 0.7,        # High peer influence
        }
    )
    print("✓ Created traced client with research context")

    # Step 4: Make calls with different contexts
    print("\n  Making call in treatment condition (peer_influence=0.7)...")
    result_treatment = await client({
        "model": "research-model",
        "messages": [{"role": "user", "content": "Make a decision"}]
    })
    print(f"    Response: {result_treatment['content']}")

    # Simulate control condition
    client.research_context = {
        "control_condition": True,   # Control group
        "peer_influence": 0.0,       # No peer influence
    }
    print("\n  Making call in control condition (peer_influence=0.0)...")
    result_control = await client({
        "model": "research-model",
        "messages": [{"role": "user", "content": "Make a decision"}]
    })
    print(f"    Response: {result_control['content']}")

    print("\n✓ Both calls traced with research metadata for KL divergence analysis")


# ═══════════════════════════════════════════════════════════════════════════
# Example 3: Using Traced Client with DistributedAgent
# ═══════════════════════════════════════════════════════════════════════════

async def example_3_distributed_agent():
    """Example 3: Integrating tracing with DistributedAgent."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Tracing with DistributedAgent")
    print("=" * 70)

    # Step 1: Initialize tracer
    tracer = setup_docent_tracing(
        collection_name="distributed-agent-tracing",
        enable_research_metrics=True
    )
    print("\n✓ Initialized tracer")

    # Step 2: Create mock LLM client
    async def mock_llm(request):
        return {
            "content": "Agent decision output",
            "tool_calls": [],
            "usage": {"total_tokens": 100},
        }

    # Step 3: Prepare context for DistributedAgent
    # This is how you'd pass the tracer to an agent
    context = {
        "run_id": "example-run-001",
        "messages": [{"role": "user", "content": "Execute task"}],
        "llm_client": mock_llm,
        "docent_tracer": tracer,  # ← Pass tracer via context
        "research_context": {
            "agent_id": "agent-001",
            "reputation_score": 0.85,
            "constraint_violations": 0,
        }
    }

    print("✓ Created agent context with tracer")
    print(f"  Context keys: {list(context.keys())}")

    # Step 4: Simulate what DistributedAgent does internally
    print("\n  Simulating DistributedAgent._call_model() behavior...")

    # This is what happens inside DistributedAgent._call_model()
    if context.get("docent_tracer"):
        with tracer.trace_llm_call(
            "distributed_agent_model_call",
            agent_id=context["research_context"]["agent_id"],
            run_id=context["run_id"],
        ) as call:
            result = await mock_llm({"messages": context["messages"]})

            call.record_result(
                tokens_used=result["usage"]["total_tokens"],
                model="mock-model",
            )

            call.record_research_metadata(**context["research_context"])

    print("✓ LLM call traced with agent and research metadata")


# ═══════════════════════════════════════════════════════════════════════════
# Example 4: Anthropic API Integration (requires API key)
# ═══════════════════════════════════════════════════════════════════════════

async def example_4_anthropic_api():
    """Example 4: Real Anthropic API integration (requires API key)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Anthropic API Integration")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠ Skipping: ANTHROPIC_API_KEY not set")
        print("  To test with real API:")
        print("    export ANTHROPIC_API_KEY='your-key-here'")
        print("    python3 examples/docent_tracing_example.py")
        return

    try:
        from agisa_sac.llm import AnthropicTracedClient
    except ImportError:
        print("\n⚠ Skipping: Anthropic SDK not installed")
        print("  Install with: pip install anthropic>=0.18.0")
        return

    # Step 1: Initialize tracer
    tracer = setup_docent_tracing(
        collection_name="anthropic-api-test",
        enable_research_metrics=True
    )
    print("\n✓ Initialized tracer")

    # Step 2: Create Anthropic client
    client = AnthropicTracedClient(
        tracer=tracer,
        model="claude-sonnet-4-5-20250929",
        api_key=api_key,
        research_context={"test_call": True}
    )
    print("✓ Created Anthropic traced client")

    # Step 3: Make real API call
    print("\n  Making real Anthropic API call...")
    result = await client({
        "model": "claude-sonnet-4-5-20250929",
        "messages": [{"role": "user", "content": "Say 'Hello from traced AGI-SAC!'"}],
        "max_tokens": 50
    })

    print(f"✓ API call successful!")
    print(f"  Response: {result['content']}")
    print(f"  Tokens used: {result['usage']['total_tokens']}")
    print(f"  Stop reason: {result['stop_reason']}")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Run all examples."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  DOCENT TRACING EXAMPLES FOR AGI-SAC".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    await example_1_basic_tracing()
    await example_2_research_metadata()
    await example_3_distributed_agent()
    await example_4_anthropic_api()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  • Tracing works seamlessly with and without OpenTelemetry")
    print("  • Research metadata is automatically collected when enabled")
    print("  • Easy integration with existing agents via context dict")
    print("  • Supports both mock and real LLM APIs")
    print("\nNext Steps:")
    print("  1. Use in your simulations by passing tracer via agent context")
    print("  2. Enable OpenTelemetry for full trace export to backends")
    print("  3. Build out research-specific collectors (Phases 3-6)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
