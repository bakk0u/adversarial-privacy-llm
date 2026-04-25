from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


def get_git_commit(project_root: Path) -> str | None:
    """Return the current git commit hash if the repository is available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    commit = result.stdout.strip()
    return commit or None


def build_run_metadata(
    *,
    config: Mapping[str, Any],
    project_root: Path,
    seed: int,
    num_records: int,
    num_cases: int,
    backend_type: str,
    model_name: str,
    requested_model_name: str | None = None,
    fallback_model_name: str | None = None,
) -> Dict[str, Any]:
    """Build reproducibility metadata for an experiment run."""
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(project_root),
        "random_seed": seed,
        "num_records": num_records,
        "num_cases": num_cases,
        "backend_type": backend_type,
        "model_name": model_name,
        "requested_model_name": requested_model_name or model_name,
        "fallback_model_name": fallback_model_name,
        "config_snapshot": dict(config),
    }
