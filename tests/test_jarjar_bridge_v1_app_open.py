from __future__ import annotations
import hashlib, os, sys
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

_APP_NAME   = "notepad"
_APP_TARGET = "notepad.exe"
_APP_SOURCE = "builtin"
_LNK_NAME   = "chrome"
_LNK_TARGET = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Google Chrome.lnk"
_LNK_SOURCE = "start_menu"


def _ok_exe(*, app=_APP_NAME, name=_APP_NAME, target=_APP_TARGET, source=_APP_SOURCE, pid=None):
    if pid is None:
        pid = os.getpid()
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {"ok": True, "name": name, "target": target, "source": source}
    ex.open_app_by_target.return_value = {"ok": True, "pid": pid, "target": target, "source": source}
    return ex


def _ok_lnk():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {"ok": True, "name": "Google Chrome", "target": _LNK_TARGET, "source": _LNK_SOURCE}
    ex.open_app_by_target.return_value = {"ok": True, "pid": None, "target": _LNK_TARGET, "source": _LNK_SOURCE}
    return ex


def _unresolved():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {"ok": False, "error": "APP_NOT_IN_INVENTORY"}
    return ex


def _failed_launch():
    ex = _ok_exe()
    ex.open_app_by_target.return_value = {"ok": False, "error": "APP_OPEN_FAILED:backend_error"}
    return ex


def _prep(tmp_path, executor, *, app=_APP_NAME, session_id="ao"):
    return PC2.pc_v2_app_open_prepare(
        app, stores_base_dir=tmp_path / "stores", session_id=session_id, executor=executor)


def _exec(tmp_path, prepared, executor, *, session_id="ao"):
    eah = prepared["execution_authority_hash"]
    return PC2.pc_v2_app_open_execute(
        prepared, eah, "human-ref-ao-1",
        stores_base_dir=tmp_path / "stores", session_id=session_id, executor=executor)


# A. graphe + dispatcher
def test_a_app_open_in_capability_graph():
    ids = G.capability_ids()
    assert "PC_V2_APP_OPEN_PREPARE" in ids
    assert "PC_V2_APP_OPEN_EXECUTE" in ids

def test_a_app_open_in_self_check():
    sc = PC2.self_check_v2()
    assert "PC_V2_APP_OPEN_PREPARE" in sc["capabilities"]
    assert "PC_V2_APP_OPEN_EXECUTE" in sc["capabilities"]
    assert PC2.OP_APP_OPEN in sc["operations"]


# B. PREPARE lifecycle
def test_b_prepare_resolves_app(tmp_path):
    ex = _ok_exe()
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["j5_phase"] == "PREPARE"
    assert r["requested_app"] == _APP_NAME
    assert r["resolved_target"] == _APP_TARGET
    assert r["resolved_source"] == _APP_SOURCE

def test_b_prepare_calls_resolve_not_open(tmp_path):
    ex = _ok_exe()
    _prep(tmp_path, ex)
    ex.resolve_app.assert_called_once_with(_APP_NAME)
    ex.open_app_by_target.assert_not_called()

def test_b_prepare_psa_64hex(tmp_path):
    r = _prep(tmp_path, _ok_exe())
    psa = r.get("physical_state_anchor", "")
    assert len(psa) == 64 and all(c in "0123456789abcdef" for c in psa)

def test_b_prepare_psa_independent_from_eah(tmp_path):
    r = _prep(tmp_path, _ok_exe())
    assert r["physical_state_anchor"] != r["execution_authority_hash"]

def test_b_prepare_state_anchor_kind_physical(tmp_path):
    r = _prep(tmp_path, _ok_exe())
    assert r["state_anchor_kind"] == "PHYSICAL_PRE_STATE"

def test_b_prepare_anchor_deterministic(tmp_path):
    r1 = _prep(tmp_path, _ok_exe())
    r2 = PC2.pc_v2_app_open_prepare(
        _APP_NAME, stores_base_dir=tmp_path / "stores2", session_id="ao", executor=_ok_exe())
    assert r1["physical_state_anchor"] == r2["physical_state_anchor"]

