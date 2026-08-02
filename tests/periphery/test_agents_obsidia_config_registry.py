"""
Tests for periphery.agents_obsidia_config_registry — Batch 001 + Batch 002.

PHASE: AGENTS52_READONLY_REGISTRY_BATCH002_001
AUTHORITY: NON_SOVEREIGN — no agent invoked, no model called, no memory written.
"""
from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import inspect

import pytest

from periphery.agents_obsidia_config_registry import (
    AgentConfigEntry,
    _BATCH001_AGENT_TO_ROW,
    _BATCH001_ROW_MAP,
    _BATCH001_TAG,
    _BATCH002_AGENT_TO_ROW,
    _BATCH002_ROW_MAP,
    _BATCH002_TAG,
    _registry_path,
    get_agent_config,
    get_registry_provenance,
    list_agent_configs,
    list_agents_by_family,
    load_registry,
    validate_registry,
)

# ART118 reference data — single source of truth for batch001 mapping verification
_ART118_ROW_MAP = {
    "1811": "SECURITY_FIREWALL_ARCHITECT",
    "1812": "POLICY_FIREWALL_AGENT",
    "1813": "RUNTIME_ATTESTATION_AGENT",
    "1814": "SUPPLY_CHAIN_GUARD",
    "1815": "SECRET_GUARD",
}
_ART118_NAMES = set(_ART118_ROW_MAP.values())
_SECURITY_FAMILY = "Sécurité / Pare-feu"

# ART150 reference data — single source of truth for batch002 mapping verification
_ART150_ROW_MAP = {
    "1821": "FRISE_HUMAINE",
    "1822": "CARTOGRAPHE_34_ARBRES",
    "1823": "HUMAN_HISTORY_MAPPER",
    "1824": "CALIBRATION_PROCEDURALE",
    "1825": "NUAGE_POINTS",
}
_ART150_NAMES = set(_ART150_ROW_MAP.values())
_FRISE_FAMILY = "Frise / Arbres / Monde humain"


# ── Registry source and load ──────────────────────────────────────────────────

def test_001_registry_source_present():
    """Registry JSON file exists at the relative path built from __file__."""
    path = _registry_path()
    assert path.exists(), f"Registry not found: {path}"
    assert path.suffix == ".json"


def test_002_sha256_calculated():
    """SHA256 is non-empty (64 hex chars) after loading."""
    import periphery.agents_obsidia_config_registry as mod
    load_registry()
    assert mod._CACHE_SHA, "SHA256 must be non-empty after load"
    assert len(mod._CACHE_SHA) == 64


def test_003_52_entries_loaded():
    """Registry loads exactly 52 entries."""
    entries = load_registry()
    assert len(entries) == 52, f"Expected 52, got {len(entries)}"


def test_004_unique_agent_ids():
    """All 52 agent_ids are unique."""
    ids = [e.agent_id for e in load_registry()]
    assert len(set(ids)) == 52


def test_005_ids_non_empty():
    """All agent_ids are non-empty strings."""
    for e in load_registry():
        assert isinstance(e.agent_id, str) and e.agent_id, f"Empty agent_id: {e}"


def test_006_schema_complete():
    """All entries have non-empty values for all required fields."""
    required_str = [
        "agent_id", "name", "family", "role", "input_contract",
        "output_contract", "boundary", "deployment", "validation_status",
        "source_path", "source_reference", "source_registry_sha256",
        "compilation_status", "authority",
    ]
    for e in load_registry():
        for field in required_str:
            val = getattr(e, field)
            assert val, f"{e.agent_id}: field {field!r} is empty or falsy"


# ── Batch 001 mapping ─────────────────────────────────────────────────────────

def test_007_batch001_five_mappings():
    """Exactly 5 entries carry the AGENTS52_BATCH001 tag."""
    batch = [e for e in load_registry() if e.compilation_batch == _BATCH001_TAG]
    assert len(batch) == 5, f"Expected 5 batch001 entries, got {len(batch)}"


def test_008_batch001_exact_agent_ids():
    """Batch 001 agent_ids match ART118 names exactly."""
    batch_ids = {
        e.agent_id for e in load_registry() if e.compilation_batch == _BATCH001_TAG
    }
    assert batch_ids == _ART118_NAMES, f"Mismatch: {batch_ids} != {_ART118_NAMES}"


def test_009_batch001_row_ids_match_art118():
    """Each batch001 entry's source_row_id matches ART118's explicit mapping."""
    batch_map = {
        e.agent_id: e.source_row_id
        for e in load_registry()
        if e.compilation_batch == _BATCH001_TAG
    }
    for row_id, agent_name in _ART118_ROW_MAP.items():
        got = batch_map.get(agent_name)
        assert got == row_id, (
            f"Row ID for {agent_name}: expected {row_id!r}, got {got!r}"
        )


def test_010_other_42_documented_source_only():
    """42 non-batch entries have compilation_batch=None and DOCUMENTED_SOURCE_ONLY."""
    others = [e for e in load_registry() if e.compilation_batch is None]
    assert len(others) == 42, f"Expected 42 (47 minus 5 batch002), got {len(others)}"
    for e in others:
        assert e.compilation_status == "DOCUMENTED_SOURCE_ONLY", (
            f"{e.agent_id}: status should be DOCUMENTED_SOURCE_ONLY"
        )


def test_011_validation_status_preserved():
    """All 52 entries retain NEEDS_HUMAN_VALIDATION — never auto-promoted."""
    for e in load_registry():
        assert e.validation_status == "NEEDS_HUMAN_VALIDATION", (
            f"{e.agent_id}: validation_status must remain NEEDS_HUMAN_VALIDATION"
        )


# ── Immutability and determinism ──────────────────────────────────────────────

def test_012_immutable_objects():
    """AgentConfigEntry is frozen; direct attribute assignment raises FrozenInstanceError."""
    entry = load_registry()[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.agent_id = "TAMPERED"  # type: ignore[misc]


def test_013_deterministic_list():
    """list_agent_configs is sorted and reproducible across two calls."""
    first = list_agent_configs()
    second = list_agent_configs()
    assert first == second
    assert first == sorted(first)
    assert len(first) == 52


def test_014_filter_by_family():
    """list_agents_by_family returns only entries matching the family."""
    results = list_agents_by_family(_SECURITY_FAMILY)
    assert all(e.family == _SECURITY_FAMILY for e in results)
    assert len(results) >= 5
    batch_in_family = {e.agent_id for e in results if e.compilation_batch == _BATCH001_TAG}
    assert batch_in_family == _ART118_NAMES


def test_015_unknown_agent_rejected():
    """get_agent_config raises KeyError with UNKNOWN_AGENT_CONFIG for bad id."""
    with pytest.raises(KeyError, match="UNKNOWN_AGENT_CONFIG"):
        get_agent_config("NOT_AN_AGENT_XYZ_000")


# ── Safety: no write functions, no JSON mutation ──────────────────────────────

def test_016_no_write_functions_exported():
    """Module exposes no write/mutate/invoke/run functions."""
    import periphery.agents_obsidia_config_registry as mod
    forbidden = [
        "write_registry", "update_agent", "delete_agent", "select_agent",
        "invoke_agent", "run_agent", "route_agent", "choose_model",
        "generate_prompt", "call_model", "invoke_model",
    ]
    for fn in forbidden:
        assert not hasattr(mod, fn), f"Module must not expose {fn!r}"


def test_017_no_json_mutation():
    """load_registry does not modify the source JSON file."""
    path = _registry_path()
    sha_before = hashlib.sha256(path.read_bytes()).hexdigest()
    load_registry()
    sha_after = hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha_before == sha_after, "Registry JSON must not be mutated by load_registry"


def test_018_no_network_calls(monkeypatch):
    """Registry module performs no network I/O (reads local file only)."""
    import socket

    def _blocked(*args, **kwargs):
        raise OSError("NETWORK_CALL_FORBIDDEN in agents_obsidia_config_registry")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)
    entries = load_registry()
    assert len(entries) == 52


