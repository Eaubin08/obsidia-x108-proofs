"""
F34 tests — Live Route Smoke: API Contract Proof Readonly.

Exercises POST /api/periphery/brody-runtime/f33/integration-packet via TestClient.
Verifies the full HTTP API contract:
  - HTTP 200
  - entrypoint_id = F33_BRODY_RUNTIME_ENTRYPOINT_READONLY
  - f32_packet embedded with 7 surfaces READY_READONLY
  - Full boundary block at top level and inside f32_packet
  - decision_authority = KX108_ONLY at every layer
  - No forbidden mutation tokens (emits_act, kernel_mutation, etc. all False)
  - Graceful behavior with unsupported domain
  - Trading domain end-to-end
  - Route registered in main app (OpenAPI schema)
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

ROUTE = "/api/periphery/brody-runtime/f33/integration-packet"

BANK_PAYLOAD = {
    "domain": "bank",
    "sigma_payload": {
        "request_type": "STRUCTURAL_PREPARATION",
        "amount": 100,
        "recipient": "readonly-smoke-target",
    },
    "title": "F34 live route smoke",
    "session_id": "f34-live-route-smoke",
    "signal_id": "f34-tree-signal",
    "theta": 0.15,
    "request_type": "STRUCTURAL_PREPARATION",
}

TRADING_PAYLOAD = {
    "domain": "trading",
    "sigma_payload": {
        "symbol": "BTC/USDT",
        "prices": [100.0 + i for i in range(30)],
        "highs": [101.0 + i for i in range(30)],
        "lows": [99.0 + i for i in range(30)],
        "volumes": [1_000.0] * 30,
    },
    "title": "F34 trading smoke",
    "session_id": "f34-trading-smoke",
    "request_type": "STRUCTURAL_PREPARATION",
}

EXPECTED_SURFACES = {
    "sigma_dispatcher",
    "tree_signal_packet",
    "monitoring_adapters",
    "operator_view_packet",
    "brody_runtime_context",
    "workflow_governance_readonly",
    "neo4j_guide_bridge",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def assert_boundary_block(data: dict, label: str = "") -> None:
    prefix = f"[{label}] " if label else ""
    assert data.get("decision_authority") == "KX108_ONLY", f"{prefix}decision_authority"
    assert data.get("allowed_to_decide") is False, f"{prefix}allowed_to_decide"
    assert data.get("readonly") is True, f"{prefix}readonly"
    assert data.get("advisory_only") is True, f"{prefix}advisory_only"
    assert data.get("context_signal_only") is True, f"{prefix}context_signal_only"
    assert data.get("can_decide") is False, f"{prefix}can_decide"
    assert data.get("can_emit_act") is False, f"{prefix}can_emit_act"
    assert data.get("emits_act") is False, f"{prefix}emits_act"
    assert data.get("emits_verdict") is False, f"{prefix}emits_verdict"
    assert data.get("memory_write") is False, f"{prefix}memory_write"
    assert data.get("graphiti_write") is False, f"{prefix}graphiti_write"
    assert data.get("neo4j_write") is False, f"{prefix}neo4j_write"
    assert data.get("kernel_mutation") is False, f"{prefix}kernel_mutation"
    assert data.get("x108_mutation") is False, f"{prefix}x108_mutation"
    assert data.get("runtime_execute") is False, f"{prefix}runtime_execute"


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_f34_route_returns_200():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    assert r.status_code == 200, f"Expected 200 got {r.status_code}: {r.text[:200]}"


def test_f34_route_returns_json():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    assert isinstance(data, dict)


def test_f34_route_entrypoint_envelope():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    assert data["entrypoint_id"] == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    assert data["version"] == "F33_V1"
    assert "called_at" in data
    assert data["proof_status"] == "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN"


def test_f34_route_entrypoint_status_ready():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    assert data["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert data["integration_status"] == "READY_READONLY"
    assert data["surfaces_ready"] == 7
    assert data["surfaces_missing"] == 0
    assert data["surfaces_total"] == 7


def test_f34_route_f32_packet_embedded():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    f32 = data.get("f32_packet", {})
    assert isinstance(f32, dict) and f32, "f32_packet missing or empty"
    assert f32["packet_id"] == "F32_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET"
    assert f32["version"] == "F32_V1"
    assert f32["integration_status"] == "READY_READONLY"


def test_f34_route_seven_surfaces_present_and_ready():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    surfaces = data["f32_packet"]["surfaces"]
    assert set(surfaces.keys()) == EXPECTED_SURFACES, (
        f"missing: {EXPECTED_SURFACES - set(surfaces.keys())}"
    )
    not_ready = {k: v["status"] for k, v in surfaces.items() if v.get("status") != "READY"}
    assert not_ready == {}, f"surfaces not READY: {not_ready}"


def test_f34_route_top_level_boundary():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    assert_boundary_block(data, "top-level")


def test_f34_route_f32_packet_boundary():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    assert_boundary_block(data["f32_packet"], "f32_packet")


def test_f34_route_every_surface_kx108():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    surfaces = r.json()["f32_packet"]["surfaces"]
    for name, surface in surfaces.items():
        assert surface.get("decision_authority") == "KX108_ONLY", (
            f"surface '{name}' missing KX108_ONLY"
        )


def test_f34_route_no_mutation_flags_anywhere():
    r = client.post(ROUTE, json=BANK_PAYLOAD)
    data = r.json()
    for flag in ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write", "memory_write"):
        assert data.get(flag) is False, f"top-level {flag} must be False"
        assert data["f32_packet"].get(flag) is False, f"f32_packet {flag} must be False"
        for name, surface in data["f32_packet"]["surfaces"].items():
            val = surface.get(flag)
            assert val is not True, f"surface '{name}': {flag}={val!r} must not be True"


def test_f34_route_trading_domain():
    r = client.post(ROUTE, json=TRADING_PAYLOAD)
    assert r.status_code == 200
    data = r.json()
    assert data["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert data["f32_packet"]["surfaces"]["sigma_dispatcher"]["domain"] == "trading"
    assert_boundary_block(data, "trading")


def test_f34_route_unsupported_domain():
    r = client.post(ROUTE, json={"domain": "unknown_xyz", "sigma_payload": {}})
    assert r.status_code == 200
    data = r.json()
    sigma = data["f32_packet"]["surfaces"]["sigma_dispatcher"]
    assert sigma["status"] == "READY"
    assert sigma["result"]["status"] == "UNSUPPORTED_DOMAIN"
    assert data["surfaces_total"] == 7
    assert_boundary_block(data, "unsupported-domain")


def test_f34_route_registered_in_openapi():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert ROUTE in paths, f"Route {ROUTE} not found in OpenAPI schema"


def test_f34_route_default_payload():
    r = client.post(ROUTE, json={})
    assert r.status_code == 200
    data = r.json()
    assert data["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert data["surfaces_ready"] == 7
