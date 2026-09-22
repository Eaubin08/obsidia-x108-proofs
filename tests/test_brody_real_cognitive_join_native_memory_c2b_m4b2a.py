from __future__ import annotations

import inspect

from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)


def _native_snapshot(
    retrieval_status: str = "MEMORY_USABLE",
    with_material: bool = True,
):
    items = []

    if with_material:
        items = [
            {
                "id": "NATIVE_SYNTHETIC_A",
                "source_ref": "NATIVE_SYNTHETIC_A",
                "material": (
                    "Memoire structurelle readonly "
                    "pour contexte cognitif."
                ),
                "has_material": True,
                "readonly": True,
                "memory_authority": False,
                "memory_decision": False,
                "memory_write": False,
                "canonical_write": False,
                "auto_promotion": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "emits_verdict": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "decision_authority": "KX108_ONLY",
            }
        ]

    return {
        "schema_version":
            "BRODY_NATIVE_MEMORY_RESPONSE_V1",

        "status": (
            "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
            if retrieval_status == "MEMORY_USABLE"
            else retrieval_status
        ),

        "retrieval_status":
            retrieval_status,

        "source_mode":
            "OBSIDIA_NATIVE_MEMORY",

        "semantic_query":
            "memoire structurelle",

        "effective_query":
            "memoire structurelle",

        "material_quality": (
            "USABLE_MATERIAL"
            if with_material
            else "NOT_REQUIRED"
        ),

        "selected_items":
            items,

        "selected_items_count":
            len(items),

        "readonly": True,
        "response_only": True,

        "memory_authority": False,
        "memory_decision": False,

        "memory_write": False,
        "canonical_write": False,
        "auto_promotion": False,

        "allowed_to_decide": False,
        "allowed_to_act": False,

        "emits_act": False,
        "emits_verdict": False,

        "kernel_mutation": False,
        "x108_mutation": False,

        "decision_authority":
            "KX108_ONLY",
    }


def test_native_memory_reaches_context_before_w1_w2():
    result = run_real_cognitive_join(
        message="Inspecter la memoire structurelle",
        language="fr",
        session_id="m4b2a-positive",
        precomputed_memory_chain=_native_snapshot(),
    )

    assert (
        result["components"][
            "W4_MEMORY_RETRIEVAL"
        ]
        == "READY:REAL_RETRIEVAL:MEMORY_USABLE"
    )

    assert (
        result["memory_retrieval_applied"]
        is True
    )

    assert (
        result["memory_retrieval_status"]
        == "MEMORY_USABLE"
    )

    packet = result[
        "context_packet_v2"
    ]

    assert (
        packet["retrieval_status"]
        == "MEMORY_USABLE"
    )

    assert (
        "NATIVE_SYNTHETIC_A"
        in packet["source_refs"]
    )

    assert any(
        str(item).startswith(
            "MEMORY_RETRIEVAL:"
            "NATIVE_SYNTHETIC_A:"
        )
        for item
        in packet["context_items"]
    )

    assert (
        result["components"][
            "W1_RUNTIME_JOIN"
        ]
        == "READY"
    )

    assert (
        result["components"][
            "W2_X108_ADMISSION"
        ]
        == "READY:DRY_RUN"
    )

    assert (
        result["kx108_admission"]
        == "DRY_RUN"
    )

    assert result["memory_write"] is False
    assert result["allowed_to_act"] is False
    assert result["real_execution"] is False

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )


def test_memory_not_required_snapshot_is_valid():
    result = run_real_cognitive_join(
        message="Bonjour",
        language="fr",
        session_id="m4b2a-off",
        precomputed_memory_chain=_native_snapshot(
            retrieval_status="MEMORY_NOT_REQUIRED",
            with_material=False,
        ),
    )

    assert (
        result["components"][
            "W4_MEMORY_RETRIEVAL"
        ]
        == (
            "READY:REAL_RETRIEVAL:"
            "MEMORY_NOT_REQUIRED"
        )
    )

    assert (
        result["memory_retrieval_status"]
        == "MEMORY_NOT_REQUIRED"
    )

    assert (
        result["context_packet_v2"][
            "retrieval_status"
        ]
        == "MEMORY_NOT_REQUIRED"
    )


def test_no_precomputed_memory_executes_nothing():
    result = run_real_cognitive_join(
        message="Bonjour",
        language="fr",
        session_id="m4b2a-none",
    )

    assert (
        result["components"][
            "W4_MEMORY_RETRIEVAL"
        ]
        == (
            "SKIPPED_BY_PATH_POLICY:"
            "MEMORY_RETRIEVAL_NOT_PRECOMPUTED"
        )
    )

    assert (
        result["memory_retrieval_applied"]
        is False
    )

    assert (
        result["memory_response_chain_snapshot"]
        is None
    )


def test_w4_join_surface_is_provider_neutral():
    source = inspect.getsource(
        run_real_cognitive_join
    ).lower()

    provider_a = "grap" + "hiti"
    provider_b = "neo" + "4j"

    assert provider_a not in source
    assert provider_b not in source

    assert "w4_memory_retrieval" in source
    assert "w4_graphiti_memory" not in source
