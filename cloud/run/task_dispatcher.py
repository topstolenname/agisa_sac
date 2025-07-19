import json
import os
import uuid
from fastapi import FastAPI, HTTPException
from google.cloud import firestore, pubsub_v1

app = FastAPI(title="Mindlink Task Dispatcher")

memory_db = {"tasks": {}}
try:
    db = firestore.Client()
    publisher = pubsub_v1.PublisherClient()
    PROJECT = os.getenv("GCP_PROJECT", "local-project")
    TOPIC = os.getenv("EVENT_TOPIC", "agent-events")
    topic_path = publisher.topic_path(PROJECT, TOPIC)
except Exception:  # Fallback when credentials are unavailable
    db = None
    publisher = None
    topic_path = None


@app.post("/submit-task")
async def submit_task(task: dict):
    """Stores task in Firestore and publishes to Pub/Sub."""
    if not isinstance(task, dict):
        raise HTTPException(status_code=400, detail="Invalid task payload")
    if db is None or publisher is None or topic_path is None:
        task_id = str(uuid.uuid4())
        task["id"] = task_id
        memory_db["tasks"][task_id] = task
        return {"task_id": task_id}

    task_id = str(uuid.uuid4())
    task["id"] = task_id
    db.collection("tasks").document(task_id).set(task)
    publisher.publish(topic_path, json.dumps(task).encode("utf-8"))
    return {"task_id": task_id}
