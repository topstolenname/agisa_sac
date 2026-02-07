"""Sanctions ladder and escalation rules for MV-EL.

Defines the graduated sanctions system (S0–S5) with automatic
escalation for repeat violations and severity-based skip rules.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import SanctionLevel

logger = logging.getLogger(__name__)

# Default escalation window (seconds) for repeat violations
DEFAULT_ESCALATION_WINDOW: float = 3600.0  # 1 hour

# Default clean period for de-escalation (seconds)
DEFAULT_DEESCALATION_PERIOD: float = 7200.0  # 2 hours


@dataclass
class SanctionRecord:
    """A record of a sanction applied to a scope."""

    scope: str
    level: SanctionLevel
    reason: str
    timestamp: float = field(default_factory=time.time)
    violation_type: str = ""
    auto_escalated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope": self.scope,
            "level": self.level.value,
            "level_name": self.level.name,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "violation_type": self.violation_type,
            "auto_escalated": self.auto_escalated,
        }


class SanctionsLadder:
    """Manages the graduated sanctions system.

    Escalation rules:
    - Repeat violations of the same type within the escalation window
      escalate one sanction level.
    - Critical violations (configurable) can skip levels.
    - De-escalation occurs after a clean period.
    - S5 (TERMINATE) requires a D2 governance decision to reverse.
    """

    def __init__(
        self,
        escalation_window: float = DEFAULT_ESCALATION_WINDOW,
        deescalation_period: float = DEFAULT_DEESCALATION_PERIOD,
        critical_violation_types: Optional[List[str]] = None,
    ) -> None:
        self.escalation_window = escalation_window
        self.deescalation_period = deescalation_period
        self.critical_violation_types = critical_violation_types or [
            "unauthorized_network_access",
            "data_exfiltration",
            "governance_bypass",
        ]
        # scope -> list of sanction records
        self._history: Dict[str, List[SanctionRecord]] = {}
        # scope -> current sanction level
        self._current_levels: Dict[str, SanctionLevel] = {}

    def evaluate_violation(
        self,
        scope: str,
        violation_type: str,
        reason: str,
        severity: Optional[SanctionLevel] = None,
    ) -> SanctionRecord:
        """Evaluate a violation and determine the appropriate sanction.

        Args:
            scope: The scope that violated.
            violation_type: Category of violation.
            reason: Human-readable description.
            severity: Optional explicit severity (for critical violations).

        Returns:
            The SanctionRecord with the determined level.
        """
        now = time.time()
        history = self._history.get(scope, [])
        current = self._current_levels.get(scope, SanctionLevel.S0_WARN)

        # Check for critical violation (skip levels)
        if violation_type in self.critical_violation_types:
            level = severity or SanctionLevel.S3_QUARANTINE
            if level.value < SanctionLevel.S3_QUARANTINE.value:
                level = SanctionLevel.S3_QUARANTINE
        elif severity is not None:
            level = severity
        else:
            # Check for repeat violations within window
            recent_same_type = [
                r
                for r in history
                if r.violation_type == violation_type
                and now - r.timestamp < self.escalation_window
            ]

            if recent_same_type:
                # Escalate one level
                next_val = min(current.value + 1, SanctionLevel.S5_TERMINATE_INSTANCE.value)
                level = SanctionLevel(next_val)
                logger.warning(
                    "Auto-escalation for scope '%s': %s -> %s "
                    "(repeat %s within window)",
                    scope,
                    current.name,
                    level.name,
                    violation_type,
                )
            else:
                level = current if current.value > SanctionLevel.S0_WARN.value else SanctionLevel.S0_WARN

        record = SanctionRecord(
            scope=scope,
            level=level,
            reason=reason,
            timestamp=now,
            violation_type=violation_type,
            auto_escalated=level.value > current.value,
        )

        if scope not in self._history:
            self._history[scope] = []
        self._history[scope].append(record)
        self._current_levels[scope] = level

        return record

    def check_deescalation(self, scope: str) -> Optional[SanctionLevel]:
        """Check if a scope is eligible for de-escalation.

        Returns the new (lower) sanction level if eligible, None otherwise.
        """
        current = self._current_levels.get(scope)
        if current is None or current == SanctionLevel.S0_WARN:
            return None

        # S5 requires governance decision to reverse
        if current == SanctionLevel.S5_TERMINATE_INSTANCE:
            return None

        history = self._history.get(scope, [])
        if not history:
            return None

        latest = max(r.timestamp for r in history)
        if time.time() - latest >= self.deescalation_period:
            new_level = SanctionLevel(max(0, current.value - 1))
            self._current_levels[scope] = new_level
            logger.info(
                "De-escalation for scope '%s': %s -> %s",
                scope,
                current.name,
                new_level.name,
            )
            return new_level

        return None

    def get_current_level(self, scope: str) -> SanctionLevel:
        """Get current sanction level for a scope."""
        return self._current_levels.get(scope, SanctionLevel.S0_WARN)

    def get_history(self, scope: str) -> List[SanctionRecord]:
        """Get sanction history for a scope."""
        return self._history.get(scope, [])

    def reset_scope(self, scope: str) -> None:
        """Reset a scope's sanctions (requires governance decision for S5)."""
        self._current_levels.pop(scope, None)
        self._history.pop(scope, None)
        logger.info("Sanctions reset for scope '%s'", scope)
