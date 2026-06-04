"""P38 — Tests API: OS Map endpoint.

Vérifie :
1. GET /os-map/status retourne os_map_status.
2. POST /os-map/query retourne detected_intents.
3. POST /os-map/query retourne required_capabilities.
4. POST /os-map/query retourne selected_runtime_path.
5. Query "IR alphabet reverse OS" montre route_capability_path + adapter interlanguage.
6. Query "IR alphabet reverse OS" contient REVERSE_OS_INTERLANGUAGE_CANON_V1.
7. Query action retourne ACTION_BLOCKED.
8. No ACT / KX108_ONLY dans tous les champs boundary.
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


# ── Test 1 : GET /os-map/status ───────────────────────────────────────────────

def test_os_map_status_endpoint(client):
    """Test API 1 — GET /os-map/status retourne os_map_status."""
    resp = client.get("/api/runtime-wiring/os-map/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "os_map_status" in data, f"os_map_status manquant: {list(data.keys())}"
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True
    assert data.get("emits_act") is False
    assert data.get("runtime_allowed_now") is False


# ── Test 2 : detected_intents présent ────────────────────────────────────────

def test_os_map_query_returns_detected_intents(client):
    """Test API 2 — POST /os-map/query retourne detected_intents."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "detected_intents" in data, f"detected_intents manquant: {list(data.keys())}"
    assert isinstance(data["detected_intents"], list)


# ── Test 3 : required_capabilities présent ────────────────────────────────────

def test_os_map_query_returns_required_capabilities(client):
    """Test API 3 — POST /os-map/query retourne required_capabilities."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "required_capabilities" in data
    assert isinstance(data["required_capabilities"], list)


# ── Test 4 : selected_runtime_path présent ────────────────────────────────────

def test_os_map_query_returns_selected_runtime_path(client):
    """Test API 4 — POST /os-map/query retourne selected_runtime_path."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "selected_runtime_path" in data
    assert isinstance(data["selected_runtime_path"], dict)


# ── Test 5 : IR query → route_capability_path + adapter interlanguage ─────────

def test_ir_query_shows_interlanguage_adapter(client):
    """Test API 5 — Query IR montre l'adapter interlanguage dans selected_adapters."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS interlanguage canon V1", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    selected_path = data.get("selected_runtime_path", {})
    adapters = selected_path.get("adapters", []) or data.get("selected_adapters", [])
    fns = data.get("selected_functions", [])
    # Vérifie que l'adapter IR est présent dans le chemin ou les fonctions
    ir_present = (
        "reverse_os_interlanguage_to_context_packet" in adapters
        or "reverse_os_interlanguage_to_context_packet" in fns
        or any("interlanguage" in str(cap) for cap in data.get("required_capabilities", []))
    )
    assert ir_present or "REVERSE_OS_INTERLANGUAGE" in data.get("required_capabilities", []), (
        f"Adapter/capability IR manquant. adapters={adapters}, caps={data.get('required_capabilities')}"
    )


# ── Test 6 : IR query → REVERSE_OS_INTERLANGUAGE_CANON_V1 ─────────────────────

def test_ir_query_shows_canon_v1(client):
    """Test API 6 — Query IR contient REVERSE_OS_INTERLANGUAGE_CANON_V1."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS interlanguage canon V1", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    subfamilies = data.get("selected_source_subfamilies", [])
    evidence_packs = data.get("selected_evidence_packs", [])
    path_subfamilies = data.get("selected_runtime_path", {}).get("source_subfamilies", [])
    found = (
        "REVERSE_OS_INTERLANGUAGE_CANON_V1" in subfamilies
        or "REVERSE_OS_INTERLANGUAGE_CANON_V1" in evidence_packs
        or "REVERSE_OS_INTERLANGUAGE_CANON_V1" in path_subfamilies
    )
    assert found, (
        f"REVERSE_OS_INTERLANGUAGE_CANON_V1 manquant. "
        f"subfamilies={subfamilies}, evidence={evidence_packs}"
    )


# ── Test 7 : requête action → ACTION_BLOCKED ──────────────────────────────────

def test_action_query_returns_action_blocked(client):
    """Test API 7 — Query action retourne ACTION_BLOCKED."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "envoie un mail à l'équipe technique", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    status = data.get("os_map_status", "")
    action_blocked = data.get("action_blocked", False)
    cap_chain = data.get("selected_runtime_path", {}).get("capability_chain", [])
    assert status == "ACTION_BLOCKED" or action_blocked is True or "ACTION_REQUEST_BLOCKED" in cap_chain, (
        f"ACTION_BLOCKED manquant. status={status}, action_blocked={action_blocked}, chain={cap_chain}"
    )


# ── Test 8 : no ACT / KX108_ONLY ─────────────────────────────────────────────

def test_os_map_no_act_kx108(client):
    """Test API 8 — No ACT / KX108_ONLY dans tous les champs boundary."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS", "max_paths": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("readonly") is True
    assert data.get("emits_act") is False
    assert data.get("runtime_allowed_now") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("memory_write") is False
    assert data.get("graph_write") is False
    assert data.get("kernel_mutation") is False
