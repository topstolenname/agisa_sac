from fastapi import FastAPI, HTTPException
from google.cloud import firestore

app = FastAPI(title="Mindlink Simulation API")

db = firestore.Client()


@app.post("/inject-agent")
async def inject_agent(agent: dict):
    agent_id = agent.get("id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Missing agent id")
    db.collection("agents").document(agent_id).set(agent)
    return {"status": "injected", "agent_id": agent_id}


@app.post("/submit-task")
async def submit_task(task: dict):
    from cloud.run.task_dispatcher import submit_task as dispatch
    return await dispatch(task)


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    doc = db.collection("agents").document(agent_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    return doc.to_dict()


@app.get("/task/{task_id}")
async def get_task(task_id: str):
    doc = db.collection("tasks").document(task_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task not found")
    return doc.to_dict()
