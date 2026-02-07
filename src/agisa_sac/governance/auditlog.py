"""Append-only audit log with hash chain and Merkle root anchoring.

Provides tamper-evident logging for all governance actions. Each entry
references the previous entry's hash, forming a hash chain. Periodic
Merkle root computation enables efficient integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Genesis hash for the first entry
GENESIS_HASH = "0" * 64


@dataclass
class AuditEntry:
    """A single append-only audit log entry."""

    entry_id: str = field(default_factory=lambda: f"log-{uuid.uuid4().hex[:12]}")
    timestamp: float = field(default_factory=time.time)
    event_type: str = ""  # e.g., "decision_proposed", "vote_cast", "ep_created"
    decision_id: Optional[str] = None
    actor_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    previous_hash: str = GENESIS_HASH
    entry_hash: str = ""
    summary: str = ""

    def compute_hash(self) -> str:
        """Compute the hash of this entry (excluding entry_hash itself)."""
        content = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "decision_id": self.decision_id,
            "actor_id": self.actor_id,
            "data": self.data,
            "previous_hash": self.previous_hash,
        }
        serialized = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "decision_id": self.decision_id,
            "actor_id": self.actor_id,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "summary": self.summary,
        }


class AuditLog:
    """Append-only audit log with hash chain integrity.

    Features:
    - Hash chain: each entry references previous entry's hash.
    - Merkle roots: periodic computation for efficient verification.
    - Bounded summaries: configurable summary generation.
    - Verifiable inclusion: Merkle proofs for specific entries.
    - External anchoring interface (stub).
    """

    def __init__(self, merkle_interval: int = 10) -> None:
        """Initialize audit log.

        Args:
            merkle_interval: Compute Merkle root every N entries.
        """
        self._entries: List[AuditEntry] = []
        self._merkle_roots: List[Dict[str, Any]] = []
        self._merkle_interval = merkle_interval
        self._anchored_roots: List[Dict[str, Any]] = []

    @property
    def entries(self) -> List[AuditEntry]:
        return list(self._entries)

    @property
    def length(self) -> int:
        return len(self._entries)

    def append(
        self,
        event_type: str,
        data: Dict[str, Any],
        decision_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        summary: str = "",
    ) -> AuditEntry:
        """Append a new entry to the audit log.

        The entry's hash is automatically computed and chained to
        the previous entry.

        Returns:
            The newly appended AuditEntry.
        """
        previous_hash = (
            self._entries[-1].entry_hash if self._entries else GENESIS_HASH
        )

        entry = AuditEntry(
            event_type=event_type,
            decision_id=decision_id,
            actor_id=actor_id,
            data=data,
            previous_hash=previous_hash,
            summary=summary or f"{event_type}: {decision_id or 'system'}",
        )
        entry.entry_hash = entry.compute_hash()
        self._entries.append(entry)

        # Check if we should compute a Merkle root
        if len(self._entries) % self._merkle_interval == 0:
            root = self._compute_merkle_root()
            self._merkle_roots.append({
                "root_hash": root,
                "entry_count": len(self._entries),
                "timestamp": time.time(),
            })

        return entry

    def verify_log_integrity(self) -> bool:
        """Verify the entire hash chain integrity.

        Returns True if the chain is valid, False if tampered.
        """
        if not self._entries:
            return True

        # First entry should reference genesis
        if self._entries[0].previous_hash != GENESIS_HASH:
            logger.error("First entry does not reference genesis hash")
            return False

        for i, entry in enumerate(self._entries):
            # Verify entry hash
            expected_hash = entry.compute_hash()
            if entry.entry_hash != expected_hash:
                logger.error(
                    "Entry %d (%s) hash mismatch: stored=%s computed=%s",
                    i,
                    entry.entry_id,
                    entry.entry_hash,
                    expected_hash,
                )
                return False

            # Verify chain link (except first entry)
            if i > 0:
                if entry.previous_hash != self._entries[i - 1].entry_hash:
                    logger.error(
                        "Entry %d chain broken: previous_hash=%s "
                        "but entry %d hash=%s",
                        i,
                        entry.previous_hash,
                        i - 1,
                        self._entries[i - 1].entry_hash,
                    )
                    return False

        return True

    def verify_entry_inclusion(self, entry_id: str) -> bool:
        """Verify that a specific entry is included in the log with valid chain.

        This is a simplified inclusion check. A full implementation would
        use Merkle proofs for O(log n) verification.
        """
        for i, entry in enumerate(self._entries):
            if entry.entry_id == entry_id:
                # Verify this entry's hash
                if entry.entry_hash != entry.compute_hash():
                    return False
                # Verify chain to this point
                if i > 0 and entry.previous_hash != self._entries[i - 1].entry_hash:
                    return False
                return True
        return False  # Entry not found

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get a specific entry by ID."""
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_entries_by_decision(self, decision_id: str) -> List[AuditEntry]:
        """Get all entries related to a specific decision."""
        return [e for e in self._entries if e.decision_id == decision_id]

    def get_bounded_summary(
        self, max_entries: int = 50
    ) -> List[Dict[str, Any]]:
        """Get a bounded summary of recent log entries.

        Provides human-readable summaries with verifiable detail pointers
        to mitigate transparency-by-volume attacks.
        """
        recent = self._entries[-max_entries:]
        return [
            {
                "entry_id": e.entry_id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "summary": e.summary,
                "entry_hash": e.entry_hash,
            }
            for e in recent
        ]

    def get_merkle_roots(self) -> List[Dict[str, Any]]:
        """Get all computed Merkle roots."""
        return list(self._merkle_roots)

    def anchor_root(self, root_hash: str) -> str:
        """Anchor a Merkle root to an external system.

        Simulation stub: records the anchoring request locally.
        Production: would submit to blockchain, notary service, etc.

        Returns:
            Anchor reference ID.
        """
        anchor_ref = f"anchor-{uuid.uuid4().hex[:8]}"
        self._anchored_roots.append({
            "anchor_ref": anchor_ref,
            "root_hash": root_hash,
            "timestamp": time.time(),
            "status": "anchored_stub",
        })
        logger.info(
            "Root anchored (stub): %s -> %s", root_hash[:16], anchor_ref
        )
        return anchor_ref

    def _compute_merkle_root(self) -> str:
        """Compute a Merkle root over all current entry hashes."""
        if not self._entries:
            return GENESIS_HASH

        hashes = [e.entry_hash for e in self._entries]
        return _merkle_root(hashes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self._entries],
            "merkle_roots": self._merkle_roots,
            "anchored_roots": self._anchored_roots,
            "merkle_interval": self._merkle_interval,
        }


def _merkle_root(hashes: List[str]) -> str:
    """Compute Merkle root from a list of hashes."""
    if not hashes:
        return GENESIS_HASH
    if len(hashes) == 1:
        return hashes[0]

    # Pad to even number
    if len(hashes) % 2 == 1:
        hashes = hashes + [hashes[-1]]

    next_level: List[str] = []
    for i in range(0, len(hashes), 2):
        combined = hashes[i] + hashes[i + 1]
        next_level.append(hashlib.sha256(combined.encode()).hexdigest())

    return _merkle_root(next_level)
