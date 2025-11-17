# In agisa_sac/cognition/cge/orchestrator.py
import asyncio
from typing import List
from agisa_sac.cognition.cge.optimizer import CognitiveGradientEngine
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)


async def evolve_pool(agent_pool: List):
    """
    Run a cognitive evolution cycle for all agents in the pool.

    This function orchestrates the CGE optimization process across multiple
    agents concurrently, using gather to run optimizations in parallel.

    Args:
        agent_pool: List of agents to evolve
    """
    logger.info(f"CGE cycle starting for {len(agent_pool)} agents")
    await asyncio.gather(*[evolve_agent(agent) for agent in agent_pool])
    logger.info(f"CGE cycle complete for {len(agent_pool)} agents")


async def evolve_agent(agent):
    """
    Evolve a single agent's cognitive genome.

    This function:
    1. Creates a CGE optimizer for the agent
    2. Runs optimization to find better genome parameters
    3. Hot-swaps the agent's memory with the optimized profile

    Args:
        agent: The agent to evolve (must have 'id' or 'agent_id' attribute)
    """
    # Get agent ID (support both 'id' and 'agent_id' attributes)
    agent_id = getattr(agent, "id", None) or getattr(agent, "agent_id", "unknown")

    try:
        logger.debug(f"Evolving agent {agent_id}...")

        # Create optimizer and run optimization
        cge = CognitiveGradientEngine(agent_id=agent_id, max_evals=8)
        genome = await cge.optimize()

        # Hot-swap the agent's memory with optimized profile
        await agent.load_cognitive_profile(genome)

        logger.info(f"Successfully evolved agent {agent_id}")

    except Exception as e:
        logger.error(f"CGE failed for agent {agent_id}: {e}", exc_info=True)
