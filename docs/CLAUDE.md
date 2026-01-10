# CLAUDE.md: AI Assistant Guide for AGI-SAC

> **Purpose**: This document provides comprehensive guidance for AI assistants (like Claude) working with the AGI-SAC codebase. It explains the architecture, conventions, patterns, and workflows to enable effective code modifications and contributions.

> **Documentation Contract**
> This file is a living internal guide for AI assistants working on AGI-SAC.
> It must reflect the current state of the codebase.
> When new CLI commands, modules, or workflows are added, this document
> MUST be updated in the same change to avoid documentation drift.
> Experimental or planned features should be labeled explicitly.

**Last Updated**: 2026-01-10
**Framework Version**: 1.0.0-alpha
**Python Version**: 3.9+
**Build System**: Poetry

---

## 📋 Documentation Contract

**This file is the authoritative execution contract for AI assistants working with AGI-SAC.**

### Contract Terms

1. **This document must remain accurate** - Any changes to architecture, CLI commands, core workflows, or development conventions REQUIRE updating this file
2. **Code is the source of truth** - If this document conflicts with the actual codebase, the codebase is correct and this document must be updated
3. **No undocumented features** - Features, CLI commands, or APIs not described here or in the codebase should be treated as non-existent until properly documented
4. **Accuracy over aspirations** - Describe what exists, not what is planned. Use clear language ("planned", "in progress", "experimental") for non-shipped features

### Update Triggers

Update CLAUDE.md when:
- Adding, removing, or modifying CLI commands
- Changing core architectural patterns
- Introducing new development conventions
- Modifying testing strategies
- Updating CI/CD workflows
- Adding or removing major components

### Validation

