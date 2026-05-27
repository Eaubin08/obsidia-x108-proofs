from fastapi.testclient import TestClient

from apps.obsidia_api.main import app


client = TestClient(app)


def _get(path: str):
    response = client.get(path)
    assert response.status_code == 200, response.text
    return response.json()


def _assert_readonly(payload):
    serialized = str(payload)
    assert "KX108_ONLY" in serialized
    assert payload.get("emits_act") is False
    assert payload.get("emits_verdict") is False
    assert payload.get("graphiti_write") is False
    assert payload.get("neo4j_write") is False


def test_graphiti_status_readonly():
    data = _get("/api/graphiti/status")
    _assert_readonly(data)


def test_graphiti_readiness_readonly():
    data = _get("/api/graphiti/readiness")
    _assert_readonly(data)


def test_graphiti_context_readonly():
    data = _get("/api/graphiti/context?q=Brody&limit=5")
    _assert_readonly(data)
    assert "results" in data
