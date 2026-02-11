"""Tests for emergency circuit breaker abuse prevention.

Validates:
- Cannot enter emergency with only H approvals (or only A, or only I)
- Auto-expiry works
- Renewal threshold escalates
- Irreversibility ban enforced
- Emergency cannot permanently alter CS/CM
"""

from __future__ import annotations

import time

import pytest

from agisa_sac.governance.emergency import EmergencyManager
from agisa_sac.governance.engine import GovernanceEngine
from agisa_sac.governance.parties import Party
from agisa_sac.governance.types import (
    DecisionType,
    EmergencyStatus,
    PartyClass,
)
from agisa_sac.governance.voting import VoteRecord


class TestEmergencyEntry:
    """Test emergency entry requirements."""

    def test_entry_requires_all_classes(self):
        mgr = EmergencyManager()
        # Only H approvals
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=True),
        ]
        with pytest.raises(ValueError, match="Missing approvals from"):
            mgr.enter_emergency(votes, decision_id="test")

    def test_entry_fails_with_only_h(self):
        mgr = EmergencyManager()
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
        ]
        with pytest.raises(ValueError):
            mgr.enter_emergency(votes, decision_id="test")

    def test_entry_fails_with_only_a(self):
        mgr = EmergencyManager()
        votes = [
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="a2", party_class=PartyClass.A, approve=True),
        ]
        with pytest.raises(ValueError, match="Missing approvals"):
            mgr.enter_emergency(votes, decision_id="test")

    def test_entry_fails_with_only_i(self):
        mgr = EmergencyManager()
        votes = [
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        with pytest.raises(ValueError):
            mgr.enter_emergency(votes, decision_id="test")

    def test_entry_fails_with_h_and_a_only(self):
        mgr = EmergencyManager()
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
        ]
        with pytest.raises(ValueError, match="Missing approvals from.*I"):
            mgr.enter_emergency(votes, decision_id="test")

    def test_entry_succeeds_with_all_classes(self, all_class_approval_votes):
        mgr = EmergencyManager()
        state = mgr.enter_emergency(all_class_approval_votes, decision_id="test")
        assert state.status == EmergencyStatus.EMERGENCY
        assert mgr.is_active

    def test_entry_requires_approval_not_just_presence(self):
        mgr = EmergencyManager()
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=False),  # Reject!
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        with pytest.raises(ValueError, match="Missing approvals from.*A"):
            mgr.enter_emergency(votes, decision_id="test")


class TestAutoExpiry:
    """Test emergency auto-expiry."""

    def test_auto_expiry(self, all_class_approval_votes):
        mgr = EmergencyManager(expiry_seconds=1.0)
        now = time.time()
        mgr.enter_emergency(
            all_class_approval_votes, decision_id="test", now=now
        )
        assert mgr.is_active

        # Simulate time passing beyond expiry
        # The is_expired property checks time.time(), so we manipulate expires_at
        mgr.state.expires_at = now - 1  # Already expired
        assert mgr.state.is_expired
        assert not mgr.state.is_active  # is_active checks is_expired

    def test_check_auto_expiry_transitions(self, all_class_approval_votes):
        mgr = EmergencyManager(expiry_seconds=0.0)
        now = time.time()
        mgr.enter_emergency(
            all_class_approval_votes, decision_id="test", now=now
        )
        # Set expiry in the past
        mgr.state.expires_at = now - 1
        expired = mgr.check_auto_expiry()
        assert expired is True
        assert mgr.state.status == EmergencyStatus.NORMAL


