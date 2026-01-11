# In cognee/memory/hierarchical/config.py
from pydantic import BaseModel, Field
from typing import Literal


class MemoryGenome(BaseModel):
    """Cognitive configuration validated against biological constraints"""

    sensory_buffer_capacity: int = Field(
        100, ge=50, le=500, description="Milliseconds of sensory retention"
    )
    working_memory_limit: int = Field(
        7, ge=5, le=11, description="Miller's Law ±2 items"
    )
    episodic_salience_threshold: float = Field(
        0.5,
        ge=0.1,
        le=0.9,
        description="Minimum emotional valence for episodic storage",
    )
    semantic_strengthening_rate: float = Field(
        0.3, ge=0.05, le=0.5, description="Rate of fact reinforcement"
    )
    procedural_learning_threshold: float = Field(
        0.1, ge=0.01, le=0.2, description="Confidence threshold for skill acquisition"
    )
    decay_constant: float = Field(
        500.0, ge=100.0, le=1000.0, description="Ebbinghaus time constant (seconds)"
    )
    emotional_weight_multiplier: float = Field(
        2.0, ge=1.0, le=5.0, description="Amplifier for salient memories"
    )
    usage_reinforcement_gain: float = Field(
        0.1, ge=0.05, le=0.3, description="Logarithmic gain for access frequency"
    )

    version: Literal["1.0"] = "1.0"  # For migration path
