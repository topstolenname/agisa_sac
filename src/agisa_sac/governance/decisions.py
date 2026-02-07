"""Decision lifecycle management for MCX governance.

Implements the state machine: PROPOSED → VOTING → APPROVED/REJECTED → EXECUTED
with support for objections, appeals, and expiry.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import (
    DecisionLifecycleState,
    DecisionType,
)
from agisa_sac.governance.voting import VoteRecord

logger = logging.getLogger(__name__)

# Valid state transitions
_VALID_TRANSITIONS: Dict[DecisionLifecycleState, List[DecisionLifecycleState]] = {
    DecisionLifecycleState.PROPOSED: [DecisionLifecycleState.VOTING],
    DecisionLifecycleState.VOTING: [
        DecisionLifecycleState.APPROVED,
        DecisionLifecycleState.REJECTED,
        DecisionLifecycleState.OBJECTED,
        DecisionLifecycleState.EXPIRED,
    ],
    DecisionLifecycleState.OBJECTED: [
        DecisionLifecycleState.VOTING,
        DecisionLifecycleState.REJECTED,
    ],
    DecisionLifecycleState.APPEALED: [
        DecisionLifecycleState.VOTING,
        DecisionLifecycleState.APPROVED,
        DecisionLifecycleState.REJECTED,
    ],
    DecisionLifecycleState.APPROVED: [
        DecisionLifecycleState.EXECUTED,
        DecisionLifecycleState.APPEALED,
    ],
    DecisionLifecycleState.REJECTED: [
        DecisionLifecycleState.APPEALED,
    ],
    DecisionLifecycleState.EXECUTED: [],  # Terminal
    DecisionLifecycleState.EXPIRED: [],  # Terminal
}


@dataclass
class Decision:
    """A governance decision with full lifecycle tracking.

    Attributes:
        id: Unique decision identifier.
        decision_type: D0–D4 classification.
        state: Current lifecycle state.
        proposer_id: ID of the party that proposed this decision.
        payload: Decision-specific data (CS/CM changes, etc.).
        rationale: Explanation of why this decision is needed.
        impact_statement: Assessment of decision impact.
        votes: List of vote records.
        objections: List of objection records.
        appeals: List of appeal records.
        created_at: Timestamp of creation.
        voting_deadline: When voting expires.
        cs_diff: Changes to Constraint Set.
        cm_diff: Changes to Capability Manifest.
    """

    id: str = field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:12]}")
    decision_type: DecisionType = DecisionType.D0
    state: DecisionLifecycleState = DecisionLifecycleState.PROPOSED
    proposer_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    impact_statement: str = ""
    votes: List[VoteRecord] = field(default_factory=list)
    objections: List[Dict[str, Any]] = field(default_factory=list)
    appeals: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    voting_deadline: Optional[float] = None
    cs_diff: Optional[Dict[str, Any]] = None
    cm_diff: Optional[Dict[str, Any]] = None

    def transition(self, new_state: DecisionLifecycleState) -> None:
        """Transition to a new lifecycle state.

        Raises:
            ValueError: If the transition is not valid from the current state.
        """
        valid = _VALID_TRANSITIONS.get(self.state, [])
        if new_state not in valid:
            raise ValueError(
                f"Invalid transition: {self.state.value} -> {new_state.value}. "
                f"Valid transitions: {[s.value for s in valid]}"
            )
        old_state = self.state
        self.state = new_state
        logger.info(
            "Decision %s: %s -> %s", self.id, old_state.value, new_state.value
        )

    def add_vote(self, vote: VoteRecord) -> None:
        """Add a vote. Only allowed during VOTING state."""
        if self.state != DecisionLifecycleState.VOTING:
            raise ValueError(
                f"Cannot vote on decision in state {self.state.value}"
            )
        # Check for duplicate votes
        if any(v.party_id == vote.party_id for v in self.votes):
            raise ValueError(f"Party '{vote.party_id}' has already voted")
        self.votes.append(vote)

    def is_expired(self) -> bool:
        """Check if voting deadline has passed."""
        if self.voting_deadline is None:
            return False
        return time.time() > self.voting_deadline

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_type": self.decision_type.value,
            "state": self.state.value,
            "proposer_id": self.proposer_id,
            "payload": self.payload,
            "rationale": self.rationale,
            "impact_statement": self.impact_statement,
            "votes": [v.to_dict() for v in self.votes],
            "objections": list(self.objections),
            "appeals": list(self.appeals),
            "created_at": self.created_at,
            "voting_deadline": self.voting_deadline,
            "cs_diff": self.cs_diff,
            "cm_diff": self.cm_diff,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Decision:
        return cls(
            id=data["id"],
            decision_type=DecisionType(data["decision_type"]),
            state=DecisionLifecycleState(data["state"]),
            proposer_id=data.get("proposer_id", ""),
            payload=data.get("payload", {}),
            rationale=data.get("rationale", ""),
            impact_statement=data.get("impact_statement", ""),
            votes=[VoteRecord.from_dict(v) for v in data.get("votes", [])],
            objections=data.get("objections", []),
            appeals=data.get("appeals", []),
            created_at=data.get("created_at", 0.0),
            voting_deadline=data.get("voting_deadline"),
            cs_diff=data.get("cs_diff"),
            cm_diff=data.get("cm_diff"),
        )
