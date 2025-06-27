import base64
import json
import os
from google.cloud import firestore, tasks_v2

db = firestore.Client()
client = tasks_v2.CloudTasksClient()
PROJECT = os.getenv("GCP_PROJECT", "local-project")
QUEUE = os.getenv("TASK_QUEUE", "eval-queue")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")


def evaluator(event, context):
    """Evaluates agent responses and requeues if needed."""
    data = base64.b64decode(event["data"]).decode("utf-8")
    result = json.loads(data)
    task_id = result.get("task_id")
    score = result.get("score", 0)

    db.collection("tasks").document(task_id).update({"score": score})

    if score < 0.5:
        parent = client.queue_path(PROJECT, LOCATION, QUEUE)
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": result.get("retry_url", "")
            }
        }
        client.create_task(parent=parent, task=task)
