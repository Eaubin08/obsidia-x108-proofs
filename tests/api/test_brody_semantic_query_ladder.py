"""
Tests: brody_semantic_query_router — primary_query + fallback_queries ladder.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_semantic_query_router import build_semantic_query


def _route(msg: str) -> dict:
    return build_semantic_query(msg)


def test_x108_has_primary_and_fallbacks():
    r = _route("Explique X108 et le kernel")
    assert r["topic"] == "X108"
    assert r["primary_query"] == "x108"
    assert isinstance(r["fallback_queries"], list)
    assert len(r["fallback_queries"]) > 0


def test_primary_query_is_short():
    for msg, expected_primary in [
        ("X108 kernel", "x108"),
        ("mémoire graphiti candidat", "memory"),
        ("gencoin jeton valorisation", "gencoin"),
        ("preuve lean tla merkle", "proof"),
    ]:
        r = _route(msg)
        assert r["primary_query"] == expected_primary, f"msg={msg!r}: got {r['primary_query']!r}"


def test_fallback_queries_are_shorter_than_semantic_query():
    r = _route("X108 kernel")
    for fallback in r["fallback_queries"]:
        assert len(fallback) < len(r["semantic_query"]) or len(fallback) <= 20, (
            f"fallback {fallback!r} is not shorter than semantic_query"
        )


def test_general_fallback_has_primary_and_fallbacks():
    r = _route("bonjour comment vas-tu")
    assert r["topic"] == "GENERAL"
    assert "primary_query" in r
    assert "fallback_queries" in r
    assert isinstance(r["fallback_queries"], list)


def test_34_arbres_route():
    r = _route("les 34 arbres sont bloqués")
    assert r["topic"] == "34_ARBRES"
    assert r["primary_query"] == "34_arbres"
    assert "arbres" in r["fallback_queries"]


def test_creator_route():
    r = _route("je t'ai créé Brody")
    assert r["topic"] == "CREATOR_CONTEXT"
    assert r["primary_query"] == "brody"


def test_memory_route():
    r = _route("mémoire graphiti neo4j candidat")
    assert r["topic"] == "MEMORY_QUERY"
    assert r["primary_query"] == "memory"
    assert "graphiti" in r["fallback_queries"]


def test_mojibake_normalized_before_routing():
    r = _route("mÃ©moire graphiti candidat")
    assert r["topic"] == "MEMORY_QUERY"


def test_is_canonical_true_for_known_topics():
    r = _route("X108 kernel")
    assert r["is_canonical"] is True


def test_is_canonical_false_for_unknown():
    r = _route("bonjour comment vas-tu")
    assert r["is_canonical"] is False
