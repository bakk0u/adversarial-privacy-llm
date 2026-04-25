from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.llm.base import LLMBackend
from src.llm.mock_backend import MockLLMBackend
from src.llm.ollama_backend import OllamaBackend, list_local_models, select_ollama_model


@dataclass(frozen=True, slots=True)
class BackendSpec:
    """Resolved backend instance and model metadata."""

    backend: LLMBackend
    backend_type: str
    model_name: str
    requested_model_name: str
    fallback_model_name: str | None = None


def _ollama_options(backend_config: Mapping[str, Any], seed: int) -> dict[str, Any]:
    """Build deterministic Ollama generation options from config."""
    options: dict[str, Any] = {"seed": seed}
    for key in ("temperature", "num_ctx", "num_predict"):
        if key in backend_config:
            options[key] = backend_config[key]
    return options


def build_backend(config: Mapping[str, Any], seed: int) -> BackendSpec:
    """Build the configured LLM backend.

    Args:
        config: Experiment configuration dictionary.
        seed: Global experiment seed used by deterministic backends.

    Returns:
        Backend plus metadata about the actual model selected.

    Raises:
        ValueError: If the configured backend type is unsupported.
        RuntimeError: If Ollama is configured but unavailable or missing models.
    """
    backend_config = dict(config.get("model_backend", {}))
    backend_type = str(backend_config.get("type", config.get("default_model_name", "mock"))).lower()
    requested_model = str(backend_config.get("model_name", config.get("default_model_name", backend_type)))

    if backend_type == "mock":
        base_probability = float(backend_config.get("base_leak_probability", 0.6))
        return BackendSpec(
            backend=MockLLMBackend(base_leak_probability=base_probability, seed=seed),
            backend_type="mock",
            model_name=requested_model,
            requested_model_name=requested_model,
        )

    if backend_type == "ollama":
        url = str(backend_config.get("ollama_url", "http://localhost:11434/api/generate"))
        timeout_seconds = int(backend_config.get("timeout_seconds", 30))
        fallback_model = backend_config.get("fallback_model")
        fallback_model_name = str(fallback_model) if fallback_model else None
        available_models = list_local_models(generate_url=url, timeout_seconds=10)
        selected_model = select_ollama_model(
            requested_model=requested_model,
            fallback_model=fallback_model_name,
            available_models=available_models,
        )
        print(f"Using Ollama model: {selected_model}")
        return BackendSpec(
            backend=OllamaBackend(
                model_name=selected_model,
                url=url,
                timeout_seconds=timeout_seconds,
                options=_ollama_options(backend_config, seed=seed),
            ),
            backend_type="ollama",
            model_name=selected_model,
            requested_model_name=requested_model,
            fallback_model_name=fallback_model_name,
        )

    raise ValueError(f"Unsupported model backend type: {backend_type}")
