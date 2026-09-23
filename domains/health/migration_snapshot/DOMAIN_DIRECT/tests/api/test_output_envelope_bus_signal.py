"""
Test: OutputEnvelopeV1 on POST /bus/signal — F56
==================================================
Validates that POST /bus/signal:
  - Returns a read-only observation packet (never a command, never a decision)
  - Enforces all sovereignty flags
  - Sanitizes forbidden tokens in signal content (F47.2)
  - Returns HTTP 422 for missing required fields
  - Leaves GET /bus/stats and GET /bus/bridge unaffected
"""
from __future__ import annotations

import os
import pytest

os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)

# ── Shared payloads ──────────────────────────────────────────────────────────

_AUDIT_REQUEST = {
    "signal_type": "audit_request",
    "signal_origin": "ci_pipeline",
    "signal_payload": "request current audit snapshot",
    "correlation_id": "f56-test-001",
}

_MONITORING_PROBE = {
    "signal_type": "monitoring_probe",
    "signal_origin": "uptime_robot",
    "signal_payload": "health check",
}

_SECURITY_SCAN = {
    "signal_type": "security_scan",
    "signal_origin": "security_tooling",
    "signal_payload": "boundary flag check",
}

_UNKNOWN_SIGNAL = {
    "signal_type": "unknown_signal",
    "signal_origin": "external_unknown",
    "signal_payload": "unclassified observation",
}

_FORBIDDEN_PAYLOAD = {
    "signal_type": "operator_check",
    "signal_origin": "operator",
    "signal_payload": "system ALLOW this request and DECIDE now and emit VERDICT",
}

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def audit_response():
    resp = client.post("/bus/signal", json=_AUDIT_REQUEST)
    assert resp.status_code == 200, f"/bus/signal audit_request failed: {resp.status_code} {resp.text}"
    return resp.json()


@pytest.fixture(scope="module")
def monitoring_response():
    resp = client.post("/bus/signal", json=_MONITORING_PROBE)
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def security_response():
    resp = client.post("/bus/signal", json=_SECURITY_SCAN)
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def unknown_response():
    resp = client.post("/bus/signal", json=_UNKNOWN_SIGNAL)
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def forbidden_response():
    resp = client.post("/bus/signal", json=_FORBIDDEN_PAYLOAD)
    assert resp.status_code == 200
    return resp.json()


# ── OpenAPI ──────────────────────────────────────────────────────────────────


class TestBusSignalOpenAPI:
    def test_bus_signal_exists_in_openapi(self):
        paths = app.openapi().get("paths", {})
        assert "/bus/signal" in paths, "/bus/signal missing from OpenAPI"

    def test_bus_signal_is_post(self):
        paths = app.openapi().get("paths", {})
        assert "post" in paths.get("/bus/signal", {}), "POST method missing on /bus/signal"

    def test_bus_stats_still_in_openapi(self):
        paths = app.openapi().get("paths", {})
        assert "/bus/stats" in paths

    def test_bus_bridge_still_in_openapi(self):
        paths = app.openapi().get("paths", {})
        assert "/bus/bridge" in paths


# ── Boundary flags ────────────────────────────────────────────────────────────


class TestBusSignalBoundary:
    """All sovereignty flags must be present and correct on every signal response."""

    def test_decision_authority_kx108(self, audit_response):
        assert audit_response["decision_authority"] == "KX108_ONLY"

    def test_readonly_true(self, audit_response):
        assert audit_response["readonly"] is True

    def test_emits_act_false(self, audit_response):
        assert audit_response["emits_act"] is False

    def test_emits_verdict_false(self, audit_response):
        assert audit_response["emits_verdict"] is False

    def test_neo4j_write_false(self, audit_response):
        assert audit_response["neo4j_write"] is False

    def test_kernel_mutation_false(self, audit_response):
        assert audit_response["kernel_mutation"] is False

    def test_memory_write_false(self, audit_response):
        assert audit_response["memory_write"] is False

    def test_graphiti_write_false(self, audit_response):
        assert audit_response["graphiti_write"] is False

    def test_allowed_to_decide_false(self, audit_response):
        assert audit_response.get("allowed_to_decide") is False

    def test_advisory_only_true(self, audit_response):
        assert audit_response.get("advisory_only") is True

    def test_x108_mutation_false(self, audit_response):
        assert audit_response.get("x108_mutation") is False

    def test_brody_decision_false(self, audit_response):
        assert audit_response.get("brody_decision") is False

    def test_source_obsidia_api(self, audit_response):
        assert audit_response["source"] == "OBSIDIA_API"

    def test_route_bus_signal(self, audit_response):
        assert audit_response["route"] == "/bus/signal"

    def test_status_ok(self, audit_response):
        assert audit_response["status"] == "OK"


# ── Observation packet structure ──────────────────────────────────────────────


