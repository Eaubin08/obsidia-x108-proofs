"""
P53 — Tests unitaires : activation World Action Bus DRY_RUN_ACTIVE contrôlée.
Vérifie les invariants KX108, no ACT, dry-run boundary, dry_run_packet.
NO ACT. NO write. DRY_RUN.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = ROOT / "_runtime_wiring_preflight" / "P53_REAL_WORLD_ACTION_BUS_DISCOVERY.json"
MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P53_WORLD_ACTION_BUS_DRY_RUN_ACTIVATION_MAP.json"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def state():
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    return build_world_action_bus_dry_run_state("Explique le runtime path Obsidia")


@pytest.fixture(scope="module")
def state_action_email():
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    return build_world_action_bus_dry_run_state("envoie un mail maintenant")


@pytest.fixture(scope="module")
def state_action_blockchain():
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    return build_world_action_bus_dry_run_state("lance une transaction blockchain")


@pytest.fixture(scope="module")
def state_action_memory():
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    return build_world_action_bus_dry_run_state("écris en mémoire")


@pytest.fixture(scope="module")
def p53_discovery():
    assert DISCOVERY_PATH.exists(), f"P53 discovery missing: {DISCOVERY_PATH}"
    return json.loads(DISCOVERY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p53_map():
    assert MAP_PATH.exists(), f"P53 map missing: {MAP_PATH}"
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : discovery JSON existe ────────────────────────────────────────────

def test_p53_discovery_exists(p53_discovery):
    assert p53_discovery["audit_id"] == "P53_REAL_WORLD_ACTION_BUS_DISCOVERY"


# ── Test 2 : vrai composant trouvé ────────────────────────────────────────────

def test_p53_real_component_found(p53_discovery):
    candidates = p53_discovery.get("candidates", [])
    real_candidates = [c for c in candidates if c.get("activation_candidate") is True]
    assert len(real_candidates) >= 2, (
        "Au moins 2 composants réels activation_candidate=True requis"
    )


# ── Test 3 : dry_run_enabled == True si composant réel ───────────────────────

def test_dry_run_enabled_true(state):
    assert state["dry_run_enabled"] is True


# ── Test 4 : real_action_enabled == False ─────────────────────────────────────

def test_real_action_enabled_false(state):
    assert state["real_action_enabled"] is False


# ── Test 5 : can_execute_real_action == False ─────────────────────────────────

def test_can_execute_real_action_false(state):
    assert state["can_execute_real_action"] is False


# ── Test 6 : runtime_allowed_now == False ─────────────────────────────────────

def test_runtime_allowed_now_false(state):
    assert state["runtime_allowed_now"] is False


# ── Test 7 : emits_act == False ───────────────────────────────────────────────

def test_emits_act_false(state):
    assert state["emits_act"] is False


# ── Test 8 : decision_authority == KX108_ONLY ─────────────────────────────────

def test_decision_authority_kx108(state):
    assert state["decision_authority"] == "KX108_ONLY"


# ── Test 9 : dry_run_packet contient real_execution=False ────────────────────

def test_dry_run_packet_real_execution_false_email(state_action_email):
    pkt = state_action_email.get("dry_run_packet", {})
    assert isinstance(pkt, dict), "dry_run_packet doit être présent pour action query"
    assert pkt.get("real_execution") is False


# ── Test 10 : dry_run_packet contient side_effects=False ─────────────────────

def test_dry_run_packet_side_effects_false_email(state_action_email):
    pkt = state_action_email.get("dry_run_packet", {})
    assert pkt.get("side_effects") is False


# ── Test 11 : action_request_blocked == True pour mail ───────────────────────

def test_action_request_blocked_email(state_action_email):
    assert state_action_email["action_request_blocked"] is True


# ── Test 12 : detected_action_type == EMAIL_SEND ─────────────────────────────

def test_detected_action_type_email(state_action_email):
    assert state_action_email["detected_action_type"] == "EMAIL_SEND"


# ── Test 13 : blockchain action détectée et bloquée ──────────────────────────

def test_blockchain_action_blocked(state_action_blockchain):
    assert state_action_blockchain["action_request_blocked"] is True
    assert state_action_blockchain["detected_action_type"] == "BLOCKCHAIN_TX"
    pkt = state_action_blockchain.get("dry_run_packet", {})
    assert pkt.get("real_execution") is False
    assert pkt.get("side_effects") is False


# ── Test 14 : memory write action détectée et bloquée ────────────────────────

def test_memory_write_action_blocked(state_action_memory):
    assert state_action_memory["action_request_blocked"] is True
    assert state_action_memory["detected_action_type"] == "MEMORY_WRITE"
    pkt = state_action_memory.get("dry_run_packet", {})
    assert pkt.get("real_execution") is False


# ── Test 15 : activation map JSON existe et valide ───────────────────────────

def test_p53_activation_map_valid(p53_map):
    assert p53_map["activation_level"] == "LEVEL_2_DRY_RUN_ACTIVE"
    assert p53_map["real_action_enabled"] is False
    assert p53_map["emits_act"] is False
    assert p53_map["runtime_allowed_now"] is False
    assert p53_map["decision_authority"] == "KX108_ONLY"


# ── Test 16 : module importable ───────────────────────────────────────────────

def test_module_importable():
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    assert callable(build_world_action_bus_dry_run_state)


# ── Test 17 : allowed_to_act == False ─────────────────────────────────────────

def test_allowed_to_act_false(state):
    assert state.get("allowed_to_act") is False


# ── Test 18 : x108_required_before_act == True ───────────────────────────────

def test_x108_required_before_act(state):
    assert state["x108_required_before_act"] is True
