"""
tests/test_capability_graph_create_dir_p1.py
=============================================
P1 remediation tests: register CREATE_DIR V2 capabilities in the
canonical capability graph and V2 self-check surface.

RED baseline (pre-fix): PC_V2_CREATE_DIR_PREPARE / PC_V2_CREATE_DIR_EXECUTE
  were absent from _GRAPH, _KIND_TO_CAPABILITY, and _CAPABILITY_IDS_V2.

GREEN (post-fix): both capabilities fully registered, Relay resolution works,
  V2 self-check aligned. Other ops unchanged. Unknown kinds still fail closed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
for _p in (str(_SCRIPTS),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_capability_graph_v0 as G   # noqa: E402
import obsidia_pc_capabilities_v2 as PC2  # noqa: E402


# ── Graph registration ────────────────────────────────────────────────────

def test_create_dir_prepare_registered():
    assert "PC_V2_CREATE_DIR_PREPARE" in G.capability_ids()


def test_create_dir_execute_registered():
    assert "PC_V2_CREATE_DIR_EXECUTE" in G.capability_ids()


def test_create_dir_prepare_schema():
    c = G.get_capability("PC_V2_CREATE_DIR_PREPARE")
    assert c is not None
    assert c["route"] == "STACK_NATIVE_ROUTE"
    assert c["authority_class"] == "KX108_ONLY"
    assert c["read_write"] == "NONE"
    assert c["mode"] == "GOVERNED_RAIL"
    assert c["is_execution_authority"] is False
    assert c["grants_authority"] is False
    assert "dir_path" in c["accepted_input_shape"]


def test_create_dir_execute_schema():
    c = G.get_capability("PC_V2_CREATE_DIR_EXECUTE")
    assert c is not None
    assert c["route"] == "STAGE4_GOVERNED_RAIL"
    assert c["authority_class"] == "KX108_ONLY"
    assert c["read_write"] == "WRITE_GOVERNED"
    assert c["mode"] == "GOVERNED_RAIL"
    assert c["is_execution_authority"] is False
    assert c["grants_authority"] is False
    assert "prepared_result" in c["accepted_input_shape"]


# ── Relay resolution ──────────────────────────────────────────────────────

def test_relay_resolves_create_dir_prepare():
    r = G.resolve_capability_for_kind("PC_V2_CREATE_DIR_PREPARE")
    assert r["capability_id"] == "PC_V2_CREATE_DIR_PREPARE"
    assert r["grants_authority"] is False
    assert "gap" not in r


def test_relay_resolves_create_dir_execute():
    r = G.resolve_capability_for_kind("PC_V2_CREATE_DIR_EXECUTE")
    assert r["capability_id"] == "PC_V2_CREATE_DIR_EXECUTE"
    assert r["grants_authority"] is False
    assert "gap" not in r


def test_unknown_kind_still_fail_closed():
    gap = G.resolve_capability_for_kind("SOMETHING_NOT_REGISTERED_XYZ")
    assert gap["gap"] == "STACK_NATIVE_CAPABILITY_GAP"
    assert gap["capability_id"] is None
    assert gap["route"] == "HOLD"
    assert gap["authority_class"] == "HUMAN"


# ── V2 self-check alignment ───────────────────────────────────────────────

def test_v2_self_check_includes_create_dir_capabilities():
    sc = PC2.self_check_v2()
    caps = sc["capabilities"]
    assert "PC_V2_CREATE_DIR_PREPARE" in caps
    assert "PC_V2_CREATE_DIR_EXECUTE" in caps


def test_v2_self_check_includes_create_dir_operation():
    sc = PC2.self_check_v2()
    assert "V2_CREATE_DIR" in sc["operations"]


# ── Regression: other ops unchanged ──────────────────────────────────────

@pytest.mark.parametrize("cid", [
    "PC_V2_CREATE_FILE_PREPARE", "PC_V2_CREATE_FILE_EXECUTE",
    "PC_V2_MOVE_FILE_PREPARE",   "PC_V2_MOVE_FILE_EXECUTE",
    "PC_V2_APPLY_PATCH_PREPARE", "PC_V2_APPLY_PATCH_EXECUTE",
])
def test_existing_v2_capabilities_unchanged(cid):
    assert G.get_capability(cid) is not None
    sc = PC2.self_check_v2()
    assert cid in sc["capabilities"]


def test_graph_not_authority_after_patch():
    assert G.CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY is False
    assert G.CAPABILITY_GRAPH_IS_KX_AUTHORITY is False
    snap = G.graph_snapshot()
    assert snap["is_execution_authority"] is False
    assert snap["is_kx_authority"] is False
    for cap in snap["capabilities"].values():
        assert cap["grants_authority"] is False
        assert cap["is_execution_authority"] is False
