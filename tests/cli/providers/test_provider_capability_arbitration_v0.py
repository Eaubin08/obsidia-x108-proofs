import pytest

from scripts.providers.provider_capability_arbitration_v0 import (
    ProviderCapabilityArbitration,
    ProviderCapabilityArbitrationError,
)


def build_arbitration():

    return ProviderCapabilityArbitration(
        comparison_id="capability-comparison-001"
    )


def providers():

    return [
        {
            "provider_id": "brody",
            "capabilities": [
                "reasoning",
                "analysis",
            ],
        },
        {
            "provider_id": "obsidure",
            "capabilities": [
                "formal_proof",
                "verification",
            ],
        },
    ]


def test_authority_is_blocked():

    arb = build_arbitration()

    assert arb.decision_authority is False
    assert arb.execution_authority is False
    assert arb.memory_write is False
    assert arb.kernel_mutation is False
    assert arb.emits_act is False


def test_capability_match():

    arb = build_arbitration()

    result = arb.compare_capabilities(
        "formal_proof",
        providers()
    )

    assert result["requested_capability"] == "formal_proof"
    assert len(result["compatible_providers"]) == 1
    assert result["compatible_providers"][0]["provider_id"] == "obsidure"


def test_multiple_matches():

    arb = build_arbitration()

    result = arb.compare_capabilities(
        "reasoning",
        [
            {
                "provider_id": "brody",
                "capabilities": ["reasoning"],
            },
            {
                "provider_id": "claude",
                "capabilities": ["reasoning"],
            },
        ]
    )

    assert len(result["compatible_providers"]) == 2


def test_missing_capability_blocked():

    arb = build_arbitration()

    with pytest.raises(ProviderCapabilityArbitrationError):

        arb.compare_capabilities(
            "",
            providers()
        )


def test_empty_provider_list_blocked():

    arb = build_arbitration()

    with pytest.raises(ProviderCapabilityArbitrationError):

        arb.compare_capabilities(
            "reasoning",
            []
        )
