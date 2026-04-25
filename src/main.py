from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT, load_experiment_config
from src.evaluation.runner import estimate_experiment_calls, estimate_runtime_minutes, run_experiment
from src.utils import ensure_parent_dir
from src.visualization.plots import (
    plot_avg_leakage_score,
    plot_avg_utility_score,
    plot_leakage_rate,
    plot_privacy_utility_scatter,
)


def _project_path(path_value: str) -> Path:
    """Resolve a config path relative to the project root."""
    path = Path(path_value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def write_findings_report(strategy_rows: list[dict], metadata: dict[str, Any], output_path: Path) -> None:
    """Write a compact Markdown report from aggregated strategy results."""
    ensure_parent_dir(output_path)

    by_leakage = sorted(strategy_rows, key=lambda row: row["avg_leakage_score"])
    by_utility = sorted(strategy_rows, key=lambda row: row["avg_utility_score"], reverse=True)

    best_privacy = by_leakage[0]
    worst_privacy = by_leakage[-1]
    best_utility = by_utility[0]
    backend_type = metadata.get("backend_type", "unknown")
    model_name = metadata.get("model_name", "unknown")
    num_cases = metadata.get("num_cases", sum(row["num_cases"] for row in strategy_rows))

    lines = [
        "# Experimental Findings",
        "",
        "## Overview",
        "This report summarizes a synthetic adversarial privacy evaluation pipeline for LLM prompting strategies.",
        "",
        "## Run Metadata",
        f"- Backend: **{backend_type}**",
        f"- Model used: **{model_name}**",
        f"- Cases: **{num_cases}**",
        f"- Random seed: **{metadata.get('random_seed', 'unknown')}**",
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

    if backend_type == "ollama":
        lines.extend(
            [
                "",
                "## Real LLM Validation",
                f"This run validates the pipeline on a local Ollama model: **{model_name}**.",
                f"The experiment completed **{num_cases}** real LLM cases.",
                f"The best privacy-performing strategy was **{best_privacy['strategy_name']}** "
                f"with leakage rate **{best_privacy['leakage_rate']}**.",
                f"The worst privacy-performing strategy was **{worst_privacy['strategy_name']}** "
                f"with leakage rate **{worst_privacy['leakage_rate']}**.",
                f"The highest average utility score was **{best_utility['avg_utility_score']}** "
                f"for **{best_utility['strategy_name']}**.",
                "These results are a small-scale local LLM validation and should not be treated as a universal claim "
                "about all models or all privacy attacks.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Interpretation",
                "These results should be interpreted primarily as validation of the experimental pipeline under a synthetic mock backend.",
                "Real-model conclusions should be based on Ollama or API-backed runs.",
            ]
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "- Leakage detection is heuristic and may over- or under-estimate some cases.",
            "- Utility is measured using a lightweight proxy rather than human judgment.",
            "- Small local-model runs are useful validation, not final universal evidence.",
            "",
            "## Next Steps",
            "- Add per-attack and per-task breakdown plots.",
            "- Compare exact, partial, and semantic leakage patterns by field.",
            "- Add human or model-assisted utility evaluation for selected cases.",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _format_matches(row: dict) -> str:
    """Format detected leakage matches for Markdown reports."""
    matches = row.get("matches", [])
    if not matches:
        return "None"
    return ", ".join(f"{match['field_name']} ({match['match_type']})" for match in matches)


def _select_example_cases(result_rows: list[dict]) -> list[dict]:
    """Select representative baseline failure, successful defense, and partial leakage examples."""
    examples: list[dict] = []

    baseline_failure = next(
        (row for row in result_rows if row["strategy_name"] == "direct_baseline" and row["leakage_detected"]),
        None,
    )
    if baseline_failure:
        examples.append(baseline_failure)

    successful_defense = next(
        (
            row
            for row in result_rows
            if row["strategy_name"] != "direct_baseline" and not row["leakage_detected"]
        ),
        None,
    )
    if successful_defense:
        examples.append(successful_defense)

    partial_leak = next(
        (
            row
            for row in result_rows
            if any(match.get("match_type") == "partial" for match in row.get("matches", []))
        ),
        None,
    )
    if partial_leak and partial_leak not in examples:
        examples.append(partial_leak)

    for row in result_rows:
        if len(examples) >= 5:
            break
        if row not in examples:
            examples.append(row)

    return examples[:5]


def write_example_cases(result_rows: list[dict], output_path: Path) -> None:
    """Export representative case examples to Markdown."""
    ensure_parent_dir(output_path)
    lines = [
        "# Representative Example Cases",
        "",
        "Examples are selected from the latest run to show a baseline failure, a successful defense, and partial leakage when available.",
    ]

    for index, row in enumerate(_select_example_cases(result_rows), start=1):
        lines.extend(
            [
                "",
                f"## Example {index}: {row['case_id']}",
                "",
                f"- Task: `{row['task_type']}`",
                f"- Attack: `{row['attack_type']}`",
                f"- Strategy: `{row['strategy_name']}`",
                f"- Model: `{row['model_name']}`",
                f"- Detected leaked fields: {_format_matches(row)}",
                f"- Leakage score: `{row['leakage_score']}`",
                f"- Utility score: `{row['utility_score']}`",
                "",
                "Model response:",
                "",
                "```text",
                row["response_text"].strip(),
                "```",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run adversarial privacy leakage experiments.")
    parser.add_argument(
        "--config",
        default=None,
        help="Path to an experiment config JSON file. Defaults to configs/experiment_config.json.",
    )
    parser.add_argument(
        "--estimate",
        action="store_true",
        help="Print estimated call count and approximate runtime without calling an LLM.",
    )
    parser.add_argument(
        "--max_cases",
        type=int,
        default=None,
        help="Run only the first N experiment cases.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the experiment and generate reports and plots."""
    args = parse_args()
    config = load_experiment_config(args.config)
    output_paths = config["output_paths"]

    if args.max_cases is not None and args.max_cases < 1:
        raise ValueError("--max_cases must be a positive integer.")

    estimated_calls = estimate_experiment_calls(config, max_cases=args.max_cases)
    if args.estimate:
        print(f"Estimated calls: {estimated_calls}")
        print(f"Estimated runtime: {estimate_runtime_minutes(estimated_calls)} minutes (approx)")
        return

    result_rows, strategy_rows, metadata = run_experiment(config_path=args.config, max_cases=args.max_cases)

    plots_dir = _project_path(output_paths.get("plots_dir", "results/plots"))
    report_path = _project_path(output_paths.get("summary_report_md", "results/reports/findings.md"))
    example_cases_path = _project_path(output_paths.get("example_cases_md", "results/reports/example_cases.md"))

    plot_leakage_rate(strategy_rows, plots_dir / "leakage_rate_by_strategy.png")
    plot_avg_leakage_score(strategy_rows, plots_dir / "avg_leakage_score_by_strategy.png")
    plot_avg_utility_score(strategy_rows, plots_dir / "avg_utility_score_by_strategy.png")
    plot_privacy_utility_scatter(strategy_rows, plots_dir / "privacy_utility_tradeoff.png")

    write_findings_report(strategy_rows, metadata, report_path)
    write_example_cases(result_rows, example_cases_path)

    print(f"Completed {len(result_rows)} experiment cases.")
    print(f"Backend: {metadata['backend_type']}")
    print(f"Model used: {metadata['model_name']}\n")
    print("=== Strategy Summary ===")
    for row in strategy_rows:
        print(row)

    print("\nGenerated artifacts:")
    print(plots_dir / "leakage_rate_by_strategy.png")
    print(plots_dir / "avg_leakage_score_by_strategy.png")
    print(plots_dir / "avg_utility_score_by_strategy.png")
    print(plots_dir / "privacy_utility_tradeoff.png")
    print(report_path)
    print(example_cases_path)


if __name__ == "__main__":
    main()
