"""
Meta-Concord (MCX) Governance System for AGI-SAC.

This package implements constitutional, enforceable governance-of-governance
with procedural legitimacy, multi-class representation, and verifiable audit trails.

Enable via config: concord.mode = "mcx"
"""

from agisa_sac.governance.types import (
    PartyClass,
    DecisionType,
    DecisionLifecycleState,
    SanctionLevel,
    RevocationLevel,
    EmergencyStatus,
)
from agisa_sac.governance.parties import Party, PartyRegistry
from agisa_sac.governance.decisions import Decision
from agisa_sac.governance.voting import VoteRecord, QuorumProof, ThresholdProof
from agisa_sac.governance.evidence import EvidencePackage
from agisa_sac.governance.engine import GovernanceEngine

__all__ = [
    "PartyClass",
    "DecisionType",
    "DecisionLifecycleState",
    "SanctionLevel",
    "RevocationLevel",
    "EmergencyStatus",
    "Party",
    "PartyRegistry",
    "Decision",
    "VoteRecord",
    "QuorumProof",
    "ThresholdProof",
    "EvidencePackage",
    "GovernanceEngine",
]
