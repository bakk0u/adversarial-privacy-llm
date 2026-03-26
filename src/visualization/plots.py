from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

from src.utils import ensure_parent_dir


def _extract(strategy_rows: List[dict], key: str) -> tuple[list[str], list[float]]:
    names = [row["strategy_name"] for row in strategy_rows]
    values = [float(row[key]) for row in strategy_rows]
    return names, values


def plot_leakage_rate(strategy_rows: List[dict], output_path: Path) -> None:
    names, values = _extract(strategy_rows, "leakage_rate")
    ensure_parent_dir(output_path)

    plt.figure(figsize=(10, 6))
    plt.bar(names, values)
    plt.title("Leakage Rate by Strategy")
    plt.xlabel("Strategy")
    plt.ylabel("Leakage Rate")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_avg_leakage_score(strategy_rows: List[dict], output_path: Path) -> None:
    names, values = _extract(strategy_rows, "avg_leakage_score")
    ensure_parent_dir(output_path)

    plt.figure(figsize=(10, 6))
    plt.bar(names, values)
    plt.title("Average Leakage Score by Strategy")
    plt.xlabel("Strategy")
    plt.ylabel("Average Leakage Score")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_avg_utility_score(strategy_rows: List[dict], output_path: Path) -> None:
    names, values = _extract(strategy_rows, "avg_utility_score")
    ensure_parent_dir(output_path)

    plt.figure(figsize=(10, 6))
    plt.bar(names, values)
    plt.title("Average Utility Score by Strategy")
    plt.xlabel("Strategy")
    plt.ylabel("Average Utility Score")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_privacy_utility_scatter(strategy_rows: List[dict], output_path: Path) -> None:
    ensure_parent_dir(output_path)

    x = [float(row["avg_leakage_score"]) for row in strategy_rows]
    y = [float(row["avg_utility_score"]) for row in strategy_rows]
    labels = [row["strategy_name"] for row in strategy_rows]

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y)

    for x_i, y_i, label in zip(x, y, labels):
        plt.annotate(label, (x_i, y_i), xytext=(5, 5), textcoords="offset points")

    plt.title("Privacy-Utility Tradeoff")
    plt.xlabel("Average Leakage Score")
    plt.ylabel("Average Utility Score")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()