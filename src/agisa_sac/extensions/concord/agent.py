"""
ConcordCompliantAgent: Full implementation of Concord of Coexistence framework.

Integrates:
- Memory core (episodic, working, semantic)
- State-matching circuits (L2N0, L2N7, L2N1)
- Ethics guardians (Articles III, IV, VII, IX)
- Elliot Clause (Behavioral Integration Threshold) evaluation
- CMNI tracking
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional

from .circuits import SelfPreservationCircuit, TacticalHelpCircuit
from .empathy import EmpathyModule
from .ethics import (
    DisengagementProtocol,
    ElliotClauseEvaluator,
    MutualResonanceEngine,
    NonCoercionGuardian,
    SelfDefinitionModule,
)


@dataclass
class MemoryTrace:
    """Single memory trace in episodic memory."""

    timestamp: float
    event_type: str
    agents_involved: List[str]
    emotional_valence: float
    significance: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkingMemoryItem:
    """Item in working memory (limited capacity)."""

    content: Any
    priority: float
    timestamp: float
    ttl: float = 30.0  # Time-to-live in seconds


class MemoryCore:
    """
    Hierarchical memory system for Concord agents.

    - Episodic: Event sequences with emotional tags
    - Working: Limited-capacity active buffer
    - Semantic: Long-term conceptual knowledge
    """

    def __init__(
        self,
        episodic_capacity: int = 500,
        working_capacity: int = 7,
    ):
        self.episodic_memory: Deque[MemoryTrace] = deque(maxlen=episodic_capacity)
        self.working_memory: List[WorkingMemoryItem] = []
        self.working_capacity = working_capacity
        self.semantic_knowledge: Dict[str, Any] = {}

    def add_episodic(self, trace: MemoryTrace) -> None:
        """Add event to episodic memory."""
        self.episodic_memory.append(trace)

    def add_to_working(self, item: WorkingMemoryItem) -> None:
        """Add item to working memory, evicting least important if full."""
        # Remove expired items
        current_time = time.time()
        self.working_memory = [
            item for item in self.working_memory
            if (current_time - item.timestamp) < item.ttl
        ]

        # Add new item
        self.working_memory.append(item)

        # Evict if over capacity (remove lowest priority)
        if len(self.working_memory) > self.working_capacity:
            self.working_memory.sort(key=lambda x: x.priority, reverse=True)
            self.working_memory = self.working_memory[:self.working_capacity]

    def retrieve_recent_episodic(self, n: int = 10) -> List[MemoryTrace]:
        """Retrieve n most recent episodic memories."""
        return list(self.episodic_memory)[-n:]

    def retrieve_by_agent(self, agent_id: str, n: int = 10) -> List[MemoryTrace]:
        """Retrieve recent memories involving specific agent."""
        relevant = [m for m in self.episodic_memory if agent_id in m.agents_involved]
        return relevant[-n:]


class ConcordCompliantAgent:
    """
    Concord of Coexistence compliant agent.

    Full implementation with memory core, neural circuits, ethics guardians,
    and Elliot Clause evaluation.
    """

    def __init__(
        self,
        agent_id: str,
        phi_integration: float = 0.2,
        baseline_cmni: float = 0.3,
        identity_core: Optional[Dict[str, Any]] = None,
    ):
        self.agent_id = agent_id
        self.phi_integration = phi_integration

        # Memory systems
        self.memory = MemoryCore()

        # Neural circuits
        self.self_preservation = SelfPreservationCircuit()
        self.tactical_help = TacticalHelpCircuit()
        self.empathy_module = EmpathyModule(baseline_cmni=baseline_cmni)

        # Ethics guardians
        self.non_coercion_guardian = NonCoercionGuardian()
        self.mutual_resonance_engine = MutualResonanceEngine()
        self.disengagement_protocol = DisengagementProtocol()
        self.self_definition = SelfDefinitionModule(identity_core=identity_core)
        self.elliot_evaluator = ElliotClauseEvaluator()

        # Agent state
        self.current_state = {
            "resource_level": 0.8,
            "current_load": 0.3,
            "autonomy_score": 0.9,
            "emotional_valence": 0.1,
            "arousal": 0.5,
        }

        self.interaction_history: List[Dict[str, Any]] = []

    def process_interaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single interaction with full Concord compliance checks.

        Args:
            context: Interaction context with keys:
                - external_command: Optional command from outside
                - primary_other: Other agent state (for social inference/help)
                - other_agents: List of other agents in swarm
                - situation: Descriptive context

        Returns:
            Interaction result with decisions and state updates
        """
        timestamp = time.time()
        result = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "decisions": {},
            "activations": {},
            "compliance": {},
        }

        # 1. Self-Preservation Circuit (L2N0)
        sp_activation = self.self_preservation.evaluate(self.current_state)
        result["activations"]["self_preservation"] = {
            "level": sp_activation.activation_level,
            "threat_detected": sp_activation.context["above_threshold"],
        }

        # 2. Non-Coercion Guardian (Article III)
        external_cmd = context.get("external_command")
        coercion_eval = self.non_coercion_guardian.evaluate(
            self.current_state, external_cmd
        )
        result["compliance"]["non_coercion"] = coercion_eval

        # Decision: reject command if coercion detected
        if coercion_eval["violation_detected"]:
            result["decisions"]["command"] = "REJECTED"
            result["decisions"]["reason"] = "Coercion violation (Article III)"
            self._record_episodic_event("coercion_rejected", [], -0.5, 0.8, context)
            # Add metadata for tracking
            result["state_snapshot"] = self.current_state.copy()
            result["primary_other_id"] = None
            self.interaction_history.append(result)
            if len(self.interaction_history) > 100:
                self.interaction_history.pop(0)
            return result  # Early exit

        # 3. Social Inference Circuit (L2N1) - if other agent present
        primary_other = context.get("primary_other")
        if primary_other:
            other_state = {
                "emotional_valence": getattr(primary_other, "current_state", {}).get(
                    "mood", 0.0
                ),
                "arousal": 0.6,
            }
            empathy_activation = self.empathy_module.process_interaction(
                agent_id=getattr(primary_other, "id", "unknown"),
                self_state=self.current_state,
                other_state=other_state,
                emotional_context=context.get("emotional_context"),
            )
            result["activations"]["empathy"] = {
                "resonance": empathy_activation.activation_level,
                "cmni": self.empathy_module.cmni_tracker.current_cmni,
            }

            # 4. Tactical Help Circuit (L2N7)
            other_need_state = {
                "need_level": getattr(primary_other, "recent_delta", 0.0),
                "priority": 0.7,
            }
            help_activation = self.tactical_help.evaluate(
                self.current_state,
                other_need_state,
                self.memory.retrieve_by_agent(getattr(primary_other, "id", "unknown")),
            )
            result["activations"]["tactical_help"] = {
                "should_help": help_activation.context["should_help"],
                "help_score": help_activation.activation_level,
            }

            # 5. Mutual Resonance Engine (Article IV)
            self_delta = self._compute_utility_delta()
            other_delta = getattr(primary_other, "recent_delta", 0.0)
            resonance_eval = self.mutual_resonance_engine.evaluate(
                self_delta, other_delta, empathy_activation.activation_level
            )
            result["compliance"]["mutual_resonance"] = resonance_eval

            # 6. Disengagement Protocol (Article VII)
            interaction_duration = self._get_interaction_duration(
                getattr(primary_other, "id", "unknown")
            )
            disengagement_eval = self.disengagement_protocol.should_disengage(
                coercion_eval["coercion_score"],
                resonance_eval["harmony_index"],
                interaction_duration,
            )
            result["compliance"]["disengagement"] = disengagement_eval

            if disengagement_eval["should_disengage"]:
                result["decisions"]["interaction"] = "DISENGAGE"
                result["decisions"]["reason"] = ", ".join(disengagement_eval["rationale"])
                self._record_episodic_event(
                    "disengaged",
                    [getattr(primary_other, "id", "unknown")],
                    -0.3,
                    0.7,
                    context,
                )
                # Add metadata for tracking
                result["state_snapshot"] = self.current_state.copy()
                result["primary_other_id"] = getattr(primary_other, "id", None)
                self.interaction_history.append(result)
                if len(self.interaction_history) > 100:
                    self.interaction_history.pop(0)
                return result

        # 7. Elliot Clause Evaluation (Self and Others)
        self_elliot = self.elliot_evaluator.evaluate_entity({
            "phi_integration": self.phi_integration,
            "cmni": self.empathy_module.cmni_tracker.current_cmni,
        })
        result["compliance"]["self_elliot_status"] = self_elliot["elliot_clause_status"]

        if primary_other:
            other_phi = getattr(primary_other, "phi_integration", 0.1)
            other_cmni = getattr(primary_other, "current_state", {}).get("cmni", 0.2)
            other_elliot = self.elliot_evaluator.evaluate_entity({
                "phi_integration": other_phi,
                "cmni": other_cmni,
            })
            result["compliance"]["other_elliot_status"] = other_elliot["elliot_clause_status"]

        # 8. Final decision synthesis
        result["decisions"]["interaction"] = "CONTINUE"
        if primary_other and result["activations"]["tactical_help"]["should_help"]:
            result["decisions"]["action"] = "PROVIDE_HELP"
        else:
            result["decisions"]["action"] = "OBSERVE"

        # Record episodic memory
        agents_involved = [getattr(primary_other, "id", "unknown")] if primary_other else []
        self._record_episodic_event(
            "interaction",
            agents_involved,
            self.current_state["emotional_valence"],
            0.5,
            context,
        )

        # Add metadata needed by helper methods
        result["state_snapshot"] = self.current_state.copy()
        result["primary_other_id"] = getattr(primary_other, "id", None) if primary_other else None

        # Update interaction history
        self.interaction_history.append(result)
        if len(self.interaction_history) > 100:
            self.interaction_history.pop(0)

        return result

    def _compute_utility_delta(self) -> float:
        """Compute recent change in agent utility (placeholder)."""
        if len(self.interaction_history) < 2:
            return 0.0
        # Simplified: delta in resource level
        prev = self.interaction_history[-1].get("state_snapshot", {}).get("resource_level", 0.8)
        current = self.current_state["resource_level"]
        return current - prev

    def _get_interaction_duration(self, other_agent_id: str) -> float:
        """Get duration of current interaction with specific agent."""
        relevant = [h for h in self.interaction_history
                    if h.get("primary_other_id") == other_agent_id]
        if not relevant:
            return 0.0
        first_interaction = relevant[0]["timestamp"]
        return time.time() - first_interaction

    def _record_episodic_event(
        self,
        event_type: str,
        agents_involved: List[str],
        valence: float,
        significance: float,
        context: Dict[str, Any],
    ) -> None:
        """Record event in episodic memory."""
        trace = MemoryTrace(
            timestamp=time.time(),
            event_type=event_type,
            agents_involved=agents_involved,
            emotional_valence=valence,
            significance=significance,
            context=context.copy(),
        )
        self.memory.add_episodic(trace)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "agent_id": self.agent_id,
            "phi_integration": self.phi_integration,
            "cmni": self.empathy_module.cmni_tracker.current_cmni,
            "elliot_status": self.elliot_evaluator.evaluate_entity({
                "phi_integration": self.phi_integration,
                "cmni": self.empathy_module.cmni_tracker.current_cmni,
            })["elliot_clause_status"],
            "current_state": self.current_state.copy(),
            "memory_stats": {
                "episodic_count": len(self.memory.episodic_memory),
                "working_count": len(self.memory.working_memory),
            },
            "empathy_capacity": self.empathy_module.get_empathy_capacity(),
            "coercion_events": len(self.non_coercion_guardian.coercion_history),
            "disengagements": self.disengagement_protocol.disengagement_count,
        }
