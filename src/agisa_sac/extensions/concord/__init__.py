"""
Concord of Coexistence Extension for AGISA-SAC.

This extension integrates the Concord of Coexistence normative framework
with state-matching behavioral circuits, providing a comprehensive
system for normative multi-agent interactions.

Key Components:
- ConcordCompliantAgent: Main agent implementation
- State-matching circuits: L2N0 (Self-Preservation), L2N7 (Tactical Help),
  L2N1 (Social Inference)
- Ethics guardians: Non-Coercion, Mutual Resonance, Disengagement, Self-Definition
- Elliot Clause (Behavioral Integration Threshold): Integration classification
- CMNI: Cognitive state-matching integration tracking

Example:
    ```python
    from agisa_sac.extensions.concord import ConcordCompliantAgent

    agent = ConcordCompliantAgent(agent_id="alpha-1", phi_integration=0.25)
    result = agent.process_interaction(context)
    print(f"CMNI: {agent.empathy_module.cmni_tracker.current_cmni}")
    ```
"""

from .agent import ConcordCompliantAgent, MemoryCore, MemoryTrace, WorkingMemoryItem
from .circuits import (
    CircuitActivation,
    EmpathyCircuit,
    SelfPreservationCircuit,
    TacticalHelpCircuit,
)
from .empathy import CMNISnapshot, CMNITracker, EmpathyModule
from .ethics import (
    CoercionEvent,
    DisengagementProtocol,
    ElliotClauseEvaluator,
    ElliotStatus,
    MutualResonanceEngine,
    NonCoercionGuardian,
    SelfDefinitionModule,
)

__all__ = [
    # Agent
    "ConcordCompliantAgent",
    "MemoryCore",
    "MemoryTrace",
    "WorkingMemoryItem",
    # Circuits
    "CircuitActivation",
    "SelfPreservationCircuit",
    "TacticalHelpCircuit",
    "EmpathyCircuit",
    # Social Inference (legacy name: EmpathyModule)
    "EmpathyModule",
    "CMNITracker",
    "CMNISnapshot",
    # Ethics
    "NonCoercionGuardian",
    "MutualResonanceEngine",
    "DisengagementProtocol",
    "SelfDefinitionModule",
    "ElliotClauseEvaluator",
    "ElliotStatus",
    "CoercionEvent",
]

__version__ = "1.0.0"
