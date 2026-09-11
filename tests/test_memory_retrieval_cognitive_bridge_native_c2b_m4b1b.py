from __future__ import annotations

import inspect

import pytest

from apps.obsidia_api.brody_native_memory_response_adapter import (
    build_native_memory_response,
)
from periphery.context.context_packet_builder_v2 import (
    build_context_packet_v2,
)
from periphery.context.memory_retrieval_cognitive_bridge import (
    enrich_context_packet_v2_with_memory_retrieval,
)


def _base():
    return build_context_packet_v2(
        query="Explique le kernel",
        language="fr",
        context_items=["BASE"],
    )


def _native_snapshot():
    return build_native_memory_response(
        user_message="Explique le kernel",
        semantic_query="kernel",
        memory_required=True,
        limit=5,
        max_items=3,
    )


def _bounded_snapshot(**overrides):
    obj = {
        "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
        "retrieval_status": "MEMORY_USABLE",
        "source_mode": "OBSIDIA_NATIVE_MEMORY",
        "effective_query": "kernel",
        "material_quality": "USABLE_MATERIAL",
        "selected_items": [],
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

    obj.update(overrides)
    return obj


def test_native_response_enriches_context_packet():
    snapshot = _native_snapshot()

    assert (
        snapshot["retrieval_status"]
        == "MEMORY_USABLE"
    )

    enriched = (
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )
    )

    assert (
        enriched.memory_status
        == "CANDIDATE_ONLY"
    )

    assert (
        enriched.retrieval_status
        == "MEMORY_USABLE"
    )

    expected_refs = {
        str(item.get("source_ref") or "")
        for item in snapshot["selected_items"]
        if str(
            item.get("source_ref") or ""
        ).strip()
    }

    assert expected_refs
    assert expected_refs.issubset(
        set(enriched.source_refs)
    )

    assert (
        "MEMORY_RETRIEVAL_SOURCE_MODE:"
        "OBSIDIA_NATIVE_MEMORY"
        in enriched.context_items
    )

    assert (
        "MEMORY_RETRIEVAL_RESULT:"
        "MEMORY_USABLE"
        in enriched.context_items
    )

    assert enriched.readonly is True
    assert enriched.memory_write is False
    assert enriched.allowed_to_decide is False
    assert enriched.allowed_to_act is False
    assert enriched.kernel_mutation is False


def test_reference_only_hit_preserves_provenance_without_fake_material():
    snapshot = _bounded_snapshot(
        selected_items=[
            {
                "id": "REF_ONLY",
                "source_ref": "REF_ONLY",
                "material": "",
                "has_material": False,
                "readonly": True,
                "memory_write": False,
                "canonical_write": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "emits_verdict": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "decision_authority": "KX108_ONLY",
            }
        ],
    )

    enriched = (
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )
    )

    assert "REF_ONLY" in enriched.source_refs

    assert not any(
        item.startswith(
            "MEMORY_RETRIEVAL:REF_ONLY:"
        )
        for item in enriched.context_items
    )


@pytest.mark.parametrize(
    "field",
    [
        "memory_write",
        "canonical_write",
        "allowed_to_decide",
        "allowed_to_act",
        "emits_act",
        "emits_verdict",
        "kernel_mutation",
        "x108_mutation",
        "memory_authority",
        "memory_decision",
        "auto_promotion",
        "real_action",
    ],
)
def test_native_sovereign_flags_fail_closed(field):
    snapshot = _bounded_snapshot()
    snapshot[field] = True

    with pytest.raises(AssertionError):
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )


def test_unknown_external_write_flag_fails_closed_without_provider_knowledge():
    snapshot = _bounded_snapshot()

    # Arbitrary storage-specific write capability.
    snapshot["external_store_write"] = True

    with pytest.raises(AssertionError):
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )


def test_unknown_source_identity_is_collapsed_to_generic_readonly_channel():
    snapshot = _bounded_snapshot(
        source_mode="LEGACY_EXTERNAL_SOURCE",
    )

    enriched = (
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )
    )

    assert (
        "MEMORY_RETRIEVAL_SOURCE_MODE:"
        "READONLY_MEMORY_RETRIEVAL"
        in enriched.context_items
    )


@pytest.mark.parametrize(
    "status",
    [
        "MEMORY_REQUIRED_NO_NATIVE_SOURCE",
        "MEMORY_REQUIRED_INVALID_NATIVE_SOURCE",
        "MEMORY_REQUIRED_EMPTY_QUERY",
        "MEMORY_REQUIRED_EMPTY",
    ],
)
def test_native_unavailable_states_become_unknowns(status):
    snapshot = _bounded_snapshot(
        status=status,
        retrieval_status=status,
        material_quality="NO_MATERIAL",
    )

    enriched = (
        enrich_context_packet_v2_with_memory_retrieval(
            _base(),
            snapshot,
        )
    )

    assert (
        f"MEMORY_RETRIEVAL:{status}"
        in enriched.unknowns
    )


def test_bridge_module_is_provider_neutral():
    import periphery.context.memory_retrieval_cognitive_bridge as module

    source = inspect.getsource(
        module
    ).lower()

    old_provider_a = "grap" + "hiti"
    old_provider_b = "neo" + "4j"

    assert old_provider_a not in source
    assert old_provider_b not in source

    for token in (
        "8011",
        "7688",
        "7475",
        "http://",
        "https://",
    ):
        assert token not in source
