"""
F32 tests — Brody Full Runtime Integration Readonly Packet.

Verifies:
- All 7 surfaces present and READY
- Full boundary block present and correct on top-level packet
- All surfaces carry decision_authority=KX108_ONLY
- No forbidden mutation flags anywhere
- No ACT / VERDICT / DECIDE tokens emitted
- Graceful degradation: unsupported sigma domain still builds full packet
- Proof status and integration status correct
"""
from __future__ import annotations

import pytest

from periphery.brody_runtime.f32_full_runtime_integration_readonly_packet import (
    BOUNDARY,
    PACKET_ID,
    VERSION,
    build_f32_full_runtime_integration_packet,
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
    assert data["decision_authority"] == "KX108_ONLY", "decision_authority must be KX108_ONLY"
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


def assert_surface_decision_authority(surface: dict, name: str) -> None:
    assert surface.get("decision_authority") == "KX108_ONLY", (
        f"surface '{name}' missing or wrong decision_authority"
    )


def assert_no_mutation_in_surface(surface: dict, name: str) -> None:
    for flag in ("kernel_mutation", "x108_mutation", "neo4j_write", "memory_write"):
        val = surface.get(flag)
        assert val is False or val is None, (
            f"surface '{name}': {flag}={val!r} — must be False or absent"
        )
    assert surface.get("emits_act") is not True, (
        f"surface '{name}': emits_act must not be True"
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_f32_packet_returns_all_seven_surfaces():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )

    assert pkt["packet_id"] == PACKET_ID
    assert pkt["version"] == VERSION

    surfaces = pkt["surfaces"]
    expected = {
        "sigma_dispatcher",
        "tree_signal_packet",
        "monitoring_adapters",
        "operator_view_packet",
        "brody_runtime_context",
        "workflow_governance_readonly",
        "neo4j_guide_bridge",
    }
    assert set(surfaces.keys()) == expected, (
        f"missing surfaces: {expected - set(surfaces.keys())}"
    )
    assert pkt["surfaces_total"] == 7


def test_f32_packet_all_surfaces_ready():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )

    surfaces = pkt["surfaces"]
    not_ready = {k: v["status"] for k, v in surfaces.items() if v.get("status") != "READY"}
    assert not_ready == {}, f"surfaces not READY: {not_ready}"

    assert pkt["surfaces_ready"] == 7
    assert pkt["surfaces_missing"] == 0
    assert pkt["integration_status"] == "READY_READONLY"


def test_f32_packet_top_level_boundary_block():
    pkt = build_f32_full_runtime_integration_packet(
        domain="trading",
        sigma_payload=TRADING_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert_boundary_block(pkt)


def test_f32_packet_every_surface_carries_kx108_authority():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    for name, surface in pkt["surfaces"].items():
        assert_surface_decision_authority(surface, name)


def test_f32_packet_no_mutation_flags_in_any_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    for name, surface in pkt["surfaces"].items():
        assert_no_mutation_in_surface(surface, name)


def test_f32_packet_sigma_dispatcher_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    sigma = pkt["surfaces"]["sigma_dispatcher"]
    assert sigma["status"] == "READY"
    assert sigma["domain"] == "bank"
    result = sigma["result"]
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False
    assert result["readonly"] is True


def test_f32_packet_tree_signal_surface():
    acts = [0.0] * 34
    acts[0] = 0.9
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        signal_id="f32-tree-test",
        activations=acts,
        theta=0.15,
    )
    tree = pkt["surfaces"]["tree_signal_packet"]
    assert tree["status"] == "READY"
    result = tree["result"]
    assert result["version"] == "TREE_SIGNAL_PACKET_V1"
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False
    assert result["kernel_mutation"] is False
    assert result["domain_sigma_attached"] is True


def test_f32_packet_monitoring_adapters_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    mon = pkt["surfaces"]["monitoring_adapters"]
    assert mon["status"] == "READY"
    assert "adapters" in mon
    for adapter_name in ("bank", "gps_defense_aviation", "trading"):
        assert adapter_name in mon["adapters"]
        a = mon["adapters"][adapter_name]
        assert a["status"] == "READY", f"adapter '{adapter_name}' not READY: {a}"
        assert a["decision_authority"] == "KX108_ONLY"
        assert a["control_packet_non_sovereign"] is True
        assert a["domain_sigma_attached"] is True


def test_f32_packet_operator_view_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    ovp = pkt["surfaces"]["operator_view_packet"]
    assert ovp["status"] == "READY"
    result = ovp["result"]
    assert "operator_view_packet" in result
    view = result["operator_view_packet"]
    assert view["summary"]["operator_can_decide"] is False
    assert view["decision_authority"] == "KX108_ONLY"


