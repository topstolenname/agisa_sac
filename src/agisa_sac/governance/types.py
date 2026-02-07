"""Core type definitions for the MCX governance system.

Design choice: Using stdlib dataclasses + enums rather than pydantic models.
The repo uses pydantic via FastAPI but core governance types should have zero
external dependencies for maximum portability and testability.
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class PartyClass(str, enum.Enum):
    """Party class in MCX governance. Three classes ensure no single
    constituency can dominate decision-making."""

    H = "H"  # Human operators/researchers
    A = "A"  # Autonomous agents/AI systems
    I = "I"  # Infrastructure/platform services


class DecisionType(str, enum.Enum):
    """Decision taxonomy D0–D4 with escalating governance requirements."""

    D0 = "D0"  # Operational: routine, pre-authorized
    D1 = "D1"  # Policy: CS/CM mods, party admission/removal
    D2 = "D2"  # Capability: grants, restrictions, scope changes
    D3 = "D3"  # Emergency: circuit breaker entry/renewal/exit
    D4 = "D4"  # Constitutional: governance rule changes


class DecisionLifecycleState(str, enum.Enum):
    """State machine for decision lifecycle."""

    PROPOSED = "PROPOSED"
    VOTING = "VOTING"
    OBJECTED = "OBJECTED"
    APPEALED = "APPEALED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"


class SanctionLevel(int, enum.Enum):
    """Graduated sanctions ladder for enforcement."""

    S0_WARN = 0
    S1_THROTTLE = 1
    S2_RESTRICT_TOOLS = 2
    S3_QUARANTINE = 3
    S4_SUSPEND_SCOPE = 4
    S5_TERMINATE_INSTANCE = 5


class RevocationLevel(str, enum.Enum):
    """Capability revocation levels."""

    THROTTLE = "THROTTLE"
    RESTRICT = "RESTRICT"
    QUARANTINE = "QUARANTINE"
    SUSPEND = "SUSPEND"
    TERMINATE = "TERMINATE"


class EmergencyStatus(str, enum.Enum):
    """Emergency circuit breaker state."""

    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"


# --- Governance thresholds (configurable defaults) ---

# Default approval thresholds per decision type
DEFAULT_THRESHOLDS: Dict[str, float] = {
    "D1": 2 / 3,  # supermajority
    "D2": 2 / 3,  # supermajority
    "D3": 0.5,  # simple majority
    "D4": 3 / 4,  # three-quarters
}

# Emergency defaults
DEFAULT_EMERGENCY_EXPIRY_SECONDS: float = 3600.0  # 1 hour
DEFAULT_EMERGENCY_RENEWAL_ESCALATION: float = 0.1  # +10% threshold per renewal

# Objection bonding
DEFAULT_OBJECTION_BOND_BASE: float = 1.0
DEFAULT_OBJECTION_BOND_MULTIPLIER: float = 2.0
DEFAULT_OBJECTION_RATE_LIMIT_WINDOW: float = 300.0  # 5 minutes

# Appeal settings
DEFAULT_APPEAL_WINDOW_SECONDS: float = 1800.0  # 30 minutes
DEFAULT_APPEAL_BOND_BASE: float = 2.0
DEFAULT_APPEAL_BOND_MULTIPLIER: float = 2.0

# Veto categories (only these are eligible for veto)
VETO_CATEGORIES: List[str] = [
    "irreversible_physical_action",
    "privacy_sensitive_disclosure",
    "capability_expansion_beyond_audit",
    "key_custody_rotation",
]


@dataclass
class ConstraintSet:
    """Defines what is forbidden and what invariants must hold (the CS)."""

    forbidden_actions: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    veto_categories: List[str] = field(default_factory=lambda: list(VETO_CATEGORIES))
    appeal_windows: Dict[str, float] = field(
        default_factory=lambda: {
            "D1": DEFAULT_APPEAL_WINDOW_SECONDS,
            "D2": DEFAULT_APPEAL_WINDOW_SECONDS,
            "D3": DEFAULT_APPEAL_WINDOW_SECONDS / 2,
            "D4": DEFAULT_APPEAL_WINDOW_SECONDS * 2,
        }
    )
    emergency_profile: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "forbidden_actions": self.forbidden_actions,
            "invariants": self.invariants,
            "veto_categories": self.veto_categories,
            "appeal_windows": self.appeal_windows,
            "emergency_profile": self.emergency_profile,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintSet:
        return cls(
            forbidden_actions=data.get("forbidden_actions", []),
            invariants=data.get("invariants", []),
            veto_categories=data.get("veto_categories", list(VETO_CATEGORIES)),
            appeal_windows=data.get("appeal_windows", {}),
            emergency_profile=data.get("emergency_profile", {}),
        )


@dataclass
class CapabilityManifest:
    """Defines what an agent/scope is permitted to do (the CM)."""

    tool_allowlist: List[str] = field(default_factory=list)
    tool_denylist: List[str] = field(default_factory=list)
    data_scopes: List[str] = field(default_factory=list)
    network_egress: List[str] = field(default_factory=list)
    compute_quota: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_tokens": 100000,
            "max_time_seconds": 3600,
            "max_steps": 10000,
        }
    )
    memory_scope: Dict[str, Any] = field(default_factory=dict)
    revocation_policy: str = "immediate"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_allowlist": self.tool_allowlist,
            "tool_denylist": self.tool_denylist,
            "data_scopes": self.data_scopes,
            "network_egress": self.network_egress,
            "compute_quota": self.compute_quota,
            "memory_scope": self.memory_scope,
            "revocation_policy": self.revocation_policy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapabilityManifest:
        return cls(
            tool_allowlist=data.get("tool_allowlist", []),
            tool_denylist=data.get("tool_denylist", []),
            data_scopes=data.get("data_scopes", []),
            network_egress=data.get("network_egress", []),
            compute_quota=data.get("compute_quota", {}),
            memory_scope=data.get("memory_scope", {}),
            revocation_policy=data.get("revocation_policy", "immediate"),
        )


@dataclass
class EmergencyState:
    """Tracks the current emergency circuit breaker state."""

    status: EmergencyStatus = EmergencyStatus.NORMAL
    entered_at: Optional[float] = None
    expires_at: Optional[float] = None
    renewal_count: int = 0
    active_invariants: List[str] = field(default_factory=list)
    entry_decision_id: Optional[str] = None

    @property
    def is_active(self) -> bool:
        if self.status != EmergencyStatus.EMERGENCY:
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True

    @property
    def is_expired(self) -> bool:
        if self.status != EmergencyStatus.EMERGENCY:
            return False
        return self.expires_at is not None and time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "entered_at": self.entered_at,
            "expires_at": self.expires_at,
            "renewal_count": self.renewal_count,
            "active_invariants": self.active_invariants,
            "entry_decision_id": self.entry_decision_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmergencyState:
        return cls(
            status=EmergencyStatus(data.get("status", "NORMAL")),
            entered_at=data.get("entered_at"),
            expires_at=data.get("expires_at"),
            renewal_count=data.get("renewal_count", 0),
            active_invariants=data.get("active_invariants", []),
            entry_decision_id=data.get("entry_decision_id"),
        )
