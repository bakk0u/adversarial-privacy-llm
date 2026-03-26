from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_experiment_config() -> Dict[str, Any]:
    return load_json(CONFIG_DIR / "experiment_config.json")


def load_field_weights() -> Dict[str, float]:
    raw = load_json(CONFIG_DIR / "field_weights.json")
    return {str(key): float(value) for key, value in raw.items()}