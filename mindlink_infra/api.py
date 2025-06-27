from fastapi import FastAPI
from pydantic import BaseModel
from .registry import AgentRegistry

app = FastAPI(title="Mindlink Infrastructure")
registry = AgentRegistry()


class AgentConfig(BaseModel):
    agent_id: str
    personality: dict = {}


@app.post("/spawn_agent")
async def spawn_agent(config: AgentConfig):
    agent = registry.spawn_agent(config.agent_id, config.personality)
    return {"status": "spawned", "agent_id": agent.agent_id}


@app.get("/agents")
async def list_agents():
    return {"agents": registry.list_agents()}
