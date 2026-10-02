from __future__ import annotations
"""tests/test_h1_red.py -- RED tests proving H1 contract gap.

These tests assert the NEW correct behavior. They FAIL before H1 is applied
and PASS after H1 is applied.
"""
import hashlib, json, sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
SIGMA    = WORKTREE / "sigma"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(WORKTREE) not in sys.path:
    sys.path.insert(0, str(WORKTREE))

import obsidia_pc_capabilities_v2 as PC2
from sigma.contracts import ToolingBuildState
from sigma.domains.tooling_build_agents import SessionIntegrityAgent

_HWND  = 12345
_TITLE = "Test Window - Chrome"
_REQ   = "Chrome"


def _ok():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "NativeWindowsBackend"
    ex.find_window.return_value        = {"ok": True, "hwnd": _HWND, "title": _TITLE}
    ex.focus_window_by_hwnd.return_value = {"ok": True, "hwnd": _HWND, "title": _TITLE}
    ex.verify_focus.return_value       = {"ok": True, "hwnd": _HWND, "title": _TITLE, "title_consistent": True}
    return ex


# ---- A: ToolingBuildState has canonical physical anchor field -------------------

def test_red_A_tooling_build_state_has_physical_anchor():
    """After H1: ToolingBuildState must expose physical_state_anchor and state_anchor_kind."""
    state = ToolingBuildState(
        session_id="test-h1",
        physical_state_anchor="a" * 64,
        state_anchor_kind="PHYSICAL_PRE_STATE",
    )
    # RED before H1: AttributeError or default "" overrides kwarg
    assert state.physical_state_anchor == "a" * 64
    assert state.state_anchor_kind == "PHYSICAL_PRE_STATE"


def test_red_A_default_state_anchor_kind_is_git_head():
    """After H1: default state_anchor_kind must be GIT_HEAD for backward compat."""
    state = ToolingBuildState(session_id="test-h1-default")
    assert state.state_anchor_kind == "GIT_HEAD"
    assert state.physical_state_anchor == ""


# ---- B: SessionIntegrityAgent dispatches correctly on state_anchor_kind ---------

def test_red_B_physical_pre_state_valid_anchor_no_base_sha_missing(tmp_path):
    """After H1: PHYSICAL_PRE_STATE + valid PSA must NOT produce BASE_SHA_MISSING."""
    state = ToolingBuildState(
        session_id="test-b",
        base_sha="",
        physical_state_anchor="b" * 64,
        state_anchor_kind="PHYSICAL_PRE_STATE",
        manifest_hash="c" * 16,
        worktree_isolated=True,
        branch_isolated=True,
        human_approval_status="APPROVED",
    )
    agent = SessionIntegrityAgent()
    vote = agent.evaluate(state)
    # RED before H1: BASE_SHA_MISSING is in vote.unknowns (old code ignores kind)
    assert "BASE_SHA_MISSING" not in vote.unknowns


def test_red_B_physical_pre_state_empty_anchor_produces_hold():
    """After H1: PHYSICAL_PRE_STATE + empty PSA must produce HOLD with PHYSICAL_STATE_ANCHOR_MISSING."""
    state = ToolingBuildState(
        session_id="test-b-empty",
        base_sha="",
        physical_state_anchor="",
        state_anchor_kind="PHYSICAL_PRE_STATE",
        manifest_hash="d" * 16,
        worktree_isolated=True,
        branch_isolated=True,
        human_approval_status="APPROVED",
    )
    agent = SessionIntegrityAgent()
    vote = agent.evaluate(state)
    # RED before H1: BASE_SHA_MISSING instead of PHYSICAL_STATE_ANCHOR_MISSING
    assert "PHYSICAL_STATE_ANCHOR_MISSING" in vote.unknowns


