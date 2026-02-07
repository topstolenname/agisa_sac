"""Tests for MCX decision rules.

Validates:
- D1/D2 fail without class-wise assent
- D1/D2 fail without quorum H/A/I
- D1/D2 fail if only one class approves
- D0 auto-approved
- D4 requires higher threshold
"""

from __future__ import annotations

import pytest

from agisa_sac.governance.decisions import Decision
from agisa_sac.governance.engine import GovernanceEngine
from agisa_sac.governance.parties import Party
from agisa_sac.governance.types import (
    DecisionLifecycleState,
    DecisionType,
    PartyClass,
)
from agisa_sac.governance.voting import (
    VoteRecord,
    check_quorum,
    check_threshold,
)


class TestQuorum:
    """Test quorum requirements."""

    def test_quorum_all_classes(self):
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        proof = check_quorum(votes)
        assert proof.satisfied is True
        assert proof.class_counts["H"] == 1
        assert proof.class_counts["A"] == 1
        assert proof.class_counts["I"] == 1

    def test_quorum_fails_missing_h(self):
        votes = [
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        proof = check_quorum(votes)
        assert proof.satisfied is False
        assert proof.class_counts["H"] == 0

    def test_quorum_fails_missing_a(self):
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        proof = check_quorum(votes)
        assert proof.satisfied is False

    def test_quorum_fails_missing_i(self):
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
        ]
        proof = check_quorum(votes)
        assert proof.satisfied is False

    def test_quorum_empty_votes(self):
        proof = check_quorum([])
        assert proof.satisfied is False


class TestThreshold:
    """Test threshold and class-wise assent requirements."""

    def test_d1_passes_with_supermajority_and_all_classes(self):
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        proof = check_threshold(votes, DecisionType.D1)
        assert proof.satisfied is True
        assert proof.approval_ratio == 1.0
        assert all(proof.class_wise_assent.values())

    def test_d1_fails_without_class_wise_assent(self):
        """D1 fails if one class doesn't approve."""
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=False),
        ]
        proof = check_threshold(votes, DecisionType.D1)
        assert proof.class_wise_assent["I"] is False
        assert proof.satisfied is False

    def test_d2_fails_without_class_wise_assent(self):
        """D2 fails if one class doesn't approve."""
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=False),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="a2", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
        ]
        proof = check_threshold(votes, DecisionType.D2)
        assert proof.class_wise_assent["H"] is False
        assert proof.satisfied is False

    def test_d1_fails_below_supermajority(self):
        """D1 requires 2/3 approval."""
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=False),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=False),
        ]
        proof = check_threshold(votes, DecisionType.D1)
        assert proof.approval_ratio < 2 / 3
        assert proof.satisfied is False

    def test_d1_fails_only_one_class_approves(self):
        """No D1–D4 can pass with approvals solely from one class."""
        votes = [
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="a2", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="a3", party_class=PartyClass.A, approve=True),
        ]
        proof = check_threshold(votes, DecisionType.D1)
        assert proof.class_wise_assent["H"] is False
        assert proof.class_wise_assent["I"] is False
        assert proof.satisfied is False

    def test_d2_fails_only_one_class_approves(self):
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="h3", party_class=PartyClass.H, approve=True),
        ]
        proof = check_threshold(votes, DecisionType.D2)
        assert proof.satisfied is False

    def test_d4_requires_three_quarters(self):
        """D4 requires 3/4 threshold."""
        # 3 approve, 1 reject = 75% = passes
        votes = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=True),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=False),
        ]
        proof = check_threshold(votes, DecisionType.D4)
        assert proof.satisfied is True

        # 2 approve, 2 reject = 50% = fails
        votes2 = [
            VoteRecord(party_id="h1", party_class=PartyClass.H, approve=True),
            VoteRecord(party_id="a1", party_class=PartyClass.A, approve=True),
            VoteRecord(party_id="i1", party_class=PartyClass.I, approve=False),
            VoteRecord(party_id="h2", party_class=PartyClass.H, approve=False),
        ]
        proof2 = check_threshold(votes2, DecisionType.D4)
        assert proof2.satisfied is False


