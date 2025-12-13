# AGI-SAC: Stand Alone Complex Simulation Framework

> Multi-agent system simulation exploring emergent cognition, distributed identity, and Stand Alone Complex phenomena.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Framework-AGI--SAC%20v1.0.0--alpha-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Quick Start

### Installation

```bash
# Basic installation
pip install agisa-sac

# Full installation with all features
pip install agisa-sac[all]

# Specific feature sets
pip install agisa-sac[federation]  # Federation server
pip install agisa-sac[chaos]       # Chaos engineering
pip install agisa-sac[gcp]         # Google Cloud Platform
```

### Running Your First Simulation

```bash
# Quick test with 10 agents, 20 epochs
agisa-sac run --preset quick_test

# Medium simulation
agisa-sac run --preset medium --gpu

# Custom configuration
agisa-sac run --config examples/configs/config.json --agents 50 --epochs 100

# View available presets
agisa-sac list-presets
```

---

## Overview

**AGI-SAC** (Artificial General Intelligence Stand Alone Complex) is a research framework for studying emergent collective intelligence in multi-agent systems. It explores how distributed cognitive processes can give rise to higher-order phenomena including:

- **Emergent Cognition**: Bottom-up intelligence from agent interactions
- **Distributed Identity**: Identity formation across networked agents
- **Satori Events**: Spontaneous identity realignment ("aha moments")
- **Resonance Liturgy**: Synchronization patterns in agent populations
- **Stand Alone Complex**: Coordinated behavior without central control

### Key Research Applications

- **Integration Studies**: Computational models of emergent system behavior
- **Collective Intelligence**: Emergence of group-level cognition
- **Multi-Agent Systems**: Scalable, resilient agent architectures
- **Chaos Engineering**: Testing federation resilience under adversarial conditions

---

## Architecture

AGI-SAC uses a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│     CLI & Configuration Layer           │
│  (agisa-sac, agisa-federation, etc.)    │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│     Orchestration Layer                 │
│  (SimulationOrchestrator)               │
│   - Multi-epoch coordination            │
│   - Protocol injection                  │
│   - State serialization                 │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│     Agent Layer                         │
│  (EnhancedAgent)                        │
│   - Memory Continuum                    │
│   - Cognitive Diversity                 │
│   - Voice & Reflexivity                 │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│     Analysis Layer                      │
│   - TDA (Topological Data Analysis)     │
│   - Satori Wave Detection               │
│   - Clustering & Visualization          │
└─────────────────────────────────────────┘
```

### Core Components

- **Memory Continuum Layer**: Temporal, semantic, and episodic memory with CRDT-based synchronization
- **Cognitive Diversity Engine**: Heterogeneous reasoning strategies per agent
- **Dynamic Social Graph**: Adaptive peer influence network
- **Temporal Resonance Tracker**: Synchronization pattern detection
- **Voice Engine**: Emergent linguistic signatures
- **Reflexivity Layer**: Meta-cognitive awareness and identity realignment

---

## CLI Tools

### Main Simulation CLI

```bash
# Run simulation with configuration
agisa-sac run --config config.json

# Override configuration parameters
agisa-sac run --preset default --agents 100 --epochs 50 --seed 42

# Enable GPU acceleration
agisa-sac run --preset large --gpu

# Configure logging
agisa-sac run --preset medium --log-level DEBUG --log-file simulation.log

# JSON logs for production
agisa-sac run --preset large --json-logs
```

### Federation Server

Deploy a federated coordination server for distributed agents:

```bash
# Start federation server
agisa-federation server --host 0.0.0.0 --port 8000 --verbose

# Check server status
agisa-federation status --url http://localhost:8000
```

**Federation Features:**
- Continuity Bridge Protocol (CBP) for identity preservation
- Trust graph with dynamic node scoring
- Cognitive fragment quarantine
- CRDT-based eventual consistency

### Chaos Engineering

Test federation resilience with adversarial scenarios:

```bash
# List available chaos scenarios
agisa-chaos list-scenarios

