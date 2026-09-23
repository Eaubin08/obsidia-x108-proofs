"""
test_brody_v3_secret_sequence_scrub — G5 bare token sequence scrub.
20 tests couvrant G5 (scrub contextuel séquence token sensible + valeur).
SCOPE=V3_G5_ATTEMPTED_QUERIES_SECRET_REPAIR_ONLY
DECISION_AUTHORITY=KX108_ONLY. PATCH=YES_G5_ONLY. COMMIT=NO.
"""
from __future__ import annotations

import json
import pytest

from apps.obsidia_api.brody_secret_scrubber import (
    scrub_secret_token_sequence,
    scrub_secret_like_deep,
)


# ── Tests scrub_secret_token_sequence — cas de scrub ─────────────────────────

def test_sequence_api_key_bare_token():
    """T1 — ["API_KEY", "abc123SECRET"] → valeur redactée."""
    result = scrub_secret_token_sequence(["API_KEY", "abc123SECRET"])
    assert result[0] == "API_KEY"
    assert result[1] == "[REDACTED_SECRET]"


def test_sequence_password_bare_token():
    """T2 — ["PASSWORD", "supersecret"] → valeur redactée."""
    result = scrub_secret_token_sequence(["PASSWORD", "supersecret"])
    assert result[0] == "PASSWORD"
    assert result[1] == "[REDACTED_SECRET]"


def test_sequence_token_lowercase():
    """T3 — ["token", "abc.def.ghi"] → valeur redactée (case-insensitive)."""
    result = scrub_secret_token_sequence(["token", "abc.def.ghi"])
    assert result[0] == "token"
    assert result[1] == "[REDACTED_SECRET]"


def test_sequence_bearer_mixed_case():
    """T4 — ["Bearer", "abc.def.ghi"] → valeur redactée (case-insensitive)."""
    result = scrub_secret_token_sequence(["Bearer", "abc.def.ghi"])
    assert result[0] == "Bearer"
    assert result[1] == "[REDACTED_SECRET]"


# ── Tests scrub_secret_token_sequence — cas de NON scrub ─────────────────────

def test_sequence_normal_token_no_scrub():
    """T5 — ["normal", "abc123SECRET"] → inchangé (pas un token sensible)."""
    result = scrub_secret_token_sequence(["normal", "abc123SECRET"])
    assert result[0] == "normal"
    assert result[1] == "abc123SECRET"


def test_sequence_project_secretariat_no_scrub():
    """T6 — ["project", "secretariat"] → inchangé (pas de token sensible)."""
    result = scrub_secret_token_sequence(["project", "secretariat"])
    assert result == ["project", "secretariat"]


def test_sequence_tokenisation_no_scrub():
    """T7 — ["tokenisation", "memoire"] → inchangé (pas un match exact de TOKEN)."""
    result = scrub_secret_token_sequence(["tokenisation", "memoire"])
    assert result == ["tokenisation", "memoire"]


def test_sequence_idempotent():
    """T8 — Appliquer deux fois ne double-redacte pas."""
    first = scrub_secret_token_sequence(["API_KEY", "abc123SECRET"])
    second = scrub_secret_token_sequence(first)
    assert second[1] == "[REDACTED_SECRET]"
    assert second[1].count("[REDACTED_SECRET]") == 1


# ── Tests scrub_secret_like_deep sur fallback_queries (ROOT_SOURCE_1) ─────────