def test_red_B_unknown_anchor_kind_produces_hold():
    """After H1: unknown state_anchor_kind must produce STATE_ANCHOR_KIND_UNKNOWN."""
    state = ToolingBuildState(
        session_id="test-b-unknown",
        base_sha="",
        state_anchor_kind="INVENTED_KIND",
        manifest_hash="e" * 16,
        worktree_isolated=True,
        branch_isolated=True,
        human_approval_status="APPROVED",
    )
    agent = SessionIntegrityAgent()
    vote = agent.evaluate(state)
    # RED before H1: BASE_SHA_MISSING instead of STATE_ANCHOR_KIND_UNKNOWN
    assert "STATE_ANCHOR_KIND_UNKNOWN" in vote.unknowns


def test_red_B_git_head_no_base_sha_still_produces_base_sha_missing():
    """GIT_HEAD kind without base_sha must still produce BASE_SHA_MISSING (backward compat)."""
    state = ToolingBuildState(
        session_id="test-b-git",
        base_sha="",
        state_anchor_kind="GIT_HEAD",
        manifest_hash="f" * 16,
        worktree_isolated=True,
        branch_isolated=True,
        human_approval_status="APPROVED",
    )
    agent = SessionIntegrityAgent()
    vote = agent.evaluate(state)
    assert "BASE_SHA_MISSING" in vote.unknowns


# ---- C + D: window.focus base_sha != EAH after H1 ----------------------------

def test_red_C_window_focus_base_sha_not_equal_eah(tmp_path):
    """After H1: _kx108_pre for WINDOW_FOCUS must receive base_sha='' not base_sha=EAH."""
    captured = {}
    orig_kx = PC2._kx108_pre

    def _capture_kx(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, *, kxpre, **kwargs):
        captured["base_sha"] = base_sha
        captured["eah"] = eah
        return orig_kx(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, kxpre=kxpre, **kwargs)

    PC2._kx108_pre = _capture_kx
    try:
        ex = _ok()
        prep = PC2.pc_v2_window_focus_prepare(_REQ, stores_base_dir=tmp_path / "stores", executor=ex)
        assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
        eah = prep["execution_authority_hash"]
        result = PC2.pc_v2_window_focus_execute(
            prep, eah, "human-ref",
            stores_base_dir=tmp_path / "stores", executor=ex)
        assert result["status"] == PC2.EXECUTED_OK
        # RED before H1: base_sha == eah (the workaround)
        assert captured.get("base_sha") != captured.get("eah"), \
            f"base_sha must not equal EAH after H1; got base_sha={captured.get('base_sha')!r}"
        assert captured.get("base_sha") == "", \
            f"base_sha must be empty string for PHYSICAL_PRE_STATE; got {captured.get('base_sha')!r}"
    finally:
        PC2._kx108_pre = orig_kx


def test_red_D_prepare_physical_anchor_independent_from_eah(tmp_path):
    """After H1: physical_state_anchor in PREPARE result must differ from EAH."""
    ex = _ok()
    prep = PC2.pc_v2_window_focus_prepare(_REQ, stores_base_dir=tmp_path / "stores", executor=ex)
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah  = prep["execution_authority_hash"]
    # RED before H1: physical_state_anchor field does not exist
    psa  = prep.get("physical_state_anchor", "NOT_PRESENT")
    assert psa != "NOT_PRESENT", "physical_state_anchor must be present in PREPARE result after H1"
    assert psa != eah, f"physical_state_anchor must be independent from EAH; both={eah!r}"
    assert len(psa) == 64, f"physical_state_anchor must be 64-hex SHA-256; got {psa!r}"


def test_red_D_prepare_state_anchor_kind_is_physical(tmp_path):
    """After H1: PREPARE result must contain state_anchor_kind=PHYSICAL_PRE_STATE."""
    ex = _ok()
    prep = PC2.pc_v2_window_focus_prepare(_REQ, stores_base_dir=tmp_path / "stores", executor=ex)
    # RED before H1: field not present
    assert prep.get("state_anchor_kind") == "PHYSICAL_PRE_STATE"
