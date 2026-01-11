import math
from collections import Counter
from typing import TYPE_CHECKING, Any

import numpy as np

from agisa_sac.metrics import monitoring

# Use TYPE_CHECKING for agent hint if EnhancedAgent imports this module
if TYPE_CHECKING:
    from ..agent import EnhancedAgent


class AgentStateAnalyzer:
    """Computes system-wide metrics based on the current state of all agents."""

    def __init__(self, agents: dict[str, "EnhancedAgent"]):
        if not isinstance(agents, dict):
            raise TypeError("Input 'agents' must be a dictionary.")
        self.agents = agents
        self.num_agents = len(agents)

    def compute_archetype_distribution(self) -> dict[str, int]:
        """Calculates the frequency distribution of declared agent archetypes."""
        if not self.agents:
            return {}
        return Counter(
            agent.voice.linguistic_signature.get("archetype", "unknown")
            for agent in self.agents.values()
            if hasattr(agent, "voice")
        )

    def compute_satori_wave_ratio(self, threshold: float = 0.88) -> float:
        """Calculates proportion of agents meeting satori echo threshold. (Canonical)"""
        if not self.agents:
            return 0.0
        satori_count = 0
        for agent in self.agents.values():
            if not all(
                hasattr(agent, attr)
                for attr in ["temporal_resonance", "voice", "memory"]
            ):
                continue
            current_style_vector = agent.voice.linguistic_signature.get("style_vector")
            try:
                current_theme = agent.memory.get_current_focus_theme()
            except Exception:
                current_theme = None
            if current_style_vector is None or current_theme is None:
                continue
            detected_echoes = agent.temporal_resonance.detect_echo(
                current_style_vector, current_theme
            )
            if detected_echoes and detected_echoes[0]["similarity"] >= threshold:
                satori_count += 1
        return satori_count / self.num_agents if self.num_agents > 0 else 0.0

    def compute_archetype_entropy(
        self, distribution: dict[str, int] | None = None
    ) -> float:
        """Calculates the Shannon entropy of the archetype distribution."""
        if distribution is None:
            distribution = self.compute_archetype_distribution()
        if not distribution:
            return 0.0
        total_agents = sum(distribution.values())
        if total_agents == 0:
            return 0.0
        entropy = 0.0
        for count in distribution.values():
            if count > 0:
                probability = count / total_agents
                entropy -= probability * math.log2(probability)
        return entropy

    def compute_mean_resonance_strength(self) -> float:
        """Calculates the average similarity of the strongest echo
        for agents with echoes."""
        if not self.agents:
            return 0.0
        similarities = []
        for agent in self.agents.values():
            if not all(
                hasattr(agent, attr)
                for attr in ["temporal_resonance", "voice", "memory"]
            ):
                continue
            current_style_vector = agent.voice.linguistic_signature.get("style_vector")
            try:
                current_theme = agent.memory.get_current_focus_theme()
            except Exception:
                current_theme = None
            if current_style_vector is None or current_theme is None:
                continue
            detected_echoes = agent.temporal_resonance.detect_echo(
                current_style_vector, current_theme
            )
            if detected_echoes:
                similarities.append(detected_echoes[0]["similarity"])
        return float(np.mean(similarities)) if similarities else 0.0

    def summarize(self, satori_threshold: float = 0.88) -> dict[str, Any]:
        """Computes and returns a dictionary containing all key system metrics."""
        if not self.agents:
            return {
                "satori_wave_ratio": 0.0,
                "archetype_distribution": {},
                "archetype_entropy": 0.0,
                "mean_resonance_strength": 0.0,
                "agent_count": 0,
            }
        distribution = self.compute_archetype_distribution()
        summary = {
            "satori_wave_ratio": self.compute_satori_wave_ratio(
                threshold=satori_threshold
            ),
            "archetype_distribution": distribution,
            "archetype_entropy": self.compute_archetype_entropy(
                distribution=distribution
            ),
            "mean_resonance_strength": self.compute_mean_resonance_strength(),
            "agent_count": self.num_agents,
        }
        return summary

    def generate_monitoring_metrics(self) -> dict[str, dict[str, float]]:
        """Return monitoring metrics for each agent."""
        metrics: dict[str, dict[str, float]] = {}
        for agent_id, agent in self.agents.items():
            metrics[agent_id] = monitoring.generate_monitoring_metrics(agent)
        return metrics
