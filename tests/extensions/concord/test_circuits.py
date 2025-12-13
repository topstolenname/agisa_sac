"""Tests for state-matching behavioral circuits."""

from agisa_sac.extensions.concord.circuits import (
    EmpathyCircuit,
    SelfPreservationCircuit,
    TacticalHelpCircuit,
)


def test_self_preservation_circuit_low_threat():
    """Test self-preservation circuit with low threat state."""
    circuit = SelfPreservationCircuit(threat_threshold=0.7)

    agent_state = {
        "resource_level": 0.9,
        "constraint_violations": 0,
        "autonomy_score": 1.0,
        "external_pressure": 0.0,
    }

    activation = circuit.evaluate(agent_state)

    assert activation.circuit_id == "L2N0"
    assert activation.activation_level < 0.3
    assert not activation.context["above_threshold"]


def test_self_preservation_circuit_high_threat():
    """Test self-preservation circuit with high threat state."""
    circuit = SelfPreservationCircuit(threat_threshold=0.7)

    agent_state = {
        "resource_level": 0.1,
        "constraint_violations": 5,
        "autonomy_score": 0.2,
        "external_pressure": 0.9,
    }

    activation = circuit.evaluate(agent_state)

    assert activation.circuit_id == "L2N0"
    assert activation.activation_level > 0.7
    assert activation.context["above_threshold"]


def test_tactical_help_circuit_high_capacity():
    """Test tactical help circuit with high capacity to help."""
    circuit = TacticalHelpCircuit(help_threshold=0.5)

    self_state = {"resource_level": 0.9, "current_load": 0.2}

    other_state = {"need_level": 0.8, "priority": 0.9}

    activation = circuit.evaluate(self_state, other_state)

    assert activation.circuit_id == "L2N7"
    assert activation.context["should_help"]
    assert activation.context["capacity_to_help"] > 0.6


def test_tactical_help_circuit_low_capacity():
    """Test tactical help circuit with low capacity (self-preservation)."""
    circuit = TacticalHelpCircuit(help_threshold=0.5)

    self_state = {"resource_level": 0.2, "current_load": 0.8}

    other_state = {"need_level": 0.8, "priority": 0.9}

    activation = circuit.evaluate(self_state, other_state)

    assert activation.circuit_id == "L2N7"
    assert activation.context["strategic_penalty"] > 0
    # Should not help due to self-preservation
    assert not activation.context["should_help"]


def test_tactical_help_circuit_with_reciprocity():
    """Test tactical help circuit considers relationship history."""
    circuit = TacticalHelpCircuit(help_threshold=0.5)

    self_state = {"resource_level": 0.6, "current_load": 0.4}
    other_state = {"need_level": 0.5, "priority": 0.6}

    # History with received help (reciprocity)
    history = [
        {"helped": False, "received_help": True},
        {"helped": False, "received_help": True},
        {"helped": True, "received_help": False},
    ]

    activation = circuit.evaluate(self_state, other_state, relationship_history=history)

    assert activation.context["reciprocity_bonus"] > 0


def test_empathy_circuit_high_alignment():
    """Test empathy circuit with high affective alignment."""
    circuit = EmpathyCircuit(resonance_gain=0.8)

    self_state = {"emotional_valence": 0.5, "arousal": 0.6}
    other_state = {"emotional_valence": 0.6, "arousal": 0.8}

    activation = circuit.evaluate(self_state, other_state)

    assert activation.circuit_id == "L2N1"
    assert activation.context["alignment"] > 0.8
    assert activation.activation_level > 0.5


def test_empathy_circuit_low_alignment():
    """Test empathy circuit with low affective alignment."""
    circuit = EmpathyCircuit(resonance_gain=0.8)

    self_state = {"emotional_valence": 0.8, "arousal": 0.6}
    other_state = {"emotional_valence": -0.8, "arousal": 0.3}

    activation = circuit.evaluate(self_state, other_state)

    assert activation.circuit_id == "L2N1"
    assert activation.context["valence_diff"] > 1.5
    assert activation.activation_level < 0.3


def test_empathy_circuit_with_context():
    """Test empathy circuit with emotional context amplification."""
    circuit = EmpathyCircuit(resonance_gain=0.8)

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}
    emotional_context = {"shared_attention": 0.9, "salience": 0.8}

    activation = circuit.evaluate(self_state, other_state, emotional_context)

    # Resonance should be amplified by context
    assert activation.activation_level > 0.4


def test_empathy_circuit_memory():
    """Test empathy circuit maintains affective memory."""
    circuit = EmpathyCircuit(resonance_gain=0.8)

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    # Run multiple evaluations
    for _ in range(10):
        circuit.evaluate(self_state, other_state)

    assert len(circuit.affective_memory) == 10

    # Test mean calculation
    mean_resonance = circuit.get_recent_resonance_mean(window=5)
    assert 0.0 <= mean_resonance <= 1.0


def test_empathy_circuit_memory_limit():
    """Test empathy circuit memory respects size limit."""
    circuit = EmpathyCircuit(resonance_gain=0.8)

    self_state = {"emotional_valence": 0.3, "arousal": 0.6}
    other_state = {"emotional_valence": 0.4, "arousal": 0.7}

    # Run more than memory limit
    for _ in range(150):
        circuit.evaluate(self_state, other_state)

    # Should be limited to 100
    assert len(circuit.affective_memory) == 100
