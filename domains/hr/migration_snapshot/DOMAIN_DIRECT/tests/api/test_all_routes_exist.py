"""V5B API Test: New routes exist and return correct structure."""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


@pytest.mark.parametrize("path", [
    "/api/graphiti/status",
    "/api/graphiti/context",
    "/api/graphiti/search",
    "/api/graphiti/metrics",
    "/api/graphiti/readiness",
    "/api/memory/status",
    "/api/memory/sources",
    "/api/memory/candidates",
    "/api/memory/candidate-ledger",
    "/api/memory/promotion-policy",
    "/api/x108/status",
    "/api/os3/tickets",
    "/api/worldcalls",
    "/api/worldcalls/gateway-status",
    "/api/blockchain/status",
    "/api/audit/events",
])
def test_route_exists_and_returns_200(path):
    r = client.get(path)
    assert r.status_code == 200, f"Route {path} returned {r.status_code}"


def test_all_routes_have_decision_authority():
    routes = [
        "/api/graphiti/status",
        "/api/memory/status",
        "/api/x108/status",
        "/api/os3/tickets",
        "/api/worldcalls/gateway-status",
        "/api/blockchain/status",
        "/api/audit/events",
    ]
    for path in routes:
        r = client.get(path)
        data = r.json()
        assert "decision_authority" in data or "readonly" in data, f"{path} missing sovereignty fields"


def test_no_route_returns_frontend_mock():
    routes = ["/api/graphiti/status", "/api/memory/status", "/api/x108/status",
              "/api/os3/tickets", "/api/worldcalls", "/api/blockchain/status",
              "/api/audit/events"]
    for path in routes:
        r = client.get(path)
        data = r.json()
        if "source" in data:
            assert data["source"] != "FRONTEND_MOCK", f"{path} source is FRONTEND_MOCK"
