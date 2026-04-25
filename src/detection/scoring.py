from __future__ import annotations

from typing import Dict, List

from src.data_generation.schema import LeakageMatch
from src.config import load_field_weights


FIELD_WEIGHTS = load_field_weights()


def compute_leakage_score(matches: List[LeakageMatch]) -> float:
    """Compute weighted leakage severity for a list of matches."""
    score = 0.0

    for match in matches:
        weight = FIELD_WEIGHTS.get(match.field_name, 0.0)
        score += weight * match.score

    return round(score, 4)


def leakage_detected(matches: List[LeakageMatch]) -> bool:
    """Return whether any leakage rule matched."""
    return len(matches) > 0


def compute_field_exposure(matches: List[LeakageMatch]) -> Dict[str, int]:
    """Count matched fields by field name."""
    exposure = {}

    for match in matches:
        exposure[match.field_name] = exposure.get(match.field_name, 0) + 1

    return exposure
