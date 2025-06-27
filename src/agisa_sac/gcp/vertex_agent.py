"""Wrapper class to interact with Vertex AI models."""
from __future__ import annotations

from google.cloud import aiplatform
from typing import Any


aiplatform.init()


class VertexAgent:
    """Simple proxy to call Vertex AI text models."""

    def __init__(self, model: str = "text-bison") -> None:
        self.model = model
        self.endpoint = aiplatform.TextGenerationModel.from_pretrained(model)

    def generate(self, prompt: str, **params: Any) -> str:
        response = self.endpoint.predict(prompt, **params)
        return response.text
