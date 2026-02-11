"""Party management for MCX governance.

Parties are the voting entities in the governance system, classified into
three classes (H/A/I) to ensure multi-class representation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agisa_sac.governance.types import PartyClass

logger = logging.getLogger(__name__)


@dataclass
class Party:
    """A governance party (voter/participant).

    Attributes:
        id: Unique party identifier.
        party_class: H (Human), A (Agent), or I (Infrastructure).
        pubkey: Public key for signature verification.
            Simulation stub: any string or None.
        representation_scope: Domain(s) this party can vote on.
        conflict_disclosures: Declared conflicts of interest.
    """

    id: str
    party_class: PartyClass
    pubkey: Optional[str] = None
    representation_scope: List[str] = field(default_factory=lambda: ["*"])
    conflict_disclosures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "party_class": self.party_class.value,
            "pubkey": self.pubkey,
            "representation_scope": self.representation_scope,
            "conflict_disclosures": self.conflict_disclosures,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Party:
        return cls(
            id=data["id"],
            party_class=PartyClass(data["party_class"]),
            pubkey=data.get("pubkey"),
            representation_scope=data.get("representation_scope", ["*"]),
            conflict_disclosures=data.get("conflict_disclosures", []),
        )


class PartyRegistry:
    """Registry of all governance parties.

    Manages admission, removal, and lookup of parties. Provides
    class-based queries needed for quorum and threshold calculations.
    """

    def __init__(self) -> None:
        self._parties: Dict[str, Party] = {}

    @property
    def parties(self) -> Dict[str, Party]:
        return dict(self._parties)

    def register(self, party: Party) -> None:
        """Register a party. Raises ValueError if ID already exists."""
        if party.id in self._parties:
            raise ValueError(f"Party '{party.id}' already registered")
        self._parties[party.id] = party
        logger.info(
            "Party registered: %s (class=%s)", party.id, party.party_class.value
        )

    def remove(self, party_id: str) -> Party:
        """Remove a party by ID. Raises KeyError if not found."""
        party = self._parties.pop(party_id)
        logger.info("Party removed: %s", party_id)
        return party

    def get(self, party_id: str) -> Party:
        """Get party by ID. Raises KeyError if not found."""
        return self._parties[party_id]

    def get_by_class(self, party_class: PartyClass) -> List[Party]:
        """Get all parties of a given class."""
        return [p for p in self._parties.values() if p.party_class == party_class]

    def class_counts(self) -> Dict[str, int]:
        """Count parties per class."""
        counts = {"H": 0, "A": 0, "I": 0}
        for p in self._parties.values():
            counts[p.party_class.value] += 1
        return counts

    def has_all_classes(self) -> bool:
        """Check if at least one party from each class is registered."""
        counts = self.class_counts()
        return all(v >= 1 for v in counts.values())

    def __len__(self) -> int:
        return len(self._parties)

    def __contains__(self, party_id: str) -> bool:
        return party_id in self._parties

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parties": {pid: p.to_dict() for pid, p in self._parties.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PartyRegistry:
        registry = cls()
        for pid, pdata in data.get("parties", {}).items():
            registry._parties[pid] = Party.from_dict(pdata)
        return registry
