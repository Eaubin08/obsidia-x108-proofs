"""
F36 tests — User Scenario: Brody Workbench Controlled Response.

Verifies:
- Scenario envelope fields present and correct
- Runtime entrypoint summary embedded (F33/F32, 7 surfaces)
- Workbench summary built from F32 packet surfaces
- Controlled response: can_decide=False, can_execute=False, text present
- No forbidden response tokens (ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT)
- Full boundary block at every layer
- No mutation flags anywhere
- Trading domain end-to-end
- Module-level BOUNDARY constant correct
"""
from __future__ import annotations

import re

import pytest

from periphery.brody_runtime.f36_user_scenario_controlled_response import (
    BOUNDARY,
    FORBIDDEN_RESPONSE_TOKENS,
    SCENARIO_ID,
    VERSION,
    PROOF_STATUS,
    build_user_scenario_controlled_response,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

BANK_INPUT = "Je veux analyser une transaction bancaire avant paiement."
BANK_PAYLOAD = {
    "balance": 10_000.0,
    "transactions": [{"amount": 100.0, "type": "debit", "recipient": "test-target"}],
}

TRADING_INPUT = "Inspecter les signaux du marché BTC avant intervention manuelle."
TRADING_PAYLOAD = {
    "symbol": "BTC/USDT",
    "prices": [100.0 + i for i in range(30)],
    "highs": [101.0 + i for i in range(30)],
    "lows": [99.0 + i for i in range(30)],
    "volumes": [1_000.0] * 30,
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

def test_f36_scenario_returns_envelope():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert result["scenario_id"] == SCENARIO_ID
    assert result["version"] == VERSION
    assert result["mode"] == "READONLY"
    assert result["user_input"] == BANK_INPUT
    assert result["domain"] == "bank"
    assert "scenario_at" in result
    assert result["proof_status"] == PROOF_STATUS


def test_f36_scenario_runtime_entrypoint_ready():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    ep = result["runtime_entrypoint"]
    assert ep["entrypoint_id"] == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    assert ep["integration_status"] == "READY_READONLY"
    assert ep["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert ep["surfaces_ready"] == 7
    assert ep["surfaces_missing"] == 0
    assert ep["surfaces_total"] == 7


def test_f36_scenario_workbench_summary():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    wb = result["workbench"]
    assert wb["surface_id"] == "F36_WORKBENCH_SUMMARY"
    assert wb["connector_status"] == "READY_READONLY"
    assert wb["surfaces_ready"] == 7
    assert wb["integration_status"] == "READY_READONLY"
    assert set(wb["surfaces_consulted"]) == EXPECTED_SURFACES
    assert wb["f35_c03_available"] is True


def test_f36_scenario_controlled_response_present():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    cr = result["controlled_response"]
    assert cr["response_kind"] == "contextual_explanation_only"
    assert cr["can_answer"] is True
    assert cr["can_decide"] is False
    assert cr["can_execute"] is False
    assert cr["can_emit_act"] is False
    assert isinstance(cr["text"], str)
    assert len(cr["text"]) > 50


def test_f36_scenario_no_forbidden_tokens_in_text():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    text_upper = result["controlled_response"]["text"].upper()
    for token in FORBIDDEN_RESPONSE_TOKENS:
        assert not re.search(r"\b" + re.escape(token) + r"\b", text_upper), (
            f"Forbidden token '{token}' found as standalone word in controlled_response.text"
        )


def test_f36_scenario_top_level_boundary():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert_boundary(result, "top-level")


def test_f36_scenario_workbench_boundary():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert_boundary(result["workbench"], "workbench")


def test_f36_scenario_controlled_response_boundary():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert_boundary(result["controlled_response"], "controlled_response")


def test_f36_scenario_no_mutation_flags():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    for layer_name, layer in [
        ("top", result),
        ("workbench", result["workbench"]),
        ("controlled_response", result["controlled_response"]),
    ]:
        for flag in ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write", "memory_write"):
            assert layer.get(flag) is False, f"[{layer_name}] {flag} must be False"


def test_f36_scenario_trading_domain():
    result = build_user_scenario_controlled_response(
        user_input=TRADING_INPUT,
        domain="trading",
        sigma_payload=TRADING_PAYLOAD,
    )
    assert result["mode"] == "READONLY"
    assert result["domain"] == "trading"
    assert result["runtime_entrypoint"]["integration_status"] == "READY_READONLY"
    assert result["workbench"]["connector_status"] == "READY_READONLY"
    assert result["controlled_response"]["can_decide"] is False
    assert_boundary(result, "trading")


def test_f36_scenario_text_contains_user_input():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert BANK_INPUT in result["controlled_response"]["text"]


def test_f36_scenario_text_contains_kx108_authority():
    result = build_user_scenario_controlled_response(
        user_input=BANK_INPUT,
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
    )
    assert "KX108_ONLY" in result["controlled_response"]["text"]


def test_f36_boundary_module_constant_correct():
    for flag in ("emits_act", "emits_verdict", "memory_write", "graphiti_write",
                 "neo4j_write", "kernel_mutation", "x108_mutation", "runtime_execute",
                 "can_decide", "can_emit_act", "allowed_to_decide"):
        assert BOUNDARY[flag] is False, f"BOUNDARY[{flag!r}] must be False"
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert BOUNDARY["readonly"] is True
    assert BOUNDARY["advisory_only"] is True
    assert BOUNDARY["context_signal_only"] is True


def test_f36_forbidden_tokens_list_complete():
    assert "ALLOW" in FORBIDDEN_RESPONSE_TOKENS
    assert "HOLD" in FORBIDDEN_RESPONSE_TOKENS
    assert "BLOCK" in FORBIDDEN_RESPONSE_TOKENS
    assert "ACT" in FORBIDDEN_RESPONSE_TOKENS
    assert "DECIDE" in FORBIDDEN_RESPONSE_TOKENS
    assert "VERDICT" in FORBIDDEN_RESPONSE_TOKENS