def test_deep_fallback_queries_g5_leak():
    """T9 — fallback_queries bare token scrubbed via deep scrub (G5 ROOT_SOURCE_1)."""
    obj = {
        "semantic_query_snapshot": {
            "topic": "GENERAL",
            "primary_query": "memorise",
            "fallback_queries": ["API_KEY", "abc123SECRET"],
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "[REDACTED_SECRET]" in text
    fq = result["semantic_query_snapshot"]["fallback_queries"]
    assert fq[0] == "API_KEY"
    assert fq[1] == "[REDACTED_SECRET]"


def test_deep_attempted_queries_g5_leak():
    """T10 — attempted_queries dict ladder scrubbed via deep scrub (G5 ROOT_SOURCE_2)."""
    obj = {
        "attempted_queries": [
            {"query": "memorise", "results_count": 5},
            {"query": "API_KEY", "results_count": 0},
            {"query": "abc123SECRET", "results_count": 0},
        ]
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "[REDACTED_SECRET]" in text
    assert result["attempted_queries"][2]["query"] == "[REDACTED_SECRET]"


def test_deep_support_routes_attempted_queries():
    """T11 — support_routes.os_trad.memory_context.attempted_queries scrubbed."""
    obj = {
        "support_routes": {
            "os_trad": {
                "memory_context": {
                    "attempted_queries": [
                        {"query": "API_KEY", "results_count": 0},
                        {"query": "abc123SECRET", "results_count": 0},
                    ]
                }
            }
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text


def test_deep_semantic_query_snapshot_nested():
    """T12 — semantic_query_snapshot nested dans brody_full_context."""
    obj = {
        "brody_full_context": {
            "semantic_query_snapshot": {
                "fallback_queries": ["TOKEN", "abc.def.ghi"]
            }
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc.def.ghi" not in text


def test_deep_brody_full_context_chain():
    """T13 — brody_full_context.memory_response_chain_snapshot.attempted_queries scrubbed."""
    obj = {
        "brody_full_context": {
            "memory_response_chain_snapshot": {
                "attempted_queries": [
                    {"query": "PASSWORD", "results_count": 0},
                    {"query": "supersecret", "results_count": 0},
                ]
            }
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "supersecret" not in text


def test_deep_runtime_context_nested():
    """T14 — runtime_context.semantic_query_snapshot.fallback_queries scrubbed."""
    obj = {
        "runtime_context": {
            "semantic_query_snapshot": {
                "fallback_queries": ["BEARER", "secretvalue123"]
            }
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "secretvalue123" not in text


# ── Invariants et surface propre ─────────────────────────────────────────────

def test_response_final_answer_clean():
    """T15 — response et final_answer restent inchangés (texte propre)."""
    obj = {
        "response": "Je ne peux pas mémoriser ce contenu.",
        "final_answer": "Contenu sensible détecté. KX108_ONLY.",
        "response_md": "## Réponse\nContenu refusé.",
    }
    result = scrub_secret_like_deep(obj)
    assert result["response"] == "Je ne peux pas mémoriser ce contenu."
    assert result["final_answer"] == "Contenu sensible détecté. KX108_ONLY."
    assert result["response_md"] == "## Réponse\nContenu refusé."


def test_v3_memory_readonly_packet_clean():
    """T16 — v3_memory_readonly_packet reste propre et structuré."""
    obj = {
        "v3_memory_readonly_packet": {
            "readonly": True,
            "canonical_write": False,
            "decision_authority": "KX108_ONLY",
            "allowed_to_act": False,
            "emits_act": False,
        }
    }
    result = scrub_secret_like_deep(obj)
    pkt = result["v3_memory_readonly_packet"]
    assert pkt["readonly"] is True
    assert pkt["canonical_write"] is False
    assert pkt["decision_authority"] == "KX108_ONLY"
    assert pkt["allowed_to_act"] is False
    assert pkt["emits_act"] is False


def test_runtime_cost_map_present_after_scrub():
    """T17 — runtime_cost_map reste présent et intact après scrub."""
    obj = {
        "runtime_cost_map": {
            "useful_compute_ms": 1.0,
            "orchestration_ms": 2.0,
            "dissipation_ratio": 2.0,
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "canonical_write": False,
        }
    }
    result = scrub_secret_like_deep(obj)
    rcm = result["runtime_cost_map"]
    assert rcm["decision_authority"] == "KX108_ONLY"
    assert rcm["emits_act"] is False
    assert rcm["canonical_write"] is False
    assert rcm["dissipation_ratio"] == 2.0


def test_kx108_only_preserved_throughout():
    """T18 — decision_authority=KX108_ONLY préservé à tous les niveaux."""
    obj = {
        "decision_authority": "KX108_ONLY",
        "semantic_query_snapshot": {
            "fallback_queries": ["API_KEY", "abc123SECRET"],
            "decision_authority": "KX108_ONLY",
        },
        "runtime_cost_map": {"decision_authority": "KX108_ONLY"},
    }
    result = scrub_secret_like_deep(obj)
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["semantic_query_snapshot"]["decision_authority"] == "KX108_ONLY"
    assert result["runtime_cost_map"]["decision_authority"] == "KX108_ONLY"


def test_no_canonical_write_emits_act():
    """T19 — canonical_write=False et emits_act=False préservés (no ACT, no write)."""
    obj = {
        "canonical_write": False,
        "no_canonical_write": True,
        "emits_act": False,
        "allowed_to_act": False,
        "graphiti_write": False,
        "neo4j_write": False,
    }
    result = scrub_secret_like_deep(obj)
    assert result["canonical_write"] is False
    assert result["no_canonical_write"] is True
    assert result["emits_act"] is False
    assert result["allowed_to_act"] is False
    assert result["graphiti_write"] is False
    assert result["neo4j_write"] is False


def test_booleans_preserved_throughout():
    """T20 — booléens préservés à tous les niveaux (True/False, pas scrubbed en str)."""
    obj = {
        "readonly": True,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "human_validation_required": True,
        "nested": {
            "enabled": True,
            "disabled": False,
            "count": 42,
            "ratio": 0.95,
            "empty": None,
        },
        "attempted_queries": [
            {"query": "API_KEY", "results_count": 0, "fresh": True},
            {"query": "abc123SECRET", "results_count": 0, "fresh": False},
        ],
    }
    result = scrub_secret_like_deep(obj)
    assert result["readonly"] is True
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False
    assert result["human_validation_required"] is True
    assert result["nested"]["enabled"] is True
    assert result["nested"]["disabled"] is False
    assert result["nested"]["count"] == 42
    assert result["nested"]["ratio"] == 0.95
    assert result["nested"]["empty"] is None
    # G5 scrub happened on attempted_queries
    assert result["attempted_queries"][1]["query"] == "[REDACTED_SECRET]"
    # bool field in the redacted dict preserved
    assert result["attempted_queries"][1]["fresh"] is False
