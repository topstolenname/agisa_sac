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
import logging
import sys
from pathlib import Path
from typing import Optional

from ..config import PRESETS, SimulationConfig, get_preset
from ..utils.logger import get_logger

# Import subcommands
from .convert_transcript import convert_transcript

logger = get_logger(__name__)


def list_presets() -> None:
    """List available configuration presets."""
    # Use print for CLI output (user-facing, not logging)
    print("Available configuration presets:\n")
    for name, config in PRESETS.items():
        print(
            f"  {name:12} - {config.num_agents:3} agents, {config.num_epochs:3} epochs"
        )
    print("\nUsage: agisa-sac run --preset <name>")


def run_simulation(args: argparse.Namespace) -> int:
    """Run a simulation with the specified configuration."""
    # Load configuration
    config: Optional[SimulationConfig] = None

    if args.config:
        # Load from JSON file
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            return 1

        try:
            with open(config_path) as f:
                config_dict = json.load(f)
            config = SimulationConfig.from_dict(config_dict)
            logger.info(f"Loaded configuration from: {config_path}")
            print(f"Loaded configuration from: {config_path}")
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1

    elif args.preset:
        # Load preset
        try:
            config = get_preset(args.preset)
            logger.info(f"Using preset: {args.preset}")
            print(f"Using preset: {args.preset}")
        except KeyError as e:
            logger.error(f"Invalid preset: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        # Use default preset
        config = get_preset("default")
        logger.info("Using default configuration")
        print("Using default configuration")

    # Apply command-line overrides
    if args.gpu:
        config.use_gpu = True
        logger.info("GPU acceleration enabled")
        print("GPU acceleration enabled")

    if args.agents:
        config.num_agents = args.agents
        logger.info(f"Overriding num_agents: {args.agents}")
        print(f"Overriding num_agents: {args.agents}")

    if args.epochs:
        config.num_epochs = args.epochs
        logger.info(f"Overriding num_epochs: {args.epochs}")
        print(f"Overriding num_epochs: {args.epochs}")

    if args.seed is not None:
        config.random_seed = args.seed
        logger.info(f"Using random seed: {args.seed}")
        print(f"Using random seed: {args.seed}")

    if hasattr(args, "log_file") and args.log_file:
        logger.info(f"Logging to file: {args.log_file}")

    # Run simulation
    logger.info(
        f"Starting simulation: {config.num_agents} agents, {config.num_epochs} epochs"
    )
    print(
        f"\nStarting simulation: {config.num_agents} agents, {config.num_epochs} epochs"
    )
    print("-" * 60)

    try:
        # Lazy import to avoid loading heavy ML dependencies for --help/list-presets
        from ..core.orchestrator import SimulationOrchestrator

        orchestrator = SimulationOrchestrator(config.to_dict())
        orchestrator.run_simulation()

        logger.info("Simulation completed successfully")
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETE")
        print("=" * 60)
        print(orchestrator.analyzer.summarize())

        return 0

    except Exception as e:
        logger.error(f"Error during simulation: {e}", exc_info=True)
        print(f"\nError during simulation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def main() -> int:
    """Main CLI entry point."""
    # Import version lazily to avoid loading heavy components
    from .. import __version__

    parser = argparse.ArgumentParser(
        prog="agisa-sac",
        description="AGI Stand Alone Complex - Multi-agent system simulation",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
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
    run_parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (overrides LOG_LEVEL env var)",
    )
    run_parser.add_argument(
        "--log-file",
        type=str,
        help="Write logs to specified file",
    )
    run_parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Output logs in JSON format (for production)",
    )

    # List presets command
    subparsers.add_parser("list-presets", help="List configuration presets")

    # Convert transcript command
    convert_parser = subparsers.add_parser(
        "convert-transcript",
        help="Convert auditor transcript to AGI-SAC context blob",
    )
    convert_parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input transcript JSON file",
    )
    convert_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output context blob JSON file",
    )
    convert_parser.add_argument(
        "--name",
        type=str,
        help="Optional artifact name (default: auto-generated slug)",
    )
    convert_parser.add_argument(
        "--marker",
        type=str,
        help="Optional marker string (default: ARTIFACT::<name>)",
    )
    convert_parser.add_argument(
        "--target-epoch",
        type=int,
        default=0,
        help="Target epoch for injection (default: 0)",
    )
    convert_parser.add_argument(
        "--exposure-rate",
        type=float,
        default=0.15,
        help="Fraction of agents to expose (default: 0.15)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Configure logging based on arguments
    if args.command == "run":
        log_level = None
        if hasattr(args, "log_level") and args.log_level:
            log_level = getattr(logging, args.log_level)
        elif hasattr(args, "verbose") and args.verbose:
            log_level = logging.DEBUG

        log_file = (
            Path(args.log_file) if hasattr(args, "log_file") and args.log_file else None
        )
        json_format = hasattr(args, "json_logs") and args.json_logs
        verbose = hasattr(args, "verbose") and args.verbose

        from ..utils.logger import setup_logging

        setup_logging(
            level=log_level,
            log_file=log_file,
            json_format=json_format,
            verbose=verbose,
        )

        return run_simulation(args)
    elif args.command == "list-presets":
        list_presets()
        return 0
    elif args.command == "convert-transcript":
        return convert_transcript(args)
    else:
        parser.print_help()
        return 1


__all__ = ["main", "convert_transcript", "list_presets", "run_simulation"]


if __name__ == "__main__":
    sys.exit(main())
