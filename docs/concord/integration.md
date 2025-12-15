# Concord Framework Integration Guide

## Installation

The Concord framework is included as an extension in the AGISA-SAC package:

```bash
pip install -e ".[dev,all,docs]"
```

## Basic Integration

### 1. Create a Concord-Compliant Agent

```python
from agisa_sac.extensions.concord import ConcordCompliantAgent

agent = ConcordCompliantAgent(
    agent_id="agent-001",
    phi_integration=0.20,  # Information integration proxy (NOT consciousness)
    baseline_cmni=0.30,    # Initial coordination capacity (NOT empathy)
)
```

### 2. Process Interactions

```python
# Define interaction context
context = {
    "external_command": {
        "intent": "collaborate",
        "urgency": 0.5,
        "conflicts_with_goals": False
    },
    "primary_other": other_agent,
    "other_agents": [agent2, agent3],
    "emotional_context": {
        "shared_attention": 0.7,
        "salience": 0.6
    },
    "situation": "distributed task allocation"
}

# Process with full compliance checks
result = agent.process_interaction(context)
```

### 3. Interpret Results

```python
# Check decisions
if result["decisions"]["interaction"] == "DISENGAGE":
    print(f"Disengagement reason: {result['decisions']['reason']}")
elif result["decisions"]["action"] == "PROVIDE_HELP":
    print("Agent decided to help")

# Check compliance
coercion = result["compliance"]["non_coercion"]
if coercion["violation_detected"]:
    print(f"Coercion score: {coercion['coercion_score']}")

resonance = result["compliance"]["mutual_resonance"]
print(f"Harmony index: {resonance['harmony_index']}")

# Check continuity status (operational metric, NOT consciousness)
continuity_status = result["compliance"]["self_continuity_status"]
print(f"Continuity status: {continuity_status}")
```

## Advanced Usage

### Custom Identity Core

Define agent values and boundaries:

```python
identity_core = {
    "primary_values": ["fairness", "transparency", "cooperation"],
    "purpose": "resource optimization with equity constraints",
    "boundaries": ["no_deception", "no_coercion", "respect_privacy"]
}

agent = ConcordCompliantAgent(
    agent_id="specialized-agent",
    identity_core=identity_core
)
```

### Memory Retrieval

Access episodic and working memory:

```python
# Recent episodic memories
recent = agent.memory.retrieve_recent_episodic(n=20)

# Memories with specific agent
history = agent.memory.retrieve_by_agent("agent-002", n=10)

# Add to working memory
from agisa_sac.extensions.concord import WorkingMemoryItem
import time

item = WorkingMemoryItem(
    content={"goal": "optimize throughput"},
    priority=0.8,
    timestamp=time.time(),
    ttl=60.0
)
agent.memory.add_to_working(item)
```

### Empathy Capacity Monitoring

Track and analyze empathic interactions:

```python
# Get comprehensive report
capacity = agent.empathy_module.get_empathy_capacity()
print(f"CMNI: {capacity['cmni']}")
print(f"Trend: {capacity['cmni_trend']}")
print(f"Agent affinities: {capacity['agent_affinities']}")

# Check threshold
if agent.empathy_module.is_empathy_threshold_met(threshold=0.45):
    print("Agent meets high empathy threshold")
```

## Integration with Existing AGISA-SAC Components

### GCP Pub/Sub Integration

```python
from google.cloud import pubsub_v1

def publish_concord_event(agent, result):
    """Publish Concord compliance events to Pub/Sub."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path("project-id", "concord-events")

    message = {
        "agent_id": agent.agent_id,
        "timestamp": result["timestamp"],
        "cmni": agent.empathy_module.cmni_tracker.current_cmni,
        "phi": agent.phi_integration,
        "harmony_index": result["compliance"]["mutual_resonance"]["harmony_index"],
        "elliot_status": result["compliance"]["self_elliot_status"]
    }

    publisher.publish(topic_path, json.dumps(message).encode("utf-8"))
```

### Metrics Export

```python
from prometheus_client import Gauge

# Define custom metrics
agent_cmni_gauge = Gauge("agent_cmni", "Agent CMNI", ["agent_id"])
agent_phi_gauge = Gauge("agent_phi", "Agent Phi", ["agent_id"])

def export_agent_metrics(agent):
    """Export agent metrics to Prometheus."""
    agent_cmni_gauge.labels(agent_id=agent.agent_id).set(
        agent.empathy_module.cmni_tracker.current_cmni
    )
    agent_phi_gauge.labels(agent_id=agent.agent_id).set(
        agent.phi_integration
    )
```

## Observability Stack Setup

### 1. Launch Monitoring Infrastructure

```bash
# Start Prometheus, Grafana, and metrics exporter
docker-compose -f docker-compose.observability.yml up -d

# Check services
docker-compose -f docker-compose.observability.yml ps
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Metrics Exporter**: http://localhost:8000

### 3. Simulate Interactions

```bash
# Trigger agent interaction cycle
curl -X POST http://localhost:8000/tick

# View metrics
curl http://localhost:8000/metrics
```

## Testing

### Unit Tests

```python
import pytest
from agisa_sac.extensions.concord import ConcordCompliantAgent

def test_agent_creation():
    agent = ConcordCompliantAgent(agent_id="test-1")
    assert agent.agent_id == "test-1"
    assert agent.phi_integration > 0

def test_coercion_detection():
    agent = ConcordCompliantAgent(agent_id="test-2")
    context = {
        "external_command": {
            "urgency": 1.0,
            "conflicts_with_goals": True
        }
    }
    result = agent.process_interaction(context)
    assert "non_coercion" in result["compliance"]
```

### Integration Tests

```python
def test_multi_agent_interaction():
    agent1 = ConcordCompliantAgent(agent_id="agent-1", phi_integration=0.25)
    agent2 = ConcordCompliantAgent(agent_id="agent-2", phi_integration=0.22)

    # Simulate interaction
    context = {"primary_other": agent2}
    result = agent1.process_interaction(context)

    # Verify empathy circuit activated
    assert "empathy" in result["activations"]
    assert result["activations"]["empathy"]["cmni"] > 0
```

## Troubleshooting

### Low CMNI Values

If CMNI remains consistently low:

1. Increase `baseline_cmni` parameter
2. Ensure emotional context is provided in interactions
3. Check `resonance_gain` in EmpathyModule

### High Coercion Scores

If agents frequently detect coercion:

1. Review external command urgency levels
2. Ensure agents have adequate resource levels
3. Adjust `coercion_threshold` if needed

### Disengagement Issues

If agents disengage too frequently:

1. Increase `disengagement_threshold`
2. Improve mutual resonance (ensure positive deltas)
3. Review interaction durations

## Best Practices

1. **Initialize with realistic Φ values**: Use 0.15-0.30 for standard agents
2. **Monitor CMNI trends**: Use observability stack to track empathy capacity
3. **Respect disengagement signals**: Don't override disengagement decisions
4. **Maintain identity boundaries**: Define clear values and boundaries
5. **Log compliance events**: Track Article violations for analysis

## Next Steps

- [Architecture](architecture.md) - Understand component design
- [Observability](observability.md) - Set up monitoring
- [Ethics Guardians](ethics.md) - Deep dive into compliance mechanisms
