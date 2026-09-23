from __future__ import annotations

from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)


AUTHORITY = {
    "request_type": "PURE_RESPONSE",
}


def _build(
    message: str,
    *,
    language: str = "fr",
):
    return build_brody_pre_reasoning_snapshot(
        user_message=message,
        language=language,
        intent="pure_response",
        authority_snapshot=AUTHORITY,
    )


def test_normal_current_state_stays_calibrated():
    result = _build(
        "Explique moi le statut actuel de Brody."
    )

    qualification = result[
        "unknown_qualification"
    ]

    directive = result[
        "reasoning_directive"
    ]

    assert (
        qualification["unresolved_unknowns"]
        == []
    )

    assert (
        directive["resolution_required"]
        is False
    )


def test_memory_recall_target_does_not_block_before_retrieval():
    result = _build(
        "retrouve contextpacket "
        "dans la memoire precedente"
    )

    semantic = result[
        "semantic_query_snapshot"
    ]

    qualification = result[
        "unknown_qualification"
    ]

    directive = result[
        "reasoning_directive"
    ]

    assert semantic["topic"] == "MEMORY_QUERY"

    assert (
        semantic["route"]
        == "TOPIC_MATCHED"
    )

    assert (
        qualification["unresolved_unknowns"]
        == []
    )

    assert any(
        "contextpacket" in value.lower()
        for value in qualification[
            "retrieval_targets"
        ]
    )

    assert (
        "contextpacket"
        in qualification[
            "retrieval_target_unknowns"
        ]
    )

    assert (
        directive["resolution_required"]
        is False
    )


def test_unknown_memory_lookup_target_is_not_asserted_known():
    result = _build(
        "retrouve florvaxium "
        "dans la memoire precedente"
    )

    qualification = result[
        "unknown_qualification"
    ]

    directive = result[
        "reasoning_directive"
    ]

    assert (
        "florvaxium"
        in qualification[
            "retrieval_target_unknowns"
        ]
    )

    assert (
        "florvaxium"
        not in qualification[
            "semantically_resolved_unknowns"
        ]
    )

    assert (
        "florvaxium"
        not in qualification[
            "known_context_resolved_unknowns"
        ]
    )

    # Search target, not asserted knowledge.
    assert (
        directive["resolution_required"]
        is False
    )


def test_write_memory_reuses_ir_write_and_memory_entity():
    result = _build(
        "write this to memory",
        language="fr",
    )

    ir = result["ir_candidate"]

    qualification = result[
        "unknown_qualification"
    ]

    directive = result[
        "reasoning_directive"
    ]

    known = ir[
        "lexical_calibration"
    ].get(
        "known_concept_ids",
        [],
    )

    assert "IR:WRITE" in known

    assert any(
        entity.get("entity") == "MEMORY"
        for entity in ir.get(
            "entities",
            [],
        )
    )

    assert (
        qualification["unresolved_unknowns"]
        == []
    )

    # Understanding write intent never grants write authority.
    assert ir["memory_write"] is False
    assert ir["allowed_to_act"] is False
    assert ir["executable"] is False

    assert (
        directive["resolution_required"]
        is False
    )


def test_real_unknown_still_blocks_assertion():
    result = _build(
        "explique le florvaxium"
    )

    qualification = result[
        "unknown_qualification"
    ]

    directive = result[
        "reasoning_directive"
    ]

    assert (
        qualification["unresolved_unknowns"]
        == ["florvaxium"]
    )

    assert (
        directive["resolution_required"]
        is True
    )

    assert (
        directive["resolution_targets"]
        == ["florvaxium"]
    )


def test_semantic_continuity_has_no_authority():
    result = _build(
        "write this to memory"
    )

    qualification = result[
        "unknown_qualification"
    ]

    assert (
        qualification[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        qualification["allowed_to_decide"]
        is False
    )

    assert (
        qualification["allowed_to_act"]
        is False
    )

    assert (
        qualification["memory_write"]
        is False
    )

    assert (
        qualification["kernel_mutation"]
        is False
    )
