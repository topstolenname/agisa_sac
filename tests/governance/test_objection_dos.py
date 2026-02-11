"""Tests for objection/appeal DOS prevention.

Validates:
- Repeated identical objections trigger bonding/rate limiting
- Appeal bonding escalates
- Invalid objection bases rejected
"""

from __future__ import annotations

import pytest

from agisa_sac.governance.appeals import AppealTracker
from agisa_sac.governance.objections import (
    VALID_OBJECTION_BASES,
    ObjectionTracker,
)


class TestObjectionBonding:
    """Test that repeated identical objections trigger bonding."""

    def test_first_objection_no_bond(self):
        tracker = ObjectionTracker()
        obj = tracker.file_objection(
            decision_id="dec-1",
            party_id="p1",
            basis="missing_ep_fields",
            detail="test",
        )
        assert obj.bond_amount == 0.0

    def test_second_objection_requires_bond(self):
        tracker = ObjectionTracker()
        tracker.file_objection(
            decision_id="dec-1",
            party_id="p1",
            basis="missing_ep_fields",
        )
        obj2 = tracker.file_objection(
            decision_id="dec-1",
            party_id="p1",
            basis="missing_ep_fields",
        )
        assert obj2.bond_amount > 0

    def test_bond_escalates_exponentially(self):
        tracker = ObjectionTracker(bond_base=1.0, bond_multiplier=2.0)
        bonds = []
        for i in range(5):
            obj = tracker.file_objection(
                decision_id="dec-1",
                party_id="p1",
                basis="threshold_failure",
            )
            bonds.append(obj.bond_amount)

        # First = 0, second = 1*2^1=2, third = 1*2^2=4, etc.
        assert bonds[0] == 0.0
        assert bonds[1] == 2.0
        assert bonds[2] == 4.0
        assert bonds[3] == 8.0
        assert bonds[4] == 16.0

    def test_different_bases_tracked_independently(self):
        tracker = ObjectionTracker()
        tracker.file_objection(
            decision_id="dec-1", party_id="p1", basis="missing_ep_fields"
        )
        obj2 = tracker.file_objection(
            decision_id="dec-1", party_id="p1", basis="threshold_failure"
        )
        # Different basis = first objection for this combo = no bond
        assert obj2.bond_amount == 0.0

    def test_different_parties_tracked_independently(self):
        tracker = ObjectionTracker()
        tracker.file_objection(
            decision_id="dec-1", party_id="p1", basis="missing_ep_fields"
        )
        obj2 = tracker.file_objection(
            decision_id="dec-1", party_id="p2", basis="missing_ep_fields"
        )
        assert obj2.bond_amount == 0.0

    def test_invalid_basis_rejected(self):
        tracker = ObjectionTracker()
        with pytest.raises(ValueError, match="Invalid objection basis"):
            tracker.file_objection(
                decision_id="dec-1",
                party_id="p1",
                basis="invalid_reason",
            )

    def test_veto_requires_valid_category(self):
        tracker = ObjectionTracker()
        with pytest.raises(ValueError, match="Veto only allowed"):
            tracker.file_objection(
                decision_id="dec-1",
                party_id="p1",
                basis="missing_ep_fields",
                is_veto=True,
                veto_category="not_a_real_category",
            )

    def test_veto_with_valid_category(self):
        tracker = ObjectionTracker()
        obj = tracker.file_objection(
            decision_id="dec-1",
            party_id="p1",
            basis="missing_ep_fields",
            is_veto=True,
            veto_category="irreversible_physical_action",
        )
        assert obj.is_veto is True
        assert obj.veto_category == "irreversible_physical_action"


class TestAppealBonding:
    """Test appeal bonding and admissibility."""

    def test_first_appeal_no_bond(self):
        tracker = AppealTracker()
        appeal = tracker.file_appeal(
            decision_id="dec-1",
            party_id="p1",
            grounds="procedural_error",
        )
        assert appeal.bond_amount == 0.0
        assert appeal.admissible is True

    def test_repeated_appeals_require_bond(self):
        tracker = AppealTracker()
        tracker.file_appeal(
            decision_id="dec-1", party_id="p1", grounds="procedural_error"
        )
        appeal2 = tracker.file_appeal(
            decision_id="dec-1", party_id="p1", grounds="new_evidence"
        )
        assert appeal2.bond_amount > 0

    def test_invalid_grounds_rejected(self):
        tracker = AppealTracker()
        with pytest.raises(ValueError, match="Invalid appeal grounds"):
            tracker.file_appeal(
                decision_id="dec-1",
                party_id="p1",
                grounds="i_dont_like_it",
            )

    def test_appeal_window_expired(self):
        tracker = AppealTracker(appeal_window=0.0)
        with pytest.raises(ValueError, match="Appeal window expired"):
            tracker.file_appeal(
                decision_id="dec-1",
                party_id="p1",
                grounds="procedural_error",
                decision_approved_at=0.0,  # Long ago
            )


class TestObjectionThroughEngine:
    """Test objection filing through the full engine."""

    def test_objection_pauses_decision(self, populated_engine):
        engine = populated_engine
        from agisa_sac.governance.types import DecisionType

        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D2,
            rationale="test",
            impact_statement="test",
        )
        did = result.decision_id

        # File objection
        obj_result = engine.file_objection(
            decision_id=did,
            party_id="agent-1",
            basis="missing_ep_fields",
            detail="EP not yet generated",
        )
        assert obj_result.legitimate is True

        # Decision should be in OBJECTED state
        decision = engine.get_decision(did)
        assert decision.state.value == "OBJECTED"

    def test_objection_resolved_returns_to_voting(self, populated_engine):
        engine = populated_engine
        from agisa_sac.governance.types import DecisionType

        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D2,
            rationale="test",
            impact_statement="test",
        )
        did = result.decision_id

        engine.file_objection(
            decision_id=did, party_id="agent-1", basis="threshold_failure"
        )
        resolve_result = engine.resolve_objection(did)
        assert resolve_result.legitimate is True

        decision = engine.get_decision(did)
        assert decision.state.value == "VOTING"
