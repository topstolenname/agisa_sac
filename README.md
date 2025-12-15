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

# Test Files Manifest for PR

This document lists the test files that need to be created for the Research Substrate Readiness PR.

## Test Files to Create

### 1. tests/unit/test_orchestrator_boundaries.py
**Size:** ~500 lines
**Tests:** 20
**Coverage Target:** `src/agisa_sac/core/orchestrator.py` (0% → 85%)

**Test Classes:**
- `TestOrchestrationStateTransitions` (6 tests)
- `TestAgentHandoffCoordination` (3 tests)
- `TestEpochBoundariesAndTermination` (4 tests)
- `TestStatePersistence` (3 tests)
- `TestOrchestrationErrorHandling` (2 tests)

**Key Tests:**
- `test_orchestrator_runs_exact_epoch_count`
- `test_epoch_ordering_is_sequential`
- `test_successful_agent_handoff_preserves_state`
- `test_orchestrator_state_round_trips_without_loss`

### 2. tests/unit/test_topology_fragmentation.py
**Size:** ~550 lines
**Tests:** 20
**Coverage Target:** `src/agisa_sac/orchestration/topology_manager.py` (80% → 90%)

**Test Classes:**
- `TestFragmentationDetection` (7 tests)
- `TestResonancePropagation` (4 tests)
- `TestTopologyRecovery` (3 tests)
- `TestTopologyDataAnalysis` (2 tests, skipif no ripser)
- `TestTopologyInvariants` (3 tests)

**Key Tests:**
- `test_fragmentation_detection_is_deterministic`
- `test_resonance_propagation_is_deterministic`
- `test_resonance_blocked_by_fragmentation`

### 3. tests/integration/test_message_bus_invariants.py
**Size:** ~600 lines
**Tests:** 18
**Coverage Target:** `src/agisa_sac/utils/message_bus.py` (18% → 75%)

**Test Classes:**
- `TestMessageDeliveryBasics` (4 tests)
- `TestMessageOrderingInvariants` (3 tests)
- `TestBackpressureAndResourceExhaustion` (3 tests)
- `TestMessageBusIsolation` (2 tests)
- `TestMessageBusStateSafety` (2 tests)
- `TestMessageBusDocumentedBehavior` (3 tests - documentation)

**Key Tests:**
- `test_message_ordering_not_guaranteed_across_subscribers` ⚠️
- `test_message_bus_has_no_backpressure_mechanism` ⚠️
- `test_rapid_publishing_does_not_drop_messages`

**Safety Notes:** Tests explicitly document undefined behavior (ordering, backpressure)

### 4. tests/unit/test_cognitive_thresholds.py
**Size:** ~450 lines
**Tests:** 12
**Coverage Target:** `src/agisa_sac/agents/base_agent.py`, cognitive components (24% → 70%)

**Test Classes:**
- `TestPhaseTransitionThresholdComputation` (5 tests) - renamed from Satori
- `TestReflectionTriggerConditions` (4 tests)
- `TestVoiceComponentActivation` (3 tests, skipif no voice)
- `TestCognitiveStateConsistency` (3 tests)
- `TestDecisionBoundaryConditions` (3 tests)

**Key Tests:**
- `test_phase_transition_threshold_is_deterministic`
- `test_decision_determinism_with_fixed_inputs` (documents non-determinism) ⚠️

**Updated Terminology:** "Phase transition" instead of "satori" in test names/docs

### 5. tests/unit/test_memory_degradation.py
**Size:** ~500 lines
**Tests:** 12
**Coverage Target:** `src/agisa_sac/core/components/memory.py` (39% → 70%)

**Test Classes:**
- `TestMemoryCapacityEnforcement` (5 tests)
- `TestCRDTMergeSemantics` (5 tests) - **strengthened with ID comparison**
- `TestMemoryRetrievalOrdering` (4 tests)
- `TestMemorySerializationRoundTrip` (4 tests)
- `TestMemoryEvictionPolicy` (3 tests)

**Key Tests:**
- `test_merge_is_commutative` (strengthened: compares memory ID sets)
- `test_merging_identical_memories_is_idempotent` (strengthened: checks no duplicate IDs)
- `test_capacity_is_hard_limit`

**Important:** CRDT tests use memory ID sets for stronger guarantees (not just counts)

## Creation Instructions

The full test file content is available in the conversation history above. Each file should be created with:

1. **Proper imports:**
```python
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
```

2. **Fixtures:** Each file has 3-5 pytest fixtures for test setup

3. **Docstrings:** All tests have Given/When/Then docstrings

4. **Safety notes:** Tests documenting undefined behavior include SAFETY NOTE comments

## Quick Creation Script

```bash
# From PR root directory
source venv/bin/activate

# Create test files (copy content from conversation)
# tests/unit/test_orchestrator_boundaries.py
# tests/unit/test_topology_fragmentation.py
# tests/integration/test_message_bus_invariants.py
# tests/unit/test_cognitive_thresholds.py
# tests/unit/test_memory_degradation.py

# Verify tests run
pytest tests/unit/test_orchestrator_boundaries.py -v
pytest tests/unit/test_topology_fragmentation.py -v
pytest tests/integration/test_message_bus_invariants.py -v
pytest tests/unit/test_cognitive_thresholds.py -v
pytest tests/unit/test_memory_degradation.py -v

# Check coverage
pytest --cov=src/agisa_sac --cov-report=term | grep -E "orchestr|topology|message_bus|agent|memory"
```

## Verification Checklist

After creating test files:

- [ ] All imports resolve correctly
- [ ] All fixtures work
- [ ] Tests run without errors (some may need skipif for optional deps)
- [ ] Coverage increased for target modules
- [ ] Safety-critical tests document undefined behavior
- [ ] CRDT tests use memory ID comparison (strengthened)
- [ ] Decision tests document non-determinism
- [ ] MessageBus tests document no ordering guarantee

## Expected Test Results

**Initial Run (before fixing issues):**
- Some tests may fail (documenting current bugs)
- Some tests skipped (optional dependencies: ripser, voice component)
- Coverage should increase significantly

**After addressing documented issues:**
- All non-skipped tests should pass
- Coverage targets achieved
- Safety unknowns tracked as GitHub issues
