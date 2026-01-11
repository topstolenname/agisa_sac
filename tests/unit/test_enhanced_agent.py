"""Minimal focused tests for EnhancedAgent (agents/agent.py)."""

from unittest.mock import MagicMock, Mock

import pytest

from agisa_sac.agents.agent import EnhancedAgent
from agisa_sac.utils.message_bus import MessageBus


@pytest.fixture
def basic_personality():
    """Numeric personality for cognitive engine."""
    return {
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.5,
        "agreeableness": 0.6,
        "neuroticism": 0.3,
    }


@pytest.fixture
def mock_message_bus():
    """Mock message bus."""
    return MagicMock(spec=MessageBus)


class TestInitialization:
    """Test agent initialization paths."""

    def test_basic_init(self, basic_personality):
        """Test basic initialization works."""
        agent = EnhancedAgent(
            agent_id="test_001",
            personality=basic_personality,
            capacity=50,
            use_semantic=False,
        )
        assert agent.agent_id == "test_001"
        assert agent.memory is not None
        assert agent.cognitive is not None

    def test_init_with_message_bus(self, basic_personality, mock_message_bus):
        """Test init with message bus."""
        agent = EnhancedAgent(
            agent_id="test_002",
            personality=basic_personality,
            message_bus=mock_message_bus,
        )
        assert agent.message_bus == mock_message_bus

    def test_init_with_prebuilt_components(self, basic_personality):
        """Test init with pre-built components."""
        mock_mem = MagicMock()
        mock_cog = MagicMock()
        agent = EnhancedAgent(
            agent_id="test_003",
            personality=basic_personality,
            memory=mock_mem,
            cognitive=mock_cog,
            add_initial_memory=False,
        )
        assert agent.memory is mock_mem
        assert agent.cognitive is mock_cog


class TestSimulationStep:
    """Test simulation_step method."""

    def test_simulation_step_runs(self, basic_personality):
        """Test simulation step executes."""
        agent = EnhancedAgent(
            agent_id="sim_test",
            personality=basic_personality,
            use_semantic=False,
        )
        agent.cognitive.decide = Mock(return_value={"action": "test"})
        agent.memory.get_current_focus_theme = Mock(return_value="test_theme")
        agent.temporal_resonance.detect_echo = Mock(return_value=[])

        result = agent.simulation_step(
            situational_entropy=0.5,
            peer_influence={"peer1": 0.3},
            query="test query",
        )

        assert result == {"action": "test"}
        agent.cognitive.decide.assert_called_once()


class TestCheckResonance:
    """Test check_resonance method."""

    def test_check_resonance_no_echoes(self, basic_personality):
        """Test resonance check with no echoes."""
        agent = EnhancedAgent(
            agent_id="res_test",
            personality=basic_personality,
            use_semantic=False,
        )
        agent.temporal_resonance.detect_echo = Mock(return_value=[])
        agent.memory.get_current_focus_theme = Mock(return_value="theme")

        # Should not raise
        agent.check_resonance()

    def test_check_resonance_with_high_echo_triggers_satori(self, basic_personality):
        """Test high resonance triggers satori."""
        agent = EnhancedAgent(
            agent_id="satori_test",
            personality=basic_personality,
            use_semantic=False,
        )
        high_echo = {
            "similarity": 0.95,
            "delta_t": 100.0,
            "previous_manifestation_timestamp": 12345.0,
            "previous_manifestation_theme": "past_theme",
        }
        agent.temporal_resonance.detect_echo = Mock(return_value=[high_echo])
        agent.memory.get_current_focus_theme = Mock(return_value="current_theme")
        agent.reflexivity_layer.force_deep_reflection = Mock()

        agent.check_resonance()

        # Should trigger deep reflection
        agent.reflexivity_layer.force_deep_reflection.assert_called_once()
        assert agent.last_reflection_trigger is not None


class TestSerialization:
    """Test serialization."""

    def test_to_dict_has_version(self, basic_personality):
        """Test to_dict includes version."""
        agent = EnhancedAgent(
            agent_id="ser_test",
            personality=basic_personality,
            use_semantic=False,
        )
        data = agent.to_dict()
        assert "version" in data
        assert "agent_id" in data

    def test_to_dict_has_component_states(self, basic_personality):
        """Test to_dict includes component states."""
        agent = EnhancedAgent(
            agent_id="ser_test2",
            personality=basic_personality,
            use_semantic=False,
        )
        data = agent.to_dict()
        assert "memory_state" in data
        assert "cognitive_state" in data
        assert "voice_state" in data
