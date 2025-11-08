"""Command-line interface for AGI-SAC simulations.

Usage:
    agisa-sac run --config examples/configs/config.json
    agisa-sac run --preset quick_test
    agisa-sac run --preset medium --gpu
    agisa-sac list-presets
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .config import PRESETS, SimulationConfig, get_preset
from .core.orchestrator import SimulationOrchestrator


def list_presets() -> None:
    """List available configuration presets."""
    print("Available configuration presets:\n")
    for name, config in PRESETS.items():
        print(f"  {name:12} - {config.num_agents:3} agents, {config.num_epochs:3} epochs")
    print("\nUsage: agisa-sac run --preset <name>")


def run_simulation(args: argparse.Namespace) -> int:
    """Run a simulation with the specified configuration."""
    # Load configuration
    config: Optional[SimulationConfig] = None

    if args.config:
        # Load from JSON file
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            return 1

        try:
            with open(config_path) as f:
                config_dict = json.load(f)
            config = SimulationConfig.from_dict(config_dict)
            print(f"Loaded configuration from: {config_path}")
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1

    elif args.preset:
        # Load preset
        try:
            config = get_preset(args.preset)
            print(f"Using preset: {args.preset}")
        except KeyError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        # Use default preset
        config = get_preset("default")
        print("Using default configuration")

    # Apply command-line overrides
    if args.gpu:
        config.use_gpu = True
        print("GPU acceleration enabled")

    if args.agents:
        config.num_agents = args.agents
        print(f"Overriding num_agents: {args.agents}")

    if args.epochs:
        config.num_epochs = args.epochs
        print(f"Overriding num_epochs: {args.epochs}")

    if args.seed is not None:
        config.random_seed = args.seed
        print(f"Using random seed: {args.seed}")

    # Run simulation
    print(f"\nStarting simulation: {config.num_agents} agents, {config.num_epochs} epochs")
    print("-" * 60)

    try:
        orchestrator = SimulationOrchestrator(config.to_dict())
        orchestrator.run_simulation()

        print("\n" + "=" * 60)
        print("SIMULATION COMPLETE")
        print("=" * 60)
        print(orchestrator.analyzer.summarize())

        return 0

    except Exception as e:
        print(f"\nError during simulation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="agisa-sac",
        description="AGI Stand Alone Complex - Multi-agent consciousness simulation",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file",
    )
    run_parser.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        help="Use a configuration preset",
    )
    run_parser.add_argument(
        "--gpu",
        action="store_true",
        help="Enable GPU acceleration",
    )
    run_parser.add_argument(
        "--agents",
        type=int,
        help="Override number of agents",
    )
    run_parser.add_argument(
        "--epochs",
        type=int,
        help="Override number of epochs",
    )
    run_parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    run_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output with stack traces",
    )

    # List presets command
    list_parser = subparsers.add_parser("list-presets", help="List configuration presets")

    # Parse arguments
    args = parser.parse_args()

    if args.command == "run":
        return run_simulation(args)
    elif args.command == "list-presets":
        list_presets()
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
