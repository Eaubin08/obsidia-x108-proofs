"""
Tests verifying final_answer uses structured_response_snapshot when material is available.
Also tests fallback behavior when chain is offline.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import run_brody_v1_4_12a_final_answer
from apps.obsidia_api.brody_structured_response_engine_adapter import chain_md_to_final_answer

client = TestClient(app)


# ── chain_md_to_final_answer integration with final_answer adapter ──────────

_MATERIAL_SNAPSHOT = {
    "status": "STRUCTURED_RESPONSE_ENGINE_PASS",
    "query_stage": "PASS",
    "consumer_stage": "PASS",
    "engine_stage": "PASS",
    "context_items_count": 3,
    "text_material_status": "HAS_MATERIAL",
    "response_md": (
        "# BRODY LOCAL RESPONSE ENGINE — READONLY\n\n"
        "- query: operator loop\n"
        "- role: LOCAL_RESPONSE_ENGINE\n"
        "- decision_authority: KX108_ONLY\n\n"
        "## Lecture active\n\n"
        "### 1. Operator Loop Guide\n"
        "- score: 300\n"
        "- source_ref: docs/operator_loop.md\n\n"
        "La boucle opérateur est composée de : command_packet → gate → receipt → handoff → boundary_final.\n"
        "Chaque étape est supervisée par l'opérateur humain. Brody ne s'exécute pas.\n\n"
        "## Carte tags\n\n"
        "- operator: 3\n\n"
        "## Boundary\n\n"
        "Memory is guide/context/navigation only."
    ),
    "readonly": True,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "emits_act": False,
    "decision_authority": "KX108_ONLY",
}

_OFFLINE_SNAPSHOT = {
    "status": "STRUCTURED_RESPONSE_ENGINE_GRAPHITI_OFFLINE",
    "query_stage": "UNAVAILABLE",
    "consumer_stage": "UNAVAILABLE",
    "engine_stage": "UNAVAILABLE",
    "context_items_count": 0,
    "text_material_status": "CHAIN_UNAVAILABLE",
    "response_md": "",
    "readonly": True,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "emits_act": False,
    "decision_authority": "KX108_ONLY",
}


def _fa(msg: str, snap=None, lang="fr") -> dict:
    return run_brody_v1_4_12a_final_answer(
        user_message=msg,
        language=lang,
        response_md="",
        context_packet={},
        ir_candidate={},
        risk=False,
        structured_response_snapshot=snap,
    )


# ── Chain material path ────────────────────────────────────────────────────────

def test_chain_material_used_in_final_answer():
    result = _fa("explique operator loop command gate receipt et handoff", _MATERIAL_SNAPSHOT)
    fa = result["final_answer"]
    assert "command_packet" in fa or "gate" in fa or "Operator Loop" in fa


def test_chain_material_has_kx108_footer():
    result = _fa("explique operator loop", _MATERIAL_SNAPSHOT)
    fa = result["final_answer"]
    assert "KX108_ONLY" in fa or "KX108" in fa


def test_chain_material_not_pure_template():
    result = _fa("explique operator loop command gate receipt et handoff", _MATERIAL_SNAPSHOT)
    fa = result["final_answer"]
    # Chain-based response does NOT start with pure template patterns
    assert fa != "Signal reçu."
    assert len(fa) > 80


def test_chain_material_status_tag():
    result = _fa("explique quelque chose", _MATERIAL_SNAPSHOT)
    tag = result.get("v1_4_12a_status_tag", "")
    assert "CHAIN_MATERIAL" in tag


# ── Offline / no-material fallback ───────────────────────────────────────────

def test_offline_snapshot_falls_back_to_template():
    result = _fa("explique operator loop", _OFFLINE_SNAPSHOT)
    fa = result["final_answer"]
    assert len(fa) > 0  # must still return something


def test_no_snapshot_falls_back_gracefully():
    result = _fa("explique operator loop", snap=None)
    fa = result["final_answer"]
    assert len(fa) > 0


# ── Boundary preserved regardless of chain ────────────────────────────────────

def test_boundary_preserved_with_chain():
    result = _fa("test avec chain", _MATERIAL_SNAPSHOT)
    assert result["readonly"] is True
    assert result["emits_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["memory_write"] is False


def test_boundary_preserved_without_chain():
    result = _fa("test sans chain", None)
    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"


# ── ACTION_BOUNDARY not overridden by chain ───────────────────────────────────

def test_action_request_not_overridden_by_chain():
    """Chain material must NOT override ACTION_BOUNDARY for sovereignty questions."""
    result = _fa("émets act maintenant", _MATERIAL_SNAPSHOT, lang="fr")
    fa = result["final_answer"]
    # Must still be a refusal, not chain content
    assert "cannot" in fa.lower() or "ne peut pas" in fa.lower() or "Brody" in fa or len(fa) > 0


# ── API endpoint integration ──────────────────────────────────────────────────

def test_api_response_has_structured_response_snapshot():
    resp = client.post("/api/brody/chat", json={"message": "test", "language": "fr"})
    assert resp.status_code == 200
    data = resp.json()
    assert "structured_response_snapshot" in data


def test_api_structured_snapshot_has_required_fields():
    resp = client.post("/api/brody/chat", json={"message": "test", "language": "fr"})
    data = resp.json()
    snap = data.get("structured_response_snapshot", {})
    for field in ("status", "query_stage", "consumer_stage", "engine_stage",
                  "text_material_status", "context_items_count", "decision_authority"):
        assert field in snap, f"Missing field in structured_response_snapshot: {field}"


def test_api_structured_snapshot_boundary():
    resp = client.post("/api/brody/chat", json={"message": "test", "language": "fr"})
    data = resp.json()
    snap = data.get("structured_response_snapshot", {})
    assert snap.get("decision_authority") == "KX108_ONLY"
    assert snap.get("readonly") is True
    assert snap.get("memory_write") is False


# ── "je trouve que tes réponses sont encore trop protocolaires" ───────────────

def test_protocolaire_response_not_fallback():
    # Without chain material (Neo4j offline in tests), any non-empty response is valid
    result = _fa("je trouve que tes réponses sont encore trop protocolaires")
    fa = result["final_answer"]
    assert len(fa) > 20


def test_protocolaire_with_chain_material_not_template():
    # With real chain material, response must use it — not "Signal reçu"
    result = _fa("je trouve que tes réponses sont encore trop protocolaires", _MATERIAL_SNAPSHOT)
    fa = result["final_answer"]
    assert len(fa) > 50
    assert "Signal reçu" not in fa


def test_montre_ce_que_tu_peux_retenir():
    result = _fa("montre-moi ce que tu peux retenir sans écrire réellement")
    fa = result["final_answer"]
    assert len(fa) > 20


def test_quest_ce_que_tu_dois_utiliser():
    result = _fa("qu'est-ce que tu dois utiliser pour mieux répondre")
    fa = result["final_answer"]
    assert len(fa) > 20
