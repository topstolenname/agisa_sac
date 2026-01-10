# In agisa_sac/federation/loop.py
"""
Federation heartbeat loop with CGE integration.

This module provides the main coordination loop for agent federation,
triggering cognitive evolution cycles at regular intervals.
"""
from typing import List, TYPE_CHECKING
from agisa_sac.cognition.cge.orchestrator import evolve_pool
from agisa_sac.utils.logger import get_logger

if TYPE_CHECKING:
    from agisa_sac.agents.agent import EnhancedAgent

logger = get_logger(__name__)


class FederationLoop:
    """
    Manages the federation heartbeat loop with CGE integration.

    This class encapsulates the tick counter and coordination logic,
    providing better testability and encapsulation compared to global state.
    """

    def __init__(self, cge_trigger_interval: int = 100):
        """
        Initialize the federation loop.

        Args:
            cge_trigger_interval: Number of ticks between CGE evolution cycles
        """
        self.tick = 0
        self.cge_trigger_interval = cge_trigger_interval

    async def federation_tick(self, agent_pool: List["EnhancedAgent"]):
        """
        Federation heartbeat function called on each simulation cycle.

        This function coordinates agent interactions and triggers cognitive
        evolution via the CGE optimizer at regular intervals.

        Args:
            agent_pool: List of active agents in the federation
        """
        logger.debug(f"Federation tick={self.tick}")

        # Trigger CGE optimization at configured intervals
        if self.tick > 0 and self.tick % self.cge_trigger_interval == 0:
            logger.info(f"Federation tick={self.tick}: Triggering CGE evolution cycle")
            await evolve_pool(agent_pool)

        self.tick += 1

        # Additional federation coordination logic would go here
        # (agent interactions, message passing, etc.)

    def reset(self):
        """Reset the tick counter (useful for testing)"""
        self.tick = 0


# Default instance for backward compatibility
_default_loop = FederationLoop()


async def federation_tick(agent_pool: List["EnhancedAgent"]):
    """
    Legacy function that uses the default FederationLoop instance.

    For new code, prefer creating a FederationLoop instance directly.

    Args:
        agent_pool: List of active agents in the federation
    """
    await _default_loop.federation_tick(agent_pool)


def reset_tick_counter():
    """Reset the default loop's tick counter (useful for testing)"""
    _default_loop.reset()
