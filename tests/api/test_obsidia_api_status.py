"""
V5B API Test: /api/status returns correct structure.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_root_returns_version():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "obsidia-api"
    assert data["decision_authority"] == "KX108_ONLY"


def test_api_status_ok():
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "obsidia-api"
    assert data["mode"] == "readonly_dryrun"
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["readonly"] is True
    assert data["emits_act"] is False
    assert data["memory_write"] is False
    assert data["real_action"] is False
    assert "runtime_components" in data


def test_api_status_has_brody():
    r = client.get("/api/status")
    data = r.json()
    assert "brody" in data["runtime_components"]
    assert data["brody"] in ("REAL_MODULE", "BACKEND_STUB", "MODULE_ERROR")


def test_x108_status():
    r = client.get("/api/x108/status")
    assert r.status_code == 200
    data = r.json()
    assert data["kernel_status"] == "ACTIVE"
    assert "invariants" in data
    assert data["invariants"]["decision_authority"] == "KX108_ONLY"
    assert data["invariants"]["emits_act"] is False
