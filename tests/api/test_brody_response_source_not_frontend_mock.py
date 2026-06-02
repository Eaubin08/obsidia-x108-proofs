"""
V5B API Test: API responses never have source=FRONTEND_MOCK.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_brody_source_not_frontend_mock():
    for msg in ["salut", "hello", "test context", "autorise act"]:
        r = client.post("/api/brody/chat", json={"message": msg})
        data = r.json()
        assert data["source"] != "FRONTEND_MOCK", f"source FRONTEND_MOCK for: {msg}"
        assert data["source"] in (
            "REAL_BACKEND", "BACKEND_STUB", "REAL_BRODY_RUNTIME_NO_GRAPHITI",
            "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE", "REAL_BRODY_LOCAL_RESPONSE_ENGINE",
            "REAL_BRODY_GRAPHITI_LIVE", "LIVE_EMPTY_REGISTRY",
        )


def test_status_source_is_real_backend():
    r = client.get("/api/status")
    data = r.json()
    assert data["source"] == "REAL_BACKEND"


def test_memory_source_honest():
    r = client.get("/api/memory")
    data = r.json()
    assert data["source"] in ("REAL_BACKEND", "BACKEND_STUB", "REAL_BRODY_RUNTIME_NO_GRAPHITI", "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE", "REAL_BRODY_LOCAL_RESPONSE_ENGINE")


def test_gencoin_source_honest():
    r = client.get("/api/gencoin")
    data = r.json()
    assert data["source"] in (
        "REAL_BACKEND", "BACKEND_STUB", "REAL_BRODY_RUNTIME_NO_GRAPHITI",
        "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE", "REAL_BRODY_LOCAL_RESPONSE_ENGINE",
        "LIVE_EMPTY_REGISTRY",
    )
