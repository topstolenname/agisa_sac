"""Objection handling for MCX governance.

Objections pause decision execution and must be addressed. Repeated identical
objections trigger bonding/rate limiting to prevent DOS.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import (
    DEFAULT_OBJECTION_BOND_BASE,
    DEFAULT_OBJECTION_BOND_MULTIPLIER,
    DEFAULT_OBJECTION_RATE_LIMIT_WINDOW,
    VETO_CATEGORIES,
)

logger = logging.getLogger(__name__)

# Valid objection bases
VALID_OBJECTION_BASES: List[str] = [
    "missing_ep_fields",
    "threshold_failure",
    "log_integrity_concern",
    "inadequate_impact_statement",
    "cs_cm_mismatch",
]


@dataclass
class Objection:
    """A formal objection to a governance decision."""

    objection_id: str = ""
    decision_id: str = ""
    party_id: str = ""
    basis: str = ""  # Must be one of VALID_OBJECTION_BASES
    detail: str = ""
    timestamp: float = field(default_factory=time.time)
    bond_amount: float = 0.0
    is_veto: bool = False
    veto_category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objection_id": self.objection_id,
            "decision_id": self.decision_id,
            "party_id": self.party_id,
            "basis": self.basis,
            "detail": self.detail,
            "timestamp": self.timestamp,
            "bond_amount": self.bond_amount,
            "is_veto": self.is_veto,
            "veto_category": self.veto_category,
        }


class ObjectionTracker:
    """Tracks objections per decision and enforces bonding/rate limits.

    Repeated identical objections from the same party trigger escalating
    bond requirements. This prevents objection-based denial of service.
    """

    def __init__(
        self,
        bond_base: float = DEFAULT_OBJECTION_BOND_BASE,
        bond_multiplier: float = DEFAULT_OBJECTION_BOND_MULTIPLIER,
        rate_limit_window: float = DEFAULT_OBJECTION_RATE_LIMIT_WINDOW,
    ) -> None:
        self.bond_base = bond_base
        self.bond_multiplier = bond_multiplier
        self.rate_limit_window = rate_limit_window
        # Tracks: (decision_id, party_id, basis) -> count of objections
        self._objection_counts: Dict[tuple, int] = {}
        # Tracks: party_id -> list of timestamps
        self._party_objection_times: Dict[str, List[float]] = {}

    def file_objection(
        self,
        decision_id: str,
        party_id: str,
        basis: str,
        detail: str = "",
        is_veto: bool = False,
        veto_category: Optional[str] = None,
    ) -> Objection:
        """File an objection, enforcing admissibility and bonding.

        Args:
            decision_id: ID of the decision being objected to.
            party_id: ID of the objecting party.
            basis: One of VALID_OBJECTION_BASES.
            detail: Additional detail for the objection.
            is_veto: Whether this is a veto (restricted categories only).
            veto_category: If veto, must be in VETO_CATEGORIES.

        Returns:
            The filed Objection.

        Raises:
            ValueError: If basis is invalid, veto category is invalid,
                or rate limit exceeded.
        """
        # Validate basis
        if basis not in VALID_OBJECTION_BASES:
            raise ValueError(
                f"Invalid objection basis: '{basis}'. "
                f"Valid bases: {VALID_OBJECTION_BASES}"
            )

        # Validate veto
        if is_veto:
            if veto_category not in VETO_CATEGORIES:
                raise ValueError(
                    f"Veto only allowed for categories: {VETO_CATEGORIES}. "
                    f"Got: '{veto_category}'"
                )

        # Check rate limiting
        now = time.time()
        party_times = self._party_objection_times.get(party_id, [])
        recent = [t for t in party_times if now - t < self.rate_limit_window]
        self._party_objection_times[party_id] = recent

        # Calculate bond for repeated identical objections
        key = (decision_id, party_id, basis)
        count = self._objection_counts.get(key, 0)
        bond_amount = 0.0
        if count > 0:
            bond_amount = self.bond_base * (self.bond_multiplier**count)
            logger.warning(
                "Repeated objection from %s on %s (basis=%s, count=%d). "
                "Bond required: %.2f",
                party_id,
                decision_id,
                basis,
                count + 1,
                bond_amount,
            )

        # Record
        self._objection_counts[key] = count + 1
        self._party_objection_times[party_id] = recent + [now]

        objection = Objection(
            objection_id=f"obj-{decision_id}-{count + 1}",
            decision_id=decision_id,
            party_id=party_id,
            basis=basis,
            detail=detail,
            timestamp=now,
            bond_amount=bond_amount,
            is_veto=is_veto,
            veto_category=veto_category,
        )

        logger.info(
            "Objection filed: %s by %s on decision %s (basis=%s, veto=%s)",
            objection.objection_id,
            party_id,
            decision_id,
            basis,
            is_veto,
        )
        return objection

    def get_repeat_count(
        self, decision_id: str, party_id: str, basis: str
    ) -> int:
        """Get the number of times this party has objected with this basis."""
        key = (decision_id, party_id, basis)
        return self._objection_counts.get(key, 0)

    def get_bond_required(
        self, decision_id: str, party_id: str, basis: str
    ) -> float:
        """Get the bond required for the next objection with these params."""
        count = self.get_repeat_count(decision_id, party_id, basis)
        if count == 0:
            return 0.0
        return self.bond_base * (self.bond_multiplier**count)