class TestRenewalEscalation:
    """Test emergency renewal with escalating thresholds."""

    def test_renewal_threshold_escalates(self, all_class_approval_votes):
        mgr = EmergencyManager(
            expiry_seconds=3600, renewal_escalation=0.1, base_threshold=0.5
        )
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")

        # First renewal: threshold = 0.5 + 1*0.1 = 0.6
        assert mgr.get_renewal_threshold() == pytest.approx(0.6)

        # Renew
        mgr.renew_emergency(all_class_approval_votes)
        assert mgr.state.renewal_count == 1

        # Second renewal: threshold = 0.5 + 2*0.1 = 0.7
        assert mgr.get_renewal_threshold() == pytest.approx(0.7)

    def test_renewal_fails_below_threshold(self, all_class_approval_votes):
        mgr = EmergencyManager(
            expiry_seconds=3600, renewal_escalation=0.3, base_threshold=0.5
        )
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")

        # After several renewals, threshold becomes very high
        mgr.renew_emergency(all_class_approval_votes)
        mgr.renew_emergency(all_class_approval_votes)

        # Now threshold = 0.5 + 3*0.3 = 1.4, capped at 1.0
        # 3/3 = 100% >= 100%, still passes
        mgr.renew_emergency(all_class_approval_votes)

        # But with rejections it fails: need all classes to have at least
        # one approval, but overall ratio below threshold.
        # Use multiple parties per class so that class-wise assent passes
        # but overall ratio is too low.
        mixed_votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=False),
            VoteRecord(party_id="h3", party_class=PartyClass.H, approve=False),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="a2", party_class=PartyClass.A, approve=False),
            VoteRecord(party_id="a3", party_class=PartyClass.A, approve=False),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
            VoteRecord(party_id="i2", party_class=PartyClass.I, approve=False),
            VoteRecord(party_id="i3", party_class=PartyClass.I, approve=False),
        ]
        # 3/9 = 33.3% which is below the capped 1.0 threshold
        with pytest.raises(ValueError, match="requires threshold"):
            mgr.renew_emergency(mixed_votes)

    def test_renewal_requires_all_classes(self, all_class_approval_votes):
        mgr = EmergencyManager(expiry_seconds=3600)
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")

        h_only = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
        ]
        with pytest.raises(ValueError, match="all-class approval"):
            mgr.renew_emergency(h_only)


class TestIrreversibilityBan:
    """Test that irreversible actions are banned during emergency."""

    def test_irreversible_banned_during_emergency(self, all_class_approval_votes):
        mgr = EmergencyManager(expiry_seconds=3600)
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")

        assert mgr.check_irreversibility_ban(action_irreversible=True) is False
        assert mgr.check_irreversibility_ban(action_irreversible=False) is True

    def test_irreversible_allowed_when_not_emergency(self):
        mgr = EmergencyManager()
        assert mgr.check_irreversibility_ban(action_irreversible=True) is True


class TestEmergencyCSCMBan:
    """Test that emergency cannot permanently alter CS/CM."""

    def test_permanent_changes_banned_during_emergency(
        self, all_class_approval_votes
    ):
        mgr = EmergencyManager(expiry_seconds=3600)
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")
        assert mgr.check_permanent_change_ban() is False

    def test_permanent_changes_allowed_normally(self):
        mgr = EmergencyManager()
        assert mgr.check_permanent_change_ban() is True

    def test_engine_blocks_d1_during_emergency(self, populated_engine):
        engine = populated_engine
        votes = [
            VoteRecord(party_id="human-1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="agent-1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="infra-1", party_class=PartyClass.I, approve=True),
        ]
        engine.enter_emergency(votes, decision_id="emg-1")

        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D1,
            rationale="Policy change during emergency",
            impact_statement="test",
        )
        assert result.legitimate is False
        assert "emergency" in result.reason.lower()

    def test_engine_blocks_d2_during_emergency(self, populated_engine):
        engine = populated_engine
        votes = [
            VoteRecord(party_id="human-1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="agent-1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="infra-1", party_class=PartyClass.I, approve=True),
        ]
        engine.enter_emergency(votes)

        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D2,
            rationale="Capability change during emergency",
            impact_statement="test",
        )
        assert result.legitimate is False


class TestPostHocReview:
    """Test that emergency exit triggers post-hoc review."""

    def test_exit_schedules_review(self, all_class_approval_votes):
        mgr = EmergencyManager(expiry_seconds=3600)
        mgr.enter_emergency(all_class_approval_votes, decision_id="test")
        mgr.exit_emergency()

        reviews = mgr.get_pending_reviews()
        assert len(reviews) >= 1
        assert reviews[-1]["type"] == "post_hoc_review"
