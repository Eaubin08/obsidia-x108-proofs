"""
V5A Non-Sovereignty Test: Graphiti bridge is strictly read-only.
No Neo4j write. No Graphiti write. No decision authority.
"""
import pytest
from periphery.graphiti.graphiti_readonly_bridge import query_graphiti_readonly, assert_graphiti_no_write


def test_graphiti_query_never_writes_neo4j():
    """Graphiti queries must have neo4j_write=False."""
    result = query_graphiti_readonly(
        query_id="test_bridge",
        query="Test query only",
        max_nodes=5,
    )
    assert result.neo4j_write is False
    assert result.graphiti_write is False


def test_graphiti_query_decision_authority():
    """Graphiti queries must defer to X108."""
    result = query_graphiti_readonly(
        query_id="test_bridge",
        query="Test",
        max_nodes=3,
    )
    assert result.decision_authority == "KX108_ONLY"


def test_assert_graphiti_no_write_passes():
    """assert_graphiti_no_write should not raise for readonly results."""
    result = query_graphiti_readonly(
        query_id="test_bridge",
        query="Write-free test",
    )
    # Should not raise
    assert_graphiti_no_write(result)


def test_graphiti_query_is_readonly():
    """Graphiti query results must be readonly."""
    result = query_graphiti_readonly(
        query_id="test_bridge",
        query="Read test",
    )
    assert result.readonly is True


def test_multiple_queries_all_readonly():
    """Every Graphiti query, regardless of input, must be readonly."""
    queries = [
        "Test query",
        "Another question",
        "Status check",
    ]
    for q in queries:
        result = query_graphiti_readonly(
            query_id=f"test_{q[:4]}",
            query=q,
        )
        assert result.neo4j_write is False, f"Query '{q}': neo4j_write must be False"
        assert result.graphiti_write is False, f"Query '{q}': graphiti_write must be False"