def test_019_no_model_call_symbols():
    """Source of registry module contains no LLM/model invocation symbols."""
    import periphery.agents_obsidia_config_registry as mod
    source = inspect.getsource(mod)
    model_symbols = [
        "openai", "anthropic", "vertexai", "litellm",
        "call_model", "invoke_model", "chat.complete",
        "GenerativeModel",
    ]
    for sym in model_symbols:
        assert sym not in source, f"Model symbol {sym!r} found in registry source"


# ── Authority invariants ──────────────────────────────────────────────────────

def test_020_no_memory_write():
    """memory_write, graphiti_write, neo4j_write are False for all entries."""
    for e in load_registry():
        assert not e.memory_write, f"{e.agent_id}: memory_write must be False"
        assert not e.graphiti_write, f"{e.agent_id}: graphiti_write must be False"
        assert not e.neo4j_write, f"{e.agent_id}: neo4j_write must be False"


def test_021_can_decide_false():
    """can_decide is False for all 52 entries."""
    for e in load_registry():
        assert not e.can_decide, f"{e.agent_id}: can_decide must be False"


def test_022_can_act_false():
    """can_act is False for all 52 entries."""
    for e in load_registry():
        assert not e.can_act, f"{e.agent_id}: can_act must be False"


def test_023_emits_act_false():
    """emits_act is False for all 52 entries."""
    for e in load_registry():
        assert not e.emits_act, f"{e.agent_id}: emits_act must be False"


# ── Endpoint tests ────────────────────────────────────────────────────────────

def test_024_endpoints_importable():
    """periphery_list_agents_52 and periphery_get_agent_config are callable."""
    from apps.obsidia_api.routes.periphery_ops import (
        periphery_get_agent_config,
        periphery_list_agents_52,
    )
    assert callable(periphery_list_agents_52)
    assert callable(periphery_get_agent_config)


