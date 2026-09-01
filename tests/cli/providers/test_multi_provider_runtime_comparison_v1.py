import pytest

from scripts.providers.multi_provider_runtime_comparison_v1 import (
    MultiProviderRuntimeComparison,
    MultiProviderRuntimeComparisonError,
)


def build_comparison():

    return MultiProviderRuntimeComparison()


def test_authority_invariants():

    comparison = build_comparison()

    assert comparison.decision_authority is False
    assert comparison.execution_authority is False
    assert comparison.memory_write is False
    assert comparison.kernel_mutation is False
    assert comparison.emits_act is False


def test_compare_multiple_results():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody",
                "output": "answer-a",
            },
            {
                "provider_id": "claude",
                "output": "answer-b",
            },
        ]
    )

    assert result["providers_compared"] == 2
    assert result["comparison_only"] is True


def test_provider_results_preserved():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody",
                "output": "a",
            }
        ]
    )

    assert result["results"][0]["provider_id"] == "brody"


def test_empty_results_blocked():

    comparison = build_comparison()

    with pytest.raises(MultiProviderRuntimeComparisonError):

        comparison.compare([])


def test_no_decision_field():

    comparison = build_comparison()

    result = comparison.compare(
        [
            {
                "provider_id": "brody",
                "output": "a",
            }
        ]
    )

    assert "decision" not in result
