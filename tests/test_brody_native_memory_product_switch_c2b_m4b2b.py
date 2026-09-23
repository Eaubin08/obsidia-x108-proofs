from __future__ import annotations

from pathlib import Path


ROUTE = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "obsidia_api"
    / "routes"
    / "brody.py"
)


def _src():
    return ROUTE.read_text(
        encoding="utf-8-sig"
    )


def test_product_uses_native_memory_only():
    src = _src()

    assert (
        "brody_native_memory_response_adapter"
        in src
    )

    assert (
        "build_native_memory_response"
        in src
    )

    assert (
        "brody_memory_response_chain_adapter"
        not in src
    )

    assert (
        "build_memory_response_chain"
        not in src
    )


def test_memzum_precedes_native_retrieval():
    src = _src()

    memzum = src.index(
        "_memory_required = bool("
    )

    retrieval = src.index(
        "build_native_memory_response,"
    )

    assert memzum < retrieval

    assert (
        "memory_required=_memory_required"
        in src
    )


def test_generic_memory_chain_shape_name_preserved():
    src = _src()

    assert (
        "memory_response_chain = ("
        in src
    )

    assert (
        "memory_response_chain_snapshot="
        "memory_response_chain"
        in src
    )

    assert (
        'memory_response_chain.get("response_md", "")'
        in src
    )


def test_c2_receives_product_precomputed_inputs():
    src = _src()

    assert (
        "precomputed_micro_core=("
        in src
    )

    assert (
        "precomputed_brody_runtime=r"
        in src
    )

    assert (
        "precomputed_memory_chain=("
        in src
    )


def test_backend_c1_projection_precedes_human_synthesis():
    src = _src()

    memory = src.index(
        "memory_response_chain = ("
    )

    c1 = src.index(
        "# COGNITIVE_RUNTIME_JOIN_BACKEND_V1"
    )

    v1412a = src.index(
        'safe_call_snapshot("v1412a_final_answer"'
    )

    full_context = src.index(
        'safe_call_snapshot("brody_full_context"'
    )

    true_voice = src.index(
        'safe_call_snapshot("true_voice_snapshot"'
    )

    final_selection = src.index(
        "# Final answer priority"
    )

    assert memory < c1 < v1412a < full_context < true_voice < final_selection

    assert (
        src.count(
            "# COGNITIVE_RUNTIME_JOIN_BACKEND_V1"
        )
        == 1
    )

    assert (
        "context_packet=(_c1_context_packet or context_packet)"
        in src
    )

    assert (
        "ir_candidate=_c1_ir_candidate"
        in src
    )

    assert (
        "governed_cognitive_projection=governed_cognitive_projection"
        in src
    )


def test_live_route_native_memory_reaches_w4_w1_w2():
    from fastapi.testclient import TestClient

    from apps.obsidia_api.auth import (
        require_api_key,
    )
    from apps.obsidia_api.main import app

    sentinel = object()

    previous = app.dependency_overrides.get(
        require_api_key,
        sentinel,
    )

    app.dependency_overrides[
        require_api_key
    ] = lambda: None

    try:
        client = TestClient(app)

        response = client.post(
            "/api/brody/chat",
            json={
                "message": (
                    "Dans la memoire Obsidia, "
                    "retrouve ContextPacket et "
                    "explique sa structure."
                ),
                "language": "fr",
            },
        )

        assert response.status_code == 200, (
            response.text[:800]
        )

        data = response.json()

        chain = data.get(
            "memory_response_chain_snapshot",
            {},
        )

        assert isinstance(chain, dict)
        assert chain

        assert (
            chain.get("source_mode")
            == "OBSIDIA_NATIVE_MEMORY"
        )

        assert (
            chain.get("readonly")
            is True
        )

        assert (
            chain.get("memory_write")
            is False
        )

        assert (
            chain.get("decision_authority")
            == "KX108_ONLY"
        )

        assert "graphiti_status" not in chain
        assert "neo4j_status" not in chain

        assert chain.get(
            "retrieval_status"
        ) in {
            "MEMORY_USABLE",
            "MEMORY_NOT_REQUIRED",
        }

        receipt = data.get(
            "cognitive_runtime_receipt",
            {},
        )

        assert isinstance(receipt, dict)
        assert receipt

        components = receipt.get(
            "components",
            {},
        )

        w4 = str(
            components.get(
                "W4_MEMORY_RETRIEVAL",
                "",
            )
        )

        assert w4.startswith(
            "READY:REAL_RETRIEVAL:"
        )

        assert (
            components.get(
                "W1_RUNTIME_JOIN"
            )
            == "READY"
        )

        assert (
            components.get(
                "W2_X108_ADMISSION"
            )
            == "READY:DRY_RUN"
        )

        assert (
            receipt.get(
                "kx108_admission"
            )
            == "DRY_RUN"
        )

        assert (
            receipt.get(
                "decision_authority"
            )
            == "KX108_ONLY"
        )

        assert (
            receipt.get(
                "memory_write"
            )
            is False
        )

        assert (
            receipt.get(
                "allowed_to_act"
            )
            is False
        )

        full_context = data.get(
            "brody_full_context",
            {},
        )

        projection = full_context.get(
            "governed_cognitive_projection",
            {},
        )

        assert isinstance(projection, dict)
        assert projection

        assert (
            projection.get(
                "context_packet_v2"
            )
            == receipt.get(
                "context_packet_v2"
            )
        )

        receipt_ir_candidate = (
            receipt.get("reverse_os_projection", {}).get("ir_candidate", {})
            if isinstance(receipt.get("reverse_os_projection"), dict)
            else {}
        )
        assert (
            projection.get(
                "ir_candidate"
            )
            == receipt_ir_candidate
        )

        assert (
            projection.get(
                "decision_authority"
            )
            == "KX108_ONLY"
        )

        assert (
            projection.get(
                "memory_write"
            )
            is False
        )

        assert (
            projection.get(
                "emits_act"
            )
            is False
        )

        assert (
            projection.get(
                "kernel_mutation"
            )
            is False
        )

    finally:
        if previous is sentinel:
            app.dependency_overrides.pop(
                require_api_key,
                None,
            )
        else:
            app.dependency_overrides[
                require_api_key
            ] = previous