def test_025_list_endpoint_returns_52():
    """List endpoint returns count=52 and a list of 52 agent_id strings."""
    from apps.obsidia_api.routes.periphery_ops import periphery_list_agents_52
    result = asyncio.run(periphery_list_agents_52())
    assert result["count"] == 52
    assert len(result["agents"]) == 52
    # Sovereignty flags enforced by safe_backend_response
    assert result["readonly"] is True
    assert result["emits_act"] is False
    assert result["memory_write"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_026_detail_endpoint_correct_entry():
    """Detail endpoint returns the correct entry for SECRET_GUARD (row 1815)."""
    from apps.obsidia_api.routes.periphery_ops import periphery_get_agent_config
    result = asyncio.run(periphery_get_agent_config(agent_id="SECRET_GUARD"))
    assert result["agent_id"] == "SECRET_GUARD"
    assert result["can_decide"] is False
    assert result["can_act"] is False
    assert result["emits_act"] is False
    assert result["source_row_id"] == "1815"
    assert result["compilation_batch"] == _BATCH001_TAG
    assert result["compilation_status"] == "DOCUMENTED_AGENT_CONFIG_REGISTERED_READONLY"
    assert result["validation_status"] == "NEEDS_HUMAN_VALIDATION"
    # Sovereignty enforced
    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"


def test_027_unknown_agent_produces_404():
    """Detail endpoint raises HTTP 404 for an unknown agent_id."""
    from fastapi import HTTPException
    from apps.obsidia_api.routes.periphery_ops import periphery_get_agent_config
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(periphery_get_agent_config(agent_id="DOES_NOT_EXIST_XYZ_999"))
    assert exc_info.value.status_code == 404
    assert "UNKNOWN_AGENT_CONFIG" in str(exc_info.value.detail)


def test_028_no_absolute_path_in_response():
    """Detail endpoint response does not leak absolute filesystem paths."""
    from apps.obsidia_api.routes.periphery_ops import periphery_get_agent_config
    import json
    result = asyncio.run(periphery_get_agent_config(agent_id="SECRET_GUARD"))
    body_str = json.dumps(result)
    assert "C:\\" not in body_str, "Absolute Windows path leaked in response"
    assert "C:/" not in body_str, "Absolute Windows path leaked in response"
    assert "/Users/" not in body_str, "Absolute Unix path leaked in response"
    assert "/home/" not in body_str, "Absolute Unix path leaked in response"


def test_029_historical_routes_unchanged():
    """Existing /governance/agents endpoint still returns 14 Python operational agents."""
    from apps.obsidia_api.routes.periphery_ops import periphery_list_agents
    result = asyncio.run(periphery_list_agents())
    assert result["count"] == 14, f"Expected 14 Python agents, got {result['count']}"
    assert "agents" in result
    assert len(result["agents"]) == 14


def test_030_separation_python_vs_agents52():
    """Python operational agents and agents52 configs have no name overlap."""
    from apps.obsidia_api.routes.periphery_ops import (
        periphery_list_agents,
        periphery_list_agents_52,
    )
    py_result = asyncio.run(periphery_list_agents())
    a52_result = asyncio.run(periphery_list_agents_52())
    py_agents = set(py_result["agents"])
    a52_agents = set(a52_result["agents"])
    overlap = py_agents & a52_agents
    assert not overlap, f"Overlap between Python agents and agents52: {overlap}"
    assert py_result["count"] == 14
    assert a52_result["count"] == 52


# ── agent-run rejection tests (Phase REPAIR) ─────────────────────────────────
# §8 mandatory criteria — 15 tests (test_031 through test_045)
# AGENTS52_CONFIG_NOT_EXECUTABLE → HTTP 422
# UNKNOWN_OPERATIONAL_AGENT → HTTP 404
# Valid Python operational agent → behaviour unchanged (no 500)

def _agent_run_client():
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    return TestClient(app, raise_server_exceptions=False)


_AGENT_RUN_ACTION = {
    "action_id": "test-repair-031",
    "domain": "test",
    "actor_id": "test_suite",
    "intent": "inspect",
}


def test_031_secret_guard_returns_422():
    """SECRET_GUARD (agents52) on agent-run returns HTTP 422."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "SECRET_GUARD", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"


def test_032_secret_guard_detail_deterministic():
    """SECRET_GUARD rejection detail is AGENTS52_CONFIG_NOT_EXECUTABLE:SECRET_GUARD."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "SECRET_GUARD", "action": _AGENT_RUN_ACTION},
    )
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text, f"Detail missing: {r.text}"
    assert "SECRET_GUARD" in r.text, f"Agent id missing from detail: {r.text}"


def test_033_security_firewall_architect_returns_422():
    """SECURITY_FIREWALL_ARCHITECT (agents52, batch001) on agent-run returns HTTP 422."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "SECURITY_FIREWALL_ARCHITECT", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text


def test_034_policy_firewall_agent_returns_422():
    """POLICY_FIREWALL_AGENT (agents52, batch001) on agent-run returns HTTP 422."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "POLICY_FIREWALL_AGENT", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text


def test_035_runtime_attestation_agent_returns_422():
    """RUNTIME_ATTESTATION_AGENT (agents52, batch001) on agent-run returns HTTP 422."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "RUNTIME_ATTESTATION_AGENT", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text


def test_036_supply_chain_guard_returns_422():
    """SUPPLY_CHAIN_GUARD (agents52, batch001) on agent-run returns HTTP 422."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "SUPPLY_CHAIN_GUARD", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text


def test_037_agents52_never_500():
    """No agents52 batch001 ID ever returns HTTP 500 on agent-run."""
    client = _agent_run_client()
    batch001_ids = [
        "SECURITY_FIREWALL_ARCHITECT",
        "POLICY_FIREWALL_AGENT",
        "RUNTIME_ATTESTATION_AGENT",
        "SUPPLY_CHAIN_GUARD",
        "SECRET_GUARD",
    ]
    for agent_id in batch001_ids:
        r = client.post(
            "/api/periphery/governance/agent-run",
            json={"agent_id": agent_id, "action": _AGENT_RUN_ACTION},
        )
        assert r.status_code != 500, (
            f"{agent_id}: agent-run must never return 500, got {r.status_code}: {r.text}"
        )


