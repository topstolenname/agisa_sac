"""Configuration management for AGI-SAC simulations.

This module provides configuration presets and validation for simulation runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SimulationConfig:
    """Configuration for AGI-SAC simulation runs."""

    # Agent configuration
    num_agents: int = 5
    agent_capacity: int = 100
    personalities: Optional[List[Dict[str, float]]] = None

    # Simulation parameters
    num_epochs: int = 10
    random_seed: Optional[int] = 42

    # Feature flags
    use_semantic: bool = True
    use_gpu: bool = False

    # Analysis configuration
    tda_max_dimension: int = 1
    satori_threshold_analyzer: float = 0.88

    # Logging and monitoring
    community_check_frequency: int = 5
    epoch_log_frequency: int = 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "num_agents": self.num_agents,
            "num_epochs": self.num_epochs,
            "random_seed": self.random_seed,
            "agent_capacity": self.agent_capacity,
            "use_semantic": self.use_semantic,
            "use_gpu": self.use_gpu,
            "tda_max_dimension": self.tda_max_dimension,
            "community_check_frequency": self.community_check_frequency,
            "epoch_log_frequency": self.epoch_log_frequency,
            "satori_threshold_analyzer": self.satori_threshold_analyzer,
            "personalities": self.personalities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SimulationConfig:
        """Create configuration from dictionary."""
        return cls(
            **{k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        )


# Configuration Presets
QUICK_TEST = SimulationConfig(
    num_agents=3,
    num_epochs=5,
    random_seed=1,
    agent_capacity=50,
    use_semantic=False,
    use_gpu=False,
    tda_max_dimension=1,
    community_check_frequency=2,
    epoch_log_frequency=1,
    satori_threshold_analyzer=0.90,
)

DEFAULT = SimulationConfig(
    num_agents=5,
    num_epochs=10,
    random_seed=42,
    agent_capacity=100,
    use_semantic=True,
    use_gpu=False,
    tda_max_dimension=1,
    community_check_frequency=5,
    epoch_log_frequency=2,
    satori_threshold_analyzer=0.88,
)

MEDIUM = SimulationConfig(
    num_agents=20,
    num_epochs=50,
    random_seed=123,
    agent_capacity=150,
    use_semantic=True,
    use_gpu=False,
    tda_max_dimension=2,
    community_check_frequency=10,
    epoch_log_frequency=10,
    satori_threshold_analyzer=0.85,
)

LARGE = SimulationConfig(
    num_agents=100,
    num_epochs=100,
    random_seed=None,
    agent_capacity=200,
    use_semantic=True,
    use_gpu=False,
    tda_max_dimension=1,
    community_check_frequency=5,
    epoch_log_frequency=20,
    satori_threshold_analyzer=0.88,
)

# Preset registry
PRESETS = {
    "quick_test": QUICK_TEST,
    "default": DEFAULT,
    "medium": MEDIUM,
    "large": LARGE,
}


def get_preset(name: str) -> SimulationConfig:
    """Get a configuration preset by name.

    Args:
        name: Preset name (quick_test, default, medium, large)

    Returns:
        SimulationConfig instance

    Raises:
        KeyError: If preset name not found
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]


__all__ = [
    "SimulationConfig",
    "QUICK_TEST",
    "DEFAULT",
    "MEDIUM",
    "LARGE",
    "PRESETS",
    "get_preset",
]
