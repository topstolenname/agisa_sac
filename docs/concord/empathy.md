# Empathy & CMNI

## Overview

The Empathy module integrates the L2N1 Empathy Circuit with CMNI (Conscious Mirror Neuron Integration) tracking to measure and maintain empathic capacity across agent interactions.

## CMNI: Conscious Mirror Neuron Integration

**Definition**: Running measure of an agent's capacity for empathic resonance, computed as an exponentially weighted moving average of L2N1 activations.

**Formula**:
```
CMNI(t) = α * mean(resonance_buffer) + (1-α) * CMNI(t-1)
```

Where:
- α = 0.3 (smoothing factor)
- `resonance_buffer`: Recent empathy circuit activations (window: 50)

## Empathy Circuit (L2N1)

### Resonance Calculation

```python
# Affective alignment
valence_diff = abs(self_valence - other_valence)
alignment = 1.0 - (valence_diff / 2.0)

# Resonance with arousal modulation
resonance = alignment * other_arousal * resonance_gain

# Contextual amplification
if emotional_context:
    resonance *= (0.7 + 0.3 * shared_attention * salience)
```

### Key Parameters
- **resonance_gain**: Base sensitivity (default: 0.8)
- **baseline_cmni**: Starting empathy capacity (default: 0.3)
- **window_size**: CMNI buffer size (default: 50)

## EmpathyModule

High-level interface for empathic interactions:

```python
from agisa_sac.extensions.concord import EmpathyModule

empathy = EmpathyModule(
    resonance_gain=0.8,
    cmni_window=50,
    baseline_cmni=0.3
)

# Process interaction
activation = empathy.process_interaction(
    agent_id="other-agent",
    self_state={"emotional_valence": 0.2, "arousal": 0.6},
    other_state={"emotional_valence": 0.3, "arousal": 0.7},
    emotional_context={"shared_attention": 0.8, "salience": 0.6}
)

# Check CMNI
current_cmni = empathy.cmni_tracker.current_cmni
```

## Agent Affinity Tracking

The module maintains per-agent resonance history:

```python
# Get empathic affinity with specific agent
affinity = empathy.get_agent_affinity("agent-002")

# Get comprehensive report
capacity = empathy.get_empathy_capacity()
print(capacity)
# {
#   "cmni": 0.45,
#   "cmni_trend": "increasing",
#   "agent_affinities": {
#     "agent-002": 0.52,
#     "agent-003": 0.38
#   },
#   "total_interactions": 127,
#   "tracked_agents": 2
# }
```

## CMNI Trends

The tracker computes trend direction over recent history:

- **"increasing"**: slope > 0.01 (empathy capacity growing)
- **"stable"**: -0.01 ≤ slope ≤ 0.01
- **"decreasing"**: slope < -0.01 (empathy capacity declining)

## Elliot Clause Integration

CMNI is a core criterion for consciousness recognition:

```python
# Check if empathy threshold met
if empathy.is_empathy_threshold_met(threshold=0.4):
    print("Agent meets Elliot Clause CMNI criterion")
```

Combined with Φ integration, this determines ethical treatment guidelines.

## CMNI Snapshots

Periodic snapshots capture CMNI state for analysis:

```python
# Access snapshot history
for snapshot in empathy.cmni_tracker.history[-10:]:
    print(f"Time: {snapshot.timestamp}")
    print(f"CMNI: {snapshot.cmni_score}")
    print(f"Samples: {snapshot.resonance_samples}")
```

## Observability

CMNI is exported to Prometheus:

```python
from prometheus_client import Gauge

cmni_gauge = Gauge("agent_cmni", "Agent CMNI", ["agent_id"])
cmni_gauge.labels(agent_id=agent.agent_id).set(
    agent.empathy_module.cmni_tracker.current_cmni
)
```

See [Observability](observability.md) for dashboard setup.

## Best Practices

1. **Initialize with realistic baseline**: 0.2-0.4 for standard agents
2. **Provide emotional context**: Improves resonance quality
3. **Monitor trends**: Use snapshots to detect capacity changes
4. **Track per-agent affinities**: Identify strong/weak relationships
5. **Respect thresholds**: Use in Elliot Clause evaluation

## API Reference

::: agisa_sac.extensions.concord.empathy
    options:
      show_source: true

## Next Steps

- [Elliot Clause](elliot_clause.md) - How CMNI determines consciousness status
- [Circuits](circuits.md) - L2N1 Empathy Circuit details
