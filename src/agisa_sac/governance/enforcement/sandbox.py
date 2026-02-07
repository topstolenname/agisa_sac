"""Sandbox enforcer: reference MV-EL implementation for simulations.

Implements tool allowlist/denylist, data scope checking, network egress
allowlist, and compute limits. All enforcement actions are logged.
"""

from __future__ import annotations

import fnmatch
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agisa_sac.governance.enforcement.base import EnforcementInterface
from agisa_sac.governance.types import (
    CapabilityManifest,
    RevocationLevel,
    SanctionLevel,
)

logger = logging.getLogger(__name__)


@dataclass
class ScopeState:
    """Runtime state for a governed scope."""

    scope_id: str
    cm: Optional[CapabilityManifest] = None
    active_sanction: SanctionLevel = SanctionLevel.S0_WARN
    is_suspended: bool = False
    is_terminated: bool = False
    is_quarantined: bool = False
    throttle_factor: float = 1.0  # 1.0 = no throttle, 0.0 = fully throttled
    compute_used: Dict[str, float] = field(
        default_factory=lambda: {"tokens": 0, "time_seconds": 0, "steps": 0}
    )
    enforcement_log: List[Dict[str, Any]] = field(default_factory=list)


class SandboxEnforcer(EnforcementInterface):
    """Reference enforcement implementation for simulations.

    Provides:
    - Tool allowlist/denylist checking
    - Data scope path matching
    - Network egress allowlist (stubbed)
    - Compute quota tracking
    - Full enforcement action logging
    """

    def __init__(self, audit_log: Any = None) -> None:
        """Initialize sandbox enforcer.

        Args:
            audit_log: Optional AuditLog instance for logging enforcement
                actions as EP addenda.
        """
        self._scopes: Dict[str, ScopeState] = {}
        self._audit_log = audit_log

    def apply_capability_manifest(
        self, scope: str, cm: CapabilityManifest
    ) -> None:
        state = self._get_or_create_scope(scope)
        state.cm = cm
        self._log_enforcement(scope, "cm_applied", {"cm": cm.to_dict()})
        logger.info("CM applied to scope '%s'", scope)

    def check_action_allowed(
        self, action: str, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        scope = context.get("scope", "default")
        state = self._scopes.get(scope)

        # No scope state = no restrictions (D0 operational)
        if state is None:
            return True, "no_governance_scope"

        # Check suspension/termination
        if state.is_terminated:
            return False, "scope_terminated"
        if state.is_suspended:
            return False, "scope_suspended"
        if state.is_quarantined:
            return False, "scope_quarantined"

        # Check CM
        if state.cm is None:
            return True, "no_cm_applied"

        # Tool check
        if state.cm.tool_denylist and action in state.cm.tool_denylist:
            self._log_enforcement(
                scope, "action_denied", {"action": action, "reason": "in_denylist"}
            )
            return False, f"action '{action}' is in tool denylist"

        if state.cm.tool_allowlist and action not in state.cm.tool_allowlist:
            self._log_enforcement(
                scope,
                "action_denied",
                {"action": action, "reason": "not_in_allowlist"},
            )
            return False, f"action '{action}' not in tool allowlist"

        # Data scope check
        data_path = context.get("data_path")
        if data_path and state.cm.data_scopes:
            if not any(
                fnmatch.fnmatch(data_path, pattern)
                for pattern in state.cm.data_scopes
            ):
                self._log_enforcement(
                    scope,
                    "action_denied",
                    {"action": action, "reason": "data_scope_violation", "path": data_path},
                )
                return False, f"data path '{data_path}' not in allowed scopes"

        # Network egress check
        network_target = context.get("network_target")
        if network_target and state.cm.network_egress:
            if not any(
                fnmatch.fnmatch(network_target, pattern)
                for pattern in state.cm.network_egress
            ):
                self._log_enforcement(
                    scope,
                    "action_denied",
                    {"action": action, "reason": "network_egress_violation"},
                )
                return False, f"network target '{network_target}' not in allowed egress"

        # Compute quota check
        if state.cm.compute_quota:
            quota = state.cm.compute_quota
            used = state.compute_used
            if (
                quota.get("max_steps")
                and used.get("steps", 0) >= quota["max_steps"]
            ):
                return False, "compute quota exceeded (steps)"
            if (
                quota.get("max_tokens")
                and used.get("tokens", 0) >= quota["max_tokens"]
            ):
                return False, "compute quota exceeded (tokens)"

        # CS forbidden actions check
        cs = context.get("constraint_set")
        if cs and hasattr(cs, "forbidden_actions"):
            for pattern in cs.forbidden_actions:
                if fnmatch.fnmatch(action, pattern):
                    self._log_enforcement(
                        scope,
                        "action_denied",
                        {"action": action, "reason": "cs_forbidden"},
                    )
                    return False, f"action '{action}' forbidden by Constraint Set"

        return True, "allowed"

    def revoke_capabilities(
        self, scope: str, level: RevocationLevel
    ) -> None:
        state = self._get_or_create_scope(scope)

        if level == RevocationLevel.THROTTLE:
            state.throttle_factor = 0.5
        elif level == RevocationLevel.RESTRICT:
            if state.cm:
                state.cm.tool_allowlist = []  # Remove all tools
        elif level == RevocationLevel.QUARANTINE:
            state.is_quarantined = True
        elif level == RevocationLevel.SUSPEND:
            state.is_suspended = True
        elif level == RevocationLevel.TERMINATE:
            state.is_terminated = True

        self._log_enforcement(
            scope, "capabilities_revoked", {"level": level.value}
        )
        logger.warning("Capabilities revoked for '%s': %s", scope, level.value)

    def enforce_sanction(
        self, scope: str, level: SanctionLevel, reason: str
    ) -> None:
        state = self._get_or_create_scope(scope)
        state.active_sanction = level

        # Apply corresponding enforcement
        if level >= SanctionLevel.S4_SUSPEND_SCOPE:
            state.is_suspended = True
        if level >= SanctionLevel.S5_TERMINATE_INSTANCE:
            state.is_terminated = True
        if level >= SanctionLevel.S3_QUARANTINE:
            state.is_quarantined = True

        self._log_enforcement(
            scope,
            "sanction_applied",
            {"level": level.value, "level_name": level.name, "reason": reason},
        )
        logger.warning(
            "Sanction %s applied to '%s': %s", level.name, scope, reason
        )

    def get_current_scope_state(self, scope: str) -> Dict[str, Any]:
        state = self._scopes.get(scope)
        if state is None:
            return {"scope": scope, "status": "ungoverned"}

        return {
            "scope": scope,
            "has_cm": state.cm is not None,
            "active_sanction": state.active_sanction.name,
            "is_suspended": state.is_suspended,
            "is_terminated": state.is_terminated,
            "is_quarantined": state.is_quarantined,
            "throttle_factor": state.throttle_factor,
            "compute_used": state.compute_used,
            "enforcement_log_count": len(state.enforcement_log),
        }

    def record_compute_usage(
        self, scope: str, tokens: float = 0, time_seconds: float = 0, steps: float = 0
    ) -> None:
        """Record compute usage for quota tracking."""
        state = self._get_or_create_scope(scope)
        state.compute_used["tokens"] = state.compute_used.get("tokens", 0) + tokens
        state.compute_used["time_seconds"] = (
            state.compute_used.get("time_seconds", 0) + time_seconds
        )
        state.compute_used["steps"] = state.compute_used.get("steps", 0) + steps

    def _get_or_create_scope(self, scope: str) -> ScopeState:
        if scope not in self._scopes:
            self._scopes[scope] = ScopeState(scope_id=scope)
        return self._scopes[scope]

    def _log_enforcement(
        self, scope: str, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Log an enforcement action."""
        entry = {
            "scope": scope,
            "event_type": event_type,
            "data": data,
            "timestamp": time.time(),
        }

        state = self._scopes.get(scope)
        if state:
            state.enforcement_log.append(entry)

        # Also log to audit log if available
        if self._audit_log is not None:
            self._audit_log.append(
                event_type=f"enforcement:{event_type}",
                data=data,
                actor_id=f"enforcer:{scope}",
                summary=f"Enforcement {event_type} on scope {scope}",
            )
