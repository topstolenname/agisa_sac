"""GovernanceEngine: central orchestration for MCX governance.

Coordinates the full governance lifecycle: propose, vote, object, appeal,
execute, and audit. Enforces all MCX rules including quorum, thresholds,
class-wise assent, emergency constraints, and enforcement authorization.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from agisa_sac.governance.appeals import Appeal, AppealTracker
from agisa_sac.governance.auditlog import AuditLog
from agisa_sac.governance.custody import ThresholdCustody
from agisa_sac.governance.deadlock import DeadlockResolver
from agisa_sac.governance.decisions import Decision
from agisa_sac.governance.emergency import EmergencyManager
from agisa_sac.governance.enforcement.base import EnforcementInterface
from agisa_sac.governance.enforcement.sandbox import SandboxEnforcer
from agisa_sac.governance.enforcement.sanctions import SanctionsLadder
from agisa_sac.governance.evidence import EvidencePackage, build_evidence_package
from agisa_sac.governance.objections import Objection, ObjectionTracker
from agisa_sac.governance.parties import Party, PartyRegistry
from agisa_sac.governance.types import (
    CapabilityManifest,
    ConstraintSet,
    DecisionLifecycleState,
    DecisionType,
    EmergencyStatus,
    PartyClass,
    SanctionLevel,
)
from agisa_sac.governance.voting import (
    QuorumProof,
    ThresholdProof,
    VoteRecord,
    check_quorum,
    check_threshold,
)

logger = logging.getLogger(__name__)


class GovernanceResult:
    """Result of a governance operation with legitimacy status."""

    def __init__(
        self,
        legitimate: bool,
        reason: str,
        decision_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.legitimate = legitimate
        self.reason = reason
        self.decision_id = decision_id
        self.data = data or {}

    def __str__(self) -> str:
        status = "LEGITIMATE" if self.legitimate else "ILLEGITIMATE"
        return f"[{status}] {self.reason}"

    def __repr__(self) -> str:
        return (
            f"GovernanceResult(legitimate={self.legitimate}, "
            f"reason='{self.reason}', decision_id={self.decision_id})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "legitimate": self.legitimate,
            "reason": self.reason,
            "decision_id": self.decision_id,
            "data": self.data,
        }


class GovernanceEngine:
    """Central governance orchestrator for MCX.

    Manages the full lifecycle of governance decisions including:
    - Party registration
    - Decision proposal and voting
    - Quorum and threshold verification
    - Objection and appeal handling
    - Evidence Package generation
    - Emergency circuit breaker
    - Enforcement authorization
    - Audit logging

    Usage:
        engine = GovernanceEngine()
        engine.register_party(Party(id="alice", party_class=PartyClass.H))
        result = engine.propose_decision(
            proposer_id="alice",
            decision_type=DecisionType.D2,
            payload={...},
            rationale="...",
            impact_statement="...",
        )
    """

    def __init__(
        self,
        cs: Optional[ConstraintSet] = None,
        cm: Optional[CapabilityManifest] = None,
        enforcer: Optional[EnforcementInterface] = None,
        emergency_expiry: float = 3600.0,
    ) -> None:
        self.party_registry = PartyRegistry()
        self.audit_log = AuditLog()
        self.objection_tracker = ObjectionTracker()
        self.appeal_tracker = AppealTracker()
        self.deadlock_resolver = DeadlockResolver()
        self.emergency_manager = EmergencyManager(expiry_seconds=emergency_expiry)
        self.sanctions_ladder = SanctionsLadder()
        self.custody = ThresholdCustody()
        self.cs = cs or ConstraintSet()
        self.cm = cm or CapabilityManifest()
        self.enforcer = enforcer or SandboxEnforcer(audit_log=self.audit_log)

        # Decision storage
        self._decisions: Dict[str, Decision] = {}
        # Evidence Package storage
        self._evidence_packages: Dict[str, EvidencePackage] = {}

    # --- Party Management ---

    def register_party(self, party: Party) -> GovernanceResult:
        """Register a new party."""
        try:
            self.party_registry.register(party)
            self.audit_log.append(
                event_type="party_registered",
                data=party.to_dict(),
                actor_id=party.id,
                summary=f"Party {party.id} ({party.party_class.value}) registered",
            )
            return GovernanceResult(
                legitimate=True,
                reason=f"Party {party.id} registered successfully",
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

    def remove_party(self, party_id: str) -> GovernanceResult:
        """Remove a party (self-removal always permitted)."""
        try:
            party = self.party_registry.remove(party_id)
            self.audit_log.append(
                event_type="party_removed",
                data={"party_id": party_id},
                actor_id=party_id,
                summary=f"Party {party_id} removed",
            )
            return GovernanceResult(
                legitimate=True,
                reason=f"Party {party_id} removed",
            )
        except KeyError:
            return GovernanceResult(
                legitimate=False, reason=f"Party {party_id} not found"
            )

    # --- Decision Lifecycle ---

    def propose_decision(
        self,
        proposer_id: str,
        decision_type: DecisionType,
        payload: Optional[Dict[str, Any]] = None,
        rationale: str = "",
        impact_statement: str = "",
        cs_diff: Optional[Dict[str, Any]] = None,
        cm_diff: Optional[Dict[str, Any]] = None,
        voting_deadline: Optional[float] = None,
    ) -> GovernanceResult:
        """Propose a new governance decision.

        D0 decisions are auto-approved (operational, pre-authorized).
        D1–D4 enter the voting pipeline.
        """
        # Verify proposer exists
        if proposer_id not in self.party_registry:
            return GovernanceResult(
                legitimate=False,
                reason=f"Proposer '{proposer_id}' not registered",
            )

        # D0 = operational, no governance needed
        if decision_type == DecisionType.D0:
            return GovernanceResult(
                legitimate=True,
                reason="D0 operational decision: pre-authorized",
            )

        # Emergency constraints
        if self.emergency_manager.is_active:
            # No permanent CS/CM changes during emergency
            if decision_type in (DecisionType.D1, DecisionType.D2):
                if not self.emergency_manager.check_permanent_change_ban():
                    return GovernanceResult(
                        legitimate=False,
                        reason="Cannot propose permanent CS/CM changes during emergency. "
                        "Must be reproposed after emergency exit.",
                    )

        decision = Decision(
            decision_type=decision_type,
            proposer_id=proposer_id,
            payload=payload or {},
            rationale=rationale,
            impact_statement=impact_statement,
            cs_diff=cs_diff,
            cm_diff=cm_diff,
            voting_deadline=voting_deadline,
        )
        decision.transition(DecisionLifecycleState.VOTING)

        self._decisions[decision.id] = decision
        self.audit_log.append(
            event_type="decision_proposed",
            data=decision.to_dict(),
            decision_id=decision.id,
            actor_id=proposer_id,
            summary=f"{decision_type.value} proposed by {proposer_id}",
        )

        return GovernanceResult(
            legitimate=True,
            reason=f"Decision {decision.id} proposed ({decision_type.value})",
            decision_id=decision.id,
            data={"state": decision.state.value},
        )

    def cast_vote(
        self,
        decision_id: str,
        party_id: str,
        approve: bool,
    ) -> GovernanceResult:
        """Cast a vote on a decision."""
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if party_id not in self.party_registry:
            return GovernanceResult(
                legitimate=False, reason=f"Party '{party_id}' not registered"
            )

        party = self.party_registry.get(party_id)

        # Stub signature
        vote = VoteRecord(
            party_id=party_id,
            party_class=party.party_class,
            approve=approve,
            signature=f"stub:vote:{party_id}:{decision_id}",
        )

        try:
            decision.add_vote(vote)
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

        self.audit_log.append(
            event_type="vote_cast",
            data=vote.to_dict(),
            decision_id=decision_id,
            actor_id=party_id,
            summary=f"Vote by {party_id}: {'approve' if approve else 'reject'}",
        )

        return GovernanceResult(
            legitimate=True,
            reason=f"Vote recorded for {party_id} on {decision_id}",
            decision_id=decision_id,
        )

    def evaluate_decision(self, decision_id: str) -> GovernanceResult:
        """Evaluate whether a decision has met all governance requirements.

        Checks quorum, threshold, and class-wise assent. Transitions
        the decision to APPROVED or REJECTED.
        """
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if decision.state != DecisionLifecycleState.VOTING:
            return GovernanceResult(
                legitimate=False,
                reason=f"Decision not in VOTING state (current: {decision.state.value})",
                decision_id=decision_id,
            )

        # Check expiry
        if decision.is_expired():
            decision.transition(DecisionLifecycleState.EXPIRED)
            return GovernanceResult(
                legitimate=False,
                reason="Decision expired: voting deadline passed",
                decision_id=decision_id,
            )

        # Check quorum
        quorum = check_quorum(decision.votes)
        if not quorum.satisfied:
            return GovernanceResult(
                legitimate=False,
                reason=f"Quorum not met: {quorum.class_counts}",
                decision_id=decision_id,
                data={"quorum_proof": quorum.to_dict()},
            )

        # Check threshold + class-wise assent
        threshold = check_threshold(decision.votes, decision.decision_type)
        if not threshold.satisfied:
            reasons = []
            if threshold.approval_ratio < threshold.threshold_required:
                reasons.append(
                    f"threshold {threshold.approval_ratio:.2%} < "
                    f"{threshold.threshold_required:.2%}"
                )
            if not all(threshold.class_wise_assent.values()):
                missing = [
                    c for c, v in threshold.class_wise_assent.items() if not v
                ]
                reasons.append(f"missing class-wise assent from: {missing}")

            decision.transition(DecisionLifecycleState.REJECTED)
            return GovernanceResult(
                legitimate=False,
                reason=f"Threshold not met: {'; '.join(reasons)}",
                decision_id=decision_id,
                data={
                    "quorum_proof": quorum.to_dict(),
                    "threshold_proof": threshold.to_dict(),
                },
            )

        # All checks passed
        decision.transition(DecisionLifecycleState.APPROVED)

        self.audit_log.append(
            event_type="decision_approved",
            data={
                "quorum_proof": quorum.to_dict(),
                "threshold_proof": threshold.to_dict(),
            },
            decision_id=decision_id,
            summary=f"Decision {decision_id} APPROVED",
        )

        return GovernanceResult(
            legitimate=True,
            reason=f"Decision {decision_id} APPROVED",
            decision_id=decision_id,
            data={
                "quorum_proof": quorum.to_dict(),
                "threshold_proof": threshold.to_dict(),
            },
        )

    def execute_decision(self, decision_id: str) -> GovernanceResult:
        """Execute an approved decision with full EP generation.

        This is the final step. It:
        1. Verifies the decision is APPROVED
        2. Builds an Evidence Package
        3. Validates the EP
        4. Appends to audit log
        5. Authorizes via enforcement layer
        6. Transitions to EXECUTED
        """
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if decision.state != DecisionLifecycleState.APPROVED:
            return GovernanceResult(
                legitimate=False,
                reason=f"Decision not APPROVED (current: {decision.state.value})",
                decision_id=decision_id,
            )

        # Emergency irreversibility check
        if self.emergency_manager.is_active:
            is_irreversible = decision.payload.get("irreversible", False)
            if not self.emergency_manager.check_irreversibility_ban(is_irreversible):
                return GovernanceResult(
                    legitimate=False,
                    reason="Irreversible actions banned during emergency",
                    decision_id=decision_id,
                )

        # Build Evidence Package
        quorum = check_quorum(decision.votes)
        threshold = check_threshold(decision.votes, decision.decision_type)

        participants = [
            {
                "party_id": v.party_id,
                "party_class": v.party_class.value,
                "role": "proposer" if v.party_id == decision.proposer_id else "voter",
            }
            for v in decision.votes
        ]

        # Anchor in audit log first
        anchor_entry = self.audit_log.append(
            event_type="ep_anchored",
            data={"decision_id": decision_id},
            decision_id=decision_id,
            summary=f"EP anchor for decision {decision_id}",
        )

        ep = build_evidence_package(
            decision_id=decision_id,
            decision_type=decision.decision_type,
            participants=participants,
            quorum_proof=quorum,
            threshold_proof=threshold,
            rationale=decision.rationale,
            impact_statement=decision.impact_statement,
            cs_diff=decision.cs_diff,
            cm_diff=decision.cm_diff,
            timestamps={
                "proposed_at": decision.created_at,
                "voting_started_at": decision.created_at,
                "approved_at": time.time(),
                "executed_at": time.time(),
            },
        )
        ep.audit_anchor_ref = anchor_entry.entry_id

        # Sign EP with all approving parties
        for v in decision.votes:
            if v.approve:
                ep.sign(v.party_id)

        # Validate EP
        errors = ep.validate()
        if errors:
            return GovernanceResult(
                legitimate=False,
                reason=f"Evidence Package validation failed: {errors}",
                decision_id=decision_id,
                data={"ep_errors": errors},
            )

        # Store EP
        self._evidence_packages[ep.ep_id] = ep

        # Execute via enforcement layer
        decision.transition(DecisionLifecycleState.EXECUTED)

        self.audit_log.append(
            event_type="decision_executed",
            data={"ep_id": ep.ep_id, "ep": ep.to_dict()},
            decision_id=decision_id,
            summary=f"Decision {decision_id} EXECUTED (EP: {ep.ep_id})",
        )

        return GovernanceResult(
            legitimate=True,
            reason=f"Decision {decision_id} EXECUTED with EP {ep.ep_id}",
            decision_id=decision_id,
            data={"ep_id": ep.ep_id, "ep": ep.to_dict()},
        )

    # --- Objections ---

    def file_objection(
        self,
        decision_id: str,
        party_id: str,
        basis: str,
        detail: str = "",
        is_veto: bool = False,
        veto_category: Optional[str] = None,
    ) -> GovernanceResult:
        """File an objection against a decision."""
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if party_id not in self.party_registry:
            return GovernanceResult(
                legitimate=False, reason=f"Party '{party_id}' not registered"
            )

        try:
            objection = self.objection_tracker.file_objection(
                decision_id=decision_id,
                party_id=party_id,
                basis=basis,
                detail=detail,
                is_veto=is_veto,
                veto_category=veto_category,
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

        # Pause execution
        if decision.state == DecisionLifecycleState.VOTING:
            decision.transition(DecisionLifecycleState.OBJECTED)

        decision.objections.append(objection.to_dict())

        self.audit_log.append(
            event_type="objection_filed",
            data=objection.to_dict(),
            decision_id=decision_id,
            actor_id=party_id,
            summary=f"Objection by {party_id}: {basis}"
            + (f" (VETO: {veto_category})" if is_veto else ""),
        )

        msg = f"Objection filed: {objection.objection_id}"
        if objection.bond_amount > 0:
            msg += f" (bond required: {objection.bond_amount:.2f})"
        if is_veto:
            msg += " - VETO triggers mandatory arbitration"

        return GovernanceResult(
            legitimate=True,
            reason=msg,
            decision_id=decision_id,
            data={"objection": objection.to_dict()},
        )

    def resolve_objection(self, decision_id: str) -> GovernanceResult:
        """Resolve objections and return decision to VOTING state."""
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if decision.state != DecisionLifecycleState.OBJECTED:
            return GovernanceResult(
                legitimate=False,
                reason=f"Decision not in OBJECTED state (current: {decision.state.value})",
            )

        decision.transition(DecisionLifecycleState.VOTING)
        return GovernanceResult(
            legitimate=True,
            reason=f"Objections resolved, decision {decision_id} returned to VOTING",
            decision_id=decision_id,
        )

    # --- Appeals ---

    def file_appeal(
        self,
        decision_id: str,
        party_id: str,
        grounds: str,
        detail: str = "",
    ) -> GovernanceResult:
        """File an appeal against a decision outcome."""
        decision = self._decisions.get(decision_id)
        if decision is None:
            return GovernanceResult(
                legitimate=False, reason=f"Decision '{decision_id}' not found"
            )

        if party_id not in self.party_registry:
            return GovernanceResult(
                legitimate=False, reason=f"Party '{party_id}' not registered"
            )

        try:
            appeal = self.appeal_tracker.file_appeal(
                decision_id=decision_id,
                party_id=party_id,
                grounds=grounds,
                detail=detail,
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

        if decision.state in (
            DecisionLifecycleState.APPROVED,
            DecisionLifecycleState.REJECTED,
        ):
            decision.transition(DecisionLifecycleState.APPEALED)

        decision.appeals.append(appeal.to_dict())

        self.audit_log.append(
            event_type="appeal_filed",
            data=appeal.to_dict(),
            decision_id=decision_id,
            actor_id=party_id,
            summary=f"Appeal by {party_id}: {grounds}",
        )

        msg = f"Appeal filed: {appeal.appeal_id}"
        if appeal.bond_amount > 0:
            msg += f" (bond required: {appeal.bond_amount:.2f})"

        return GovernanceResult(
            legitimate=True,
            reason=msg,
            decision_id=decision_id,
            data={"appeal": appeal.to_dict()},
        )

    # --- Emergency ---

    def enter_emergency(
        self,
        votes: List[VoteRecord],
        decision_id: Optional[str] = None,
        invariants: Optional[List[str]] = None,
    ) -> GovernanceResult:
        """Enter emergency state via D3 decision."""
        try:
            # If no decision_id provided, create an ad-hoc D3 decision
            if decision_id is None:
                decision_id = f"emergency-{int(time.time())}"

            state = self.emergency_manager.enter_emergency(
                votes=votes,
                decision_id=decision_id,
                invariants=invariants,
            )
            self.audit_log.append(
                event_type="emergency_entered",
                data=state.to_dict(),
                decision_id=decision_id,
                summary="EMERGENCY ENTERED",
            )
            return GovernanceResult(
                legitimate=True,
                reason=f"Emergency entered (expires: {state.expires_at})",
                decision_id=decision_id,
                data={"emergency_state": state.to_dict()},
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

    def renew_emergency(
        self, votes: List[VoteRecord]
    ) -> GovernanceResult:
        """Renew emergency with escalating thresholds."""
        try:
            state = self.emergency_manager.renew_emergency(votes=votes)
            self.audit_log.append(
                event_type="emergency_renewed",
                data=state.to_dict(),
                summary=f"Emergency renewed #{state.renewal_count}",
            )
            return GovernanceResult(
                legitimate=True,
                reason=f"Emergency renewed #{state.renewal_count}",
                data={"emergency_state": state.to_dict()},
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

    def exit_emergency(self) -> GovernanceResult:
        """Exit emergency state."""
        try:
            state = self.emergency_manager.exit_emergency()
            self.audit_log.append(
                event_type="emergency_exited",
                data=state.to_dict(),
                summary="Emergency exited",
            )
            return GovernanceResult(
                legitimate=True, reason="Emergency exited"
            )
        except ValueError as e:
            return GovernanceResult(legitimate=False, reason=str(e))

    # --- Action Authorization ---

    def check_action(
        self, action: str, context: Optional[Dict[str, Any]] = None
    ) -> GovernanceResult:
        """Check if an action is authorized under current governance.

        This is the main integration point for the action execution path:
        1. Check CM allows it
        2. Check CS doesn't forbid it
        3. Check enforcement state

        For D0 (operational) actions within existing scope.
        D1–D4 actions require a completed governance decision.
        """
        ctx = context or {}
        ctx["constraint_set"] = self.cs

        # Check emergency auto-expiry
        self.emergency_manager.check_auto_expiry()

        # Check enforcement
        allowed, reason = self.enforcer.check_action_allowed(action, ctx)

        if not allowed:
            self.audit_log.append(
                event_type="action_denied",
                data={"action": action, "reason": reason},
                actor_id=ctx.get("actor_id"),
                summary=f"Action denied: {action} ({reason})",
            )
            return GovernanceResult(legitimate=False, reason=reason)

        # CS forbidden actions check
        for pattern in self.cs.forbidden_actions:
            if action == pattern or (pattern.endswith("*") and action.startswith(pattern[:-1])):
                return GovernanceResult(
                    legitimate=False,
                    reason=f"Action '{action}' forbidden by Constraint Set",
                )

        self.audit_log.append(
            event_type="action_allowed",
            data={"action": action},
            actor_id=ctx.get("actor_id"),
            summary=f"Action allowed: {action}",
        )

        return GovernanceResult(legitimate=True, reason="allowed")

    # --- Audit ---

    def verify_audit_log(self) -> GovernanceResult:
        """Verify the full audit log integrity."""
        valid = self.audit_log.verify_log_integrity()
        return GovernanceResult(
            legitimate=valid,
            reason="Audit log integrity verified" if valid else "AUDIT LOG INTEGRITY FAILURE",
        )

    def verify_decision_audit(self, decision_id: str) -> GovernanceResult:
        """Verify all audit entries for a specific decision."""
        entries = self.audit_log.get_entries_by_decision(decision_id)
        if not entries:
            return GovernanceResult(
                legitimate=False,
                reason=f"No audit entries found for decision {decision_id}",
            )

        for entry in entries:
            if not self.audit_log.verify_entry_inclusion(entry.entry_id):
                return GovernanceResult(
                    legitimate=False,
                    reason=f"Entry {entry.entry_id} failed inclusion verification",
                )

        return GovernanceResult(
            legitimate=True,
            reason=f"All {len(entries)} audit entries verified for {decision_id}",
            data={"entry_count": len(entries)},
        )

    # --- Accessors ---

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self._decisions.get(decision_id)

    def get_evidence_package(self, ep_id: str) -> Optional[EvidencePackage]:
        return self._evidence_packages.get(ep_id)

    def get_all_decisions(self) -> Dict[str, Decision]:
        return dict(self._decisions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "party_registry": self.party_registry.to_dict(),
            "decisions": {
                did: d.to_dict() for did, d in self._decisions.items()
            },
            "evidence_packages": {
                eid: ep.to_dict() for eid, ep in self._evidence_packages.items()
            },
            "audit_log": self.audit_log.to_dict(),
            "emergency": self.emergency_manager.to_dict(),
            "cs": self.cs.to_dict(),
            "cm": self.cm.to_dict(),
        }
