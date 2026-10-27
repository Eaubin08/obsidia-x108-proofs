"""
Test: OutputEnvelopeV1 on /api/blockchain/classifiers/fraud-check
=======================================================================
Validates that the fraud-check endpoint uses the standardized output envelope:
  - Default mode: boundary flags present, fraud-check results preserved
  - Compact mode: light payload, deep risk dicts omitted
  - Debug mode: full payload with all risk assessments
  - Bus endpoints still pass (regression)
"""
from __future__ import annotations
import os
import pytest

os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)

# Minimal valid payload for fraud-check
_MIN_PAYLOAD = {
    "action_id": "fraud-test-001",
    "chain_id": "ethereum",
    "action_class": "DEFI_SWAP",
    "defi_protocol": "uniswap",
    "defi_operation": "swap",
    "slippage_pct": 1.5,
    "protocol_audited": True,
    "is_mainnet": True,
}


@pytest.fixture(scope="module")
def default_response():
    resp = client.post("/api/blockchain/classifiers/fraud-check", json=_MIN_PAYLOAD)
    assert resp.status_code == 200, f"Default fraud-check failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def compact_response():
    body = {**_MIN_PAYLOAD, "compact": True}
    resp = client.post("/api/blockchain/classifiers/fraud-check", json=body)
    assert resp.status_code == 200, f"Compact fraud-check failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def debug_response():
    body = {**_MIN_PAYLOAD, "debug": True}
    resp = client.post("/api/blockchain/classifiers/fraud-check", json=body)
    assert resp.status_code == 200, f"Debug fraud-check failed: {resp.status_code}"
    return resp.json()


class TestFraudCheckBoundary:
    """Verify boundary invariants on fraud-check endpoint."""

    def test_status_200(self, default_response):
        assert default_response is not None

    def test_decision_authority_kx108(self, default_response):
        assert default_response.get("decision_authority") == "KX108_ONLY"

    def test_writes_are_false(self, default_response):
        assert default_response.get("emits_act") is False
        assert default_response.get("emits_verdict") is False
        assert default_response.get("memory_write") is False
        assert default_response.get("graphiti_write") is False
        assert default_response.get("neo4j_write") is False
        assert default_response.get("kernel_mutation") is False

    def test_readonly_is_true(self, default_response):
        assert default_response.get("readonly") is True

    def test_route_present(self, default_response):
        assert default_response.get("route") == "/api/blockchain/classifiers/fraud-check"

    def test_compact_debug_flags_default(self, default_response):
        assert default_response.get("compact") is False
        assert default_response.get("debug") is False


class TestFraudCheckDefault:
    """Default mode: fraud-check results preserved."""

    def test_action_id_present(self, default_response):
        assert default_response.get("action_id") == "fraud-test-001"

    def test_aggregate_gate_present(self, default_response):
        assert "aggregate_gate" in default_response

    def test_essential_results_present(self, default_response):
        for field in ["action_decision", "tx_simulation"]:
            assert field in default_response, f"Essential field '{field}' missing"

    def test_status_field(self, default_response):
        assert default_response.get("status") == "OK"


class TestFraudCheckCompact:
    """Compact mode: light payload, deep risk dicts omitted."""

    def test_status_200(self, compact_response):
        assert compact_response is not None

    def test_compact_flag(self, compact_response):
        assert compact_response.get("compact") is True

    def test_omission_markers(self, compact_response):
        assert compact_response.get("deep_snapshots_omitted") is True
        assert compact_response.get("deep_snapshots_available") is True
        assert compact_response.get("debug_payload_omitted") is True
        assert compact_response.get("debug_payload_available") is True

    def test_omitted_fields_listed(self, compact_response):
        omitted = compact_response.get("omitted_debug_fields", [])
        assert isinstance(omitted, list)
        assert len(omitted) > 0, "omitted_debug_fields should be non-empty"

    def test_deep_risk_dicts_omitted(self, compact_response):
        deep_fields = [
            "action_decision", "chain_context", "tx_simulation",
            "defi_risk", "contract_risk", "bridge_risk", "audit_packet",
        ]
        for field in deep_fields:
            assert field not in compact_response, \
                f"Deep field '{field}' leaked in compact mode"

    def test_boundary_still_present(self, compact_response):
        assert compact_response.get("decision_authority") == "KX108_ONLY"


class TestFraudCheckDebug:
    """Debug mode: full payload with risk assessments."""

    def test_status_200(self, debug_response):
        assert debug_response is not None

    def test_debug_flag(self, debug_response):
        assert debug_response.get("debug") is True

    def test_boundary_present(self, debug_response):
        assert debug_response.get("decision_authority") == "KX108_ONLY"

    def test_deep_data_preserved(self, debug_response):
        assert "action_decision" in debug_response
        assert "tx_simulation" in debug_response


class TestBusRegression:
    """Regression: bus endpoints still work after blockchain patch."""

    def test_bus_stats_ok(self):
        resp = client.get("/bus/stats")
        assert resp.status_code == 200

    def test_bus_bridge_ok(self):
        resp = client.get("/bus/bridge")
        assert resp.status_code == 200


class TestContentType:
    """Verify JSON content-type on fraud-check."""

    def test_content_type_is_json(self):
        resp = client.post("/api/blockchain/classifiers/fraud-check", json=_MIN_PAYLOAD)
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct
