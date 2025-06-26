import sys
from pathlib import Path

# Ensure the package is importable when running from repo root
sys.path.append(str(Path(__file__).resolve().parent / 'src'))

from agisa_sac import SimulationOrchestrator


def main():
    config = {
        'num_agents': 5,
        'num_epochs': 3,
        'random_seed': 42,
    }

    orchestrator = SimulationOrchestrator(config)
    orchestrator.run_simulation()

    summary = orchestrator.get_summary_metrics()
    print("Summary metrics:\n", summary)


if __name__ == '__main__':
    main()
