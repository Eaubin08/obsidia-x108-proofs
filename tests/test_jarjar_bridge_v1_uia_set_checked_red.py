from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import jarjar_executor_bridge_v0 as BRIDGE

_WIN  = "Acme Installer"
_CTRL = "Accept Terms"
_ID = {"window_hwnd": 1234, "process_id": 5678, "runtime_id": [10, 20, 30],
       "automation_id": "chk_accept", "control_type": "CheckBox",
       "class_name": "Button", "framework_id": "Win32",
       "native_handle": 0, "parent_runtime_id": []}
_CHK_CTRL = {"name": _CTRL, "enabled": True, "visible": True,
             "is_password": False, "patterns": ["toggle"],
             "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 20},
             "identity": _ID}


def _ex(*, pre_toggle=0, post_toggle=None, mutation=True):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "StructuredUIBackend"
    ex.discover_controls_by_window_title.return_value = {"ok": True, "window": _WIN, "controls": [_CHK_CTRL]}
    ex.read_checked_by_identity.return_value = {
        "ok": True, "toggle_state": pre_toggle, "checked": pre_toggle == 1, "indeterminate": False}
    final = post_toggle if post_toggle is not None else pre_toggle
    ex.set_checked_by_identity.return_value = {
        "ok": True, "mutation_performed": mutation, "post_toggle_state": final,
        "realized_state_verified": True, "proof": "uia_toggle_pattern_readback"}
    return ex

def test_prepare_is_registered():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_CHECKED_PREPARE",
        window_title=_WIN, control_name=_CTRL, target_checked=True,
        stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"

def test_execute_is_registered():
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_CHECKED_EXECUTE",
        prepared_result=fake, human_authorized_eah="a" * 64,
        human_authorization_reference="REF", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"

def test_prepare_without_executor_rejected():
    r = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")

def test_prepare_non_bool_target_rejected():
    r = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, 1, stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "TARGET_CHECKED_MUST_BE_BOOL" in r.get("reason", "")

def test_prepare_control_not_found_rejected():
    ex = _ex()
    ex.discover_controls_by_window_title.return_value = {"ok": True, "window": _WIN, "controls": []}
    r = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "CONTROL_NOT_FOUND" in r.get("reason", "")

def test_prepare_indeterminate_rejected():
    ex = _ex()
    ex.read_checked_by_identity.return_value = {"ok": True, "toggle_state": 2, "indeterminate": True}
    r = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "INDETERMINATE" in r.get("reason", "")

def test_prepare_no_mutation():
    ex = _ex()
    PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s", executor=ex)
    ex.set_checked_by_identity.assert_not_called()

def test_execute_wrong_eah_rejected():
    ex = _ex()
    prep = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s", executor=ex)
    r = PC2.pc_v2_uia_set_checked_execute(prep, "x" * 64, "REF", stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.set_checked_by_identity.assert_not_called()

def test_execute_missing_approval_reference_rejected():
    ex = _ex()
    prep = PC2.pc_v2_uia_set_checked_prepare(_WIN, _CTRL, True, stores_base_dir="/tmp/s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "", stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
def test_off_to_on_strong_proof(tmp_path):
    ex = _ex(pre_toggle=0, post_toggle=1, mutation=True)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert prep["target_checked"] is True and prep["pre_toggle_state"] == 0
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-001", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r.get("proof_strength") == "STRONG" and r.get("realized_state_verified") is True
    assert r.get("post_toggle_state") == 1

def test_on_to_off_strong_proof(tmp_path):
    ex = _ex(pre_toggle=1, post_toggle=0, mutation=True)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, False, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep["pre_toggle_state"] == 1
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-002", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK and r.get("post_toggle_state") == 0

def test_on_to_on_noop(tmp_path):
    ex = _ex(pre_toggle=1, post_toggle=1, mutation=False)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-003", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK and r.get("mutation_performed") is False

def test_off_to_off_noop(tmp_path):
    ex = _ex(pre_toggle=0, post_toggle=0, mutation=False)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, False, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-004", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK and r.get("mutation_performed") is False

def test_pre_state_drift_rejected(tmp_path):
    ex = _ex(pre_toggle=0)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_checked_by_identity.return_value = {"ok": True, "toggle_state": 1, "checked": True}
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-005", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED and "PRE_STATE_DRIFT" in r.get("reason", "")
    ex.set_checked_by_identity.assert_not_called()

def test_realized_state_mismatch_rejected(tmp_path):
    ex = _ex(pre_toggle=0)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.set_checked_by_identity.return_value = {
        "ok": True, "mutation_performed": True, "post_toggle_state": 0, "realized_state_verified": False}
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-006", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED and "REALIZED_STATE_MISMATCH" in r.get("reason", "")

def test_schk_caps_registered_in_graph():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert "PC_V2_UIA_SET_CHECKED_PREPARE" in g and "PC_V2_UIA_SET_CHECKED_EXECUTE" in g

def test_schk_authority_class():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_UIA_SET_CHECKED_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_UIA_SET_CHECKED_EXECUTE"]["authority_class"] == "KX108_ONLY"

def test_bridge_has_list_controls_uia():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "list_controls_uia")

def test_bridge_has_read_checked():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "read_checked_by_identity")

def test_bridge_has_set_checked():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "set_checked_by_identity")

def test_eah_commits_target_checked(tmp_path):
    ex = _ex(pre_toggle=0)
    prep_true = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    prep_false = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, False, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep_true["execution_authority_hash"] != prep_false["execution_authority_hash"]

def test_no_generic_click_capability():
    r = PC2.execute_pc_capability_v2("PC_V2_GENERIC_CLICK", window_title=_WIN)
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"

def test_psa_is_pre_state_only_target_lives_in_eah(tmp_path):
    ex = _ex(pre_toggle=0)
    prep_true = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    prep_false = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, False, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep_true["physical_state_anchor"] == prep_false["physical_state_anchor"]
    assert prep_true["execution_authority_hash"] != prep_false["execution_authority_hash"]

def test_noop_requires_independent_post_read(tmp_path):
    ex = _ex(pre_toggle=1, post_toggle=1, mutation=False)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.set_checked_by_identity.return_value = {
        "ok": True, "mutation_performed": False, "post_toggle_state": 0, "realized_state_verified": False}
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-007", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED and "REALIZED_STATE_MISMATCH" in r.get("reason", "")

def test_execute_uses_only_identity_bound_executor_calls(tmp_path):
    ex = _ex(pre_toggle=0, post_toggle=1)
    prep = PC2.pc_v2_uia_set_checked_prepare(
        _WIN, _CTRL, True, stores_base_dir=tmp_path / "s", executor=ex)
    ex.reset_mock()
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_checked_execute(prep, eah, "REF-008", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK and r["proof_strength"] == "STRONG"
    called = {c[0].split(".")[0] for c in ex.method_calls}
    assert called == {"read_checked_by_identity", "set_checked_by_identity"}
    ex.set_checked_by_identity.assert_called_once_with(_ID, True)
