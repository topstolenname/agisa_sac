from __future__ import annotations

from typing import Dict, Optional, Any

from .agent import EnhancedAgent


class MultiAgentSystem:
    """Simple container to manage multiple agents."""

    def __init__(self) -> None:
        self.agents: Dict[str, EnhancedAgent] = {}

    def create_agent(
        self,
        agent_id: str,
        personality: Optional[Dict[str, float]] = None,
        capacity: int = 100,
        use_semantic: bool = False,
    ) -> EnhancedAgent:
        """Instantiate an ``EnhancedAgent`` and add it to the system."""
        if personality is None:
            personality = {
                "openness": 0.5,
                "consistency": 0.5,
                "conformity": 0.5,
                "curiosity": 0.5,
            }
        agent = EnhancedAgent(
            agent_id=agent_id,
            personality=personality,
            capacity=capacity,
            use_semantic=use_semantic,
        )
        self.add_agent(agent)
        return agent

    def add_agent(self, agent: EnhancedAgent) -> None:
        """Add an already created agent to the system."""
        self.agents[agent.agent_id] = agent

    def get_system_stats(self) -> Dict[str, Any]:
        """Return basic statistics for the system."""
        return {"total_agents": len(self.agents)}
