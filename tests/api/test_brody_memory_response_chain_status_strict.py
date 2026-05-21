"""
Tests: build_memory_response_chain() — strict status classification rules.

Valid statuses: BRODY_MEMORY_RESPONSE_CHAIN_PASS, LOCAL_INDEX_FALLBACK_PARTIAL,
                NO_MEMORY_RESULTS, ERROR.
Never: NEO4J_UNAVAILABLE (old error type that masked local fallback).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_memory_response_chain_adapter import build_memory_response_chain

_VALID_STATUSES = {
    "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "LOCAL_INDEX_FALLBACK_PARTIAL",
    "NO_MEMORY_RESULTS",
    "PARTIAL_QUERY_ONLY",
    "ERROR",
}

_MESSAGES = [
    "X108 kernel",
    "mémoire graphiti candidat",
    "34 arbres bloqués",
    "gencoin jeton",
    "preuve lean tla",
    "bonjour",
]


def test_status_always_in_known_set():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        assert r["status"] in _VALID_STATUSES, (
            f"msg={msg!r}: unexpected status {r['status']!r}"
        )


def test_no_raw_neo4j_unavailable_status():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        # Old behavior returned status="ERROR" with error_type="NEO4J_UNAVAILABLE"
        # New behavior must use error_type="NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING"
        # when Neo4j AND local index are both unavailable
        if r.get("error_type") == "NEO4J_UNAVAILABLE":
            raise AssertionError(
                f"msg={msg!r}: got old-style NEO4J_UNAVAILABLE error — "
                "local index fallback should have been attempted first"
            )


def test_source_mode_always_present():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        assert "source_mode" in r, f"msg={msg!r}: missing source_mode"


def test_local_fallback_has_graphiti_live_false():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        if r.get("source_mode") == "LOCAL_GRAPHITI_INDEX_FALLBACK":
            assert r.get("graphiti_live") is False


def test_chain_pass_implies_response_md_nonempty():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        if r["status"] == "BRODY_MEMORY_RESPONSE_CHAIN_PASS":
            assert r.get("response_md") and len(r["response_md"]) > 50, (
                f"msg={msg!r}: PASS but response_md too short"
            )


def test_no_memory_results_has_note():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        if r["status"] == "NO_MEMORY_RESULTS":
            assert "note" in r


def test_error_has_error_type():
    for msg in _MESSAGES:
        r = build_memory_response_chain(user_message=msg)
        if r["status"] == "ERROR":
            assert "error_type" in r
