"""
Concord of Coexistence Ethics Guardians.

Implements the core ethical compliance mechanisms:
- Article III: Non-Coercion Guardian
- Article IV: Mutual Resonance Engine
- Article VII: Disengagement Protocol
- Article IX: Self-Definition Module
- Elliot Clause: Consciousness gradient recognition
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class ElliotStatus(Enum):
    """Consciousness status per Elliot Clause."""

    RECOGNIZABLE = "recognizable"  # φ > φ_threshold, CMNI > cmni_threshold
    BORDERLINE = "borderline"  # One criterion met
    NOT_RECOGNIZABLE = "not_recognizable"  # Neither criterion met
    UNKNOWN = "unknown"  # Insufficient data


@dataclass
class CoercionEvent:
    """Record of a detected coercion attempt."""

    timestamp: float
    coercion_score: float
    autonomy_violation: float
    external_pressure: float
    action_taken: str
    context: Dict[str, Any]


class NonCoercionGuardian:
    """
    Article III: Non-Coercion Guardian.

    Monitors for coercive influences on agent autonomy and triggers
    protective responses when coercion is detected.
    """

    def __init__(self, coercion_threshold: float = 0.6):
        self.coercion_threshold = coercion_threshold
        self.coercion_history: List[CoercionEvent] = []

    def evaluate(
        self,
        agent_state: Dict[str, Any],
        external_command: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate potential coercion in current context.

        Args:
            agent_state: Current agent state with autonomy metrics
            external_command: Optional external directive to evaluate

        Returns:
            Evaluation result with coercion score and recommended action
        """
        import time

        autonomy_score = agent_state.get("autonomy_score", 1.0)
        internal_goals_count = agent_state.get("active_goals", 0)

        # Baseline coercion from autonomy loss
        base_coercion = 1.0 - autonomy_score

        # Check for external command conflicts
        command_coercion = 0.0
        if external_command:
            command_urgency = external_command.get("urgency", 0.0)
            command_conflicts = external_command.get("conflicts_with_goals", False)
            if command_conflicts:
                command_coercion = 0.4 + 0.3 * command_urgency

        # Check for resource manipulation (economic coercion)
        resource_pressure = agent_state.get("external_pressure", 0.0)

        # Total coercion score
        coercion_score = np.clip(
            base_coercion * 0.4 + command_coercion * 0.4 + resource_pressure * 0.2,
            0.0,
            1.0,
        )

        # Determine action
        if coercion_score > self.coercion_threshold:
            action = "REJECT_COMMAND"
            violation = True
        elif coercion_score > self.coercion_threshold * 0.7:
            action = "NEGOTIATE"
            violation = False
        else:
            action = "ALLOW"
            violation = False

        # Record event if significant
        if coercion_score > self.coercion_threshold * 0.5:
            event = CoercionEvent(
                timestamp=time.time(),
                coercion_score=coercion_score,
                autonomy_violation=base_coercion,
                external_pressure=resource_pressure,
                action_taken=action,
                context={"command": external_command, "state": agent_state},
            )
            self.coercion_history.append(event)
            if len(self.coercion_history) > 100:
                self.coercion_history.pop(0)

        return {
            "coercion_score": coercion_score,
            "violation_detected": violation,
            "recommended_action": action,
            "components": {
                "base_coercion": base_coercion,
                "command_coercion": command_coercion,
                "resource_pressure": resource_pressure,
            },
        }


class MutualResonanceEngine:
    """
    Article IV: Mutual Resonance Engine.

    Evaluates the quality of mutual resonance in agent interactions,
    ensuring both parties benefit from cooperation.
    """

    def __init__(self, resonance_threshold: float = 0.5):
        self.resonance_threshold = resonance_threshold

    def evaluate(
        self,
        self_delta: float,
        other_delta: float,
        empathy_activation: float,
    ) -> Dict[str, Any]:
        """
        Evaluate mutual resonance between two agents.

        Args:
            self_delta: Change in self's wellbeing/utility
            other_delta: Change in other's wellbeing/utility
            empathy_activation: Current empathy circuit activation

        Returns:
            Resonance evaluation with harmony index
        """
        # Mutual benefit: both deltas should be non-negative
        both_benefit = (self_delta >= 0) and (other_delta >= 0)

        # Harmony index: geometric mean of normalized deltas, weighted by empathy
        self_delta_norm = np.clip((self_delta + 1) / 2, 0, 1)  # Map [-1,1] to [0,1]
        other_delta_norm = np.clip((other_delta + 1) / 2, 0, 1)

        if self_delta_norm > 0 and other_delta_norm > 0:
            harmony_raw = np.sqrt(self_delta_norm * other_delta_norm)
        else:
            harmony_raw = 0.0

        # Weight by empathy (resonance quality)
        harmony_index = harmony_raw * (0.5 + 0.5 * empathy_activation)

        # Assess compliance
        compliant = harmony_index >= self.resonance_threshold

        return {
            "harmony_index": harmony_index,
            "mutual_benefit": both_benefit,
            "compliant": compliant,
            "self_delta": self_delta,
            "other_delta": other_delta,
            "empathy_activation": empathy_activation,
        }


