# In tests/cognee/test_memory_genome.py
import pytest
from pydantic import ValidationError

from cognee.memory.hierarchical.config import MemoryGenome


def test_genome_validation():
    # Test valid
    genome = MemoryGenome(working_memory_limit=7)
    assert genome.working_memory_limit == 7

    # Test invalid
    with pytest.raises(ValidationError):
        # Miller's Law constraint is 5-11
        MemoryGenome(working_memory_limit=15)

    with pytest.raises(ValidationError):
        # sensory buffer constraint is 50-500
        MemoryGenome(sensory_buffer_capacity=10)


def test_genome_defaults():
    """Test that default values are valid"""
    genome = MemoryGenome()
    assert genome.version == "1.0"
    assert 50 <= genome.sensory_buffer_capacity <= 500
    assert 5 <= genome.working_memory_limit <= 11
    assert 0.1 <= genome.episodic_salience_threshold <= 0.9
