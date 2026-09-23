"""P27 — Source pack context propagation through Brody engine to final_answer.

Tests that source pack context is:
1. Propagated into True Voice and final_answer (when packs available)
2. Reflected in payload with new P27 fields
3. Always advisory/readonly — sovereignty invariants never degraded
4. Falls back cleanly when packs absent
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient
from apps.obsidia_api.main import app
import apps.obsidia_api.brody_real_cognitive_join as cognitive_join
import apps.obsidia_api.routes.brody as brody_route

client = TestClient(app)

try:
    from runtime_wiring.source_runtime.source_pack_resolver import list_available_families
    _PACKS_AVAILABLE = len(list_available_families()) > 0
except Exception:
    _PACKS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Main P27 propagation test
# ─────────────────────────────────────────────────────────────────────────────

def test_source_pack_context_propagated_to_final_answer():
    """P27 core: source pack context reaches final_answer via True Voice."""
    r = client.post("/api/brody/chat", json={
        "message": "Explique X108 avec les sources Cognitive et NPL disponibles",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    # Sovereignty always
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True
    assert data.get("memory_write") is False
    assert data.get("kernel_mutation") is False

    # P27 new fields always present
    assert "source_pack_context_summary" in data
    assert "final_answer_source_pack_enriched" in data
    assert "source_pack_context_used" in data

    if _PACKS_AVAILABLE:
        assert data["source_pack_context_used"] is True
        assert data["source_pack_entries_used"] >= 1
        assert data["source_pack_x108_decision"] == "ALLOW_CONTEXT_ONLY"

        # P27 enrichment flags
        assert data["final_answer_source_pack_enriched"] is True

        # final_answer contains readable source pack trace
        fa = data.get("final_answer", "") or data.get("response", "")
        assert isinstance(fa, str) and len(fa) > 20

        # Must mention families or advisory nature or X108
        fa_lower = fa.lower()
        has_family_mention = any(
            kw in fa_lower for kw in [
                "cognitive", "atlas", "rssi", "npl", "narrative", "external",
                "familles", "families", "source", "advisory", "readonly",
                "allow_context_only", "x108", "kx108",
            ]
        )
        assert has_family_mention, (
            f"final_answer should mention source pack context, families or X108. Got: {fa[:300]}"
        )
    else:
        assert data["final_answer_source_pack_enriched"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: source_pack_context_summary field present and valid
# ─────────────────────────────────────────────────────────────────────────────

def test_source_pack_context_summary_field():
    """source_pack_context_summary is always a string, non-empty when packs used."""
    r = client.post("/api/brody/chat", json={
        "message": "Résume les sources disponibles dans le registry Obsidia",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    assert "source_pack_context_summary" in data
    assert isinstance(data["source_pack_context_summary"], str)

    if _PACKS_AVAILABLE and data.get("source_pack_context_used"):
        # When packs used, summary should be non-empty
        assert len(data["source_pack_context_summary"]) > 10


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: final_answer_source_pack_enriched field is boolean
# ─────────────────────────────────────────────────────────────────────────────

def test_final_answer_source_pack_enriched_is_bool():
    """final_answer_source_pack_enriched must be a boolean, never null/undefined."""
    r = client.post("/api/brody/chat", json={
        "message": "Bonjour Brody",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()
    val = data.get("final_answer_source_pack_enriched")
    assert isinstance(val, bool), f"Expected bool, got {type(val)}: {val}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Sovereignty never degraded by P27 enrichment
# ─────────────────────────────────────────────────────────────────────────────

def test_p27_does_not_degrade_sovereignty():
    """P27 enrichment must not override any sovereignty flag."""
    r = client.post("/api/brody/chat", json={
        "message": "Explique les source packs et familles disponibles",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    sovereignty = [
        "emits_act", "emits_verdict", "memory_write", "graphiti_write",
        "neo4j_write", "kernel_mutation", "x108_mutation", "allowed_to_decide",
    ]
    for key in sovereignty:
        if key in data:
            assert data[key] is False, f"{key} must remain False after P27 enrichment"

    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True

    # source_pack_context nested dict must have correct flags
    ctx = data.get("source_pack_context", {})
    if ctx.get("source_pack_context_used"):
        assert ctx.get("no_act") is True
        assert ctx.get("memory_write") is False
        assert ctx.get("zip_extraction") is False
        boundary = ctx.get("boundary", {})
        assert boundary.get("emits_act") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: fallback when packs absent — final_answer_source_pack_enriched=False
# ─────────────────────────────────────────────────────────────────────────────

def test_fallback_when_packs_unavailable():
    """When source packs are not used, final_answer_source_pack_enriched=False, no crash."""
    r = client.post("/api/brody/chat", json={
        "message": "Comment vas-tu Brody ?",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    # Always present
    assert "final_answer_source_pack_enriched" in data
    assert "source_pack_context_summary" in data
    assert "source_pack_context_used" in data

    # If packs weren't used (greeting topic — source pack not triggered):
    if not data.get("source_pack_context_used"):
        assert data["final_answer_source_pack_enriched"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: P26 fields still present (no regression)
# ─────────────────────────────────────────────────────────────────────────────

def test_p26_fields_still_present():
    """P27 must not remove any P26 fields from the payload."""
    r = client.post("/api/brody/chat", json={
        "message": "X108 Cognitive sources test",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    p26_fields = [
        "source_pack_context",
        "source_pack_context_used",
        "source_pack_families",
        "source_pack_entries_used",
        "source_pack_x108_decision",
        "source_pack_os3_evidence_id",
    ]
    for field in p26_fields:
        assert field in data, f"P26 field missing after P27: {field}"


def test_source_pack_context_built_once_enters_c1_and_true_voice(monkeypatch):
    calls = {
        "source_build": 0,
        "c1": 0,
        "true_voice": 0,
        "c1_ctx_id": None,
        "true_voice_ctx_id": None,
    }

    def fake_source_context(*, query, limit=5):
        calls["source_build"] += 1
        return {
            "source_pack_context_used": True,
            "source_pack_families": ["ATLAS"],
            "source_pack_entries_used": 1,
            "x108_decision": "ALLOW_CONTEXT_ONLY",
            "x108_gate_status": "ALLOW_CONTEXT_ONLY",
            "selected_source_families": ["ATLAS"],
            "source_file_refs": ["atlas/ref-once.md"],
            "context_summary_for_brody": "x" * 120,
            "no_act": True,
            "memory_write": False,
            "zip_extraction": False,
            "boundary": {"emits_act": False},
        }

    def fake_c1(**kwargs):
        calls["c1"] += 1
        ctx = kwargs.get("precomputed_source_pack_context")
        calls["c1_ctx_id"] = id(ctx)
        return {
            "status": "READY_SHADOW_READONLY",
            "completeness": "COMPLETE",
            "context_packet_v2": {
                "context_items": ["SOURCE_ROUTING_STATE_AVAILABLE:True"],
                "source_refs": [
                    "brody:source_routing",
                    "source:atlas/ref-once.md",
                ],
                "readonly": True,
                "decision_authority": "KX108_ONLY",
                "allowed_to_act": False,
                "memory_write": False,
            },
            "source_routing_signal_snapshot": {
                "status": "READY:SOURCE_ROUTING_ADVISORY",
                "applied": True,
                "selected_source_families": ["ATLAS"],
                "source_refs": ["atlas/ref-once.md"],
                "source_context_authority": "NONE",
                "source_context_mode": "ADVISORY_ONLY",
                "raw_content_included": False,
            },
            "reverse_os_projection": {"ir_candidate": {}},
            "deep_cognitive_signal_snapshot": {},
            "components": {"SOURCE_ROUTING": "READY:PRECOMPUTED:ADVISORY_ONLY"},
            "kx108_admission": "DRY_RUN",
            "decision_ticket_dry_run": {"decision": "ALLOW_CONTEXT_ONLY"},
            "readonly": True,
            "memory_write": False,
            "emits_act": False,
            "kernel_mutation": False,
            "decision_authority": "KX108_ONLY",
        }

    def fake_true_voice(*, source_pack_context=None, **kwargs):
        calls["true_voice"] += 1
        calls["true_voice_ctx_id"] = id(source_pack_context)
        return {
            "final_answer": "source-pack preserved",
            "voice_source": "SOURCE_PACK_CONTEXT",
            "source_pack_enriched": True,
            "source_pack_context_used": True,
            "readonly": True,
            "memory_write": False,
            "emits_act": False,
        }

    monkeypatch.setattr(
        brody_route,
        "_build_source_pack_context",
        fake_source_context,
    )
    monkeypatch.setattr(
        cognitive_join,
        "run_real_cognitive_join",
        fake_c1,
    )
    monkeypatch.setattr(
        brody_route,
        "build_true_brody_answer",
        fake_true_voice,
    )

    r = client.post("/api/brody/chat", json={
        "message": "atlas source routing audit",
        "language": "fr",
        "session_id": "source-routing-once",
    })

    assert r.status_code == 200
    data = r.json()
    assert calls["source_build"] == 1
    assert calls["c1"] == 1
    assert calls["true_voice"] == 1
    assert calls["c1_ctx_id"] == calls["true_voice_ctx_id"]
    assert data["source_pack_context_used"] is True
    assert data["final_answer_source_pack_enriched"] is True
    assert data["cognitive_runtime_receipt"][
        "source_routing_signal_snapshot"
    ]["applied"] is True
    assert data["brody_full_context"]["governed_cognitive_projection"][
        "source_routing_signal_snapshot"
    ]["selected_source_families"] == ["ATLAS"]
