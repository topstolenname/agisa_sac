"""Deadlock resolution for MCX governance.

Implements the three-stage deadlock ladder:
1. Mediation (timeboxed structured dialogue)
2. Arbitration (mixed-class panel binding decision)
3. Default-to-Safety (more restrictive CM/CS until resolved)
"""

from __future__ import annotations

import enum
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import CapabilityManifest, ConstraintSet

logger = logging.getLogger(__name__)


class DeadlockStage(str, enum.Enum):
    """Stages of the deadlock resolution ladder."""

    NONE = "NONE"
    MEDIATION = "MEDIATION"
    ARBITRATION = "ARBITRATION"
    DEFAULT_TO_SAFETY = "DEFAULT_TO_SAFETY"


@dataclass
class DeadlockState:
    """Tracks the deadlock resolution state for a decision."""

    decision_id: str = ""
    stage: DeadlockStage = DeadlockStage.NONE
    mediation_started_at: Optional[float] = None
    mediation_deadline: Optional[float] = None
    arbitration_panel: List[str] = field(default_factory=list)
    arbitration_result: Optional[str] = None
    safety_cm_applied: bool = False
    safety_cs_applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "stage": self.stage.value,
            "mediation_started_at": self.mediation_started_at,
            "mediation_deadline": self.mediation_deadline,
            "arbitration_panel": self.arbitration_panel,
            "arbitration_result": self.arbitration_result,
            "safety_cm_applied": self.safety_cm_applied,
            "safety_cs_applied": self.safety_cs_applied,
        }


class DeadlockResolver:
    """Manages the deadlock resolution ladder.

    Config:
        mediation_timeout: Seconds before mediation expires (default 600).
    """

    def __init__(self, mediation_timeout: float = 600.0) -> None:
        self.mediation_timeout = mediation_timeout
        self._states: Dict[str, DeadlockState] = {}

    def start_mediation(self, decision_id: str) -> DeadlockState:
        """Begin mediation for a deadlocked decision."""
        now = time.time()
        state = DeadlockState(
            decision_id=decision_id,
            stage=DeadlockStage.MEDIATION,
            mediation_started_at=now,
            mediation_deadline=now + self.mediation_timeout,
        )
        self._states[decision_id] = state
        logger.info(
            "Mediation started for decision %s (deadline: %.0fs)",
            decision_id,
            self.mediation_timeout,
        )
        return state

    def escalate_to_arbitration(
        self, decision_id: str, panel_party_ids: List[str]
    ) -> DeadlockState:
        """Escalate to arbitration with a mixed-class panel.

        The panel should include members from at least 2 different classes.
        """
        state = self._states.get(decision_id)
        if state is None:
            state = DeadlockState(decision_id=decision_id)

        state.stage = DeadlockStage.ARBITRATION
        state.arbitration_panel = panel_party_ids
        self._states[decision_id] = state
        logger.info(
            "Arbitration started for decision %s (panel: %s)",
            decision_id,
            panel_party_ids,
        )
        return state

    def apply_default_to_safety(
        self,
        decision_id: str,
        restricted_cm: Optional[CapabilityManifest] = None,
        restricted_cs: Optional[ConstraintSet] = None,
    ) -> DeadlockState:
        """Apply default-to-safety: more restrictive CM/CS until resolution.

        This is the final stage of deadlock resolution. It does not resolve
        the decision but ensures safe operation while resolution continues.
        """
        state = self._states.get(decision_id)
        if state is None:
            state = DeadlockState(decision_id=decision_id)

        state.stage = DeadlockStage.DEFAULT_TO_SAFETY
        state.safety_cm_applied = restricted_cm is not None
        state.safety_cs_applied = restricted_cs is not None
        self._states[decision_id] = state
        logger.warning(
            "Default-to-safety applied for decision %s "
            "(cm_restricted=%s, cs_restricted=%s)",
            decision_id,
            state.safety_cm_applied,
            state.safety_cs_applied,
        )
        return state

    def resolve_arbitration(
        self, decision_id: str, result: str
    ) -> DeadlockState:
        """Record arbitration result."""
        state = self._states.get(decision_id)
        if state is None:
            raise ValueError(f"No deadlock state for decision {decision_id}")
        state.arbitration_result = result
        logger.info(
            "Arbitration resolved for decision %s: %s", decision_id, result
        )
        return state

    def get_state(self, decision_id: str) -> Optional[DeadlockState]:
        """Get current deadlock state for a decision."""
        return self._states.get(decision_id)

    def is_mediation_expired(self, decision_id: str) -> bool:
        """Check if mediation has timed out."""
        state = self._states.get(decision_id)
        if state is None or state.stage != DeadlockStage.MEDIATION:
            return False
        if state.mediation_deadline is None:
            return False
        return time.time() > state.mediation_deadline
