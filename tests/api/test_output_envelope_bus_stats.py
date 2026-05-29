"""
Test: OutputEnvelopeV1 on /bus/stats
========================================
Validates that /bus/stats uses the standardized output envelope:
  - Default mode: boundary flags present, internal data preserved
  - Compact mode: light payload, deep fields omitted
  - Debug mode: full payload with boundary flags
  - /bus/bridge unchanged (not wrapped in envelope)
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
    resp = client.get("/bus/stats")
    assert resp.status_code == 200, f"Default /bus/stats failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def compact_response():
    resp = client.get("/bus/stats?compact=true")
    assert resp.status_code == 200, f"Compact /bus/stats failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def debug_response():
    resp = client.get("/bus/stats?debug=true")
    assert resp.status_code == 200, f"Debug /bus/stats failed: {resp.status_code}"
    return resp.json()


class TestBusStatsBoundary:
    """Verify boundary invariants on /bus/stats."""

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
        assert default_response.get("route") == "/bus/stats"

    def test_timestamp_present(self, default_response):
        assert default_response.get("timestamp"), "timestamp is empty"

    def test_compact_debug_flags_default(self, default_response):
        assert default_response.get("compact") is False
        assert default_response.get("debug") is False


class TestBusStatsDefault:
    """Default mode: backward-compatible, internal data preserved."""

    def test_internal_data_preserved(self, default_response):
        # In default mode, internal fields from the broker are still present
        # (merged into the envelope)
        assert "emitted" in default_response or "dropped" in default_response or "queue_size" in default_response, \
            "Internal bus stats should be preserved in default mode"

    def test_status_field(self, default_response):
        assert default_response.get("status") == "OK"


class TestBusStatsCompact:
    """Compact mode: light payload, deep fields omitted."""

    def test_status_200(self, compact_response):
        assert compact_response is not None

    def test_boundary_flags_present(self, compact_response):
        assert compact_response.get("decision_authority") == "KX108_ONLY"
        assert compact_response.get("emits_act") is False

    def test_compact_flag(self, compact_response):
        assert compact_response.get("compact") is True

    def test_deep_snapshots_omitted(self, compact_response):
        assert compact_response.get("deep_snapshots_omitted") is True
        assert compact_response.get("deep_snapshots_available") is True
        assert compact_response.get("debug_payload_omitted") is True
        assert compact_response.get("debug_payload_available") is True

    def test_omitted_fields_listed(self, compact_response):
        omitted = compact_response.get("omitted_debug_fields", [])
        assert isinstance(omitted, list)
        assert len(omitted) > 0, "omitted_debug_fields should list omitted fields"

    def test_internal_fields_not_exposed_in_compact(self, compact_response):
        """In compact mode, internal broker fields should NOT be top-level."""
        deep_fields = [
            "brody_context", "sigma_counters", "bridge_snapshot",
            "bridge_registration",
        ]
        for field in deep_fields:
            assert field not in compact_response, \
                f"Deep field '{field}' leaked in compact mode"

    def test_status_field(self, compact_response):
        assert compact_response.get("status") == "OK"


class TestBusStatsDebug:
    """Debug mode: full payload with boundary flags."""

    def test_status_200(self, debug_response):
        assert debug_response is not None

    def test_boundary_flags_present(self, debug_response):
        assert debug_response.get("decision_authority") == "KX108_ONLY"
        assert debug_response.get("emits_act") is False

    def test_debug_flag(self, debug_response):
        assert debug_response.get("debug") is True

    def test_internal_data_preserved(self, debug_response):
        # In debug mode, internal broker fields should be present
        assert "bridge_registration" in debug_response or "brody_context" in debug_response


class TestBusBridgeNowEnveloped:
    """Verify /bus/bridge IS now wrapped in the envelope (Phase 2 applied)."""

    def test_bus_bridge_is_wrapped(self):
        resp = client.get("/bus/bridge")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("decision_authority") == "KX108_ONLY", \
            "/bus/bridge should be wrapped in envelope"
        assert data.get("route") == "/bus/bridge", \
            "/bus/bridge should have route field"
        assert data.get("emits_act") is False


class TestContentType:
    """Verify JSON content-type on /bus/stats."""

    def test_content_type_is_json(self):
        resp = client.get("/bus/stats")
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct, f"Expected JSON content-type, got: {ct}"

    def test_compact_content_type_is_json(self):
        resp = client.get("/bus/stats?compact=true")
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct
