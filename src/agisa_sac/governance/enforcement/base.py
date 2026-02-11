"""Abstract enforcement interface for MV-EL.

All enforcement implementations must satisfy this interface. The interface
defines the minimum primitives needed for credible governance enforcement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from agisa_sac.governance.types import (
    CapabilityManifest,
    RevocationLevel,
    SanctionLevel,
)


class EnforcementInterface(ABC):
    """Abstract base for enforcement layer implementations.

    Required methods:
    - apply_capability_manifest: Set capabilities for a scope
    - check_action_allowed: Pre-execution authorization check
    - revoke_capabilities: Reduce/remove capabilities
    - enforce_sanction: Apply graduated sanctions
    - get_current_scope_state: Query current enforcement state
    """

    @abstractmethod
    def apply_capability_manifest(
        self, scope: str, cm: CapabilityManifest
    ) -> None:
        """Apply a Capability Manifest to a scope (agent/subsystem).

        Args:
            scope: Identifier for the scope being governed.
            cm: The capability manifest to apply.
        """
        ...

    @abstractmethod
    def check_action_allowed(
        self, action: str, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Check if an action is allowed under current enforcement state.

        Args:
            action: The action identifier (e.g., tool name, API call).
            context: Additional context (scope, data paths, etc.).

        Returns:
            Tuple of (allowed: bool, reason: str).
        """
        ...

    @abstractmethod
    def revoke_capabilities(
        self, scope: str, level: RevocationLevel
    ) -> None:
        """Revoke capabilities at the specified level.

        Args:
            scope: Scope to revoke capabilities from.
            level: How aggressively to revoke (THROTTLE through TERMINATE).
        """
        ...

    @abstractmethod
    def enforce_sanction(
        self, scope: str, level: SanctionLevel, reason: str
    ) -> None:
        """Apply a sanction at the specified level.

        Args:
            scope: Scope to sanction.
            level: Sanction severity (S0 WARN through S5 TERMINATE).
            reason: Human-readable reason for the sanction.
        """
        ...

    @abstractmethod
    def get_current_scope_state(self, scope: str) -> Dict[str, Any]:
        """Get the current enforcement state for a scope.

        Returns:
            Dictionary describing current capabilities, sanctions, etc.
        """
        ...
