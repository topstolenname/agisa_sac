# In tests/agisa_sac/test_agent_profile_swap.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from agisa_sac.agents.agent import EnhancedAgent
from cognee.memory.hierarchical.config import MemoryGenome
from cognee.memory.hierarchical.core import HierarchicalMemory


@pytest.mark.asyncio
async def test_profile_swap_stops_old_and_starts_new():
    """Test that load_cognitive_profile safely stops old memory and starts new"""
    # Create a minimal EnhancedAgent instance
    agent = EnhancedAgent(
        agent_id="test_agent_X",
        personality={"openness": 0.7, "conscientiousness": 0.6},
        capacity=50,
        use_semantic=False,  # Avoid heavy dependencies
        add_initial_memory=False,  # Don't add initial memory for test
    )

    # Give it a mock "old" memory that has a 'stop' method
    old_memory = MagicMock()
    old_memory.stop = AsyncMock()
    agent.memory = old_memory

    # Create a genome to load
    genome = MemoryGenome()

    # Load the new profile
    await agent.load_cognitive_profile(genome)

    # 1. Check that the old memory's 'stop' was called
    old_memory.stop.assert_called_once()

    # 2. Check that the new memory is a HierarchicalMemory
    assert isinstance(agent.memory, HierarchicalMemory)

    # 3. Check that the new memory's consolidation task is running
    assert agent.memory.consolidation_task is not None

    # Clean up - stop the new memory
    await agent.memory.stop()


@pytest.mark.asyncio
async def test_profile_swap_with_no_old_memory():
    """Test that load_cognitive_profile works when there's no previous memory"""
    # Create agent without memory attribute
    agent = EnhancedAgent(
        agent_id="test_agent_Y",
        personality={"openness": 0.5},
        capacity=50,
        use_semantic=False,
        add_initial_memory=False,
    )

    # Delete the memory to simulate no previous memory
    delattr(agent, "memory")

    genome = MemoryGenome()

    # Should not raise error
    await agent.load_cognitive_profile(genome)

    # New memory should be created
    assert isinstance(agent.memory, HierarchicalMemory)

    # Clean up
    await agent.memory.stop()
