#!/usr/bin/env python3
"""
Meta-Concord (MCX) Governance Demo

Demonstrates the full MCX governance lifecycle:
1. Register parties (H/A/I)
2. Propose a D2 capability restriction
3. Vote + generate Evidence Package
4. Execute via enforcement layer
5. Demonstrate objection + arbitration
6. Demonstrate emergency entry + expiry

Usage:
    python examples/mcx_governance_demo.py

Requires:
    pip install -e .  (or PYTHONPATH includes src/)
"""

from __future__ import annotations

import sys
import time

# Ensure src is importable
sys.path.insert(0, "src")

from agisa_sac.governance.engine import GovernanceEngine
from agisa_sac.governance.enforcement.sandbox import SandboxEnforcer
from agisa_sac.governance.parties import Party
from agisa_sac.governance.types import (
    CapabilityManifest,
    ConstraintSet,
    DecisionType,
    PartyClass,
)
from agisa_sac.governance.voting import VoteRecord


def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(result) -> None:
    status = "LEGITIMATE" if result.legitimate else "ILLEGITIMATE"
    print(f"  [{status}] {result.reason}")


def main() -> int:
    # ============================================================
    # Setup
    # ============================================================
    print_header("MCX Governance Demo")

    cs = ConstraintSet(
        forbidden_actions=["delete_all_data", "bypass_governance"],
        invariants=["audit_log_intact", "all_actions_logged"],
    )
    cm = CapabilityManifest(
        tool_allowlist=["read_data", "write_data", "analyze", "report"],
        data_scopes=["/data/*", "/reports/*"],
        network_egress=["api.approved.com"],
    )
    engine = GovernanceEngine(cs=cs, cm=cm, emergency_expiry=30.0)

    # ============================================================
    # 1. Register Parties
    # ============================================================
    print_header("1. Register Parties")

    parties = [
        Party(id="alice", party_class=PartyClass.H, representation_scope=["*"]),
        Party(id="bob", party_class=PartyClass.H, representation_scope=["*"]),
        Party(id="agent-alpha", party_class=PartyClass.A, representation_scope=["*"]),
        Party(id="agent-beta", party_class=PartyClass.A, representation_scope=["*"]),
        Party(id="infra-monitor", party_class=PartyClass.I, representation_scope=["*"]),
    ]

    for party in parties:
        result = engine.register_party(party)
        print_result(result)

    print(f"\n  Total parties: {len(engine.party_registry)}")
    print(f"  Class counts: {engine.party_registry.class_counts()}")

    # ============================================================
    # 2. Propose D2 Capability Restriction
    # ============================================================
    print_header("2. Propose D2 Capability Restriction")

    result = engine.propose_decision(
        proposer_id="alice",
        decision_type=DecisionType.D2,
        payload={"target": "agent-alpha", "restriction": "remove network egress to *.external.com"},
        rationale="Agent-alpha's network egress scope exceeds audited requirements.",
        impact_statement="Agent-alpha loses access to undocumented external endpoints.",
        cm_diff={
            "removed": {"network_egress": ["*.external.com"]},
            "modified": {"network_egress": ["api.approved.com"]},
        },
    )
    print_result(result)
    decision_id = result.decision_id
    print(f"  Decision ID: {decision_id}")

    # ============================================================
    # 3. Vote
    # ============================================================
    print_header("3. Voting Phase")

    votes = [
        ("alice", True),
        ("bob", True),
        ("agent-alpha", True),
        ("agent-beta", True),
        ("infra-monitor", True),
    ]

    for party_id, approve in votes:
        result = engine.cast_vote(decision_id, party_id, approve)
        action = "approve" if approve else "reject"
        print(f"  {party_id} votes to {action}")

    # Evaluate
    print("\n  Evaluating decision...")
    eval_result = engine.evaluate_decision(decision_id)
    print_result(eval_result)

    # ============================================================
    # 4. Execute with EP
    # ============================================================
    print_header("4. Execute Decision")

    exec_result = engine.execute_decision(decision_id)
    print_result(exec_result)
    if exec_result.data.get("ep_id"):
        print(f"  Evidence Package ID: {exec_result.data['ep_id']}")

    # Verify audit
    audit_result = engine.verify_decision_audit(decision_id)
    print(f"  Audit verification: {audit_result}")

    # ============================================================
    # 5. Demonstrate Objection + Arbitration
    # ============================================================
    print_header("5. Objection + Arbitration Demo")

    # Propose another decision
    result2 = engine.propose_decision(
        proposer_id="agent-beta",
        decision_type=DecisionType.D2,
        rationale="Expand agent-beta's compute quota",
        impact_statement="Increases compute allocation by 50%",
    )
    did2 = result2.decision_id
    print(f"  New decision: {did2}")

    # File objection
    obj_result = engine.file_objection(
        decision_id=did2,
        party_id="alice",
        basis="inadequate_impact_statement",
        detail="Impact statement does not address resource contention",
    )
    print_result(obj_result)

    # Check state
    decision2 = engine.get_decision(did2)
    print(f"  Decision state: {decision2.state.value}")

    # File repeated objection (triggers bonding)
    obj2_result = engine.file_objection(
        decision_id=did2,
        party_id="alice",
        basis="inadequate_impact_statement",
        detail="Still inadequate",
    )
    print_result(obj2_result)
    print("  (Note: bonding triggered for repeated objection)")

    # Resolve and continue
    engine.resolve_objection(did2)
    print(f"  Decision state after resolution: {engine.get_decision(did2).state.value}")

    # ============================================================
    # 6. Emergency Entry + Expiry Demo
    # ============================================================
    print_header("6. Emergency Circuit Breaker Demo")

    # Multi-class approval votes for emergency
    emergency_votes = [
        VoteRecord(party_id="alice", party_class=PartyClass.H, approve=True),
        VoteRecord(party_id="agent-alpha", party_class=PartyClass.A, approve=True),
        VoteRecord(party_id="infra-monitor", party_class=PartyClass.I, approve=True),
    ]

    emg_result = engine.enter_emergency(
        votes=emergency_votes,
        invariants=["no_external_network", "audit_required"],
    )
    print_result(emg_result)
    print(f"  Emergency active: {engine.emergency_manager.is_active}")

    # Try D1 during emergency (should fail)
    d1_result = engine.propose_decision(
        proposer_id="alice",
        decision_type=DecisionType.D1,
        rationale="Policy change during emergency",
        impact_statement="test",
    )
    print(f"  D1 during emergency: {d1_result}")

    # Renew emergency
    renew_result = engine.renew_emergency(emergency_votes)
    print_result(renew_result)
    print(f"  Renewal count: {engine.emergency_manager.state.renewal_count}")
    print(f"  Next renewal threshold: {engine.emergency_manager.get_renewal_threshold():.2%}")

    # Exit emergency
    exit_result = engine.exit_emergency()
    print_result(exit_result)
    print(f"  Emergency active: {engine.emergency_manager.is_active}")

    # Check pending reviews
    reviews = engine.emergency_manager.get_pending_reviews()
    print(f"  Pending post-hoc reviews: {len(reviews)}")

    # ============================================================
    # 7. Capture Resistance Demo
    # ============================================================
    print_header("7. Capture Resistance Demo")

    result3 = engine.propose_decision(
        proposer_id="agent-alpha",
        decision_type=DecisionType.D1,
        rationale="Grant all agents unrestricted access",
        impact_statement="Major capability expansion",
    )
    did3 = result3.decision_id

    # Only agents approve
    engine.cast_vote(did3, "agent-alpha", approve=True)
    engine.cast_vote(did3, "agent-beta", approve=True)
    engine.cast_vote(did3, "alice", approve=False)
    engine.cast_vote(did3, "bob", approve=False)
    engine.cast_vote(did3, "infra-monitor", approve=False)

    eval3 = engine.evaluate_decision(did3)
    print_result(eval3)
    print("  (Correctly rejected: agent-only coalition cannot pass D1)")

    # ============================================================
    # 8. Audit Log Summary
    # ============================================================
    print_header("8. Audit Log Summary")

    log_result = engine.verify_audit_log()
    print_result(log_result)
    print(f"  Total entries: {engine.audit_log.length}")

    summary = engine.audit_log.get_bounded_summary(max_entries=10)
    print(f"  Last {len(summary)} entries:")
    for entry in summary:
        print(f"    [{entry['event_type']}] {entry['summary']}")

    # ============================================================
    # Done
    # ============================================================
    print_header("Demo Complete")
    print("  All governance operations demonstrated successfully.")
    print("  Run tests with: pytest tests/governance/ -v")
    return 0


if __name__ == "__main__":
    sys.exit(main())
