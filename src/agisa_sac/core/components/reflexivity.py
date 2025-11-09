import time
import warnings
from typing import TYPE_CHECKING

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"

# Use TYPE_CHECKING for agent hint to avoid circular import
if TYPE_CHECKING:
    from ..agent import EnhancedAgent


class ReflexivityLayer:
    """Handles agent self-reflection and meta-cognition.
    (State managed via agent ref, no extra serialization needed here)"""

    def __init__(self, agent: "EnhancedAgent"):
        """Initializes with a reference to the owning agent."""
        if not hasattr(
            agent, "agent_id"
        ):  # Basic check for valid agent object
            raise TypeError(
                "Agent reference is required for ReflexivityLayer."
            )
        self.agent = agent

    def force_deep_reflection(self, trigger: str):
        """Initiate identity-realignment sequence (Satori Event)."""
        if not all(
            hasattr(self.agent, attr)
            for attr in ["voice", "memory", "cognitive"]
        ):
            warnings.warn(
                f"Agent {self.agent.agent_id}: Missing components for deep reflection.",
                RuntimeWarning,
            )
            return

        old_style = self.agent.voice.linguistic_signature.copy()
        # Evolve voice style
        self.agent.voice.evolve_style(
            influence={
                "archetype": "enlightened",
                "sentence_structure": "paradoxical",
            }
        )
        # Add Satori memory event
        satori_memory_content = {
            "type": "satori_event",
            "trigger": trigger,
            "timestamp": time.time(),
            "theme": "self_reflection",
            "reflection_details": {
                "old_style_archetype": old_style.get("archetype"),
                "new_style_archetype": self.agent.voice.linguistic_signature.get(
                    "archetype"
                ),
            },
        }
        # Use agent's memory component to add memory
        self.agent.memory.add_memory(satori_memory_content, importance=1.0)

        # Optional: Trigger cognitive heuristic changes here if desired
        # e.g., self.agent.cognitive.heuristics =
        #     self._apply_satori_heuristic_shift(
        #         self.agent.cognitive.heuristics)

        if self.agent.message_bus:
            self.agent.message_bus.publish(
                "agent_satori_event",
                {"agent_id": self.agent.agent_id, "trigger": trigger},
            )

    # Optional helper for heuristic shifts during satori
    # def _apply_satori_heuristic_shift(self, current_heuristics):
    #     # Example: Increase novelty/creativity focus
    #     shifted = current_heuristics.copy()
    #     shifted[2, 1] += 0.1 # Novelty -> Creative
    #     shifted[2, 2] += 0.1 # Novelty -> Balanced
    #     return np.clip(shifted, 0.1, 0.9)
