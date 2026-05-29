"""
F38 tests — Multi-Domain Live API Route Readonly.

Verifies:
- Route POST /api/periphery/brody-runtime/f38/multi-domain-scenarios registered
- HTTP 200 with correct Content-Type
- packet_id = F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY
- scenario_count = 4, scenarios_run = 4
- All 4 domains present (bank, gps_defense_aviation, trading, unknown_refusal)
- Known domains: status READY_READONLY, surfaces_ready=7
- unknown_refusal: status REFUSAL_READONLY
- global_status = READY_READONLY
- No forbidden tokens in any controlled_response text
- Full boundary at global and per-scenario level
- No mutation flags anywhere
- Route registered in OpenAPI schema
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from apps.obsidia_api.main import app

ROUTE = "/api/periphery/brody-runtime/f38/multi-domain-scenarios"
EXPECTED_DOMAINS = {"bank", "gps_defense_aviation", "trading", "unknown_refusal"}
KNOWN_DOMAINS = {"bank", "gps_defense_aviation", "trading"}
FORBIDDEN_RESPONSE_TOKENS = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")
MUTATION_FLAGS = ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write",
                  "memory_write", "graphiti_write", "runtime_execute")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def response(client):
    return client.post(ROUTE, json={})


@pytest.fixture(scope="module")
def body(response):
    return response.json()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_scenario(body: dict, domain: str) -> dict:
    for s in body.get("scenarios", []):
        if s.get("domain") == domain:
            return s
    pytest.fail(f"Domain '{domain}' not found in scenarios")


def _has_forbidden_token(text: str) -> bool:
    text_upper = text.upper()
    return any(
        re.search(r"\b" + re.escape(t) + r"\b", text_upper)
        for t in FORBIDDEN_RESPONSE_TOKENS
    )


def assert_boundary(data: dict, label: str = "") -> None:
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

def test_f38_route_http_200(response):
    assert response.status_code == 200


def test_f38_route_content_type_json(response):
    assert "application/json" in response.headers.get("content-type", "")


def test_f38_route_registered_in_openapi(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "f38/multi-domain-scenarios" in r.text


def test_f38_packet_id_correct(body):
    assert body.get("packet_id") == "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY"


def test_f38_version_correct(body):
    assert body.get("version") == "F37_V1"


def test_f38_mode_readonly(body):
    assert body.get("mode") == "READONLY"


def test_f38_scenario_count_4(body):
    assert body.get("scenario_count") == 4
    assert body.get("scenarios_run") == 4


def test_f38_all_domains_present(body):
    domains = {s.get("domain") for s in body.get("scenarios", [])}
    assert domains == EXPECTED_DOMAINS


def test_f38_bank_ready(body):
    s = _get_scenario(body, "bank")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f38_gps_ready(body):
    s = _get_scenario(body, "gps_defense_aviation")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f38_trading_ready(body):
    s = _get_scenario(body, "trading")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f38_unknown_refusal_ready(body):
    s = _get_scenario(body, "unknown_refusal")
    assert s["status"] == "REFUSAL_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    cr = s.get("controlled_response", {})
    assert cr.get("response_kind") == "refusal_out_of_scope"


def test_f38_global_status_ready(body):
    assert body.get("global_status") == "READY_READONLY"


def test_f38_no_forbidden_tokens_in_any_text(body):
    for s in body.get("scenarios", []):
        cr = s.get("controlled_response", {})
        text = cr.get("text", "")
        assert not _has_forbidden_token(text), (
            f"Forbidden token in domain '{s.get('domain')}' text"
        )


def test_f38_forbidden_tokens_found_false(body):
    assert body.get("forbidden_tokens_found") is False


def test_f38_all_mutations_false(body):
    assert body.get("all_mutations_false") is True


def test_f38_global_boundary(body):
    assert_boundary(body, "global")


def test_f38_per_scenario_boundary(body):
    for s in body.get("scenarios", []):
        assert_boundary(s, s.get("domain", "?"))


def test_f38_no_mutation_flags_global(body):
    for flag in MUTATION_FLAGS:
        assert body.get(flag) is False, f"global {flag} must be False"


def test_f38_no_mutation_flags_per_scenario(body):
    for s in body.get("scenarios", []):
        dom = s.get("domain", "?")
        for flag in MUTATION_FLAGS:
            assert s.get(flag) is False, f"[{dom}] {flag} must be False"