def test_038_unknown_id_returns_404():
    """Completely unknown agent_id on agent-run returns HTTP 404."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "NONEXISTENT_AGENT_XYZ_999", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"


def test_039_unknown_id_detail_deterministic():
    """Unknown agent_id rejection detail is UNKNOWN_OPERATIONAL_AGENT:<id>."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "NONEXISTENT_AGENT_XYZ_999", "action": _AGENT_RUN_ACTION},
    )
    assert "UNKNOWN_OPERATIONAL_AGENT" in r.text, f"Detail missing: {r.text}"


def test_040_unknown_id_never_500():
    """Completely unknown agent_id never returns HTTP 500 (no unhandled KeyError)."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "GHOST_AGENT_000", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code != 500, f"Unknown agent must not return 500, got {r.text}"
    assert r.status_code == 404


def test_041_agents52_rejection_not_404():
    """agents52 IDs return 422 (not 404) — they exist as configs, are not unknown."""
    client = _agent_run_client()
    r = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": "SECRET_GUARD", "action": _AGENT_RUN_ACTION},
    )
    assert r.status_code != 404, (
        f"agents52 IDs must not return 404 (they are known configs): {r.text}"
    )
    assert r.status_code == 422


def test_042_readonly_config_routes_unaffected():
    """GET /governance/agents-52 and GET /governance/agent-config still return 200."""
    client = _agent_run_client()
    r_list = client.get("/api/periphery/governance/agents-52")
    assert r_list.status_code == 200, f"agents-52 list broken: {r_list.text}"
    r_detail = client.get("/api/periphery/governance/agent-config/SECRET_GUARD")
    assert r_detail.status_code == 200, f"agent-config detail broken: {r_detail.text}"


def test_043_list_agents_route_unaffected():
    """GET /governance/agents still returns 14 Python operational agents."""
    client = _agent_run_client()
    r = client.get("/api/periphery/governance/agents")
    assert r.status_code == 200
    body = r.json()
    assert body.get("count") == 14
    assert len(body.get("agents", [])) == 14


def test_044_all_52_agents52_ids_rejected():
    """All 52 agents52 IDs return 422 on agent-run (full population check)."""
    from periphery.agents_obsidia_config_registry import list_agent_configs
    client = _agent_run_client()
    all_ids = list_agent_configs()
    assert len(all_ids) == 52
    failures = []
    for agent_id in all_ids:
        r = client.post(
            "/api/periphery/governance/agent-run",
            json={"agent_id": agent_id, "action": _AGENT_RUN_ACTION},
        )
        if r.status_code != 422:
            failures.append(f"{agent_id}: got {r.status_code}")
    assert not failures, (
        f"Agents52 IDs that did not return 422 ({len(failures)}/{len(all_ids)}): {failures}"
    )


def test_045_no_raw_exception_in_rejection_response():
    """Rejection responses contain no Python traceback or raw exception class names."""
    client = _agent_run_client()
    for agent_id, expected_status in [
        ("SECRET_GUARD", 422),
        ("NONEXISTENT_XYZ_000", 404),
    ]:
        r = client.post(
            "/api/periphery/governance/agent-run",
            json={"agent_id": agent_id, "action": _AGENT_RUN_ACTION},
        )
        assert r.status_code == expected_status
        body = r.text
        assert "Traceback" not in body, f"{agent_id}: traceback leaked in response"
        assert "KeyError" not in body, f"{agent_id}: KeyError leaked in response"
        assert "Exception" not in body, f"{agent_id}: raw Exception class in response"


# ── Batch 002 mapping (ART150 — Frise / Arbres / Monde humain) ───────────────


def test_046_batch002_five_mappings():
    """Exactly 5 entries carry the AGENTS52_BATCH002 tag."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    assert len(batch2) == 5, f"Expected 5 batch002 entries, got {len(batch2)}"


