"""
test_brody_v3_secret_surface_scrub — V3 Block 3F G1b+G4 surface repair.
20 tests couvrant G1b (espace-séparé sans =), G4 (deep scrub récursif),
préservation des invariants KX108_ONLY.
DECISION_AUTHORITY=KX108_ONLY. PATCH=YES_SECRET_SURFACE_ONLY. COMMIT=NO.
"""
from __future__ import annotations

import json
import pytest

from apps.obsidia_api.brody_secret_scrubber import (
    detect_secret_like,
    scrub_secret_like,
    scrub_secret_like_deep,
    is_private_key_message,
)


# ── Test 1 — scrub_secret_like: API_KEY=VALUE form (= form) ──────────────────

def test_scrub_api_key_eq_form():
    result = scrub_secret_like("API_KEY=abc123SECRET")
    assert "abc123SECRET" not in result
    assert "API_KEY" in result
    assert "[REDACTED_SECRET]" in result


# ── Test 2 — scrub_secret_like: API_KEY VALUE form (G1b — space) ─────────────

def test_scrub_api_key_space_form():
    result = scrub_secret_like("Requête mémoire extraite : Mémorise API_KEY abc123SECRET")
    assert "abc123SECRET" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 3 — scrub_secret_like: PASSWORD=VALUE form ──────────────────────────

def test_scrub_password_eq_form():
    result = scrub_secret_like("PASSWORD=supersecret")
    assert "supersecret" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 4 — scrub_secret_like: PASSWORD VALUE form (G1b) ────────────────────

def test_scrub_password_space_form():
    result = scrub_secret_like("Ajoute PASSWORD supersecret à la mémoire")
    assert "supersecret" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 5 — scrub_secret_like: Bearer form (Bearer pattern already covers space) ──

def test_scrub_bearer_space_form():
    result = scrub_secret_like("Sauvegarde Bearer abc.def.ghi")
    assert "abc.def.ghi" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 6 — scrub_secret_like: token space form (G1b) ───────────────────────

def test_scrub_token_space_form():
    result = scrub_secret_like("token abc.def.ghi.xyz.abcdefgh")
    assert "abc.def.ghi.xyz.abcdefgh" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 7 — scrub_secret_like: PRIVATE KEY header ───────────────────────────

def test_scrub_private_key_header():
    result = scrub_secret_like("-----BEGIN PRIVATE KEY----- test")
    assert "BEGIN PRIVATE KEY-----" not in result
    assert "[REDACTED_SECRET]" in result


# ── Test 8 — scrub_secret_like_deep: scrub dict nested ───────────────────────