class TestDecisionLifecycle:
    """Test the full decision lifecycle through the engine."""

    def test_d0_auto_approved(self, populated_engine):
        result = populated_engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D0,
            rationale="Routine action",
            impact_statement="No impact",
        )
        assert result.legitimate is True
        assert "pre-authorized" in result.reason

    def test_d1_full_lifecycle(self, populated_engine):
        engine = populated_engine

        # Propose
        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D1,
            rationale="Add new party",
            impact_statement="Minimal impact",
        )
        assert result.legitimate is True
        decision_id = result.decision_id

        # Vote - all approve
        engine.cast_vote(decision_id, "human-1", approve=True)
        engine.cast_vote(decision_id, "agent-1", approve=True)
        engine.cast_vote(decision_id, "infra-1", approve=True)

        # Evaluate
        eval_result = engine.evaluate_decision(decision_id)
        assert eval_result.legitimate is True
        assert "APPROVED" in eval_result.reason

        # Execute
        exec_result = engine.execute_decision(decision_id)
        assert exec_result.legitimate is True
        assert "EXECUTED" in exec_result.reason
        assert "ep_id" in exec_result.data

    def test_d1_rejected_without_quorum(self, engine):
        """D1 fails without all three classes voting."""
        # Only register H and A
        engine.register_party(Party(id="h1", party_class=PartyClass.H))
        engine.register_party(Party(id="a1", party_class=PartyClass.A))

        result = engine.propose_decision(
            proposer_id="h1",
            decision_type=DecisionType.D1,
            rationale="test",
            impact_statement="test",
        )
        decision_id = result.decision_id

        engine.cast_vote(decision_id, "h1", approve=True)
        engine.cast_vote(decision_id, "a1", approve=True)

        eval_result = engine.evaluate_decision(decision_id)
        assert eval_result.legitimate is False
        assert "Quorum" in eval_result.reason

    def test_cannot_execute_unapproved(self, populated_engine):
        """Cannot execute a decision that hasn't been approved."""
        result = populated_engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D2,
            rationale="test",
            impact_statement="test",
        )
        exec_result = populated_engine.execute_decision(result.decision_id)
        assert exec_result.legitimate is False

    def test_duplicate_vote_rejected(self, populated_engine):
        result = populated_engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D1,
            rationale="test",
            impact_statement="test",
        )
        did = result.decision_id
        populated_engine.cast_vote(did, "human-1", approve=True)
        result2 = populated_engine.cast_vote(did, "human-1", approve=True)
        assert result2.legitimate is False
        assert "already voted" in result2.reason


class TestCaptureResistance:
    """Test that governance capture by a single class is prevented."""

    def test_coalition_of_agents_cannot_pass_d1(self, multi_party_engine):
        """A coalition of A parties cannot pass D1 without H and I assent."""
        engine = multi_party_engine

        result = engine.propose_decision(
            proposer_id="agent-1",
            decision_type=DecisionType.D1,
            rationale="Agent-proposed policy",
            impact_statement="Expands agent capabilities",
        )
        did = result.decision_id

        # All agents approve, H and I reject
        engine.cast_vote(did, "agent-1", approve=True)
        engine.cast_vote(did, "agent-2", approve=True)
        engine.cast_vote(did, "human-1", approve=False)
        engine.cast_vote(did, "human-2", approve=False)
        engine.cast_vote(did, "infra-1", approve=False)
        engine.cast_vote(did, "infra-2", approve=False)

        eval_result = engine.evaluate_decision(did)
        assert eval_result.legitimate is False

    def test_coalition_of_agents_cannot_pass_d2(self, multi_party_engine):
        """A coalition of A parties cannot pass D2 without H and I assent."""
        engine = multi_party_engine

        result = engine.propose_decision(
            proposer_id="agent-1",
            decision_type=DecisionType.D2,
            rationale="Agent capability expansion",
            impact_statement="Significant capability change",
        )
        did = result.decision_id

        # Only A class approves
        engine.cast_vote(did, "agent-1", approve=True)
        engine.cast_vote(did, "agent-2", approve=True)
        engine.cast_vote(did, "human-1", approve=False)
        engine.cast_vote(did, "infra-1", approve=False)

        eval_result = engine.evaluate_decision(did)
        assert eval_result.legitimate is False

    def test_requires_multi_class_approval(self, multi_party_engine):
        """Even with supermajority from one class, need cross-class assent."""
        engine = multi_party_engine
        # Register extra H parties for supermajority
        engine.register_party(Party(id="human-3", party_class=PartyClass.H))
        engine.register_party(Party(id="human-4", party_class=PartyClass.H))

        result = engine.propose_decision(
            proposer_id="human-1",
            decision_type=DecisionType.D1,
            rationale="Human-dominated vote",
            impact_statement="test",
        )
        did = result.decision_id

        # 4 H approve, A and I reject
        for hid in ["human-1", "human-2", "human-3", "human-4"]:
            engine.cast_vote(did, hid, approve=True)
        engine.cast_vote(did, "agent-1", approve=False)
        engine.cast_vote(did, "infra-1", approve=False)

        eval_result = engine.evaluate_decision(did)
        # Even though 4/6 = 66.7% >= 2/3, class-wise assent fails
        assert eval_result.legitimate is False
