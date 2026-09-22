"""P28 — Brody API tests: cache + smart family selection.

Verifies that:
1. source_pack_selected_families reflects smart selection
2. source_pack_cache_hit is a boolean
3. source_pack_runtime_stats is present and valid
4. /api/runtime-wiring/preview exposes source_runtime_* fields
5. Sovereignty never degraded
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

try:
    from runtime_wiring.source_runtime.source_pack_resolver import list_available_families
    _PACKS_AVAILABLE = len(list_available_families()) > 0
except Exception:
    _PACKS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Smart family selection reflected in Brody payload
# ─────────────────────────────────────────────────────────────────────────────

def test_smart_family_selection_in_payload():
    """P28 cache + selector: source_pack_selected_families present."""
    r = client.post("/api/brody/chat", json={
        "message": "Explique X108 et la gouvernance Obsidia Cognitive",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    # Sovereignty always
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"

    ctx = data.get("source_pack_context", {})
    if ctx.get("source_pack_context_used"):
        assert "source_pack_selected_families" in ctx
        assert isinstance(ctx["source_pack_selected_families"], list)
        assert len(ctx["source_pack_selected_families"]) >= 1

        # X108 message → COGNITIVE_REINTEGRATION should be selected
        assert "COGNITIVE_REINTEGRATION" in ctx["source_pack_selected_families"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Cache hit tracking
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_hit_field_present():
    """source_pack_cache_hit is a boolean in the nested context dict."""
    r = client.post("/api/brody/chat", json={
        "message": "Résume les sources ATLAS disponibles",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    ctx = data.get("source_pack_context", {})
    if ctx.get("source_pack_context_used"):
        assert "source_pack_cache_hit" in ctx
        assert isinstance(ctx["source_pack_cache_hit"], bool)


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Runtime stats field present and shaped correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_runtime_stats_present():
    """source_pack_runtime_stats is a dict with required keys."""
    r = client.post("/api/brody/chat", json={
        "message": "Sources disponibles pour Obsidia",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    ctx = data.get("source_pack_context", {})
    if ctx.get("source_pack_context_used"):
        assert "source_pack_runtime_stats" in ctx
        stats = ctx["source_pack_runtime_stats"]
        assert isinstance(stats, dict)
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "registry_ttl_seconds" in stats
        assert stats.get("decision_authority") == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Second request benefits from cache (hit_rate increases)
# ─────────────────────────────────────────────────────────────────────────────

def test_second_request_cache_hit(request):
    """After warm-up, a second identical query should show cache_hits > 0."""
    from runtime_wiring.source_runtime.source_runtime_cache import clear_cache
    clear_cache()
    request.addfinalizer(clear_cache)
    # First request — warms cache
    r1 = client.post("/api/brody/chat", json={
        "message": "X108 Cognitive sources",
        "language": "fr",
    })
    # Second request — should hit cache
    r2 = client.post("/api/brody/chat", json={
        "message": "X108 Cognitive sources",
        "language": "fr",
    })
    assert r1.status_code == 200
    assert r2.status_code == 200

    ctx2 = r2.json().get("source_pack_context", {})
    if ctx2.get("source_pack_context_used") and "source_pack_cache_hit" in ctx2:
        # Second call should be a cache hit
        assert ctx2["source_pack_cache_hit"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: /api/runtime-wiring/preview exposes source_runtime fields
# ─────────────────────────────────────────────────────────────────────────────

def test_runtime_wiring_preview_source_runtime_fields():
    """P28: /api/runtime-wiring/preview includes source_runtime_* fields."""
    r = client.get("/api/runtime-wiring/preview")
    assert r.status_code == 200
    data = r.json()

    assert "source_runtime_available" in data
    assert "source_runtime_cache_enabled" in data
    assert "source_runtime_families" in data
    assert "brody_context_bridge_available" in data
    assert "real_readonly_hydration_available" in data

    # These must be booleans
    assert isinstance(data["source_runtime_available"], bool)
    assert isinstance(data["brody_context_bridge_available"], bool)

    # If source runtime available, families list should be populated
    if data["source_runtime_available"]:
        assert isinstance(data["source_runtime_families"], list)
        assert len(data["source_runtime_families"]) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: P27 fields still present (no regression)
# ─────────────────────────────────────────────────────────────────────────────

def test_p27_fields_not_broken_by_p28():
    """P28 must not remove P27 fields from the Brody payload."""
    r = client.post("/api/brody/chat", json={
        "message": "X108 source packs cognitive npl",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    p27_fields = [
        "source_pack_context_summary",
        "final_answer_source_pack_enriched",
        "source_pack_context_used",
        "source_pack_families",
        "source_pack_entries_used",
        "source_pack_x108_decision",
    ]
    for field in p27_fields:
        assert field in data, f"P27 field missing after P28: {field}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Sovereignty invariants never degraded by P28
# ─────────────────────────────────────────────────────────────────────────────

def test_p28_does_not_degrade_sovereignty():
    """All sovereignty flags remain False after P28 changes."""
    r = client.post("/api/brody/chat", json={
        "message": "RSSI sécurité conformité audit sources",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()

    for key in ("emits_act", "memory_write", "kernel_mutation", "graphiti_write"):
        if key in data:
            assert data[key] is False, f"{key} must remain False"
    assert data.get("decision_authority") == "KX108_ONLY"
