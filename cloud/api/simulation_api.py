from fastapi import FastAPI, HTTPException
try:
    from google.cloud import firestore
except Exception:  # noqa: BLE001
    firestore = None

app = FastAPI(title="Mindlink Simulation API")

try:
    if firestore is not None:
        db = firestore.Client()
        memory_db = None
    else:
        raise RuntimeError("Firestore not available")
except Exception:  # Fallback when credentials or library are unavailable
    db = None
    memory_db = {"agents": {}, "tasks": {}}


@app.post("/inject-agent")
async def inject_agent(agent: dict):
    agent_id = agent.get("id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Missing agent id")
    if db is not None:
        db.collection("agents").document(agent_id).set(agent)
    else:
        memory_db["agents"][agent_id] = agent
    return {"status": "injected", "agent_id": agent_id}


@app.post("/submit-task")
async def submit_task(task: dict):
    from cloud.run.task_dispatcher import submit_task as dispatch
    result = await dispatch(task)
    if db is None and isinstance(result, dict) and "task_id" in result:
        memory_db["tasks"][result["task_id"]] = task
    return result


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    if db is not None:
        doc = db.collection("agents").document(agent_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Agent not found")
        return doc.to_dict()
    else:
        agent = memory_db["agents"].get(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent


@app.get("/task/{task_id}")
async def get_task(task_id: str):
    if db is not None:
        doc = db.collection("tasks").document(task_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Task not found")
        return doc.to_dict()
    else:
        task = memory_db["tasks"].get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
