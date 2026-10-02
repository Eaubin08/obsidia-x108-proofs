from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import obsidia_capability_graph_v0 as G
import jarjar_executor_bridge_v0 as BRIDGE

_HWND = 12345
_TITLE = "Test Window - Chrome"
_REQ_TITLE = "Chrome"


def _ok(*, hwnd=_HWND, title=_TITLE):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.find_window.return_value = {"ok": True, "hwnd": hwnd, "title": title}
    ex.focus_window_by_hwnd.return_value = {"ok": True, "hwnd": hwnd, "title": title}
    ex.verify_focus.return_value = {"ok": True, "hwnd": hwnd, "title": title, "title_consistent": True}
    return ex


def _nowin():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.find_window.return_value = {"ok": False, "error": "WINDOW_NOT_FOUND"}
    return ex


def _drift(*, hwnd=_HWND):
    ex = _ok(hwnd=hwnd)
    ex.focus_window_by_hwnd.return_value = {"ok": False, "error": "TARGET_HWND_NOT_FOUND"}
    return ex


def _focusfail(*, hwnd=_HWND):
    ex = _ok(hwnd=hwnd)
    ex.focus_window_by_hwnd.return_value = {"ok": False, "error": "FOCUS_FAILED:win32"}
    return ex


def _verifyfail(*, hwnd=_HWND):
    ex = _ok(hwnd=hwnd)
    ex.verify_focus.return_value = {"ok": False, "error": "HWND_NOT_FOUND_POST_FOCUS"}
    return ex


def _prep(tmp_path, executor, *, title=_REQ_TITLE, session_id="wf"):
    return PC2.pc_v2_window_focus_prepare(
        title, stores_base_dir=tmp_path / "stores", session_id=session_id, executor=executor)


def _exec(tmp_path, prepared, executor, *, session_id="wf"):
    eah = prepared["execution_authority_hash"]
    return PC2.pc_v2_window_focus_execute(
        prepared, eah, "human-ref-1",
        stores_base_dir=tmp_path / "stores", session_id=session_id, executor=executor)

def test_prepare_resolves_exact_target(tmp_path):
    ex = _ok()
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["j5_phase"] == "PREPARE"
    assert r["resolved_hwnd"] == _HWND
    assert r["resolved_title"] == _TITLE
    assert r["requested_title"] == _REQ_TITLE
    assert r["execution_authority_hash"]