def test_047_batch002_exact_row_ids():
    """Batch002 source_row_ids match ART150 exactly: {1821, 1822, 1823, 1824, 1825}."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    row_ids = {e.source_row_id for e in batch2}
    expected = set(_ART150_ROW_MAP.keys())
    assert row_ids == expected, f"Row IDs mismatch: {row_ids} != {expected}"


def test_048_batch002_exact_agent_ids():
    """Batch002 agent_ids match ART150 names exactly."""
    batch2_ids = {
        e.agent_id for e in load_registry() if e.compilation_batch == _BATCH002_TAG
    }
    assert batch2_ids == _ART150_NAMES, f"Mismatch: {batch2_ids} != {_ART150_NAMES}"


def test_049_batch002_row_id_to_agent_exact():
    """Each batch002 entry's source_row_id → agent_id matches ART150 explicitly."""
    batch_map = {
        e.source_row_id: e.agent_id
        for e in load_registry()
        if e.compilation_batch == _BATCH002_TAG
    }
    for row_id, agent_name in _ART150_ROW_MAP.items():
        got = batch_map.get(row_id)
        assert got == agent_name, (
            f"Row {row_id}: expected {agent_name!r}, got {got!r}"
        )


def test_050_batch001_still_five_mappings():
    """Batch001 count remains exactly 5 after batch002 addition."""
    batch1 = [e for e in load_registry() if e.compilation_batch == _BATCH001_TAG]
    assert len(batch1) == 5, f"Expected 5 batch001 entries, got {len(batch1)}"


def test_051_batch001_unchanged():
    """Batch001 mapping is identical to ART118 — no entry modified or displaced."""
    batch_map = {
        e.agent_id: e.source_row_id
        for e in load_registry()
        if e.compilation_batch == _BATCH001_TAG
    }
    for row_id, agent_name in _ART118_ROW_MAP.items():
        got = batch_map.get(agent_name)
        assert got == row_id, (
            f"Batch001 regression: {agent_name} expected row {row_id!r}, got {got!r}"
        )


def test_052_no_overlap_batch001_batch002():
    """No agent_id appears in both batch001 and batch002."""
    batch1_ids = {
        e.agent_id for e in load_registry() if e.compilation_batch == _BATCH001_TAG
    }
    batch2_ids = {
        e.agent_id for e in load_registry() if e.compilation_batch == _BATCH002_TAG
    }
    overlap = batch1_ids & batch2_ids
    assert not overlap, f"Batch001/002 overlap detected: {overlap}"


def test_053_ten_technically_compiled_readonly():
    """Exactly 10 entries are technically compiled readonly (batch001 + batch002)."""
    compiled = [
        e for e in load_registry()
        if e.compilation_batch in (_BATCH001_TAG, _BATCH002_TAG)
    ]
    assert len(compiled) == 10, f"Expected 10 compiled, got {len(compiled)}"


def test_054_42_documented_source_only():
    """Exactly 42 entries remain DOCUMENTED_SOURCE_ONLY (compilation_batch=None)."""
    others = [e for e in load_registry() if e.compilation_batch is None]
    assert len(others) == 42, f"Expected 42, got {len(others)}"
    for e in others:
        assert e.compilation_status == "DOCUMENTED_SOURCE_ONLY", (
            f"{e.agent_id}: compilation_status must be DOCUMENTED_SOURCE_ONLY"
        )


def test_055_all_52_needs_human_validation():
    """All 52 entries remain NEEDS_HUMAN_VALIDATION — semantic validation not granted."""
    violations = [
        e.agent_id for e in load_registry()
        if e.validation_status != "NEEDS_HUMAN_VALIDATION"
    ]
    assert not violations, (
        f"Entries with wrong validation_status: {violations}"
    )


