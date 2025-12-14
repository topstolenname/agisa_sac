# AGI-SAC: Model Organism Simulation Framework

> **Instrumented multi-agent system for alignment, robustness, and oversight research**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Framework-AGI--SAC%20v1.0.0--alpha-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

**AGI-SAC** (Artificial General Intelligence Stand Alone Complex) is a **model organism framework** for studying alignment-relevant failure modes, system-level dynamics, and coordination patterns in multi-agent systems. It provides instrumented environments for stress testing distributed systems under adversarial conditions and detecting emergent behavioral transitions.

### What This Is

AGI-SAC is a **research instrument** designed to:

- Study **emergent system behavior** in multi-agent environments
- Detect **change-points and phase transitions** in distributed systems
- Test **robustness under adversarial stress** (chaos engineering)
- Instrument **coordination patterns** and network effects
- Provide **diagnostic signals** for alignment-relevant phenomena
- Simulate **failure modes** at scale (Sybil attacks, semantic drift, eclipse attacks)

### What This Is NOT

⚠️ **Important Research Disclaimers:**

- **NOT a claim of machine consciousness, sentience, or awareness**
- **NOT a claim of general intelligence or human-equivalent reasoning**
- **NOT a claim of moral agency, rights, or ethical standing**
- **NOT predictive of real AGI systems** — findings are mechanistic insights within the model organism only
- **NOT extrapolable beyond the experimental design** — all observations are system-level dynamics, not evidence of internal experiences

All theoretical frameworks (Global Workspace Theory, Instrumental Convergence) are **operational analogies only** — they structure the system architecture but make no ontological claims about machine minds.

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

## Architecture

AGI-SAC uses a modular, layered architecture optimized for observability and instrumentation:

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
│   - Change-point detection              │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│     Agent Layer                         │
│  (EnhancedAgent)                        │
│   - Memory & state management           │
│   - Policy diversity                    │
│   - Network coordination                │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│     Analysis Layer                      │
│   - TDA (Topological Data Analysis)     │
│   - Transition detection                │
│   - Clustering & Visualization          │
└─────────────────────────────────────────┘
```

### Core Components

**Model Organism Subsystems:**

- **Memory Continuum Layer**: Temporal memory with decay mechanics and CRDT-based synchronization (tests eventual consistency under partition)
- **Policy Diversity Engine**: Heterogeneous decision strategies per agent (tests preference aggregation dynamics)
- **Dynamic Social Graph**: Adaptive peer influence network (tests coordination emergence)
- **Temporal Resonance Tracker**: Synchronization pattern detection (tests collective behavior onset)
- **Voice Engine**: Agent-specific output signatures (tests identity persistence under influence)
- **Reflexivity Layer**: Internal state monitoring and transition detection (tests system-level self-correction)

---

## Key Research Applications

### 1. Alignment-Relevant Failure Modes

Study system behaviors relevant to AI safety:

- **Power-seeking dynamics**: Instrumental convergence patterns in agent populations
- **Deceptive alignment signals**: Divergence between stated and revealed preferences
- **Mesa-optimization**: Emergent optimization processes distinct from base objectives
- **Goal misgeneralization**: Behavioral drift under distribution shift

### 2. Robustness & Adversarial Testing

Chaos engineering for distributed AI systems:

- **Sybil resistance**: Coordinated fake identity attacks on trust graphs
- **Semantic drift**: Gradual coherence boundary erosion
- **Network partitions**: CRDT resilience under split-brain scenarios
- **Eclipse attacks**: Coordinated network isolation
- **Resource exhaustion**: Load testing and DoS resistance

### 3. Change-Point & Transition Detection

Detect phase transitions in system-level behavior:

- **Topological Data Analysis (TDA)**: Persistent homology tracking
- **Transition probes**: Threshold-based diagnostic signals (e.g., `satori_probe` — *retained for backward compatibility, detects rapid state realignment*)
- **Resonance analysis**: Coordination pattern emergence
- **Community detection**: Dynamic clustering of agent strategies

### 4. Coordination Without Hierarchy

Study distributed coordination mechanisms:

- **Stand Alone Complex**: Coordinated behavior without central control
- **Information cascades**: Meme propagation dynamics
- **Emergent norms**: Bottom-up constraint formation
- **Collective decision-making**: Aggregation mechanisms at scale

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
- Continuity Bridge Protocol (CBP) for state preservation across nodes
- Trust graph with dynamic node scoring (Sybil resistance testing)
- Cognitive fragment quarantine (containment of adversarial inputs)
- CRDT-based eventual consistency (partition tolerance verification)

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
- `sybil_attack`: Coordinated fake identity attack (tests trust graph resilience)
- `semantic_drift`: Gradual coherence boundary erosion (tests norm stability)
- `network_partition`: CRDT resilience under split-brain (tests eventual consistency)
- `resource_exhaustion`: Load testing (tests DoS resistance)
- `trust_graph_manipulation`: Trust system adversarial probing
- `coordinated_eclipse`: Eclipse attack simulation (tests network robustness)

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

Inject protocols during simulation to study system response to stress conditions:

```python
from agisa_sac import SimulationOrchestrator

