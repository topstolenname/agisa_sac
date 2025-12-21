"""Wrapper class to interact with Vertex AI models."""

from __future__ import annotations

from typing import Any, Optional

try:
    from google.cloud import aiplatform

    HAS_VERTEX_AI = True
except Exception:  # pragma: no cover - optional dependency
    aiplatform = None
    HAS_VERTEX_AI = False

# Optional: Docent tracing for LLM calls
try:
    from agisa_sac.observability.docent_tracing import DocentTracer
    HAS_DOCENT_TRACING = True
except ImportError:
    HAS_DOCENT_TRACING = False
    DocentTracer = None  # type: ignore

if HAS_VERTEX_AI:
    aiplatform.init()


class VertexAgent:
    """Simple proxy to call Vertex AI text models."""

    def __init__(
        self,
        model: str = "gemini-pro",
        tracer: Optional["DocentTracer"] = None
    ) -> None:
        if not HAS_VERTEX_AI:
            raise ImportError(
                "google-cloud-aiplatform is required for VertexAgent"
            )
        self.model = model
        self.tracer = tracer
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
        # Add Docent tracing if tracer is available
        if self.tracer and HAS_DOCENT_TRACING:
            with self.tracer.trace_llm_call(
                "vertex_ai_generate",
                model=self.model,
                prompt_length=len(prompt),
            ) as call:
                try:
                    if self.model.startswith("gemini"):
                        # Gemini models use generate_content
                        response = self.endpoint.generate_content(prompt, **params)
                    else:
                        # Legacy text-bison models use predict
                        response = self.endpoint.predict(prompt, **params)

                    result_text = response.text

                    # Record result (Vertex AI doesn't always provide token counts)
                    call.record_result(
                        response_content=result_text,
                        model=self.model,
                    )

                    return result_text
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to generate text with model {self.model}: {e}"
                    ) from e
        else:
            # No tracing available
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
