"""
FastAPI Prometheus Exporter for Concord-Compliant Agent Swarm.

Exports key metrics:
- Φ (phi) integration: GWT consciousness measure
- β₀ (beta0): Topological connected components (TDA)
- β₁ (beta1): Topological loops (TDA)
- Coexistence score: Harmony index
- CMNI mean: Mean Conscious Mirror Neuron Integration across swarm

Endpoints:
- GET /metrics: Prometheus metrics exposition
- POST /tick: Simulate agent interaction step (for testing)
- GET /health: Health check
"""

import random
import time
from typing import Dict, List

from fastapi import FastAPI
from prometheus_client import Gauge, make_asgi_app
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="AGISA-SAC Concord Exporter", version="1.0.0")

# Prometheus metrics
phi_integration_gauge = Gauge(
    "agisa_phi_integration",
    "Integrated information (Φ) - GWT consciousness measure",
    ["agent_id"],
)
beta0_components_gauge = Gauge(
    "agisa_beta0_components",
    "Connected components (β₀) - TDA topology measure",
)
beta1_loops_gauge = Gauge(
    "agisa_beta1_loops",
    "Feedback loops (β₁) - TDA topology measure",
)
coexistence_score_gauge = Gauge(
    "agisa_coexistence_score",
    "Harmony index - mutual resonance measure",
)
cmni_mean_gauge = Gauge(
    "agisa_cmni_mean",
    "Mean CMNI across agent swarm",
)
agent_count_gauge = Gauge(
    "agisa_agent_count",
    "Total number of active agents",
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Simulated agent swarm state
class SwarmState:
    """Maintains simulated swarm state for demo purposes."""

    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.topology = {"beta0": 1, "beta1": 0}
        self._initialize_agents(3)

    def _initialize_agents(self, count: int):
        for i in range(count):
            agent_id = f"agent-{i}"
            self.agents[agent_id] = {
                "phi": 0.15 + random.uniform(0, 0.1),
                "cmni": 0.3 + random.uniform(0, 0.2),
                "resource_level": 0.8,
                "emotional_valence": random.uniform(-0.2, 0.3),
            }

    def tick(self):
        """Simulate one interaction cycle."""
        # Update agent states
        for agent_id, state in self.agents.items():
            # Random walk for phi and cmni
            state["phi"] += random.uniform(-0.02, 0.03)
            state["phi"] = max(0.05, min(state["phi"], 0.5))

            state["cmni"] += random.uniform(-0.05, 0.06)
            state["cmni"] = max(0.0, min(state["cmni"], 1.0))

            state["resource_level"] += random.uniform(-0.05, 0.05)
            state["resource_level"] = max(0.3, min(state["resource_level"], 1.0))

            state["emotional_valence"] += random.uniform(-0.1, 0.1)
            state["emotional_valence"] = max(-1.0, min(state["emotional_valence"], 1.0))

        # Update topology based on agent count and connectivity
        agent_count = len(self.agents)
        self.topology["beta0"] = max(1, agent_count - random.randint(0, 2))
        self.topology["beta1"] = random.randint(
            0, max(0, agent_count - 2)
        )  # Loops emerge with more agents

    def get_coexistence_score(self) -> float:
        """Compute harmony index (simplified)."""
        if len(self.agents) < 2:
            return 0.5

        # Average emotional alignment
        valences = [a["emotional_valence"] for a in self.agents.values()]
        variance = sum((v - sum(valences) / len(valences)) ** 2 for v in valences) / len(valences)
        # Low variance = high alignment
        alignment = 1.0 / (1.0 + variance)

        # Factor in mean CMNI
        mean_cmni = sum(a["cmni"] for a in self.agents.values()) / len(self.agents)

        return (alignment * 0.6 + mean_cmni * 0.4)

    def export_metrics(self):
        """Export current state to Prometheus gauges."""
        # Per-agent phi
        for agent_id, state in self.agents.items():
            phi_integration_gauge.labels(agent_id=agent_id).set(state["phi"])

        # Topology
        beta0_components_gauge.set(self.topology["beta0"])
        beta1_loops_gauge.set(self.topology["beta1"])

        # Swarm-level metrics
        mean_cmni = sum(a["cmni"] for a in self.agents.values()) / len(self.agents)
        cmni_mean_gauge.set(mean_cmni)

        coexistence = self.get_coexistence_score()
        coexistence_score_gauge.set(coexistence)

        agent_count_gauge.set(len(self.agents))


# Global swarm state
swarm_state = SwarmState()


# API Models
class TickResponse(BaseModel):
    """Response from /tick endpoint."""

    timestamp: float
    agent_count: int
    mean_phi: float
    mean_cmni: float
    beta0: int
    beta1: int
    coexistence_score: float


# Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agisa-sac-exporter"}


@app.post("/tick", response_model=TickResponse)
def tick():
    """
    Simulate one agent interaction cycle and update metrics.

    This endpoint is useful for testing and demo purposes.
    In production, metrics would be updated by actual agent interactions.
    """
    swarm_state.tick()
    swarm_state.export_metrics()

    mean_phi = sum(a["phi"] for a in swarm_state.agents.values()) / len(swarm_state.agents)
    mean_cmni = sum(a["cmni"] for a in swarm_state.agents.values()) / len(swarm_state.agents)

    return TickResponse(
        timestamp=time.time(),
        agent_count=len(swarm_state.agents),
        mean_phi=mean_phi,
        mean_cmni=mean_cmni,
        beta0=swarm_state.topology["beta0"],
        beta1=swarm_state.topology["beta1"],
        coexistence_score=swarm_state.get_coexistence_score(),
    )


@app.on_event("startup")
async def startup_event():
    """Initialize metrics on startup."""
    swarm_state.export_metrics()


# For local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
