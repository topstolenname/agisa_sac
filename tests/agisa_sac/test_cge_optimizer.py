# In tests/agisa_sac/test_cge_optimizer.py
from unittest.mock import AsyncMock, patch

import pytest

from agisa_sac.cognition.cge.optimizer import CognitiveGradientEngine
from cognee.memory.hierarchical.config import MemoryGenome


@pytest.mark.asyncio
async def test_optimizer_returns_valid_genome():
    """Test that CGE returns a valid, constrained MemoryGenome"""
    # Use very few evals for fast test
    cge = CognitiveGradientEngine(agent_id="test_agent_A", max_evals=2)

    genome = await cge.optimize()

    # Check it's the right type
    assert isinstance(genome, MemoryGenome)

    # Check version
    assert genome.version == "1.0"

    # Check constraints are respected
    assert 50 <= genome.sensory_buffer_capacity <= 500
    assert 5 <= genome.working_memory_limit <= 11
    assert 0.1 <= genome.episodic_salience_threshold <= 0.9
    assert 0.05 <= genome.semantic_strengthening_rate <= 0.5
    assert 0.01 <= genome.procedural_learning_threshold <= 0.2
    assert 100.0 <= genome.decay_constant <= 1000.0
    assert 1.0 <= genome.emotional_weight_multiplier <= 5.0
    assert 0.05 <= genome.usage_reinforcement_gain <= 0.3

    # Verify explicit type conversions for quniform parameters
    assert isinstance(
        genome.sensory_buffer_capacity, int
    ), "sensory_buffer_capacity should be explicitly converted to int"
    assert isinstance(
        genome.decay_constant, float
    ), "decay_constant should remain as float"


@pytest.mark.asyncio
async def test_optimizer_persists_profile():
    """Test that CGE calls the persistence layer via _save_profile"""
    cge = CognitiveGradientEngine(agent_id="test_agent_B", max_evals=1)

    # Mock the _save_profile method to verify it's called
    with patch.object(
        CognitiveGradientEngine, "_save_profile", new_callable=AsyncMock
    ) as mock_save:
        genome = await cge.optimize()

        # Verify _save_profile was called exactly once
        mock_save.assert_called_once()

        # Verify it was called with a MemoryGenome instance
        call_args = mock_save.call_args
        assert call_args is not None
        saved_genome = call_args[0][0]  # First positional argument
        assert isinstance(saved_genome, MemoryGenome)

    # Verify the returned genome is valid
    assert isinstance(genome, MemoryGenome)
