"""P32 — API tests: OS_TRAD_REVERSE_OS visible dans l'API source runtime.

Vérifie :
1. /api/runtime-wiring/source-runtime/status retourne 8 familles si zip présent.
2. OS_TRAD_REVERSE_OS apparaît dans la liste des familles.
3. POST /preview sélectionne OS_TRAD sur query dédiée.
4. Sovereignty inchangée (emits_act=False, KX108_ONLY).
5. Brody final_answer n'est pas dégradé.
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
    from runtime_wiring.source_runtime.source_pack_resolver import is_source_pack_available
    _ZIP_AVAILABLE = is_source_pack_available(
        "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip"
    )
except Exception:
    _ZIP_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 : /preview expose source_runtime_family_count >= 7
# ─────────────────────────────────────────────────────────────────────────────

def test_preview_family_count_at_least_7():
    """GET /preview expose source_runtime_family_count >= 7."""
    r = client.get("/api/runtime-wiring/preview")
    assert r.status_code == 200
    data = r.json()
    count = data.get("source_runtime_family_count", 0)
    assert count >= 7, f"Attendu >=7 familles, obtenu {count}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 : /status retourne 8 familles si zip présent
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _ZIP_AVAILABLE, reason="ZIP OS_TRAD non disponible localement")
def test_status_endpoint_shows_8_families():
    """GET /source-runtime/status retourne 8 familles si zip OS_TRAD présent."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()
    families = data.get("source_runtime_families", [])
    assert "OS_TRAD_REVERSE_OS" in families, f"OS_TRAD absent: {families}"
    assert len(families) == 8, f"Attendu 8 familles, obtenu {len(families)}: {families}"
    assert data.get("source_runtime_family_count") == 8


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 : POST /preview sélectionne OS_TRAD sur query dédiée
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _ZIP_AVAILABLE, reason="ZIP OS_TRAD non disponible localement")
def test_source_runtime_preview_selects_os_trad():
    """POST /source-runtime/preview sélectionne OS_TRAD_REVERSE_OS sur query dédiée."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "reverse os 34 arbres agents 52 pipeline cognitif ssr mmonde",
        "limit": 3,
    })
    assert r.status_code == 200
    data = r.json()
    selected = data.get("selected_families", [])
    assert "OS_TRAD_REVERSE_OS" in selected, f"OS_TRAD non sélectionné: {selected}"
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 : Sovereignty inchangée dans /status
# ─────────────────────────────────────────────────────────────────────────────

def test_status_sovereignty_unchanged():
    """GET /source-runtime/status : tous les flags boundary sont False."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()
    for key in ("emits_act", "memory_write", "graph_write", "kernel_mutation", "zip_extraction", "world_action"):
        assert data.get(key) is False, f"{key} doit être False dans /status"
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 : Brody chat reste souverain après P32
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_sovereignty_after_p32():
    """POST /api/brody/chat : sovereignty inchangée après ajout OS_TRAD."""
    r = client.post("/api/brody/chat", json={
        "message": "Explique le reverse os et les 34 arbres cognitifs Obsidia",
        "language": "fr",
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    for key in ("memory_write", "kernel_mutation", "graphiti_write"):
        if key in data:
            assert data[key] is False, f"{key} doit être False"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 : Workbench preview /preview expose source_runtime_status READY
# ─────────────────────────────────────────────────────────────────────────────

def test_preview_source_runtime_status_ready():
    """GET /preview retourne source_runtime_status READY ou PARTIAL (pas UNAVAILABLE)."""
    r = client.get("/api/runtime-wiring/preview")
    assert r.status_code == 200
    data = r.json()
    status = data.get("source_runtime_status")
    assert status in ("READY", "PARTIAL"), f"Status inattendu: {status}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 : /preview ne régresse pas les 7 familles existantes
# ─────────────────────────────────────────────────────────────────────────────

def test_existing_families_still_present():
    """GET /source-runtime/status : les 7 familles P24-P31 restent présentes."""
    r = client.get("/api/runtime-wiring/source-runtime/status")
    assert r.status_code == 200
    data = r.json()
    families = data.get("source_runtime_families", [])
    expected_7 = {
        "ATLAS", "COGNITIVE_REINTEGRATION", "COMPLIANCE_DATA_GOVERNANCE",
        "EXTERNAL_SIGNALS", "NARRATIVE_PROVENANCE_LAYER", "RSSI_RGPD",
        "RSSI_SECURITY_PRESENTATION",
    }
    for fam in expected_7:
        assert fam in families, f"Famille existante disparue après P32: {fam}"