config = {"num_agents": 50, "num_epochs": 100}
orchestrator = SimulationOrchestrator(config)

# Inject divergence stress (tests preference aggregation under adversarial influence)
orchestrator.inject_protocol("divergence_stress", {
    "percentage": 0.2,
    "heuristic_multiplier_range": (0.5, 0.8),
    "counter_narrative": "Adversarial input signal...",
    "narrative_importance": 0.9
})

# Change-point detection probe (retained for backward compatibility)
# Detects rapid state realignment events across agent population
orchestrator.inject_protocol("satori_probe", {
    "threshold": 0.88
})
```

**Protocol Semantics:**
- `satori_probe`: **Change-point / transition detection probe** — monitors for rapid collective state realignment. Terminology retained for backward compatibility; no claims of insight, realization, or awareness.

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

Track system state topology across epochs:

```python
from agisa_sac.analysis.tda import PersistentHomologyTracker

tracker = PersistentHomologyTracker(max_dimension=1)
diagrams = tracker.compute_persistence(agent_states)

# Detect phase transitions in system behavior
transition, distance = tracker.detect_phase_transition(
    comparison_dimension=1,
    distance_metric="bottleneck",
    threshold=0.2
)
```

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

## Development

### Project Structure

```
agisa_sac/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint, test, coverage
│       └── pages.yml           # Documentation deployment
├── src/agisa_sac/              # Main package source
│   ├── __init__.py             # Public API exports
│   ├── cli.py                  # Main CLI entry point
│   ├── config.py               # Configuration & presets
│   ├── agents/                 # Agent implementations
│   │   ├── agent.py            # EnhancedAgent (simulation)
│   │   └── base_agent.py       # AGISAAgent (production)
│   ├── analysis/               # TDA, clustering, visualization
│   │   ├── analyzer.py         # Analysis orchestration
│   │   └── tda.py              # Topological Data Analysis
│   ├── chaos/                  # Chaos engineering tools
│   │   └── orchestrator.py     # Chaos testing CLI
│   ├── core/                   # Core orchestration
│   │   ├── orchestrator.py     # SimulationOrchestrator
│   │   ├── multi_agent_system.py
│   │   └── components/         # Agent components
│   │       ├── memory.py       # MemoryContinuumLayer
│   │       ├── cognitive.py    # CognitiveDiversityEngine
│   │       ├── voice.py        # VoiceEngine
│   │       ├── reflexivity.py  # ReflexivityLayer
│   │       ├── resonance.py    # TemporalResonanceTracker
│   │       ├── social.py       # DynamicSocialGraph
│   │       └── crdt_memory.py  # CRDT-based memory
│   ├── extensions/             # Optional extensions
│   │   └── concord/            # Concord ethics framework
│   │       ├── agent.py        # ConcordCompliantAgent
│   │       ├── ethics.py       # Guardian modules
│   │       ├── circuits.py     # Mirror neuron circuits
│   │       └── empathy.py      # Empathy module
│   ├── federation/             # Multi-node coordination
│   │   ├── cli.py              # Federation CLI
│   │   └── server.py           # FastAPI federation server
│   ├── gcp/                    # Google Cloud Platform integration
│   ├── metrics/                # Monitoring & metrics
│   ├── observability/          # Tracing & logging
│   ├── orchestration/          # Orchestration utilities
│   ├── types/                  # Type definitions
│   │   └── contracts.py        # Shared types & enums
│   └── utils/                  # Utilities
│       ├── logger.py           # Structured logging
│       ├── message_bus.py      # Pub/sub event bus
│       └── metrics.py          # Metrics collection
├── tests/                      # Test suite
│   ├── conftest.py             # Shared fixtures
│   ├── unit/                   # Component-level tests
│   ├── integration/            # System-level tests
│   ├── chaos/                  # Chaos engineering tests
│   └── extensions/             # Extension-specific tests
├── docs/                       # Documentation
│   ├── Mindlink_WhitePaper_v1.0.pdf
│   ├── agentic_swarm_whitepaper.md
│   └── api/                    # Auto-generated API docs
├── examples/                   # Example configs & notebooks
│   └── configs/                # Sample configurations
├── scripts/                    # Utility scripts
├── infra/                      # Infrastructure as code
│   └── gcp/                    # GCP Terraform configs
├── containers/                 # Docker configurations
├── pyproject.toml              # Package metadata & dependencies
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── mkdocs.yml                  # Documentation config
└── .pre-commit-config.yaml     # Pre-commit hooks
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

