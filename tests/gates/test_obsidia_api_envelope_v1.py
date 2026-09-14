from apps.obsidia_api.output_envelope import (
    build_output_envelope,
    verify_envelope_invariants,
)


def test_envelope_core_authority_is_kx108_only():
    x = build_output_envelope({"hello": "world"})
    verify_envelope_invariants(x)

    assert x["decision_authority"] == "KX108_ONLY"
    assert x["emits_act"] is False
    assert x["allowed_to_decide"] is False


def test_envelope_cannot_be_overridden():
    x = build_output_envelope(
        {
            "decision_authority": "BRODY",
            "emits_act": True,
            "memory_write": True,
        }
    )

    assert x["decision_authority"] == "KX108_ONLY"
    assert x["emits_act"] is False
    assert x["memory_write"] is False


def test_envelope_blocks_write_surface():
    x = build_output_envelope(
        {
            "graphiti_write": True,
            "neo4j_write": True,
            "kernel_mutation": True,
        }
    )

    assert x["graphiti_write"] is False
    assert x["neo4j_write"] is False
    assert x["kernel_mutation"] is False


def test_envelope_readonly_flag():
    x = build_output_envelope({})
    assert x["readonly"] is True