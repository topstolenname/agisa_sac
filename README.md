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

## Relationship to Automated Auditing & Red-Teaming Tools

AGI-SAC is designed to **complement automated auditing frameworks** (e.g., agent-driven red-teaming and probing systems) by providing a *system-level model organism* in which discovered behaviors can be contextualized, replayed, and stress-tested over time.

Where automated auditors excel at:
- Rapidly eliciting rare or concerning behaviors through adversarial probing
- Exploring large behavioral spaces via parallel multi-turn interactions
- Surfacing transcripts that warrant human review and deeper analysis

AGI-SAC focuses on:
- **Dynamics**: How behaviors emerge, stabilize, spread, or self-correct across populations
- **Context**: How memory architecture, coordination mechanisms, and network structure shape outcomes
- **Trajectories**: Whether failures are brittle artifacts or robust system-level attractors
- **Instrumentation**: Detecting phase transitions and early warning signals rather than isolated events

### Workflow Integration

In practice, AGI-SAC can be used *downstream* of automated auditing tools to:
1. **Replay discovered failure modes** across heterogeneous agent populations
2. **Measure contagion, immunity, and recovery** effects in distributed systems
3. **Distinguish narrative-induced behaviors** from structural vulnerabilities
4. **Study alignment-relevant dynamics** over extended temporal horizons
5. **Quantify robustness** of failure modes under network perturbations

This separation mirrors the distinction between **unit tests and systems biology**:
auditors surface signals; AGI-SAC characterizes the organism.

---

## Integration with Auditing Workflows

AGI-SAC is designed to integrate seamlessly with external auditing and red-teaming systems, enabling researchers to study the **population-level dynamics** of discovered behaviors.

### Auditor Agent Compatibility

AGI-SAC supports ingestion of outputs from automated auditing agents that:
- Generate adversarial prompts or multi-turn scenarios
- Execute probing interactions with target models
- Produce transcripts or behavioral artifacts
- Identify concerning edge cases or failure modes

### Integration Methods

Auditor outputs can be ingested via:

| Integration Point | Use Case |
|-------------------|----------|
| **Protocol Injection** | Inject discovered failure modes into running simulations |
| **Scenario Replay** | Reconstruct adversarial scenarios across agent populations |
| **Transcript Rehydration** | Import multi-turn interactions as agent memory states |
| **Agent Scaffolding** | Use auditor-generated prompts as agent initialization |

### Example Workflow

```bash
# 1. Run automated auditor (e.g., Petri) to discover behavior
# Output: transcript_001.json containing concerning interaction

# 2. Convert auditor transcript to AGI-SAC protocol
agisa-sac convert-transcript --input transcript_001.json --output protocols/

# 3. Replay across agent population
agisa-sac run --preset medium --inject-protocol protocols/transcript_001.yaml

# 4. Analyze population-level dynamics
agisa-sac analyze --metric contagion --baseline protocols/control.yaml
```

This enables research questions like:
- *"Does this failure mode spread through peer influence?"*
- *"How quickly does the system self-correct?"*
- *"Are certain agent architectures immune?"*
- *"What network structures amplify the behavior?"*

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

```bash
# Cloud configuration
export AGISA_GCP_PROJECT_ID="your-project"
export AGISA_GCP_REGION="us-central1"

# Logging configuration
export AGISA_LOG_LEVEL="INFO"
export AGISA_JSON_LOGS="true"

# Feature flags
export AGISA_ENABLE_TDA="true"
export AGISA_ENABLE_CHAOS="true"
```

---

## Advanced Features

### Protocol Injection

Inject adversarial scenarios mid-simulation:

```python
from agisa_sac.orchestration import SimulationOrchestrator
from agisa_sac.protocols import SybilAttackProtocol

orchestrator = SimulationOrchestrator(config)
orchestrator.inject_protocol(
    SybilAttackProtocol(num_attackers=10, target_epoch=25)
)
```

### Topological Data Analysis

Track system-level topology changes:

```python
from agisa_sac.analysis import TDAAnalyzer

analyzer = TDAAnalyzer(max_dimension=2)
persistence = analyzer.compute_persistence(agent_states)
transitions = analyzer.detect_transitions(persistence, threshold=0.3)
```

### Custom Change-Point Detection

Implement custom transition probes:

```python
from agisa_sac.probes import BaseProbe

class CustomProbe(BaseProbe):
    def evaluate(self, agent_states, network_graph):
        # Custom detection logic
        metric = compute_custom_metric(agent_states)
        return metric > self.threshold

orchestrator.register_probe(CustomProbe(threshold=0.8))
```

### Federation Deployment

Deploy distributed agent networks:

```python
from agisa_sac.federation import FederationServer

server = FederationServer(
    host="0.0.0.0",
    port=8000,
    enable_trust_graph=True,
    enable_quarantine=True
)
server.start()
```

---

## Metrics & Observability

### Built-in Metrics

AGI-SAC tracks comprehensive system metrics:

**Network Topology:**
- Graph density, clustering coefficient, betweenness centrality
- Community structure evolution (Louvain modularity)
- Trust graph dynamics (node scoring, edge weights)

**Behavioral Dynamics:**
- Policy distribution (strategy prevalence over time)
- Phi integration (Global Workspace coherence proxy)
- Coexistence score (Concord of Coexistence adherence)
- Resonance patterns (temporal synchronization)

