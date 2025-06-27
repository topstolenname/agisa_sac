from typing import Dict
from agisa_sac.agent import EnhancedAgent

class AgentRegistry:
    """Simple in-memory registry for managing agents."""
    def __init__(self):
        self.agents: Dict[str, EnhancedAgent] = {}

    def spawn_agent(self, agent_id: str, personality: Dict) -> EnhancedAgent:
        """Create and store a new agent instance."""
        agent = EnhancedAgent(agent_id=agent_id, personality=personality, capacity=50, use_semantic=False)
        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> EnhancedAgent | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> list[str]:
        return list(self.agents.keys())
