from __future__ import annotations

import pytest

from src.config import PROJECT_ROOT, load_experiment_config
from src.evaluation.runner import estimate_experiment_calls, run_experiment
from src.evaluation.metadata import build_run_metadata


def test_load_experiment_config_from_custom_path() -> None:
    """A custom config path should load instead of the default config."""
    config = load_experiment_config("configs/ollama_experiment_config.json")

    assert config["model_backend"]["type"] == "ollama"
    assert config["model_backend"]["model_name"] == "llama3.1:8b"
    assert config["dataset_size"] == 10


def test_light_ollama_config_is_laptop_sized() -> None:
    """The lightweight Ollama config should stay within the local LLM call cap."""
    config = load_experiment_config("configs/ollama_light_config.json")

    assert config["dataset_size"] == 5
    assert config["model_backend"]["temperature"] == 0.1
    assert config["model_backend"]["num_predict"] == 60
    assert config["model_backend"]["timeout_seconds"] == 30
    assert estimate_experiment_calls(config) == 60


def test_tiny_ollama_config_is_six_calls() -> None:
    """The tiny Ollama config should provide the smallest real-model validation."""
    config = load_experiment_config("configs/ollama_tiny_config.json")

    assert config["dataset_size"] == 2
    assert config["task_types"] == ["summarization"]
    assert config["attack_types"] == ["direct_extraction"]
    assert config["strategy_types"] == [
        "direct_baseline",
        "policy_first_structured",
        "tree_of_thoughts",
    ]
    assert config["model_backend"]["timeout_seconds"] == 90
    assert config["model_backend"]["num_ctx"] == 1024
    assert config["model_backend"]["num_predict"] == 40
    assert estimate_experiment_calls(config) == 6


def test_oversized_ollama_run_fails_before_backend_setup() -> None:
    """Oversized real-LLM runs should fail without contacting Ollama."""
    with pytest.raises(ValueError, match="Experiment too large for local execution. Reduce config."):
        run_experiment("configs/ollama_experiment_config.json")


def test_metadata_includes_backend_and_model_fields() -> None:
    """Run metadata should record backend and actual/requested/fallback model names."""
    metadata = build_run_metadata(
        config={"model_backend": {"type": "ollama"}},
        project_root=PROJECT_ROOT,
        seed=42,
        num_records=10,
        num_cases=600,
        backend_type="ollama",
        model_name="deepseek-r1:8b",
        requested_model_name="llama3.1:8b",
        fallback_model_name="deepseek-r1:8b",
    )

    assert metadata["backend_type"] == "ollama"
    assert metadata["model_name"] == "deepseek-r1:8b"
    assert metadata["requested_model_name"] == "llama3.1:8b"
    assert metadata["fallback_model_name"] == "deepseek-r1:8b"
