"""
Test: OutputEnvelopeV1 on /api/periphery/pipeline/run
===========================================================
Validates that the pipeline endpoint uses the standardized output envelope:
  - Default mode: boundary flags present, pipeline results preserved
  - Compact mode: light payload, deep fields omitted
  - Debug mode: full payload with boundary flags
  - All other suites still pass (regression)
"""
from __future__ import annotations
import os
import pytest

os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)

_MIN_PAYLOAD = {
    "action_id": "pipeline-test-001",
    "domain": "test",
    "intent": "inspect",
    "action_type": "query",
}


@pytest.fixture(scope="module")
def default_response():
    resp = client.post("/api/periphery/pipeline/run", json=_MIN_PAYLOAD)
    assert resp.status_code == 200, f"Default pipeline failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def compact_response():
    resp = client.post("/api/periphery/pipeline/run?compact=true", json=_MIN_PAYLOAD)
    assert resp.status_code == 200, f"Compact pipeline failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def debug_response():
    resp = client.post("/api/periphery/pipeline/run?debug=true", json=_MIN_PAYLOAD)
    assert resp.status_code == 200, f"Debug pipeline failed: {resp.status_code}"
    return resp.json()


class TestPipelineBoundary:
    """Verify boundary invariants on pipeline endpoint."""

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
        assert default_response.get("route") == "/api/periphery/pipeline/run"

    def test_compact_debug_flags_default(self, default_response):
        assert default_response.get("compact") is False
        assert default_response.get("debug") is False


class TestPipelineDefault:
    """Default mode: pipeline results preserved."""

    def test_status_field(self, default_response):
        assert default_response.get("status") == "OK"


class TestPipelineCompact:
    """Compact mode: light payload, internal fields omitted."""

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

    def test_boundary_still_present(self, compact_response):
        assert compact_response.get("decision_authority") == "KX108_ONLY"


class TestPipelineDebug:
    """Debug mode: full payload with boundary flags."""

    def test_status_200(self, debug_response):
        assert debug_response is not None

    def test_debug_flag(self, debug_response):
        assert debug_response.get("debug") is True

    def test_boundary_present(self, debug_response):
        assert debug_response.get("decision_authority") == "KX108_ONLY"


class TestRegression:
    """Regression: all other suites still pass."""

    def test_fraud_check_ok(self):
        resp = client.post("/api/blockchain/classifiers/fraud-check", json={
            "action_id": "reg-test", "chain_id": "eth", "action_class": "DEFI_SWAP",
        })
        assert resp.status_code == 200

    def test_bus_stats_ok(self):
        resp = client.get("/bus/stats")
        assert resp.status_code == 200

    def test_bus_bridge_ok(self):
        resp = client.get("/bus/bridge")
        assert resp.status_code == 200

    def test_brody_chat_ok(self):
        resp = client.post("/api/brody/chat", json={
            "message": "explique X108", "language": "fr", "session_id": "reg-test",
        })
        assert resp.status_code == 200


class TestContentType:
    """Verify JSON content-type on pipeline."""

    def test_content_type_is_json(self):
        resp = client.post("/api/periphery/pipeline/run", json=_MIN_PAYLOAD)
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct
