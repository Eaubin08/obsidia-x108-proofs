"""
Tests for periphery.agents_obsidia_config_registry — Batch 001.

PHASE: AGENTS52_READONLY_REGISTRY_ADAPTER_BATCH001_001
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
    _registry_path,
    get_agent_config,
    get_registry_provenance,
    list_agent_configs,
    list_agents_by_family,
    load_registry,
    validate_registry,
)

# ART118 reference data — single source of truth for batch mapping verification
_ART118_ROW_MAP = {
    "1811": "SECURITY_FIREWALL_ARCHITECT",
    "1812": "POLICY_FIREWALL_AGENT",
    "1813": "RUNTIME_ATTESTATION_AGENT",
    "1814": "SUPPLY_CHAIN_GUARD",
    "1815": "SECRET_GUARD",
}
_ART118_NAMES = set(_ART118_ROW_MAP.values())
_SECURITY_FAMILY = "Sécurité / Pare-feu"


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


def test_010_other_47_documented_source_only():
    """47 non-batch entries have compilation_batch=None and DOCUMENTED_SOURCE_ONLY."""
    others = [e for e in load_registry() if e.compilation_batch != _BATCH001_TAG]
    assert len(others) == 47, f"Expected 47, got {len(others)}"
    for e in others:
        assert e.compilation_batch is None, f"{e.agent_id}: batch should be None"
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
