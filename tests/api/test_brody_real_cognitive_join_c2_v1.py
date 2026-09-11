from __future__ import annotations

import inspect

import pytest

from apps.obsidia_api.brody_real_response_cognitive_adapter import (
    adapt_real_brody_runtime_to_response,
)
from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)
from periphery.context.context_packet_builder_v2 import (
    build_context_packet_v2,
)
from periphery.context.memory_retrieval_cognitive_bridge import (
    enrich_context_packet_v2_with_memory_retrieval,
)


MESSAGE = "Inspecter la memoire cognitive Obsidia en lecture seule"


def _real_brody() -> dict:
    return {
        "action_id": "brody_real_c2_test",
        "language": "fr",
        "timestamp": "2026-09-07T09:00:00+00:00",
        "response_md": "Reponse Brody runtime readonly avec contexte reel.",
        "source": "REAL_BRODY_GRAPHITI_V20_FROZEN_READONLY",
        "readonly": True,
        "response_only": True,
        "memory_decision": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "emits_allow_hold_block": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "real_action": False,
        "decision_authority": "KX108_ONLY",
        "context_packet": {
            "packet_id": "cp_brody_real_c2_test",
            "query": MESSAGE,
            "readonly": True,
        },
        "selected_items": [],
    }


def _memory_chain() -> dict:
    return {
        "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
        "source_mode": "GRAPHITI_V20_FROZEN_HTTP_PRIMARY",
        "semantic_query": "memoire cognitive Obsidia",
        "effective_query": "memory",
        "graphiti_status": "GRAPHITI_V20_FROZEN_READONLY_PASS",
        "neo4j_status": "NEO4J_PASSWORD_NOT_SET",
        "material_quality": "USABLE_MATERIAL",
        "selected_items_count": 2,
        "selected_items": [
            {
                "rank": 1,
                "id": "SRC_A",
                "title": "Source A",
                "path": "",
                "tags": [],
                "score": 999,
                "source_ref": "SRC_A",
                "material": "Matiere memoire A.",
                "has_material": True,
            },
            {
                "rank": 2,
                "id": "SRC_B",
                "title": "Source B",
                "path": "",
                "tags": [],
                "score": 998,
                "source_ref": "SRC_B",
                "material": "Matiere memoire B.",
                "has_material": True,
            },
        ],
        "chain_source": (
            "neo4j_unavailable→graphiti_v20_frozen_http"
            "→local_response_engine"
        ),
        "readonly": True,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
    }


def test_c2_real_brody_adapter_uses_real_runtime_text():
    response = adapt_real_brody_runtime_to_response(
        _real_brody(),
        query=MESSAGE,
        language="fr",
    )

    assert response.response_id == "brody_real_c2_test"
    assert response.query == MESSAGE
    assert response.language == "fr"
    assert response.response_text == (
        "Reponse Brody runtime readonly avec contexte reel."
    )

    assert response.readonly is True
    assert response.emits_act is False
    assert response.memory_write is False

    assert (
        "brody-source:REAL_BRODY_GRAPHITI_V20_FROZEN_READONLY"
        in response.context_refs
    )

    assert (
        response.contract["runtime_adapter"]["confidence_status"]
        == "NOT_AVAILABLE_SENTINEL_0_0"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("readonly", False),
        ("allowed_to_decide", True),
        ("allowed_to_act", True),
        ("emits_act", True),
        ("memory_write", True),
        ("kernel_mutation", True),
        ("x108_mutation", True),
        ("real_action", True),
    ],
)
def test_c2_real_brody_adapter_fails_closed(field, value):
    runtime = _real_brody()
    runtime[field] = value

    with pytest.raises(AssertionError):
        adapt_real_brody_runtime_to_response(
            runtime,
            query=MESSAGE,
            language="fr",
        )


def test_c2_memory_retrieval_is_not_memory_candidate():
    base = build_context_packet_v2(
        query=MESSAGE,
        language="fr",
        context_items=["BASE"],
    )

    enriched = enrich_context_packet_v2_with_memory_retrieval(
        base,
        _memory_chain(),
    )

    assert enriched.memory_status == "CANDIDATE_ONLY"
    assert (
        enriched.retrieval_status
        == "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
    )

    assert "SRC_A" in enriched.source_refs
    assert "SRC_B" in enriched.source_refs

    assert any(
        item.startswith("MEMORY_RETRIEVAL:SRC_A:")
        for item in enriched.context_items
    )

    assert enriched.readonly is True
    assert enriched.allowed_to_decide is False
    assert enriched.allowed_to_act is False
    assert enriched.memory_write is False
    assert enriched.kernel_mutation is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("readonly", False),
        ("memory_write", True),
        ("graphiti_write", True),
        ("neo4j_write", True),
        ("emits_act", True),
        ("emits_verdict", True),
        ("kernel_mutation", True),
    ],
)
def test_c2_memory_retrieval_fails_closed(field, value):
    chain = _memory_chain()
    chain[field] = value

    base = build_context_packet_v2(
        query=MESSAGE,
        language="fr",
    )

    with pytest.raises(AssertionError):
        enrich_context_packet_v2_with_memory_retrieval(
            base,
            chain,
        )


def test_c2_join_closes_w3_w4_with_precomputed_real_results():
    result = run_real_cognitive_join(
        message=MESSAGE,
        language="fr",
        session_id="c2-join-test",
        precomputed_brody_runtime=_real_brody(),
        precomputed_memory_chain=_memory_chain(),
    )

    assert (
        result["components"]["W3_BRODY"]
        == "READY:REAL_RUNTIME_ADAPTER"
    )

    assert result["components"]["W4_MEMORY_RETRIEVAL"] == (
        "READY:REAL_RETRIEVAL:"
        "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
    )

    assert result["memory_retrieval_applied"] is True

    refs = result["context_packet_v2"]["source_refs"]

    assert "SRC_A" in refs
    assert "SRC_B" in refs

    assert result["decision_authority"] == "KX108_ONLY"
    assert result["real_execution"] is False
    assert result["response_governance_applied"] is False
    assert result["kx108_admission"] == "DRY_RUN"


def test_c2_fastpath_policy_does_not_execute_missing_memory_chain():
    result = run_real_cognitive_join(
        message=MESSAGE,
        language="fr",
        session_id="c2-no-precomputed",
    )

    assert result["components"]["W3_BRODY"] == (
        "SKIPPED_BY_PATH_POLICY:"
        "NO_PRECOMPUTED_BRODY_RUNTIME"
    )

    assert result["components"]["W4_MEMORY_RETRIEVAL"] == (
        "SKIPPED_BY_PATH_POLICY:"
        "MEMORY_RETRIEVAL_NOT_PRECOMPUTED"
    )


def test_c2_backend_route_passes_existing_real_results():
    import apps.obsidia_api.routes.brody as brody_route

    src = inspect.getsource(brody_route.brody_chat)

    assert "precomputed_brody_runtime=r" in src
    assert "precomputed_memory_chain=(" in src
    assert "memory_response_chain" in src
    assert "precomputed_micro_core=(" in src
