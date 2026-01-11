import random
import time
import warnings
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Optional

import numpy as np

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"  # noqa: N806

# Forward reference for type hints
if TYPE_CHECKING:
    from .voice import VoiceEngine


class TemporalResonanceTracker:
    """Tracks vectors over time for an agent. Includes serialization."""

    def __init__(self, agent_id: str, resonance_threshold: float = 0.82):
        self.agent_id = agent_id
        self.history: dict[float, dict[str, Any]] = (
            {}
        )  # {timestamp: {"vector": list, "theme": str, "content": Dict}}
        self.resonance_threshold = resonance_threshold

    def record_state(
        self,
        timestamp: float,
        vector: np.ndarray,
        theme: str,
        content: Optional[dict] = None,
    ):
        if vector is not None and theme is not None:
            self.history[timestamp] = {
                "vector": vector.tolist(),
                "theme": theme,
                "content": content or {},
            }

    def detect_echo(self, current_vector: np.ndarray, current_theme: str) -> list[dict]:
        # ... (logic from previous combined file) ...
        echoes = []
        if current_vector is None or current_theme is None:
            return echoes
        current_norm = np.linalg.norm(current_vector)
        if current_norm < 1e-6:
            return echoes
        past_data = [
            (ts, state.get("vector"), state.get("theme"), state.get("content"))
            for ts, state in self.history.items()
            if state.get("theme") == current_theme and state.get("vector")
        ]
        if not past_data:
            return echoes
        try:
            past_timestamps, past_vectors_list, past_themes, past_contents = zip(
                *past_data
            )
            past_vectors_array = np.array(past_vectors_list)
            past_norms = np.linalg.norm(past_vectors_array, axis=1)
            valid_indices = past_norms > 1e-6
            if not np.any(valid_indices):
                return echoes
            past_vectors_array = past_vectors_array[valid_indices]
            past_norms = past_norms[valid_indices]
            past_timestamps = np.array(past_timestamps)[valid_indices]
            past_contents = [
                past_contents[i] for i, valid in enumerate(valid_indices) if valid
            ]
            past_themes = [
                past_themes[i] for i, valid in enumerate(valid_indices) if valid
            ]
            similarities = np.dot(past_vectors_array, current_vector) / (
                past_norms * current_norm
            )
            similarities = np.clip(similarities, 0.0, 1.0)
            echo_indices = np.where(similarities > self.resonance_threshold)[0]
            current_time = time.time()
            for idx in echo_indices:
                ts = past_timestamps[idx]
                echoes.append(
                    {
                        "similarity": float(similarities[idx]),
                        "delta_t": current_time - ts,
                        "previous_manifestation_timestamp": float(ts),
                        "previous_manifestation_theme": past_themes[idx],
                        "previous_manifestation_content": past_contents[idx],
                    }
                )
            return sorted(echoes, key=lambda x: x["similarity"], reverse=True)
        except (
            ValueError
        ) as e:  # Handle potential errors during unpacking or array creation
            warnings.warn(
                f"Agent {self.agent_id}: Error during echo detection - {e}",
                RuntimeWarning,
            )
            return []

    def get_history_summary(self, limit: int = 20) -> list[dict]:
        sorted_ts = sorted(self.history.keys(), reverse=True)
        summary = []
        for ts in sorted_ts[:limit]:
            state = self.history[ts]
            vector_list = state.get("vector")
            summary.append(
                {
                    "timestamp": ts,
                    "theme": state.get("theme"),
                    "vector_norm": (
                        float(np.linalg.norm(vector_list)) if vector_list else 0.0
                    ),
                    "content_keys": list(state.get("content", {}).keys()),
                }
            )
        return summary

    def to_dict(self, history_limit: Optional[int] = None) -> dict:
        history_to_save = self.history
        if history_limit is not None:
            sorted_ts = sorted(self.history.keys(), reverse=True)[:history_limit]
            history_to_save = {ts: self.history[ts] for ts in sorted_ts}
        return {
            "version": FRAMEWORK_VERSION,
            "resonance_threshold": self.resonance_threshold,
            "history": history_to_save,
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], agent_id: str
    ) -> "TemporalResonanceTracker":
        loaded_version = data.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Agent {agent_id}: Loading resonance v "
                f"'{loaded_version}' into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )
        instance = cls(
            agent_id=agent_id,
            resonance_threshold=data.get("resonance_threshold", 0.82),
        )
        instance.history = data.get("history", {})  # Vectors are already lists
        return instance


