import warnings
from typing import Any, Dict, Optional

import numpy as np

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"  # noqa: N806


class VoiceEngine:
    """Agent's voice/style engine. Includes serialization."""

    def __init__(self, agent_id: str, initial_style: Optional[Dict] = None):
        self.agent_id = agent_id
        # Default linguistic signature
        self.linguistic_signature = {
            "style_vector": np.random.rand(64) * 0.5 + 0.25,  # Example dimension
            "archetype": "neutral",
            "sentence_structure": "declarative",
            "vocabulary_richness": 0.5,
        }
        if initial_style:
            # Validate and update with initial style if provided
            if "style_vector" in initial_style and isinstance(
                initial_style["style_vector"], list
            ):
                initial_style["style_vector"] = np.array(initial_style["style_vector"])
            self.linguistic_signature.update(initial_style)

    def generate_response(self, prompt: str) -> str:
        """Generates a stylized response based on the prompt
        and signature. (Placeholder)"""
        style = self.linguistic_signature.get("archetype", "unknown")
        structure = self.linguistic_signature.get("sentence_structure", "simple")
        # Extract context (e.g., last relevant line of prompt)
        context_lines = [
            line.strip() for line in prompt.strip().splitlines() if line.strip()
        ]
        context = context_lines[-1] if context_lines else "prompt"
        return f"[{style}/{structure}] Response to: {context[:60]}..."

    def evolve_style(self, influence: Dict):
        """Evolves the linguistic signature based on external influence."""
        if "archetype" in influence and isinstance(influence["archetype"], str):
            self.linguistic_signature["archetype"] = influence["archetype"]
        if "sentence_structure" in influence and isinstance(
            influence["sentence_structure"], str
        ):
            self.linguistic_signature["sentence_structure"] = influence[
                "sentence_structure"
            ]
        if "vocabulary_richness" in influence and isinstance(
            influence["vocabulary_richness"], (int, float)
        ):
            self.linguistic_signature["vocabulary_richness"] = np.clip(
                influence["vocabulary_richness"], 0.0, 1.0
            )

        # Apply shift to style vector based on influence type or magnitude
        shift_magnitude = influence.get("shift_magnitude", 0.1)
        if influence.get("archetype") == "enlightened":
            shift_magnitude = 0.2  # Example specific shift

        if isinstance(self.linguistic_signature["style_vector"], np.ndarray):
            noise = (
                np.random.rand(*self.linguistic_signature["style_vector"].shape) - 0.5
            ) * shift_magnitude
            self.linguistic_signature["style_vector"] += noise
            # Optional: Normalize or clip the vector to prevent unbounded
            # growth
            # norm = np.linalg.norm(
            #     self.linguistic_signature["style_vector"])
            # if norm > 1.0:
            #     self.linguistic_signature["style_vector"] /= norm

    def to_dict(self) -> Dict:
        """Serializes the voice engine state."""
        sig = self.linguistic_signature.copy()
        if "style_vector" in sig and isinstance(sig["style_vector"], np.ndarray):
            sig["style_vector"] = sig["style_vector"].tolist()  # Convert numpy array
        return {"version": FRAMEWORK_VERSION, "linguistic_signature": sig}

    @classmethod
    def from_dict(cls, data: Dict[str, Any], agent_id: str) -> "VoiceEngine":
        """Reconstructs the voice engine from serialized data."""
        loaded_version = data.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Agent {agent_id}: Loading voice state v "
                f"'{loaded_version}' into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )

        instance = cls(agent_id=agent_id)  # Basic init
        sig_data = data.get("linguistic_signature", {})
        if "style_vector" in sig_data and isinstance(sig_data["style_vector"], list):
            # Ensure loaded vector has correct shape if needed
            try:
                loaded_vector = np.array(sig_data["style_vector"])
                # Check shape against default if necessary, e.g., expected_shape = (64,)
                # if loaded_vector.shape != expected_shape: ... handle error ...
                sig_data["style_vector"] = loaded_vector
            except Exception as e:
                warnings.warn(
                    f"Agent {agent_id}: Failed to load style vector: {e}. "
                    f"Using default.",
                    RuntimeWarning,
                )
                sig_data["style_vector"] = instance.linguistic_signature[
                    "style_vector"
                ]  # Fallback

        # Update the instance's signature, preserving defaults if keys are missing
        instance.linguistic_signature.update(sig_data)
        return instance
