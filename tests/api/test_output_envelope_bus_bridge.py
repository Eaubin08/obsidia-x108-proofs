"""
Test: OutputEnvelopeV1 on /bus/bridge
==========================================
Validates that /bus/bridge uses the standardized output envelope:
  - Default mode: boundary flags present, internal data preserved
  - Compact mode: light payload, internal fields omitted
  - Debug mode: full payload with boundary flags
  - /bus/stats still passes unchanged
"""
from __future__ import annotations
import os
import pytest

os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)

# F52 quarantine lifted by F54 after /bus/stats and /bus/bridge implementation.


@pytest.fixture(scope="module")
def default_response():
    resp = client.get("/bus/bridge")
    assert resp.status_code == 200, f"Default /bus/bridge failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def compact_response():
    resp = client.get("/bus/bridge?compact=true")
    assert resp.status_code == 200, f"Compact /bus/bridge failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def debug_response():
    resp = client.get("/bus/bridge?debug=true")
    assert resp.status_code == 200, f"Debug /bus/bridge failed: {resp.status_code}"
    return resp.json()


class TestBusBridgeBoundary:
    """Verify boundary invariants on /bus/bridge."""

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

    def test_source_and_route_present(self, default_response):
        assert default_response.get("source") == "OBSIDIA_API"
        assert default_response.get("route") == "/bus/bridge"

    def test_timestamp_present(self, default_response):
        assert default_response.get("timestamp"), "timestamp is empty"

    def test_compact_debug_flags_default(self, default_response):
        assert default_response.get("compact") is False
        assert default_response.get("debug") is False


class TestBusBridgeDefault:
    """Default mode: backward-compatible, internal data preserved."""

    def test_internal_data_preserved(self, default_response):
        assert "bridge_id" in default_response, "bridge_id should be present in default mode"
        assert "is_attached" in default_response, "is_attached should be present"


class TestBusBridgeCompact:
    """Compact mode: light payload, internal fields omitted."""

    def test_status_200(self, compact_response):
        assert compact_response is not None

    def test_boundary_flags_present(self, compact_response):
        assert compact_response.get("decision_authority") == "KX108_ONLY"
        assert compact_response.get("emits_act") is False

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
        assert len(omitted) > 0, "omitted_debug_fields should list omitted fields"

    def test_internal_fields_not_exposed_in_compact(self, compact_response):
        """In compact mode, internal bridge fields should NOT be top-level."""
        deep_fields = ["bridge_id", "is_attached", "stats"]
        for field in deep_fields:
            assert field not in compact_response, \
                f"Internal field '{field}' leaked in compact mode"


class TestBusBridgeDebug:
    """Debug mode: full payload with boundary flags."""

    def test_status_200(self, debug_response):
        assert debug_response is not None

    def test_boundary_flags_present(self, debug_response):
        assert debug_response.get("decision_authority") == "KX108_ONLY"
        assert debug_response.get("emits_act") is False

    def test_debug_flag(self, debug_response):
        assert debug_response.get("debug") is True

    def test_internal_data_preserved(self, debug_response):
        assert "bridge_id" in debug_response, "bridge_id should be present in debug mode"


class TestBusStatsStillOK:
    """Regression: /bus/stats must still pass after /bus/bridge patch."""

    def test_bus_stats_still_returns_200(self):
        resp = client.get("/bus/stats")
        assert resp.status_code == 200

    def test_bus_stats_has_boundary(self):
        resp = client.get("/bus/stats")
        data = resp.json()
        assert data.get("decision_authority") == "KX108_ONLY"
        assert data.get("emits_act") is False

    def test_bus_stats_compact_still_works(self):
        resp = client.get("/bus/stats?compact=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("compact") is True
        assert data.get("debug_payload_omitted") is True


class TestContentType:
    """Verify JSON content-type on /bus/bridge."""

    def test_content_type_is_json(self):
        resp = client.get("/bus/bridge")
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct, f"Expected JSON content-type, got: {ct}"

    def test_compact_content_type_is_json(self):
        resp = client.get("/bus/bridge?compact=true")
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct
