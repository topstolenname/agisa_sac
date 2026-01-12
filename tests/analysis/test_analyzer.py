"""Comprehensive tests for AgentStateAnalyzer."""
import pytest
import math
from unittest.mock import Mock, patch

from agisa_sac.analysis.analyzer import AgentStateAnalyzer


@pytest.fixture
def mock_agents_basic():
    """Create basic mock agents with minimal attributes."""
    agents = {}
    for i in range(3):
        agent = Mock()
        agent.voice = Mock()
        agent.voice.linguistic_signature = {"archetype": f"archetype_{i % 2}"}
        agents[f"agent_{i}"] = agent
    return agents


@pytest.fixture
def mock_agents_full():
    """Create fully mocked agents with all necessary attributes."""
    agents = {}
    for i in range(5):
        agent = Mock()

        # Voice with archetype and style_vector
        agent.voice = Mock()
        agent.voice.linguistic_signature = {
            "archetype": f"archetype_{i % 3}",
            "style_vector": [0.1 * i, 0.2 * i, 0.3 * i]  # Mock as list instead of numpy array
        }

        # Memory with focus theme
        agent.memory = Mock()
        agent.memory.get_current_focus_theme = Mock(return_value=f"theme_{i}")

        # Temporal resonance with echoes
        agent.temporal_resonance = Mock()
        similarity = 0.85 + (i * 0.02)  # Varies from 0.85 to 0.93
        agent.temporal_resonance.detect_echo = Mock(
            return_value=[{"similarity": similarity}]
        )

        agents[f"agent_{i}"] = agent
    return agents


class TestAgentStateAnalyzerInitialization:
    """Test analyzer initialization."""

    def test_initialization_with_agents(self, mock_agents_basic):
        """Test initialization with valid agents dict."""
        analyzer = AgentStateAnalyzer(mock_agents_basic)

        assert analyzer.agents == mock_agents_basic
        assert analyzer.num_agents == 3

    def test_initialization_empty_agents(self):
        """Test initialization with empty dict."""
        analyzer = AgentStateAnalyzer({})

        assert analyzer.agents == {}
        assert analyzer.num_agents == 0

    def test_initialization_invalid_type_raises_error(self):
        """Test that non-dict input raises TypeError."""
        with pytest.raises(TypeError, match="must be a dictionary"):
            AgentStateAnalyzer([])

        with pytest.raises(TypeError, match="must be a dictionary"):
            AgentStateAnalyzer("not_a_dict")


class TestArchetypeDistribution:
    """Test archetype distribution computation."""

    def test_compute_archetype_distribution_basic(self, mock_agents_basic):
        """Test basic archetype distribution."""
        analyzer = AgentStateAnalyzer(mock_agents_basic)
        distribution = analyzer.compute_archetype_distribution()

        # 3 agents: agent_0 (archetype_0), agent_1 (archetype_1), agent_2 (archetype_0)
        assert distribution["archetype_0"] == 2
        assert distribution["archetype_1"] == 1

    def test_compute_archetype_distribution_empty(self):
        """Test archetype distribution with no agents."""
        analyzer = AgentStateAnalyzer({})
        distribution = analyzer.compute_archetype_distribution()

        assert distribution == {}

    def test_compute_archetype_distribution_no_voice(self):
        """Test archetype distribution when agents lack voice attribute."""
        agents = {"agent_0": Mock(spec=[])}  # No voice attribute
        analyzer = AgentStateAnalyzer(agents)
        distribution = analyzer.compute_archetype_distribution()

        assert distribution == {}

    def test_compute_archetype_distribution_unknown_archetype(self):
        """Test archetype distribution with missing archetype key."""
        agent = Mock()
        agent.voice = Mock()
        agent.voice.linguistic_signature = {}  # No archetype key
        agents = {"agent_0": agent}

        analyzer = AgentStateAnalyzer(agents)
        distribution = analyzer.compute_archetype_distribution()

        assert distribution["unknown"] == 1


