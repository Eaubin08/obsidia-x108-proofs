import pytest
from periphery.graphiti.graphiti_readonly_bridge import query_graphiti_readonly, assert_graphiti_no_write
from periphery.graphiti.graphiti_context_adapter import adapt_graphiti_context
from periphery.graphiti.graphiti_freeze_snapshot_reader import read_freeze_snapshot


def test_query_no_neo4j_write():
    r = query_graphiti_readonly("gnw1", "MATCH (n) RETURN n")
    assert r.neo4j_write is False


def test_query_no_graphiti_write():
    r = query_graphiti_readonly("gnw2", "context")
    assert r.graphiti_write is False


def test_assert_no_write_invariant():
    r = query_graphiti_readonly("gnw3", "invariant check")
    assert_graphiti_no_write(r)


def test_context_adapter_no_write():
    qr = query_graphiti_readonly("gnw4_q", "context")
    adapted = adapt_graphiti_context("gnw4", qr)
    assert adapted.graphiti_write is False


def test_freeze_snapshot_readonly():
    r = read_freeze_snapshot("gnw5")
    assert r.readonly is True
    assert r.is_frozen is True
