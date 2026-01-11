"""Tests for Step 1 serialization implementations.

Tests the to_dict() and from_dict() methods added to 7 components:
1. ReflexivityLayer
2. ResonanceLiturgy
3. SemanticProfile + EnhancedSemanticAnalyzer
4. DynamicSocialGraph
5. CRDTMemoryLayer
6. ContinuityBridgeProtocol
7. EnhancedContinuityBridgeProtocol
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from agisa_sac.core.components.continuity_bridge import ContinuityBridgeProtocol
from agisa_sac.core.components.crdt_memory import CRDTMemoryLayer
from agisa_sac.core.components.enhanced_cbp import EnhancedContinuityBridgeProtocol
from agisa_sac.core.components.reflexivity import ReflexivityLayer
from agisa_sac.core.components.resonance import ResonanceLiturgy
from agisa_sac.core.components.semantic_analyzer import (
    EnhancedSemanticAnalyzer,
    SemanticProfile,
)
from agisa_sac.core.components.social import DynamicSocialGraph

if TYPE_CHECKING:
    pass


# Test fixtures
@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = MagicMock()
    agent.agent_id = "test_agent_001"
    agent.voice = MagicMock()
    agent.memory = MagicMock()
    agent.cognitive = MagicMock()
    agent.voice.linguistic_signature = {"archetype": "balanced", "style": "neutral"}
    agent.message_bus = None
    return agent


@pytest.fixture
def mock_message_bus():
    """Create a mock message bus."""
    bus = MagicMock()
    return bus


class TestReflexivityLayer:
    """Tests for ReflexivityLayer serialization."""

    def test_to_dict_includes_version(self, mock_agent):
        """Test that to_dict includes version field."""
        layer = ReflexivityLayer(agent=mock_agent)
        data = layer.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_includes_agent_id(self, mock_agent):
        """Test that to_dict includes agent_id."""
        layer = ReflexivityLayer(agent=mock_agent)
        data = layer.to_dict()

        assert "agent_id" in data
        assert data["agent_id"] == "test_agent_001"

    def test_from_dict_reconstructs_layer(self, mock_agent):
        """Test that from_dict reconstructs the layer."""
        layer = ReflexivityLayer(agent=mock_agent)
        data = layer.to_dict()

        reconstructed = ReflexivityLayer.from_dict(data, agent=mock_agent)

        assert isinstance(reconstructed, ReflexivityLayer)
        assert reconstructed.agent.agent_id == mock_agent.agent_id

    def test_round_trip_serialization(self, mock_agent):
        """Test round-trip serialization preserves state."""
        layer = ReflexivityLayer(agent=mock_agent)
        data1 = layer.to_dict()

        reconstructed = ReflexivityLayer.from_dict(data1, agent=mock_agent)
        data2 = reconstructed.to_dict()

        assert data1["agent_id"] == data2["agent_id"]
        assert data1["version"] == data2["version"]

    def test_version_mismatch_warning(self, mock_agent):
        """Test that version mismatch triggers warning."""
        data = {"version": "0.0.1", "agent_id": "test_agent_001"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ReflexivityLayer.from_dict(data, agent=mock_agent)

            assert len(w) >= 1
            assert any(
                "reflexivitylayer" in str(warning.message).lower() for warning in w
            )

    def test_agent_id_mismatch_warning(self, mock_agent):
        """Test that agent_id mismatch triggers warning."""
        from agisa_sac import FRAMEWORK_VERSION

        data = {"version": FRAMEWORK_VERSION, "agent_id": "different_agent"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ReflexivityLayer.from_dict(data, agent=mock_agent)

            # Should have at least one warning about agent ID mismatch
            assert any("mismatch" in str(warning.message).lower() for warning in w)

    def test_requires_agent_reference(self):
        """Test that ReflexivityLayer requires an agent reference."""
        with pytest.raises(TypeError):
            ReflexivityLayer(agent=None)


class TestResonanceLiturgy:
    """Tests for ResonanceLiturgy serialization."""

    def test_to_dict_includes_version(self):
        """Test that to_dict includes version field."""
        liturgy = ResonanceLiturgy(agent_id="test_agent", satori_threshold=0.9)
        data = liturgy.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_includes_config(self):
        """Test that to_dict includes configuration."""
        liturgy = ResonanceLiturgy(agent_id="test_agent", satori_threshold=0.85)
        data = liturgy.to_dict()

        assert "agent_id" in data
        assert data["agent_id"] == "test_agent"
        assert "satori_threshold" in data
        assert data["satori_threshold"] == 0.85
        assert "ritual_phrases" in data
        assert isinstance(data["ritual_phrases"], list)

    def test_from_dict_reconstructs_liturgy(self):
        """Test that from_dict reconstructs the liturgy."""
        liturgy = ResonanceLiturgy(agent_id="test_agent", satori_threshold=0.88)
        data = liturgy.to_dict()

        reconstructed = ResonanceLiturgy.from_dict(data)

        assert reconstructed.agent_id == "test_agent"
        assert reconstructed.satori_threshold == 0.88
        assert len(reconstructed.ritual_phrases) > 0

    def test_from_dict_with_agent_id_override(self):
        """Test from_dict with agent_id override."""
        liturgy = ResonanceLiturgy(agent_id="original_agent")
        data = liturgy.to_dict()

        reconstructed = ResonanceLiturgy.from_dict(data, agent_id="new_agent")

        assert reconstructed.agent_id == "new_agent"

    def test_round_trip_preserves_custom_phrases(self):
        """Test that custom ritual phrases are preserved."""
        liturgy = ResonanceLiturgy(agent_id="test_agent")
        custom_phrases = ["Custom phrase 1", "Custom phrase 2"]
        liturgy.ritual_phrases = custom_phrases

        data = liturgy.to_dict()
        reconstructed = ResonanceLiturgy.from_dict(data)

        assert reconstructed.ritual_phrases == custom_phrases

    def test_version_mismatch_warning(self):
        """Test that version mismatch triggers warning."""
        data = {
            "version": "0.0.1",
            "agent_id": "test_agent",
            "satori_threshold": 0.9,
            "ritual_phrases": ["test"],
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ResonanceLiturgy.from_dict(data)

            assert len(w) >= 1
            assert any("resonanceliturgy" in str(warning.message).lower() for warning in w)


class TestSemanticProfile:
    """Tests for SemanticProfile serialization."""

    def test_to_dict_includes_version(self):
        """Test that to_dict includes version field."""
        profile = SemanticProfile(
            text_embedding=np.array([0.1, 0.2, 0.3]),
            concept_vectors={"concept1": np.array([0.5, 0.6])},
            ethical_signature=np.array([0.7, 0.8]),
        )
        data = profile.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_converts_numpy_to_lists(self):
        """Test that to_dict converts numpy arrays to lists."""
        profile = SemanticProfile(
            text_embedding=np.array([0.1, 0.2]),
            concept_vectors={"concept1": np.array([0.3, 0.4])},
            ethical_signature=np.array([0.5, 0.6]),
        )
        data = profile.to_dict()

        assert isinstance(data["text_embedding"], list)
        assert isinstance(data["ethical_signature"], list)
        assert isinstance(data["concept_vectors"]["concept1"], list)

    def test_from_dict_reconstructs_profile(self):
        """Test that from_dict reconstructs the profile."""
        profile = SemanticProfile(
            text_embedding=np.array([0.1, 0.2, 0.3]),
            concept_vectors={"test": np.array([0.4, 0.5])},
            ethical_signature=np.array([0.6, 0.7]),
            confidence_score=0.95,
        )
        data = profile.to_dict()

        reconstructed = SemanticProfile.from_dict(data)

        assert isinstance(reconstructed, SemanticProfile)
        assert np.allclose(reconstructed.text_embedding, profile.text_embedding)
        assert np.allclose(reconstructed.ethical_signature, profile.ethical_signature)
        assert reconstructed.confidence_score == 0.95

    def test_round_trip_serialization(self):
        """Test round-trip serialization preserves all fields."""
        profile = SemanticProfile(
            text_embedding=np.array([1.0, 2.0]),
            concept_vectors={"c1": np.array([3.0]), "c2": np.array([4.0])},
            ethical_signature=np.array([5.0, 6.0]),
            temporal_context=np.array([7.0, 8.0]),
            confidence_score=0.88,
        )

        data = profile.to_dict()
        reconstructed = SemanticProfile.from_dict(data)

        assert np.allclose(reconstructed.text_embedding, profile.text_embedding)
        assert np.allclose(reconstructed.ethical_signature, profile.ethical_signature)
        assert np.allclose(reconstructed.temporal_context, profile.temporal_context)
        assert reconstructed.confidence_score == profile.confidence_score


class TestEnhancedSemanticAnalyzer:
    """Tests for EnhancedSemanticAnalyzer serialization."""

    @patch("agisa_sac.core.components.semantic_analyzer.SentenceTransformer")
    def test_to_dict_includes_version(self, mock_transformer):
        """Test that to_dict includes version field."""
        analyzer = EnhancedSemanticAnalyzer(device="cpu")
        data = analyzer.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    @patch("agisa_sac.core.components.semantic_analyzer.SentenceTransformer")
    def test_to_dict_includes_model_name(self, mock_transformer):
        """Test that to_dict stores model_name."""
        mock_instance = Mock()
        mock_transformer.return_value = mock_instance

        analyzer = EnhancedSemanticAnalyzer(
            device="cpu", model_name="test-model-v1"
        )
        data = analyzer.to_dict()

        assert "model_name" in data
        assert data["model_name"] == "test-model-v1"

    @patch("agisa_sac.core.components.semantic_analyzer.SentenceTransformer")
    def test_from_dict_reconstructs_analyzer(self, mock_transformer):
        """Test that from_dict reconstructs the analyzer."""
        mock_instance = Mock()
        mock_transformer.return_value = mock_instance

        analyzer = EnhancedSemanticAnalyzer(device="cpu")
        data = analyzer.to_dict()

        reconstructed = EnhancedSemanticAnalyzer.from_dict(data)

        assert isinstance(reconstructed, EnhancedSemanticAnalyzer)
        assert reconstructed.model_name == analyzer.model_name

    @patch("agisa_sac.core.components.semantic_analyzer.SentenceTransformer")
    def test_version_mismatch_warning(self, mock_transformer):
        """Test that version mismatch triggers warning."""
        data = {"version": "0.0.1", "model_name": "test-model"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            EnhancedSemanticAnalyzer.from_dict(data)

            assert len(w) >= 1
            assert any(
                "enhancedsemanticanalyzer" in str(warning.message).lower()
                for warning in w
            )


class TestDynamicSocialGraph:
    """Tests for DynamicSocialGraph serialization."""

    def test_to_dict_includes_version(self, mock_message_bus):
        """Test that to_dict includes version field."""
        graph = DynamicSocialGraph(
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )
        data = graph.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_includes_matrix_state(self, mock_message_bus):
        """Test that to_dict includes sparse matrix state."""
        graph = DynamicSocialGraph(
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )

        # Use update_influence (the actual method name)
        graph.update_influence("agent1", "agent2", 0.5)
        graph.update_influence("agent2", "agent3", 0.8)

        data = graph.to_dict()

        assert "influence_matrix_coo" in data
        assert isinstance(data["influence_matrix_coo"], list)

    def test_to_dict_includes_reputation(self, mock_message_bus):
        """Test that to_dict includes reputation scores."""
        graph = DynamicSocialGraph(
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )
        data = graph.to_dict()

        assert "reputation" in data
        assert isinstance(data["reputation"], list)
        assert len(data["reputation"]) == 3

    def test_from_dict_reconstructs_graph(self, mock_message_bus):
        """Test that from_dict reconstructs the graph."""
        graph = DynamicSocialGraph(
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )
        graph.update_influence("agent1", "agent2", 0.7)
        data = graph.to_dict()

        reconstructed = DynamicSocialGraph.from_dict(
            data,
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )

        assert isinstance(reconstructed, DynamicSocialGraph)
        assert reconstructed.num_agents == 3

    def test_round_trip_with_communities(self, mock_message_bus):
        """Test round-trip with community data."""
        graph = DynamicSocialGraph(
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )
        graph.last_communities = [{0, 1}, {2}]

        data = graph.to_dict()
        reconstructed = DynamicSocialGraph.from_dict(
            data,
            num_agents=3,
            agent_ids=["agent1", "agent2", "agent3"],
            use_gpu=False,
            message_bus=mock_message_bus,
        )

        assert reconstructed.last_communities is not None
        assert len(reconstructed.last_communities) == 2


class TestCRDTMemoryLayer:
    """Tests for CRDTMemoryLayer serialization."""

    def test_to_dict_includes_version(self):
        """Test that to_dict includes version field."""
        layer = CRDTMemoryLayer(node_id="test_node", max_memory_size=100)
        data = layer.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_includes_node_id(self):
        """Test that to_dict includes node_id."""
        layer = CRDTMemoryLayer(node_id="test_node_123")
        data = layer.to_dict()

        assert "node_id" in data
        assert data["node_id"] == "test_node_123"

    def test_from_dict_reconstructs_layer(self):
        """Test that from_dict reconstructs the layer."""
        layer = CRDTMemoryLayer(node_id="test_node")
        data = layer.to_dict()

        reconstructed = CRDTMemoryLayer.from_dict(data)

        assert isinstance(reconstructed, CRDTMemoryLayer)
        assert reconstructed.node_id == "test_node"

    def test_round_trip_serialization(self):
        """Test round-trip serialization."""
        layer = CRDTMemoryLayer(node_id="test_node", max_memory_size=200)

        data1 = layer.to_dict()
        reconstructed = CRDTMemoryLayer.from_dict(data1)
        data2 = reconstructed.to_dict()

        assert data1["node_id"] == data2["node_id"]
        assert data1["version"] == data2["version"]


class TestContinuityBridgeProtocol:
    """Tests for ContinuityBridgeProtocol serialization."""

    def test_to_dict_includes_version(self):
        """Test that to_dict includes version field."""
        bridge = ContinuityBridgeProtocol(
            coherence_threshold=0.8, memory_window_hours=24
        )
        data = bridge.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_includes_config(self):
        """Test that to_dict includes configuration."""
        bridge = ContinuityBridgeProtocol(
            coherence_threshold=0.75, memory_window_hours=48
        )
        data = bridge.to_dict()

        assert "coherence_threshold" in data
        assert data["coherence_threshold"] == 0.75

    def test_from_dict_reconstructs_bridge(self):
        """Test that from_dict reconstructs the bridge."""
        bridge = ContinuityBridgeProtocol(coherence_threshold=0.85)
        data = bridge.to_dict()

        reconstructed = ContinuityBridgeProtocol.from_dict(data)

        assert isinstance(reconstructed, ContinuityBridgeProtocol)
        assert reconstructed.coherence_threshold == 0.85

    def test_round_trip_serialization(self):
        """Test round-trip serialization preserves state."""
        bridge = ContinuityBridgeProtocol(coherence_threshold=0.9)

        data1 = bridge.to_dict()
        reconstructed = ContinuityBridgeProtocol.from_dict(data1)
        data2 = reconstructed.to_dict()

        assert data1["coherence_threshold"] == data2["coherence_threshold"]

    def test_version_mismatch_warning(self):
        """Test that version mismatch triggers warning."""
        data = {"version": "0.0.1", "coherence_threshold": 0.8}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ContinuityBridgeProtocol.from_dict(data)

            assert len(w) >= 1
            assert any(
                "continuitybridgeprotocol" in str(warning.message).lower()
                for warning in w
            )


class TestEnhancedContinuityBridgeProtocol:
    """Tests for EnhancedContinuityBridgeProtocol serialization."""

    def test_to_dict_includes_version(self):
        """Test that to_dict includes version field."""
        enhanced = EnhancedContinuityBridgeProtocol(coherence_threshold=0.8)
        data = enhanced.to_dict()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_to_dict_delegates_to_base(self):
        """Test that to_dict delegates to base ContinuityBridgeProtocol."""
        enhanced = EnhancedContinuityBridgeProtocol(coherence_threshold=0.8)
        data = enhanced.to_dict()

        # Should include base_cbp wrapper
        assert "base_cbp" in data
        assert "coherence_threshold" in data["base_cbp"]

    def test_from_dict_reconstructs_enhanced_bridge(self):
        """Test that from_dict reconstructs the enhanced bridge."""
        enhanced = EnhancedContinuityBridgeProtocol(coherence_threshold=0.75)
        data = enhanced.to_dict()

        reconstructed = EnhancedContinuityBridgeProtocol.from_dict(data)

        assert isinstance(reconstructed, EnhancedContinuityBridgeProtocol)
        assert reconstructed.base_cbp.coherence_threshold == 0.75

    def test_round_trip_serialization(self):
        """Test round-trip serialization."""
        enhanced = EnhancedContinuityBridgeProtocol(coherence_threshold=0.9)

        data1 = enhanced.to_dict()
        reconstructed = EnhancedContinuityBridgeProtocol.from_dict(data1)
        data2 = reconstructed.to_dict()

        assert data1["base_cbp"]["coherence_threshold"] == data2["base_cbp"]["coherence_threshold"]

    def test_version_mismatch_warning(self):
        """Test that version mismatch triggers warning."""
        data = {"version": "0.0.1", "coherence_threshold": 0.8}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            EnhancedContinuityBridgeProtocol.from_dict(data)

            assert len(w) >= 1
            assert any(
                "continuitybridgeprotocol" in str(warning.message).lower()
                for warning in w
            )
