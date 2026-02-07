from ..agents.agent import EnhancedAgent


class MultiAgentSystem:
    """Minimal container managing a collection of EnhancedAgent instances."""

    def __init__(self) -> None:
        self.agents: dict[str, EnhancedAgent] = {}
        self.created_agents: int = 0

    def create_agent(self, agent_id: str, personality: dict) -> EnhancedAgent:
        """Create and register a new EnhancedAgent."""
        agent = EnhancedAgent(
            agent_id=agent_id,
            personality=personality,
            capacity=10,
            use_semantic=False,
        )
        self.agents[agent_id] = agent
        self.created_agents += 1
        return agent

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent by id. Returns True if removed."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def get_system_stats(self) -> dict:
        """Return simple statistics about the system."""
        return {
            "total_agents": len(self.agents),
            "created_agents": self.created_agents,
        }
