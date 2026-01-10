# In cognee/memory/hierarchical/decay.py
import math
from typing import Dict
from cognee.memory.hierarchical.config import MemoryGenome


class MemoryDecayModel:
    """Implements the Ebbinghaus forgetting curve with reinforcement"""

    def __init__(self, genome: MemoryGenome):
        self.genome = genome

    def calculate_strength(
        self, memory: Dict, time_elapsed: float, access_count: int
    ) -> float:
        """
        Calculates the current retrieval strength of a memory.
        """
        base = math.exp(-time_elapsed / self.genome.decay_constant)
        usage = 1 + math.log(1 + access_count) * self.genome.usage_reinforcement_gain
        emotional_boost = 1 + (
            memory.get("emotional_valence", 0) * self.genome.emotional_weight_multiplier
        )

        return float(min(1.0, base * usage * emotional_boost))
