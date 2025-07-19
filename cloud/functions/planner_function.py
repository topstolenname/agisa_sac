import base64
import json
import os
from google.cloud import pubsub_v1

try:
    publisher = pubsub_v1.PublisherClient()
    PROJECT = os.getenv("GCP_PROJECT", "local-project")
    TOPIC = os.getenv("EVENT_TOPIC", "agent-events")
    topic_path = publisher.topic_path(PROJECT, TOPIC)
except Exception:  # Ignore initialization failures during import
    publisher = None
    topic_path = None


def planner(event, context):
    """Cloud Function entrypoint triggered by Pub/Sub."""
    data = base64.b64decode(event["data"]).decode("utf-8")
    task = json.loads(data)

    # Placeholder decomposition logic
    subtask = {"parent": task.get("id"), "goal": task.get("goal"), "step": 1}
    publisher.publish(topic_path, json.dumps(subtask).encode("utf-8"))
