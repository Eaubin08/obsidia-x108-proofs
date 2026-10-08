from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


ROUTE = Path("apps/obsidia_api/routes/brody.py")


def _client():
    app.dependency_overrides[require_api_key] = lambda: None
    return TestClient(app)


def test_route_no_longer_imports_legacy_graphiti_memory_activation():
    src = ROUTE.read_text(encoding="utf-8-sig")
    assert "graphiti_memory_readonly_activation" not in src
    assert "build_graphiti_memory_readonly_activation_state" not in src
    assert "_graphiti_memory_state" not in src


def test_top_level_memory_truth_is_native_memory():
    client = _client()
    r = client.post(
        "/api/brody/chat",
        json={
            "message": "retrouve contextpacket dans la memoire precedente",
            "language": "fr",
        },
    )
    assert r.status_code == 200
    data = r.json()

    chain = data["memory_response_chain_snapshot"]
    project = data["project_memory_snapshot"]

    assert chain["source_mode"] == "OBSIDIA_NATIVE_MEMORY"
    assert project["source_mode"] == "OBSIDIA_NATIVE_MEMORY"
    assert data["real_memory_component_found"] is bool(project["native_memory_ready"])
    assert data["memory_read_enabled"] is bool(project["native_memory_ready"])
    assert data["memory_write_enabled"] is False
    assert data["memory_write"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert "graphiti_status" not in data
    assert "neo4j_status" not in data
