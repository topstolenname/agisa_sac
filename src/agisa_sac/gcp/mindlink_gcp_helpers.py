"""Helper utilities for running AGI-SAC on Google Cloud."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Iterable, Optional

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None
    JSONResponse = None
    HAS_FASTAPI = False

try:
    from google.cloud import storage
    HAS_GOOGLE_STORAGE = True
except Exception:  # pragma: no cover - optional dependency
    storage = None
    HAS_GOOGLE_STORAGE = False

try:
    from google.cloud import firestore
    HAS_FIRESTORE = True
except Exception:  # pragma: no cover - optional dependency
    firestore = None
    HAS_FIRESTORE = False

try:
    from google.cloud import bigquery
    HAS_BIGQUERY = True
except Exception:  # pragma: no cover - optional dependency
    bigquery = None
    HAS_BIGQUERY = False

try:
    from google.cloud import pubsub_v1
    HAS_PUBSUB = True
except Exception:  # pragma: no cover - optional dependency
    pubsub_v1 = None
    HAS_PUBSUB = False

try:
    from google.cloud import aiplatform
    HAS_VERTEX = True
except Exception:  # pragma: no cover - optional dependency
    aiplatform = None
    HAS_VERTEX = False

# Basic stdout logging works with Cloud Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration values read from environment
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
GCS_BUCKET = os.getenv("GCS_BUCKET", "")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "")
FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "agent_states")
VERTEX_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")


# ------------------------------
# Storage helpers
# ------------------------------
def upload_bytes(blob_name: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
    """Upload data to Cloud Storage and return the public URL."""
    if not HAS_GOOGLE_STORAGE:
        raise ImportError("google-cloud-storage is required for upload_bytes")
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
    logger.info("Uploaded %s to GCS bucket %s", blob_name, GCS_BUCKET)
    return blob.public_url


def download_bytes(blob_name: str) -> bytes:
    """Download data from Cloud Storage."""
    if not HAS_GOOGLE_STORAGE:
        raise ImportError("google-cloud-storage is required for download_bytes")
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(blob_name)
    logger.info("Downloading %s from GCS bucket %s", blob_name, GCS_BUCKET)
    return blob.download_as_bytes()


# ------------------------------
# Firestore and BigQuery state persistence
# ------------------------------
def save_state(agent_id: str, state: Dict[str, Any]) -> None:
    """Persist agent state to Firestore."""
    if not HAS_FIRESTORE:
        raise ImportError("google-cloud-firestore is required for save_state")
    db = firestore.Client()
    db.collection(FIRESTORE_COLLECTION).document(agent_id).set(state)
    logger.info("Saved agent state for %s", agent_id)


def load_state(agent_id: str) -> Optional[Dict[str, Any]]:
    """Load agent state from Firestore."""
    if not HAS_FIRESTORE:
        raise ImportError("google-cloud-firestore is required for load_state")
    db = firestore.Client()
    doc = db.collection(FIRESTORE_COLLECTION).document(agent_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def save_state_bq(agent_id: str, state: Dict[str, Any]) -> None:
    """Insert agent state into BigQuery."""
    if not HAS_BIGQUERY:
        raise ImportError("google-cloud-bigquery is required for save_state_bq")
    table_id = f"{PROJECT_ID}.mindlink.agent_states"
    rows: Iterable[dict[str, Any]] = [{**state, "agent_id": agent_id}]
    client = bigquery.Client()
    errors = client.insert_rows_json(table_id, list(rows))
    if errors:
        logger.error("BigQuery insert errors: %s", errors)
    else:
        logger.info("Saved agent state for %s to BigQuery", agent_id)


# ------------------------------
# Pub/Sub events
# ------------------------------
def publish_event(event: Dict[str, Any]) -> None:
    """Publish an event dictionary to a Pub/Sub topic."""
    if not HAS_PUBSUB:
        raise ImportError("google-cloud-pubsub is required for publish_event")
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
    future = publisher.publish(topic_path, data=str(event).encode("utf-8"))
    logger.info("Published event: %s", event)
    return future.result()


# ------------------------------
# Vertex AI wrapper
# ------------------------------
class VertexAILLM:
    """Simplified interface to Vertex AI text models."""

    def __init__(self, *, project: str = PROJECT_ID, location: str = VERTEX_LOCATION, model: str = "text-bison") -> None:
        if not HAS_VERTEX:
            raise ImportError("google-cloud-aiplatform is required for VertexAILLM")
        self.project = project
        self.location = location
        self.model = model
        aiplatform.init(project=project, location=location)
        self.endpoint = aiplatform.TextGenerationModel.from_pretrained(model)

    def query(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 256) -> str:
        response = self.endpoint.predict(prompt, temperature=temperature, max_output_tokens=max_tokens)
        logger.info("Queried Vertex AI model %s", self.model)
        return response.text


# ------------------------------
# Observability helpers
# ------------------------------
def log_agent_event(event_type: str, agent_id: str, details: Dict[str, Any]) -> None:
    """Log an agent-related event."""
    logger.info("[%s] Agent: %s | Details: %s", event_type, agent_id, details)


# ------------------------------
# Optional FastAPI health check
# ------------------------------
if HAS_FASTAPI:
    app = FastAPI()

    @app.get("/healthz")
    async def healthz() -> JSONResponse:
        return JSONResponse({"status": "ok"})
else:  # pragma: no cover - API optional
    app = None


async def main() -> None:
    """Example asynchronous entrypoint."""
    logger.info("Mindlink helper module started")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    if app is not None:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    else:
        asyncio.run(main())
