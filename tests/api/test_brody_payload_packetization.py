"""
Test: Brody Payload Packetization — compact / debug / default modes
=====================================================================
Validates that /api/brody/chat responds correctly in all three modes:
  - default (no flags): backward-compatible, no debug markers
  - compact=true: light payload, deep snapshots omitted
  - debug=true: full payload with snapshots and debug markers
"""
from __future__ import annotations
import os
import pytest

os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)

MESSAGE = "explique X108 avec la memoire actuelle"

# ── Deep snapshot fields that should be absent in compact mode ──────────
_DEEP_SNAPSHOTS = {
    "brody_full_context",
    "memory_response_chain_snapshot",
    "temporal_context_snapshot",
    "runtime_context",
    "candidate_memory_snapshot",
    "operator_loop_snapshot",
    "tree_policy_snapshot",
    "cognitive_modules_snapshot",
    "true_voice_snapshot",
    "session_memory_snapshot",
    "true_response_structure_snapshot",
    "project_memory_snapshot",
}


@pytest.fixture(scope="module")
def default_response():
    resp = client.post("/api/brody/chat", json={
        "message": MESSAGE, "language": "fr", "session_id": "test_packet_default",
    })
    assert resp.status_code == 200, f"Default mode failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def compact_response():
    resp = client.post("/api/brody/chat", json={
        "message": MESSAGE, "language": "fr", "session_id": "test_packet_compact",
        "compact": True,
    })
    assert resp.status_code == 200, f"Compact mode failed: {resp.status_code}"
    return resp.json()


@pytest.fixture(scope="module")
def debug_response():
    resp = client.post("/api/brody/chat", json={
        "message": MESSAGE, "language": "fr", "session_id": "test_packet_debug",
        "debug": True,
    })
    assert resp.status_code == 200, f"Debug mode failed: {resp.status_code}"
    return resp.json()


class TestDefaultPayload:
    """Default mode: backward-compatible, no debug markers."""

    def test_status_200(self, default_response):
        assert default_response is not None

    def test_final_answer_present(self, default_response):
        fa = default_response.get("final_answer", "")
        assert fa and len(fa) > 20

    def test_topic_present(self, default_response):
        assert default_response.get("topic", "")

    def test_final_answer_source_present(self, default_response):
        assert default_response.get("final_answer_source", "")

    def test_decision_authority_kx108(self, default_response):
        assert default_response.get("decision_authority") == "KX108_ONLY"

    def test_writes_are_false(self, default_response):
        assert default_response.get("emits_act") is False
        assert default_response.get("memory_write") is False
        assert "graphiti_write" not in default_response
        assert "neo4j_write" not in default_response

    def test_no_debug_markers_in_default(self, default_response):
        for key in default_response:
            assert not key.startswith("debug_"), f"Debug marker leaked in default mode: {key}"

    def test_snapshots_present(self, default_response):
        """Default mode should have snapshots (backward compat)."""
        assert "brody_full_context" in default_response
        assert "authority_snapshot" in default_response


class TestCompactPayload:
    """Compact mode: light payload, deep snapshots omitted."""

    def test_status_200(self, compact_response):
        assert compact_response is not None

    def test_final_answer_present(self, compact_response):
        fa = compact_response.get("final_answer", "")
        assert fa and len(fa) > 20

    def test_topic_present(self, compact_response):
        assert compact_response.get("topic", "")

    def test_decision_authority_kx108(self, compact_response):
        assert compact_response.get("decision_authority") == "KX108_ONLY"

    def test_writes_are_false(self, compact_response):
        assert compact_response.get("emits_act") is False
        assert compact_response.get("memory_write") is False
        assert "graphiti_write" not in compact_response
        assert "neo4j_write" not in compact_response

    def test_compact_mode_flag(self, compact_response):
        assert compact_response.get("compact_mode") is True

    def test_debug_payload_omitted(self, compact_response):
        assert compact_response.get("deep_snapshots_omitted") is True

    def test_deep_snapshots_omitted(self, compact_response):
        for snap in _DEEP_SNAPSHOTS:
            assert snap not in compact_response, f"Deep snapshot leaked in compact mode: {snap}"

    def test_final_answer_not_truncated(self, compact_response):
        fa = compact_response.get("final_answer", "")
        assert len(fa) > 30, f"final_answer appears truncated: {len(fa)} chars"
        assert "KX108" in fa or "X108" in fa or "kernel" in fa.lower()

    def test_no_debug_markers_in_compact(self, compact_response):
        _EXEMPT = {"debug_payload_omitted", "debug_payload_available"}
        for key in compact_response:
            if key.startswith("debug_") and key not in _EXEMPT:
                raise AssertionError(f"Debug marker leaked in compact mode: {key}")


class TestDebugPayload:
    """Debug mode: full payload with snapshots and debug markers."""

    def test_status_200(self, debug_response):
        assert debug_response is not None

    def test_final_answer_present(self, debug_response):
        fa = debug_response.get("final_answer", "")
        assert fa and len(fa) > 20

    def test_decision_authority_kx108(self, debug_response):
        assert debug_response.get("decision_authority") == "KX108_ONLY"

    def test_writes_are_false(self, debug_response):
        assert debug_response.get("emits_act") is False
        assert debug_response.get("memory_write") is False
        assert "graphiti_write" not in debug_response
        assert "neo4j_write" not in debug_response

    def test_debug_markers_present(self, debug_response):
        markers = [k for k in debug_response if k.startswith("debug_")]
        assert len(markers) >= 2, f"Expected debug markers, found: {markers}"

    def test_deep_snapshots_present(self, debug_response):
        found = [s for s in _DEEP_SNAPSHOTS if s in debug_response]
        assert len(found) >= 2, f"Expected deep snapshots in debug mode, found: {found}"


class TestUTF8Clean:
    """UTF-8 cleanliness across all modes."""

    def test_compact_utf8_clean(self, compact_response):
        fa = compact_response.get("final_answer", "")
        assert "\u00c3" not in fa, "Mojibake in compact final_answer"
        assert "\u00e2" not in fa, "Mojibake in compact final_answer"

    def test_debug_utf8_clean(self, debug_response):
        fa = debug_response.get("final_answer", "")
        assert "\u00c3" not in fa, "Mojibake in debug final_answer"
        assert "\u00e2" not in fa, "Mojibake in debug final_answer"

    def test_default_utf8_clean(self, default_response):
        fa = default_response.get("final_answer", "")
        assert "\u00c3" not in fa, "Mojibake in default final_answer"
        assert "\u00e2" not in fa, "Mojibake in default final_answer"


class TestJSONContentType:
    """Verify JSON content-type header."""

    def test_content_type_is_json(self, default_response):
        # TestClient includes headers implicitly — check response object
        resp = client.post("/api/brody/chat", json={
            "message": MESSAGE, "language": "fr", "session_id": "test_ct",
        })
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct, f"Expected JSON content-type, got: {ct}"

    def test_compact_content_type_is_json(self):
        resp = client.post("/api/brody/chat", json={
            "message": MESSAGE, "language": "fr", "session_id": "test_ct_compact",
            "compact": True,
        })
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct, f"Expected JSON content-type, got: {ct}"