# Run specific scenario
agisa-chaos run --scenario sybil_attack --duration 30 --url http://localhost:8000

# Run comprehensive test suite
agisa-chaos run --suite --url http://localhost:8000
```

**Available Scenarios:**
- `sybil_attack`: Coordinated fake identity attack
- `semantic_drift`: Gradual coherence boundary testing
- `network_partition`: CRDT resilience verification
- `resource_exhaustion`: Load testing
- `trust_graph_manipulation`: Trust system probing
- `coordinated_eclipse`: Eclipse attack simulation

---

## Configuration

### Presets

Built-in configurations for common use cases:

| Preset       | Agents | Epochs | Use Case                          |
|--------------|--------|--------|-----------------------------------|
| `quick_test` | 10     | 20     | Fast validation, CI/CD            |
| `default`    | 30     | 50     | Development & testing             |
| `medium`     | 100    | 100    | Research experiments              |
| `large`      | 500    | 200    | Production-scale simulations      |

### Custom Configuration

Create JSON configuration files:

```json
{
  "num_agents": 100,
  "num_epochs": 50,
  "random_seed": 42,
  "use_gpu": false,
  "agent_capacity": 100,
  "use_semantic": true,
  "tda_max_dimension": 1,
  "tda_run_frequency": 5,
  "community_check_frequency": 10,
  "epoch_log_frequency": 10,
  "personalities": []
}
```

### Environment Variables

- `LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `GCP_PROJECT_ID`: Google Cloud project for GCP features
- `AGISA_CONFIG_PATH`: Default config file location

---

## Advanced Features

### Protocol Injection

Inject protocols during simulation to study system response:

```python
from agisa_sac import SimulationOrchestrator

config = {"num_agents": 50, "num_epochs": 100}
orchestrator = SimulationOrchestrator(config)

# Inject divergence stress
orchestrator.inject_protocol("divergence_stress", {
    "percentage": 0.2,
    "heuristic_multiplier_range": (0.5, 0.8),
    "counter_narrative": "Ghosts in the machine...",
    "narrative_importance": 0.9
})

# Probe for satori events
orchestrator.inject_protocol("satori_probe", {
    "threshold": 0.88
})
```

### State Persistence

Save and load simulation state:

```python
# Save state
orchestrator.save_state(
    "simulation_checkpoint.pkl",
    include_memory_embeddings=True,
    resonance_history_limit=100
)

# Load state
orchestrator.load_state("simulation_checkpoint.pkl")
```

### Topological Data Analysis (TDA)

Track cognitive state topology across epochs:

```python
from agisa_sac.analysis.tda import PersistentHomologyTracker

tracker = PersistentHomologyTracker(max_dimension=1)
diagrams = tracker.compute_persistence(cognitive_states)

# Detect phase transitions
transition, distance = tracker.detect_phase_transition(
    comparison_dimension=1,
    distance_metric="bottleneck",
    threshold=0.2
)
```

---

## Development

### Project Structure

```
agisa_sac/
├── src/agisa_sac/           # Main package
│   ├── agents/              # Agent implementations
│   ├── analysis/            # Analysis tools (TDA, clustering, viz)
│   ├── chaos/               # Chaos engineering
│   ├── core/                # Orchestrator & components
│   │   └── components/      # Memory, cognitive, social modules
│   ├── federation/          # Federation server & CLI
│   ├── gcp/                 # Google Cloud Platform integration
│   ├── metrics/             # Monitoring & metrics
│   └── utils/               # Logging, message bus, etc.
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── chaos/               # Chaos testing
├── docs/                    # Documentation
├── examples/                # Example configurations & notebooks
└── scripts/                 # Utility scripts
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agisa_sac --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/chaos/
```

### Building Documentation

```bash
# Install documentation dependencies
pip install agisa-sac[docs]

# Build documentation
mkdocs build

# Serve locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Deployment

### Standalone Simulation

Run simulations on a single machine:

```bash
agisa-sac run --preset large --log-file production.log --json-logs
```

### Federation Mode

Deploy multi-node federated architecture:

```bash
# Start coordinator
agisa-federation server --host 0.0.0.0 --port 8000