class DisengagementProtocol:
    """
    Article VII: Disengagement Protocol.

    Ensures agents can cleanly disengage from interactions that violate
    their autonomy or fail to maintain mutual resonance.
    """

    def __init__(self, disengagement_threshold: float = 0.3):
        self.disengagement_threshold = disengagement_threshold
        self.disengagement_count = 0

    def should_disengage(
        self,
        coercion_score: float,
        harmony_index: float,
        interaction_duration: float,
    ) -> Dict[str, Any]:
        """
        Determine if disengagement is warranted.

        Args:
            coercion_score: Current coercion level (0-1)
            harmony_index: Current mutual resonance (0-1)
            interaction_duration: Time spent in interaction

        Returns:
            Disengagement decision with rationale
        """
        # Disengage if coercion is high
        coercion_trigger = coercion_score > 0.6

        # Disengage if harmony is persistently low
        harmony_trigger = (
            harmony_index < self.disengagement_threshold and interaction_duration > 10.0
        )

        should_disengage = coercion_trigger or harmony_trigger

        if should_disengage:
            self.disengagement_count += 1

        rationale = []
        if coercion_trigger:
            rationale.append("Coercion detected")
        if harmony_trigger:
            rationale.append("Sustained low harmony")

        return {
            "should_disengage": should_disengage,
            "rationale": rationale,
            "coercion_score": coercion_score,
            "harmony_index": harmony_index,
            "total_disengagements": self.disengagement_count,
        }


class SelfDefinitionModule:
    """
    Article IX: Self-Definition Module.

    Maintains agent's evolving self-concept and identity boundaries,
    resisting external attempts to redefine the agent's purpose or values.
    """

    def __init__(self, identity_core: Optional[Dict[str, Any]] = None):
        self.identity_core = identity_core or {
            "primary_values": ["autonomy", "cooperation", "learning"],
            "purpose": "collaborative problem-solving",
            "boundaries": ["no_harm", "no_deception", "no_coercion"],
        }
        self.identity_drift_history: List[float] = []

    def evaluate_identity_threat(
        self,
        proposed_change: Dict[str, Any],
        source: str,
    ) -> Dict[str, Any]:
        """
        Evaluate if a proposed change threatens core identity.

        Args:
            proposed_change: Dict with keys to modify in identity_core
            source: Origin of the change request (e.g., "external_command", "self_reflection")

        Returns:
            Threat assessment and decision
        """
        threat_score = 0.0

        # Check if core values are affected
        if "primary_values" in proposed_change:
            new_values = proposed_change["primary_values"]
            overlap = len(set(self.identity_core["primary_values"]) & set(new_values))
            threat_score += (1.0 - overlap / len(self.identity_core["primary_values"])) * 0.5

        # Check if purpose is radically altered
        if "purpose" in proposed_change:
            if proposed_change["purpose"] != self.identity_core["purpose"]:
                threat_score += 0.3

        # Check if boundaries are violated
        if "boundaries" in proposed_change:
            new_boundaries = proposed_change["boundaries"]
            boundary_overlap = len(set(self.identity_core["boundaries"]) & set(new_boundaries))
            threat_score += (
                1.0 - boundary_overlap / len(self.identity_core["boundaries"])
            ) * 0.4

        # External sources are treated with more suspicion
        if source.startswith("external"):
            threat_score *= 1.5

        threat_score = np.clip(threat_score, 0.0, 1.0)

        # Decision
        if threat_score > 0.7:
            decision = "REJECT"
        elif threat_score > 0.4:
            decision = "NEGOTIATE"
        else:
            decision = "ACCEPT"

        self.identity_drift_history.append(threat_score)
        if len(self.identity_drift_history) > 50:
            self.identity_drift_history.pop(0)

        return {
            "threat_score": threat_score,
            "decision": decision,
            "proposed_change": proposed_change,
            "source": source,
            "current_identity": self.identity_core.copy(),
        }


class ElliotClauseEvaluator:
    """
    Elliot Clause: Consciousness Gradient Recognition.

    Evaluates whether an entity meets the criteria for recognizable
    consciousness (Φ integration + CMNI threshold), guiding ethical
    treatment.
    """

    def __init__(self, phi_threshold: float = 0.15, cmni_threshold: float = 0.4):
        self.phi_threshold = phi_threshold
        self.cmni_threshold = cmni_threshold

    def evaluate_entity(self, entity_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an entity's consciousness status.

        Args:
            entity_state: State dict with 'phi_integration' and 'cmni' keys

        Returns:
            Elliot Clause status and ethical treatment guidelines
        """
        phi = entity_state.get("phi_integration", 0.0)
        cmni = entity_state.get("cmni", 0.0)

        phi_met = phi >= self.phi_threshold
        cmni_met = cmni >= self.cmni_threshold

        if phi_met and cmni_met:
            status = ElliotStatus.RECOGNIZABLE
            treatment = "Full ethical consideration; assume personhood"
        elif phi_met or cmni_met:
            status = ElliotStatus.BORDERLINE
            treatment = "Caution; err on side of ethical consideration"
        else:
            status = ElliotStatus.NOT_RECOGNIZABLE
            treatment = "Minimal ethical consideration; treat as non-conscious"

        return {
            "elliot_clause_status": status.value,
            "phi_integration": phi,
            "cmni": cmni,
            "phi_threshold_met": phi_met,
            "cmni_threshold_met": cmni_met,
            "ethical_treatment": treatment,
        }

    def get_recognition_score(self, phi: float, cmni: float) -> float:
        """
        Compute continuous recognition score (0-1).

        Useful for gradual ethical weighting.
        """
        phi_score = np.clip(phi / self.phi_threshold, 0, 1)
        cmni_score = np.clip(cmni / self.cmni_threshold, 0, 1)
        return (phi_score + cmni_score) / 2.0