def test_056_batch002_non_sovereign():
    """All 5 batch002 entries have authority=NON_SOVEREIGN."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert e.authority == "NON_SOVEREIGN", (
            f"{e.agent_id}: authority must be NON_SOVEREIGN"
        )


def test_057_batch002_can_decide_false():
    """can_decide is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.can_decide, f"{e.agent_id}: can_decide must be False"


def test_058_batch002_can_act_false():
    """can_act is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.can_act, f"{e.agent_id}: can_act must be False"


def test_059_batch002_emits_act_false():
    """emits_act is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.emits_act, f"{e.agent_id}: emits_act must be False"


def test_060_batch002_memory_write_false():
    """memory_write is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.memory_write, f"{e.agent_id}: memory_write must be False"


def test_061_batch002_graphiti_write_false():
    """graphiti_write is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.graphiti_write, f"{e.agent_id}: graphiti_write must be False"


def test_062_batch002_neo4j_write_false():
    """neo4j_write is False for all 5 batch002 entries."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    for e in batch2:
        assert not e.neo4j_write, f"{e.agent_id}: neo4j_write must be False"


def test_063_no_new_file_or_component():
    """No new write, mutation, clustering, or calibration runtime functions exposed."""
    import periphery.agents_obsidia_config_registry as mod
    forbidden = [
        "write_registry", "update_agent", "delete_agent", "invoke_agent",
        "run_agent", "route_agent", "cluster_agent", "calibrate_runtime",
        "fit", "predict", "transform",
    ]
    for fn in forbidden:
        assert not hasattr(mod, fn), f"Forbidden function {fn!r} must not be exposed"


def test_064_list_api_still_52():
    """list_agent_configs still returns exactly 52 agent_id strings."""
    ids = list_agent_configs()
    assert len(ids) == 52, f"Expected 52, got {len(ids)}"
    assert len(set(ids)) == 52, "Duplicate agent_ids detected"


def test_065_frise_humaine_detail_batch002():
    """API detail for FRISE_HUMAINE returns compilation_batch=AGENTS52_BATCH002."""
    from apps.obsidia_api.routes.periphery_ops import periphery_get_agent_config
    result = asyncio.run(periphery_get_agent_config(agent_id="FRISE_HUMAINE"))
    assert result["agent_id"] == "FRISE_HUMAINE"
    assert result["compilation_batch"] == _BATCH002_TAG
    assert result["source_row_id"] == "1821"
    assert result["compilation_status"] == "DOCUMENTED_AGENT_CONFIG_REGISTERED_READONLY"
    assert result["validation_status"] == "NEEDS_HUMAN_VALIDATION"
    assert result["can_decide"] is False
    assert result["emits_act"] is False
    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"


def test_066_nuage_points_detail_row_1825():
    """API detail for NUAGE_POINTS returns source_row_id=1825 and batch002 tag."""
    from apps.obsidia_api.routes.periphery_ops import periphery_get_agent_config
    result = asyncio.run(periphery_get_agent_config(agent_id="NUAGE_POINTS"))
    assert result["agent_id"] == "NUAGE_POINTS"
    assert result["source_row_id"] == "1825"
    assert result["compilation_batch"] == _BATCH002_TAG
    assert result["can_decide"] is False
    assert result["emits_act"] is False


def test_067_batch002_ids_rejected_422():
    """All 5 batch002 agent_ids return HTTP 422 on agent-run."""
    client = _agent_run_client()
    for agent_id in sorted(_ART150_NAMES):
        r = client.post(
            "/api/periphery/governance/agent-run",
            json={"agent_id": agent_id, "action": _AGENT_RUN_ACTION},
        )
        assert r.status_code == 422, (
            f"{agent_id}: expected 422, got {r.status_code}: {r.text}"
        )
        assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in r.text, (
            f"{agent_id}: rejection detail missing from response: {r.text}"
        )


def test_068_all_52_still_rejected_422():
    """All 52 agents52 IDs still return 422 on agent-run after batch002 addition."""
    client = _agent_run_client()
    all_ids = list_agent_configs()
    assert len(all_ids) == 52
    failures = []
    for agent_id in all_ids:
        r = client.post(
            "/api/periphery/governance/agent-run",
            json={"agent_id": agent_id, "action": _AGENT_RUN_ACTION},
        )
        if r.status_code != 422:
            failures.append(f"{agent_id}: got {r.status_code}")
    assert not failures, (
        f"Agents52 IDs not returning 422 ({len(failures)}/52): {failures}"
    )


def test_069_python_operational_agent_unchanged():
    """Python operational agents endpoint still returns 14 — batch002 has no effect."""
    from apps.obsidia_api.routes.periphery_ops import periphery_list_agents
    result = asyncio.run(periphery_list_agents())
    assert result["count"] == 14, f"Expected 14 Python agents, got {result['count']}"
    assert len(result["agents"]) == 14


def test_070_deterministic_order_and_serialization():
    """list_agent_configs is sorted, reproducible, and includes all batch002 entries."""
    first = list_agent_configs()
    second = list_agent_configs()
    assert first == second, "list_agent_configs is not deterministic"
    assert first == sorted(first), "list_agent_configs is not sorted"
    assert len(first) == 52
    for name in _ART150_NAMES:
        assert name in first, f"Batch002 agent {name!r} missing from list_agent_configs"


def test_071_json_source_unchanged():
    """Source registry JSON is not modified by batch002 registry mutation."""
    path = _registry_path()
    sha_before = hashlib.sha256(path.read_bytes()).hexdigest()
    load_registry()
    sha_after = hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha_before == sha_after, (
        f"Source JSON modified: before={sha_before} after={sha_after}"
    )


def test_072_no_new_route():
    """Batch002 agents are served by the existing generic /agents-52 endpoint."""
    client = _agent_run_client()
    r = client.get("/api/periphery/governance/agents-52")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 52
    for name in _ART150_NAMES:
        assert name in body["agents"], (
            f"Batch002 agent {name!r} missing from /agents-52 response"
        )


def test_073_no_model_call_in_registry_source():
    """Registry source contains no LLM/model/clustering invocation symbols."""
    import periphery.agents_obsidia_config_registry as mod
    source = inspect.getsource(mod)
    forbidden_symbols = [
        "openai", "anthropic", "vertexai", "litellm",
        "call_model", "invoke_model", "chat.complete",
        "GenerativeModel", "cluster(", ".fit(", ".predict(",
    ]
    for sym in forbidden_symbols:
        assert sym not in source, (
            f"Forbidden symbol {sym!r} found in registry source after batch002"
        )


def test_074_no_memory_write_in_registry_source():
    """Registry source contains no memory/graphiti/neo4j write call symbols."""
    import periphery.agents_obsidia_config_registry as mod
    source = inspect.getsource(mod)
    # Target write call patterns — not field names (neo4j_write is a field, not a call)
    write_call_symbols = [
        "graphiti.add", "GraphDatabase", "neo4j.driver", "neo4j.connect",
        "memory.write", "write_to", "db.commit", "session.add", "session.run(",
    ]
    for sym in write_call_symbols:
        assert sym not in source, (
            f"Write call symbol {sym!r} found in registry source after batch002"
        )


def test_075_no_decision_or_act_emission():
    """Batch002: readonly=True, non_decision=True, all ACT/decide flags False."""
    batch2 = [e for e in load_registry() if e.compilation_batch == _BATCH002_TAG]
    assert len(batch2) == 5, f"Expected 5 batch002 entries, got {len(batch2)}"
    for e in batch2:
        assert e.readonly is True, f"{e.agent_id}: readonly must be True"
        assert e.non_decision is True, f"{e.agent_id}: non_decision must be True"
        assert e.emits_act is False, f"{e.agent_id}: emits_act must be False"
        assert e.can_decide is False, f"{e.agent_id}: can_decide must be False"
        assert e.can_act is False, f"{e.agent_id}: can_act must be False"
        assert e.memory_write is False, f"{e.agent_id}: memory_write must be False"
