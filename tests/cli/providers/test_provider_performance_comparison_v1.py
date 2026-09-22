import pytest

from scripts.providers.provider_performance_comparison_v1 import (
    ProviderPerformanceComparison,
    ProviderPerformanceComparisonError,
)


def build_comparison():

    return ProviderPerformanceComparison()


def test_initial_invariants():

    comparison = build_comparison()

    assert comparison.decision_authority is False
    assert comparison.execution_authority is False
    assert comparison.memory_write is False
    assert comparison.kernel_mutation is False
    assert comparison.emits_act is False


def test_compare_performance_receipts():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody",
                "latency_ms": 100,
                "compute_cost": 0.2,
            },
            {
                "provider_id": "provider-b",
                "latency_ms": 200,
                "compute_cost": 0.5,
            },
        ]
    )

    assert result["providers_compared"] == 2
    assert result["comparison_only"] is True


def test_receipts_preserved():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody",
                "latency_ms": 50,
            }
        ]
    )

    assert result["receipts"][0]["provider_id"] == "brody"


def test_empty_receipts_blocked():

    comparison = build_comparison()

    with pytest.raises(
        ProviderPerformanceComparisonError
    ):

        comparison.compare([])


def test_no_decision_output():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody"
            }
        ]
    )

    assert "decision" not in result
