"""Emergency circuit breaker for MCX governance.

The emergency system provides a controlled mechanism for rapid response
while maintaining governance integrity through:
- Multi-class invocation requirement
- Auto-expiry with configurable timeout
- Escalating renewal thresholds
- Irreversibility ban during emergency
- Mandatory post-hoc review
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import (
    DEFAULT_EMERGENCY_EXPIRY_SECONDS,
    DEFAULT_EMERGENCY_RENEWAL_ESCALATION,
    DEFAULT_THRESHOLDS,
    EmergencyState,
    EmergencyStatus,
    PartyClass,
)
from agisa_sac.governance.voting import VoteRecord

logger = logging.getLogger(__name__)


class EmergencyManager:
    """Manages the emergency circuit breaker lifecycle.

    Invariants:
    - Entry requires multi-class threshold (>=1 H, >=1 A, >=1 I).
    - Auto-expiry at T + expiry_seconds.
    - Renewal requires escalating thresholds.
    - Mandatory audit on 2nd+ renewals.
    - Irreversibility ban unless special higher-threshold exception.
    - No permanent CS/CM changes during emergency.
    """

    def __init__(
        self,
        expiry_seconds: float = DEFAULT_EMERGENCY_EXPIRY_SECONDS,
        renewal_escalation: float = DEFAULT_EMERGENCY_RENEWAL_ESCALATION,
        base_threshold: float = DEFAULT_THRESHOLDS["D3"],
    ) -> None:
        self.expiry_seconds = expiry_seconds
        self.renewal_escalation = renewal_escalation
        self.base_threshold = base_threshold
        self.state = EmergencyState()
        self._post_hoc_reviews: List[Dict[str, Any]] = []

    @property
    def is_active(self) -> bool:
        return self.state.is_active

    def check_auto_expiry(self) -> bool:
        """Check and apply auto-expiry if needed.

        Returns True if emergency was expired by this call.
        """
        if self.state.status == EmergencyStatus.EMERGENCY and self.state.is_expired:
            logger.warning(
                "Emergency auto-expired for decision %s",
                self.state.entry_decision_id,
            )
            self._schedule_post_hoc_review()
            self.state.status = EmergencyStatus.NORMAL
            return True
        return False

    def enter_emergency(
        self,
        votes: List[VoteRecord],
        decision_id: str,
        invariants: Optional[List[str]] = None,
        now: Optional[float] = None,
    ) -> EmergencyState:
        """Enter emergency state.

        Requires multi-class approval: >=1 H, >=1 A, >=1 I must approve.

        Args:
            votes: Approval votes from multiple classes.
            decision_id: The D3 decision authorizing emergency entry.
            invariants: Active invariants during emergency.
            now: Override current time (for testing).

        Returns:
            Updated EmergencyState.

        Raises:
            ValueError: If multi-class requirement not met.
        """
        if self.state.status == EmergencyStatus.EMERGENCY and not self.state.is_expired:
            raise ValueError(
                "Already in emergency state. Use renew_emergency() instead."
            )

        # Verify multi-class approval
        approving_classes: Dict[str, bool] = {"H": False, "A": False, "I": False}
        for v in votes:
            if v.approve:
                approving_classes[v.party_class.value] = True

        if not all(approving_classes.values()):
            missing = [c for c, ok in approving_classes.items() if not ok]
            raise ValueError(
                f"Emergency entry requires approval from all classes (H/A/I). "
                f"Missing approvals from: {missing}"
            )

        ts = now if now is not None else time.time()
        self.state = EmergencyState(
            status=EmergencyStatus.EMERGENCY,
            entered_at=ts,
            expires_at=ts + self.expiry_seconds,
            renewal_count=0,
            active_invariants=invariants or [],
            entry_decision_id=decision_id,
        )

        logger.warning(
            "EMERGENCY ENTERED: decision=%s, expires_at=%.0f, invariants=%s",
            decision_id,
            self.state.expires_at,
            invariants,
        )
        return self.state

    def renew_emergency(
        self,
        votes: List[VoteRecord],
        now: Optional[float] = None,
    ) -> EmergencyState:
        """Renew emergency state with escalating thresholds.

        Each renewal requires a higher approval threshold:
        threshold = base_threshold + (renewal_count * escalation)

        2nd+ renewals require mandatory audit (tracked for post-hoc review).

        Raises:
            ValueError: If not in emergency, or threshold not met.
        """
        if self.state.status != EmergencyStatus.EMERGENCY:
            raise ValueError("Not in emergency state. Cannot renew.")

        new_count = self.state.renewal_count + 1
        required_threshold = min(
            1.0, self.base_threshold + (new_count * self.renewal_escalation)
        )

        # Check multi-class approval
        approving_classes: Dict[str, bool] = {"H": False, "A": False, "I": False}
        approve_count = 0
        total_count = 0
        for v in votes:
            total_count += 1
            if v.approve:
                approve_count += 1
                approving_classes[v.party_class.value] = True

        if not all(approving_classes.values()):
            missing = [c for c, ok in approving_classes.items() if not ok]
            raise ValueError(
                f"Emergency renewal requires all-class approval. "
                f"Missing: {missing}"
            )

        ratio = approve_count / total_count if total_count > 0 else 0.0
        if ratio < required_threshold:
            raise ValueError(
                f"Emergency renewal #{new_count} requires threshold "
                f"{required_threshold:.2%} but got {ratio:.2%}"
            )

        # Mandatory audit on 2nd+ renewals
        if new_count >= 2:
            logger.warning(
                "Emergency renewal #%d: MANDATORY AUDIT TRIGGERED",
                new_count,
            )
            self._post_hoc_reviews.append({
                "type": "renewal_audit",
                "renewal_count": new_count,
                "timestamp": time.time(),
                "decision_id": self.state.entry_decision_id,
            })

        ts = now if now is not None else time.time()
        self.state.renewal_count = new_count
        self.state.expires_at = ts + self.expiry_seconds

        logger.warning(
            "EMERGENCY RENEWED #%d: new expiry=%.0f, threshold=%.2f",
            new_count,
            self.state.expires_at,
            required_threshold,
        )
        return self.state

    def exit_emergency(self) -> EmergencyState:
        """Exit emergency state and schedule post-hoc review."""
        if self.state.status != EmergencyStatus.EMERGENCY:
            raise ValueError("Not in emergency state.")

        self._schedule_post_hoc_review()
        self.state.status = EmergencyStatus.NORMAL
        logger.info(
            "EMERGENCY EXITED: decision=%s, renewals=%d",
            self.state.entry_decision_id,
            self.state.renewal_count,
        )
        return self.state

    def check_irreversibility_ban(self, action_irreversible: bool) -> bool:
        """Check if an irreversible action is allowed during emergency.

        During emergency, irreversible actions are banned unless a special
        higher-threshold exception vote has been recorded.

        Returns True if the action is allowed, False if banned.
        """
        if not self.is_active:
            return True  # Not in emergency, no ban
        if action_irreversible:
            return False  # Banned during emergency
        return True

    def check_permanent_change_ban(self) -> bool:
        """Check if permanent CS/CM changes are banned (during emergency).

        Returns True if permanent changes are allowed, False if banned.
        """
        if self.is_active:
            return False
        return True

    def get_renewal_threshold(self) -> float:
        """Get the threshold required for the next renewal."""
        next_count = self.state.renewal_count + 1
        return min(
            1.0, self.base_threshold + (next_count * self.renewal_escalation)
        )

    def _schedule_post_hoc_review(self) -> None:
        """Record that a post-hoc review is needed."""
        self._post_hoc_reviews.append({
            "type": "post_hoc_review",
            "entry_decision_id": self.state.entry_decision_id,
            "renewal_count": self.state.renewal_count,
            "entered_at": self.state.entered_at,
            "timestamp": time.time(),
        })

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get all pending post-hoc reviews."""
        return list(self._post_hoc_reviews)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "expiry_seconds": self.expiry_seconds,
            "renewal_escalation": self.renewal_escalation,
            "base_threshold": self.base_threshold,
            "post_hoc_reviews": self._post_hoc_reviews,
        }
