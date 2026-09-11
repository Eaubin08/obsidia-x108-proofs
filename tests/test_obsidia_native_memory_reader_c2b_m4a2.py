from __future__ import annotations

import inspect
import json
from pathlib import Path

from apps.obsidia_api.brody_memory_response_chain_adapter import (
    _load_local_graphiti_index,
    _query_local_index,
)

from apps.obsidia_api.brody_obsidia_native_memory import (
    build_native_memory_retrieval_snapshot,
    load_native_memory_index,
    query_native_memory,
)


ROOT = Path(__file__).resolve().parents[1]

INDEX = (
    ROOT
    / "_obsidia_native_memory"
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1"
    / "obsidia_native_memory_records_v1.jsonl"
)

EXPECTED = 3267


def _legacy():
    return _load_local_graphiti_index(
        ROOT
    )


def _signature(items):
    return [
        (
            item.get("score"),
            item.get("title"),
            item.get("source_ref"),
            item.get("path"),
            item.get("excerpt"),
        )
        for item in items
    ]


def test_native_reader_loads_complete_index():
    records = load_native_memory_index()

    assert len(records) == EXPECTED

    assert len({
        r["native_id"]
        for r in records
    }) == EXPECTED


def test_native_reader_is_readonly_non_sovereign():
    records = load_native_memory_index()

    for record in records:
        assert record["readonly"] is True
        assert record["memory_write"] is False
        assert record["allowed_to_decide"] is False
        assert record["allowed_to_act"] is False
        assert record["kernel_mutation"] is False
        assert record["x108_mutation"] is False
        assert record["emits_act"] is False

        assert (
            record["decision_authority"]
            == "KX108_ONLY"
        )


def test_empty_query_fails_closed():
    assert query_native_memory("") == []
    assert query_native_memory("   ") == []


def test_memory_not_required_does_not_need_index():
    missing = (
        ROOT
        / "_does_not_exist_"
        / "memory.jsonl"
    )

    result = (
        build_native_memory_retrieval_snapshot(
            "kernel",
            memory_required=False,
            index_path=missing,
        )
    )

    assert (
        result["status"]
        == "MEMORY_NOT_REQUIRED"
    )

    assert (
        result["selected_items"]
        == []
    )

    assert (
        result["memory_write"]
        is False
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )


def test_required_missing_source_fails_closed():
    missing = (
        ROOT
        / "_does_not_exist_"
        / "memory.jsonl"
    )

    result = (
        build_native_memory_retrieval_snapshot(
            "kernel",
            memory_required=True,
            index_path=missing,
        )
    )

    assert (
        result["status"]
        == "MEMORY_REQUIRED_NO_NATIVE_SOURCE"
    )

    assert (
        result["selected_items_count"]
        == 0
    )

    assert result["emits_act"] is False


def test_required_known_query_returns_native_material():
    result = (
        build_native_memory_retrieval_snapshot(
            "kernel",
            memory_required=True,
        )
    )

    assert (
        result["status"]
        == "MEMORY_USABLE"
    )

    assert (
        result["material_quality"]
        == "USABLE_MATERIAL"
    )

    assert result["selected_items_count"] > 0
    assert result["index_record_count"] == EXPECTED

    for item in result["selected_items"]:
        assert item["readonly"] is True
        assert item["memory_write"] is False
        assert item["emits_act"] is False

        assert (
            item["decision_authority"]
            == "KX108_ONLY"
        )


def test_native_ranking_matches_proven_legacy_semantics():
    legacy = _legacy()
    native = load_native_memory_index()

    queries = [
        "x108",
        "kernel",
        "agents",
        "audit",
        "proof",
        "hexaflux",
        "nodecontinuum",
        "timeline",
        "treespace34",
        "shazamcognitif",
        "completedecisionflow",
        "ltcuplus",
        "mcpbridge",
        "obsidiair",
        "agents52allowedoutput",
        "agentcontract",
        "avdr",
        "frictionsymbolique",
        "oban",
        "projectionphi",
        "contextpacket",
        "visualstate",
    ]

    for query in queries:
        old = _query_local_index(
            query,
            legacy,
            limit=8,
        )

        new = query_native_memory(
            query,
            native,
            limit=8,
        )

        assert _signature(new) == _signature(old), query


def test_reader_module_has_no_network_surface():
    import apps.obsidia_api.brody_obsidia_native_memory as module

    source = inspect.getsource(module).lower()

    forbidden = (
        "socket.",
        "urllib.",
        "requests.",
        "http://",
        "https://",
    )

    for token in forbidden:
        assert token not in source
