"""Appeals handling for MCX governance.

Appeals allow parties to challenge decision outcomes. Subject to
admissibility filtering, rate limiting, and bonding for repeated appeals.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import (
    DEFAULT_APPEAL_BOND_BASE,
    DEFAULT_APPEAL_BOND_MULTIPLIER,
    DEFAULT_APPEAL_WINDOW_SECONDS,
)

logger = logging.getLogger(__name__)

VALID_APPEAL_GROUNDS: List[str] = [
    "procedural_error",
    "new_evidence",
    "threshold_miscalculation",
    "conflict_of_interest",
    "inadequate_review",
]


@dataclass
class Appeal:
    """A formal appeal of a governance decision outcome."""

    appeal_id: str = ""
    decision_id: str = ""
    party_id: str = ""
    grounds: str = ""
    detail: str = ""
    timestamp: float = field(default_factory=time.time)
    bond_amount: float = 0.0
    admissible: bool = False
    resolution: Optional[str] = None  # "upheld", "overturned", "dismissed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appeal_id": self.appeal_id,
            "decision_id": self.decision_id,
            "party_id": self.party_id,
            "grounds": self.grounds,
            "detail": self.detail,
            "timestamp": self.timestamp,
            "bond_amount": self.bond_amount,
            "admissible": self.admissible,
            "resolution": self.resolution,
        }


class AppealTracker:
    """Manages appeals with admissibility filtering and bonding."""

    def __init__(
        self,
        appeal_window: float = DEFAULT_APPEAL_WINDOW_SECONDS,
        bond_base: float = DEFAULT_APPEAL_BOND_BASE,
        bond_multiplier: float = DEFAULT_APPEAL_BOND_MULTIPLIER,
    ) -> None:
        self.appeal_window = appeal_window
        self.bond_base = bond_base
        self.bond_multiplier = bond_multiplier
        # decision_id -> list of appeals
        self._appeals: Dict[str, List[Appeal]] = {}

    def file_appeal(
        self,
        decision_id: str,
        party_id: str,
        grounds: str,
        detail: str = "",
        decision_approved_at: Optional[float] = None,
    ) -> Appeal:
        """File an appeal against a decision.

        Args:
            decision_id: ID of the decision being appealed.
            party_id: ID of the appealing party.
            grounds: Must be one of VALID_APPEAL_GROUNDS.
            detail: Additional detail.
            decision_approved_at: When the decision was approved/rejected
                (for window check).

        Returns:
            The filed Appeal.

        Raises:
            ValueError: If grounds invalid, window expired, or other issues.
        """
        if grounds not in VALID_APPEAL_GROUNDS:
            raise ValueError(
                f"Invalid appeal grounds: '{grounds}'. "
                f"Valid grounds: {VALID_APPEAL_GROUNDS}"
            )

        now = time.time()

        # Check appeal window
        if decision_approved_at is not None:
            if now - decision_approved_at > self.appeal_window:
                raise ValueError(
                    f"Appeal window expired. Decision was finalized "
                    f"{now - decision_approved_at:.0f}s ago "
                    f"(window: {self.appeal_window:.0f}s)"
                )

        # Calculate bond based on number of prior appeals on this decision
        prior = self._appeals.get(decision_id, [])
        party_prior = [a for a in prior if a.party_id == party_id]
        count = len(party_prior)
        bond_amount = 0.0
        if count > 0:
            bond_amount = self.bond_base * (self.bond_multiplier**count)

        appeal = Appeal(
            appeal_id=f"appeal-{decision_id}-{len(prior) + 1}",
            decision_id=decision_id,
            party_id=party_id,
            grounds=grounds,
            detail=detail,
            timestamp=now,
            bond_amount=bond_amount,
            admissible=True,
        )

        if decision_id not in self._appeals:
            self._appeals[decision_id] = []
        self._appeals[decision_id].append(appeal)

        logger.info(
            "Appeal filed: %s by %s on decision %s (grounds=%s, bond=%.2f)",
            appeal.appeal_id,
            party_id,
            decision_id,
            grounds,
            bond_amount,
        )
        return appeal

    def get_appeals(self, decision_id: str) -> List[Appeal]:
        """Get all appeals for a decision."""
        return self._appeals.get(decision_id, [])

    def resolve_appeal(
        self, appeal_id: str, decision_id: str, resolution: str
    ) -> None:
        """Resolve an appeal."""
        for appeal in self._appeals.get(decision_id, []):
            if appeal.appeal_id == appeal_id:
                appeal.resolution = resolution
                logger.info("Appeal %s resolved: %s", appeal_id, resolution)
                return
        raise ValueError(f"Appeal {appeal_id} not found for decision {decision_id}")