def test_f32_packet_runtime_context_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    ctx_surface = pkt["surfaces"]["brody_runtime_context"]
    assert ctx_surface["status"] == "READY"
    ctx = ctx_surface["result"]
    assert ctx["status"] == "BRODY_RUNTIME_CONTEXT_READY"
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["domain_sigma_ready"] is True
    assert ctx["tree_signal_ready"] is True
    assert ctx["emits_act"] is False
    assert ctx["kernel_mutation"] is False
    assert ctx["x108_mutation"] is False


def test_f32_packet_workflow_governance_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        sop_text=(
            "1. Receive request\n"
            "2. Validate readonly contract\n"
            "3. Prepare advisory response"
        ),
        title="F32 workflow test",
        session_id="f32-wf-test",
        activations=ACTIVATIONS_34,
    )
    wf = pkt["surfaces"]["workflow_governance_readonly"]
    assert wf["status"] == "READY"
    snapshot = wf["result"]
    assert snapshot["snapshot_kind"] == "BRODY_WORKFLOW_GOVERNANCE_SNAPSHOT_READONLY_V5"
    assert snapshot["decision_authority"] == "KX108_ONLY"
    assert snapshot["boundary"]["emits_act"] is False
    assert snapshot["boundary"]["kernel_mutation"] is False
    assert snapshot["boundary"]["x108_mutation"] is False


def test_f32_packet_neo4j_guide_bridge_surface():
    pkt = build_f32_full_runtime_integration_packet(
        domain="bank",
        sigma_payload=BANK_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    neo4j = pkt["surfaces"]["neo4j_guide_bridge"]
    assert neo4j["status"] == "READY"
    assert neo4j["guard_mode"] == "DOUBLE_GUARD_MANUAL_ONLY"
    assert neo4j["runtime_auto_accessible"] is False
    assert neo4j["neo4j_write"] is False
    assert neo4j["kernel_mutation"] is False
    assert neo4j["x108_mutation"] is False
    assert neo4j["decision_authority"] == "KX108_ONLY"
    nb = neo4j["neo4j_boundary"]
    assert nb["decision_authority"] == "KX108_ONLY"
    assert nb["runtime_execute"] is False
    assert nb["kernel_mutation"] is False
    assert nb["x108_mutation"] is False


def test_f32_packet_proof_status():
    pkt = build_f32_full_runtime_integration_packet()
    assert pkt["proof_status"] == "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN"
    assert pkt["mode"] == "READONLY"


def test_f32_packet_has_stable_sha256():
    pkt = build_f32_full_runtime_integration_packet()
    sha = pkt["packet_sha256"]
    assert isinstance(sha, str)
    assert len(sha) == 64
    # Stable: two calls with same params yield same sha256
    pkt2 = build_f32_full_runtime_integration_packet()
    assert pkt["packet_sha256"] == pkt2["packet_sha256"]


def test_f32_packet_graceful_degradation_unsupported_domain():
    pkt = build_f32_full_runtime_integration_packet(
        domain="unknown_domain_xyz",
        sigma_payload={},
        activations=ACTIVATIONS_34,
    )
    # sigma returns READY with UNSUPPORTED_DOMAIN status inside result — not a degraded surface
    sigma = pkt["surfaces"]["sigma_dispatcher"]
    assert sigma["status"] == "READY"
    assert sigma["result"]["status"] == "UNSUPPORTED_DOMAIN"
    # The rest of the packet still builds
    assert pkt["surfaces_total"] == 7
    assert_boundary_block(pkt)


def test_f32_packet_trading_domain():
    pkt = build_f32_full_runtime_integration_packet(
        domain="trading",
        sigma_payload=TRADING_PAYLOAD,
        activations=ACTIVATIONS_34,
    )
    assert pkt["integration_status"] == "READY_READONLY"
    assert pkt["surfaces"]["sigma_dispatcher"]["domain"] == "trading"
    result = pkt["surfaces"]["sigma_dispatcher"]["result"]
    assert result["domain"] == "trading"
    assert result["decision_authority"] == "KX108_ONLY"
    assert_boundary_block(pkt)


def test_f32_boundary_module_constant_correct():
    for flag in ("emits_act", "emits_verdict", "memory_write", "graphiti_write",
                 "neo4j_write", "kernel_mutation", "x108_mutation", "runtime_execute",
                 "can_decide", "can_emit_act", "allowed_to_decide"):
        assert BOUNDARY[flag] is False, f"BOUNDARY[{flag!r}] must be False"
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert BOUNDARY["readonly"] is True
    assert BOUNDARY["advisory_only"] is True
    assert BOUNDARY["context_signal_only"] is True
