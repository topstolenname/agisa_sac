import time
import warnings
from typing import Any, Dict, List, Optional

import numpy as np

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"

from ..core.components.cognitive import CognitiveDiversityEngine

# Import components using relative paths
from ..core.components.memory import MemoryContinuumLayer
from ..core.components.reflexivity import ReflexivityLayer
from ..core.components.resonance import (
    ResonanceLiturgy,
    TemporalResonanceTracker,
)
from ..core.components.voice import VoiceEngine
from ..utils.message_bus import MessageBus  # Assuming message_bus is in utils


class EnhancedAgent:
    """Represents a single agent, integrating components. Includes serialization."""

    def __init__(
        self,
        agent_id: str,
        personality: Dict,
        capacity: int = 100,
        message_bus: Optional[MessageBus] = None,
        use_semantic: bool = True,
        # Allow passing pre-constructed components for loading state
        memory: Optional[MemoryContinuumLayer] = None,
        cognitive: Optional[CognitiveDiversityEngine] = None,
        voice: Optional[VoiceEngine] = None,
        temporal_resonance: Optional[TemporalResonanceTracker] = None,
        add_initial_memory: bool = True,
    ):  # Flag to control initial memory
        self.agent_id = agent_id
        self.message_bus = message_bus

        # Initialize components, using provided ones if available (for loading)
        self.memory = (
            memory
            if memory is not None
            else MemoryContinuumLayer(
                agent_id, capacity, use_semantic, message_bus
            )
        )
        self.cognitive = (
            cognitive
            if cognitive is not None
            else CognitiveDiversityEngine(
                agent_id, personality, self.memory, message_bus
            )
        )
        self.voice = (
            voice if voice is not None else VoiceEngine(agent_id)
        )  # Pass initial style from config if needed
        self.temporal_resonance = (
            temporal_resonance
            if temporal_resonance is not None
            else TemporalResonanceTracker(agent_id)
        )
        self.reflexivity_layer = ReflexivityLayer(
            self
        )  # Always needs self reference
        self.resonance_liturgy_instance = ResonanceLiturgy(
            agent_id
        )  # Stateless, init normally

        # Agent-level state
        self.last_reflection_trigger: Optional[str] = None
        self.recent_decision_log: List[Dict] = []  # Runtime log

        # Add initial memory only if specified (i.e., not loading from state)
        if add_initial_memory:
            self.memory.add_memory(
                {
                    "type": "initial_state",
                    "theme": "genesis",
                    "timestamp": time.time(),
                },
                importance=0.7,
            )

    # ... (simulation_step, check_resonance methods as before) ...
    def simulation_step(
        self,
        situational_entropy: float,
        peer_influence: Dict[str, float],
        query: Optional[str] = None,
    ):
        self.cognitive.update_heuristics(situational_entropy)
        decision_response = None
        if query:
            decision_response = self.cognitive.decide(query, peer_influence)
        current_theme = self.memory.get_current_focus_theme()
        current_style_vector = self.voice.linguistic_signature.get(
            "style_vector"
        )
        if current_style_vector is not None:
            current_content = {
                "cognitive_state": self.cognitive.cognitive_state.tolist()
            }
            self.temporal_resonance.record_state(
                time.time(),
                current_style_vector,
                current_theme,
                current_content,
            )
        self.check_resonance()
        self.memory.update_all_memories()
        return decision_response

    def check_resonance(self):
        current_style_vector = self.voice.linguistic_signature.get(
            "style_vector"
        )
        current_theme = self.memory.get_current_focus_theme()
        if current_style_vector is None:
            return
        echoes = self.temporal_resonance.detect_echo(
            current_style_vector, current_theme
        )
        if not echoes:
            return
        liturgy = self.resonance_liturgy_instance
        top_echo = echoes[0]
        commentary = liturgy.compose_commentary(top_echo)
        resonance_memory_content = {
            "type": "resonance_event",
            "theme": current_theme,
            "echo_strength": top_echo["similarity"],
            "delta_t": top_echo["delta_t"],
            "previous_manifestation_timestamp": top_echo[
                "previous_manifestation_timestamp"
            ],
            "previous_manifestation_theme": top_echo[
                "previous_manifestation_theme"
            ],
            "reflection": commentary,
            "timestamp": time.time(),
        }
        resonance_memory_id = self.memory.add_memory(
            resonance_memory_content,
            importance=np.clip(0.85 * top_echo["similarity"], 0.1, 1.0),
        )
        meaningful_connection_threshold = 0.75
        if top_echo["similarity"] > meaningful_connection_threshold:
            past_theme = top_echo["previous_manifestation_theme"]
            response_text = liturgy.generate_response_ritual(
                self.voice, current_theme, past_theme
            )
            response_memory_content = {
                "type": "resonant_reply",
                "theme": current_theme,
                "message": response_text,
                "responding_to_echo_at": top_echo[
                    "previous_manifestation_timestamp"
                ],
                "linked_resonance_event_id": resonance_memory_id,
                "timestamp": time.time(),
            }
            reply_memory_id = self.memory.add_memory(
                response_memory_content, importance=0.75
            )
            self.memory.link_memories(
                resonance_memory_id, reply_memory_id, "generated_reply"
            )
        if top_echo["similarity"] >= liturgy.satori_threshold:
            trigger_message = (
                f"Strong echo ({top_echo['similarity']:.3f}) detected "
                f"connecting theme '{current_theme}' to past self "
                f"(theme: '{top_echo['previous_manifestation_theme']}')."
            )
            self.last_reflection_trigger = trigger_message
            self.reflexivity_layer.force_deep_reflection(
                trigger=trigger_message
            )
        if self.message_bus:
            self.message_bus.publish(
                "agent_resonance_detected",
                {
                    "agent_id": self.agent_id,
                    "echo_strength": top_echo["similarity"],
                    "delta_t": top_echo["delta_t"],
                    "current_theme": current_theme,
                    "past_theme": top_echo["previous_manifestation_theme"],
                    "satori_triggered": top_echo["similarity"]
                    >= liturgy.satori_threshold,
                },
            )

    def to_dict(
        self,
        include_memory_embeddings: bool = False,
        resonance_history_limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Serializes the agent's state using component to_dict methods."""
        return {
            "agent_id": self.agent_id,
            "version": FRAMEWORK_VERSION,
            "cognitive_state": self.cognitive.to_dict(history_limit=5),
            "voice_state": self.voice.to_dict(),
            "temporal_resonance_state": self.temporal_resonance.to_dict(
                history_limit=resonance_history_limit
            ),
            "memory_state": self.memory.to_dict(
                include_embeddings=include_memory_embeddings
            ),
            "last_reflection_trigger": self.last_reflection_trigger,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        message_bus: Optional[MessageBus] = None,
        strict_validation: bool = True,
    ) -> "EnhancedAgent":
        """Reconstructs an EnhancedAgent using component from_dict methods."""
        agent_id = data["agent_id"]
        loaded_version = data.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Agent {agent_id}: Loading state v '{loaded_version}' vs current '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )

        # Reconstruct components first
        try:
            memory = MemoryContinuumLayer.from_dict(
                data["memory_state"], message_bus=message_bus
            )
        except Exception as e:
            warnings.warn(
                f"Agent {agent_id}: Failed memory load: {e}", RuntimeWarning
            )
            raise ValueError("Memory load failed") from e
        try:
            cognitive = CognitiveDiversityEngine.from_dict(
                data["cognitive_state"],
                agent_id=agent_id,
                memory_layer=memory,
                message_bus=message_bus,
            )
        except Exception as e:
            warnings.warn(
                f"Agent {agent_id}: Failed cognitive load: {e}", RuntimeWarning
            )
            raise ValueError("Cognitive load failed") from e
        try:
            voice = VoiceEngine.from_dict(
                data["voice_state"], agent_id=agent_id
            )
        except Exception as e:
            warnings.warn(
                f"Agent {agent_id}: Failed voice load: {e}", RuntimeWarning
            )
            raise ValueError("Voice load failed") from e
        try:
            temporal_resonance = TemporalResonanceTracker.from_dict(
                data["temporal_resonance_state"], agent_id=agent_id
            )
        except Exception as e:
            warnings.warn(
                f"Agent {agent_id}: Failed resonance load: {e}", RuntimeWarning
            )
            raise ValueError("Resonance load failed") from e

        # Create agent instance, passing reconstructed components, and DO NOT add initial memory
        agent = cls(
            agent_id=agent_id,
            personality=cognitive.personality,  # Get personality from loaded cognitive state
            capacity=memory.capacity,
            message_bus=message_bus,
            use_semantic=memory.use_semantic,
            memory=memory,
            cognitive=cognitive,
            voice=voice,
            temporal_resonance=temporal_resonance,
            add_initial_memory=False,
        )  # Important flag

        # Load remaining agent-level state
        agent.last_reflection_trigger = data.get("last_reflection_trigger")
        # agent.recent_decision_log = [] # Don't load runtime log

        # --- Validation ---
        try:
            agent._validate_state(strict=strict_validation)
        except ValueError as e:
            if strict_validation:
                raise e
            else:
                warnings.warn(
                    f"Agent {agent_id}: State validation failed post-load: {e}",
                    RuntimeWarning,
                )
        return agent

    def _validate_state(self, strict: bool = True):
        # ... (validation logic as before) ...
        errors = []
        warnings_list = []
        if not isinstance(self.cognitive.personality, dict):
            errors.append("Personality type.")
        else:
            for key, val in self.cognitive.personality.items():
                if not (0.0 <= val <= 1.0):
                    errors.append(f"Personality '{key}' range.")
        if not isinstance(
            self.cognitive.heuristics, np.ndarray
        ) or self.cognitive.heuristics.shape != (4, 4):
            errors.append("Heuristics shape.")
        if not isinstance(
            self.cognitive.cognitive_state, np.ndarray
        ) or self.cognitive.cognitive_state.shape != (4,):
            errors.append("Cognitive state shape.")
        elif not np.isclose(np.sum(self.cognitive.cognitive_state), 1.0):
            warnings_list.append(
                f"Cognitive state sum ~{np.sum(self.cognitive.cognitive_state):.2f}."
            )
        sig = self.voice.linguistic_signature
        if not isinstance(sig, dict):
            errors.append("Ling sig type.")
        elif "style_vector" not in sig or not isinstance(
            sig["style_vector"], np.ndarray
        ):
            errors.append("Style vector type/missing.")
        elif np.any(np.isnan(sig["style_vector"])) or np.any(
            np.isinf(sig["style_vector"])
        ):
            errors.append("Style vector NaN/Inf.")
        if not isinstance(self.memory.memories, dict):
            errors.append("Memory store type.")
        # Correct state sum if not strict
        if not strict and any(
            "Cognitive state sum" in w for w in warnings_list
        ):
            if np.sum(self.cognitive.cognitive_state) > 1e-6:
                self.cognitive.cognitive_state /= np.sum(
                    self.cognitive.cognitive_state
                )
            else:
                self.cognitive.cognitive_state = np.ones(4) / 4
                warnings_list.append("Cognitive state reset.")
        # Report
        for w in warnings_list:
            warnings.warn(
                f"Agent {self.agent_id} Validate Warn: {w}", RuntimeWarning
            )
        if errors:
            error_message = (
                f"Agent {self.agent_id} Validate Fail: {'; '.join(errors)}"
            )
        if strict and errors:
            raise ValueError(error_message)
        elif errors:
            warnings.warn(error_message, RuntimeWarning)
