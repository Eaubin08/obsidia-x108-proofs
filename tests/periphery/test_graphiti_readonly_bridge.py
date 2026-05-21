import pytest
from periphery.graphiti.graphiti_readonly_bridge import query_graphiti_readonly, assert_graphiti_no_write


def test_query_returns_readonly():
    r = query_graphiti_readonly("gq1", "MATCH (n) RETURN n LIMIT 1")
    assert r.readonly is True


def test_no_neo4j_write():
    r = query_graphiti_readonly("gq2", "MATCH (n) RETURN n")
    assert r.neo4j_write is False


def test_no_graphiti_write():
    r = query_graphiti_readonly("gq3", "context query")
    assert r.graphiti_write is False


def test_decision_authority_kx108():
    r = query_graphiti_readonly("gq4", "who decides?")
    assert r.decision_authority == "KX108_ONLY"


def test_assert_no_write_helper():
    r = query_graphiti_readonly("gq5", "nodes")
    assert_graphiti_no_write(r)


def test_dict_fields():
    r = query_graphiti_readonly("gq6", "nodes")
    d = r.to_dict()
    assert "readonly" in d and "neo4j_write" in d and "graphiti_write" in d
