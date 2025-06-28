from __future__ import annotations

from typing import Dict, Optional, Iterable

from ..agent import EnhancedAgent


class MultiAgentSystem:
    """Minimal container for managing multiple :class:`EnhancedAgent` instances."""

    def __init__(self) -> None:
        self.agents: Dict[str, EnhancedAgent] = {}

    def add_agent(self, agent: EnhancedAgent) -> None:
        """Add an agent to the system."""
        self.agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[EnhancedAgent]:
        """Return an agent by ID if present."""
        return self.agents.get(agent_id)

    def remove_agent(self, agent_id: str) -> Optional[EnhancedAgent]:
        """Remove and return an agent by ID if present."""
        return self.agents.pop(agent_id, None)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.agents)

    def __iter__(self) -> Iterable[EnhancedAgent]:  # pragma: no cover - trivial
        return iter(self.agents.values())
