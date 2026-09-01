import pytest

from scripts.providers.provider_arbitration_v0 import (
    ProviderArbitration,
    ProviderArbitrationError,
)


def build_arbitration():
    return ProviderArbitration(
        comparison_id="comparison-001"
    )


def test_initial_authority_blocked():

    arb = build_arbitration()

    assert arb.decision_authority is False
    assert arb.execution_authority is False
    assert arb.memory_write is False
    assert arb.kernel_mutation is False
    assert arb.emits_act is False


def test_compare_multiple_results():

    arb = build_arbitration()

    result = arb.compare(
        [
            {
                "provider_id": "brody",
                "result_ref": "r1",
            },
            {
                "provider_id": "claude",
                "result_ref": "r2",
            }
        ]
    )

    assert result["providers_compared"] == 2
    assert result["comparison_only"] is True


def test_compare_empty_blocked():

    arb = build_arbitration()

    with pytest.raises(ProviderArbitrationError):
        arb.compare([])


def test_results_are_preserved():

    arb = build_arbitration()

    data = [
        {
            "provider_id": "brody",
            "result_ref": "r1",
        }
    ]

    result = arb.compare(data)

    assert result["results"] == data


def test_no_decision_output():

    arb = build_arbitration()

    result = arb.compare(
        [
            {
                "provider_id": "brody",
                "result_ref": "r1",
            }
        ]
    )

    assert "decision" not in result
