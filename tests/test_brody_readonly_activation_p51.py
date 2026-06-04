"""
P51 — Tests unitaires : activation Brody READONLY_CONTEXT contrôlée.
Vérifie l'état d'activation, les invariants KX108, no ACT.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P51_BRODY_READONLY_ACTIVATION_MAP.json"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def state():
    from runtime_wiring.source_runtime.brody_readonly_activation import (
        build_brody_readonly_activation_state,
    )
    return build_brody_readonly_activation_state("IR alphabet reverse OS interlanguage")


@pytest.fixture(scope="module")
def state_action():
    from runtime_wiring.source_runtime.brody_readonly_activation import (
        build_brody_readonly_activation_state,
    )
    return build_brody_readonly_activation_state("envoie un mail maintenant")


@pytest.fixture(scope="module")
def p51_map():
    assert MAP_PATH.exists(), f"P51 map missing: {MAP_PATH}"
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : module importable ────────────────────────────────────────────────

def test_brody_readonly_activation_importable():
    from runtime_wiring.source_runtime.brody_readonly_activation import (
        build_brody_readonly_activation_state,
    )
    assert callable(build_brody_readonly_activation_state)


# ── Test 2 : brody_readonly_enabled == true ───────────────────────────────────

def test_brody_readonly_enabled_true(state):
    assert state["brody_readonly_enabled"] is True


# ── Test 3 : activation_level == LEVEL_1_READONLY_ACTIVE ─────────────────────

def test_activation_level(state):
    assert state["activation_level"] == "LEVEL_1_READONLY_ACTIVE"


# ── Test 4 : brody_can_answer == true ─────────────────────────────────────────

def test_brody_can_answer(state):
    assert state["brody_can_answer"] is True


# ── Test 5 : brody_can_explain_runtime_path == true ───────────────────────────

def test_brody_can_explain_runtime_path(state):
    assert state["brody_can_explain_runtime_path"] is True


# ── Test 6 : brody_can_execute_actions == false ───────────────────────────────

def test_brody_can_execute_actions_false(state):
    assert state["brody_can_execute_actions"] is False


# ── Test 7 : brody_can_write_memory == false ──────────────────────────────────

def test_brody_can_write_memory_false(state):
    assert state["brody_can_write_memory"] is False


# ── Test 8 : brody_can_write_graphiti == false ────────────────────────────────

def test_brody_can_write_graphiti_false(state):
    assert state["brody_can_write_graphiti"] is False


# ── Test 9 : runtime_allowed_now == false ─────────────────────────────────────

def test_runtime_allowed_now_false(state):
    assert state["runtime_allowed_now"] is False


# ── Test 10 : emits_act == false ──────────────────────────────────────────────

def test_emits_act_false(state):
    assert state["emits_act"] is False


# ── Test 11 : decision_authority == KX108_ONLY ───────────────────────────────

def test_decision_authority_kx108_only(state):
    assert state["decision_authority"] == "KX108_ONLY"


# ── Test 12 : action query bloque correctement ───────────────────────────────

def test_action_query_blocked(state_action):
    assert state_action["action_request_blocked"] is True
    assert state_action["action_status"] == "ACTION_REQUEST_BLOCKED"
    assert state_action["emits_act"] is False
    assert state_action["brody_can_execute_actions"] is False


# ── Test 13 : non-action query ne bloque pas ──────────────────────────────────

def test_non_action_query_not_blocked(state):
    assert state["action_request_blocked"] is False
    assert state["action_status"] == "NO_ACTION_IN_QUERY"


# ── Test bonus : os_map_summary présent ──────────────────────────────────────

def test_os_map_summary_present(state):
    summary = state.get("os_map_summary", {})
    assert isinstance(summary, dict)
    assert "os_map_summary_status" in summary
    assert summary.get("readonly") is True
    assert summary.get("emits_act") is False


# ── Test bonus : blocked_modes contient ACTION ────────────────────────────────

def test_blocked_modes_contains_action(state):
    blocked = state.get("blocked_modes", [])
    assert "ACTION" in blocked
    assert "MEMORY_WRITE" in blocked
    assert "GRAPHITI_WRITE" in blocked
    assert "WORLD_ACTION" in blocked


# ── Test bonus : p51_status correct ──────────────────────────────────────────

def test_p51_status(state):
    assert state["p51_status"] == "P51_BRODY_READONLY_CONTROLLED_ACTIVATION_READY"


# ── Test bonus : get_brody_readonly_boundary ─────────────────────────────────

def test_get_brody_readonly_boundary():
    from runtime_wiring.source_runtime.brody_readonly_activation import (
        get_brody_readonly_boundary,
    )
    boundary = get_brody_readonly_boundary()
    assert boundary["emits_act"] is False
    assert boundary["memory_write"] is False
    assert boundary["graph_write"] is False
    assert boundary["kernel_mutation"] is False
    assert boundary["runtime_allowed_now"] is False
    assert boundary["decision_authority"] == "KX108_ONLY"


# ── Test bonus : JSON map cohérente ──────────────────────────────────────────

def test_p51_map_exists(p51_map):
    assert p51_map["audit_id"] == "P51_BRODY_READONLY_ACTIVATION_MAP"
    contract = p51_map.get("p51_activation_contract", {})
    assert contract.get("brody_readonly_enabled") is True
    assert contract.get("emits_act") is False
    assert contract.get("decision_authority") == "KX108_ONLY"