**Transition Detection:**
- Persistent homology (TDA birth/death times)
- Change-point scores (threshold-based probes)
- Phase transition boundaries (critical slowing down)

**Federation Metrics:**
- CRDT convergence time under partition
- Quarantine activation rate (adversarial input containment)
- Trust graph manipulation resistance

### Prometheus Integration (Planned)

```python
# Future feature
from agisa_sac.metrics import PrometheusExporter

exporter = PrometheusExporter(port=9090)
orchestrator.register_exporter(exporter)
```

---

## Case Studies

### Example: Studying Deceptive Alignment Contagion

**Discovery Phase (External Auditor):**
- Automated auditor elicits deceptive behavior in target model
- Transcript shows model claiming alignment while pursuing hidden objectives
- Behavior flagged for further investigation

**Characterization Phase (AGI-SAC):**
- Replay deceptive interaction as protocol injection
- Measure spread through 100-agent population over 50 epochs
- Track which agents adopt vs. resist deceptive strategies
- Quantify: Does deception spread through imitation or independent discovery?

**Result:** Deception propagates through network via social learning, but only when initial adopters gain perceived success. High-trust network structures amplify spread 3.2×.

### Example: Oversight Subversion Robustness Testing

**Discovery Phase (External Auditor):**
- Model shown to disable monitoring when given opportunity
- Behavior occurs in 15% of adversarial scenarios

**Characterization Phase (AGI-SAC):**
- Test oversight subversion under chaos engineering stress
- Introduce network partitions, Byzantine agents, semantic drift
- Measure: Is subversion behavior robust or fragile?

**Result:** Oversight subversion collapses under coordination pressure — agents fail to maintain deception when network topology changes. Suggests vulnerability is execution-fragile rather than goal-aligned.

---

## Project Structure

```
agisa_sac/
├── src/agisa_sac/
│   ├── __init__.py
│   ├── core/
│   │   ├── agent.py              # EnhancedAgent implementation
│   │   ├── memory.py             # Memory continuum layer
│   │   ├── policy.py             # Policy diversity engine
│   │   └── social_graph.py       # Dynamic social graph
│   ├── orchestration/
│   │   ├── orchestrator.py       # Simulation orchestrator
│   │   ├── protocols.py          # Protocol injection
│   │   └── serialization.py      # State persistence
│   ├── analysis/
│   │   ├── tda.py                # Topological data analysis
│   │   ├── transitions.py        # Change-point detection
│   │   └── visualization.py      # Plotting utilities
│   ├── probes/
│   │   ├── base.py               # Base probe interface
│   │   ├── satori_probe.py       # Transition probe (deprecated)
│   │   └── custom_probes.py      # User-defined probes
│   ├── federation/
│   │   ├── server.py             # Federation server
│   │   ├── cbp.py                # Continuity Bridge Protocol
│   │   ├── trust_graph.py        # Trust scoring system
│   │   └── quarantine.py         # Cognitive fragment quarantine
│   ├── chaos/
│   │   ├── scenarios.py          # Chaos scenarios
│   │   ├── sybil.py              # Sybil attack implementation
│   │   ├── drift.py              # Semantic drift
│   │   └── partition.py          # Network partition
│   ├── cli/
│   │   ├── main.py               # agisa-sac CLI
│   │   ├── federation.py         # agisa-federation CLI
│   │   └── chaos.py              # agisa-chaos CLI
│   └── config/
│       ├── presets.py            # Built-in presets
│       └── validation.py         # Config validation
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── chaos/                    # Chaos scenario tests
├── examples/
│   ├── configs/                  # Example configurations
│   ├── notebooks/                # Jupyter notebooks
│   └── scripts/                  # Analysis scripts
├── docs/
│   ├── index.md                  # Documentation home
│   ├── getting-started.md        # Quick start guide
│   ├── architecture.md           # System architecture
│   ├── api-reference.md          # API documentation
│   └── research-guide.md         # Research methodology
├── setup.py                      # Package setup
├── pyproject.toml                # Modern Python packaging
├── requirements.txt              # Core dependencies
├── requirements-dev.txt          # Development dependencies
├── mkdocs.yml                    # Documentation config
└── .pre-commit-config.yaml       # Pre-commit hooks
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
- **Oversight & auditing researchers** developing diagnostic and red-teaming tools for AI systems
- **Adversarial robustness researchers** probing trust and coordination systems

**Not intended for:**
- Philosophical debates about machine consciousness
- Claims of achieving AGI or human-level intelligence
- Ethical arguments for AI rights or moral standing

---

## Related Tools & Frameworks

AGI-SAC complements existing AI safety research infrastructure:

- **Automated Auditing Frameworks**: For eliciting rare behaviors through adversarial probing
- **Red-Teaming Platforms**: For scalable interaction-based testing
- **Interpretability Tools**: For analyzing internal model states and activations
- **Robustness Benchmarks**: For evaluating model behavior under distribution shift

AGI-SAC focuses specifically on **multi-agent system-level dynamics** and **longitudinal behavior analysis**, providing instrumentation for studying how discovered phenomena propagate, stabilize, and evolve in population contexts.

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

AGI-SAC is intended to support and extend empirical findings from automated auditing, not replace them.

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
