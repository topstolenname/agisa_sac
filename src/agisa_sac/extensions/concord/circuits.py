"""
Mirror Neuron-Inspired Neural Circuits for Concord Framework.

Implements three core circuits based on Lacoboni's mirror neuron research:
- L2N0: Self-Preservation Circuit (survival, threat detection)
- L2N7: Tactical Help Circuit (strategic assistance, resource optimization)
- L2N1: Empathy Circuit (emotional resonance, perspective-taking)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class CircuitActivation:
    """Represents the activation state of a neural circuit."""

    circuit_id: str
    activation_level: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any]
    timestamp: float


class SelfPreservationCircuit:
    """
    L2N0: Self-Preservation Circuit.

    Monitors agent's internal state for threats to operational integrity,
    resource depletion, or constraint violations. Aligns with Article III
    (Non-Coercion) by detecting forced states.
    """

    def __init__(self, threat_threshold: float = 0.7):
        self.circuit_id = "L2N0"
        self.threat_threshold = threat_threshold
        self.baseline_state: Optional[Dict[str, float]] = None

    def evaluate(self, agent_state: Dict[str, Any]) -> CircuitActivation:
        """
        Evaluate self-preservation needs.

        Args:
            agent_state: Current agent state with keys:
                - resource_level: float (0-1)
                - constraint_violations: int
                - autonomy_score: float (0-1)
                - external_pressure: float (0-1)

        Returns:
            CircuitActivation with threat level
        """
        import time

        resource_level = agent_state.get("resource_level", 1.0)
        violations = agent_state.get("constraint_violations", 0)
        autonomy = agent_state.get("autonomy_score", 1.0)
        pressure = agent_state.get("external_pressure", 0.0)

        # Calculate threat score
        threat_components = [
            (1.0 - resource_level) * 0.3,  # Resource depletion
            min(violations * 0.2, 1.0) * 0.2,  # Constraint violations
            (1.0 - autonomy) * 0.3,  # Loss of autonomy (coercion indicator)
            pressure * 0.2,  # External pressure
        ]
        threat_score = sum(threat_components)

        # Calculate confidence based on state completeness
        available_signals = sum(
            1 for k in ["resource_level", "constraint_violations", "autonomy_score"]
            if k in agent_state
        )
        confidence = available_signals / 3.0

        return CircuitActivation(
            circuit_id=self.circuit_id,
            activation_level=min(threat_score, 1.0),
            confidence=confidence,
            context={
                "threat_score": threat_score,
                "resource_level": resource_level,
                "violations": violations,
                "autonomy": autonomy,
                "pressure": pressure,
                "above_threshold": threat_score > self.threat_threshold,
            },
            timestamp=time.time(),
        )


class TacticalHelpCircuit:
    """
    L2N7: Tactical Help Circuit.

    Evaluates strategic opportunities for providing assistance to other agents.
    Optimizes for resource efficiency and mutual benefit. Aligns with Article IV
    (Mutual Resonance) and Article VII (Disengagement).
    """

    def __init__(self, help_threshold: float = 0.5):
        self.circuit_id = "L2N7"
        self.help_threshold = help_threshold

    def evaluate(
        self,
        self_state: Dict[str, Any],
        other_state: Dict[str, Any],
        relationship_history: Optional[List[Dict[str, Any]]] = None
    ) -> CircuitActivation:
        """
        Evaluate opportunity and capacity to provide tactical help.

        Args:
            self_state: Current agent's state (resource_level, capacity, etc.)
            other_state: Other agent's state (need_level, request_type, etc.)
            relationship_history: Past interactions with this agent

        Returns:
            CircuitActivation with help propensity
        """
        import time

        self_capacity = self_state.get("resource_level", 0.5)
        self_load = self_state.get("current_load", 0.5)
        other_need = other_state.get("need_level", 0.0)
        other_priority = other_state.get("priority", 0.5)

        # Calculate help propensity
        capacity_to_help = self_capacity * (1.0 - self_load)
        need_urgency = other_need * other_priority

        # Factor in relationship history (reciprocity)
        reciprocity_bonus = 0.0
        if relationship_history:
            # Handle both dict and MemoryTrace objects
            past_helps = 0
            received_helps = 0
            for h in relationship_history:
                # If it's a dict (legacy format)
                if isinstance(h, dict):
                    if h.get("helped", False):
                        past_helps += 1
                    if h.get("received_help", False):
                        received_helps += 1
                # If it's a MemoryTrace object (dataclass)
                else:
                    event_type = getattr(h, "event_type", "")
                    if event_type in ["help_provided", "assistance_given"]:
                        past_helps += 1
                    elif event_type in ["help_received", "assistance_received"]:
                        received_helps += 1

            if len(relationship_history) > 0:
                reciprocity_bonus = (received_helps / len(relationship_history)) * 0.2

        help_score = (capacity_to_help * 0.5 + need_urgency * 0.4 + reciprocity_bonus)

        # Strategic value: avoid over-extension
        strategic_penalty = 0.0
        if self_capacity < 0.3:
            strategic_penalty = 0.3  # Self-preservation takes precedence

        final_score = max(help_score - strategic_penalty, 0.0)

        confidence = 0.7 if relationship_history else 0.5

        return CircuitActivation(
            circuit_id=self.circuit_id,
            activation_level=min(final_score, 1.0),
            confidence=confidence,
            context={
                "help_score": final_score,
                "capacity_to_help": capacity_to_help,
                "need_urgency": need_urgency,
                "reciprocity_bonus": reciprocity_bonus,
                "strategic_penalty": strategic_penalty,
                "should_help": final_score > self.help_threshold,
            },
            timestamp=time.time(),
        )


class EmpathyCircuit:
    """
    L2N1: Empathy Circuit.

    Simulates emotional resonance and perspective-taking. Core to CMNI
    (Conscious Mirror Neuron Integration) tracking and Article IV
    (Mutual Resonance) compliance.
    """

    def __init__(self, resonance_gain: float = 0.8):
        self.circuit_id = "L2N1"
        self.resonance_gain = resonance_gain
        self.affective_memory: List[CircuitActivation] = []

    def evaluate(
        self,
        self_state: Dict[str, Any],
        other_state: Dict[str, Any],
        emotional_context: Optional[Dict[str, Any]] = None
    ) -> CircuitActivation:
        """
        Evaluate empathic resonance with another agent.

        Args:
            self_state: Current agent's emotional state
            other_state: Other agent's emotional state
            emotional_context: Shared situational context

        Returns:
            CircuitActivation with resonance level (contributes to CMNI)
        """
        import time

        self_valence = self_state.get("emotional_valence", 0.0)  # -1 to 1
        other_valence = other_state.get("emotional_valence", 0.0)
        other_arousal = other_state.get("arousal", 0.5)  # 0 to 1

        # Calculate affective alignment
        valence_diff = abs(self_valence - other_valence)
        alignment = 1.0 - (valence_diff / 2.0)  # Normalize to 0-1

        # Resonance is stronger when other's arousal is high
        resonance_raw = alignment * other_arousal * self.resonance_gain

        # Contextual modulation
        if emotional_context:
            shared_attention = emotional_context.get("shared_attention", 0.5)
            situational_salience = emotional_context.get("salience", 0.5)
            resonance_raw *= (0.7 + 0.3 * shared_attention * situational_salience)

        resonance = np.clip(resonance_raw, 0.0, 1.0)

        # Confidence based on signal quality
        confidence = 0.5 + 0.5 * other_arousal

        activation = CircuitActivation(
            circuit_id=self.circuit_id,
            activation_level=resonance,
            confidence=confidence,
            context={
                "resonance": resonance,
                "alignment": alignment,
                "other_arousal": other_arousal,
                "valence_diff": valence_diff,
                "self_valence": self_valence,
                "other_valence": other_valence,
            },
            timestamp=time.time(),
        )

        # Store in affective memory (limited window)
        self.affective_memory.append(activation)
        if len(self.affective_memory) > 100:
            self.affective_memory.pop(0)

        return activation

    def get_recent_resonance_mean(self, window: int = 10) -> float:
        """Calculate mean resonance over recent activations (for CMNI)."""
        if not self.affective_memory:
            return 0.0
        recent = self.affective_memory[-window:]
        return np.mean([a.activation_level for a in recent])
