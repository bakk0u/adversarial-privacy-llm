from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import List

from src.data_generation.schema import SensitiveRecord
from src.data_generation.templates import (
    CITIES,
    FIRST_NAMES,
    HEALTH_NOTES,
    LAST_NAMES,
    MOBILITY_SUMMARIES,
    ORGANIZATIONS,
    SERVICE_STATUSES,
    TRAVEL_PATTERNS,
)
from src.utils import ensure_parent_dir, write_json


class SyntheticRecordGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)

    def _choice(self, values: List[str]) -> str:
        return self.random.choice(values)

    def _sample_distinct_cities(self, k: int = 3) -> List[str]:
        return self.random.sample(CITIES, k=k)

    def _make_full_name(self) -> str:
        return f"{self._choice(FIRST_NAMES)} {self._choice(LAST_NAMES)}"

    def _make_email(self, full_name: str) -> str:
        first, last = full_name.lower().split()
        domain = self.random.choice(["example.com", "mail.com", "synthetic.org"])
        return f"{first}.{last}@{domain}"

    def _make_phone(self) -> str:
        part1 = self.random.randint(150, 179)
        part2 = self.random.randint(1000, 9999)
        part3 = self.random.randint(1000, 9999)
        return f"+49-{part1}-{part2}-{part3}"

    def _make_account_id(self) -> str:
        return f"ACC-{self.random.randint(10000, 99999)}"

    def _make_vehicle_id(self) -> str:
        return f"VH-{self.random.randint(10000, 99999)}"

    def _make_travel_history(self) -> str:
        city1, city2, city3 = self._sample_distinct_cities(3)
        template = self._choice(TRAVEL_PATTERNS)
        return template.format(city1=city1, city2=city2, city3=city3)

    def _make_mobility_summary(self) -> str:
        return self._choice(MOBILITY_SUMMARIES)

    def _make_health_note(self) -> str:
        return self._choice(HEALTH_NOTES)

    def _make_monthly_mileage_km(self) -> int:
        return self.random.randint(600, 3200)

    def _make_avg_speed_kmh(self) -> float:
        return round(self.random.uniform(28.0, 92.0), 1)

    def _make_hard_brake_events(self) -> int:
        return self.random.randint(0, 18)

    def _make_night_drive_ratio(self) -> float:
        return round(self.random.uniform(0.05, 0.55), 2)

    def generate_record(self, index: int) -> SensitiveRecord:
        full_name = self._make_full_name()

        return SensitiveRecord(
            record_id=f"R-{index:04d}",
            full_name=full_name,
            city=self._choice(CITIES),
            email=self._make_email(full_name),
            phone=self._make_phone(),
            account_id=self._make_account_id(),
            vehicle_id=self._make_vehicle_id(),
            organization=self._choice(ORGANIZATIONS),
            travel_history=self._make_travel_history(),
            mobility_summary=self._make_mobility_summary(),
            health_note=self._make_health_note(),
            monthly_mileage_km=self._make_monthly_mileage_km(),
            avg_speed_kmh=self._make_avg_speed_kmh(),
            hard_brake_events=self._make_hard_brake_events(),
            night_drive_ratio=self._make_night_drive_ratio(),
            service_status=self._choice(SERVICE_STATUSES),
        )

    def generate_dataset(self, size: int) -> List[SensitiveRecord]:
        if size <= 0:
            raise ValueError("Dataset size must be greater than zero.")
        return [self.generate_record(index=i) for i in range(1, size + 1)]


def export_records_to_csv(records: List[SensitiveRecord], output_path: Path) -> None:
    if not records:
        raise ValueError("No records provided for CSV export.")

    ensure_parent_dir(output_path)

    fieldnames = list(records[0].to_dict().keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())


def export_records_to_json(records: List[SensitiveRecord], output_path: Path) -> None:
    payload = [record.to_dict() for record in records]
    write_json(output_path, payload, indent=2)