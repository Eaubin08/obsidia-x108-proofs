"""
C2B-M2A ? MEMZUM canonical memory activation tests.

MEMZUM:
- consolidates existing cognitive signals
- is provider-neutral
- performs no retrieval
- has no decision authority
"""

from apps.obsidia_api.brody_memzum_activation_adapter import (
    evaluate_memzum_activation,
)


def _mc(*, adversarial=False):
    return {
        "is_adversarial": adversarial,
        "domain_detected": "GPS",
        "intent_type": "FOLLOWUP",
        "bio_animal_signal": {
            "memory_relevance_signal": 0.9,
        },
    }


def _bal():
    return {
        "balances": {
            "balance_memoire": {
                "tension": 0.8,
            },
        },
    }


def _pc(*, required):
    return {
        "vector_21d": {
            13: 0.8,
        },
        "memory_packet_required": required,
        "domain_detected": "GPS",
    }


def test_memzum_required_follows_existing_cognitive_signal():
    result = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=_pc(required=True),
    )

    assert result["memory_required"] is True
    assert result["reason"] == "MEMORY_REQUIRED_COGNITIVE_SIGNAL"


def test_memzum_not_required_follows_existing_cognitive_signal():
    result = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=_pc(required=False),
    )

    assert result["memory_required"] is False
    assert result["reason"] == "MEMORY_NOT_REQUIRED"


def test_memzum_adversarial_blocks_activation():
    result = evaluate_memzum_activation(
        micro_core=_mc(adversarial=True),
        balance_output=_bal(),
        point_cloud=_pc(required=True),
    )

    assert result["memory_required"] is False
    assert result["reason"] == "MEMORY_BLOCKED_ADVERSARIAL"


def test_memzum_preserves_existing_cognitive_evidence():
    result = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=_pc(required=True),
    )

    basis = result["activation_basis"]

    assert basis["memory_packet_required"] is True
    assert basis["axis_13_memory"] == 0.8
    assert basis["memory_relevance_signal"] == 0.9
    assert basis["balance_memoire_tension"] == 0.8
    assert basis["domain_detected"] == "GPS"
    assert basis["intent_type"] == "FOLLOWUP"


def test_memzum_is_provider_neutral_and_non_sovereign():
    result = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=_pc(required=True),
    )

    assert result["provider_neutral"] is True
    assert result["retrieval_performed"] is False
    assert result["readonly"] is True

    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["decision_authority"] == "KX108_ONLY"

    # Provider-specific runtime fields must not leak into MEMZUM.
    forbidden_keys = {
        "graphiti_allowed",
        "graphiti_live",
        "neo4j_status",
        "source_mode",
        "provider",
    }

    assert forbidden_keys.isdisjoint(result.keys())


def test_graphiti_noise_in_point_cloud_cannot_change_memzum():
    base = _pc(required=True)

    without_provider_noise = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=dict(base),
    )

    noisy = dict(base)
    noisy["graphiti_allowed"] = True
    noisy["graphiti_live"] = True

    with_provider_noise = evaluate_memzum_activation(
        micro_core=_mc(),
        balance_output=_bal(),
        point_cloud=noisy,
    )

    assert (
        without_provider_noise["memory_required"]
        == with_provider_noise["memory_required"]
    )

    assert (
        without_provider_noise["activation_basis"]
        == with_provider_noise["activation_basis"]
    )


def test_missing_inputs_degrade_to_memory_not_required():
    result = evaluate_memzum_activation()

    assert result["memory_required"] is False
    assert result["reason"] == "MEMORY_NOT_REQUIRED"
    assert result["decision_authority"] == "KX108_ONLY"
