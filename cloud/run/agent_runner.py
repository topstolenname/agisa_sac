import base64
import json
import os
from fastapi import FastAPI, Request
from agisa_sac.agents.agent import EnhancedAgent

app = FastAPI(title="Mindlink Agent Runner")


@app.post("/")
async def handle_event(request: Request):
    """HTTP endpoint for Pub/Sub push messages."""
    envelope = await request.json()
    message = envelope.get("message", {})
    data = message.get("data")
    if data:
        event = json.loads(base64.b64decode(data).decode("utf-8"))
    else:
        event = {}

    observation = event.get("observation")
    state = event.get("agent_state", {})
    agent = EnhancedAgent(agent_id=state.get("id", "agent"), personality={})
    result = agent.simulation_step(0.0, {}, query=observation)
    return {"result": result}