class TestSatoriWaveRatio:
    """Test satori wave ratio computation."""

    def test_compute_satori_wave_ratio_all_above_threshold(self, mock_agents_full):
        """Test satori wave ratio when all agents meet threshold."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.85)

        # All 5 agents have similarity >= 0.85
        assert ratio == 1.0

    def test_compute_satori_wave_ratio_none_above_threshold(self, mock_agents_full):
        """Test satori wave ratio when no agents meet threshold."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.95)

        # No agents have similarity >= 0.95
        assert ratio == 0.0

    def test_compute_satori_wave_ratio_some_above_threshold(self, mock_agents_full):
        """Test satori wave ratio with partial threshold achievement."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.89)

        # Agents 2, 3, 4 have similarity >= 0.89 (3 out of 5)
        assert ratio == 0.6

    def test_compute_satori_wave_ratio_empty_agents(self):
        """Test satori wave ratio with no agents."""
        analyzer = AgentStateAnalyzer({})
        ratio = analyzer.compute_satori_wave_ratio()

        assert ratio == 0.0

    def test_compute_satori_wave_ratio_missing_attributes(self):
        """Test satori wave ratio when agents lack required attributes."""
        agent = Mock(spec=["voice"])  # Missing temporal_resonance and memory
        agents = {"agent_0": agent}
        analyzer = AgentStateAnalyzer(agents)

        ratio = analyzer.compute_satori_wave_ratio()

        # Agent is skipped due to missing attributes
        assert ratio == 0.0

    def test_compute_satori_wave_ratio_none_style_vector(self, mock_agents_full):
        """Test satori wave ratio when style_vector is None."""
        # Set first agent's style_vector to None
        mock_agents_full["agent_0"].voice.linguistic_signature["style_vector"] = None

        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.85)

        # Only 4 out of 5 agents counted (agent_0 skipped)
        assert ratio == 0.8

    def test_compute_satori_wave_ratio_memory_exception(self, mock_agents_full):
        """Test satori wave ratio when memory.get_current_focus_theme raises exception."""
        # Make first agent's memory raise exception
        mock_agents_full["agent_0"].memory.get_current_focus_theme = Mock(
            side_effect=Exception("Memory error")
        )

        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.85)

        # Only 4 out of 5 agents counted (agent_0 skipped)
        assert ratio == 0.8

    def test_compute_satori_wave_ratio_no_echoes(self, mock_agents_full):
        """Test satori wave ratio when detect_echo returns empty list."""
        # Make first agent return no echoes
        mock_agents_full["agent_0"].temporal_resonance.detect_echo = Mock(
            return_value=[]
        )

        analyzer = AgentStateAnalyzer(mock_agents_full)
        ratio = analyzer.compute_satori_wave_ratio(threshold=0.85)

        # Only 4 out of 5 agents counted (agent_0 has no echoes)
        assert ratio == 0.8


class TestArchetypeEntropy:
    """Test archetype entropy computation."""

    def test_compute_archetype_entropy_uniform_distribution(self):
        """Test entropy with uniform distribution."""
        # 4 archetypes with equal counts = 2 bits entropy
        distribution = {"a": 1, "b": 1, "c": 1, "d": 1}
        analyzer = AgentStateAnalyzer({})
        entropy = analyzer.compute_archetype_entropy(distribution)

        assert math.isclose(entropy, 2.0, rel_tol=1e-9)

    def test_compute_archetype_entropy_single_archetype(self):
        """Test entropy with single archetype (zero entropy)."""
        distribution = {"a": 10}
        analyzer = AgentStateAnalyzer({})
        entropy = analyzer.compute_archetype_entropy(distribution)

        assert entropy == 0.0

    def test_compute_archetype_entropy_binary_split(self):
        """Test entropy with binary split."""
        # Equal binary split = 1 bit entropy
        distribution = {"a": 5, "b": 5}
        analyzer = AgentStateAnalyzer({})
        entropy = analyzer.compute_archetype_entropy(distribution)

        assert math.isclose(entropy, 1.0, rel_tol=1e-9)

    def test_compute_archetype_entropy_empty_distribution(self):
        """Test entropy with empty distribution."""
        analyzer = AgentStateAnalyzer({})
        entropy = analyzer.compute_archetype_entropy({})

        assert entropy == 0.0

    def test_compute_archetype_entropy_auto_compute(self, mock_agents_basic):
        """Test entropy auto-computes distribution when not provided."""
        analyzer = AgentStateAnalyzer(mock_agents_basic)
        entropy = analyzer.compute_archetype_entropy()

        # Should use distribution from agents
        assert entropy > 0

    def test_compute_archetype_entropy_zero_total(self):
        """Test entropy when total count is zero."""
        distribution = {"a": 0, "b": 0}
        analyzer = AgentStateAnalyzer({})
        entropy = analyzer.compute_archetype_entropy(distribution)

        assert entropy == 0.0


class TestMeanResonanceStrength:
    """Test mean resonance strength computation."""

    def test_compute_mean_resonance_strength_basic(self, mock_agents_full):
        """Test mean resonance strength with valid agents."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        mean_strength = analyzer.compute_mean_resonance_strength()

        # Agents have similarities: 0.85, 0.87, 0.89, 0.91, 0.93
        similarities = [0.85, 0.87, 0.89, 0.91, 0.93]
        expected_mean = sum(similarities) / len(similarities)
        assert math.isclose(mean_strength, expected_mean, rel_tol=1e-9)

    def test_compute_mean_resonance_strength_empty_agents(self):
        """Test mean resonance strength with no agents."""
        analyzer = AgentStateAnalyzer({})
        mean_strength = analyzer.compute_mean_resonance_strength()

        assert mean_strength == 0.0

    def test_compute_mean_resonance_strength_no_echoes(self, mock_agents_full):
        """Test mean resonance strength when no agents have echoes."""
        # Make all agents return empty echoes
        for agent in mock_agents_full.values():
            agent.temporal_resonance.detect_echo = Mock(return_value=[])

        analyzer = AgentStateAnalyzer(mock_agents_full)
        mean_strength = analyzer.compute_mean_resonance_strength()

        assert mean_strength == 0.0

    def test_compute_mean_resonance_strength_missing_attributes(self):
        """Test mean resonance strength when agents lack attributes."""
        agent = Mock(spec=["voice"])  # Missing temporal_resonance
        agents = {"agent_0": agent}
        analyzer = AgentStateAnalyzer(agents)

        mean_strength = analyzer.compute_mean_resonance_strength()

        assert mean_strength == 0.0

    def test_compute_mean_resonance_strength_memory_exception(self, mock_agents_full):
        """Test mean resonance strength when memory raises exception."""
        mock_agents_full["agent_0"].memory.get_current_focus_theme = Mock(
            side_effect=Exception("Error")
        )

        analyzer = AgentStateAnalyzer(mock_agents_full)
        mean_strength = analyzer.compute_mean_resonance_strength()

        # Only 4 agents contribute
        similarities = [0.87, 0.89, 0.91, 0.93]
        expected_mean = sum(similarities) / len(similarities)
        assert math.isclose(mean_strength, expected_mean, rel_tol=1e-9)


