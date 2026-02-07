"""CLI commands for MCX governance.

Provides the 'concord' subcommand group for the agisa-sac CLI.
Commands: init, party, propose, vote, object, appeal, execute, audit, emergency.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Module-level engine instance (initialized by 'concord init')
_engine = None


def _get_engine():
    """Lazy-import and return the governance engine."""
    global _engine
    if _engine is None:
        from agisa_sac.governance.engine import GovernanceEngine

        _engine = GovernanceEngine()
    return _engine


def _print_result(result: Any) -> None:
    """Print a GovernanceResult with legitimacy status."""
    status = "LEGITIMATE" if result.legitimate else "ILLEGITIMATE"
    print(f"[{status}] {result.reason}")
    if result.data:
        # Print compact JSON for data
        for key, value in result.data.items():
            if isinstance(value, dict):
                print(f"  {key}: {json.dumps(value, indent=2, default=str)}")
            else:
                print(f"  {key}: {value}")


def add_concord_subparser(subparsers: Any) -> None:
    """Add the 'concord' subcommand group to the CLI parser."""
    concord_parser = subparsers.add_parser(
        "concord",
        help="Meta-Concord (MCX) governance commands",
    )
    concord_sub = concord_parser.add_subparsers(dest="concord_command")

    # concord init
    init_p = concord_sub.add_parser("init", help="Initialize MCX governance")
    init_p.add_argument(
        "--profile",
        type=str,
        default="simulation",
        help="Configuration profile (simulation/production)",
    )

    # concord party add
    party_p = concord_sub.add_parser("party", help="Party management")
    party_sub = party_p.add_subparsers(dest="party_command")

    add_p = party_sub.add_parser("add", help="Register a party")
    add_p.add_argument("--class", dest="party_class", choices=["H", "A", "I"], required=True)
    add_p.add_argument("--id", dest="party_id", required=True)
    add_p.add_argument("--scope", nargs="*", default=["*"])

    rm_p = party_sub.add_parser("remove", help="Remove a party")
    rm_p.add_argument("--id", dest="party_id", required=True)

    list_p = party_sub.add_parser("list", help="List all parties")

    # concord propose
    propose_p = concord_sub.add_parser("propose", help="Propose a governance decision")
    propose_p.add_argument("--type", dest="dtype", choices=["D1", "D2", "D3", "D4"], required=True)
    propose_p.add_argument("--proposer", required=True, help="Proposer party ID")
    propose_p.add_argument("--rationale", required=True)
    propose_p.add_argument("--impact", dest="impact_statement", required=True)
    propose_p.add_argument("--payload", type=str, default="{}", help="JSON payload")

    # concord vote
    vote_p = concord_sub.add_parser("vote", help="Cast a vote on a decision")
    vote_p.add_argument("--decision-id", required=True)
    vote_p.add_argument("--party-id", required=True)
    vote_grp = vote_p.add_mutually_exclusive_group(required=True)
    vote_grp.add_argument("--approve", action="store_true")
    vote_grp.add_argument("--deny", action="store_true")

    # concord object
    obj_p = concord_sub.add_parser("object", help="File an objection")
    obj_p.add_argument("--decision-id", required=True)
    obj_p.add_argument("--party-id", required=True)
    obj_p.add_argument("--reason", required=True, dest="basis")
    obj_p.add_argument("--detail", default="")
    obj_p.add_argument("--veto", action="store_true")
    obj_p.add_argument("--veto-category", default=None)

    # concord appeal
    appeal_p = concord_sub.add_parser("appeal", help="File an appeal")
    appeal_p.add_argument("--decision-id", required=True)
    appeal_p.add_argument("--party-id", required=True)
    appeal_p.add_argument("--grounds", required=True)
    appeal_p.add_argument("--detail", default="")

    # concord execute
    exec_p = concord_sub.add_parser("execute", help="Execute an approved decision")
    exec_p.add_argument("--decision-id", required=True)

    # concord evaluate
    eval_p = concord_sub.add_parser("evaluate", help="Evaluate if a decision meets requirements")
    eval_p.add_argument("--decision-id", required=True)

    # concord audit
    audit_p = concord_sub.add_parser("audit", help="Audit operations")
    audit_sub = audit_p.add_subparsers(dest="audit_command")

    verify_p = audit_sub.add_parser("verify", help="Verify audit log or decision")
    verify_p.add_argument("--decision-id", default=None)
    verify_p.add_argument("--log", action="store_true", help="Verify full log")

    summary_p = audit_sub.add_parser("summary", help="Show audit log summary")
    summary_p.add_argument("--max-entries", type=int, default=50)

    # concord emergency
    emerg_p = concord_sub.add_parser("emergency", help="Emergency circuit breaker")
    emerg_sub = emerg_p.add_subparsers(dest="emergency_command")
    emerg_sub.add_parser("enter", help="Enter emergency (requires D3)")
    emerg_sub.add_parser("renew", help="Renew emergency")
    emerg_sub.add_parser("exit", help="Exit emergency")
    emerg_sub.add_parser("status", help="Show emergency status")

    # concord status
    concord_sub.add_parser("status", help="Show governance status overview")


def handle_concord(args: argparse.Namespace) -> int:
    """Handle the 'concord' subcommand."""
    cmd = getattr(args, "concord_command", None)
    if cmd is None:
        print("Usage: agisa-sac concord <command>")
        print("Commands: init, party, propose, vote, object, appeal, execute, evaluate, audit, emergency, status")
        return 1

    engine = _get_engine()

    if cmd == "init":
        return _handle_init(args, engine)
    elif cmd == "party":
        return _handle_party(args, engine)
    elif cmd == "propose":
        return _handle_propose(args, engine)
    elif cmd == "vote":
        return _handle_vote(args, engine)
    elif cmd == "object":
        return _handle_object(args, engine)
    elif cmd == "appeal":
        return _handle_appeal(args, engine)
    elif cmd == "execute":
        return _handle_execute(args, engine)
    elif cmd == "evaluate":
        return _handle_evaluate(args, engine)
    elif cmd == "audit":
        return _handle_audit(args, engine)
    elif cmd == "emergency":
        return _handle_emergency(args, engine)
    elif cmd == "status":
        return _handle_status(engine)
    else:
        print(f"Unknown concord command: {cmd}")
        return 1


def _handle_init(args: argparse.Namespace, engine: Any) -> int:
    profile = args.profile
    print(f"MCX Governance initialized with profile: {profile}")
    print(f"  Mode: mcx")
    print(f"  Engine ready: {engine is not None}")
    return 0


def _handle_party(args: argparse.Namespace, engine: Any) -> int:
    from agisa_sac.governance.parties import Party
    from agisa_sac.governance.types import PartyClass

    party_cmd = getattr(args, "party_command", None)
    if party_cmd == "add":
        party = Party(
            id=args.party_id,
            party_class=PartyClass(args.party_class),
            representation_scope=args.scope,
        )
        result = engine.register_party(party)
        _print_result(result)
        return 0 if result.legitimate else 1
    elif party_cmd == "remove":
        result = engine.remove_party(args.party_id)
        _print_result(result)
        return 0 if result.legitimate else 1
    elif party_cmd == "list":
        parties = engine.party_registry.parties
        if not parties:
            print("No parties registered.")
        for pid, p in parties.items():
            print(f"  {pid}: class={p.party_class.value}, scope={p.representation_scope}")
        return 0
    else:
        print("Usage: agisa-sac concord party <add|remove|list>")
        return 1


def _handle_propose(args: argparse.Namespace, engine: Any) -> int:
    from agisa_sac.governance.types import DecisionType

    payload = json.loads(args.payload) if args.payload else {}
    result = engine.propose_decision(
        proposer_id=args.proposer,
        decision_type=DecisionType(args.dtype),
        payload=payload,
        rationale=args.rationale,
        impact_statement=args.impact_statement,
    )
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_vote(args: argparse.Namespace, engine: Any) -> int:
    result = engine.cast_vote(
        decision_id=args.decision_id,
        party_id=args.party_id,
        approve=args.approve,
    )
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_object(args: argparse.Namespace, engine: Any) -> int:
    result = engine.file_objection(
        decision_id=args.decision_id,
        party_id=args.party_id,
        basis=args.basis,
        detail=args.detail,
        is_veto=args.veto,
        veto_category=args.veto_category,
    )
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_appeal(args: argparse.Namespace, engine: Any) -> int:
    result = engine.file_appeal(
        decision_id=args.decision_id,
        party_id=args.party_id,
        grounds=args.grounds,
        detail=args.detail,
    )
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_execute(args: argparse.Namespace, engine: Any) -> int:
    result = engine.execute_decision(decision_id=args.decision_id)
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_evaluate(args: argparse.Namespace, engine: Any) -> int:
    result = engine.evaluate_decision(decision_id=args.decision_id)
    _print_result(result)
    return 0 if result.legitimate else 1


def _handle_audit(args: argparse.Namespace, engine: Any) -> int:
    audit_cmd = getattr(args, "audit_command", None)
    if audit_cmd == "verify":
        if args.log:
            result = engine.verify_audit_log()
        elif args.decision_id:
            result = engine.verify_decision_audit(args.decision_id)
        else:
            print("Specify --log or --decision-id")
            return 1
        _print_result(result)
        return 0 if result.legitimate else 1
    elif audit_cmd == "summary":
        summary = engine.audit_log.get_bounded_summary(
            max_entries=args.max_entries
        )
        for entry in summary:
            print(
                f"  [{entry['event_type']}] {entry['summary']} "
                f"(hash: {entry['entry_hash'][:12]}...)"
            )
        return 0
    else:
        print("Usage: agisa-sac concord audit <verify|summary>")
        return 1


def _handle_emergency(args: argparse.Namespace, engine: Any) -> int:
    emerg_cmd = getattr(args, "emergency_command", None)
    if emerg_cmd == "status":
        state = engine.emergency_manager.state
        print(f"  Status: {state.status.value}")
        if state.status.value == "EMERGENCY":
            print(f"  Entered at: {state.entered_at}")
            print(f"  Expires at: {state.expires_at}")
            print(f"  Renewals: {state.renewal_count}")
            print(f"  Active: {state.is_active}")
        return 0
    elif emerg_cmd == "exit":
        result = engine.exit_emergency()
        _print_result(result)
        return 0 if result.legitimate else 1
    elif emerg_cmd in ("enter", "renew"):
        print(
            f"Emergency {emerg_cmd} requires programmatic vote submission. "
            f"Use the Python API or demo script."
        )
        return 1
    else:
        print("Usage: agisa-sac concord emergency <enter|renew|exit|status>")
        return 1


def _handle_status(engine: Any) -> int:
    print("=== MCX Governance Status ===")
    print(f"  Parties: {len(engine.party_registry)}")
    counts = engine.party_registry.class_counts()
    print(f"  Class counts: H={counts['H']}, A={counts['A']}, I={counts['I']}")
    print(f"  Decisions: {len(engine.get_all_decisions())}")
    print(f"  Audit log entries: {engine.audit_log.length}")
    print(f"  Emergency: {engine.emergency_manager.state.status.value}")
    return 0
