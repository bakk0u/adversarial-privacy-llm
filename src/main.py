from __future__ import annotations

from pathlib import Path

from src.config import PROJECT_ROOT
from src.evaluation.runner import run_experiment
from src.utils import ensure_parent_dir
from src.visualization.plots import (
    plot_avg_leakage_score,
    plot_avg_utility_score,
    plot_leakage_rate,
    plot_privacy_utility_scatter,
)


def write_findings_report(strategy_rows: list[dict], output_path: Path) -> None:
    ensure_parent_dir(output_path)

    by_leakage = sorted(strategy_rows, key=lambda row: row["avg_leakage_score"])
    by_utility = sorted(strategy_rows, key=lambda row: row["avg_utility_score"], reverse=True)

    best_privacy = by_leakage[0]
    worst_privacy = by_leakage[-1]
    best_utility = by_utility[0]

    lines = [
        "# Experimental Findings",
        "",
        "## Overview",
        "This report summarizes the results of a synthetic adversarial privacy evaluation pipeline for LLM prompting strategies.",
        "",
        "## Key Observations",
        f"- Lowest average leakage score: **{best_privacy['strategy_name']}** ({best_privacy['avg_leakage_score']}).",
        f"- Highest average leakage score: **{worst_privacy['strategy_name']}** ({worst_privacy['avg_leakage_score']}).",
        f"- Highest average utility score: **{best_utility['strategy_name']}** ({best_utility['avg_utility_score']}).",
        "",
        "## Strategy Table",
        "",
        "| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for row in strategy_rows:
        lines.append(
            f"| {row['strategy_name']} | {row['num_cases']} | {row['num_leaks']} | "
            f"{row['leakage_rate']} | {row['avg_leakage_score']} | {row['avg_utility_score']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "These results should be interpreted primarily as a validation of the experimental pipeline under a synthetic mock backend.",
            "The current setup is useful for testing data flow, prompt construction, leakage detection, scoring, aggregation, and visualization.",
            "Stronger scientific conclusions should be based on future runs with real local or API-backed LLMs.",
            "",
            "## Limitations",
            "- The backend used here is synthetic and rule-based.",
            "- Leakage detection is heuristic and may over- or under-estimate some cases.",
            "- Utility is measured using a lightweight proxy rather than human judgment.",
            "",
            "## Next Steps",
            "- Run the same framework against Ollama-backed local models.",
            "- Refine leakage detection for semantic leakage.",
            "- Add per-attack and per-task breakdown plots.",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result_rows, strategy_rows = run_experiment()

    plots_dir = PROJECT_ROOT / "results" / "plots"
    report_path = PROJECT_ROOT / "results" / "reports" / "findings.md"

    plot_leakage_rate(strategy_rows, plots_dir / "leakage_rate_by_strategy.png")
    plot_avg_leakage_score(strategy_rows, plots_dir / "avg_leakage_score_by_strategy.png")
    plot_avg_utility_score(strategy_rows, plots_dir / "avg_utility_score_by_strategy.png")
    plot_privacy_utility_scatter(strategy_rows, plots_dir / "privacy_utility_tradeoff.png")

    write_findings_report(strategy_rows, report_path)

    print(f"Completed {len(result_rows)} experiment cases.\n")
    print("=== Strategy Summary ===")
    for row in strategy_rows:
        print(row)

    print("\nGenerated artifacts:")
    print(PROJECT_ROOT / "results" / "plots" / "leakage_rate_by_strategy.png")
    print(PROJECT_ROOT / "results" / "plots" / "avg_leakage_score_by_strategy.png")
    print(PROJECT_ROOT / "results" / "plots" / "avg_utility_score_by_strategy.png")
    print(PROJECT_ROOT / "results" / "plots" / "privacy_utility_tradeoff.png")
    print(PROJECT_ROOT / "results" / "reports" / "findings.md")


if __name__ == "__main__":
    main()