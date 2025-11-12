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

    def __init__(self, model: str = "gemini-pro") -> None:
        if not HAS_VERTEX_AI:
            raise ImportError(
                "google-cloud-aiplatform is required for VertexAgent"
            )
        self.model = model
        # Use GenerativeModel for Gemini models, fallback to TextGenerationModel for legacy
        if model.startswith("gemini"):
            from google.cloud.aiplatform import generative_models
            self.endpoint = generative_models.GenerativeModel(model)
        else:
            self.endpoint = aiplatform.TextGenerationModel.from_pretrained(model)

    def generate(self, prompt: str, **params: Any) -> str:
        """Generate text using the configured model with error handling.

        Args:
            prompt: The input prompt for text generation
            **params: Additional parameters for the model

        Returns:
            Generated text string

        Raises:
            RuntimeError: If prediction fails
        """
        try:
            if self.model.startswith("gemini"):
                # Gemini models use generate_content
                response = self.endpoint.generate_content(prompt, **params)
            else:
                # Legacy text-bison models use predict
                response = self.endpoint.predict(prompt, **params)
            return response.text
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate text with model {self.model}: {e}"
            ) from e
