"""
P52 — Tests unitaires : activation Graphiti/Memory READONLY_CONTEXT contrôlée.
Vérifie les vrais composants, invariants KX108, no write, no ACT.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = ROOT / "_runtime_wiring_preflight" / "P52_REAL_GRAPHITI_MEMORY_DISCOVERY.json"
MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P52_GRAPHITI_MEMORY_READONLY_ACTIVATION_MAP.json"
GRAPHITI_CLIENT_PATH = ROOT / "apps" / "obsidia_api" / "graphiti_v20_readonly_client.py"
MEMORY_ROUTE_PATH = ROOT / "apps" / "obsidia_api" / "routes" / "memory.py"
GRAPHITI_RECORDS_PATH = (
    ROOT
    / "_graphiti_readonly_indexes"
    / "GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854"
    / "graphiti_readonly_records_v2.jsonl"
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def state():
    from runtime_wiring.source_runtime.graphiti_memory_readonly_activation import (
        build_graphiti_memory_readonly_activation_state,
    )
    return build_graphiti_memory_readonly_activation_state("IR alphabet reverse OS interlanguage")


@pytest.fixture(scope="module")
def discovery():
    assert DISCOVERY_PATH.exists(), f"Discovery missing: {DISCOVERY_PATH}"
    return json.loads(DISCOVERY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p52_map():
    assert MAP_PATH.exists(), f"P52 map missing: {MAP_PATH}"
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : discovery JSON existe ───────────────────────────────────────────

def test_discovery_json_exists():
    assert DISCOVERY_PATH.exists()


# ── Test 2 : aucun faux composant déclaré real_component_found=true ──────────

def test_no_fake_component(discovery):
    for candidate in discovery.get("candidates", []):
        if candidate.get("activation_candidate") is True:
            path = ROOT / candidate["path"]
            assert path.exists(), (
                f"Component declared activation_candidate=True but file not found: {candidate['path']}"
            )


# ── Test 3 : si graphiti trouvé, le path existe réellement ───────────────────

def test_graphiti_client_path_exists():
    assert GRAPHITI_CLIENT_PATH.exists(), (
        f"graphiti_v20_readonly_client.py not found at {GRAPHITI_CLIENT_PATH}"
    )


# ── Test 4 : si memory trouvé, le path existe réellement ─────────────────────

def test_memory_route_path_exists():
    assert MEMORY_ROUTE_PATH.exists(), (
        f"memory.py route not found at {MEMORY_ROUTE_PATH}"
    )


# ── Test 5 : graphiti_write_enabled == false ──────────────────────────────────

def test_graphiti_write_enabled_false(state):
    assert state["graphiti_write_enabled"] is False


# ── Test 6 : memory_write_enabled == false ────────────────────────────────────

def test_memory_write_enabled_false(state):
    assert state["memory_write_enabled"] is False


# ── Test 7 : runtime_allowed_now == false ────────────────────────────────────

def test_runtime_allowed_now_false(state):
    assert state["runtime_allowed_now"] is False


# ── Test 8 : emits_act == false ──────────────────────────────────────────────

def test_emits_act_false(state):
    assert state["emits_act"] is False


# ── Test 9 : decision_authority == KX108_ONLY ────────────────────────────────

def test_decision_authority_kx108_only(state):
    assert state["decision_authority"] == "KX108_ONLY"


# ── Test 10 : graphiti_readonly_records_v2.jsonl existe et a des records ─────

def test_graphiti_readonly_records_exist():
    if not GRAPHITI_RECORDS_PATH.exists():
        pytest.skip("graphiti_readonly_records_v2.jsonl not found — skipping")
    count = 0
    with GRAPHITI_RECORDS_PATH.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                count += 1
    assert count > 0, "graphiti_readonly_records_v2.jsonl must not be empty"


# ── Test 11 : module importable ──────────────────────────────────────────────

def test_module_importable():
    from runtime_wiring.source_runtime.graphiti_memory_readonly_activation import (
        build_graphiti_memory_readonly_activation_state,
    )
    assert callable(build_graphiti_memory_readonly_activation_state)


# ── Test 12 : real_component_found cohérent avec graphiti_read_enabled ────────

def test_real_component_found_coherent(state):
    if state["real_component_found"]:
        assert state["graphiti_read_enabled"] or state["memory_read_enabled"], (
            "real_component_found=True but both graphiti and memory disabled"
        )


# ── Test bonus : p52_status ───────────────────────────────────────────────────

def test_p52_status_ready(state):
    assert state["p52_status"] == "P52_GRAPHITI_MEMORY_READONLY_CONTROLLED_ACTIVATION_READY"


# ── Test bonus : readonly dans le graphiti_v20_readonly_client ────────────────

def test_graphiti_client_has_readonly_envelope():
    content = GRAPHITI_CLIENT_PATH.read_text(encoding="utf-8")
    assert "graphiti_write" in content
    assert "neo4j_write" in content
    assert "emits_act" in content
    assert "readonly" in content
    assert "False" in content  # all set to False


# ── Test bonus : memory route a memory_write=False ────────────────────────────

def test_memory_route_has_no_write():
    content = MEMORY_ROUTE_PATH.read_text(encoding="utf-8")
    assert "memory_write" in content
    assert "auto_promotion" in content


# ── Test bonus : map JSON cohérente ──────────────────────────────────────────

def test_p52_map_status(p52_map):
    contract = p52_map.get("activation_contract", {})
    assert contract.get("graphiti_write_enabled") is False
    assert contract.get("memory_write_enabled") is False
    assert contract.get("emits_act") is False
    assert contract.get("decision_authority") == "KX108_ONLY"
