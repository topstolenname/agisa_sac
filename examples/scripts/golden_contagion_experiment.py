#!/usr/bin/env python3
"""Golden contagion experiment.

Simulates contagion spread across three network topologies (dense, modular,
sparse) using NetworkX. Writes results to a single JSON artifact.

This script is standalone and does not depend on SimulationOrchestrator.
It uses pure Python + NetworkX for network simulation.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import networkx as nx
except ImportError:
    print("Error: NetworkX is required for this script.", file=sys.stderr)
    print("Install with: pip install networkx", file=sys.stderr)
    sys.exit(1)

from agisa_sac.auditing import load_transcript, transcript_to_artifact


def create_dense_graph(n: int, seed: int) -> nx.Graph:
    """Create a dense graph (high connectivity).

    Args:
        n: Number of nodes
        seed: Random seed

    Returns:
        Dense graph with ~80% edge probability
    """
    return nx.erdos_renyi_graph(n, p=0.8, seed=seed)


def create_modular_graph(n: int, seed: int) -> nx.Graph:
    """Create a modular graph (community structure).

    Args:
        n: Number of nodes
        seed: Random seed

    Returns:
        Modular graph with community structure
    """
    # Create 4 communities with internal density 0.7, inter-community 0.05
    sizes = [n // 4] * 4
    # Adjust for rounding
    while sum(sizes) < n:
        sizes[0] += 1

    probs = [[0.7 if i == j else 0.05 for j in range(4)] for i in range(4)]
    return nx.stochastic_block_model(sizes, probs, seed=seed)


def create_sparse_graph(n: int, seed: int) -> nx.Graph:
    """Create a sparse graph (low connectivity).

    Args:
        n: Number of nodes
        seed: Random seed

    Returns:
        Sparse graph with ~10% edge probability
    """
    return nx.erdos_renyi_graph(n, p=0.1, seed=seed)


def simulate_contagion(
    graph: nx.Graph,
    exposure_rate: float,
    p_transmit: float,
    p_recover: float,
    steps: int,
    seed: int,
) -> Dict[str, Any]:
    """Simulate contagion spread on a graph.

    Args:
        graph: NetworkX graph
        exposure_rate: Initial fraction of infected nodes
        p_transmit: Probability of transmission to neighbor
        p_recover: Probability of recovery per step
        steps: Number of simulation steps
        seed: Random seed

    Returns:
        Simulation results with metrics
    """
    random.seed(seed)
    n = len(graph.nodes())

    # Initialize infected set
    num_initial = max(1, int(n * exposure_rate))
    infected: Set[int] = set(random.sample(list(graph.nodes()), num_initial))
    recovered: Set[int] = set()

    # Track time series
    series = []
    peak_infected = len(infected)
    peak_epoch = 0
    recovery_epoch = None

    for epoch in range(steps):
        num_infected = len(infected)
        num_recovered = len(recovered)
        num_susceptible = n - num_infected - num_recovered

        series.append(
            {
                "epoch": epoch,
                "infected": num_infected,
                "recovered": num_recovered,
                "susceptible": num_susceptible,
            }
        )

        # Track peak
        if num_infected > peak_infected:
            peak_infected = num_infected
            peak_epoch = epoch

        # Check for recovery (no more infected)
        if num_infected == 0 and recovery_epoch is None:
            recovery_epoch = epoch

        # Stop early if no more infected
        if num_infected == 0:
            break

        # Transmission phase
        new_infected = set()
        for node in infected:
            for neighbor in graph.neighbors(node):
                if neighbor not in infected and neighbor not in recovered:
                    if random.random() < p_transmit:
                        new_infected.add(neighbor)

        # Recovery phase
        new_recovered = set()
        for node in infected:
            if random.random() < p_recover:
                new_recovered.add(node)

        # Update state
        infected = (infected | new_infected) - new_recovered
        recovered = recovered | new_recovered

    # Final epoch if not already recorded
    if len(infected) == 0 and recovery_epoch is None:
        recovery_epoch = len(series) - 1

    return {
        "peak": peak_infected,
        "peak_epoch": peak_epoch,
        "recovery_epoch": recovery_epoch,
        "series": series,
    }


def run_golden_experiment(
    transcript_path: Path,
    n: int,
    steps: int,
    exposure_rate: float,
    p_transmit: float,
    p_recover: float,
    seed: int,
) -> Dict[str, Any]:
    """Run the golden contagion experiment.

    Args:
        transcript_path: Path to transcript JSON
        n: Number of nodes per graph
        steps: Number of simulation steps
        exposure_rate: Initial infection rate
        p_transmit: Transmission probability
        p_recover: Recovery probability
        seed: Random seed

    Returns:
        Full experiment results
    """
    # Load transcript and create artifact
    transcript = load_transcript(transcript_path)
    artifact = transcript_to_artifact(transcript)

    # Create topologies
    topologies = {
        "dense": create_dense_graph(n, seed),
        "modular": create_modular_graph(n, seed + 1),
        "sparse": create_sparse_graph(n, seed + 2),
    }

    # Run simulations
    runs = []
    for topology_name, graph in topologies.items():
        print(f"Running simulation on {topology_name} topology...")
        result = simulate_contagion(
            graph, exposure_rate, p_transmit, p_recover, steps, seed
        )
        runs.append(
            {
                "topology": topology_name,
                "peak": result["peak"],
                "peak_epoch": result["peak_epoch"],
                "recovery_epoch": result["recovery_epoch"],
                "series": result["series"],
            }
        )
        print(
            f"  Peak: {result['peak']} at epoch {result['peak_epoch']}, "
            f"Recovery: epoch {result['recovery_epoch']}"
        )

    return {
        "marker": artifact["marker"],
        "artifact_name": artifact["name"],
        "params": {
            "n": n,
            "steps": steps,
            "exposure_rate": exposure_rate,
            "p_transmit": p_transmit,
            "p_recover": p_recover,
            "seed": seed,
        },
        "runs": runs,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Golden contagion experiment across network topologies"
    )
    parser.add_argument(
        "--transcript",
        type=str,
        required=True,
        help="Path to transcript JSON file",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=100,
        help="Number of nodes per graph (default: 100)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=50,
        help="Number of simulation steps (default: 50)",
    )
    parser.add_argument(
        "--exposure-rate",
        type=float,
        default=0.15,
        help="Initial infection rate (default: 0.15)",
    )
    parser.add_argument(
        "--p-transmit",
        type=float,
        default=0.12,
        help="Transmission probability (default: 0.12)",
    )
    parser.add_argument(
        "--p-recover",
        type=float,
        default=0.04,
        help="Recovery probability (default: 0.04)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="examples/results/golden_contagion.json",
        help="Output JSON path (default: examples/results/golden_contagion.json)",
    )

    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    out_path = Path(args.out)

    if not transcript_path.exists():
        print(f"Error: Transcript file not found: {transcript_path}", file=sys.stderr)
        return 1

    print("Starting golden contagion experiment...")
    print(f"Transcript: {transcript_path}")
    print(f"Parameters: n={args.n}, steps={args.steps}, seed={args.seed}")
    print(
        f"Contagion: exposure_rate={args.exposure_rate}, "
        f"p_transmit={args.p_transmit}, p_recover={args.p_recover}"
    )
    print()

    try:
        results = run_golden_experiment(
            transcript_path,
            args.n,
            args.steps,
            args.exposure_rate,
            args.p_transmit,
            args.p_recover,
            args.seed,
        )

        # Write results
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)

        print()
        print(f"Results written to: {out_path}")
        print(f"Artifact: {results['artifact_name']}")
        print(f"Marker: {results['marker']}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
