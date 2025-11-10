"""Entry point for running a simple AGI-SAC simulation."""

import sys
from pathlib import Path

# Ensure src directory on path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from agisa_sac import SimulationOrchestrator  # noqa: E402

if __name__ == "__main__":
    config = {"num_agents": 3, "num_epochs": 2}
    orchestrator = SimulationOrchestrator(config)
    orchestrator.run_simulation()
    print(orchestrator.analyzer.summarize())
