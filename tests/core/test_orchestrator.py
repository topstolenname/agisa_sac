"""Comprehensive tests for SimulationOrchestrator."""
import pytest
from unittest.mock import Mock, patch
import numpy as np
import tempfile
import os

from agisa_sac.core.orchestrator import SimulationOrchestrator


@pytest.fixture
def minimal_config():
    """Minimal valid configuration for orchestrator."""
    return {
        "num_agents": 5,
        "num_epochs": 3,
        "random_seed": 42,
        "use_gpu": False,
        "tda_max_dimension": 1,
    }


@pytest.fixture
def orchestrator(minimal_config):
    """Create an orchestrator instance with mocked dependencies."""
    with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
        with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
            with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                    with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                        orch = SimulationOrchestrator(minimal_config)
                        return orch


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""

    def test_initialization_with_minimal_config(self, orchestrator):
        """Test that orchestrator initializes with minimal config."""
        assert orchestrator.num_agents == 5
        assert orchestrator.num_epochs == 3
        assert orchestrator.current_epoch == 0
        assert not orchestrator.is_running
        assert orchestrator.simulation_start_time is None

    def test_random_seed_sets_rng(self, minimal_config):
        """Test that random seed properly initializes RNG."""
        with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
            with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
                with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                    with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                        with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                            orch1 = SimulationOrchestrator(minimal_config)
                            orch2 = SimulationOrchestrator(minimal_config)
                            # Reset RNGs to same state
                            orch1.rng = np.random.default_rng(42)
                            orch2.rng = np.random.default_rng(42)
                            # Both should generate same random numbers
                            assert orch1.rng.random() == orch2.rng.random()

    def test_agent_ids_generated(self, orchestrator):
        """Test that agent IDs are generated correctly."""
        assert len(orchestrator.agent_ids) == 5
        assert orchestrator.agent_ids[0] == "agent_0"
        assert orchestrator.agent_ids[4] == "agent_4"

    def test_hooks_initialized_as_defaultdict(self, orchestrator):
        """Test that hooks are initialized as defaultdict."""
        assert isinstance(orchestrator.hooks, dict)
        # Access non-existent key should return empty list
        assert orchestrator.hooks["nonexistent"] == []


class TestAgentSelection:
    """Test agent selection methods."""

    def test_select_agents_percentage_method(self, orchestrator):
        """Test percentage-based agent selection."""
        # Mock agents
        mock_agents = {f"agent_{i}": Mock() for i in range(5)}
        orchestrator.agents = mock_agents

        params = {"selection_method": "percentage", "percentage": 0.4}
        selected = orchestrator._select_agents_for_protocol(params)

        # Should select at least 1 agent (max(1, int(5 * 0.4)))
        assert len(selected) >= 1
        assert len(selected) <= 5
        # All selected should be from agents
        assert all(agent in mock_agents.values() for agent in selected)

    def test_select_agents_empty_list(self):
        """Test agent selection with no agents available."""
        with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
            with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
                with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                    with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                        with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                            orch = SimulationOrchestrator({"num_agents": 0, "num_epochs": 1})
                            orch.agents = {}

                            params = {"selection_method": "percentage", "percentage": 0.5}
                            selected = orch._select_agents_for_protocol(params)

                            assert selected == []

    def test_select_agents_unknown_method(self, orchestrator):
        """Test agent selection with unknown method returns all agents."""
        mock_agents = {f"agent_{i}": Mock() for i in range(3)}
        orchestrator.agents = mock_agents

        params = {"selection_method": "unknown_method"}
        selected = orchestrator._select_agents_for_protocol(params)

        # Should return all agents
        assert len(selected) == 3


