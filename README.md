# AGI-SAC: Model Organism Simulation Framework

> **Instrumented multi-agent system for alignment, robustness, and oversight research**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Framework-AGI--SAC%20v1.0.0--alpha-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Core Thesis

**AGI-SAC studies alignment as a property of integrated groups within a system architecture, rather than as a property of individual agents.**

Here, "AGI" refers to Aligned Group Integration, not artificial general intelligence.

## Overview

**AGI-SAC** (Aligned Group Integration — System Architecture Coexistence) is a **model organism framework** for studying alignment-relevant failure modes, system-level dynamics, and coordination patterns in multi-agent systems. It provides instrumented environments for stress testing multi-agent populations under adversarial conditions and detecting emergent behavioral transitions.

### What This Is

AGI-SAC is a **research instrument** designed to:

- Study **emergent system behavior** in multi-agent environments
- Detect **change-points and phase transitions** in distributed dynamics
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

### Reviewer Orientation

**For reviewers and collaborators:**

AGI-SAC is a research framework for studying multi-agent dynamics, robustness, and behavioral propagation under controlled conditions. It makes no claims about consciousness, sentience, or general intelligence. All metrics are operational proxies used for system-level analysis only.

---

## Quick Start

### Installation

```bash
# Basic installation
pip install agisa-sac

# Full installation with all features (optional extras may vary by environment)
pip install agisa-sac[all]
```

### Running Your First Simulation (Current CLI)

AGI-SAC currently exposes two CLI commands:
- `agisa-sac run`
- `agisa-sac list-presets`

```bash
# Run a preset
agisa-sac run --preset quick_test

# Run from config JSON
agisa-sac run --config examples/configs/config.json

# Override agent/epoch counts
agisa-sac run --preset default --agents 50 --epochs 100 --seed 42

# List presets
agisa-sac list-presets
```

---

## Architecture

AGI-SAC uses a modular, layered architecture optimized for observability and instrumentation:

- **Core simulation loop** (multi-agent system + orchestrator)
- **Analysis layer** (TDA, clustering, visualization)
- **Chaos layer** (adversarial stress and resilience scenarios)
- **Orchestration integrations** (handoff consumer + topology manager for distributed/GCP workflows)

### Core Components (Model Organism Subsystems)

- **Memory Continuum Layer**: Temporal memory with decay mechanics and CRDT-based synchronization
- **Policy Diversity Engine**: Heterogeneous decision strategies per agent
- **Dynamic Social Graph**: Adaptive peer influence network
- **Temporal Resonance Tracker**: Synchronization pattern detection
- **Voice Engine**: Agent-specific output signatures (identity persistence under influence)
- **Reflexivity Layer**: Internal state monitoring and transition detection (self-correction dynamics)

---

## Key Research Applications

### 1. Alignment-Relevant Failure Modes

- **Power-seeking dynamics**: Instrumental convergence patterns in agent populations
- **Deceptive alignment signals**: Divergence between stated and revealed preferences
- **Mesa-optimization**: Emergent optimization processes distinct from base objectives
- **Goal misgeneralization**: Behavioral drift under distribution shift

### 2. Robustness & Adversarial Testing (Chaos Engineering)

- **Sybil resistance**: Coordinated fake identity attacks on trust graphs
- **Semantic drift**: Gradual coherence boundary erosion
- **Network partitions**: Consistency under split-brain scenarios
- **Eclipse attacks**: Coordinated network isolation
- **Resource exhaustion**: Load testing and DoS resistance

### 3. Change-Point & Transition Detection

- **Topological Data Analysis (TDA)**: Persistent homology tracking
- **Resonance analysis**: Coordination pattern emergence
- **Community detection**: Dynamic clustering of agent strategies

### 4. Coordination Without Hierarchy

- **Stand Alone Complex**: Coordinated behavior without central control
- **Information cascades**: Meme propagation dynamics
- **Emergent norms**: Bottom-up constraint formation
- **Collective decision-making**: Aggregation mechanisms at scale

---

## Relationship to Automated Auditing & Red-Teaming Tools

AGI-SAC is designed to **complement automated auditing frameworks** (agent-driven red-teaming / probing systems) by providing a *system-level model organism* in which discovered behaviors can be contextualized, replayed, and stress-tested over time.

**Where automated auditors excel at:**
- Rapidly eliciting rare or concerning behaviors through adversarial probing
- Exploring behavioral space via parallel multi-turn interactions
- Surfacing transcripts that warrant human review and deeper analysis

**AGI-SAC focuses on:**
- **Dynamics**: how behaviors emerge, stabilize, spread, or self-correct across populations
- **Context**: how memory, coordination, and network structure shape outcomes
- **Trajectories**: brittle artifacts vs. robust system-level attractors
- **Instrumentation**: phase transitions and early warning signals, not one-off anecdotes

This separation mirrors the distinction between **unit tests and systems biology**:  
auditors surface signals; AGI-SAC characterizes the organism.

---

## Auditing Integration (In Progress)

AGI-SAC is adding first-class tooling to ingest generic auditor outputs (e.g., JSON transcripts) into repeatable experiments.

**Current Tooling:**
- **`agisa-sac convert-transcript`**: Convert auditor transcript JSON to AGI-SAC context blob
  - Generates artifact with privacy-preserving names (no content leakage)
  - Configurable injection policy (target epoch, exposure rate)
- **Golden experiment script** (`examples/scripts/golden_contagion_experiment.py`):
  - Simulates contagion spread across 3 network topologies (dense, modular, sparse)
  - Standalone NetworkX-based simulation (no orchestrator dependency)
  - Outputs JSON with time series data for analysis

**Planned:**
- Orchestration integration for distributed artifact ingestion
- Handoff consumer support for context blob loading
- Policy-driven injection at specified epochs

---

## Project Structure (Current)

Key packages include:

- `agents/` — agent implementations
- `core/` — core simulation loop (multi-agent system + orchestrator)
- `analysis/` — TDA, clustering, visualization, analyzers
- `chaos/` — chaos engine + adversarial scenario orchestration
- `cognition/` + `cge/` — cognitive evaluation/optimization components
- `extensions/concord/` — ethical/constraint and "Concord" extensions
- `federation/` — federation components (experimental / evolving)
- `gcp/` — GCS/Vertex helpers and distributed agent utilities
- `orchestration/` — integration layer (handoff consumer + topology manager)
- `persistence/` — storage abstractions (e.g., Firestore)
- `utils/`, `types/`, `observability/`, `metrics/`, `chronicler.py` — supporting infrastructure

---

## Intended Audience

AGI-SAC is designed for:

- **AI safety researchers** studying alignment-relevant failure modes
- **Multi-agent systems researchers** investigating coordination dynamics
- **Chaos engineers** testing distributed system resilience
- **Oversight & auditing researchers** developing diagnostic and red-teaming tools

**Not intended for:**
- Philosophical debates about machine consciousness
- Claims of achieving AGI or human-level intelligence
- Ethical arguments for AI rights or moral standing

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

MIT License — see [LICENSE](LICENSE) for details.

All code and documentation in this repository are licensed under the MIT License unless otherwise noted.

---

## Contact

- **Email**: [tristan@mindlink.dev](mailto:tristan@mindlink.dev)
- **GitHub**: [topstolenname/agisa_sac](https://github.com/topstolenname/agisa_sac)