class ResonanceLiturgy:
    """Handles the agent's 'ritual' response to temporal resonance.
    (Stateless, no serialization needed)"""

    def __init__(self, agent_id: str, satori_threshold: float = 0.9):
        self.agent_id = agent_id
        self.satori_threshold = satori_threshold
        self.ritual_phrases = [
            "I recognize this shadow of myself.",
            "An older voice speaks through me.",
            "The past breathes anew...",
            "This pattern feels familiar...",
            "A thread connects me...",
        ]  # Shortened

    def _format_timedelta(self, delta_seconds: float) -> str:
        # ... (timedelta formatting logic) ...
        try:
            delta = timedelta(seconds=int(delta_seconds))
            days, rem_secs = delta.days, delta.seconds
            hours, rem_secs = divmod(rem_secs, 3600)
            minutes, seconds = divmod(rem_secs, 60)
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if not parts and seconds >= 0:
                parts.append(f"{seconds}s")
            if not parts:
                return "instant"
            return " ".join(parts)
        except ValueError:
            return f"{delta_seconds:.0f}s"

    def compose_commentary(self, echo: dict) -> str:
        elapsed_str = self._format_timedelta(echo["delta_t"])
        phrase = random.choice(self.ritual_phrases)
        return (
            f"Resonance {echo['similarity']:.3f} echoes self "
            f"from ~{elapsed_str} ago. {phrase}"
        )

    def generate_response_ritual(
        self, voice_engine: "VoiceEngine", current_theme: str, past_theme: str
    ) -> str:
        # Need to import VoiceEngine for type hint or use string
        ritual_phrase = random.choice(self.ritual_phrases)
        arch = voice_engine.linguistic_signature["archetype"]
        struct = voice_engine.linguistic_signature["sentence_structure"]
        vocab = voice_engine.linguistic_signature["vocabulary_richness"]
        prompt = (
            f"Context: Echo ({ritual_phrase}) connects '{current_theme}' "
            f"to past '{past_theme}'.\n"
            f"Task: Brief response acknowledging connection, "
            f"linking past to present.\n"
            f"Style: Arch: {arch}, Struct: {struct}, Vocab: {vocab:.1f}"
        )
        return voice_engine.generate_response(prompt)

    def to_dict(self) -> dict:
        """Serialize ResonanceLiturgy state."""
        return {
            "version": FRAMEWORK_VERSION,
            "agent_id": self.agent_id,
            "satori_threshold": self.satori_threshold,
            "ritual_phrases": self.ritual_phrases.copy(),
        }

    @classmethod
    def from_dict(
        cls, data: dict, agent_id: Optional[str] = None
    ) -> "ResonanceLiturgy":
        """Reconstruct ResonanceLiturgy from serialized state.

        Args:
            data: Serialized state dictionary
            agent_id: Optional agent_id override (uses data['agent_id'] if not provided)

        Returns:
            Reconstructed ResonanceLiturgy instance
        """
        loaded_version = data.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Loading ResonanceLiturgy v '{loaded_version}' "
                f"into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )

        # Use provided agent_id or fall back to serialized one
        final_agent_id = (
            agent_id if agent_id is not None else data.get("agent_id", "unknown")
        )

        instance = cls(
            agent_id=final_agent_id,
            satori_threshold=data.get("satori_threshold", 0.9),
        )

        # Restore ritual phrases if they were customized
        if "ritual_phrases" in data:
            instance.ritual_phrases = data["ritual_phrases"]

        return instance
