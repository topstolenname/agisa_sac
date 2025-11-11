"""Tests for EmpathyModule and CMNI tracking."""

import pytest

from agisa_sac.extensions.concord.empathy import CMNITracker, EmpathyModule
from agisa_sac.extensions.concord.circuits import CircuitActivation


def test_cmni_tracker_initialization():
    """Test CMNI tracker initializes correctly."""
    tracker = CMNITracker(window_size=50, baseline_cmni=0.3)

    assert tracker.current_cmni == 0.3
    assert len(tracker.resonance_buffer) == 0
    assert len(tracker.history) == 0


def test_cmni_tracker_update():
    """Test CMNI tracker updates with new activations."""
    import time

    tracker = CMNITracker(baseline_cmni=0.3)

    activation = CircuitActivation(
        circuit_id="L2N1",
        activation_level=0.6,
        confidence=0.8,
        context={},
        timestamp=time.time(),
    )

    new_cmni = tracker.update(activation)

    assert new_cmni > 0.3  # Should increase from baseline
    assert len(tracker.resonance_buffer) == 1


def test_cmni_tracker_rejects_wrong_circuit():
    """Test CMNI tracker only accepts L2N1 activations."""
    import time

    tracker = CMNITracker()

    activation = CircuitActivation(
        circuit_id="L2N0",  # Wrong circuit
        activation_level=0.5,
        confidence=0.8,
        context={},
        timestamp=time.time(),
    )

    with pytest.raises(ValueError):
        tracker.update(activation)


def test_cmni_tracker_trend_calculation():
    """Test CMNI trend detection."""
    import time

    tracker = CMNITracker(baseline_cmni=0.3)

    # Simulate increasing CMNI
    for i in range(20):
        activation = CircuitActivation(
            circuit_id="L2N1",
            activation_level=0.3 + i * 0.02,
            confidence=0.8,
            context={},
            timestamp=time.time(),
        )
        tracker.update(activation)

    trend = tracker.get_cmni_trend(lookback=10)
    assert trend == "increasing"


def test_cmni_tracker_stable_trend():
    """Test CMNI recognizes stable trend."""
    import time

    tracker = CMNITracker(baseline_cmni=0.4)

    # Simulate stable CMNI
    for _ in range(20):
        activation = CircuitActivation(
            circuit_id="L2N1",
            activation_level=0.4,
            confidence=0.8,
            context={},
            timestamp=time.time(),
        )
        tracker.update(activation)

    trend = tracker.get_cmni_trend(lookback=10)
    assert trend == "stable"


def test_empathy_module_initialization():
    """Test EmpathyModule initializes correctly."""
    module = EmpathyModule(resonance_gain=0.8, cmni_window=50, baseline_cmni=0.3)

    assert module.empathy_circuit.resonance_gain == 0.8
    assert module.cmni_tracker.window_size == 50
    assert module.cmni_tracker.baseline_cmni == 0.3


def test_empathy_module_process_interaction():
    """Test empathy module processes interactions and updates CMNI."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    activation = module.process_interaction(
        agent_id="agent-001", self_state=self_state, other_state=other_state
    )

    assert activation.circuit_id == "L2N1"
    assert module.cmni_tracker.current_cmni > 0


def test_empathy_module_agent_affinity():
    """Test empathy module tracks per-agent affinity."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    # Process multiple interactions with same agent
    for _ in range(5):
        module.process_interaction(
            agent_id="agent-001", self_state=self_state, other_state=other_state
        )

    affinity = module.get_agent_affinity("agent-001")
    assert affinity > 0
    assert affinity <= 1.0


def test_empathy_module_multiple_agents():
    """Test empathy module tracks multiple agents separately."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}

    # High resonance agent
    high_res_state = {"emotional_valence": 0.35, "arousal": 0.8}
    for _ in range(5):
        module.process_interaction("agent-high", self_state, high_res_state)

    # Low resonance agent
    low_res_state = {"emotional_valence": -0.5, "arousal": 0.3}
    for _ in range(5):
        module.process_interaction("agent-low", self_state, low_res_state)

    high_affinity = module.get_agent_affinity("agent-high")
    low_affinity = module.get_agent_affinity("agent-low")

    assert high_affinity > low_affinity


def test_empathy_module_capacity_report():
    """Test empathy module generates comprehensive capacity report."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    # Process several interactions
    for i in range(10):
        module.process_interaction(f"agent-{i % 3}", self_state, other_state)

    capacity = module.get_empathy_capacity()

    assert "cmni" in capacity
    assert "cmni_trend" in capacity
    assert "agent_affinities" in capacity
    assert "total_interactions" in capacity
    assert "tracked_agents" in capacity

    assert capacity["total_interactions"] == 10
    assert capacity["tracked_agents"] == 3


def test_empathy_module_threshold_check():
    """Test empathy module threshold checking."""
    module = EmpathyModule(baseline_cmni=0.45)

    # Should meet threshold
    assert module.is_empathy_threshold_met(threshold=0.4)

    # Should not meet threshold
    assert not module.is_empathy_threshold_met(threshold=0.5)


def test_empathy_module_agent_history_limit():
    """Test per-agent resonance history respects limit."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    # Process more than limit (20)
    for _ in range(30):
        module.process_interaction("agent-001", self_state, other_state)

    # Should be limited to 20
    assert len(module.agent_resonance_map["agent-001"]) == 20


def test_cmni_snapshot_creation():
    """Test CMNI snapshots are created periodically."""
    import time

    tracker = CMNITracker(baseline_cmni=0.3)

    # Create 15 activations (snapshots every 10)
    for i in range(15):
        activation = CircuitActivation(
            circuit_id="L2N1",
            activation_level=0.4,
            confidence=0.8,
            context={"iteration": i},
            timestamp=time.time(),
        )
        tracker.update(activation)

    # Should have 1 snapshot (at iteration 10)
    assert len(tracker.history) == 1

    snapshot = tracker.history[0]
    assert snapshot.cmni_score > 0
    assert len(snapshot.resonance_samples) <= 10


def test_empathy_with_emotional_context():
    """Test empathy module with emotional context amplification."""
    module = EmpathyModule()

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.35, "arousal": 0.7}
    emotional_context = {"shared_attention": 0.9, "salience": 0.8}

    activation = module.process_interaction(
        "agent-001", self_state, other_state, emotional_context
    )

    # With high shared attention, resonance should be amplified
    assert activation.activation_level > 0.4
