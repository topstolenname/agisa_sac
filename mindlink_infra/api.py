from fastapi import FastAPI
from pydantic import BaseModel

from .registry import AgentRegistry

app = FastAPI(title="Mindlink Infrastructure")
registry = AgentRegistry()


class AgentConfig(BaseModel):
    agent_id: str
    personality: dict = {}
    agent_type: str = "enhanced"


class AgentTypeConfig(BaseModel):
    """Configuration for registering a new agent class."""
    path: str  # dotted path to class, e.g. "mypkg.module:CustomAgent"
    name: str | None = None


@app.post("/spawn_agent")
async def spawn_agent(config: AgentConfig):
    agent = registry.spawn_agent(
        config.agent_id,
        config.personality,
        agent_type=config.agent_type,
    )
    return {"status": "spawned", "agent_id": agent.agent_id}


@app.get("/agents")
async def list_agents():
    return {"agents": registry.list_agents()}


@app.post("/register_agent_type")
async def register_agent_type(cfg: AgentTypeConfig):
    registry.load_agent_class(cfg.path, cfg.name)
    return {"status": "registered"}
