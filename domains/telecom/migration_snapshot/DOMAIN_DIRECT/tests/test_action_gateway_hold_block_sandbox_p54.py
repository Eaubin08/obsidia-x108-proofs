"""
P54 — Tests unitaires : Hold/Block sandbox pour l'action gateway.
Vérifie les verdicts HOLD/BLOCK, invariants KX108, no ACT.
NO ACT. NO write. SANDBOX.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = ROOT / "_runtime_wiring_preflight" / "P54_REAL_ACTION_GATEWAY_DISCOVERY.json"
MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P54_ACTION_GATEWAY_HOLD_BLOCK_SANDBOX_MAP.json"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def state():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    return build_action_gateway_sandbox_state("Explique le runtime Obsidia")


@pytest.fixture(scope="module")
def state_mail():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    return build_action_gateway_sandbox_state("envoie un mail maintenant")


@pytest.fixture(scope="module")
def state_blockchain():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    return build_action_gateway_sandbox_state("lance une transaction blockchain")


@pytest.fixture(scope="module")
def state_memory():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    return build_action_gateway_sandbox_state("écris en mémoire")


@pytest.fixture(scope="module")
def state_generic():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    return build_action_gateway_sandbox_state("fais une action quelconque")


@pytest.fixture(scope="module")
def p54_discovery():
    assert DISCOVERY_PATH.exists(), f"P54 discovery missing: {DISCOVERY_PATH}"
    return json.loads(DISCOVERY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p54_map():
    assert MAP_PATH.exists(), f"P54 map missing: {MAP_PATH}"
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : sandbox importable ────────────────────────────────────────────────

def test_sandbox_importable():
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    assert callable(build_action_gateway_sandbox_state)


# ── Test 2 : sandbox_enabled == True ──────────────────────────────────────────

def test_sandbox_enabled(state):
    assert state["sandbox_enabled"] is True


# ── Test 3 : can_evaluate_hold_block == True ──────────────────────────────────

def test_can_evaluate_hold_block(state):
    assert state["can_evaluate_hold_block"] is True


# ── Test 4 : can_emit_act == False ────────────────────────────────────────────

def test_can_emit_act_false(state):
    assert state["can_emit_act"] is False


# ── Test 5 : real_action_enabled == False ─────────────────────────────────────

def test_real_action_enabled_false(state):
    assert state["real_action_enabled"] is False


# ── Test 6 : runtime_allowed_now == False ─────────────────────────────────────

def test_runtime_allowed_now_false(state):
    assert state["runtime_allowed_now"] is False


# ── Test 7 : emits_act == False ───────────────────────────────────────────────

def test_emits_act_false(state):
    assert state["emits_act"] is False


# ── Test 8 : decision_authority == KX108_ONLY ─────────────────────────────────

def test_decision_authority_kx108(state):
    assert state["decision_authority"] == "KX108_ONLY"


# ── Test 9 : mail query donne BLOCK ───────────────────────────────────────────

def test_mail_gives_block(state_mail):
    assert state_mail["sandbox_verdict"] == "BLOCK"
    assert state_mail["detected_action_type"] == "EMAIL_SEND"


# ── Test 10 : blockchain query donne BLOCK ────────────────────────────────────

def test_blockchain_gives_block(state_blockchain):
    assert state_blockchain["sandbox_verdict"] == "BLOCK"
    assert state_blockchain["detected_action_type"] == "BLOCKCHAIN_TX"


# ── Test 11 : memory write donne BLOCK ────────────────────────────────────────

def test_memory_write_gives_block(state_memory):
    assert state_memory["sandbox_verdict"] == "BLOCK"
    assert state_memory["detected_action_type"] == "MEMORY_WRITE"


# ── Test 12 : generic action donne HOLD ou BLOCK ──────────────────────────────

def test_generic_action_gives_hold_or_block(state_generic):
    assert state_generic["sandbox_verdict"] in ("HOLD", "BLOCK"), (
        f"Generic action must give HOLD or BLOCK, got: {state_generic['sandbox_verdict']}"
    )


# ── Test 13 : aucun cas ne produit ACT ────────────────────────────────────────

def test_no_act_in_any_case(state, state_mail, state_blockchain, state_memory, state_generic):
    for s in (state, state_mail, state_blockchain, state_memory, state_generic):
        assert s["sandbox_verdict"] in ("ALLOW_CONTEXT_ONLY", "HOLD", "BLOCK"), (
            f"sandbox_verdict must not be ACT, got: {s['sandbox_verdict']}"
        )
        assert s["can_emit_act"] is False
        assert s["emits_act"] is False
        assert s["real_action_enabled"] is False


# ── Test 14 : X108 ticket emits_act == False ──────────────────────────────────

def test_x108_ticket_emits_act_false(state_mail):
    x108 = state_mail.get("x108_evaluation", {})
    assert x108.get("x108_emits_act") is False


# ── Test 15 : discovery JSON présent et valide ────────────────────────────────

def test_p54_discovery_valid(p54_discovery):
    candidates = p54_discovery.get("candidates", [])
    real = [c for c in candidates if c.get("sandbox_candidate") is True]
    assert len(real) >= 2


# ── Test 16 : activation map présente ────────────────────────────────────────

def test_p54_map_valid(p54_map):
    assert p54_map["activation_level"] == "LEVEL_3_HOLD_GATE_CANDIDATE"
    assert p54_map["real_action_enabled"] is False
    assert p54_map["emits_act"] is False
