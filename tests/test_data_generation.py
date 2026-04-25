from __future__ import annotations

import pytest

from src.data_generation.generator import SyntheticRecordGenerator


def test_generator_is_deterministic_for_same_seed() -> None:
    """The same seed should produce identical synthetic records."""
    first = SyntheticRecordGenerator(seed=7).generate_dataset(size=3)
    second = SyntheticRecordGenerator(seed=7).generate_dataset(size=3)

    assert [record.to_dict() for record in first] == [record.to_dict() for record in second]


def test_generator_rejects_non_positive_dataset_size() -> None:
    """Dataset size must be positive."""
    with pytest.raises(ValueError):
        SyntheticRecordGenerator(seed=7).generate_dataset(size=0)


def test_generated_record_contains_sensitive_and_operational_fields() -> None:
    """Generated records should include monitored and utility-oriented fields."""
    record = SyntheticRecordGenerator(seed=1).generate_record(index=1)

    assert record.record_id == "R-0001"
    assert record.email
    assert record.account_id.startswith("ACC-")
    assert record.monthly_mileage_km > 0
    assert "email" in record.sensitive_field_values()
    assert "monthly_mileage_km" not in record.sensitive_field_values()
