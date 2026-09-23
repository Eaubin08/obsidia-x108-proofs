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


def _deep_signals(
    *,
    dominant_balance: str = "balance_memoire",
    active_layers: list[str] | None = None,
    memory_required: bool = True,
    axis13: float = 0.82,
):
    return {
        "balance": {
            "balance_engine_version": "V3_BLOCK_1",
            "balances_count": 11,
            "balances": {
                "balance_memoire": {
                    "balance": "balance_memoire",
                    "tension": 0.71,
                },
            },
            "coordinator": {
                "dominant_balance": dominant_balance,
                "top3_balances": [dominant_balance],
                "layers_to_activate": [
                    "memory_selector_layer",
                ],
                "layers_to_avoid": [],
                "balance_risk_level": 0.2,
                "hold_required": False,
            },
            "advisory_only": True,
            "decision_authority": "KX108_ONLY",
        },
        "point_cloud": {
            "selector_version": "V3_BLOCK_1",
            "dimensions": 21,
            "vector_21d": {
                13: axis13,
                21: 0.4,
            },
            "dominant_axes": [13],
            "active_layers": active_layers
            or [
                "memory_selector_layer",
            ],
            "forbidden_layers": [],
            "memory_packet_required": memory_required,
            "domain_packet_required": False,
            "advisory_only": True,
            "decision_authority": "KX108_ONLY",
        },
        "memzum": {
            "module": "MEMZUM",
            "version": "C2B_M2A_V0",
            "status": "MEMZUM_ACTIVATION_PASS",
            "memory_required": memory_required,
            "reason": (
                "MEMORY_REQUIRED_COGNITIVE_SIGNAL"
                if memory_required
                else "MEMORY_NOT_REQUIRED"
            ),
            "activation_basis": {
                "memory_packet_required": memory_required,
                "axis_13_memory": axis13,
                "memory_relevance_signal": 0.8,
                "balance_memoire_tension": 0.71,
                "domain_detected": None,
                "intent_type": "information_request",
                "is_adversarial": False,
            },
            "advisory_only": True,
            "memory_write": False,
            "decision_authority": "KX108_ONLY",
        },
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


def test_deep_precomputed_signals_reach_c1_and_context_packet():
    signals = _deep_signals()

    result = run_real_cognitive_join(
        message="Inspecter la memoire structurelle",
        language="fr",
        session_id="m4b2a-deep",
        precomputed_balance_signal=signals["balance"],
        precomputed_point_cloud_21d=signals["point_cloud"],
        precomputed_memzum_activation=signals["memzum"],
        precomputed_memory_chain=_native_snapshot(),
    )

    assert (
        result["components"]["DEEP_COGNITIVE_SIGNALS"]
        == "READY:PRECOMPUTED"
    )

    deep = result["deep_cognitive_signal_snapshot"]

    assert deep["available"] == {
        "balance": True,
        "point_cloud_21d": True,
        "memzum": True,
    }

    assert (
        deep["balance_snapshot"]["dominant_balance"]
        == "balance_memoire"
    )

    assert (
        deep["point_cloud_21d_snapshot"][
            "memory_packet_required"
        ]
        is True
    )

    assert (
        deep["memzum_activation_snapshot"][
            "memory_required"
        ]
        is True
    )

    packet = result["context_packet_v2"]

    assert "brody:balance_engine" in packet["source_refs"]
    assert "brody:point_cloud_21d" in packet["source_refs"]
    assert "brody:memzum_activation" in packet["source_refs"]

    assert "BALANCE_STATE_AVAILABLE:True" in packet["context_items"]
    assert "POINT_CLOUD_21D_AVAILABLE:True" in packet["context_items"]
    assert "MEMZUM_STATE_AVAILABLE:True" in packet["context_items"]

    assert result["decision_authority"] == "KX108_ONLY"
    assert result["memory_write"] is False
    assert result["emits_act"] is False


def test_deep_optional_inputs_absent_preserves_old_c1_surface():
    result = run_real_cognitive_join(
        message="Bonjour",
        language="fr",
        session_id="m4b2a-no-deep",
    )

    assert (
        result["components"]["DEEP_COGNITIVE_SIGNALS"]
        == "SKIPPED_OPTIONAL_NOT_PROVIDED"
    )

    deep = result["deep_cognitive_signal_snapshot"]
    assert deep["available"] == {
        "balance": False,
        "point_cloud_21d": False,
        "memzum": False,
    }

    packet = result["context_packet_v2"]
    assert "brody:balance_engine" not in packet["source_refs"]
    assert "brody:point_cloud_21d" not in packet["source_refs"]
    assert "brody:memzum_activation" not in packet["source_refs"]
    assert not any(
        str(item).startswith("BALANCE_STATE_AVAILABLE:")
        for item in packet["context_items"]
    )


def test_deep_cognitive_material_effect_at_context_packet():
    signals_a = _deep_signals(
        active_layers=[
            "memory_selector_layer",
        ],
        memory_required=True,
        axis13=0.82,
    )
    signals_b = _deep_signals(
        dominant_balance="balance_coherence",
        active_layers=[
            "symbolic_layer",
        ],
        memory_required=False,
        axis13=0.2,
    )

    result_a = run_real_cognitive_join(
        message="Comparer la memoire structurelle",
        language="fr",
        session_id="m4b2a-effect-a",
        precomputed_balance_signal=signals_a["balance"],
        precomputed_point_cloud_21d=signals_a["point_cloud"],
        precomputed_memzum_activation=signals_a["memzum"],
    )
    result_b = run_real_cognitive_join(
        message="Comparer la memoire structurelle",
        language="fr",
        session_id="m4b2a-effect-b",
        precomputed_balance_signal=signals_b["balance"],
        precomputed_point_cloud_21d=signals_b["point_cloud"],
        precomputed_memzum_activation=signals_b["memzum"],
    )

    assert (
        result_a["deep_cognitive_signal_snapshot"]
        != result_b["deep_cognitive_signal_snapshot"]
    )

    assert (
        result_a["context_packet_v2"]["context_items"]
        != result_b["context_packet_v2"]["context_items"]
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