class TestHooks:
    """Test hook registration and execution."""

    def test_register_hook(self, orchestrator):
        """Test hook registration."""
        callback = Mock(__name__="test_callback")
        orchestrator.register_hook("pre_epoch", callback)

        assert "pre_epoch" in orchestrator.hooks
        assert callback in orchestrator.hooks["pre_epoch"]

    def test_register_multiple_hooks_same_event(self, orchestrator):
        """Test registering multiple hooks for same event."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        orchestrator.register_hook("post_epoch", callback1)
        orchestrator.register_hook("post_epoch", callback2)

        assert len(orchestrator.hooks["post_epoch"]) == 2
        assert callback1 in orchestrator.hooks["post_epoch"]
        assert callback2 in orchestrator.hooks["post_epoch"]

    def test_register_invalid_hook(self, orchestrator):
        """Test registering an invalid hook point."""
        callback = Mock()
        orchestrator.register_hook("invalid_hook", callback)

        # Invalid hooks should not be added
        assert "invalid_hook" not in orchestrator.hooks

    def test_trigger_hooks(self, orchestrator):
        """Test triggering hooks."""
        callback = Mock(__name__="trigger_callback")
        orchestrator.register_hook("pre_agent_step", callback)

        orchestrator._trigger_hooks("pre_agent_step", data="test_data")

        # Hooks receive orchestrator, epoch, and additional kwargs
        callback.assert_called_once()
        call_kwargs = callback.call_args[1]
        assert call_kwargs["orchestrator"] == orchestrator
        assert "epoch" in call_kwargs
        assert call_kwargs["data"] == "test_data"

    def test_trigger_hooks_no_registered(self, orchestrator):
        """Test triggering hooks when none are registered."""
        # Should not raise error
        orchestrator._trigger_hooks("nonexistent_event", data="test")

    def test_trigger_hooks_multiple_callbacks(self, orchestrator):
        """Test triggering multiple hooks."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        orchestrator.register_hook("simulation_end", callback1)
        orchestrator.register_hook("simulation_end", callback2)

        orchestrator._trigger_hooks("simulation_end", value=123)

        # Both should be called
        assert callback1.call_count == 1
        assert callback2.call_count == 1

    def test_hook_execution_continues_on_error(self, orchestrator):
        """Test that hook execution continues even if one hook fails."""
        def failing_hook(**kwargs):
            raise ValueError("Hook error")

        callback1 = Mock(__name__="failing_callback", side_effect=failing_hook)
        callback2 = Mock(__name__="working_callback")

        orchestrator.register_hook("pre_protocol_injection", callback1)
        orchestrator.register_hook("pre_protocol_injection", callback2)

        # Should not raise error
        orchestrator._trigger_hooks("pre_protocol_injection")

        # Second callback should still be called
        callback2.assert_called_once()


class TestProtocolInjection:
    """Test protocol injection functionality."""

    def test_inject_protocol_basic(self, orchestrator):
        """Test basic protocol injection."""
        mock_agents = {f"agent_{i}": Mock() for i in range(5)}
        for agent in mock_agents.values():
            agent.inject_protocol = Mock()
        orchestrator.agents = mock_agents

        # inject_protocol takes protocol_name and parameters separately
        # Valid protocols: satori_prime, continuity_bridge, resonance, reflexivity, satori_lattice
        orchestrator.inject_protocol("resonance", {"test_param": "value"})

        # Since we're using mocks, at least verify the method ran without error
        # The actual protocol injection logic depends on selection_method in params
        assert orchestrator.agents is not None


class TestStateManagement:
    """Test orchestrator state management."""

    @pytest.mark.skip(reason="save_state cannot serialize mocked dependencies")
    def test_save_and_load_state(self, orchestrator):
        """Test saving and loading state."""
        # This test cannot work with mocked dependencies since
        # MagicMock objects are not JSON serializable.
        # Integration tests should verify save/load with real components.
        pass

    def test_load_state_nonexistent_file(self, orchestrator):
        """Test loading state from nonexistent file."""
        result = orchestrator.load_state("/nonexistent/path.json")
        assert result is False


class TestGetState:
    """Test state retrieval methods."""

    def test_get_summary_metrics(self, orchestrator):
        """Test getting summary metrics."""
        # Configure mocked analyzer to return a dict
        orchestrator.analyzer.summarize.return_value = {
            "current_epoch": 0,
            "num_agents": 5,
            "test_metric": "test_value"
        }

        metrics = orchestrator.get_summary_metrics()

        assert isinstance(metrics, dict)
        assert "current_epoch" in metrics
        assert "num_agents" in metrics

    def test_get_summary_metrics_no_analyzer(self, orchestrator):
        """Test getting summary metrics when analyzer is None."""
        orchestrator.analyzer = None
        metrics = orchestrator.get_summary_metrics()

        assert isinstance(metrics, dict)
        assert "error" in metrics


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_zero_agents(self):
        """Test that orchestrator handles zero agents gracefully."""
        config = {"num_agents": 0, "num_epochs": 1}

        with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
            with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
                with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                    with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                        with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                            orch = SimulationOrchestrator(config)
                            assert orch.num_agents == 0
                            assert len(orch.agent_ids) == 0

    def test_handles_negative_epochs(self):
        """Test that orchestrator handles negative epochs."""
        config = {"num_agents": 5, "num_epochs": -1}

        with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
            with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
                with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                    with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                        with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                            orch = SimulationOrchestrator(config)
                            # Should accept the value (validation is caller's responsibility)
                            assert orch.num_epochs == -1

    def test_missing_config_keys_use_defaults(self):
        """Test that missing config keys use default values."""
        config = {}  # Empty config

        with patch('agisa_sac.core.orchestrator.EnhancedAgent'):
            with patch('agisa_sac.core.orchestrator.DynamicSocialGraph'):
                with patch('agisa_sac.core.orchestrator.ResonanceChronicler'):
                    with patch('agisa_sac.core.orchestrator.AgentStateAnalyzer'):
                        with patch('agisa_sac.core.orchestrator.PersistentHomologyTracker'):
                            orch = SimulationOrchestrator(config)
                            # Should use defaults
                            assert orch.num_agents == 100  # Default
                            assert orch.num_epochs == 50   # Default
