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

_HWND = 8001
_ID = {
    "window_hwnd": 8001, "process_id": 2222, "runtime_id": [40, 50, 60],
    "automation_id": "tab_settings", "control_type": "TabItem",
    "class_name": "TabItem", "framework_id": "Win32",
    "native_handle": 0, "parent_runtime_id": [],
}
_TAB_CTRL = {
    "name": "Settings", "enabled": True, "visible": True,
    "is_password": False, "patterns": ["selection_item"],
    "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 20},
    "identity": _ID,
}


def _ex(*, pre_selected=False, post_selected=True, mutation=True, realized=True):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "StructuredUIBackend"
    ex.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": [_TAB_CTRL]}
    ex.read_selected_by_identity.return_value = {
        "ok": True, "is_selected": pre_selected, "target_identity": _ID,
    }
    ex.select_tab_by_identity.return_value = {
        "ok": True, "mutation_performed": mutation,
        "post_is_selected": post_selected,
        "realized_state_verified": realized,
        "proof": "uia_selection_item_pattern_readback",
    }
    return ex


def test_stab_prepare_is_registered():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SELECT_TAB_PREPARE",
        window_hwnd=_HWND, target_identity=_ID,
        stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"


def test_stab_execute_is_registered():
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SELECT_TAB_EXECUTE",
        prepared_result=fake, human_authorized_eah="a" * 64,
        human_authorization_reference="REF", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"


def test_prepare_without_executor_rejected():
    r = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir="/tmp/s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")


def test_prepare_bad_hwnd_rejected():
    r = PC2.pc_v2_uia_select_tab_prepare(0, _ID, stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "WINDOW_HWND_REQUIRED" in r.get("reason", "")


def test_prepare_control_not_found_rejected():
    ex = _ex()
    ex.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": []}
    r = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "CONTROL_NOT_FOUND" in r.get("reason", "")


def test_prepare_wrong_type_rejected():
    ex = _ex()
    wrong_id = dict(_ID, control_type="Button")
    ctrl = dict(_TAB_CTRL, identity=wrong_id)
    ex.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": [ctrl]}
    r = PC2.pc_v2_uia_select_tab_prepare(_HWND, wrong_id, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "UNSUPPORTED_CONTROL_TYPE" in r.get("reason", "")


def test_prepare_disabled_rejected():
    ex = _ex()
    ctrl = dict(_TAB_CTRL, enabled=False, identity=dict(_ID))
    ex.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": [ctrl]}
    r = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "CONTROL_DISABLED" in r.get("reason", "")


def test_prepare_missing_pattern_rejected():
    ex = _ex()
    ctrl = dict(_TAB_CTRL, patterns=[], identity=dict(_ID))
    ex.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": [ctrl]}
    r = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "SELECTION_ITEM_PATTERN_REQUIRED" in r.get("reason", "")


def test_prepare_no_mutation_called():
    ex = _ex()
    PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir="/tmp/s", executor=ex)
    ex.select_tab_by_identity.assert_not_called()


def test_execute_wrong_eah_rejected(tmp_path):
    ex = _ex(pre_selected=False)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    r = PC2.pc_v2_uia_select_tab_execute(prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.select_tab_by_identity.assert_not_called()


def test_execute_missing_reference_rejected(tmp_path):
    ex = _ex(pre_selected=False)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED


def test_unselected_to_selected_strong_proof(tmp_path):
    ex = _ex(pre_selected=False, post_selected=True, mutation=True)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert prep["pre_is_selected"] is False
    assert prep["desired_state"] == "SELECTED"
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "REF-T001", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["realized_state_verified"] is True
    assert r["post_is_selected"] is True
    assert r["mutation_performed"] is True


def test_already_selected_noop(tmp_path):
    ex = _ex(pre_selected=True, post_selected=True, mutation=False)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "REF-T002", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["mutation_performed"] is False
    ex.select_tab_by_identity.assert_not_called()


def test_pre_state_drift_rejected(tmp_path):
    ex = _ex(pre_selected=False)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_selected_by_identity.return_value = {"ok": True, "is_selected": True}
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "REF-T003", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")
    ex.select_tab_by_identity.assert_not_called()


def test_realized_state_mismatch_rejected(tmp_path):
    ex = _ex(pre_selected=False)
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.select_tab_by_identity.return_value = {
        "ok": True, "mutation_performed": True,
        "post_is_selected": False, "realized_state_verified": False,
    }
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "REF-T004", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")


def test_psa_same_for_same_pre_state(tmp_path):
    ex = _ex(pre_selected=False)
    p1 = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s1", executor=ex)
    p2 = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s2", executor=ex)
    assert p1["physical_state_anchor"] == p2["physical_state_anchor"]


def test_noop_requires_independent_post_read(tmp_path):
    ex = _ex(pre_selected=True)
    good = {"ok": True, "is_selected": True}
    bad  = {"ok": True, "is_selected": False}
    ex.read_selected_by_identity.side_effect = [good, good, bad]
    prep = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_select_tab_execute(prep, eah, "REF-T005", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")
    ex.select_tab_by_identity.assert_not_called()


def test_stab_caps_registered_in_graph():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert "PC_V2_UIA_SELECT_TAB_PREPARE" in g
    assert "PC_V2_UIA_SELECT_TAB_EXECUTE" in g


def test_stab_authority_class():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_UIA_SELECT_TAB_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_UIA_SELECT_TAB_EXECUTE"]["authority_class"] == "KX108_ONLY"


def test_bridge_has_read_selected():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "read_selected_by_identity")


def test_bridge_has_select_tab():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "select_tab_by_identity")


def test_no_generic_click_capability():
    r = PC2.execute_pc_capability_v2("PC_V2_GENERIC_CLICK", window_hwnd=_HWND)
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"


def test_eah_differs_from_radio_eah(tmp_path):
    ex_t = _ex(pre_selected=False)
    ex_r = MagicMock()
    ex_r.EXECUTOR_PROVIDER = "JARJAR"
    ex_r.EXECUTOR_BACKEND = "StructuredUIBackend"
    rad_id = dict(_ID, control_type="RadioButton", runtime_id=[40, 50, 60])
    rad_ctrl = dict(_TAB_CTRL, identity=rad_id)
    ex_r.list_controls_uia.return_value = {"ok": True, "hwnd": _HWND, "controls": [rad_ctrl]}
    ex_r.read_selected_by_identity.return_value = {"ok": True, "is_selected": False}
    prep_tab = PC2.pc_v2_uia_select_tab_prepare(_HWND, _ID, stores_base_dir=tmp_path / "t", executor=ex_t)
    prep_rad = PC2.pc_v2_uia_select_radio_prepare(_HWND, rad_id, stores_base_dir=tmp_path / "r", executor=ex_r)
    assert prep_tab["execution_authority_hash"] != prep_rad["execution_authority_hash"]
