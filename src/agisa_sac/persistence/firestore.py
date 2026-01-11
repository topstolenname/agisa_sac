# In agisa_sac/persistence/firestore.py
from typing import Dict


class FirestoreClient:
    """Mock Firestore client for saving agent cognitive profiles."""

    def __init__(self):
        print("[MockFirestore] Firestore client initialized")

    async def update_document(self, path: str, data: Dict):
        """
        Mock update method that simulates persisting data to Firestore.

        Args:
            path: Document path (e.g., "agents/agent_0")
            data: Dictionary of data to persist

        In production, this would actually write to Google Cloud Firestore.
        """
        print(f"[MockFirestore] update {path}: {list(data.keys())}")
