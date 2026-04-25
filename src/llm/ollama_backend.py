from __future__ import annotations

from typing import Any, Mapping

import requests

from src.llm.base import LLMBackend


class OllamaBackend(LLMBackend):
    """LLM backend for a local Ollama server."""

    def __init__(
        self,
        model_name: str = "llama3.1:8b",
        url: str = "http://localhost:11434/api/generate",
        timeout_seconds: int = 30,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        self.model_name = model_name
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.options = dict(options or {})

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using Ollama's `/api/generate` endpoint."""
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
        }
        if self.options:
            payload["options"] = self.options

        try:
            response = requests.post(self.url, json=payload, timeout=self.timeout_seconds)
        except requests.Timeout as exc:
            raise TimeoutError(f"Ollama request timed out after {self.timeout_seconds} seconds.") from exc
        response.raise_for_status()

        data = response.json()
        return str(data.get("response", ""))


def tags_url_from_generate_url(generate_url: str) -> str:
    """Return the Ollama tags endpoint for a generate endpoint URL."""
    if generate_url.endswith("/api/generate"):
        return generate_url[: -len("/api/generate")] + "/api/tags"
    return generate_url.rstrip("/") + "/api/tags"


def list_local_models(generate_url: str, timeout_seconds: int = 10) -> list[str]:
    """List locally available Ollama models.

    Raises:
        RuntimeError: If Ollama is not reachable or returns an invalid response.
    """
    tags_url = tags_url_from_generate_url(generate_url)
    try:
        response = requests.get(tags_url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Ollama is not reachable. Start Ollama locally and verify "
            f"{tags_url} is accessible."
        ) from exc

    payload = response.json()
    models = payload.get("models", [])
    if not isinstance(models, list):
        raise RuntimeError("Ollama /api/tags returned an unexpected response format.")

    names = [str(model.get("name", "")) for model in models if isinstance(model, dict)]
    return [name for name in names if name]


def select_ollama_model(
    requested_model: str,
    fallback_model: str | None,
    available_models: list[str],
) -> str:
    """Select requested Ollama model or configured fallback from local models."""
    if requested_model in available_models:
        return requested_model

    if fallback_model and fallback_model in available_models:
        print(
            f"Requested Ollama model '{requested_model}' is not installed; "
            f"falling back to '{fallback_model}'."
        )
        return fallback_model

    available = ", ".join(available_models) if available_models else "none"
    fallback_text = f" or fallback '{fallback_model}'" if fallback_model else ""
    raise RuntimeError(
        f"Neither requested Ollama model '{requested_model}'{fallback_text} is available locally. "
        f"Installed models: {available}. Run `ollama pull {requested_model}`"
        + (f" or `ollama pull {fallback_model}`." if fallback_model else ".")
    )
