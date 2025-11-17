# In agisa_sac/federation/loop.py
"""
Federation heartbeat loop with CGE integration.

This module provides the main coordination loop for agent federation,
triggering cognitive evolution cycles at regular intervals.
"""
from typing import List
from agisa_sac.cognition.cge.orchestrator import evolve_pool
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Global tick counter for coordination
_tick = 0


async def federation_tick(agent_pool: List):
    """
    Federation heartbeat function called on each simulation cycle.

    This function coordinates agent interactions and triggers cognitive
    evolution via the CGE optimizer every 100 ticks.

    Args:
        agent_pool: List of active agents in the federation

    Note:
        The CGE evolution is triggered every 100 ticks to balance
        optimization overhead with adaptation responsiveness.
    """
    global _tick

    logger.debug(f"Federation tick={_tick}")

    # Trigger CGE optimization every 100 ticks
    if _tick > 0 and _tick % 100 == 0:
        logger.info(f"Federation tick={_tick}: Triggering CGE evolution cycle")
        await evolve_pool(agent_pool)

    _tick += 1

    # Additional federation coordination logic would go here
    # (agent interactions, message passing, etc.)


def reset_tick_counter():
    """Reset the global tick counter (useful for testing)"""
    global _tick
    _tick = 0
