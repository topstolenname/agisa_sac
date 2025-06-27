"""Command line interface for running AGI-SAC simulations on GCP or locally."""
from __future__ import annotations

import argparse
from pathlib import Path
import json

from agisa_sac import SimulationOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AGI-SAC simulation")
    parser.add_argument("config", type=Path, help="Path to JSON config file")
    parser.add_argument("--use-gpu", action="store_true", help="Enable GPU acceleration")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text())
    config["use_gpu"] = args.use_gpu
    orchestrator = SimulationOrchestrator(config)
    orchestrator.run_simulation()
    print(orchestrator.analyzer.summarize())


if __name__ == "__main__":
    main()
