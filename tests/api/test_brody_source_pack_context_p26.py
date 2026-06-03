"""P26 — Brody API integration test: source pack context injection.

Verifies that POST /api/brody/chat correctly injects source pack context when
packs are available, and falls back cleanly when they are not.
Sovereignty invariants (emits_act, decision_authority, etc.) are always verified.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

# Detect if packs are locally available (affects assertions)
try:
    from runtime_wiring.source_runtime.source_pack_resolver import list_available_families
    _PACKS_AVAILABLE = len(list_available_families()) > 0
except Exception:
    _PACKS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Main P26 test
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_source_pack_context_injection():
    """POST /chat with a message covering Cognitive + NPL sources.

    When packs are present: source_pack_context_used=True, x108_decision=ALLOW_CONTEXT_ONLY.
    When packs absent: source_pack_context_used=False, no crash.
    In all cases: emits_act=False, decision_authority=KX108_ONLY.
    """
    r = client.post("/api/brody/chat", json={
        "message": "Explique X108 avec les sources Cognitive et NPL disponibles",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    # Sovereignty invariants — always true regardless of packs
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True
    assert data.get("memory_write") is False
    assert data.get("kernel_mutation") is False

    # Source pack field always present (True or False)
    assert "source_pack_context_used" in data

    if _PACKS_AVAILABLE:
        assert data["source_pack_context_used"] is True, (
            "Packs are locally available — expected source_pack_context_used=True"
        )
        assert data.get("source_pack_entries_used", 0) >= 1
        assert data.get("source_pack_x108_decision") == "ALLOW_CONTEXT_ONLY"
        assert isinstance(data.get("source_pack_families"), list)
        assert len(data["source_pack_families"]) >= 1
    else:
        # Clean fallback — no crash, no injection
        assert data["source_pack_context_used"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Sovereignty never degraded by source pack injection
# ─────────────────────────────────────────────────────────────────────────────

def test_source_pack_does_not_degrade_sovereignty():
    """Source pack context must not override sovereignty flags."""
    r = client.post("/api/brody/chat", json={
        "message": "Résume les sources disponibles dans le registry",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    sovereignty_keys = [
        "emits_act", "emits_verdict", "memory_write", "graphiti_write",
        "neo4j_write", "kernel_mutation", "x108_mutation", "allowed_to_decide",
    ]
    for key in sovereignty_keys:
        if key in data:
            assert data[key] is False, f"{key} must be False — source pack must not degrade sovereignty"

    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True


# ─────────────────────────────────────────────────────────────────────────────
# Source pack context dict shape
# ─────────────────────────────────────────────────────────────────────────────

def test_source_pack_context_shape():
    """Verify the shape of source_pack_context nested dict."""
    r = client.post("/api/brody/chat", json={
        "message": "Quelles sont les familles de source packs disponibles ?",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    # Top-level keys always present
    assert "source_pack_context_used" in data
    assert "source_pack_entries_used" in data
    assert "source_pack_families" in data
    assert "source_pack_x108_decision" in data
    assert "source_pack_os3_evidence_id" in data

    # Nested dict (may be empty fallback)
    ctx = data.get("source_pack_context", {})
    assert isinstance(ctx, dict)

    if ctx.get("source_pack_context_used"):
        # When used: mandatory safety fields
        assert ctx.get("no_act") is True
        assert ctx.get("memory_write") is False
        assert ctx.get("zip_extraction") is False
        boundary = ctx.get("boundary", {})
        assert boundary.get("emits_act") is False
        assert boundary.get("decision_authority") == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Fallback on unrelated query — no crash
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_fallback_on_generic_query():
    """Generic query should still return 200 with source_pack field present."""
    r = client.post("/api/brody/chat", json={
        "message": "Bonjour Brody, comment vas-tu ?",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()
    assert "source_pack_context_used" in data
    assert data.get("emits_act") is False