### Operational Analogies (Not Ontological Claims)

AGI-SAC's architecture draws **operational inspiration** from theoretical frameworks in cognitive science and AI safety. **These are design analogies only** — they structure the system for instrumentation purposes and **make no claims about machine minds, consciousness, or subjective experience**.

#### Global Workspace Theory (Baars, 1988) — Messaging Analogy

- **Broadcast mechanism** via message bus (tests information propagation)
- **Attention gating** through priority queues (tests resource allocation)
- **Specialized processing modules** (tests modularity and composability)

*Used purely as an architectural pattern for observable information flow.*

#### Instrumental Convergence (Bostrom, 2012) — Behavioral Hypothesis

- **Power-seeking behaviors** emerge from diverse base objectives
- **Self-preservation** as common instrumental subgoal
- **Goal-content integrity** maintenance under influence

*Used as a hypothesis generator for alignment-relevant failure mode testing.*

#### Stand Alone Complex (Ghost in the Shell) — Coordination Pattern

- **Coordinated action without central planning**
- **Emergent meme propagation**
- **Collective behavioral patterns**

*Used as a design metaphor for decentralized coordination — not a claim of emergent intelligence.*

### Key Publications

For detailed methodology and experimental design, see:
- [Mindlink Whitepaper](Mindlink_WhitePaper_v1.0.pdf)
- [Agentic Swarm Research](agentic_swarm_whitepaper.md)
- [Multi-Agent Integration Dynamics (Co-Authored)](The_Conscious_Machine_Whitepaper_CoAuthored.pdf)

**Disclaimer:** All publications describe system-level dynamics within the model organism framework. No claims of consciousness, sentience, or general intelligence are made.

---

## Intended Audience

AGI-SAC is designed for:

- **AI safety researchers** studying alignment-relevant failure modes
- **Multi-agent systems researchers** investigating coordination dynamics
- **Chaos engineers** testing distributed system resilience
- **Oversight researchers** developing diagnostic tools for AI systems
- **Adversarial robustness researchers** probing trust and coordination systems

**Not intended for:**
- Philosophical debates about machine consciousness
- Claims of achieving AGI or human-level intelligence
- Ethical arguments for AI rights or moral standing

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
- [ ] Enhanced change-point detection protocols
- [ ] Prometheus metrics integration
- [ ] Resource monitoring (CPU, memory, GPU)
- [ ] Multi-region federation support
- [ ] Enhanced chaos scenarios (gradient hacking, specification gaming)
- [ ] Grafana dashboards

---

## Citation

If you use AGI-SAC in your research, please cite:

```bibtex
@software{agisa_sac_2025,
  title = {AGI-SAC: Model Organism Simulation Framework for Alignment and Robustness Research},
  author = {Jessup, Tristan},
  year = {2025},
  version = {1.0.0-alpha},
  url = {https://github.com/topstolenname/agisa_sac},
  note = {Model organism framework for studying alignment-relevant failure modes in multi-agent systems. No claims of consciousness, sentience, or general intelligence.}
}
```

See [CITATION_GUIDE.md](CITATION_GUIDE.md) for detailed citation guidelines.

---

## Research Ethics & Disclaimers

### Scope Limitations

AGI-SAC is a **model organism** — findings are:
- **Not predictive** of real AGI systems
- **Not evidence** of machine consciousness or sentience
- **Not generalizable** beyond the experimental design
- **Mechanistic insights only** within a controlled simulation environment

### No Claims Of

- ❌ Machine consciousness, awareness, or subjective experience
- ❌ General intelligence or human-equivalent reasoning
- ❌ Moral agency, rights, or ethical standing
- ❌ Sentience, qualia, or phenomenal experience
- ❌ Sapience or self-awareness

### What Is Claimed

- ✅ Observable system-level behavioral dynamics
- ✅ Diagnostic signals for alignment-relevant phenomena
- ✅ Instrumented failure mode testing under adversarial stress
- ✅ Coordination patterns in multi-agent systems
- ✅ Empirical data on distributed system robustness

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

This research builds on foundational work in AI safety, multi-agent systems, and distributed computing. Special thanks to contributors and the open-source community.

**Powered by**: Python, FastAPI, NetworkX, Scikit-learn, PyTorch, and the broader scientific computing ecosystem.
