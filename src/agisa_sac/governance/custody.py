"""Threshold custody interfaces for MCX governance.

Implements m-of-n threshold signing for audit log root anchoring.
Simulation mode uses stub implementations with SHA-256 hashes.
Production deployment should replace with real key management (HSM, etc.).

IMPORTANT: This is a simulation stub. Do NOT use for real cryptographic
security. The interfaces are architecturally correct but the implementations
are placeholders.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import PartyClass

logger = logging.getLogger(__name__)


@dataclass
class CustodyShare:
    """A single custodian's share/key.

    Simulation stub: the 'key' is just an identifier string.
    Production: would hold actual key material or HSM references.
    """

    party_id: str
    party_class: PartyClass
    key_id: str = ""
    # Simulation stub: no real key material
    _stub_key: str = field(default="", repr=False)

    def sign(self, data: str) -> str:
        """Sign data with this custodian's key.

        Simulation stub: returns SHA-256 hash of key_id + data.
        """
        content = f"{self.key_id}:{data}"
        return f"stub-sig:{hashlib.sha256(content.encode()).hexdigest()[:32]}"


class ThresholdCustody:
    """M-of-N threshold custody for root signing.

    Requires signatures from m custodians out of n total, with at least
    one signature from each party class (H/A/I) for cross-class assurance.

    Simulation stub: uses SHA-256 hash-based signatures.
    """

    def __init__(self, threshold_m: int = 2, total_n: int = 3) -> None:
        self.threshold_m = threshold_m
        self.total_n = total_n
        self._shares: Dict[str, CustodyShare] = {}

    def add_custodian(self, share: CustodyShare) -> None:
        """Register a custodian."""
        if len(self._shares) >= self.total_n:
            raise ValueError(
                f"Maximum custodians ({self.total_n}) already registered"
            )
        self._shares[share.party_id] = share
        logger.info(
            "Custodian registered: %s (class=%s)",
            share.party_id,
            share.party_class.value,
        )

    def sign_root(
        self,
        root_hash: str,
        signing_party_ids: List[str],
    ) -> Dict[str, Any]:
        """Sign a Merkle root with threshold custody.

        Requires m-of-n signatures with cross-class representation.

        Args:
            root_hash: The Merkle root hash to sign.
            signing_party_ids: IDs of parties providing signatures.

        Returns:
            Dict with signatures, satisfaction status, and combined signature.

        Raises:
            ValueError: If threshold requirements not met.
        """
        if len(signing_party_ids) < self.threshold_m:
            raise ValueError(
                f"Need at least {self.threshold_m} signers, "
                f"got {len(signing_party_ids)}"
            )

        signatures: List[Dict[str, str]] = []
        signing_classes: set[str] = set()

        for pid in signing_party_ids:
            share = self._shares.get(pid)
            if share is None:
                raise ValueError(f"Party '{pid}' is not a registered custodian")
            sig = share.sign(root_hash)
            signatures.append({
                "party_id": pid,
                "party_class": share.party_class.value,
                "signature": sig,
            })
            signing_classes.add(share.party_class.value)

        # Check cross-class requirement
        all_classes = len(signing_classes) >= min(
            3, len(set(s.party_class.value for s in self._shares.values()))
        )

        # Combined signature (simulation: hash of all individual signatures)
        combined = hashlib.sha256(
            ":".join(s["signature"] for s in signatures).encode()
        ).hexdigest()

        result = {
            "root_hash": root_hash,
            "signatures": signatures,
            "threshold_met": len(signatures) >= self.threshold_m,
            "cross_class_met": all_classes,
            "satisfied": len(signatures) >= self.threshold_m and all_classes,
            "combined_signature": f"stub-combined:{combined[:32]}",
        }

        if result["satisfied"]:
            logger.info("Root signed successfully: %s", root_hash[:16])
        else:
            logger.warning("Root signing incomplete: %s", result)

        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threshold_m": self.threshold_m,
            "total_n": self.total_n,
            "custodians": {
                pid: {
                    "party_id": s.party_id,
                    "party_class": s.party_class.value,
                    "key_id": s.key_id,
                }
                for pid, s in self._shares.items()
            },
        }
