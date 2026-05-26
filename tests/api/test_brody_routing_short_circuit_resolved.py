"""
Tests: BRODY_ROUTING_SHORT_CIRCUIT_RESOLVED_SEMANTIC_LIVE — v2

Step 7d split:
  ERROR                                  → MEMORY_CHAIN_INFRASTRUCTURE_ERROR (transparent)
  NO_MEMORY_RESULTS + GENERAL + tag      → SEMANTIC_MATCH_FAILED_EXPLICIT_TAG
  NO_MEMORY_RESULTS + GENERAL, no tag   → SEMANTIC_MATCH_FAILED_GENERAL
  NO_MEMORY_RESULTS + known topic        → SEMANTIC_ADVISORY_NO_MEMORY
  PARTIAL_QUERY_ONLY                     → same routing as NO_MEMORY_RESULTS
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer, _detect_explicit_identifier

_BASE_CTX = {
    "true_response_structure_snapshot": {},
    "project_memory_snapshot": {},
    "session_memory_snapshot": {},
    "freeze_metrics_snapshot": {},
    "creator_context": {},
    "rights_action_snapshot": {},
}


def _ctx(chain: dict) -> dict:
    c = dict(_BASE_CTX)
    c["memory_response_chain_snapshot"] = chain
    return c


# ── _detect_explicit_identifier ──────────────────────────────────────────────

def test_detect_p136():
    assert _detect_explicit_identifier("montre la pépite P136") == "P136"

def test_detect_b12():
    assert _detect_explicit_identifier("accède au bloc B12") == "B12"

def test_detect_t20():
    assert _detect_explicit_identifier("arbre T20 est-il safe?") == "T20"

def test_detect_bloc_allcaps():
    assert _detect_explicit_identifier("quel est le statut de BLOC") == "BLOC"

def test_detect_no_id_generic_fr():
    assert _detect_explicit_identifier("pourquoi tu fais ça") == ""

def test_detect_no_id_common_word():
    assert _detect_explicit_identifier("BRODY répond toujours PASS") == ""


# ── ERROR branch → MEMORY_CHAIN_INFRASTRUCTURE_ERROR ─────────────────────────

def test_error_surfaces_infra_not_masked():
    chain = {
        "status": "ERROR",
        "error_type": "NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING",
        "error": "NEO4J_PASSWORD_NOT_SET — local index not found",
        "neo4j_status": "NEO4J_PASSWORD_NOT_SET",
        "material_quality": "CHAIN_UNAVAILABLE",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(user_message="X108 status", brody_full_context=_ctx(chain))
    assert r.get("voice_source") == "MEMORY_CHAIN_INFRASTRUCTURE_ERROR"
    fa = r.get("final_answer", "")
    assert "NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING" in fa or "infrastructure" in fa.lower()
    assert "NEO4J_PASSWORD_NOT_SET" in fa or "neo4j" in fa.lower()

def test_fail_soft_error_surfaces():
    chain = {
        "status": "ERROR",
        "source_mode": "FAIL_SOFT",
        "error_type": "ImportError",
        "error_message": "No module named 'brody_memory'",
    }
    r = build_true_brody_answer(user_message="mémoire", brody_full_context=_ctx(chain))
    assert r.get("voice_source") == "MEMORY_CHAIN_INFRASTRUCTURE_ERROR"
    fa = r.get("final_answer", "")
    assert "ImportError" in fa or "infrastructure" in fa.lower()

def test_error_not_masked_as_semantic_advisory():
    chain = {"status": "ERROR", "error_type": "CHAIN_EXECUTION_ERROR", "error": "timeout"}
    r = build_true_brody_answer(user_message="test", brody_full_context=_ctx(chain))
    assert r.get("voice_source") != "SEMANTIC_ADVISORY_NO_MEMORY"
    assert r.get("voice_source") == "MEMORY_CHAIN_INFRASTRUCTURE_ERROR"


# ── NO_MEMORY_RESULTS + GENERAL + explicit tag → SEMANTIC_MATCH_FAILED_EXPLICIT_TAG

def test_p136_general_topic_explicit_miss():
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "GENERAL",
        "attempted_queries": [
            {"query": "montre", "results_count": 0},
            {"query": "pepite", "results_count": 0},
            {"query": "P136", "results_count": 0},
        ],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="montre la pépite P136",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_MATCH_FAILED_EXPLICIT_TAG"
    fa = r.get("final_answer", "")
    assert "P136" in fa
    assert "correspondance" in fa.lower() or "match" in fa.lower() or "local" in fa.lower()

def test_bloc_allcaps_general_explicit_miss():
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "GENERAL",
        "attempted_queries": [{"query": "BLOC", "results_count": 0}],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="statut du BLOC",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_MATCH_FAILED_EXPLICIT_TAG"
    fa = r.get("final_answer", "")
    assert "BLOC" in fa

def test_explicit_miss_not_open_question():
    """Must NOT contain 'sur quel axe' or simulate an open discussion."""
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "GENERAL",
        "attempted_queries": [{"query": "P136", "results_count": 0}],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="P136 où",
        brody_full_context=_ctx(chain),
    )
    fa = r.get("final_answer", "")
    assert "sur quel axe" not in fa.lower()
    assert "axe" not in fa.lower() or "veux-tu" not in fa.lower()


# ── NO_MEMORY_RESULTS + GENERAL, no explicit tag → SEMANTIC_MATCH_FAILED_GENERAL

def test_generic_query_no_results_not_open_question():
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "GENERAL",
        "attempted_queries": [
            {"query": "pourquoi", "results_count": 0},
            {"query": "forces", "results_count": 0},
        ],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="pourquoi tu forces le mode terminal dialogue",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_MATCH_FAILED_GENERAL"
    fa = r.get("final_answer", "")
    # Must NOT simulate an open question discussion
    assert "sur quel axe" not in fa.lower()
    # Must hint at reformulation
    assert "reformul" in fa.lower() or "x108" in fa.lower() or "term" in fa.lower()

def test_generic_miss_shows_attempted_queries():
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "GENERAL",
        "attempted_queries": [
            {"query": "comment", "results_count": 0},
            {"query": "fonctionne", "results_count": 0},
        ],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="comment ça fonctionne",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_MATCH_FAILED_GENERAL"
    fa = r.get("final_answer", "")
    assert "comment" in fa or "fonctionne" in fa or "tentée" in fa.lower() or "attempted" in fa.lower()


# ── NO_MEMORY_RESULTS + known topic → SEMANTIC_ADVISORY_NO_MEMORY ─────────────

def test_known_topic_no_results_still_advisory():
    chain = {
        "status": "NO_MEMORY_RESULTS",
        "topic": "X108",
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
        "query_results_count": 0,
    }
    r = build_true_brody_answer(
        user_message="X108 kernel",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_ADVISORY_NO_MEMORY"
    fa = r.get("final_answer", "")
    assert "X108" in fa or "kernel" in fa.lower()

def test_partial_query_only_routes_same_as_no_memory():
    """PARTIAL_QUERY_ONLY (Neo4j path) follows same routing logic as NO_MEMORY_RESULTS."""
    chain = {
        "status": "PARTIAL_QUERY_ONLY",
        "topic": "GENERAL",
        "attempted_queries": [],
        "material_quality": "NO_MATERIAL",
        "response_md": "",
        "selected_items": [],
    }
    r = build_true_brody_answer(
        user_message="test sans identifiant",
        brody_full_context=_ctx(chain),
    )
    assert r.get("voice_source") == "SEMANTIC_MATCH_FAILED_GENERAL"


# ── Guards — action boundary and creator context unaffected ──────────────────

def test_action_request_not_overridden():
    chain = {"status": "ERROR", "error_type": "NEO4J_DOWN"}
    ctx = _ctx(chain)
    ctx["rights_action_snapshot"] = {"request_type": "ACTION_OR_ACT_REQUEST"}
    r = build_true_brody_answer(
        user_message="déclenche l'action",
        brody_full_context=ctx,
    )
    assert r.get("voice_source") != "MEMORY_CHAIN_INFRASTRUCTURE_ERROR"

def test_boundary_invariants_all_branches():
    for status, msg in [
        ("ERROR", "test"),
        ("NO_MEMORY_RESULTS", "P136 accès"),
        ("NO_MEMORY_RESULTS", "comment ça"),
        ("NO_MEMORY_RESULTS", "X108 kernel"),
    ]:
        chain = {
            "status": status, "topic": "GENERAL" if msg != "X108 kernel" else "X108",
            "error_type": "ERR" if status == "ERROR" else None,
            "material_quality": "NO_MATERIAL", "response_md": "", "selected_items": [],
            "attempted_queries": [],
        }
        r = build_true_brody_answer(user_message=msg, brody_full_context=_ctx(chain))
        assert r.get("readonly") is True, f"readonly failed for status={status}"
        assert r.get("memory_write") is False
        assert r.get("emits_act") is False
        assert r.get("decision_authority") == "KX108_ONLY"
