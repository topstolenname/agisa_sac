"""Voting mechanics for MCX governance.

Implements quorum checking, threshold calculation, and class-wise assent
verification. All D1–D4 decisions require multi-class representation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import (
    DEFAULT_THRESHOLDS,
    DecisionType,
    PartyClass,
)


@dataclass
class VoteRecord:
    """A single vote cast by a party."""

    party_id: str
    party_class: PartyClass
    approve: bool
    signature: Optional[str] = None  # Simulation stub
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "party_id": self.party_id,
            "party_class": self.party_class.value,
            "approve": self.approve,
            "signature": self.signature,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VoteRecord:
        return cls(
            party_id=data["party_id"],
            party_class=PartyClass(data["party_class"]),
            approve=data["approve"],
            signature=data.get("signature"),
            timestamp=data.get("timestamp", 0.0),
        )


@dataclass
class QuorumProof:
    """Proof that quorum requirements are met.

    For D1–D4: at least 1 H, 1 A, 1 I must be present.
    """

    present_parties: List[str] = field(default_factory=list)
    class_counts: Dict[str, int] = field(
        default_factory=lambda: {"H": 0, "A": 0, "I": 0}
    )
    satisfied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "present_parties": self.present_parties,
            "class_counts": self.class_counts,
            "satisfied": self.satisfied,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuorumProof:
        return cls(
            present_parties=data.get("present_parties", []),
            class_counts=data.get("class_counts", {"H": 0, "A": 0, "I": 0}),
            satisfied=data.get("satisfied", False),
        )


@dataclass
class ThresholdProof:
    """Proof that approval threshold and class-wise assent are met."""

    total_votes: int = 0
    approvals: int = 0
    rejections: int = 0
    approval_ratio: float = 0.0
    threshold_required: float = 0.0
    class_wise_assent: Dict[str, bool] = field(
        default_factory=lambda: {"H": False, "A": False, "I": False}
    )
    satisfied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_votes": self.total_votes,
            "approvals": self.approvals,
            "rejections": self.rejections,
            "approval_ratio": self.approval_ratio,
            "threshold_required": self.threshold_required,
            "class_wise_assent": self.class_wise_assent,
            "satisfied": self.satisfied,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ThresholdProof:
        return cls(
            total_votes=data.get("total_votes", 0),
            approvals=data.get("approvals", 0),
            rejections=data.get("rejections", 0),
            approval_ratio=data.get("approval_ratio", 0.0),
            threshold_required=data.get("threshold_required", 0.0),
            class_wise_assent=data.get(
                "class_wise_assent", {"H": False, "A": False, "I": False}
            ),
            satisfied=data.get("satisfied", False),
        )


def check_quorum(
    votes: List[VoteRecord],
) -> QuorumProof:
    """Check quorum: at least 1 H, 1 A, 1 I party must have voted.

    Args:
        votes: List of vote records to check.

    Returns:
        QuorumProof with satisfaction status.
    """
    present = list({v.party_id for v in votes})
    counts: Dict[str, int] = {"H": 0, "A": 0, "I": 0}
    for v in votes:
        counts[v.party_class.value] += 1

    satisfied = all(counts[c] >= 1 for c in ("H", "A", "I"))

    return QuorumProof(
        present_parties=present,
        class_counts=counts,
        satisfied=satisfied,
    )


def check_threshold(
    votes: List[VoteRecord],
    decision_type: DecisionType,
    thresholds: Optional[Dict[str, float]] = None,
) -> ThresholdProof:
    """Check approval threshold and class-wise assent.

    Rules:
    - D1/D2: 2/3 supermajority + class-wise assent from each H/A/I
    - D3: simple majority + class-wise assent
    - D4: 3/4 supermajority + class-wise assent
    - No D1–D4 can pass with approvals solely from one class.

    Args:
        votes: List of vote records.
        decision_type: The decision type being voted on.
        thresholds: Optional custom thresholds (defaults used if None).

    Returns:
        ThresholdProof with satisfaction status.
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    threshold_required = thresholds.get(decision_type.value, 2 / 3)

    total = len(votes)
    approvals = sum(1 for v in votes if v.approve)
    rejections = total - approvals
    ratio = approvals / total if total > 0 else 0.0

    # Class-wise assent: at least one approval from each class
    class_approvals: Dict[str, bool] = {"H": False, "A": False, "I": False}
    approving_classes: set[str] = set()
    for v in votes:
        if v.approve:
            class_approvals[v.party_class.value] = True
            approving_classes.add(v.party_class.value)

    all_classes_assent = all(class_approvals.values())

    # Anti-capture: must have approvals from more than one class
    multi_class_approval = len(approving_classes) >= 2

    # Overall satisfaction
    threshold_met = ratio >= threshold_required
    satisfied = threshold_met and all_classes_assent and multi_class_approval

    return ThresholdProof(
        total_votes=total,
        approvals=approvals,
        rejections=rejections,
        approval_ratio=ratio,
        threshold_required=threshold_required,
        class_wise_assent=class_approvals,
        satisfied=satisfied,
    )
