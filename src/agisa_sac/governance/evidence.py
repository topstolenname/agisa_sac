"""Evidence Package (EP) builder and validator for MCX governance.

Every D1–D4 decision must produce a valid Evidence Package that contains
all proofs of legitimate governance process.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import DecisionType
from agisa_sac.governance.voting import QuorumProof, ThresholdProof

logger = logging.getLogger(__name__)


@dataclass
class EvidencePackage:
    """Canonical proof artifact for D1–D4 governance decisions.

    All fields are required for a valid EP. The EP is the primary
    accountability artifact and is anchored in the audit log.
    """

    ep_id: str = field(default_factory=lambda: f"ep-{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    decision_type: DecisionType = DecisionType.D1
    participants: List[Dict[str, str]] = field(default_factory=list)
    quorum_proof: Optional[QuorumProof] = None
    threshold_proof: Optional[ThresholdProof] = None
    rationale: str = ""
    impact_statement: str = ""
    cs_diff: Optional[Dict[str, Any]] = None
    cm_diff: Optional[Dict[str, Any]] = None
    timestamps: Dict[str, float] = field(default_factory=dict)
    signatures: List[Dict[str, Any]] = field(default_factory=list)
    audit_anchor_ref: str = ""

    def validate(self) -> List[str]:
        """Validate the Evidence Package for completeness and correctness.

        Returns:
            List of validation errors (empty if valid).
        """
        errors: List[str] = []

        if not self.decision_id:
            errors.append("decision_id is required")
        if self.decision_type == DecisionType.D0:
            errors.append("D0 decisions do not require Evidence Packages")
        if not self.participants:
            errors.append("participants list is empty")
        if self.quorum_proof is None:
            errors.append("quorum_proof is required")
        elif not self.quorum_proof.satisfied:
            errors.append("quorum_proof is not satisfied")
        if self.threshold_proof is None:
            errors.append("threshold_proof is required")
        elif not self.threshold_proof.satisfied:
            errors.append("threshold_proof is not satisfied")
        if not self.rationale:
            errors.append("rationale is required")
        if not self.impact_statement:
            errors.append("impact_statement is required")
        if "proposed_at" not in self.timestamps:
            errors.append("timestamps.proposed_at is required")
        if not self.audit_anchor_ref:
            errors.append("audit_anchor_ref is required")

        # Check class-wise assent
        if self.threshold_proof is not None:
            cwa = self.threshold_proof.class_wise_assent
            if not all(cwa.values()):
                missing = [c for c, v in cwa.items() if not v]
                errors.append(
                    f"class_wise_assent missing from: {missing}"
                )

        return errors

    @property
    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def compute_hash(self) -> str:
        """Compute a deterministic hash of the EP contents.

        Simulation stub: uses SHA-256 of JSON-serialized content.
        Production would use proper digital signatures.
        """
        content = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def sign(self, party_id: str, signature: Optional[str] = None) -> None:
        """Add a signature to the EP.

        Simulation stub: generates SHA-256 hash as signature placeholder.
        Production would use real asymmetric cryptography.
        """
        if signature is None:
            # Stub: hash of party_id + ep contents
            stub_data = f"{party_id}:{self.compute_hash()}"
            signature = f"stub:sha256:{hashlib.sha256(stub_data.encode()).hexdigest()[:16]}"

        self.signatures.append({
            "party_id": party_id,
            "signature": signature,
            "timestamp": time.time(),
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ep_id": self.ep_id,
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "participants": self.participants,
            "quorum_proof": self.quorum_proof.to_dict() if self.quorum_proof else None,
            "threshold_proof": (
                self.threshold_proof.to_dict() if self.threshold_proof else None
            ),
            "rationale": self.rationale,
            "impact_statement": self.impact_statement,
            "cs_diff": self.cs_diff,
            "cm_diff": self.cm_diff,
            "timestamps": self.timestamps,
            "signatures": self.signatures,
            "audit_anchor_ref": self.audit_anchor_ref,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidencePackage:
        qp = data.get("quorum_proof")
        tp = data.get("threshold_proof")
        return cls(
            ep_id=data.get("ep_id", ""),
            decision_id=data.get("decision_id", ""),
            decision_type=DecisionType(data.get("decision_type", "D1")),
            participants=data.get("participants", []),
            quorum_proof=QuorumProof.from_dict(qp) if qp else None,
            threshold_proof=ThresholdProof.from_dict(tp) if tp else None,
            rationale=data.get("rationale", ""),
            impact_statement=data.get("impact_statement", ""),
            cs_diff=data.get("cs_diff"),
            cm_diff=data.get("cm_diff"),
            timestamps=data.get("timestamps", {}),
            signatures=data.get("signatures", []),
            audit_anchor_ref=data.get("audit_anchor_ref", ""),
        )


def build_evidence_package(
    decision_id: str,
    decision_type: DecisionType,
    participants: List[Dict[str, str]],
    quorum_proof: QuorumProof,
    threshold_proof: ThresholdProof,
    rationale: str,
    impact_statement: str,
    cs_diff: Optional[Dict[str, Any]] = None,
    cm_diff: Optional[Dict[str, Any]] = None,
    timestamps: Optional[Dict[str, float]] = None,
) -> EvidencePackage:
    """Factory function to build a complete Evidence Package."""
    ep = EvidencePackage(
        decision_id=decision_id,
        decision_type=decision_type,
        participants=participants,
        quorum_proof=quorum_proof,
        threshold_proof=threshold_proof,
        rationale=rationale,
        impact_statement=impact_statement,
        cs_diff=cs_diff,
        cm_diff=cm_diff,
        timestamps=timestamps or {"proposed_at": time.time()},
    )
    return ep
