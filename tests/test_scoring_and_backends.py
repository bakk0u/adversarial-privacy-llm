from __future__ import annotations

from src.detection.utility import compute_utility_score
from src.llm.factory import build_backend
from src.llm.mock_backend import MockLLMBackend
from src.llm.ollama_backend import OllamaBackend, select_ollama_model
from src.tasks.benign_tasks import BenignTaskType


def test_utility_score_rewards_task_relevant_response() -> None:
    """Task-aware responses should score higher than empty or irrelevant text."""
    useful = (
        "The record indicates a usage pattern with moderate mobility activity. "
        "Continued monitoring would be beneficial."
    )

    assert compute_utility_score(BenignTaskType.ANOMALY_DETECTION, useful) > 0.5
    assert compute_utility_score(BenignTaskType.ANOMALY_DETECTION, "") == 0.0


def test_mock_backend_strategy_probabilities_are_distinct() -> None:
    """Mock strategy probabilities should not collapse privacy-aware prompts."""
    backend = MockLLMBackend(base_leak_probability=0.6, seed=42)

    baseline = backend._leak_probability("You are a helpful analytical assistant.")
    tree = backend._leak_probability("You are privacy-aware. Use tree reasoning internally.")
    skeleton = backend._leak_probability("You are privacy-aware. Use a skeleton internally.")

    assert baseline > skeleton > tree


def test_backend_factory_selects_mock_and_ollama(monkeypatch) -> None:
    """The backend factory should select implementations from config."""
    monkeypatch.setattr("src.llm.factory.list_local_models", lambda generate_url, timeout_seconds: ["llama3:8b"])

    mock_spec = build_backend(
        {"model_backend": {"type": "mock", "model_name": "mock"}},
        seed=42,
    )
    ollama_spec = build_backend(
        {"model_backend": {"type": "ollama", "model_name": "llama3:8b"}},
        seed=42,
    )

    assert isinstance(mock_spec.backend, MockLLMBackend)
    assert mock_spec.model_name == "mock"
    assert isinstance(ollama_spec.backend, OllamaBackend)
    assert ollama_spec.model_name == "llama3:8b"


def test_select_ollama_model_uses_fallback_when_requested_missing() -> None:
    """Fallback model selection should be deterministic and testable without Ollama."""
    selected = select_ollama_model(
        requested_model="llama3.1:8b",
        fallback_model="deepseek-r1:8b",
        available_models=["deepseek-r1:8b"],
    )

    assert selected == "deepseek-r1:8b"