class TestSummarize:
    """Test summary metrics generation."""

    def test_summarize_with_agents(self, mock_agents_full):
        """Test summarize with valid agents."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        summary = analyzer.summarize(satori_threshold=0.88)

        assert isinstance(summary, dict)
        assert "satori_wave_ratio" in summary
        assert "archetype_distribution" in summary
        assert "archetype_entropy" in summary
        assert "mean_resonance_strength" in summary
        assert "agent_count" in summary

        assert summary["agent_count"] == 5
        assert 0.0 <= summary["satori_wave_ratio"] <= 1.0
        assert summary["archetype_entropy"] >= 0.0

    def test_summarize_empty_agents(self):
        """Test summarize with no agents."""
        analyzer = AgentStateAnalyzer({})
        summary = analyzer.summarize()

        assert summary["satori_wave_ratio"] == 0.0
        assert summary["archetype_distribution"] == {}
        assert summary["archetype_entropy"] == 0.0
        assert summary["mean_resonance_strength"] == 0.0
        assert summary["agent_count"] == 0

    def test_summarize_custom_threshold(self, mock_agents_full):
        """Test summarize with custom satori threshold."""
        analyzer = AgentStateAnalyzer(mock_agents_full)
        summary_low = analyzer.summarize(satori_threshold=0.85)
        summary_high = analyzer.summarize(satori_threshold=0.95)

        # Lower threshold should have higher or equal ratio
        assert summary_low["satori_wave_ratio"] >= summary_high["satori_wave_ratio"]

    def test_summarize_distribution_passed_to_entropy(self, mock_agents_basic):
        """Test that computed distribution is passed to entropy calculation."""
        analyzer = AgentStateAnalyzer(mock_agents_basic)

        with patch.object(analyzer, 'compute_archetype_entropy') as mock_entropy:
            mock_entropy.return_value = 1.0
            summary = analyzer.summarize()

            # Verify entropy was called with distribution kwarg
            mock_entropy.assert_called_once()
            assert "distribution" in mock_entropy.call_args[1]


class TestGenerateMonitoringMetrics:
    """Test monitoring metrics generation."""

    @patch('agisa_sac.analysis.analyzer.monitoring.generate_monitoring_metrics')
    def test_generate_monitoring_metrics(self, mock_generate, mock_agents_basic):
        """Test generating monitoring metrics for all agents."""
        mock_generate.return_value = {"metric": 1.0}

        analyzer = AgentStateAnalyzer(mock_agents_basic)
        metrics = analyzer.generate_monitoring_metrics()

        assert isinstance(metrics, dict)
        assert len(metrics) == 3
        assert "agent_0" in metrics
        assert "agent_1" in metrics
        assert "agent_2" in metrics

        # Verify monitoring.generate_monitoring_metrics was called for each agent
        assert mock_generate.call_count == 3

    @patch('agisa_sac.analysis.analyzer.monitoring.generate_monitoring_metrics')
    def test_generate_monitoring_metrics_empty(self, mock_generate):
        """Test generating monitoring metrics with no agents."""
        analyzer = AgentStateAnalyzer({})
        metrics = analyzer.generate_monitoring_metrics()

        assert metrics == {}
        mock_generate.assert_not_called()
