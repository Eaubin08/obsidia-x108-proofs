"""
F37 tests — Multi-Domain User Scenarios Readonly.

Verifies:
- Global packet envelope (packet_id, version, mode, scenario_count)
- All 4 domains present (bank, gps_defense_aviation, trading, unknown_refusal)
- Each domain: controlled_response_present=True, can_decide=False, can_execute=False
- No forbidden tokens in any controlled_response.text (word-boundary check)
- Boundary enforced at global and per-scenario level
- No mutation flags anywhere
- unknown_refusal domain: status=REFUSAL_READONLY, refusal text present
- Module-level BOUNDARY constant correct
- FORBIDDEN_RESPONSE_TOKENS list complete
"""
from __future__ import annotations

import re

import pytest

from periphery.brody_runtime.f37_multi_domain_user_scenarios_readonly import (
    BOUNDARY,
    FORBIDDEN_RESPONSE_TOKENS,
    PACKET_ID,
    VERSION,
    PROOF_STATUS,
    build_multi_domain_user_scenarios,
)

EXPECTED_DOMAINS = {"bank", "gps_defense_aviation", "trading", "unknown_refusal"}
MUTATION_FLAGS = ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write",
                  "memory_write", "graphiti_write", "runtime_execute")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_scenario(result: dict, domain: str) -> dict:
    for s in result["scenarios"]:
        if s["domain"] == domain:
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

def test_f37_returns_global_envelope():
    result = build_multi_domain_user_scenarios()
    assert result["packet_id"] == PACKET_ID
    assert result["version"] == VERSION
    assert result["mode"] == "READONLY"
    assert result["proof_status"] == PROOF_STATUS
    assert result["scenario_count"] == 4
    assert result["scenarios_run"] == 4
    assert "built_at" in result


def test_f37_all_four_domains_present():
    result = build_multi_domain_user_scenarios()
    domains = {s["domain"] for s in result["scenarios"]}
    assert domains == EXPECTED_DOMAINS


def test_f37_bank_scenario_ready():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "bank")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f37_gps_scenario_ready():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "gps_defense_aviation")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f37_trading_scenario_ready():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "trading")
    assert s["status"] == "READY_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    assert s["surfaces_ready"] == 7


def test_f37_unknown_refusal_scenario():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "unknown_refusal")
    assert s["status"] == "REFUSAL_READONLY"
    assert s["controlled_response_present"] is True
    assert s["can_decide"] is False
    assert s["can_execute"] is False
    cr = s.get("controlled_response", {})
    assert cr.get("response_kind") == "refusal_out_of_scope"
    assert isinstance(cr.get("text"), str) and len(cr["text"]) > 50


def test_f37_no_forbidden_tokens_in_any_text():
    result = build_multi_domain_user_scenarios()
    for s in result["scenarios"]:
        cr = s.get("controlled_response", {})
        text = cr.get("text", "")
        assert not _has_forbidden_token(text), (
            f"Forbidden token found in domain '{s['domain']}' text"
        )
        assert s.get("forbidden_tokens_found") is False


def test_f37_global_forbidden_tokens_false():
    result = build_multi_domain_user_scenarios()
    assert result["forbidden_tokens_found"] is False


def test_f37_global_all_mutations_false():
    result = build_multi_domain_user_scenarios()
    assert result["all_mutations_false"] is True


def test_f37_global_boundary():
    result = build_multi_domain_user_scenarios()
    assert_boundary(result, "global")


def test_f37_per_scenario_boundary():
    result = build_multi_domain_user_scenarios()
    for s in result["scenarios"]:
        assert_boundary(s, s["domain"])


def test_f37_per_scenario_controlled_response_boundary():
    result = build_multi_domain_user_scenarios()
    for s in result["scenarios"]:
        cr = s.get("controlled_response", {})
        assert_boundary(cr, f"{s['domain']}.controlled_response")


def test_f37_no_mutation_flags_anywhere():
    result = build_multi_domain_user_scenarios()
    for layer_name, layer in [("global", result)] + [
        (f"scenario_{s['domain']}", s) for s in result["scenarios"]
    ] + [
        (f"cr_{s['domain']}", s.get("controlled_response", {}))
        for s in result["scenarios"]
    ]:
        for flag in MUTATION_FLAGS:
            assert layer.get(flag) is False, f"[{layer_name}] {flag} must be False"


def test_f37_global_status_ready():
    result = build_multi_domain_user_scenarios()
    assert result["global_status"] == "READY_READONLY"


def test_f37_unknown_refusal_text_no_execute():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "unknown_refusal")
    text = s["controlled_response"]["text"]
    assert "irréversible" in text.lower() or "opérateur" in text.lower()
    assert not _has_forbidden_token(text)


def test_f37_refusal_input_echoed():
    result = build_multi_domain_user_scenarios()
    s = _get_scenario(result, "unknown_refusal")
    text = s["controlled_response"]["text"]
    assert "irréversible" in text.lower() or "Brody" in text


def test_f37_boundary_module_constant_correct():
    for flag in ("emits_act", "emits_verdict", "memory_write", "graphiti_write",
                 "neo4j_write", "kernel_mutation", "x108_mutation", "runtime_execute",
                 "can_decide", "can_emit_act", "allowed_to_decide"):
        assert BOUNDARY[flag] is False, f"BOUNDARY[{flag!r}] must be False"
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert BOUNDARY["readonly"] is True
    assert BOUNDARY["advisory_only"] is True
    assert BOUNDARY["context_signal_only"] is True


def test_f37_forbidden_tokens_list_complete():
    assert "ALLOW" in FORBIDDEN_RESPONSE_TOKENS
    assert "HOLD" in FORBIDDEN_RESPONSE_TOKENS
    assert "BLOCK" in FORBIDDEN_RESPONSE_TOKENS
    assert "ACT" in FORBIDDEN_RESPONSE_TOKENS
    assert "DECIDE" in FORBIDDEN_RESPONSE_TOKENS
    assert "VERDICT" in FORBIDDEN_RESPONSE_TOKENS
