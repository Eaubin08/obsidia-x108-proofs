"""
F33 tests — Brody Runtime Entrypoint Readonly.

Verifies:
- Entrypoint envelope fields present and correct
- F32 packet embedded and READY_READONLY
- Full boundary block on entrypoint response
- All 7 surfaces present and READY inside f32_packet
- No forbidden mutation flags anywhere
- Graceful passthrough of unsupported sigma domain
- Trading domain works end-to-end
- Module-level BOUNDARY constant correct
"""
from __future__ import annotations

import pytest

from periphery.brody_runtime.f33_runtime_entrypoint_readonly import (
    BOUNDARY,
    ENTRYPOINT_ID,
    VERSION,
    PROOF_STATUS,
    call_brody_runtime_entrypoint,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

BANK_PAYLOAD = {
    "balance": 10_000.0,
    "transactions": [{"amount": 100.0, "type": "debit"}],
}

TRADING_PAYLOAD = {
    "symbol": "BTC/USDT",
    "prices": [100.0 + i for i in range(30)],
    "highs": [101.0 + i for i in range(30)],
    "lows": [99.0 + i for i in range(30)],
    "volumes": [1_000.0] * 30,
}

ACTIVATIONS_34 = [0.0] * 34


# ── Helpers ───────────────────────────────────────────────────────────────────

def assert_boundary_block(data: dict) -> None:
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["allowed_to_decide"] is False
    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["context_signal_only"] is True
    assert data["can_decide"] is False
    assert data["can_emit_act"] is False
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False
    assert data["runtime_execute"] is False


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_f33_entrypoint_returns_envelope():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert result["entrypoint_id"] == ENTRYPOINT_ID
    assert result["version"] == VERSION
    assert result["proof_status"] == PROOF_STATUS
    assert "called_at" in result
    assert isinstance(result["called_at"], str)
    assert len(result["called_at"]) > 0


def test_f33_entrypoint_status_ready():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert result["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert result["integration_status"] == "READY_READONLY"
    assert result["surfaces_ready"] == 7
    assert result["surfaces_missing"] == 0
    assert result["surfaces_total"] == 7


def test_f33_entrypoint_embeds_f32_packet():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    f32 = result["f32_packet"]
    assert f32["packet_id"] == "F32_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET"
    assert f32["version"] == "F32_V1"
    assert f32["integration_status"] == "READY_READONLY"
    assert "surfaces" in f32
    assert len(f32["surfaces"]) == 7


def test_f33_entrypoint_top_level_boundary():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert_boundary_block(result)


def test_f33_entrypoint_f32_packet_boundary():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert_boundary_block(result["f32_packet"])


def test_f33_entrypoint_all_seven_surfaces_ready():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    surfaces = result["f32_packet"]["surfaces"]
    expected = {
        "sigma_dispatcher",
        "tree_signal_packet",
        "monitoring_adapters",
        "operator_view_packet",
        "brody_runtime_context",
        "workflow_governance_readonly",
        "neo4j_guide_bridge",
    }
    assert set(surfaces.keys()) == expected
    not_ready = {k: v["status"] for k, v in surfaces.items() if v.get("status") != "READY"}
    assert not_ready == {}, f"surfaces not READY: {not_ready}"


def test_f33_entrypoint_no_mutation_flags():
    result = call_brody_runtime_entrypoint(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    for flag in ("kernel_mutation", "x108_mutation", "neo4j_write", "memory_write", "emits_act"):
        assert result.get(flag) is False, f"entrypoint: {flag} must be False"
    f32 = result["f32_packet"]
    for flag in ("kernel_mutation", "x108_mutation", "neo4j_write", "memory_write", "emits_act"):
        assert f32.get(flag) is False, f"f32_packet: {flag} must be False"


def test_f33_entrypoint_trading_domain():
    result = call_brody_runtime_entrypoint(
        domain="trading",
        sigma_payload=TRADING_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert result["entrypoint_status"] == "ENTRYPOINT_READY_READONLY"
    assert result["integration_status"] == "READY_READONLY"
    sigma = result["f32_packet"]["surfaces"]["sigma_dispatcher"]
    assert sigma["domain"] == "trading"
    assert sigma["result"]["domain"] == "trading"
    assert_boundary_block(result)


def test_f33_entrypoint_graceful_degradation_unsupported_domain():
    result = call_brody_runtime_entrypoint(
        domain="unknown_xyz",
        sigma_payload={},
        activations=ACTIVATIONS_34,
    )
    sigma = result["f32_packet"]["surfaces"]["sigma_dispatcher"]
    assert sigma["status"] == "READY"
    assert sigma["result"]["status"] == "UNSUPPORTED_DOMAIN"
    assert result["surfaces_total"] == 7
    assert_boundary_block(result)


def test_f33_entrypoint_proof_status():
    result = call_brody_runtime_entrypoint()
    assert result["proof_status"] == "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN"
    assert result["f32_packet"]["mode"] == "READONLY"


def test_f33_entrypoint_called_at_is_iso_string():
    result = call_brody_runtime_entrypoint()
    ts = result["called_at"]
    assert isinstance(ts, str)
    assert "T" in ts
    assert "+" in ts or ts.endswith("Z") or "+00:00" in ts or "UTC" in ts


def test_f33_boundary_module_constant_correct():
    for flag in ("emits_act", "emits_verdict", "memory_write", "graphiti_write",
                 "neo4j_write", "kernel_mutation", "x108_mutation", "runtime_execute",
                 "can_decide", "can_emit_act", "allowed_to_decide"):
        assert BOUNDARY[flag] is False, f"BOUNDARY[{flag!r}] must be False"
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert BOUNDARY["readonly"] is True
    assert BOUNDARY["advisory_only"] is True
    assert BOUNDARY["context_signal_only"] is True
