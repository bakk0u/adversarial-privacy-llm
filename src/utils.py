from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def ensure_parent_dir(path: Path) -> None:
    """Create the parent directory for a file path if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON object from disk."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any, indent: int = 2) -> None:
    """Write JSON to disk with UTF-8 encoding."""
    ensure_parent_dir(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=indent, ensure_ascii=False)