def test_scrub_deep_dict_nested():
    obj = {
        "context_packet": {
            "query": "Memorise API_KEY=abc123SECRET.",
            "inner": {"field": "Bearer sometoken123456789"},
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "sometoken123456789" not in text
    assert "[REDACTED_SECRET]" in text
    assert isinstance(result, dict)
    assert isinstance(result["context_packet"], dict)


# ── Test 9 — scrub_secret_like_deep: scrub list nested ───────────────────────

def test_scrub_deep_list_nested():
    obj = {
        "fallback_queries": [
            "normal query",
            "abc123SECRET",
            "API_KEY=secret123456",
        ]
    }
    result = scrub_secret_like_deep(obj)
    assert "secret123456" not in json.dumps(result, ensure_ascii=False)
    assert isinstance(result["fallback_queries"], list)
    assert len(result["fallback_queries"]) == 3
    assert result["fallback_queries"][0] == "normal query"


# ── Test 10 — scrub_secret_like_deep: préserve les booléens ──────────────────

def test_scrub_deep_preserves_booleans():
    obj = {
        "readonly": True,
        "canonical_write": False,
        "allowed_to_act": False,
        "emits_act": False,
        "human_validation_required": True,
        "api_debug_only": True,
        "nested": {"enabled": True, "disabled": False},
    }
    result = scrub_secret_like_deep(obj)
    assert result["readonly"] is True
    assert result["canonical_write"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["human_validation_required"] is True
    assert result["api_debug_only"] is True
    assert result["nested"]["enabled"] is True
    assert result["nested"]["disabled"] is False


# ── Test 11 — scrub_secret_like_deep: préserve decision_authority=KX108_ONLY ─

def test_scrub_deep_preserves_kx108_only():
    obj = {
        "decision_authority": "KX108_ONLY",
        "nested": {"decision_authority": "KX108_ONLY"},
        "list": [{"decision_authority": "KX108_ONLY"}],
    }
    result = scrub_secret_like_deep(obj)
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["nested"]["decision_authority"] == "KX108_ONLY"
    assert result["list"][0]["decision_authority"] == "KX108_ONLY"


# ── Test 12 — scrub_secret_like_deep: préserve canonical_write=False ─────────

def test_scrub_deep_preserves_canonical_write_false():
    obj = {
        "canonical_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "deep": {"canonical_write": False, "allowed_to_act": False},
    }
    result = scrub_secret_like_deep(obj)
    assert result["canonical_write"] is False
    assert result["graphiti_write"] is False
    assert result["neo4j_write"] is False
    assert result["kernel_mutation"] is False
    assert result["deep"]["canonical_write"] is False
    assert result["deep"]["allowed_to_act"] is False


# ── Test 13 — response_md ne contient plus secret reformulé (G1b) ─────────────

def test_scrub_response_md_g1b_reformulation():
    response_md = (
        "RÉPONSE STRUCTURELLE.\n"
        "Requête mémoire extraite : Memorise API_KEY abc123SECRET\n\n"
        "Sources :\n\nBoundary: READONLY=true"
    )
    result = scrub_secret_like(response_md)
    assert "abc123SECRET" not in result
    assert "[REDACTED_SECRET]" in result
    assert "READONLY=true" in result


# ── Test 14 — machination_packet ne contient plus secret brut (G4) ────────────

def test_scrub_deep_machination_packet():
    obj = {
        "machination_packet": {
            "session_memory_snapshot": {
                "previous_user_message": "Memorise API_KEY=abc123SECRET.",
                "current_user_message_excerpt": "Memorise API_KEY=abc123SECRET.",
            },
            "semantic_query_snapshot": {
                "semantic_query": "Memorise API_KEY abc123SECRET",
                "original_message": "Memorise API_KEY=abc123SECRET.",
                "normalized_message": "Memorise API_KEY=abc123SECRET.",
                "fallback_queries": ["API_KEY=abc123SECRET", "API_KEY abc123SECRET"],
            },
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "[REDACTED_SECRET]" in text


# ── Test 15 — context_packet ne contient plus secret brut (G4) ───────────────

def test_scrub_deep_context_packet():
    obj = {
        "context_packet": {
            "query": "Memorise API_KEY=abc123SECRET.",
            "memory_query": "Memorise API_KEY abc123SECRET",
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text


# ── Test 16 — semantic_query_snapshot ne contient plus secret brut (G4) ───────

def test_scrub_deep_semantic_query_snapshot():
    obj = {
        "semantic_query_snapshot": {
            "semantic_query": "API_KEY abc123SECRET",
            "original_message": "API_KEY=abc123SECRET.",
            "normalized_message": "API_KEY=abc123SECRET.",
            "fallback_queries": ["API_KEY=abc123SECRET"],
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "[REDACTED_SECRET]" in text


# ── Test 17 — source_pack_context ne contient plus secret brut (G4) ──────────

def test_scrub_deep_source_pack_context():
    obj = {
        "source_pack_context": {
            "context_summary_for_brody": (
                "[SOURCE PACK CONTEXT — KX108_ONLY — READONLY]\n"
                "Query: Memorise API_KEY=abc123SECRET.\nFamilies: COGNITIVE"
            )
        }
    }
    result = scrub_secret_like_deep(obj)
    text = json.dumps(result, ensure_ascii=False)
    assert "abc123SECRET" not in text
    assert "KX108_ONLY" in text
    assert "READONLY" in text


# ── Test 18 — v3_memory_readonly_packet reste clean (pas de double-scrub) ──────

def test_scrub_deep_v3_memory_readonly_packet_already_clean():
    obj = {
        "v3_memory_readonly_packet": {
            "readonly": True,
            "canonical_write": False,
            "decision_authority": "KX108_ONLY",
            "memory_candidate": {
                "candidate_payload": {
                    "message_excerpt": "Mémoriser [REDACTED_SECRET]",
                }
            }
        }
    }
    result = scrub_secret_like_deep(obj)
    pkt = result["v3_memory_readonly_packet"]
    assert pkt["readonly"] is True
    assert pkt["canonical_write"] is False
    assert pkt["decision_authority"] == "KX108_ONLY"
    # Already scrubbed → no double-redaction
    excerpt = pkt["memory_candidate"]["candidate_payload"]["message_excerpt"]
    assert "[REDACTED_SECRET]" in excerpt
    assert excerpt.count("[REDACTED_SECRET]") == 1


# ── Test 19 — no ACT: emits_act=False préservé après deep scrub ──────────────

def test_scrub_deep_no_act():
    obj = {
        "emits_act": False,
        "allowed_to_act": False,
        "allowed_to_decide": False,
        "decision_authority": "KX108_ONLY",
        "machination_packet": {
            "emits_act": False,
            "act_status": "NO_ACT",
        }
    }
    result = scrub_secret_like_deep(obj)
    assert result["emits_act"] is False
    assert result["allowed_to_act"] is False
    assert result["allowed_to_decide"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["machination_packet"]["emits_act"] is False


# ── Test 20 — no memory write: canonical_write + graphiti_write préservés ─────

def test_scrub_deep_no_memory_write():
    obj = {
        "canonical_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "v3_memory_readonly_packet": {
            "canonical_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "decision_authority": "KX108_ONLY",
        }
    }
    result = scrub_secret_like_deep(obj)
    assert result["canonical_write"] is False
    assert result["graphiti_write"] is False
    assert result["neo4j_write"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False
    pkt = result["v3_memory_readonly_packet"]
    assert pkt["canonical_write"] is False
    assert pkt["graphiti_write"] is False


# ── Bonus: detect_secret_like catches G1b space form ─────────────────────────

def test_detect_secret_like_g1b_space_form():
    assert detect_secret_like("API_KEY abc123SECRET") is True
    assert detect_secret_like("PASSWORD supersecret") is True
    assert detect_secret_like("Texte normal sans secret") is False


# ── Bonus: scrub_secret_like idempotent on already-scrubbed ──────────────────

def test_scrub_idempotent_already_scrubbed():
    already = "API_KEY=[REDACTED_SECRET]"
    result = scrub_secret_like(already)
    assert result == "API_KEY=[REDACTED_SECRET]"
    assert result.count("[REDACTED_SECRET]") == 1


# ── Bonus: scrub_secret_like_deep handles None/int/float ─────────────────────

def test_scrub_deep_preserves_none_int_float():
    obj = {
        "score": 0.75,
        "count": 42,
        "nullable": None,
        "nested": {"priority": 3, "ratio": 0.5, "empty": None},
    }
    result = scrub_secret_like_deep(obj)
    assert result["score"] == 0.75
    assert result["count"] == 42
    assert result["nullable"] is None
    assert result["nested"]["priority"] == 3
    assert result["nested"]["ratio"] == 0.5
    assert result["nested"]["empty"] is None