Before relying on information in this document:
1. Verify CLI commands exist in `src/agisa_sac/cli.py` or equivalent
2. Confirm file paths match actual repository structure
3. Check that described patterns appear in the codebase
4. Test commands work as documented

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Core Architecture](#core-architecture)
4. [Development Conventions](#development-conventions)
5. [Testing Strategy](#testing-strategy)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Common Tasks](#common-tasks)
8. [Code Patterns](#code-patterns)
9. [Troubleshooting](#troubleshooting)
10. [Resources](#resources)

---

## Project Overview

**AGI-SAC** (Artificial General Intelligence Stand Alone Complex) is a Python-based research framework for simulating and studying emergent collective intelligence in multi-agent systems.

### Key Research Areas
- **Emergent Cognition**: Bottom-up intelligence from agent interactions
- **Distributed Identity**: Identity formation across networked agents
- **Stand Alone Complex**: Coordinated behavior without central control
- **Integration Studies**: Computational models of emergent system behavior

### Technology Stack
- **Language**: Python 3.9+
- **Build System**: Poetry 2.x
- **Core Libraries**: PyTorch, Scikit-learn, NetworkX, SentenceTransformers
- **API Framework**: FastAPI
- **Documentation**: MkDocs with Material theme
- **Deployment**: Docker, GCP (optional)
- **Testing**: pytest with coverage
- **Code Quality**: black (line-length=88), ruff, flake8, mypy, pre-commit

### CLI Tools
```bash
agisa-sac           # Main simulation CLI
agisa-federation    # Federation server CLI
agisa-chaos         # Chaos engineering CLI
```

### Current CLI Commands
```bash
agisa-sac run              # Run a simulation
agisa-sac list-presets     # List configuration presets
agisa-sac convert-transcript  # Convert auditor transcript to context blob
```

---

## Codebase Structure

### Directory Layout

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
│   ├── auditing/               # Auditing integration (NEW)
│   │   ├── __init__.py         # Public exports
│   │   └── transcript_converter.py  # Transcript to context blob conversion
│   ├── analysis/               # TDA, clustering, visualization
│   │   ├── analyzer.py         # Analysis orchestration
│   │   └── tda.py              # Topological Data Analysis
│   ├── chaos/                  # Chaos engineering tools
│   │   └── orchestrator.py     # Chaos testing CLI
│   ├── cli/                    # CLI command handlers (NEW)
│   │   ├── __init__.py         # CLI exports
│   │   └── convert_transcript.py  # convert-transcript handler
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
│   ├── configs/                # Sample configurations
│   ├── scripts/                # Example scripts (NEW)
│   │   └── golden_contagion_experiment.py  # Network contagion simulation
│   └── results/                # Output directory for examples (NEW)
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

### Key File Paths (Relative to project root)

| Path | Purpose |
|------|---------|
| `src/agisa_sac/__init__.py` | Public API exports (`FRAMEWORK_VERSION`, main classes) |
| `src/agisa_sac/cli.py` | Main simulation CLI (`agisa-sac` command) |
| `src/agisa_sac/config.py` | Configuration dataclasses & presets |
| `src/agisa_sac/core/orchestrator.py` | Simulation orchestration & protocol injection |
| `src/agisa_sac/agents/agent.py` | EnhancedAgent with memory, cognition, voice |
| `src/agisa_sac/core/components/*.py` | Modular agent components |
| `src/agisa_sac/utils/logger.py` | Structured logging setup |
| `src/agisa_sac/utils/message_bus.py` | Event-driven pub/sub system |
| `src/agisa_sac/types/contracts.py` | Type definitions (Tool, LoopExit, etc.) |
| `src/agisa_sac/auditing/transcript_converter.py` | Transcript conversion utilities |
| `src/agisa_sac/cli/convert_transcript.py` | convert-transcript command handler |
| `examples/scripts/golden_contagion_experiment.py` | Standalone contagion simulation |

---

## Core Architecture

### Layered Architecture

AGI-SAC follows a 4-layer architecture pattern:

```
┌─────────────────────────────────────────────┐
│  CLI Layer (cli.py)                         │
│  - Argument parsing                         │
│  - Config loading                           │
│  - Orchestrator initialization              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Orchestration Layer (orchestrator.py)      │
│  - Multi-epoch coordination                 │
│  - Protocol injection                       │
│  - State persistence                        │
│  - Hook system (pre_epoch, post_epoch, etc.)│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Agent Layer (agents/)                      │
│  - EnhancedAgent (simulation)               │
│  - AGISAAgent (production)                  │
│  - Component composition                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Component Layer (core/components/)         │
│  - Memory, Cognitive, Voice, Reflexivity    │
│  - Social Graph, Resonance Tracker          │
│  - Modular, composable, serializable        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Analysis Layer (analysis/)                 │
│  - TDA (Topological Data Analysis)          │
│  - Satori wave detection                    │
│  - Clustering & visualization               │
└─────────────────────────────────────────────┘
```

### Component Composition Pattern

Agents are composed of specialized, independent components:

```python
EnhancedAgent
├── MemoryContinuumLayer     # Episodic & semantic memory with decay
├── CognitiveDiversityEngine # Heterogeneous decision heuristics
├── VoiceEngine              # Linguistic signature generation
├── TemporalResonanceTracker # Synchronization pattern detection
├── ReflexivityLayer         # Meta-cognitive awareness
└── ResonanceLiturgy         # Synchronization commentary
```

**Key Properties:**
- Each component is self-contained and testable
- Components communicate via MessageBus (pub/sub)
- All components support serialization (`to_dict()`/`from_dict()`)
- Graceful degradation for optional dependencies

### Memory Architecture

Three-tier memory system:

1. **MemoryEncapsulation**: Individual memory unit
   - Content verification (MD5 hash)
   - Importance/confidence scoring
   - Decay mechanics (recency & access-based)
   - Optional semantic embeddings

2. **MemoryContinuumLayer**: Memory manager
   - Capacity-based eviction (importance-weighted)
   - Semantic retrieval (cosine similarity)
   - Keyword fallback when embeddings unavailable
   - Theme-based organization

3. **CRDTMemoryLayer**: Distributed memory
   - Conflict-free replicated data types
   - Multi-node synchronization
   - Federation support

### Data Flow

**Simulation Loop:**
```
CLI → Orchestrator.run_simulation()
  ↓
  For each epoch:
    ↓
    orchestrator.run_epoch()
      ↓
      For each agent:
        ├── update_heuristics(entropy)
        ├── decide(query, peer_influence)
        ├── simulation_step()
        ├── check_resonance()
        └── record to chronicler
      ↓
      TDA analysis on cognitive states
      Community detection on social graph
      Protocol injection (if scheduled)
      Hook execution (post_epoch, etc.)
  ↓
  Save state, generate reports
```

**Component Interaction:**
```
Cognitive retrieves memories → Decision → Updates cognitive state
                                  ↓
                            Voice signature recorded
                                  ↓
                        Temporal resonance check
                                  ↓
                    Strong echoes → Reflexivity layer
                                  ↓
                          MessageBus publishes event
```

### Extension Pattern (Concord Example)

Extensions are self-contained modules that:
- Wrap or extend base agents
- Implement additional constraints/behaviors
- Follow same serialization patterns

```
extensions/concord/
├── __init__.py         # Public API exports
├── agent.py            # ConcordCompliantAgent
├── ethics.py           # Guardian modules (Articles III, IV, VII, IX)
├── circuits.py         # Mirror neuron circuits
└── empathy.py          # Empathy module
```

Ethical modules act as decorators/middleware:
- `NonCoercionGuardian`: Checks actions against constraints
- `ContinuityEvaluator`: Behavioral continuity assessment (operational metrics, NOT consciousness)
- `DisengagementProtocol`: Right to terminate interaction

---

## Development Conventions

### 1. Serialization is Mandatory

**Every stateful component MUST implement:**

```python
import warnings
from typing import Any, Dict

class MyComponent:
    def to_dict(self, **options) -> Dict[str, Any]:
        """Serialize component state to dictionary."""
        # IMPORTANT: avoid top-level imports of FRAMEWORK_VERSION inside the package.
        # In `src/agisa_sac/core/components/*.py`, the correct relative import is:
        #   from ... import FRAMEWORK_VERSION
        # and it should be done inside methods to reduce circular-import risk.
        try:
            from ... import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"
        return {
            "version": FRAMEWORK_VERSION,
            "state_key": self.state_value,
            # ... more state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **context) -> "MyComponent":
        """Reconstruct component from dictionary."""
        try:
            from ... import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"

        # Version check
        if data.get("version") != FRAMEWORK_VERSION:
            warnings.warn(
                f"Version mismatch: {data.get('version')} != {FRAMEWORK_VERSION}"
            )

        # Reconstruct state
        instance = cls(...)
        instance.state_value = data["state_key"]
        return instance
```

**Why?** State persistence, federation synchronization, checkpointing.

### 2. Optional Dependencies Pattern

**Always gracefully degrade for optional dependencies:**

```python
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMER = True
except ImportError:
    HAS_SENTENCE_TRANSFORMER = False

class MyComponent:
    def __init__(self, use_semantic: bool = True):
        if use_semantic and HAS_SENTENCE_TRANSFORMER:
            self.model = SentenceTransformer(...)
        elif use_semantic:
            warnings.warn("SentenceTransformer not available, using fallback")
            self.model = None
        else:
            self.model = None
```

**Common optional deps:** SentenceTransformers, CuPy (GPU), GCP libraries

### 3. MessageBus for Decoupling

**Use pub/sub for cross-component communication:**

```python
import time
from typing import Dict, Any
from agisa_sac.utils.message_bus import MessageBus
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Publisher
self.message_bus.publish("agent_resonance_detected", {
    "agent_id": self.agent_id,
    "resonance_score": score,
    "timestamp": time.time()
})

# Subscriber
def on_resonance(event_data: Dict[str, Any]):
    logger.info("Agent %s resonated!", event_data['agent_id'])

message_bus.subscribe("agent_resonance_detected", on_resonance)
```

**Standard events:**
- `agent_resonance_detected`
- `cognitive_heuristic_update`
- `satori_event_detected`
- `memory_consolidated`

### 4. Logging Not Print

**Always use structured logging:**

```python
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Good
logger.info("Simulation started", extra={"agents": num_agents, "epochs": num_epochs})
logger.debug("Processing epoch %d", epoch)
logger.error("Failed to load state", exc_info=True)

# Bad
print("Simulation started")  # ❌ Never use print()
```

**Log levels:**
- `DEBUG`: Detailed diagnostic info
- `INFO`: General informational messages
- `WARNING`: Warning messages for degraded functionality
- `ERROR`: Error messages with stack traces

### 5. Type Hints Everywhere

**Use comprehensive type hints:**

```python
from typing import Dict, List, Optional, Union, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from agisa_sac.core.orchestrator import SimulationOrchestrator

def process_data(
    config: Dict[str, Any],
    output_path: Optional[Path] = None,
    *,
    strict: bool = True
) -> List[str]:
    """Process data with configuration."""
    ...
```

**Common types:**
- Use `Dict[str, Any]` for JSON-like data
- Use `Optional[T]` for nullable values
- Use `Path` for file paths
- Use `*` for keyword-only arguments

### 6. Hook System for Extension

**Use hooks for extensibility:**

```python
from typing import Callable

# Register hook
def my_hook(orchestrator, epoch: int, **kwargs):
    logger.info(f"Hook called at epoch {epoch}")

orchestrator.register_hook("pre_epoch", my_hook)

# Available hooks
- pre_epoch(orchestrator, epoch, **kwargs)
- post_epoch(orchestrator, epoch, metrics, **kwargs)
- simulation_start(orchestrator, **kwargs)
- simulation_end(orchestrator, results, **kwargs)
```

### 7. GPU/Hardware Agnostic

**Always check for GPU availability:**

```python
import warnings
import numpy as np

try:
    import cupy as cp
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

def process_matrix(data: np.ndarray, use_gpu: bool = False):
    if use_gpu and HAS_CUPY:
        data_gpu = cp.array(data)
        result = cp.asnumpy(cp.sum(data_gpu))
        return result
    elif use_gpu:
        warnings.warn("GPU requested but CuPy not available, using CPU")

    return np.sum(data)
```

### 8. Version Tracking

**Include version in serialized state:**

```python
import warnings
from typing import Any, Dict

def to_dict(self) -> Dict[str, Any]:
    try:
        from ... import FRAMEWORK_VERSION
    except ImportError:
        FRAMEWORK_VERSION = "unknown"
    return {
        "version": FRAMEWORK_VERSION,  # Always include
        # ... rest of state
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "MyClass":
    try:
        from ... import FRAMEWORK_VERSION
    except ImportError:
        FRAMEWORK_VERSION = "unknown"
    version = data.get("version")
    if version != FRAMEWORK_VERSION:
        warnings.warn(
            f"State version mismatch: {version} != {FRAMEWORK_VERSION}. "
            "Behavior may be unpredictable."
        )
    # ... reconstruct
```

### 9. Validation Pattern

**Implement validation with strict/non-strict modes:**

```python
import warnings

def _validate_state(self, strict: bool = True) -> None:
    """Validate internal state."""
    errors = []
    warnings_list = []

    if self.value < 0:
        errors.append("value must be non-negative")

    if self.optional_field is None:
        warnings_list.append("optional_field is None, using default")

    if strict and errors:
        raise ValueError(f"Validation failed: {', '.join(errors)}")
    elif errors:
        warnings.warn(f"Validation warnings: {', '.join(errors + warnings_list)}")
    elif warnings_list:
        warnings.warn(f"Validation notes: {', '.join(warnings_list)}")
```

### 10. Resource Management

**Clean up resources properly:**

```python
from contextlib import contextmanager

@contextmanager
def gcp_client():
    """Context manager for GCP client."""
    client = SomeGCPClient()
    try:
        yield client
    finally:
        client.close()

# Usage
with gcp_client() as client:
    client.do_something()

# GPU memory management
if HAS_CUPY:
    cp.get_default_memory_pool().free_all_blocks()
```

---

## Testing Strategy

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Component-level tests
│   ├── conftest.py          # Path setup
│   ├── test_memory.py
│   ├── test_cognitive.py
│   └── ...
├── integration/             # System-level tests
│   └── test_multi_agent_system.py
├── chaos/                   # Chaos engineering tests
│   └── test_federation_resilience.py
└── extensions/              # Extension-specific tests
    └── concord/
        └── test_ethics.py
```

### Shared Fixtures (tests/conftest.py)

```python
@pytest.fixture
def sample_config():
    """Minimal configuration for testing."""
    return {
        "num_agents": 3,
        "num_epochs": 2,
        "random_seed": 42,
        "use_semantic": False,  # Avoid heavy dependencies
        "use_gpu": False
    }

@pytest.fixture
def sample_personality():
    """Standard personality traits."""
    return {
        "openness": 0.7,
        "conscientiousness": 0.6,
        "extraversion": 0.5,
        "agreeableness": 0.8,
        "neuroticism": 0.3
    }
```

### Testing Best Practices

**1. Disable heavy dependencies in tests:**
```python
config = {
    "use_semantic": False,  # Disable SentenceTransformer
    "use_gpu": False,       # Disable GPU acceleration
}
```

**2. Mock GCP dependencies:**
```python
from unittest.mock import Mock, patch

@patch("agisa_sac.gcp.SomeClient")
def test_gcp_integration(mock_client):
    mock_client.return_value.method.return_value = "mocked"
    # ... test
```

**3. Use small agent counts for speed:**
```python
# Good for unit tests
config = {"num_agents": 3, "num_epochs": 2}

# Good for integration tests
config = {"num_agents": 10, "num_epochs": 5}

# Avoid in tests unless necessary
config = {"num_agents": 100, "num_epochs": 100}
```

**4. Test serialization:**
```python
def test_component_serialization():
    component = MyComponent(param=42)

    # Serialize
    state = component.to_dict()

    # Deserialize
    restored = MyComponent.from_dict(state)

    # Verify
    assert restored.param == 42
    assert component.to_dict() == restored.to_dict()
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/agisa_sac --cov-report=html --cov-report=term

# Run specific test suite
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/chaos/

# Run with parallel execution
poetry run pytest -n auto

# Run with timeout (5 minutes per test)
poetry run pytest --timeout=300

# Run verbose with strict markers
poetry run pytest -v --strict-markers --strict-config
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

**Workflow File:** `.github/workflows/ci.yml`

**Jobs:**

1. **Lint & Format** (Python 3.12)
   - `ruff` - Linting and formatting
   - `black --check` - Formatting check
   - `mypy` - Type checking
   - `pip-audit` - Security audit (non-blocking)

2. **Test** (Python 3.10, 3.11, 3.12)
   - Install dependencies (`poetry install`)
   - Run `poetry run pytest` with coverage
   - Upload coverage to Codecov
   - Upload test results as artifacts
   - Publish test results to GitHub Checks

3. **GCP Preview** (main branch only)
   - Authenticate with GCP Workload Identity
   - Run smoke tests on Cloud Run services
   - Dry-run Kubernetes manifests

4. **CI Success** (summary job)
   - Checks all required jobs passed
   - Provides single status check for PRs

### Pre-commit Hooks

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

**Setup:**
```bash
poetry install --with dev
poetry run pre-commit install
```

**Manual run:**
```bash
poetry run pre-commit run --all-files
```

### Code Quality Requirements

Before committing:
```bash
# Format code (line-length=88)
poetry run black src/ tests/

# Lint with flake8
poetry run flake8 src/ tests/

# Lint with ruff
poetry run ruff src/ tests/

# Type check
poetry run mypy src/agisa_sac --ignore-missing-imports

# Run tests
poetry run pytest --cov=src/agisa_sac

# Run all pre-commit checks
poetry run pre-commit run --all-files
```

---

## Common Tasks

### Adding a New Component

**1. Create the component file:**
```bash
touch src/agisa_sac/core/components/my_component.py
```

**2. Implement the component:**
```python
import warnings
from typing import Any, Dict
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

class MyComponent:
    """Brief description of component."""

    def __init__(self, param: float = 1.0):
        self.param = param
        self.state = {}

    def process(self, data: Dict[str, Any]) -> Any:
        """Process data."""
        logger.debug("Processing with param=%f", self.param)
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        try:
            from ... import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"
        return {
            "version": FRAMEWORK_VERSION,
            "param": self.param,
            "state": self.state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MyComponent":
        """Deserialize from dictionary."""
        try:
            from ... import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"
        if data.get("version") != FRAMEWORK_VERSION:
            warnings.warn(
                f"Loading MyComponent v '{data.get('version')}' into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )
        instance = cls(param=data["param"])
        instance.state = data["state"]
        return instance
```

**3. Add tests:**
```python
# tests/unit/test_my_component.py
import pytest
from agisa_sac.core.components.my_component import MyComponent

def test_my_component():
    component = MyComponent(param=2.0)
    assert component.param == 2.0

def test_serialization():
    component = MyComponent(param=3.0)
    state = component.to_dict()
    restored = MyComponent.from_dict(state)
    assert restored.param == 3.0
```

**4. Export in `__init__.py`:**
```python
# src/agisa_sac/core/components/__init__.py
from .my_component import MyComponent

__all__ = ["MyComponent", ...]
```

### Adding a New Protocol

**1. Locate protocol injection in orchestrator:**
```python
# src/agisa_sac/core/orchestrator.py
def inject_protocol(self, protocol_name: str, params: Dict[str, Any]) -> str:
    """Inject a protocol during simulation."""
```

**2. Add protocol handler:**
```python
elif protocol_name == "my_new_protocol":
    return self._inject_my_protocol(params)
```

**3. Implement the protocol:**
```python
def _inject_my_protocol(self, params: Dict[str, Any]) -> str:
    """Inject my new protocol."""
    threshold = params.get("threshold", 0.8)

    affected_agents = []
    for agent in self.mas.agents:
        if agent.some_metric > threshold:
            agent.apply_effect(params)
            affected_agents.append(agent.agent_id)

    logger.info(
        "My protocol injected: %d agents affected",
        len(affected_agents)
    )
    return f"My protocol injected on {len(affected_agents)} agents"
```

**4. Document in docstring and add tests.**

### Adding a CLI Command

**1. Locate CLI parser:**
```python
# src/agisa_sac/cli.py
def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command")
```

**2. Add subcommand:**
```python
# New subcommand
my_parser = subparsers.add_parser(
    "my-command",
    help="Description of my command"
)
my_parser.add_argument("--param", type=str, help="Parameter")
```

**3. Implement command handler:**
```python
def handle_my_command(args):
    """Handle my-command."""
    logger.info("Executing my-command with param=%s", args.param)
    # ... implementation
    return 0  # Exit code
```

**4. Wire up in main:**
```python
def main():
    # ... parser setup

    if args.command == "my-command":
        return handle_my_command(args)
```

### Modifying Agent Behavior

**1. Locate agent class:**
- Simulation agent: `src/agisa_sac/agents/agent.py` (EnhancedAgent)
- Production agent: `src/agisa_sac/agents/base_agent.py` (AGISAAgent)

**2. Modify behavior:**
```python
class EnhancedAgent:
    def decide(self, query: str, peer_influence: float = 0.0) -> float:
        # Original logic
        # ...

        # Add new behavior
        if self.should_apply_new_behavior():
            result = self.apply_new_behavior(query)
            return result

        # ... rest of original logic
```

**3. Update serialization if state changed:**
```python
def to_dict(self) -> Dict[str, Any]:
    d = {
        # ... existing state
        "new_field": self.new_field,  # Add new field
    }
    return d
```

**4. Add tests for new behavior.**

### Updating Documentation

**1. Edit Markdown files in `docs/`:**
```bash
vim docs/my_topic.md
```

**2. Update `mkdocs.yml` if adding new pages:**
```yaml
nav:
  - Home: index.md
  - My Topic: my_topic.md
```

**3. Build and preview locally:**
```bash
poetry install --with docs
poetry run mkdocs build --strict  # Check for errors
poetry run mkdocs serve            # Preview at http://127.0.0.1:8000/
```

**4. Deploy to GitHub Pages (if authorized):**
```bash
poetry run mkdocs gh-deploy
```

---

## Code Patterns

### Configuration Pattern

**Use dataclasses for configuration:**

```python
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class SimulationConfig:
    """Configuration for simulation."""
    num_agents: int = 5
    num_epochs: int = 10
    random_seed: Optional[int] = 42
    use_gpu: bool = False
    personalities: List[Dict[str, float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "num_agents": self.num_agents,
            "num_epochs": self.num_epochs,
            "random_seed": self.random_seed,
            "use_gpu": self.use_gpu,
            "personalities": self.personalities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
```

### Factory Pattern for Agents

```python
def create_agent(
    agent_id: int,
    personality: Optional[Dict[str, float]] = None,
    config: Optional[Dict[str, Any]] = None
) -> EnhancedAgent:
    """Factory function for creating agents."""
    config = config or {}
    personality = personality or _default_personality()

    return EnhancedAgent(
        agent_id=agent_id,
        capacity=config.get("agent_capacity", 100),
        use_semantic=config.get("use_semantic", False),
        personality_traits=personality,
        message_bus=config.get("message_bus")
    )
```

### Observer Pattern (MessageBus)

```python
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

class MessageBus:
    """Simple pub/sub message bus."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable):
        """Subscribe to event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)

    def publish(self, event: str, data: Any):
        """Publish event."""
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error("Error in subscriber: %s", e, exc_info=True)
```

### Decorator Pattern for Ethics

```python
class EthicsDecorator:
    """Wrapper for ethical constraints."""

    def __init__(self, agent: EnhancedAgent, guardian: Guardian):
        self.agent = agent
        self.guardian = guardian

    def decide(self, query: str, **kwargs) -> float:
        """Make decision with ethical check."""
        # Check if action is permitted
        if not self.guardian.check_action(query):
            logger.warning("Action blocked by ethics: %s", query)
            return 0.0

        # Proceed with original decision
        return self.agent.decide(query, **kwargs)
```

### Strategy Pattern for Cognitive Diversity

```python
from abc import ABC, abstractmethod

class CognitiveStrategy(ABC):
    """Base class for cognitive strategies."""

    @abstractmethod
    def compute(self, state: Dict[str, Any]) -> float:
        """Compute decision value."""
        pass

class ConservativeStrategy(CognitiveStrategy):
    def compute(self, state: Dict[str, Any]) -> float:
        return state.get("base_value", 0.5) * 0.8

class AggressiveStrategy(CognitiveStrategy):
    def compute(self, state: Dict[str, Any]) -> float:
        return min(state.get("base_value", 0.5) * 1.2, 1.0)

# Usage
class CognitiveDiversityEngine:
    def __init__(self, strategy: CognitiveStrategy):
        self.strategy = strategy

    def decide(self, state: Dict[str, Any]) -> float:
        return self.strategy.compute(state)
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'agisa_sac'`

**Solution:**
```bash
# Install with Poetry
poetry install

# Or install development dependencies
poetry install --with dev

# Or add src to PYTHONPATH (from project root)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 2. Missing Optional Dependencies

**Problem:** `ImportError: SentenceTransformer not available`

**Solution:**
```bash
# Install all optional dependency groups
poetry install --with dev,docs,visualization,monitoring,gcp,topology,chaos,federation

# Or specific group
poetry install --with dev

# Or disable in config
config = {"use_semantic": False}
```

#### 3. GPU Not Available

**Problem:** `GPU requested but CuPy not available`

**Solution:**
```bash
# Install CuPy (requires CUDA)
pip install cupy-cuda11x  # Replace 11x with your CUDA version

# Or disable GPU
agisa-sac run --preset medium  # Don't use --gpu flag
```

#### 4. Serialization Version Mismatch

**Problem:** `UserWarning: State version mismatch: 0.9.0 != 1.0.0-alpha`

**Solution:**
```python
# Load with non-strict mode
orchestrator.load_state("old_state.pkl", strict=False)

# Or regenerate state with current version
```

#### 5. Memory Errors

**Problem:** `MemoryError` during large simulations

**Solution:**
```bash
# Reduce agent count
agisa-sac run --preset medium --agents 50  # Instead of 500

# Disable embeddings
config = {"use_semantic": False}

# Limit memory history
config = {"max_memory_per_agent": 50}
```

### Debugging Tips

**1. Enable debug logging:**
```bash
agisa-sac run --preset default --log-level DEBUG
```

**2. Use Python debugger:**
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

**3. Check component state:**
```python
state = agent.to_dict()
import json
print(json.dumps(state, indent=2))
```

**4. Trace MessageBus events:**
```python
def trace_all(event_data):
    print(f"Event: {event_data}")

message_bus.subscribe("*", trace_all)  # If wildcard supported
```

### Performance Optimization

**1. Profile simulations:**
```bash
python -m cProfile -o profile.stats -m agisa_sac.cli run --preset medium
python -m pstats profile.stats
```

**2. Use GPU acceleration:**
```bash
agisa-sac run --preset large --gpu
```

**3. Reduce TDA frequency:**
```python
config = {
    "tda_run_frequency": 10,  # Run TDA every 10 epochs instead of every epoch
}
```

**4. Disable expensive features:**
```python
config = {
    "use_semantic": False,  # Disable semantic embeddings
    "community_check_frequency": 20,  # Reduce community detection frequency
}
```

---

## Resources

### Documentation

- **Main README**: `README.md`
- **GEMINI.md**: AI-generated project overview
- **CONTRIBUTING.md**: Contribution guidelines
- **TODO.md**: Roadmap and unimplemented features
- **Whitepapers**:
  - `docs/Mindlink_WhitePaper_v1.0.pdf`
  - `docs/agentic_swarm_whitepaper.md`

### Key Modules to Study

1. **Core Orchestration**: `src/agisa_sac/core/orchestrator.py` (SimulationOrchestrator)
2. **Agent Implementation**: `src/agisa_sac/agents/agent.py` (EnhancedAgent)
3. **Memory System**: `src/agisa_sac/core/components/memory.py`
4. **Configuration**: `src/agisa_sac/config.py`
5. **CLI**: `src/agisa_sac/cli.py`
6. **Type Contracts**: `src/agisa_sac/types/contracts.py`

### External References

- **Global Workspace Theory**: Baars, B. J. (1988)
- **Instrumental Convergence**: Bostrom, N. (2012)
- **Stand Alone Complex**: Ghost in the Shell (philosophical concept)
- **CRDT**: Conflict-free Replicated Data Types (Marc Shapiro et al.)
- **TDA**: Topological Data Analysis (Carlsson, G.)

### Development Tools

- **Build System**: `poetry` (2.x)
- **Code Formatter**: `black` (line-length=88)
- **Linters**: `flake8` (max-line-length=88), `ruff`
- **Type Checker**: `mypy` (Python 3.9+)
- **Test Framework**: `pytest` with coverage
- **Documentation**: `mkdocs` with Material theme
- **Pre-commit**: `.pre-commit-config.yaml`

### Contact & Support

- **Repository**: https://github.com/topstolenname/agisa_sac
- **Email**: tristan@mindlink.dev
- **Issues**: https://github.com/topstolenname/agisa_sac/issues

---

## Quick Reference

### CLI Commands

```bash
# Run simulation
agisa-sac run --preset medium --agents 50 --epochs 100

# List presets
agisa-sac list-presets

# Convert auditor transcript to context blob
agisa-sac convert-transcript --input transcript.json --output context.json

# Start federation server
agisa-federation server --host 0.0.0.0 --port 8000

# Run chaos tests
agisa-chaos run --scenario sybil_attack --url http://localhost:8000

# Run golden contagion experiment (requires networkx)
python examples/scripts/golden_contagion_experiment.py --transcript transcript.json
```

### Configuration Presets

| Preset | Agents | Epochs | Use Case |
|--------|--------|--------|----------|
| `quick_test` | 10 | 20 | Fast testing, CI/CD |
| `default` | 30 | 50 | Development |
| `medium` | 100 | 100 | Research experiments |
| `large` | 500 | 200 | Production simulations |

### Important Paths

```
.
├── src/agisa_sac/           # Package source
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Example configs
├── pyproject.toml           # Package metadata
└── mkdocs.yml               # Docs config
```

### Key Imports

```python
from agisa_sac import FRAMEWORK_VERSION
from agisa_sac.core.orchestrator import SimulationOrchestrator
from agisa_sac.agents.agent import EnhancedAgent
from agisa_sac.config import SimulationConfig, PRESETS
from agisa_sac.utils.logger import get_logger
from agisa_sac.utils.message_bus import MessageBus
```

---

**End of CLAUDE.md**

**This document is maintained for AI assistants working with the AGI-SAC codebase. When making significant changes to architecture or conventions, update this file accordingly.**