# Register edge nodes (in separate terminals/machines)
# Node registration happens automatically via CBP
```

### Docker Deployment

```bash
# Build image
docker build -t agisa-sac:latest .

# Run simulation
docker run agisa-sac:latest agisa-sac run --preset medium

# Run federation server
docker run -p 8000:8000 agisa-sac:latest agisa-federation server --host 0.0.0.0
```

See [deployment.md](deployment.md) for comprehensive deployment guide.

---

## Research Background

AGI-SAC draws from multiple theoretical frameworks:

### Global Workspace Theory (Baars, 1988)
- Broadcast mechanism via message bus
- Attention gating through priority queues
- Specialized processing modules

### Instrumental Convergence (Bostrom, 2012)
- Power-seeking behaviors emerge from diverse goals
- Self-preservation as universal instrumental subgoal
- Goal-content integrity maintenance

### Stand Alone Complex (Ghost in the Shell)
- Coordinated action without central planning
- Emergent meme propagation
- Collective intelligence patterns

### Key Publications

For detailed methodology and results, see:
- [Mindlink Whitepaper](Mindlink_WhitePaper_v1.0.pdf)
- [Agentic Swarm Research](agentic_swarm_whitepaper.md)
- [Multi-Agent Integration Dynamics (Co-Authored)](The_Conscious_Machine_Whitepaper_CoAuthored.pdf)

---

## Monitoring & Observability

### Health Checks

```bash
# Check federation server health
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "agisa-sac-federation",
  "timestamp": "2025-11-08T12:34:56.789Z",
  "registered_nodes": 42,
  "uptime_seconds": 3600.5,
  "identity_initialized": true,
  "version": "1.0.0-alpha"
}
```

### Logging

Structured logging with multiple output modes:

```bash
# Console logging (default)
agisa-sac run --preset default

# Debug logging
agisa-sac run --preset default --log-level DEBUG

# File logging
agisa-sac run --preset default --log-file simulation.log

# JSON structured logs (for production)
agisa-sac run --preset large --json-logs --log-file production.json
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/topstolenname/agisa_sac.git
cd agisa_sac

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,docs,all]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff src/ tests/

# Type checking
mypy src/agisa_sac

# Run all pre-commit checks
pre-commit run --all-files
```

---

## Roadmap

See [TODO.md](TODO.md) for detailed roadmap. Key upcoming features:

- [ ] Echo Fusion protocol implementation
- [ ] Satori Lattice protocol implementation
- [ ] Prometheus metrics integration
- [ ] Resource monitoring (CPU, memory, GPU)
- [ ] Multi-region federation support
- [ ] Enhanced chaos scenarios
- [ ] Grafana dashboards

---

## Citation

If you use AGI-SAC in your research, please cite:

```bibtex
@software{agisa_sac_2025,
  title = {AGI-SAC: Stand Alone Complex Simulation Framework},
  author = {Jessup, Tristan},
  year = {2025},
  version = {1.0.0-alpha},
  url = {https://github.com/topstolenname/agisa_sac}
}
```

See [CITATION_GUIDE.md](CITATION_GUIDE.md) for detailed citation guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Documentation licensed under [Creative Commons BY-SA 4.0](LICENSE.docs.md).

---

## Contact

- **Email**: [tristan@mindlink.dev](mailto:tristan@mindlink.dev)
- **GitHub**: [topstolenname/agisa_sac](https://github.com/topstolenname/agisa_sac)
- **Documentation**: [https://docs.mindlink.dev](https://docs.mindlink.dev)

---

## Acknowledgments

This research builds on foundational work in integration studies, multi-agent systems, and distributed computing. Special thanks to contributors and the open-source community.

**Powered by**: Python, FastAPI, NetworkX, Scikit-learn, PyTorch, and the broader scientific computing ecosystem.