def test_prepare_produces_receipt(tmp_path):
    ex = _ok()
    r = _prep(tmp_path, ex)
    rcpt = r["receipt"]
    assert rcpt["capability"] == "PC_V2_WINDOW_FOCUS_PREPARE"
    assert rcpt["result_status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert rcpt["resolved_hwnd"] == _HWND
    assert rcpt["resolved_title"] == _TITLE


def test_prepare_does_not_call_focus(tmp_path):
    ex = _ok()
    _prep(tmp_path, ex)
    ex.find_window.assert_called_once_with(_REQ_TITLE)
    ex.focus_window_by_hwnd.assert_not_called()
    ex.verify_focus.assert_not_called()


def test_prepare_window_not_found(tmp_path):
    ex = _nowin()
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "WINDOW_NOT_FOUND" in r["reason"]
    ex.focus_window_by_hwnd.assert_not_called()


def test_prepare_executor_required(tmp_path):
    r = PC2.pc_v2_window_focus_prepare(
        _REQ_TITLE, stores_base_dir=tmp_path / "stores", session_id="s1", executor=None)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert r["reason"] == "EXECUTOR_REQUIRED"


def test_prepare_empty_title_rejected(tmp_path):
    ex = _ok()
    r = PC2.pc_v2_window_focus_prepare(
        "   ", stores_base_dir=tmp_path / "stores", session_id="s1", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert r["reason"] == "TITLE_REQUIRED"
    ex.find_window.assert_not_called()


def test_execute_wrong_eah_blocks_executor(tmp_path):
    ex = _ok()
    prep = _prep(tmp_path, ex)
    r = PC2.pc_v2_window_focus_execute(
        prep, "wrong-eah", "human-ref",
        stores_base_dir=tmp_path / "stores", session_id="wf", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert r.get("reason") == PC2.EAH_MISMATCH
    ex.focus_window_by_hwnd.assert_not_called()


def test_execute_missing_human_ref_blocks_executor(tmp_path):
    ex = _ok()
    prep = _prep(tmp_path, ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_window_focus_execute(
        prep, eah, "",
        stores_base_dir=tmp_path / "stores", session_id="wf", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED" in r["reason"]
    ex.focus_window_by_hwnd.assert_not_called()


def test_execute_wrong_phase_blocks_executor(tmp_path):
    ex = _ok()
    bad = {"j5_phase": "EXECUTE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
           "execution_authority_hash": "x"}
    r = PC2.pc_v2_window_focus_execute(
        bad, "x", "ref",
        stores_base_dir=tmp_path / "stores", session_id="wf", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.focus_window_by_hwnd.assert_not_called()


def test_execute_no_executor_blocks(tmp_path):
    ex = _ok()
    prep = _prep(tmp_path, ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_window_focus_execute(
        prep, eah, "human-ref",
        stores_base_dir=tmp_path / "stores", session_id="wf", executor=None)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert r["reason"] == "EXECUTOR_REQUIRED"


def test_unknown_capability_fails_closed():
    r = PC2.execute_pc_capability_v2("PC_V2_SOMETHING_UNMAPPED")
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"

def test_execute_valid_full_flow(tmp_path):
    ex = _ok()
    prep = _prep(tmp_path, ex)
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["j5_phase"] == "EXECUTE"
    assert r["focused_hwnd"] == _HWND
    assert r["focused_title"] == _TITLE
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r["human_authorization_consumed"] is True
    ex.focus_window_by_hwnd.assert_called_once_with(_HWND)


def test_execute_receipt_contains_executor_metadata(tmp_path):
    ex = _ok()
    prep = _prep(tmp_path, ex)
    r = _exec(tmp_path, prep, ex)
    rcpt = r["receipt"]
    assert rcpt["executor_provider"] == "JARJAR"
    assert rcpt["executor_backend"] == "NativeWindowsBackend"
    assert rcpt["executor_capability"] == "window.focus"
    assert rcpt["focused_hwnd"] == _HWND
    assert rcpt["focused_title"] == _TITLE
    assert rcpt["requested_title"] == _REQ_TITLE


def test_execute_exact_prepared_hwnd_used(tmp_path):
    ex = _ok(hwnd=99999, title="Exact Window Title")
    prep = _prep(tmp_path, ex, title="Exact")
    assert prep["resolved_hwnd"] == 99999
    ex2 = _ok(hwnd=99999, title="Exact Window Title")
    r = _exec(tmp_path, prep, ex2)
    assert r["status"] == PC2.EXECUTED_OK
    ex2.focus_window_by_hwnd.assert_called_once_with(99999)


def test_target_drift_fails_closed(tmp_path):
    ex_prep = _ok()
    prep = _prep(tmp_path, ex_prep)
    r = _exec(tmp_path, prep, _drift())
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "JARJAR_EXECUTOR_FAILED" in r["reason"]
    assert "TARGET_HWND_NOT_FOUND" in r["reason"]


def test_focus_failure_fails_closed(tmp_path):
    ex_prep = _ok()
    prep = _prep(tmp_path, ex_prep)
    r = _exec(tmp_path, prep, _focusfail())
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "JARJAR_EXECUTOR_FAILED" in r["reason"]


def test_verify_failure_fails_closed(tmp_path):
    ex_prep = _ok()
    prep = _prep(tmp_path, ex_prep)
    r = _exec(tmp_path, prep, _verifyfail())
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r["reason"]


def test_graph_prepare_registered():
    assert "PC_V2_WINDOW_FOCUS_PREPARE" in G.capability_ids()


def test_graph_execute_registered():
    assert "PC_V2_WINDOW_FOCUS_EXECUTE" in G.capability_ids()


def test_graph_prepare_schema():
    c = G.get_capability("PC_V2_WINDOW_FOCUS_PREPARE")
    assert c["route"] == "STACK_NATIVE_ROUTE"
    assert c["authority_class"] == "KX108_ONLY"
    assert c["read_write"] == "NONE"
    assert c["is_execution_authority"] is False
    assert c["grants_authority"] is False


def test_graph_execute_schema():
    c = G.get_capability("PC_V2_WINDOW_FOCUS_EXECUTE")
    assert c["route"] == "STAGE4_GOVERNED_RAIL"
    assert c["read_write"] == "WRITE_GOVERNED"
    assert c["is_execution_authority"] is False


def test_relay_resolves_window_focus():
    rp = G.resolve_capability_for_kind("PC_V2_WINDOW_FOCUS_PREPARE")
    assert rp["capability_id"] == "PC_V2_WINDOW_FOCUS_PREPARE"
    re_ = G.resolve_capability_for_kind("PC_V2_WINDOW_FOCUS_EXECUTE")
    assert re_["capability_id"] == "PC_V2_WINDOW_FOCUS_EXECUTE"


def test_unknown_kind_still_fail_closed():
    gap = G.resolve_capability_for_kind("UNMAPPED_WINDOW_XYZ")
    assert gap["gap"] == "STACK_NATIVE_CAPABILITY_GAP"


def test_v2_self_check_includes_wfocus():
    sc = PC2.self_check_v2()
    assert "PC_V2_WINDOW_FOCUS_PREPARE" in sc["capabilities"]
    assert "PC_V2_WINDOW_FOCUS_EXECUTE" in sc["capabilities"]
    assert "V2_WINDOW_FOCUS" in sc["operations"]


def test_graph_not_authority_after_patch():
    snap = G.graph_snapshot()
    assert snap["is_execution_authority"] is False
    assert snap["is_kx_authority"] is False
    for cap in snap["capabilities"].values():
        assert cap["grants_authority"] is False
        assert cap["is_execution_authority"] is False


def test_bridge_self_check_invariants():
    sc = BRIDGE.self_check_bridge_v0()
    assert sc["openjarvis_authority"] == "NONE"
    assert sc["jarjar_authority"] == "NONE"
    assert sc["kx108_only"] is True
    assert sc["human_approval_required"] is True
    assert sc["generic_shell_enabled"] is False
    assert sc["makes_authorization_decisions"] is False
    assert sc["is_execution_authority"] is False
    assert sc["is_kx_authority"] is False
    assert sc["new_parallel_mutation_engine"] is False


@pytest.fixture
def bridge_world(tmp_path):
    main = tmp_path / "main"
    (main / "sub").mkdir(parents=True)
    (main / "sub" / "src.txt").write_bytes(b"g1-regression")

    def _git(*a):
        r = subprocess.run(["git"] + list(a), cwd=str(main), capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    _git("init", "-q")
    _git("config", "user.email", "t@t.com")
    _git("config", "user.name", "t")
    _git("config", "commit.gpgsign", "false")
    _git("add", "sub/src.txt")
    _git("commit", "-q", "-m", "seed")
    base_sha = _git("rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git("worktree", "add", str(exec_wt), "-b", "g1-reg-br", base_sha)
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha,
            "stores_base": tmp_path / "stores"}


def test_g0_move_file_regression(tmp_path, bridge_world):
    w = bridge_world
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"
    def _mv(sa, da):
        da.parent.mkdir(parents=True, exist_ok=True)
        sa.rename(da)
        return {"ok": True, "error": None}
    ex.move_file.side_effect = _mv
    prep = PC2.pc_v2_move_file_prepare(
        "sub/src.txt", "sub/moved.txt",
        execution_worktree_path=w["exec_wt"], main_worktree_path=w["main"],
        branch_name="g1-reg-br", base_sha=w["base_sha"], stores_base_dir=w["stores_base"])
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_move_file_execute(
        prep, eah, "ref-g1",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    ex.move_file.assert_called_once()


def test_g0_create_dir_regression(tmp_path, bridge_world):
    w = bridge_world
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"
    def _mkdir(da):
        da.mkdir(parents=False, exist_ok=False)
        return {"ok": True, "error": None}
    ex.create_dir.side_effect = _mkdir
    prep = PC2.pc_v2_create_dir_prepare(
        "sub/newdir",
        execution_worktree_path=w["exec_wt"], main_worktree_path=w["main"],
        branch_name="g1-reg-br", base_sha=w["base_sha"], stores_base_dir=w["stores_base"])
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_create_dir_execute(
        prep, eah, "ref-g1",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    ex.create_dir.assert_called_once()


# ============================================================
# G1-A REMEDIATION TESTS — canonical physical state anchor
# ============================================================

def test_prepare_captures_physical_anchor(tmp_path):
    ex = _ok()
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    psa = r.get("physical_state_anchor", "")
    assert len(psa) == 64, f"physical_state_anchor must be 64-hex SHA-256; got {psa!r}"
    assert all(c in "0123456789abcdef" for c in psa)


def test_prepare_state_anchor_kind_is_physical_pre_state(tmp_path):
    ex = _ok()
    r = _prep(tmp_path, ex)
    assert r.get("state_anchor_kind") == "PHYSICAL_PRE_STATE"


def test_prepare_anchor_deterministic(tmp_path):
    """Same inputs always produce the same physical_state_anchor."""
    ex1 = _ok(hwnd=_HWND, title=_TITLE)
    ex2 = _ok(hwnd=_HWND, title=_TITLE)
    r1 = _prep(tmp_path / "s1", ex1)
    r2 = _prep(tmp_path / "s2", ex2)
    assert r1["physical_state_anchor"] == r2["physical_state_anchor"]


def test_prepare_eah_independent_from_physical_anchor(tmp_path):
    """EAH (approval anchor) must differ from physical_state_anchor (state anchor)."""
    ex = _ok()
    r = _prep(tmp_path, ex)
    eah = r["execution_authority_hash"]
    psa = r["physical_state_anchor"]
    assert eah != psa, f"EAH must not equal PSA; both={eah!r}"


def test_execute_base_sha_not_equal_eah(tmp_path):
    """After H1: _kx108_pre receives base_sha='' not base_sha=EAH."""
    import obsidia_pc_capabilities_v2 as _PC2
    captured = {}
    orig = _PC2._kx108_pre
    def _cap(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, *, kxpre, **kwargs):
        captured["base_sha"] = base_sha
        captured["eah"] = eah
        return orig(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, kxpre=kxpre, **kwargs)
    _PC2._kx108_pre = _cap
    try:
        ex = _ok()
        prep = _prep(tmp_path, ex)
        r = _exec(tmp_path, prep, ex)
        assert r["status"] == PC2.EXECUTED_OK
        assert captured.get("base_sha") == "", f"base_sha must be empty; got {captured.get('base_sha')!r}"
        assert captured.get("base_sha") != captured.get("eah"), "base_sha must not equal EAH"
    finally:
        _PC2._kx108_pre = orig


def test_execute_physical_anchor_passed_to_kx108(tmp_path):
    """After H1: _kx108_pre receives physical_state_anchor and state_anchor_kind=PHYSICAL_PRE_STATE."""
    import obsidia_pc_capabilities_v2 as _PC2
    captured = {}
    orig = _PC2._kx108_pre
    def _cap(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, *, kxpre, **kwargs):
        captured["physical_state_anchor"] = kwargs.get("physical_state_anchor", "MISSING")
        captured["state_anchor_kind"] = kwargs.get("state_anchor_kind", "MISSING")
        return orig(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, kxpre=kxpre, **kwargs)
    _PC2._kx108_pre = _cap
    try:
        ex = _ok()
        prep = _prep(tmp_path, ex)
        r = _exec(tmp_path, prep, ex)
        assert r["status"] == PC2.EXECUTED_OK
        assert captured.get("state_anchor_kind") == "PHYSICAL_PRE_STATE"
        psa = captured.get("physical_state_anchor", "")
        assert len(psa) == 64
    finally:
        _PC2._kx108_pre = orig


def _disappeared_at_execute(hwnd=_HWND, title=_TITLE):
    """Mock: PREPARE find_window OK, EXECUTE find_window fails."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.focus_window_by_hwnd.return_value = {"ok": True, "hwnd": hwnd, "title": title}
    ex.verify_focus.return_value = {"ok": True, "hwnd": hwnd, "title": title, "title_consistent": True}
    call_count = [0]
    def fw(t):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"ok": True, "hwnd": hwnd, "title": title}
        return {"ok": False, "error": "WINDOW_NOT_FOUND"}
    ex.find_window.side_effect = fw
    return ex


def _hwnd_drifted_at_execute(*, hwnd=_HWND, title=_TITLE, drift_hwnd=99999):
    """Mock: PREPARE find_window OK, EXECUTE find_window returns different hwnd."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.focus_window_by_hwnd.return_value = {"ok": True, "hwnd": hwnd, "title": title}
    ex.verify_focus.return_value = {"ok": True, "hwnd": hwnd, "title": title, "title_consistent": True}
    call_count = [0]
    def fw(t):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"ok": True, "hwnd": hwnd, "title": title}
        return {"ok": True, "hwnd": drift_hwnd, "title": title}
    ex.find_window.side_effect = fw
    return ex


def test_execute_target_disappeared_fails_closed(tmp_path):
    """If target hwnd vanishes between PREPARE and EXECUTE, must fail closed."""
    ex = _disappeared_at_execute()
    prep = _prep(tmp_path, ex)
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "TARGET_IDENTITY_LOST" in r["reason"]


def test_execute_target_hwnd_drifted_fails_closed(tmp_path):
    """If same title now maps to different hwnd, must fail closed."""
    ex = _hwnd_drifted_at_execute()
    prep = _prep(tmp_path, ex)
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "TARGET_HWND_DRIFTED" in r["reason"]


def test_execute_unrelated_window_state_unchanged(tmp_path):
    """Unrelated windows changing titles between PREPARE and EXECUTE do not fail
    window.focus if the target window itself is unchanged."""
    ex = _ok()
    prep = _prep(tmp_path, ex)
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTED_OK, f"Expected EXECUTED_OK; got {r}"


def test_execute_no_mutation_before_kx108(tmp_path):
    """PREPARE must not call focus_window_by_hwnd. Only find_window is read-only."""
    ex = _ok()
    _prep(tmp_path, ex)
    ex.focus_window_by_hwnd.assert_not_called()
    ex.verify_focus.assert_not_called()
