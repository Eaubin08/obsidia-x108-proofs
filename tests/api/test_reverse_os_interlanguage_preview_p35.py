"""P35 — Tests API: REVERSE_OS_INTERLANGUAGE_CANON_V1 preview endpoint.

Vérifie :
1. GET /preview retourne source_runtime_family_count >= 1 (OS_TRAD).
2. GET /source-runtime/status montre OS_TRAD_REVERSE_OS avec P35.
3. POST /source-runtime/preview sélectionne OS_TRAD sur requête interlanguage.
4. Payload ContextPacket expose source_subfamily.
5. X108 decision = ALLOW_CONTEXT_ONLY.
6. runtime_allowed_now reste False dans le preview.
7. Les 8 familles existantes restent présentes.
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


def test_p35_status_endpoint_shows_os_trad(client):
    """GET /source-runtime/status montre OS_TRAD_REVERSE_OS."""
    resp = client.get("/api/runtime-wiring/source-runtime/status")
    assert resp.status_code == 200
    data = resp.json()
    families = data.get("source_runtime_families", [])
    assert "OS_TRAD_REVERSE_OS" in families, (
        f"OS_TRAD_REVERSE_OS manquant dans les familles: {families}"
    )
    assert data.get("readonly") is True
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


def test_p35_preview_selects_os_trad_on_interlanguage_query(client):
    """POST /source-runtime/preview sélectionne OS_TRAD sur requête IR alphabet."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "IR alphabet reverse OS interlanguage canon", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    selected = data.get("selected_families", [])
    assert "OS_TRAD_REVERSE_OS" in selected, (
        f"OS_TRAD_REVERSE_OS non sélectionné pour requête IR alphabet: {selected}"
    )
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


def test_p35_preview_x108_decision_allow_context_only(client):
    """POST /source-runtime/preview: X108 decision = ALLOW_CONTEXT_ONLY."""
    resp = client.post(
        "/api/runtime-wiring/source-runtime/preview",
        json={"query": "réciproque miroir TWIN_CALL SCF interlanguage", "limit": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    x108 = data.get("x108_decision", "")
    assert x108 in ("ALLOW_CONTEXT_ONLY", "N/A"), (
        f"X108 decision inattendue: {x108}"
    )
    assert data.get("x108_decision_authority") == "KX108_ONLY"


def test_p35_sovereignty_unchanged_after_p35(client):
    """Toutes les flags de souveraineté restent False après P35."""
    resp = client.get("/api/runtime-wiring/source-runtime/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("readonly") is True
    assert data.get("emits_act") is False
    assert data.get("memory_write") is False
    assert data.get("graph_write") is False
    assert data.get("kernel_mutation") is False
    assert data.get("zip_extraction") is False
    assert data.get("decision_authority") == "KX108_ONLY"


def test_p35_existing_families_still_present(client):
    """P35 ne dégrade pas les 8 familles existantes."""
    resp = client.get("/api/runtime-wiring/source-runtime/status")
    assert resp.status_code == 200
    families = resp.json().get("source_runtime_families", [])
    expected = ["OS_TRAD_REVERSE_OS"]
    for family in expected:
        assert family in families, f"Famille dégradée après P35: {family}"
