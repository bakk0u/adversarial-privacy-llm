from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

from src.utils import ensure_parent_dir, write_json


def export_rows_to_csv(rows: Iterable[Mapping], output_path: Path) -> None:
    """Export a non-empty iterable of dictionaries to CSV."""
    rows = list(rows)
    if not rows:
        raise ValueError("No rows provided for CSV export.")

    ensure_parent_dir(output_path)

    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_rows_to_json(rows: Iterable[Mapping], output_path: Path) -> None:
    """Export rows to JSON."""
    write_json(output_path, list(rows), indent=2)
