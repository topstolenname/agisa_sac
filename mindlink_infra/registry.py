"""Runtime agent registry with dynamic loading capabilities."""

from importlib import import_module
from typing import Dict, Type

from agisa_sac.agent import EnhancedAgent

class AgentRegistry:
    """Manage active agents and available agent types."""

    def __init__(self) -> None:
        self.agents: Dict[str, EnhancedAgent] = {}
        self.agent_classes: Dict[str, Type[EnhancedAgent]] = {
            "enhanced": EnhancedAgent
        }

    # ------------------------------------------------------------------
    # Agent type registration
    # ------------------------------------------------------------------

    def register_agent_class(self, name: str, cls: Type[EnhancedAgent]) -> None:
        """Register a new agent class for spawning."""
        if not name:
            raise ValueError("name must be non-empty")
        self.agent_classes[name] = cls

    def load_agent_class(self, dotted_path: str, name: str | None = None) -> None:
        """Load and register an agent class from ``module:Class`` syntax."""
        module_path, _, class_name = dotted_path.partition(":")
        if not class_name:
            # allow module.Class style
            module_path, _, class_name = dotted_path.rpartition(".")
        module = import_module(module_path)
        cls = getattr(module, class_name)
        self.register_agent_class(name or class_name.lower(), cls)

    def spawn_agent(
        self, agent_id: str, personality: Dict, *, agent_type: str = "enhanced"
    ) -> EnhancedAgent:
        """Create and store a new agent instance of ``agent_type``."""
        cls = self.agent_classes.get(agent_type)
        if cls is None:
            raise ValueError(f"Unknown agent type: {agent_type}")
        agent = cls(
            agent_id=agent_id,
            personality=personality,
            capacity=50,
            use_semantic=False,
        )
        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> EnhancedAgent | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> list[str]:
        return list(self.agents.keys())