def test_b_prepare_without_executor_rejected():
    r = PC2.pc_v2_app_open_prepare("notepad", stores_base_dir="/s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r["reason"]

def test_b_prepare_empty_app_rejected():
    r = PC2.pc_v2_app_open_prepare("  ", stores_base_dir="/s", executor=_ok_exe())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "APP_REQUIRED" in r["reason"]

def test_b_prepare_unresolved_app_rejected(tmp_path):
    r = _prep(tmp_path, _unresolved(), app="unknown_xyz")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "APP_NOT_IN_INVENTORY" in r["reason"]

def test_b_prepare_lnk_app(tmp_path):
    r = PC2.pc_v2_app_open_prepare(
        _LNK_NAME, stores_base_dir=tmp_path / "stores", executor=_ok_lnk())
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["resolved_target"] == _LNK_TARGET


# C. EXECUTE lifecycle
def test_c_execute_ok_exe(tmp_path):
    ex = _ok_exe(pid=os.getpid())
    r = _exec(tmp_path, _prep(tmp_path, ex), ex)
    assert r["status"] == PC2.EXECUTED_OK, r
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r["human_authorization_consumed"] is True
    assert r["proof_strength"] == "STRONG"
    assert r["pid_verified"] is True
    assert r["lnk_policy"] == "NOT_APPLICABLE"
    assert r["executor_provider"] == "JARJAR"
    assert r["executor_capability"] == "app.open"

def test_c_execute_lnk_weak_proof(tmp_path):
    ex = _ok_lnk()
    prep = PC2.pc_v2_app_open_prepare(
        _LNK_NAME, stores_base_dir=tmp_path / "stores", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_app_open_execute(
        prep, eah, "human-ref-lnk",
        stores_base_dir=tmp_path / "stores", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK, r
    assert r["proof_strength"] == "WEAK"
    assert r["pid_verified"] is False
    assert r["lnk_policy"] == "WEAK_ACCEPTED"
    assert r["launched_pid"] is None

def test_c_execute_open_called_with_resolved_target(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    ex.open_app_by_target.assert_not_called()
    _exec(tmp_path, prep, ex)
    ex.open_app_by_target.assert_called_once_with(_APP_TARGET)

def test_c_execute_wrong_eah_rejected(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    r = PC2.pc_v2_app_open_execute(
        prep, "a" * 64, "human-ref",
        stores_base_dir=tmp_path / "stores", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert r["reason"] == PC2.EAH_MISMATCH
    ex.open_app_by_target.assert_not_called()

def test_c_execute_missing_human_ref_rejected(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_app_open_execute(
        prep, eah, "", stores_base_dir=tmp_path / "stores", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.open_app_by_target.assert_not_called()

def test_c_execute_without_executor_rejected(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_app_open_execute(
        prep, eah, "human-ref", stores_base_dir=tmp_path / "stores")
    assert r["status"] == PC2.EXECUTE_REJECTED

def test_c_execute_wrong_phase_rejected(tmp_path):
    ex = _ok_exe()
    fake = {"j5_phase": "EXECUTE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.pc_v2_app_open_execute(
        fake, "a" * 64, "ref", stores_base_dir=tmp_path / "stores", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.open_app_by_target.assert_not_called()


# D. TOCTOU / drift
def test_d_inventory_drift_detected(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    ex.resolve_app.return_value = {"ok": True, "name": _APP_NAME,
                                   "target": "other.exe", "source": _APP_SOURCE}
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "INVENTORY_DRIFT_DETECTED" in r["reason"]
    ex.open_app_by_target.assert_not_called()

def test_d_app_removed_at_execute(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    ex.resolve_app.return_value = {"ok": False, "error": "APP_NOT_IN_INVENTORY"}
    r = _exec(tmp_path, prep, ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "APP_NOT_IN_INVENTORY" in r["reason"]
    ex.open_app_by_target.assert_not_called()

def test_d_pre_state_drifted_lnk_deleted(tmp_path):
    lnk = str(tmp_path / "app.lnk")
    (tmp_path / "app.lnk").write_text("")
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {"ok": True, "name": "myapp", "target": lnk, "source": "start_menu"}
    ex.open_app_by_target.return_value = {"ok": True, "pid": None, "target": lnk, "source": "start_menu"}
    prep = PC2.pc_v2_app_open_prepare(
        "myapp", stores_base_dir=tmp_path / "stores", executor=ex)
    (tmp_path / "app.lnk").unlink()
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_app_open_execute(
        prep, eah, "ref", stores_base_dir=tmp_path / "stores", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFTED" in r["reason"]
    ex.open_app_by_target.assert_not_called()


# E. PID verification
def test_e_exe_pid_verified_strong(tmp_path):
    ex = _ok_exe(pid=os.getpid())
    r = _exec(tmp_path, _prep(tmp_path, ex), ex)
    assert r["status"] == PC2.EXECUTED_OK, r
    assert r["proof_strength"] == "STRONG"
    assert r["pid_verified"] is True

def test_e_exe_pid_none_rejected(tmp_path):
    ex = _ok_exe()
    ex.open_app_by_target.return_value = {"ok": True, "pid": None, "target": _APP_TARGET, "source": _APP_SOURCE}
    r = _exec(tmp_path, _prep(tmp_path, ex), ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PID_NONE" in r["reason"]

def test_e_exe_pid_not_alive_rejected(tmp_path):
    orig = PC2._is_pid_alive
    try:
        PC2._is_pid_alive = lambda pid: False
        ex = _ok_exe(pid=99999999)
        r = _exec(tmp_path, _prep(tmp_path, ex), ex)
        assert r["status"] == PC2.EXECUTE_REJECTED
        assert "PID_NOT_ALIVE" in r["reason"]
    finally:
        PC2._is_pid_alive = orig


# F. fail closed
def test_f_backend_failure_fail_closed(tmp_path):
    ex_f = _failed_launch()
    ex_ok = _ok_exe()
    prep = _prep(tmp_path, ex_ok)
    ex_ok.open_app_by_target.return_value = {"ok": False, "error": "APP_OPEN_FAILED:x"}
    r = _exec(tmp_path, prep, ex_ok)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "JARJAR_EXECUTOR_FAILED" in r["reason"]

def test_f_open_called_with_resolved_target_not_app_name(tmp_path):
    ex = _ok_exe()
    prep = _prep(tmp_path, ex)
    _exec(tmp_path, prep, ex)
    call = ex.open_app_by_target.call_args
    assert call is not None
    assert call[0][0] == _APP_TARGET


# G. receipt + metadata
def test_g_receipt_in_prepare(tmp_path):
    r = _prep(tmp_path, _ok_exe())
    rcpt = r.get("receipt", {})
    assert rcpt["capability"] == "PC_V2_APP_OPEN_PREPARE"
    assert rcpt["result_status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert rcpt.get("requested_app") == _APP_NAME
    assert rcpt.get("resolved_target") == _APP_TARGET

def test_g_receipt_in_execute(tmp_path):
    ex = _ok_exe(pid=os.getpid())
    r = _exec(tmp_path, _prep(tmp_path, ex), ex)
    rcpt = r.get("receipt", {})
    assert rcpt["capability"] == "PC_V2_APP_OPEN_EXECUTE"
    assert rcpt["result_status"] == PC2.EXECUTED_OK
    assert rcpt.get("proof_strength") == "STRONG"
    assert rcpt.get("executor_provider") == "JARJAR"

def test_g_jarvis_authority_none(tmp_path):
    ex = _ok_exe()
    r = _exec(tmp_path, _prep(tmp_path, ex), ex)
    assert r["jarvis_authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"


# H. graph entries
def test_h_graph_prepare_route_native():
    cap = G.get_capability("PC_V2_APP_OPEN_PREPARE")
    assert cap is not None
    assert cap["route"] == "STACK_NATIVE_ROUTE"
    assert cap["authority_class"] == "KX108_ONLY"
    assert cap["grants_authority"] is False

def test_h_graph_execute_route_stage4():
    cap = G.get_capability("PC_V2_APP_OPEN_EXECUTE")
    assert cap is not None
    assert cap["route"] == "STAGE4_GOVERNED_RAIL"
    assert cap["authority_class"] == "KX108_ONLY"
    assert cap["grants_authority"] is False


# I. bridge contract
def test_i_bridge_has_resolve_app():
    from jarjar_executor_bridge_v0 import JarJarWindowsExecutor
    ex = object.__new__(JarJarWindowsExecutor)
    assert hasattr(ex, "resolve_app") and callable(ex.resolve_app)

def test_i_bridge_has_open_app_by_target():
    from jarjar_executor_bridge_v0 import JarJarWindowsExecutor
    ex = object.__new__(JarJarWindowsExecutor)
    assert hasattr(ex, "open_app_by_target") and callable(ex.open_app_by_target)

def test_i_bridge_self_check_app_ops():
    from jarjar_executor_bridge_v0 import self_check_bridge_v0
    sc = self_check_bridge_v0()
    ops = sc.get("operations", [])
    assert "APP_OPEN_RESOLVE" in ops
    assert "APP_OPEN_BY_TARGET" in ops


# J. no subprocess/startfile in Obsidia code
def test_j_no_subprocess_popen_in_pc_v2():
    src = (WORKTREE / "scripts" / "obsidia_pc_capabilities_v2.py").read_text("utf-8")
    bad = [l for l in src.splitlines() if ("subprocess.Popen" in l or "os.startfile" in l) and not l.strip().startswith("#")]
    assert not bad, f"obsidia_pc_capabilities_v2.py ne doit pas contenir subprocess.Popen / os.startfile: {bad}"

def test_j_no_subprocess_popen_in_bridge():
    src = (WORKTREE / "scripts" / "jarjar_executor_bridge_v0.py").read_text("utf-8")
    bad = [l for l in src.splitlines() if ("subprocess.Popen" in l or "os.startfile" in l) and not l.strip().startswith("#")]
    assert not bad, f"jarjar_executor_bridge_v0.py ne doit pas contenir subprocess.Popen / os.startfile: {bad}"
