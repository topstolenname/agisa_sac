#!/usr/bin/env python3
"""
Simple simulation runner for testing.

Usage: python sim_runner.py <config_file>
"""

import json
import sys
from pathlib import Path

# Ensure we can import from src
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agisa_sac.core.orchestrator import SimulationOrchestrator


def main():
    """Run a simple simulation with the given config."""
    if len(sys.argv) < 2:
        print("Usage: python sim_runner.py <config_file>", file=sys.stderr)
        sys.exit(1)

    config_file = Path(sys.argv[1])
    if not config_file.exists():
        print(f"Config file not found: {config_file}", file=sys.stderr)
        sys.exit(1)

    # Load config
    with open(config_file, "r") as f:
        config = json.load(f)

    # Create orchestrator
    orchestrator = SimulationOrchestrator(config=config)

    # Run simulation
    results = orchestrator.run_simulation()

    # Print summary as last line
    summary = {
        "num_agents": results.get("num_agents", 0),
        "num_epochs": results.get("num_epochs", 0),
        "final_satori_count": len(results.get("satori_events", [])),
        "simulation_completed": True,
    }
    print(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
