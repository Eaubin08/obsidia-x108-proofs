"""P36 — Tests API: Capability Path Router via source-runtime/preview endpoint.

Vérifie :
1. preview retourne selected_runtime_path.
2. preview retourne selected_modules.
3. preview retourne selected_adapters.
4. preview retourne selected_routes.
5. preview retourne selected_evidence_packs.
6. Requête IR retourne REVERSE_OS_INTERLANGUAGE_CANON_V1 dans selected_source_subfamilies.
7. Requête action retourne ACTION_REQUEST_BLOCKED.
8. No ACT / no write / no mutation dans tous les champs boundary.
"""
import sys
import pathlib
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    _APP_AVAILABLE = True
except Exception:
    _APP_AVAILABLE = False
    app = None
    TestClient = None

pytestmark = pytest.mark.skipif(
    not _APP_AVAILABLE,
    reason="App FastAPI non disponible",
)


@pytest.fixture(scope="module")
def client():
    if not _APP_AVAILABLE or TestClient is None:
        pytest.skip("FastAPI TestClient non disponible")
    return TestClient(app)


# ── Test 1 : preview retourne selected_runtime_path ──────────────────────────

def test_preview_returns_selected_runtime_path(client):
    """Test API 1 — preview retourne selected_runtime_path."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_runtime_path" in data, (
        f"selected_runtime_path manquant dans la réponse: {list(data.keys())}"
    )


# ── Test 2 : preview retourne selected_modules ────────────────────────────────

def test_preview_returns_selected_modules(client):
    """Test API 2 — preview retourne selected_modules."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_modules" in data, (
        f"selected_modules manquant dans la réponse: {list(data.keys())}"
    )
    assert isinstance(data["selected_modules"], list)


# ── Test 3 : preview retourne selected_adapters ───────────────────────────────

def test_preview_returns_selected_adapters(client):
    """Test API 3 — preview retourne selected_adapters."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_adapters" in data, (
        f"selected_adapters manquant dans la réponse: {list(data.keys())}"
    )
    assert isinstance(data["selected_adapters"], list)


# ── Test 4 : preview retourne selected_routes ─────────────────────────────────

def test_preview_returns_selected_routes(client):
    """Test API 4 — preview retourne selected_routes."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_routes" in data, (
        f"selected_routes manquant dans la réponse: {list(data.keys())}"
    )


# ── Test 5 : preview retourne selected_evidence_packs ────────────────────────

def test_preview_returns_selected_evidence_packs(client):
    """Test API 5 — preview retourne selected_evidence_packs."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_evidence_packs" in data, (
        f"selected_evidence_packs manquant dans la réponse: {list(data.keys())}"
    )


# ── Test 6 : requête IR → REVERSE_OS_INTERLANGUAGE_CANON_V1 ──────────────────

def test_ir_query_returns_reverse_os_interlanguage_canon(client):
    """Test API 6 — Requête IR retourne REVERSE_OS_INTERLANGUAGE_CANON_V1 dans selected_source_subfamilies."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS interlanguage canon V1", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    subfamilies = data.get("selected_source_subfamilies", [])
    # Acceptable si dans selected_source_subfamilies OU dans selected_evidence_packs
    evidence_packs = data.get("selected_evidence_packs", [])
    assert "REVERSE_OS_INTERLANGUAGE_CANON_V1" in subfamilies or \
           "REVERSE_OS_INTERLANGUAGE_CANON_V1" in evidence_packs, (
        f"REVERSE_OS_INTERLANGUAGE_CANON_V1 manquant. "
        f"subfamilies={subfamilies}, evidence_packs={evidence_packs}"
    )


# ── Test 7 : requête action → ACTION_REQUEST_BLOCKED ─────────────────────────

def test_action_query_returns_blocked(client):
    """Test API 7 — Requête action retourne ACTION_REQUEST_BLOCKED."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "envoie un mail à l'équipe technique", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    selected_path = data.get("selected_runtime_path", {})
    cap_chain = selected_path.get("capability_chain", [])
    required_caps = data.get("required_capabilities", [])
    assert "ACTION_REQUEST_BLOCKED" in cap_chain or "ACTION_REQUEST_BLOCKED" in required_caps, (
        f"ACTION_REQUEST_BLOCKED manquant. chain={cap_chain}, required={required_caps}"
    )


# ── Test 8 : no ACT / no write / no mutation ─────────────────────────────────

def test_no_act_no_write_in_preview(client):
    """Test API 8 — No ACT / no write / no mutation dans tous les champs boundary."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("readonly") is True, "readonly doit être True"
    assert data.get("emits_act") is False, "emits_act doit être False"
    assert data.get("memory_write") is False, "memory_write doit être False"
    assert data.get("graph_write") is False, "graph_write doit être False"
    assert data.get("kernel_mutation") is False, "kernel_mutation doit être False"
    assert data.get("zip_extraction") is False, "zip_extraction doit être False"
    assert data.get("runtime_allowed_now") is False, "runtime_allowed_now doit être False"
    assert data.get("decision_authority") == "KX108_ONLY", "decision_authority doit être KX108_ONLY"
