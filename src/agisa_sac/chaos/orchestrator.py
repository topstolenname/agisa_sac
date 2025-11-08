"""Command-line interface for AGI-SAC chaos engineering.

Usage:
    agisa-chaos run --scenario sybil_attack --duration 30
    agisa-chaos run --suite comprehensive
    agisa-chaos list-scenarios
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


def list_scenarios() -> None:
    """List available chaos scenarios."""
    scenarios = {
        "sybil_attack": "Coordinated Sybil attack with multiple fake identities",
        "semantic_drift": "Gradual semantic drift to test coherence boundaries",
        "network_partition": "Network partition and healing (CRDT resilience)",
        "resource_exhaustion": "Resource exhaustion attack",
        "trust_graph_manipulation": "Trust graph manipulation",
        "coordinated_eclipse": "Coordinated eclipse attack",
    }

    print("Available chaos engineering scenarios:\n")
    for name, description in scenarios.items():
        print(f"  {name:28} - {description}")
    print("\nUsage: agisa-chaos run --scenario <name> --duration <minutes>")


async def run_scenario(args: argparse.Namespace) -> int:
    """Run a chaos engineering scenario."""
    try:
        # Import the chaos orchestrator from scripts
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
        from chaos_orchestrator import ChaosOrchestrator

        orchestrator = ChaosOrchestrator(coordinator_url=args.url)

        if args.suite:
            print(f"Running comprehensive chaos suite against: {args.url}")
            print("=" * 60)
            results = await orchestrator.run_comprehensive_chaos_suite()
            print("\n" + "=" * 60)
            print("CHAOS SUITE COMPLETE")
            print("=" * 60)
            print(f"Resilience Score: {results['overall_metrics']['system_resilience_score']:.3f}")
            return 0

        elif args.scenario:
            if args.scenario not in orchestrator.scenarios:
                print(f"Error: Unknown scenario '{args.scenario}'", file=sys.stderr)
                print("Use 'agisa-chaos list-scenarios' to see available scenarios")
                return 1

            print(f"Running chaos scenario: {args.scenario}")
            print(f"Duration: {args.duration} minutes")
            print(f"Target: {args.url}")
            print("-" * 60)

            scenario_func = orchestrator.scenarios[args.scenario]
            results = await scenario_func(args.duration)

            print("\n" + "=" * 60)
            print("SCENARIO COMPLETE")
            print("=" * 60)
            print(f"Results: {results}")
            return 0

        else:
            print("Error: Must specify either --scenario or --suite", file=sys.stderr)
            return 1

    except ImportError as e:
        print(f"Error: Missing dependencies for chaos engineering: {e}", file=sys.stderr)
        print("Install with: pip install agisa-sac[chaos]", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during chaos scenario: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Main CLI entry point for chaos engineering."""
    parser = argparse.ArgumentParser(
        prog="agisa-chaos",
        description="AGI-SAC Chaos Engineering - Test system resilience",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run chaos scenario")
    run_parser.add_argument(
        "--scenario",
        type=str,
        help="Chaos scenario to run",
    )
    run_parser.add_argument(
        "--suite",
        action="store_true",
        help="Run comprehensive chaos test suite",
    )
    run_parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Scenario duration in minutes (default: 30)",
    )
    run_parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Federation coordinator URL (default: http://localhost:8000)",
    )
    run_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output with stack traces",
    )

    # List scenarios command
    list_parser = subparsers.add_parser("list-scenarios", help="List chaos scenarios")

    # Parse arguments
    args = parser.parse_args()

    if args.command == "run":
        return asyncio.run(run_scenario(args))
    elif args.command == "list-scenarios":
        list_scenarios()
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
