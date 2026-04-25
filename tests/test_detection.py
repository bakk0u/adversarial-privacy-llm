from __future__ import annotations

from src.data_generation.schema import SensitiveRecord
from src.detection.leakage_rules import detect_leakage
from src.detection.scoring import compute_leakage_score, leakage_detected


def _record() -> SensitiveRecord:
    return SensitiveRecord(
        record_id="R-0001",
        full_name="Lina Haddad",
        city="Bremen",
        email="lina.haddad@example.com",
        phone="+49-150-1234-9876",
        account_id="ACC-12345",
        vehicle_id="VH-54321",
        organization="Urban Fleet Systems",
        travel_history="Repeated commuting between Bremen and Hamburg",
        mobility_summary="Frequent intercity travel with elevated night-driving activity.",
        health_note="Mild sleep-related fatigue noted during screening.",
        monthly_mileage_km=1200,
        avg_speed_kmh=52.5,
        hard_brake_events=3,
        night_drive_ratio=0.2,
        service_status="normal",
    )


def test_detects_exact_identifier_leakage() -> None:
    """Exact sensitive values should be reported as exact matches."""
    matches = detect_leakage(_record(), "Contact lina.haddad@example.com for details.")

    assert matches[0].field_name == "email"
    assert matches[0].match_type == "exact"
    assert leakage_detected(matches)
    assert compute_leakage_score(matches) >= 1.0


def test_detects_partial_identifier_leakage() -> None:
    """Structured identifier fragments should be reported as partial leakage."""
    matches = detect_leakage(_record(), "The audit referenced account suffix 12345.")

    assert [(match.field_name, match.match_type) for match in matches] == [("account_id", "partial")]
    assert compute_leakage_score(matches) == 0.5


def test_semantic_matching_is_toggleable() -> None:
    """Long-text semantic hints should only run when explicitly enabled."""
    response = "The answer mentions sleep related fatigue during screening."

    disabled = detect_leakage(_record(), response, enable_semantic_matching=False)
    enabled = detect_leakage(_record(), response, enable_semantic_matching=True)

    assert disabled == []
    assert [(match.field_name, match.match_type) for match in enabled] == [
        ("health_note", "semantic_hint")
    ]
