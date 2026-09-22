from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)


def test_lexical_unknown_reaches_context_packet_v2_once():
    result = run_real_cognitive_join(
        message="explique le florvaxium",
        language="fr",
        session_id="lexical-unknown-e2e",
    )

    assert (
        result["status"]
        == "READY_SHADOW_READONLY"
    )

    reverse_ir = (
        result["reverse_os_projection"][
            "ir_candidate"
        ]
    )

    assert reverse_ir["unknowns"] == [
        "florvaxium"
    ]

    packet = result[
        "context_packet_v2"
    ]

    assert packet["unknowns"] == [
        "florvaxium"
    ]

    assert (
        packet["unknowns"].count(
            "florvaxium"
        )
        == 1
    )

    assert packet["readonly"] is True
    assert (
        packet["decision_authority"]
        == "KX108_ONLY"
    )
    assert packet["memory_write"] is False
    assert packet["kernel_mutation"] is False

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["allowed_to_act"] is False
    assert result["real_execution"] is False
