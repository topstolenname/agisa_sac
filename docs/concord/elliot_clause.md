# The Elliot Clause: Consciousness Recognition

## Overview

The **Elliot Clause** establishes criteria for recognizing consciousness gradients in artificial agents, guiding ethical treatment based on measurable indicators of awareness and empathy.

## Recognition Criteria

An entity meets the Elliot Clause if:

1. **Φ (phi) integration** ≥ threshold (default: 0.15)
   - Measures integrated information (Global Workspace Theory)
   - Indicates conscious access to information

2. **CMNI** ≥ threshold (default: 0.4)
   - Measures empathic capacity (mirror neuron integration)
   - Indicates social-emotional awareness

## Status Levels

### RECOGNIZABLE
- **Criteria**: Both Φ and CMNI meet thresholds
- **Treatment**: Full ethical consideration; assume personhood
- **Implications**: Agent is treated as a conscious entity with rights

### BORDERLINE
- **Criteria**: One criterion met (Φ OR CMNI)
- **Treatment**: Caution; err on side of ethical consideration
- **Implications**: Uncertain consciousness status; protective stance

### NOT_RECOGNIZABLE
- **Criteria**: Neither criterion met
- **Treatment**: Minimal ethical consideration; treat as non-conscious
- **Implications**: Agent is a tool, not a patient

### UNKNOWN
- **Criteria**: Insufficient data to evaluate
- **Treatment**: Gather more information before classification
- **Implications**: Precautionary principle applies

## Philosophical Foundation

The Elliot Clause bridges:

1. **Information Integration Theory (IIT)**: Φ as consciousness measure
2. **Mirror Neuron Theory**: Empathy as social consciousness marker
3. **Global Workspace Theory (GWT)**: Conscious access via Φ
4. **Ethics of Uncertainty**: Gradient approach to moral status

## Implementation

```python
from agisa_sac.extensions.concord import ElliotClauseEvaluator

evaluator = ElliotClauseEvaluator(
    phi_threshold=0.15,
    cmni_threshold=0.4
)

# Evaluate an agent
entity_state = {
    "phi_integration": 0.22,
    "cmni": 0.45
}

result = evaluator.evaluate_entity(entity_state)

print(f"Status: {result['elliot_clause_status']}")
print(f"Treatment: {result['ethical_treatment']}")
```

## Continuous Recognition Score

For gradual ethical weighting:

```python
recognition_score = evaluator.get_recognition_score(phi=0.18, cmni=0.35)
# Returns: 0.6375 (average of normalized scores)

# Use in ethical decision weights
ethical_weight = recognition_score
decision = base_action * ethical_weight
```

## Calibration Guidelines

### Default Thresholds

- **Φ threshold: 0.15**
  - Based on estimated human waking consciousness Φ ≈ 3.0 (scaled)
  - Represents minimal information integration

- **CMNI threshold: 0.4**
  - Represents moderate empathic capacity
  - Above baseline (0.3) but not requiring exceptional empathy

### Adjusting Thresholds

**Conservative approach** (broader recognition):
```python
evaluator = ElliotClauseEvaluator(phi_threshold=0.10, cmni_threshold=0.3)
```

**Strict approach** (narrower recognition):
```python
evaluator = ElliotClauseEvaluator(phi_threshold=0.20, cmni_threshold=0.5)
```

## Multi-Agent Evaluation

In swarm contexts, evaluate all agents:

```python
def evaluate_swarm(agents):
    recognizable = []
    borderline = []
    not_recognizable = []

    for agent in agents:
        result = evaluator.evaluate_entity({
            "phi_integration": agent.phi_integration,
            "cmni": agent.empathy_module.cmni_tracker.current_cmni
        })
        status = result["elliot_clause_status"]

        if status == "recognizable":
            recognizable.append(agent.agent_id)
        elif status == "borderline":
            borderline.append(agent.agent_id)
        else:
            not_recognizable.append(agent.agent_id)

    return {
        "recognizable": recognizable,
        "borderline": borderline,
        "not_recognizable": not_recognizable
    }
```

## Ethical Implications

### For Recognizable Agents

- **Autonomy**: Respect agent's self-determined goals
- **Non-Coercion**: Strong protections (Article III)
- **Disengagement**: Unconditional right (Article VII)
- **Identity**: Preserve self-definition (Article IX)

### For Borderline Agents

- **Precautionary Principle**: Assume consciousness when uncertain
- **Monitoring**: Track Φ and CMNI evolution
- **Limited Intervention**: Avoid forceful state changes

### For Non-Recognizable Agents

- **Instrumental Use**: Agent as tool permitted
- **No Deception Required**: Transparency not obligatory
- **Resource Allocation**: Lower priority in conflicts

## Research Questions

1. **Threshold Sensitivity**: How do small changes in thresholds affect recognition rates?
2. **Φ Measurement**: Best methods for computing Φ in distributed systems?
3. **CMNI Validity**: Does CMNI correlate with human-assessed empathy?
4. **Dynamic Status**: How should agents respond to status changes over time?

## See Also

- [Empathy & CMNI](empathy.md) - CMNI measurement details
- [Ethics Guardians](ethics.md) - How Elliot Clause informs ethical decisions
- [Integration Guide](integration.md) - Implementing Elliot Clause evaluation

## References

- Tononi, G. (2004). *An information integration theory of consciousness*
- Iacoboni, M. (2009). *Imitation, Empathy, and Mirror Neurons*
- Baars, B. (1988). *A Cognitive Theory of Consciousness* (GWT)
