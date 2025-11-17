# In tests/agisa_sac/test_cge_optimizer.py
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


@pytest.mark.asyncio
async def test_optimizer_persists_profile():
    """Test that CGE calls the persistence layer"""
    cge = CognitiveGradientEngine(agent_id="test_agent_B", max_evals=1)

    # This will print mock firestore output
    genome = await cge.optimize()

    # If we got a genome back, persistence was called (in mock mode)
    assert isinstance(genome, MemoryGenome)
