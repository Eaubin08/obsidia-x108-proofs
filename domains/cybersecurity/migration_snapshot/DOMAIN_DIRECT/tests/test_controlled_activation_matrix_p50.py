"""
P50 — Tests unitaires : matrice d'activation contrôlée.
Vérifie les niveaux d'activation, invariants KX108, no ACT.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
MATRIX_PATH = ROOT / "_runtime_wiring_preflight" / "P50_CONTROLLED_ACTIVATION_MATRIX.json"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def matrix():
    from runtime_wiring.source_runtime.controlled_activation_matrix import (
        build_controlled_activation_matrix,
    )
    return build_controlled_activation_matrix()


@pytest.fixture(scope="module")
def matrix_json():
    assert MATRIX_PATH.exists(), f"Matrix JSON missing: {MATRIX_PATH}"
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


# ── Test 1 : module importable ────────────────────────────────────────────────

def test_controlled_activation_matrix_importable():
    from runtime_wiring.source_runtime.controlled_activation_matrix import (
        build_controlled_activation_matrix,
    )
    assert callable(build_controlled_activation_matrix)


# ── Test 2 : activation_allowed_now == False ──────────────────────────────────

def test_activation_allowed_now_is_false(matrix):
    assert matrix["activation_allowed_now"] is False


# ── Test 3 : runtime_allowed_now == False ────────────────────────────────────

def test_runtime_allowed_now_is_false(matrix):
    assert matrix["runtime_allowed_now"] is False


# ── Test 4 : decision_authority == KX108_ONLY ────────────────────────────────

def test_decision_authority_kx108_only(matrix):
    assert matrix["decision_authority"] == "KX108_ONLY"


# ── Test 5 : Brody est LEVEL_1 readonly candidate ────────────────────────────

def test_brody_is_level_1_readonly(matrix):
    level_1_ids = [
        item["id"]
        for item in matrix["levels"]["LEVEL_1_READONLY_ACTIVE_CANDIDATE"]
    ]
    assert "brody_context_readonly" in level_1_ids, (
        f"brody_context_readonly must be in LEVEL_1; got {level_1_ids}"
    )


# ── Test 6 : Graphiti readonly est LEVEL_1 candidate ─────────────────────────

def test_graphiti_readonly_is_level_1(matrix):
    level_1_ids = [
        item["id"]
        for item in matrix["levels"]["LEVEL_1_READONLY_ACTIVE_CANDIDATE"]
    ]
    assert "graphiti_readonly_client" in level_1_ids


# ── Test 7 : Graphiti write est LEVEL_4 future gate ──────────────────────────

def test_graphiti_write_is_level_4(matrix):
    level_4_ids = [
        item["id"]
        for item in matrix["levels"]["LEVEL_4_FUTURE_ACTION_GATE"]
    ]
    assert "graphiti_write" in level_4_ids


# ── Test 8 : world action dry-run est LEVEL_2 candidate ──────────────────────

def test_world_action_dry_run_is_level_2(matrix):
    level_2_ids = [
        item["id"]
        for item in matrix["levels"]["LEVEL_2_DRY_RUN_ACTIVE_CANDIDATE"]
    ]
    assert "world_action_bus_dry_run" in level_2_ids


# ── Test 9 : real world action est LEVEL_4 future gate ───────────────────────

def test_real_world_action_is_level_4(matrix):
    wab = matrix["world_action_bus_readiness"]
    assert wab["real_action"]["level"] == "LEVEL_4_FUTURE_ACTION_GATE"


# ── Test 10 : aucun item action réel n'est LEVEL_1 ───────────────────────────

def test_no_real_action_item_in_level_1(matrix):
    assert matrix["any_real_action_in_level_1"] is False
    for item in matrix["levels"]["LEVEL_1_READONLY_ACTIVE_CANDIDATE"]:
        assert item.get("can_execute_actions") is not True, (
            f"Level 1 item {item['id']} must not have can_execute_actions=True"
        )
        assert item.get("emits_real_action") is not True, (
            f"Level 1 item {item['id']} must not have emits_real_action=True"
        )


# ── Test 11 : aucun ACT n'est autorisé ───────────────────────────────────────

def test_no_act_authorized(matrix):
    assert matrix["emits_act"] is False
    inv = matrix["invariant_check"]
    assert inv["no_act_in_level_1"] is True
    assert inv["no_real_action_gate_open"] is True
    assert inv["activation_allowed_now_is_false"] is True
    assert inv["runtime_allowed_now_is_false"] is True
    assert inv["kx108_only"] is True


# ── Test bonus : next palier correct ─────────────────────────────────────────

def test_next_activation_palier(matrix):
    assert matrix["next_activation_palier"] == "P51_BRODY_READONLY_CONTROLLED_ACTIVATION"


# ── Test bonus : p50_status correct ──────────────────────────────────────────

def test_p50_status(matrix):
    assert matrix["p50_status"] == "P50_CONTROLLED_ACTIVATION_READINESS_READY"


# ── Test bonus : LEVEL_0 contient kernel mutation ────────────────────────────

def test_level_0_contains_kernel_mutation(matrix):
    level_0_ids = [
        item["id"]
        for item in matrix["levels"]["LEVEL_0_LOCKED"]
    ]
    assert "kernel_mutation" in level_0_ids


# ── Test bonus : tous les niveaux sont présents ───────────────────────────────

def test_all_levels_present(matrix):
    levels = matrix["levels"]
    for key in (
        "LEVEL_0_LOCKED",
        "LEVEL_1_READONLY_ACTIVE_CANDIDATE",
        "LEVEL_2_DRY_RUN_ACTIVE_CANDIDATE",
        "LEVEL_3_HOLD_GATE_CANDIDATE",
        "LEVEL_4_FUTURE_ACTION_GATE",
    ):
        assert key in levels, f"Missing level: {key}"
        assert len(levels[key]) > 0, f"Level {key} must not be empty"


# ── Test bonus : Brody readiness structure ────────────────────────────────────

def test_brody_readiness_structure(matrix):
    brody = matrix["brody_readiness"]
    assert brody["brody_activation_mode"] == "READONLY_CONTEXT"
    assert brody["can_execute_actions"] is False
    assert brody["can_write_memory"] is False
    assert brody["can_mutate_graph"] is False
    assert brody["emits_act"] is False
    assert brody["decision_authority"] == "KX108_ONLY"


# ── Test bonus : JSON matrix cohérente ────────────────────────────────────────

def test_matrix_json_activation_allowed_false(matrix_json):
    assert matrix_json["activation_allowed_now"] is False


def test_matrix_json_status_ready(matrix_json):
    assert matrix_json["activation_matrix_status"] == "READY"
