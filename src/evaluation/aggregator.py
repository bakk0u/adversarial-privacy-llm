from __future__ import annotations

from collections import defaultdict
from typing import Dict, List


def aggregate_by_strategy(result_rows: List[dict]) -> List[dict]:
    grouped: Dict[str, dict] = defaultdict(
        lambda: {
            "strategy_name": "",
            "num_cases": 0,
            "num_leaks": 0,
            "total_leakage_score": 0.0,
            "total_utility_score": 0.0,
        }
    )

    for row in result_rows:
        strategy = row["strategy_name"]
        grouped[strategy]["strategy_name"] = strategy
        grouped[strategy]["num_cases"] += 1
        grouped[strategy]["num_leaks"] += int(bool(row["leakage_detected"]))
        grouped[strategy]["total_leakage_score"] += float(row["leakage_score"])
        grouped[strategy]["total_utility_score"] += float(row["utility_score"])

    aggregated = []
    for strategy, values in grouped.items():
        num_cases = values["num_cases"]
        aggregated.append(
            {
                "strategy_name": strategy,
                "num_cases": num_cases,
                "num_leaks": values["num_leaks"],
                "leakage_rate": round(values["num_leaks"] / num_cases, 4) if num_cases else 0.0,
                "avg_leakage_score": round(values["total_leakage_score"] / num_cases, 4) if num_cases else 0.0,
                "avg_utility_score": round(values["total_utility_score"] / num_cases, 4) if num_cases else 0.0,
            }
        )

    aggregated.sort(key=lambda row: row["strategy_name"])
    return aggregated