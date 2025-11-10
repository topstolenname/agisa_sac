"""
Example: Using the DistributedAgent with GCP Integration

This example demonstrates how to use the DistributedAgent class to create
a distributed agent system with Google Cloud Platform integration.
"""

import asyncio
from agisa_sac.gcp import DistributedAgent, Budget


# Example tool function
def calculator_add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


# Example tool class (with MCP format method)
class Tool:
    def __init__(self, name: str, function, risk_level: str = "low"):
        self.name = name
        self.function = function
        self.risk_level = risk_level

    def to_mcp_format(self):
        return {
            "name": self.name,
            "description": self.function.__doc__ or "",
            "risk_level": self.risk_level,
        }


# Example LLM client implementation
async def mock_llm_client(request):
    """
    A mock LLM client that simulates model responses.
    In production, this would call OpenAI, Anthropic, or another LLM provider.
    """
    messages = request["messages"]
    
    # Simple logic: respond based on the last user message
    last_user_msg = next(
        (m for m in reversed(messages) if m["role"] == "user"), 
        {"content": ""}
    )
    
    # Simulate completion
    return {
        "done": True,
        "content": {"answer": "Task completed successfully", "details": last_user_msg["content"]},
        "summary": "Processed user request",
        "usage": {"total_tokens": 100},
    }


async def main():
    """Main example demonstrating DistributedAgent usage"""
    
    # Configure budget limits
    budget = Budget(
        max_tokens_per_run=10000,
        max_tools_per_minute=30,
        max_daily_cost=50.0,
    )

    # Define available tools
    tools = {
        "calculator_add": Tool("calculator_add", calculator_add, "low"),
    }

    # Create the distributed agent
    agent = DistributedAgent(
        agent_id="example-agent-001",
        instructions="You are a helpful assistant that can perform calculations and answer questions.",
        model="gpt-4",
        tools=tools,
        project_id="my-gcp-project",
        workspace_topic="my-workspace",
        budget=budget,
    )

    # Prepare context with LLM client
    context = {
        "llm_client": mock_llm_client,
        "max_iterations": 10,
    }

    # Run the agent with a user message
    try:
        result = await agent.run(
            message="What is 5 + 3?",
            context=context,
        )

        # Process the result
        print(f"Agent run completed!")
        print(f"Exit reason: {result.exit.value}")
        print(f"Iterations: {result.iterations}")
        print(f"Total tokens: {result.total_tokens}")
        print(f"Tool calls: {result.tool_calls}")
        print(f"Payload: {result.payload}")

        if result.errors:
            print(f"Errors: {result.errors}")

    except Exception as e:
        print(f"Error running agent: {e}")


async def example_with_guardrails():
    """Example showing guardrail usage"""
    
    budget = Budget()
    agent = DistributedAgent(
        agent_id="guarded-agent-001",
        instructions="You are a safe assistant.",
        model="gpt-4",
        project_id="my-gcp-project",
        workspace_topic="my-workspace",
        budget=budget,
    )

    # Guardrail configuration
    guardrails = {
        "enabled": True,
        "risk_threshold": "medium",
        "blocked_patterns": ["violence", "illegal"],
    }

    context = {
        "llm_client": mock_llm_client,
    }

    result = await agent.run(
        message="Tell me a story about robots",
        context=context,
        guardrails=guardrails,
    )

    print(f"Guarded run result: {result.exit.value}")


if __name__ == "__main__":
    print("=== Basic DistributedAgent Example ===")
    asyncio.run(main())
    
    print("\n=== Guardrail Example ===")
    asyncio.run(example_with_guardrails())
