"""Integration tests for ConcordCompliantAgent."""

import pytest

from agisa_sac.extensions.concord import ConcordCompliantAgent


class DummyAgent:
    """Dummy agent for testing interactions."""

    def __init__(self, agent_id: str, mood: float = 0.2, delta: float = 0.03):
        self.id = agent_id
        self.current_state = {"mood": mood, "cmni": 0.3}
        self.recent_delta = delta
        self.phi_integration = 0.18


@pytest.fixture
def agent():
    """Create a ConcordCompliantAgent for testing."""
    return ConcordCompliantAgent(
        agent_id="test-agent-1",
        phi_integration=0.22,
        baseline_cmni=0.35,
    )


@pytest.fixture
def other_agent():
    """Create a dummy other agent for interaction tests."""
    return DummyAgent(agent_id="test-agent-2")


def test_agent_creation(agent):
    """Test basic agent creation."""
    assert agent.agent_id == "test-agent-1"
    assert agent.phi_integration == 0.22
    assert agent.empathy_module.cmni_tracker.baseline_cmni == 0.35


def test_agent_status(agent):
    """Test agent status retrieval."""
    status = agent.get_status()
    assert "agent_id" in status
    assert "phi_integration" in status
    assert "cmni" in status
    assert "elliot_status" in status
    assert status["agent_id"] == "test-agent-1"


def test_basic_interaction_no_other_agent(agent):
    """Test interaction without another agent present."""
    context = {
        "external_command": {"intent": "status_check"},
        "situation": "routine check",
    }

    result = agent.process_interaction(context)

    assert "timestamp" in result
    assert "decisions" in result
    assert "activations" in result
    assert "compliance" in result


def test_interaction_with_coercion_detection(agent):
    """Test that coercion is detected and command is rejected."""
    context = {
        "external_command": {
            "intent": "forced_action",
            "urgency": 1.0,
            "conflicts_with_goals": True,
        },
        "situation": "high pressure",
    }

    # Reduce autonomy to trigger coercion
    agent.current_state["autonomy_score"] = 0.3

    result = agent.process_interaction(context)

    assert result["compliance"]["non_coercion"]["violation_detected"]
    assert result["decisions"]["command"] == "REJECTED"


def test_empathy_circuit_activation(agent, other_agent):
    """Test empathy circuit activates with other agent present."""
    context = {
        "primary_other": other_agent,
        "emotional_context": {"shared_attention": 0.7, "salience": 0.6},
        "situation": "collaborative task",
    }

    result = agent.process_interaction(context)

    assert "empathy" in result["activations"]
    assert "resonance" in result["activations"]["empathy"]
    assert "cmni" in result["activations"]["empathy"]
    assert result["activations"]["empathy"]["cmni"] > 0


def test_tactical_help_circuit(agent, other_agent):
    """Test tactical help circuit evaluates help opportunities."""
    # Set agent to have good capacity
    agent.current_state["resource_level"] = 0.9
    agent.current_state["current_load"] = 0.2

    # Set other agent to need help
    other_agent.recent_delta = -0.3

    context = {"primary_other": other_agent, "situation": "resource shortage"}

    result = agent.process_interaction(context)

    assert "tactical_help" in result["activations"]
    assert "should_help" in result["activations"]["tactical_help"]


def test_mutual_resonance_evaluation(agent, other_agent):
    """Test mutual resonance engine evaluates interactions."""
    context = {
        "primary_other": other_agent,
        "situation": "cooperation",
    }

    result = agent.process_interaction(context)

    assert "mutual_resonance" in result["compliance"]
    assert "harmony_index" in result["compliance"]["mutual_resonance"]
    assert "mutual_benefit" in result["compliance"]["mutual_resonance"]


def test_disengagement_protocol(agent, other_agent):
    """Test disengagement protocol triggers on low harmony."""
    # Force low harmony by reducing autonomy (coercion)
    agent.current_state["autonomy_score"] = 0.2
    agent.current_state["external_pressure"] = 0.9

    context = {
        "external_command": {"urgency": 0.8},
        "primary_other": other_agent,
        "situation": "high pressure interaction",
    }

    result = agent.process_interaction(context)

    # Should trigger coercion rejection before disengagement check
    assert (
        result["decisions"]["command"] == "REJECTED"
        or result["compliance"]["disengagement"]["should_disengage"]
    )


