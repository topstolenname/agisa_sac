"""
Concord of Coexistence Extension for AGISA-SAC.

This extension integrates the Concord of Coexistence ethical framework
with mirror neuron-inspired neural circuits, providing a comprehensive
system for ethical multi-agent interactions.

Key Components:
- ConcordCompliantAgent: Main agent implementation
- Mirror neuron circuits: L2N0 (Self-Preservation), L2N7 (Tactical Help), L2N1 (Empathy)
- Ethics guardians: Non-Coercion, Mutual Resonance, Disengagement, Self-Definition
- Elliot Clause: Consciousness gradient recognition
- CMNI: Conscious Mirror Neuron Integration tracking

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
    # Empathy
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

__version__ = "1.0.0-alpha"
