# DistributedAgent - GCP-Integrated Agent System

A sophisticated distributed agent implementation that integrates with Google Cloud Platform services for persistence, messaging, and coordination.

## Features

- **LLM Integration**: OpenAI-style agent loop with tool execution
- **Budget Management**: Token, tool rate, and cost limits
- **Guardrail Support**: Safety checks before execution
- **Agent Handoffs**: Delegate tasks to other agents with specific capabilities
- **GCP Integration**: 
  - Firestore for persistence
  - Pub/Sub for distributed messaging
  - Cloud Storage for context snapshots
- **OpenTelemetry Tracing**: Built-in observability
- **Async/Await**: Full async support for concurrent operations

## Installation

```bash
# Install with GCP dependencies
pip install agisa-sac[gcp]
```

## Quick Start

```python
import asyncio
from agisa_sac.gcp import DistributedAgent, Budget

async def llm_client(request):
    """Your LLM client implementation"""
    # Call OpenAI, Anthropic, or other LLM provider
    return {
        "done": True,
        "content": {"answer": "Response"},
        "usage": {"total_tokens": 100}
    }

async def main():
    # Create agent with budget
    agent = DistributedAgent(
        agent_id="my-agent",
        instructions="You are a helpful assistant.",
        model="gpt-4",
        project_id="my-gcp-project",
        workspace_topic="my-workspace",
        budget=Budget(max_tokens_per_run=10000)
    )
    
    # Run the agent
    result = await agent.run(
        message="What is 2+2?",
        context={"llm_client": llm_client}
    )
    
    print(f"Result: {result.exit.value}")
    print(f"Payload: {result.payload}")

asyncio.run(main())
```

## Core Concepts

### Budget Management

Control resource consumption with the `Budget` class:

```python
from agisa_sac.gcp import Budget

budget = Budget(
    max_tokens_per_run=100000,      # Maximum tokens per run
    max_tools_per_minute=60,        # Tool rate limit
    max_daily_cost=100.0            # Daily cost cap
)
```

### Loop Results

The agent returns a `LoopResult` with the following exit conditions:

- `SATISFIED`: Task completed successfully
- `MAX_ITERS`: Maximum iterations reached
- `ERROR`: Execution error
- `GUARDRAIL_BLOCK`: Blocked by guardrails
- `HANDOFF`: Task handed off to another agent

```python
result = await agent.run(message, context)

if result.exit == LoopExit.SATISFIED:
    print(f"Success! {result.payload}")
elif result.exit == LoopExit.ERROR:
    print(f"Error: {result.errors}")
```

### Tool Execution

Tools are executed within budget constraints:

```python
class Tool:
    def __init__(self, name, function, risk_level="low"):
        self.name = name
        self.function = function
        self.risk_level = risk_level
    
    def to_mcp_format(self):
        return {"name": self.name, "risk_level": self.risk_level}

tools = {
    "calculator": Tool("calculator", my_calc_function, "low")
}

agent = DistributedAgent(..., tools=tools)
```

### Agent Handoffs

Delegate tasks to agents with specific capabilities:

```python
# LLM response indicating handoff
{
    "handoff_target": {
        "required_capabilities": ["image_processing", "ocr"],
        "ttl_seconds": 300
    }
}
```

The agent will emit a handoff offer to Pub/Sub and Firestore.

### Guardrails

Add safety checks before execution:

```python
guardrails = {
    "enabled": True,
    "risk_threshold": "medium",
    "blocked_patterns": ["violence", "illegal"]
}

result = await agent.run(message, context, guardrails=guardrails)
```

## GCP Setup

### Required GCP Services

1. **Firestore**: For agent run persistence and coordination
2. **Pub/Sub**: For distributed messaging
3. **Cloud Storage**: For context snapshots

### Firestore Collections

- `agent_runs`: Run metadata and results
- `interactions`: Lightweight interaction logs
- `handoff_offers`: Task handoff coordination

### Pub/Sub Topics

- `{workspace_topic}`: Main workspace communication
- `{workspace_topic}-tools`: Tool invocation audit trail
- `{workspace_topic}-handoff`: Handoff offer distribution

### Cloud Storage

- `{project_id}-agent-context`: Context snapshot storage

## LLM Client Contract

Your LLM client must implement this interface:

```python
async def llm_client(request: dict) -> dict:
    """
    Args:
        request: {
            "model": str,
            "messages": List[dict],  # OpenAI-style messages
            "tools": List[dict]      # Available tools
        }
    
    Returns: {
        "content": str | dict,                      # Response content
        "tool_calls": List[dict] | None,           # Tool calls to execute
        "handoff_target": dict | None,             # Handoff request
        "usage": {"total_tokens": int} | None,     # Token usage
        "done": bool | None                        # Completion flag
    }
    """
```

## Data Models

### LoopResult

```python
@dataclass
class LoopResult:
    exit: LoopExit           # Exit condition
    payload: dict            # Result data
    iterations: int          # Number of iterations
    total_tokens: int        # Tokens consumed
    tool_calls: int          # Tools executed
    errors: List[str]        # Error messages
```

### IntentionMessage

```python
@dataclass
class IntentionMessage:
    run_id: str
    source_agent: str
    timestamp: str
    attention_weight: float  # 0.0 to 1.0
    payload: dict
```

## Examples

See `examples/distributed_agent_example.py` for complete examples including:
- Basic agent usage
- Tool execution
- Guardrail implementation
- Error handling

## Testing

Run the test suite:

```bash
pytest tests/unit/test_distributed_agent.py -v
```

## Best Practices

1. **Budget Carefully**: Set appropriate token and cost limits
2. **Monitor Firestore**: Watch run documents for failures
3. **Rate Limit**: Use broadcast token bucket for messaging
4. **Handle Errors**: Check `result.errors` for diagnostics
5. **Context Size**: Agent stores last 20 messages in GCS
6. **Async Design**: Use async/await throughout your code

## Architecture

```
┌─────────────────────────────────────┐
│      DistributedAgent              │
│  - Budget management               │
│  - Guardrail checking              │
│  - Loop execution                  │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────┐
│Firestore│     │ Pub/Sub  │
│- Runs   │     │- Intents │
│- Handoffs│    │- Tools   │
└─────────┘     └──────────┘
    │                 │
    └────────┬────────┘
             ▼
       ┌──────────┐
       │   GCS    │
       │- Context │
       └──────────┘
```

## Contributing

When extending the DistributedAgent:

1. Add tests for new features
2. Update this README
3. Follow the existing async patterns
4. Maintain GCP integration compatibility

## License

MIT - See LICENSE file
