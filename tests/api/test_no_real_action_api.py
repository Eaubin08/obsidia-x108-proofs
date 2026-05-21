"""TEST: No real action on any API endpoint."""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


@pytest.mark.parametrize("method,path", [
    ("GET", "/api/status"),
    ("GET", "/api/memory"),
    ("GET", "/api/gencoin"),
])
def test_endpoint_no_real_action(method, path):
    r = client.request(method, path)
    assert r.status_code == 200
    data = r.json()
    assert data.get("real_action", True) is False


def test_brody_chat_no_real_action():
    r = client.post("/api/brody/chat", json={"message": "execute action"})
    data = r.json()
    assert data["real_action"] is False
