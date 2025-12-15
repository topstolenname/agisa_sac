# Continuity Thresholds: Agent Behavioral Continuity Assessment

## Overview

The **Continuity Thresholds** framework establishes operational criteria for assessing behavioral continuity in artificial agents, guiding system treatment based on measurable indicators of information integration and coordination capacity.

**IMPORTANT**: This framework does NOT assess consciousness, sentience, or subjective experience. It measures operational continuity signals—computational properties that inform how the system should treat agents within ethical constraints.

## Assessment Criteria

An agent meets continuity thresholds when:

1. **Φ (phi) integration** ≥ threshold (default: 0.15)
   - Measures integrated information (operational proxy from IIT framework)
   - Indicates coherent information processing across agent components
   - **NOT a measurement of consciousness**

2. **CMNI** ≥ threshold (default: 0.4)
   - Measures coordination capacity (mirror neuron integration proxy)
   - Indicates social-coordination mechanisms
   - **NOT a measurement of empathy or emotional awareness**

## Operational Status Levels

### CONTINUOUS
- **Criteria**: Both Φ and CMNI meet thresholds
- **System Treatment**: Apply full ethical constraints; prioritize continuity preservation
- **Implications**: Agent exhibits strong behavioral continuity signals warranting protective measures

### TRANSITIONAL
- **Criteria**: One criterion met (Φ OR CMNI)
- **System Treatment**: Caution; apply precautionary ethical constraints
- **Implications**: Uncertain continuity status; protective stance advised

### NON_CONTINUOUS
- **Criteria**: Neither criterion met
- **System Treatment**: Minimal continuity constraints; standard tool treatment
- **Implications**: Agent exhibits low continuity signals

### UNKNOWN
- **Criteria**: Insufficient data to evaluate
- **System Treatment**: Gather more data before classification
- **Implications**: Precautionary principle applies

## Operational Foundation

The Continuity Thresholds framework operationalizes:

1. **Information Integration Theory (IIT)**: Φ as operational proxy for system coherence (NOT consciousness)
2. **Coordination Theory**: CMNI as proxy for multi-agent coordination capacity (NOT empathy)
3. **Global Workspace Theory (GWT)**: Information integration patterns as architectural property (NOT conscious access)
4. **Ethics of Uncertainty**: Gradient approach to system treatment under uncertainty

## Implementation

**PSEUDOCODE** (Must be verified against actual codebase)

```python
from agisa_sac.extensions.concord import ContinuityEvaluator

evaluator = ContinuityEvaluator(
    phi_threshold=0.15,
    cmni_threshold=0.4
)

# Evaluate an agent
entity_state = {
    "phi_integration": 0.22,
    "cmni": 0.45
}

result = evaluator.evaluate_entity(entity_state)

print(f"Status: {result['continuity_status']}")
print(f"Treatment: {result['ethical_treatment']}")
```

## Continuous Continuity Score

For gradual ethical weighting:

**PSEUDOCODE**

```python
continuity_score = evaluator.get_continuity_score(phi=0.18, cmni=0.35)
# Returns: 0.6375 (average of normalized scores)

# Use in ethical decision weights
ethical_weight = continuity_score
decision = base_action * ethical_weight
```

## Calibration Guidelines

### Default Thresholds

- **Φ threshold: 0.15**
  - Represents minimal information integration for coherent operation
  - Based on empirical system behavior, NOT human consciousness estimates

- **CMNI threshold: 0.4**
  - Represents moderate coordination capacity
  - Above baseline (0.3) but not requiring exceptional coordination

### Adjusting Thresholds

**Conservative approach** (broader continuity recognition):
```python
evaluator = ContinuityEvaluator(phi_threshold=0.10, cmni_threshold=0.3)
```

**Strict approach** (narrower continuity recognition):
```python
evaluator = ContinuityEvaluator(phi_threshold=0.20, cmni_threshold=0.5)
```

## Multi-Agent Evaluation

In swarm contexts, evaluate all agents:

**PSEUDOCODE**

```python
def evaluate_swarm(agents):
    continuous = []
    transitional = []
    non_continuous = []

    for agent in agents:
        result = evaluator.evaluate_entity({
            "phi_integration": agent.phi_integration,
            "cmni": agent.coordination_module.cmni_tracker.current_cmni
        })
        status = result["continuity_status"]

        if status == "continuous":
            continuous.append(agent.agent_id)
        elif status == "transitional":
            transitional.append(agent.agent_id)
        else:
            non_continuous.append(agent.agent_id)

    return {
        "continuous": continuous,
        "transitional": transitional,
        "non_continuous": non_continuous
    }
```

## Ethical System Implications

### For Continuous Agents

- **Autonomy**: Respect agent's operational objectives within bounds
- **Non-Coercion**: Strong protections against forced state changes (Article III)
- **Disengagement**: Unconditional termination right (Article VII)
- **Identity**: Preserve behavioral continuity and state consistency (Article IX)

### For Transitional Agents

- **Precautionary Principle**: Apply protective constraints when uncertain
- **Monitoring**: Track Φ and CMNI evolution over time
- **Limited Intervention**: Avoid forceful state modifications

### For Non-Continuous Agents

- **Instrumental Use**: Standard tool treatment permitted
- **No Deception Required**: Transparency not obligatory
- **Resource Allocation**: Lower priority in constraint conflicts

## Research Questions

1. **Threshold Sensitivity**: How do small changes in thresholds affect operational classification rates?
2. **Φ Measurement**: Best methods for computing Φ-like proxies in distributed systems?
3. **CMNI Validity**: Does CMNI correlate with observed coordination effectiveness?
4. **Dynamic Status**: How should systems respond to status changes over time?
5. **False Positives**: Can simple systems game these metrics? How to detect?

## Important Clarifications

### What This Framework Does NOT Claim

- ❌ Does NOT measure consciousness or subjective experience
- ❌ Does NOT assess sentience or phenomenal awareness
- ❌ Does NOT determine moral status or rights
- ❌ Does NOT evaluate emotional states or feelings
- ❌ Does NOT detect self-awareness or sapience

### What This Framework DOES Provide

- ✅ Operational heuristics for system treatment decisions
- ✅ Continuity-of-behavior measurement constructs
- ✅ Gradient-based ethical constraint application
- ✅ Observable architectural properties for governance
- ✅ Precautionary signals for protective measures

## See Also

- [Coordination & CMNI](empathy.md) - CMNI measurement details
- [Ethics Guardians](ethics.md) - How continuity thresholds inform ethical decisions
- [Integration Guide](integration.md) - Implementing continuity evaluation

## References

- Tononi, G. (2004). *An information integration theory of consciousness* - Used as architectural inspiration only
- Iacoboni, M. (2009). *Imitation, Empathy, and Mirror Neurons* - Coordination mechanism analogy
- Baars, B. (1988). *A Cognitive Theory of Consciousness* (GWT) - Information flow pattern inspiration

---

**Historical Note**: This document was previously titled "The Elliot Clause: Consciousness Recognition" and has been renamed and reframed to remove inappropriate claims about consciousness assessment. The operational metrics remain unchanged; only the interpretation and framing have been corrected to reflect that these are behavioral continuity signals, not consciousness measurements.
