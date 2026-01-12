"""
Social Inference Module with CMNI (Cognitive state-matching integration) tracking.

Implements the social inference capacity measurement and tracking system for
Concord-compliant agents, based on state-matching circuit activations.

Note: Module retains legacy name 'empathy.py' for compatibility.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .circuits import CircuitActivation, EmpathyCircuit


@dataclass
class CMNISnapshot:
    """Snapshot of CMNI state at a point in time."""

    timestamp: float
    cmni_score: float
    resonance_samples: list[float]
    agent_count: int
    context: dict[str, Any] = field(default_factory=dict)


class CMNITracker:
    """
    Tracks Cognitive state-matching integration (CMNI) over time.

    CMNI measures the agent's capacity for social inference across
    interactions with multiple agents. It's computed as the running
    mean of social inference circuit activations.
    """

    def __init__(self, window_size: int = 50, baseline_cmni: float = 0.3):
        self.window_size = window_size
        self.baseline_cmni = baseline_cmni
        self.resonance_buffer: deque[float] = deque(maxlen=window_size)
        self.current_cmni: float = baseline_cmni
        self.history: list[CMNISnapshot] = []
        self._activation_count = 0

    def update(self, activation: CircuitActivation) -> float:
        """
        Update CMNI based on new social inference circuit activation.

        Args:
            activation: Social inference circuit (L2N1) activation result

        Returns:
            Updated CMNI score
        """
        if activation.circuit_id != "L2N1":
            raise ValueError(
                f"CMNI tracker expects L2N1 activations, got {activation.circuit_id}"
            )

        # Add weighted activation (weight by confidence)
        weighted_activation = activation.activation_level * activation.confidence
        self.resonance_buffer.append(weighted_activation)
        self._activation_count += 1

        # Compute CMNI as exponentially weighted moving average
        if len(self.resonance_buffer) > 0:
            alpha = 0.3  # Smoothing factor
            raw_mean = np.mean(list(self.resonance_buffer))
            self.current_cmni = alpha * raw_mean + (1 - alpha) * self.current_cmni
        else:
            self.current_cmni = self.baseline_cmni

        # Store snapshot periodically
        if self._activation_count % 10 == 0:
            self.history.append(
                CMNISnapshot(
                    timestamp=activation.timestamp,
                    cmni_score=self.current_cmni,
                    resonance_samples=list(self.resonance_buffer)[-10:],
                    agent_count=1,  # Updated by EmpathyModule
                    context=activation.context.copy(),
                )
            )

        return self.current_cmni

    def get_cmni_trend(self, lookback: int = 10) -> str:
        """Get trend direction: 'increasing', 'decreasing', or 'stable'."""
        if len(self.history) < 2:
            return "stable"

        recent = [s.cmni_score for s in self.history[-lookback:]]
        if len(recent) < 2:
            return "stable"

        # Simple linear regression slope
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"


class EmpathyModule:
    """
    High-level social inference module integrating state-matching circuits
    with CMNI tracking.

    Manages social inference interactions across multiple agents and maintains
    the agent's overall social inference capacity score.

    Note: Class retains legacy name 'EmpathyModule' for API compatibility.
    """

    def __init__(
        self,
        resonance_gain: float = 0.8,
        cmni_window: int = 50,
        baseline_cmni: float = 0.3,
    ):
        self.empathy_circuit = EmpathyCircuit(resonance_gain=resonance_gain)
        self.cmni_tracker = CMNITracker(
            window_size=cmni_window, baseline_cmni=baseline_cmni
        )
        self.agent_resonance_map: dict[str, list[float]] = (
            {}
        )  # Track per-agent resonance

    def process_interaction(
        self,
        agent_id: str,
        self_state: dict[str, Any],
        other_state: dict[str, Any],
        emotional_context: dict[str, Any] | None = None,
    ) -> CircuitActivation:
        """
        Process a social inference interaction with another agent.

        Args:
            agent_id: Identifier of the other agent
            self_state: Current agent's state
            other_state: Other agent's state
            emotional_context: Shared situational context

        Returns:
            CircuitActivation from social inference circuit, with CMNI updated
        """
        # Run social inference circuit evaluation
        activation = self.empathy_circuit.evaluate(
            self_state, other_state, emotional_context
        )

        # Update CMNI tracker
        self.cmni_tracker.update(activation)

        # Track per-agent resonance
        if agent_id not in self.agent_resonance_map:
            self.agent_resonance_map[agent_id] = []
        self.agent_resonance_map[agent_id].append(activation.activation_level)

        # Keep only recent history per agent
        if len(self.agent_resonance_map[agent_id]) > 20:
            self.agent_resonance_map[agent_id].pop(0)

        return activation

    def get_agent_affinity(self, agent_id: str) -> float:
        """
        Get social inference affinity with a specific agent (mean resonance).

        Args:
            agent_id: Target agent identifier

        Returns:
            Mean resonance score (0-1) with this agent
        """
        if agent_id not in self.agent_resonance_map:
            return 0.0
        history = self.agent_resonance_map[agent_id]
        return np.mean(history) if history else 0.0

    def get_empathy_capacity(self) -> dict[str, Any]:
        """
        Get comprehensive social inference capacity report.

        Returns:
            Dictionary with CMNI, trends, and per-agent affinities
        """
        return {
            "cmni": self.cmni_tracker.current_cmni,
            "cmni_trend": self.cmni_tracker.get_cmni_trend(),
            "agent_affinities": {
                agent_id: self.get_agent_affinity(agent_id)
                for agent_id in self.agent_resonance_map.keys()
            },
            "total_interactions": self.cmni_tracker._activation_count,
            "tracked_agents": len(self.agent_resonance_map),
        }

    def is_empathy_threshold_met(self, threshold: float = 0.4) -> bool:
        """
        Check if current CMNI meets a minimum integration threshold.

        Used by Elliot Clause evaluation to assess integration gradients.
        """
        return self.cmni_tracker.current_cmni >= threshold