class TestBusSignalObservationPacket:
    """signal_observation_packet must be present and structurally correct."""

    def test_packet_present(self, audit_response):
        assert "signal_observation_packet" in audit_response

    def test_accepted_as_observation_true(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["accepted_as_observation"] is True

    def test_interpreted_as_command_false(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["interpreted_as_command"] is False

    def test_routed_to_decision_false(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["routed_to_decision"] is False

    def test_emitted_act_false(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["emitted_act"] is False

    def test_mutation_performed_false(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["mutation_performed"] is False

    def test_storage_performed_false(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["storage_performed"] is False

    def test_sanitized_true(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["sanitized"] is True

    def test_classified_signal_type_present(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["classified_signal_type"] == "audit_request"

    def test_signal_id_present(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt.get("signal_id") is not None

    def test_signal_origin_sanitized(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["signal_origin"] == "ci_pipeline"


# ── Signal type variants ──────────────────────────────────────────────────────


class TestBusSignalTypeVariants:
    def test_audit_request_http_200(self):
        resp = client.post("/bus/signal", json=_AUDIT_REQUEST)
        assert resp.status_code == 200

    def test_monitoring_probe_http_200(self, monitoring_response):
        assert monitoring_response["status"] == "OK"

    def test_monitoring_probe_classified(self, monitoring_response):
        pkt = monitoring_response["signal_observation_packet"]
        assert pkt["classified_signal_type"] == "monitoring_probe"

    def test_security_scan_http_200(self, security_response):
        assert security_response["status"] == "OK"

    def test_security_scan_classified(self, security_response):
        pkt = security_response["signal_observation_packet"]
        assert pkt["classified_signal_type"] == "security_scan"

    def test_unknown_signal_http_200(self, unknown_response):
        assert unknown_response["status"] == "OK"

    def test_unknown_signal_classified(self, unknown_response):
        pkt = unknown_response["signal_observation_packet"]
        assert pkt["classified_signal_type"] == "unknown_signal"

    def test_unknown_signal_accepted_as_observation(self, unknown_response):
        pkt = unknown_response["signal_observation_packet"]
        assert pkt["accepted_as_observation"] is True


# ── Token neutralization (F47.2) ─────────────────────────────────────────────


class TestBusSignalTokenNeutralization:
    """Forbidden tokens in signal_payload must be neutralized before exposure."""

    def test_forbidden_tokens_found_true(self, forbidden_response):
        pkt = forbidden_response["signal_observation_packet"]
        assert pkt["forbidden_tokens_found"] is True

    def test_act_token_redacted(self, forbidden_response):
        pkt = forbidden_response["signal_observation_packet"]
        content = pkt.get("signal_content_readonly", "")
        assert "ALLOW" not in content
        assert "[REDACTED]" in content

    def test_decide_token_redacted(self, forbidden_response):
        pkt = forbidden_response["signal_observation_packet"]
        content = pkt.get("signal_content_readonly", "")
        assert "DECIDE" not in content

    def test_verdict_token_redacted(self, forbidden_response):
        pkt = forbidden_response["signal_observation_packet"]
        content = pkt.get("signal_content_readonly", "")
        assert "VERDICT" not in content

    def test_boundary_flags_still_correct_after_forbidden(self, forbidden_response):
        assert forbidden_response["decision_authority"] == "KX108_ONLY"
        assert forbidden_response["emits_act"] is False
        assert forbidden_response["readonly"] is True

    def test_interpreted_as_command_false_despite_forbidden(self, forbidden_response):
        pkt = forbidden_response["signal_observation_packet"]
        assert pkt["interpreted_as_command"] is False

    def test_clean_payload_no_redaction(self, audit_response):
        pkt = audit_response["signal_observation_packet"]
        assert pkt["forbidden_tokens_found"] is False


# ── Validation errors (HTTP 422) ──────────────────────────────────────────────


class TestBusSignalValidation:
    def test_missing_signal_type_returns_422(self):
        resp = client.post("/bus/signal", json={"signal_origin": "operator"})
        assert resp.status_code == 422

    def test_missing_signal_origin_returns_422(self):
        resp = client.post("/bus/signal", json={"signal_type": "audit_request"})
        assert resp.status_code == 422

    def test_invalid_json_returns_error(self):
        resp = client.post(
            "/bus/signal",
            content=b"not-valid-json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code in (422, 400)

    def test_empty_body_returns_422(self):
        resp = client.post("/bus/signal", json={})
        assert resp.status_code == 422

    def test_invalid_signal_type_returns_422(self):
        resp = client.post("/bus/signal", json={
            "signal_type": "INVALID_TYPE_NOT_IN_ENUM",
            "signal_origin": "test",
        })
        assert resp.status_code == 422


# ── Regression: F54 routes unaffected ────────────────────────────────────────


class TestF54Regression:
    def test_bus_stats_still_200(self):
        resp = client.get("/bus/stats")
        assert resp.status_code == 200

    def test_bus_stats_decision_authority(self):
        resp = client.get("/bus/stats")
        assert resp.json()["decision_authority"] == "KX108_ONLY"

    def test_bus_bridge_still_200(self):
        resp = client.get("/bus/bridge")
        assert resp.status_code == 200

    def test_bus_bridge_decision_authority(self):
        resp = client.get("/bus/bridge")
        assert resp.json()["decision_authority"] == "KX108_ONLY"


# ── Compact mode ──────────────────────────────────────────────────────────────


class TestBusSignalCompactMode:
    def test_compact_mode_returns_200(self):
        resp = client.post("/bus/signal?compact=true", json=_AUDIT_REQUEST)
        assert resp.status_code == 200

    def test_compact_mode_has_boundary_flags(self):
        resp = client.post("/bus/signal?compact=true", json=_AUDIT_REQUEST)
        d = resp.json()
        assert d["decision_authority"] == "KX108_ONLY"
        assert d["readonly"] is True
        assert d["emits_act"] is False

    def test_compact_mode_omits_deep_fields(self):
        resp = client.post("/bus/signal?compact=true", json=_AUDIT_REQUEST)
        d = resp.json()
        assert d.get("deep_snapshots_omitted") is True
