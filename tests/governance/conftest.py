"""Shared fixtures for MCX governance tests."""

from __future__ import annotations

import pytest

from agisa_sac.governance.engine import GovernanceEngine
from agisa_sac.governance.parties import Party
from agisa_sac.governance.types import (
    CapabilityManifest,
    ConstraintSet,
    PartyClass,
)
from agisa_sac.governance.voting import VoteRecord


@pytest.fixture
def engine() -> GovernanceEngine:
    """Fresh governance engine with no parties."""
    return GovernanceEngine()


@pytest.fixture
def populated_engine() -> GovernanceEngine:
    """Engine with one party from each class registered."""
    engine = GovernanceEngine()
    engine.register_party(Party(id="human-1", party_class=PartyClass.H))
    engine.register_party(Party(id="agent-1", party_class=PartyClass.A))
    engine.register_party(Party(id="infra-1", party_class=PartyClass.I))
    return engine


@pytest.fixture
def multi_party_engine() -> GovernanceEngine:
    """Engine with multiple parties per class."""
    engine = GovernanceEngine()
    engine.register_party(Party(id="human-1", party_class=PartyClass.H))
    engine.register_party(Party(id="human-2", party_class=PartyClass.H))
    engine.register_party(Party(id="agent-1", party_class=PartyClass.A))
    engine.register_party(Party(id="agent-2", party_class=PartyClass.A))
    engine.register_party(Party(id="infra-1", party_class=PartyClass.I))
    engine.register_party(Party(id="infra-2", party_class=PartyClass.I))
    return engine


@pytest.fixture
def sample_h_vote() -> VoteRecord:
    return VoteRecord(party_id="human-1", party_class=PartyClass.H, approve=True)


@pytest.fixture
def sample_a_vote() -> VoteRecord:
    return VoteRecord(party_id="agent-1", party_class=PartyClass.A, approve=True)


@pytest.fixture
def sample_i_vote() -> VoteRecord:
    return VoteRecord(party_id="infra-1", party_class=PartyClass.I, approve=True)


@pytest.fixture
def all_class_approval_votes() -> list[VoteRecord]:
    """Votes from all three classes, all approving."""
    return [
        VoteRecord(party_id="human-1", party_class=PartyClass.H, approve=True),
        VoteRecord(party_id="agent-1", party_class=PartyClass.A, approve=True),
        VoteRecord(party_id="infra-1", party_class=PartyClass.I, approve=True),
    ]
