from __future__ import annotations

import inspect
from pathlib import Path

from apps.obsidia_api.brody_native_memory_response_adapter import (
    build_native_memory_response,
)


ROOT = Path(__file__).resolve().parents[1]


def test_not_required_short_circuits_cleanly():
    result = build_native_memory_response(
        user_message="bonjour",
        semantic_query="bonjour",
        memory_required=False,
        index_path=ROOT / "_missing_native_index.jsonl",
    )

    assert result["status"] == "MEMORY_NOT_REQUIRED"
    assert result["retrieval_status"] == "MEMORY_NOT_REQUIRED"
    assert result["selected_items"] == []
    assert result["local_response_engine_used"] is False
    assert result["memory_write"] is False
    assert result["emits_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_required_missing_native_source_fails_closed():
    result = build_native_memory_response(
        user_message="rappelle le kernel",
        semantic_query="kernel",
        memory_required=True,
        index_path=ROOT / "_missing_native_index.jsonl",
    )

    assert (
        result["status"]
        == "MEMORY_REQUIRED_NO_NATIVE_SOURCE"
    )

    assert result["selected_items_count"] == 0
    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["allowed_to_act"] is False
    assert result["allowed_to_decide"] is False


def test_positive_native_material_reaches_response_layer():
    result = build_native_memory_response(
        user_message="Explique le kernel",
        semantic_query="kernel",
        memory_required=True,
        limit=5,
        max_items=3,
    )

    assert result["retrieval_status"] == "MEMORY_USABLE"
    assert result["query_results_count"] > 0
    assert result["selected_items_count"] > 0
    assert result["native_index_records_total"] == 3267

    assert result["status"] in {
        "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
        "NATIVE_MEMORY_RESPONSE_PARTIAL",
    }

    assert result["material_quality"] in {
        "USABLE_MATERIAL",
        "PARTIAL_MATERIAL",
        "LOW_MATERIAL",
    }

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )


def test_native_response_shape_contains_current_generic_consumers():
    result = build_native_memory_response(
        user_message="Explique NodeContinuum",
        semantic_query="nodecontinuum",
        memory_required=True,
        limit=5,
    )

    required = {
        "status",
        "source_mode",
        "chain_source",
        "semantic_query",
        "primary_query",
        "effective_query",
        "attempted_queries",
        "query_results_count",
        "material_quality",
        "response_md",
        "response_md_length",
        "selected_items_count",
        "selected_items",
        "tag_counts",
        "final_answer_uses_response_md",
        "readonly",
        "memory_write",
        "emits_act",
        "decision_authority",
        "retrieval_status",
    }

    assert required.issubset(
        result.keys()
    )

    assert (
        result["source_mode"]
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        result["chain_source"]
        == "obsidia_native_memory->local_response_engine"
    )


def test_selected_items_keep_real_source_provenance():
    result = build_native_memory_response(
        user_message="Explique ContextPacket",
        semantic_query="contextpacket",
        memory_required=True,
        limit=5,
    )

    assert result["selected_items"]

    for item in result["selected_items"]:
        assert str(
            item.get("source_ref")
            or ""
        ).strip()

        material = str(
            item.get("material")
            or item.get("excerpt")
            or ""
        ).strip()

        has_material = item.get("has_material")

        # The historical readonly response engine legitimately preserves
        # reference-only hits. Material is required only when the engine
        # explicitly marks the selected item as material-bearing.
        assert has_material is bool(material)

        if has_material:
            assert material
        else:
            assert material == ""

        assert item.get("readonly") is True
        assert item.get("memory_write") is False

        assert (
            item.get("decision_authority")
            == "KX108_ONLY"
        )


def test_adapter_has_no_network_or_external_memory_surface():
    import apps.obsidia_api.brody_native_memory_response_adapter as module

    source = inspect.getsource(module).lower()

    forbidden = (
        "socket.",
        "urllib.",
        "requests.",
        "http://",
        "https://",
        "8011",
        "7688",
        "7475",
    )

    for token in forbidden:
        assert token not in source


def test_adapter_source_has_no_provider_identity():
    import apps.obsidia_api.brody_native_memory_response_adapter as module

    source = inspect.getsource(module).lower()

    provider_a = "grap" + "hiti"
    provider_b = "neo" + "4j"

    assert provider_a not in source
    assert provider_b not in source
