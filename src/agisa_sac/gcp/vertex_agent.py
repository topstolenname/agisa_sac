"""Wrapper class to interact with Vertex AI models."""

from __future__ import annotations

try:
    from google.cloud import aiplatform

    HAS_VERTEX_AI = True
except Exception:  # pragma: no cover - optional dependency
    aiplatform = None
    HAS_VERTEX_AI = False
from typing import Any

if HAS_VERTEX_AI:
    aiplatform.init()


class VertexAgent:
    """Simple proxy to call Vertex AI text models."""

    def __init__(self, model: str = "text-bison") -> None:
        if not HAS_VERTEX_AI:
            raise ImportError(
                "google-cloud-aiplatform is required for VertexAgent"
            )
        self.model = model
        self.endpoint = aiplatform.TextGenerationModel.from_pretrained(model)

    def generate(self, prompt: str, **params: Any) -> str:
        response = self.endpoint.predict(prompt, **params)
        return response.text
