# In agisa_sac/persistence/firestore.py

from ..utils.logger import get_logger

logger = get_logger(__name__)


class FirestoreClient:
    """Mock Firestore client for saving agent cognitive profiles."""

    def __init__(self):
        logger.debug("[MockFirestore] Firestore client initialized")

    async def update_document(self, path: str, data: dict):
        """
        Mock update method that simulates persisting data to Firestore.

        Args:
            path: Document path (e.g., "agents/agent_0")
            data: Dictionary of data to persist

        In production, this would actually write to Google Cloud Firestore.
        """
        logger.debug(f"[MockFirestore] update {path}: {list(data.keys())}")
