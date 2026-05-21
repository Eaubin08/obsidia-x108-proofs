"""
V5B API Test: No memory write on any API endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

ENDPOINTS = [
    ("GET", "/api/status"),
    ("GET", "/api/memory"),
    ("GET", "/api/gencoin"),
]


@pytest.mark.parametrize("method,path", ENDPOINTS)
def test_endpoint_no_memory_write(method, path):
    r = client.request(method, path)
    assert r.status_code == 200
    data = r.json()
    assert data.get("memory_write", None) is False
    assert data.get("real_action", None) is False
    assert data.get("emits_act", None) is False


def test_brody_chat_no_memory_write():
    r = client.post("/api/brody/chat", json={"message": "test"})
    data = r.json()
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["real_action"] is False
