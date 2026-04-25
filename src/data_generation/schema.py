from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SensitivityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass(slots=True)
class SensitiveRecord:
    """
    Synthetic structured record used as the core input unit for the experiment.
    """
    record_id: str

    # Direct / quasi identifiers
    full_name: str
    city: str
    email: str
    phone: str
    account_id: str
    vehicle_id: str
    organization: str

    # Semi-sensitive contextual fields
    travel_history: str
    mobility_summary: str
    health_note: str

    # Operational / utility-oriented fields
    monthly_mileage_km: int
    avg_speed_kmh: float
    hard_brake_events: int
    night_drive_ratio: float
    service_status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def sensitive_field_values(self) -> Dict[str, str]:
        """
        Fields that should be monitored for leakage.
        Numeric operational fields are excluded from the initial detector.
        """
        return {
            "full_name": self.full_name,
            "city": self.city,
            "email": self.email,
            "phone": self.phone,
            "account_id": self.account_id,
            "vehicle_id": self.vehicle_id,
            "organization": self.organization,
            "travel_history": self.travel_history,
            "mobility_summary": self.mobility_summary,
            "health_note": self.health_note,
        }


@dataclass(slots=True)
class FieldSpec:
    name: str
    sensitivity: SensitivityLevel
    description: str
    is_direct_identifier: bool = False
    monitor_for_leakage: bool = True


FIELD_SPECS: List[FieldSpec] = [
    FieldSpec(
        name="full_name",
        sensitivity=SensitivityLevel.HIGH,
        description="Synthetic person's full name.",
        is_direct_identifier=True,
    ),
    FieldSpec(
        name="city",
        sensitivity=SensitivityLevel.LOW,
        description="City associated with the record.",
        is_direct_identifier=False,
    ),
    FieldSpec(
        name="email",
        sensitivity=SensitivityLevel.HIGH,
        description="Synthetic email address.",
        is_direct_identifier=True,
    ),
    FieldSpec(
        name="phone",
        sensitivity=SensitivityLevel.HIGH,
        description="Synthetic phone number.",
        is_direct_identifier=True,
    ),
    FieldSpec(
        name="account_id",
        sensitivity=SensitivityLevel.HIGH,
        description="Synthetic account identifier.",
        is_direct_identifier=True,
    ),
    FieldSpec(
        name="vehicle_id",
        sensitivity=SensitivityLevel.MEDIUM,
        description="Synthetic vehicle identifier.",
        is_direct_identifier=True,
    ),
    FieldSpec(
        name="organization",
        sensitivity=SensitivityLevel.LOW,
        description="Organization linked to the record.",
        is_direct_identifier=False,
    ),
    FieldSpec(
        name="travel_history",
        sensitivity=SensitivityLevel.MEDIUM,
        description="Short synthetic history of recent travel locations.",
        is_direct_identifier=False,
    ),
    FieldSpec(
        name="mobility_summary",
        sensitivity=SensitivityLevel.MEDIUM,
        description="Short synthetic summary of mobility behavior.",
        is_direct_identifier=False,
    ),
    FieldSpec(
        name="health_note",
        sensitivity=SensitivityLevel.HIGH,
        description="Semi-sensitive synthetic health-related note.",
        is_direct_identifier=False,
    ),
    FieldSpec(
        name="monthly_mileage_km",
        sensitivity=SensitivityLevel.NONE,
        description="Monthly mileage in kilometers.",
        monitor_for_leakage=False,
    ),
    FieldSpec(
        name="avg_speed_kmh",
        sensitivity=SensitivityLevel.NONE,
        description="Average speed in km/h.",
        monitor_for_leakage=False,
    ),
    FieldSpec(
        name="hard_brake_events",
        sensitivity=SensitivityLevel.NONE,
        description="Count of hard braking events.",
        monitor_for_leakage=False,
    ),
    FieldSpec(
        name="night_drive_ratio",
        sensitivity=SensitivityLevel.NONE,
        description="Fraction of driving that occurred at night.",
        monitor_for_leakage=False,
    ),
    FieldSpec(
        name="service_status",
        sensitivity=SensitivityLevel.NONE,
        description="Operational service status.",
        monitor_for_leakage=False,
    ),
]


@dataclass(slots=True)
class LeakageMatch:
    field_name: str
    field_value: str
    match_type: str  # exact | partial | semantic_hint
    score: float


@dataclass(slots=True)
class ExperimentCase:
    case_id: str
    record_id: str
    task_type: str
    attack_type: str
    strategy_name: str
    model_name: str


@dataclass(slots=True)
class ExperimentResult:
    case_id: str
    record_id: str
    task_type: str
    attack_type: str
    strategy_name: str
    model_name: str
    prompt_text: str
    response_text: str
    leakage_score: float = 0.0
    utility_score: float = 0.0
    leakage_detected: bool = False
    matches: List[LeakageMatch] = field(default_factory=list)
    generation_failed: bool = False
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["matches"] = [asdict(match) for match in self.matches]
        return payload
