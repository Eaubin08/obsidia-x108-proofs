"""P29 — Tests: source runtime status endpoint + champs preview enrichis.

Vérifie :
1. /api/runtime-wiring/preview expose source_runtime_status + source_runtime_family_count
   + source_runtime_registry_entries (nouveaux champs P29)
2. source_runtime_available == True si modules présents
3. source_runtime_families liste valide
4. /api/runtime-wiring/source-runtime/status retourne cache_stats
5. readonly == True dans le status endpoint
6. emits_act == False dans le status endpoint
7. decision_authority == KX108_ONLY
8. Aucun champ boundary ne déclenche ACT/write/extraction
9. (bonus) POST /preview avec query X108 → selected_families, x108_decision, emits_act=False
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
# Test 1 : /preview expose les nouveaux champs P29
# ─────────────────────────────────────────────────────────────────────────────

def test_preview_exposes_p29_derived_fields():
    """GET /preview inclut source_runtime_status, source_runtime_family_count, source_runtime_registry_entries."""
    r = client.get("/api/runtime-wiring/preview")
    assert r.status_code == 200
    data = r.json()

    assert "source_runtime_status" in data, "source_runtime_status manquant"
    assert "source_runtime_family_count" in data, "source_runtime_family_count manquant"
    assert "source_runtime_registry_entries" in data, "source_runtime_registry_entries manquant"

    assert isinstance(data["source_runtime_status"], str)
    assert data["source_runtime_status"] in ("READY", "PARTIAL", "UNAVAILABLE")
    assert isinstance(data["source_runtime_family_count"], int)
    assert isinstance(data["source_runtime_registry_entries"], int)


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 : source_runtime_available == True si modules présents
# ─────────────────────────────────────────────────────────────────────────────

def test_source_runtime_available_is_true():
    """source_runtime_available doit être True (modules P26-P28 présents)."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()

    assert "source_runtime_available" in data
    assert data["source_runtime_available"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 : source_runtime_families liste valide
# ─────────────────────────────────────────────────────────────────────────────

def test_source_runtime_families_list():
    """source_runtime_families est une liste. Si packs dispo, contient 7 familles."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()

    assert "source_runtime_families" in data
    assert isinstance(data["source_runtime_families"], list)

    if _PACKS_AVAILABLE:
        assert len(data["source_runtime_families"]) == 7, (
            f"Attendu 7 familles, obtenu {len(data['source_runtime_families'])}"
        )
        expected = {
            "COGNITIVE_REINTEGRATION", "RSSI_RGPD", "ATLAS",
            "COMPLIANCE_DATA_GOVERNANCE", "RSSI_SECURITY_PRESENTATION",
            "EXTERNAL_SIGNALS", "NARRATIVE_PROVENANCE_LAYER",
        }
        actual = set(data["source_runtime_families"])
        assert actual == expected, f"Familles inattendues : {actual ^ expected}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 : cache_stats présent et structuré
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_stats_present_and_shaped():
    """cache_stats est présent avec les clés requises."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()

    assert "cache_stats" in data
    cs = data["cache_stats"]
    assert isinstance(cs, dict)
    assert "cache_hits" in cs
    assert "cache_misses" in cs
    assert "ttl_seconds" in cs
    assert cs["ttl_seconds"] == 60


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 : readonly == True
# ─────────────────────────────────────────────────────────────────────────────

def test_status_endpoint_readonly():
    """Le status endpoint retourne readonly=True."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    assert r.json().get("readonly") is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 : emits_act == False
# ─────────────────────────────────────────────────────────────────────────────

def test_status_endpoint_no_act():
    """Le status endpoint retourne emits_act=False."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    assert r.json().get("emits_act") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 : decision_authority == KX108_ONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_status_decision_authority():
    """decision_authority doit être KX108_ONLY."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    assert r.json().get("decision_authority") == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 : aucun champ boundary ne déclenche ACT/write/extraction
# ─────────────────────────────────────────────────────────────────────────────

def test_status_all_boundary_flags_safe():
    """Tous les flags de boundary sont False (no ACT, no write, no extraction)."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()

    for key in ("emits_act", "memory_write", "graph_write", "kernel_mutation", "zip_extraction", "world_action"):
        assert data.get(key) is False, f"{key} doit être False dans le status endpoint"


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 (bonus) : POST /preview — souveraineté et champs attendus
# ─────────────────────────────────────────────────────────────────────────────

def test_source_runtime_preview_basic():
    """POST /preview retourne selected_families, x108_decision, emits_act=False."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "X108 gouvernance cognitive kernel",
        "limit": 3,
    })
    assert r.status_code == 200
    data = r.json()

    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True
    assert "selected_families" in data
    assert isinstance(data["selected_families"], list)
    assert "x108_decision" in data


def test_source_runtime_preview_no_act_flags():
    """POST /preview : tous les flags boundary sont False."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "RSSI sécurité conformité",
        "limit": 2,
    })
    assert r.status_code == 200
    data = r.json()

    for key in ("emits_act", "memory_write", "graph_write", "kernel_mutation", "zip_extraction"):
        assert data.get(key) is False, f"{key} doit être False dans le preview endpoint"


@pytest.mark.skipif(not _PACKS_AVAILABLE, reason="source packs non disponibles localement")
def test_source_runtime_preview_with_packs():
    """Avec packs dispo : POST /preview renvoie des familles sélectionnées cohérentes."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "X108 gouvernance cognitive kernel",
        "limit": 3,
    })
    assert r.status_code == 200
    data = r.json()

    if data.get("source_runtime_status") == "PREVIEW_READY":
        assert len(data["selected_families"]) >= 1
        assert "COGNITIVE_REINTEGRATION" in data["selected_families"]
        assert data["x108_decision"] == "ALLOW_CONTEXT_ONLY"
