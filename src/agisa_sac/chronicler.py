import time
import warnings
from collections import defaultdict
from typing import Dict, List, Any, TYPE_CHECKING

try:
    from . import FRAMEWORK_VERSION
except ImportError:  # pragma: no cover - fallback for standalone use
    FRAMEWORK_VERSION = "unknown"

if TYPE_CHECKING:  # pragma: no cover
    from .agent import EnhancedAgent

class ResonanceChronicler:
    """Collects per-epoch summaries for each agent."""
    def __init__(self):
        self.lineages: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def record_epoch(self, agent: 'EnhancedAgent', epoch: int):
        """Capture summary information from ``agent`` for ``epoch``."""
        if agent is None:
            raise ValueError("agent required")
        try:
            theme = agent.memory.get_current_focus_theme()
        except Exception:
            theme = None
        style_vec = None
        if getattr(agent, 'voice', None) is not None:
            style_vec = agent.voice.linguistic_signature.get("style_vector")
        echo_strength = None
        if style_vec is not None and getattr(agent, 'temporal_resonance', None):
            try:
                echoes = agent.temporal_resonance.detect_echo(style_vec, theme)
                if echoes:
                    echo_strength = float(echoes[0]["similarity"])
            except Exception as e:  # pragma: no cover - noncritical
                warnings.warn(f"Chronicler echo detection failed for {agent.agent_id}: {e}", RuntimeWarning)
        cog_state = None
        if getattr(agent, 'cognitive', None) is not None and getattr(agent.cognitive, 'cognitive_state', None) is not None:
            state = agent.cognitive.cognitive_state
            if hasattr(state, "tolist"):
                cog_state = state.tolist()
            else:
                cog_state = list(state)
        entry = {
            "epoch": epoch,
            "timestamp": time.time(),
            "theme": theme,
            "cognitive_state": cog_state,
            "echo_strength": echo_strength,
            "reflection": getattr(agent, 'last_reflection_trigger', None),
        }
        self.lineages[agent.agent_id].append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of all recorded data."""
        return {
            "version": FRAMEWORK_VERSION,
            "lineages": {aid: list(entries) for aid, entries in self.lineages.items()},
        }
