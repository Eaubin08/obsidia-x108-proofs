"""
Tests: build_memory_response_chain() — local index fallback + effective_query ladder.

Neo4j is not available in CI → all tests use local Graphiti index fallback path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_memory_response_chain_adapter import (
    build_memory_response_chain,
    _load_local_graphiti_index,
    _query_local_index,
)

_WORKSPACE = Path(__file__).resolve().parents[2]


def test_local_index_loads():
    records = _load_local_graphiti_index(_WORKSPACE)
    assert isinstance(records, list), "Expected list of records"


def test_local_index_query_returns_items_or_empty():
    records = _load_local_graphiti_index(_WORKSPACE)
    if not records:
        return  # index not present — skip
    hits = _query_local_index("x108", records, limit=5)
    assert isinstance(hits, list)
    for h in hits:
        assert "rank" in h
        assert "score" in h
        assert "excerpt" in h


def test_chain_returns_dict():
    r = build_memory_response_chain(user_message="X108 kernel")
    assert isinstance(r, dict)


def test_chain_has_source_mode():
    r = build_memory_response_chain(user_message="X108 kernel")
    assert "source_mode" in r


def test_chain_not_error_when_local_index_present():
    records = _load_local_graphiti_index(_WORKSPACE)
    if not records:
        return  # index not present — skip
    r = build_memory_response_chain(user_message="X108 kernel")
    # With local index present, should not be NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING
    assert r.get("error_type") != "NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING"


def test_chain_has_attempted_queries_when_local_fallback():
    records = _load_local_graphiti_index(_WORKSPACE)
    if not records:
        return
    r = build_memory_response_chain(user_message="X108 kernel")
    if r.get("source_mode") == "LOCAL_GRAPHITI_INDEX_FALLBACK":
        assert "attempted_queries" in r
        assert isinstance(r["attempted_queries"], list)
        assert len(r["attempted_queries"]) > 0


def test_chain_effective_query_is_short_when_local():
    records = _load_local_graphiti_index(_WORKSPACE)
    if not records:
        return
    r = build_memory_response_chain(user_message="X108 kernel")
    if r.get("source_mode") == "LOCAL_GRAPHITI_INDEX_FALLBACK" and r.get("effective_query"):
        eq = r["effective_query"]
        assert len(eq) <= 30, f"effective_query too long: {eq!r}"


def test_chain_boundary_invariants():
    r = build_memory_response_chain(user_message="X108 kernel")
    assert r.get("readonly") is True
    assert r.get("memory_write") is False
    assert r.get("graphiti_write") is False
    assert r.get("neo4j_write") is False
    assert r.get("emits_act") is False
    assert r.get("emits_verdict") is False
    assert r.get("kernel_mutation") is False
    assert r.get("decision_authority") == "KX108_ONLY"


def test_chain_local_index_records_total_exposed():
    records = _load_local_graphiti_index(_WORKSPACE)
    if not records:
        return
    r = build_memory_response_chain(user_message="X108 kernel")
    if r.get("source_mode") == "LOCAL_GRAPHITI_INDEX_FALLBACK":
        if r.get("status") != "NO_MEMORY_RESULTS":
            assert "local_index_records_total" in r
            assert r["local_index_records_total"] > 0