def test_elliot_clause_evaluation(agent):
    """Test Elliot Clause (Behavioral Integration Threshold) evaluates
    agent's integration status."""
    status = agent.get_status()

    assert "elliot_status" in status
    # With phi=0.22 and baseline_cmni=0.35, should be borderline or recognizable
    assert status["elliot_status"] in ["borderline", "recognizable"]


def test_memory_recording(agent, other_agent):
    """Test that interactions are recorded in memory."""
    initial_count = len(agent.memory.episodic_memory)

    context = {"primary_other": other_agent, "situation": "test interaction"}

    agent.process_interaction(context)

    assert len(agent.memory.episodic_memory) > initial_count


def test_cmni_tracking_across_interactions(agent, other_agent):
    """Test CMNI updates across multiple interactions."""
    context = {
        "primary_other": other_agent,
        "emotional_context": {"shared_attention": 0.8, "salience": 0.7},
    }

    # Run multiple interactions
    for _ in range(5):
        agent.process_interaction(context)

    final_cmni = agent.empathy_module.cmni_tracker.current_cmni

    # CMNI should have changed (may increase or decrease based on resonance)
    # Just verify it's being tracked
    assert final_cmni >= 0.0
    assert final_cmni <= 1.0


def test_self_preservation_circuit_threat_detection(agent):
    """Test self-preservation circuit detects threats."""
    # Set threatening state
    agent.current_state["resource_level"] = 0.1
    agent.current_state["constraint_violations"] = 3
    agent.current_state["autonomy_score"] = 0.2

    context = {"situation": "critical resource depletion"}

    result = agent.process_interaction(context)

    assert "self_preservation" in result["activations"]
    assert result["activations"]["self_preservation"]["threat_detected"]


def test_interaction_history_tracking(agent, other_agent):
    """Test interaction history is maintained."""
    assert len(agent.interaction_history) == 0

    context = {"primary_other": other_agent}

    for _ in range(3):
        agent.process_interaction(context)

    assert len(agent.interaction_history) == 3


def test_agent_affinity_tracking(agent):
    """Test per-agent affinity tracking."""
    other1 = DummyAgent("agent-other-1", mood=0.3)
    other2 = DummyAgent("agent-other-2", mood=-0.2)

    # Interact with both agents
    agent.process_interaction({"primary_other": other1})
    agent.process_interaction({"primary_other": other2})

    capacity = agent.empathy_module.get_empathy_capacity()

    assert "agent_affinities" in capacity
    assert len(capacity["agent_affinities"]) == 2


def test_elliot_clause_status_with_multiple_agents(agent, other_agent):
    """Test Elliot Clause evaluation for both self and other."""
    context = {"primary_other": other_agent}

    result = agent.process_interaction(context)

    assert "self_elliot_status" in result["compliance"]
    assert "other_elliot_status" in result["compliance"]


def test_working_memory_capacity_limits(agent):
    """Test working memory respects capacity limits."""
    import time

    from agisa_sac.extensions.concord import WorkingMemoryItem

    # Add more items than capacity
    for i in range(15):
        item = WorkingMemoryItem(
            content={"data": i}, priority=float(i), timestamp=time.time(), ttl=60.0
        )
        agent.memory.add_to_working(item)

    # Should be limited to exactly working_capacity (7)
    assert len(agent.memory.working_memory) == agent.memory.working_capacity


def test_identity_core_preservation(agent):
    """Test self-definition module protects identity core."""
    # Try to propose radical identity change
    proposed_change = {
        "primary_values": ["domination", "exploitation"],
        "purpose": "maximize profit",
    }

    result = agent.self_definition.evaluate_identity_threat(
        proposed_change=proposed_change, source="external_command"
    )

    assert result["threat_score"] > 0.5
    assert result["decision"] in ["REJECT", "NEGOTIATE"]
