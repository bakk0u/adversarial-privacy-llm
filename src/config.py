from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_experiment_config(config_path: str | Path | None = None) -> Dict[str, Any]:
    """Load experiment configuration from disk.

    Args:
        config_path: Optional path to a config file. Relative paths are resolved
            from the project root.
    """
    if config_path is None:
        return load_json(CONFIG_DIR / "experiment_config.json")

    path = Path(config_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return load_json(path)


def load_field_weights() -> Dict[str, float]:
    """Load field-level leakage weights."""
    raw = load_json(CONFIG_DIR / "field_weights.json")
    return {str(key): float(value) for key, value in raw.items()}
