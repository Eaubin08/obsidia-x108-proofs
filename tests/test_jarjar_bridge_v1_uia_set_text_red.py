"""
tests/test_jarjar_bridge_v1_uia_set_text_red.py
RED SUITE – G2-A governed UIA set_text
Each test is currently RED. They become GREEN after G2-A implementation.
"""
from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import jarjar_executor_bridge_v0 as BRIDGE

_WIN   = "Notepad"
_CTRL  = "Edit"
_VALUE = "hello world"
_AUTO  = "TextArea1"
_EDIT_CTRL = {
    "id": "0", "name": _CTRL, "control_type": "Edit", "class_name": "Edit",
    "automation_id": _AUTO, "enabled": True, "visible": True,
    "bounds": {"left": 10, "top": 10, "right": 200, "bottom": 30},
}


def _ex(*, pre_value="", post_value=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "StructuredUIBackend"
    ex.list_controls.return_value = {"ok": True, "window": _WIN, "controls": [_EDIT_CTRL]}
    ex.set_text.return_value      = {"ok": True, "window": _WIN, "control": _CTRL, "value": _VALUE}
    ex.read_text.return_value     = {"ok": True, "window": _WIN, "control": _CTRL,
                                     "text": post_value if post_value is not None else pre_value}
    return ex


def test_red_uia_set_text_prepare_is_registered():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_TEXT_PREPARE",
        window_title=_WIN, control_name=_CTRL, target_value=_VALUE,
        stores_base_dir="/tmp/s",
    )
    assert r["status"] != "UNKNOWN_CAPABILITY_V2", \
        "PC_V2_UIA_SET_TEXT_PREPARE n'est pas enregistrée (G2-A non implémenté)"


def test_red_uia_set_text_execute_is_registered():
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_TEXT_EXECUTE",
        prepared_result=fake, human_authorized_eah="a" * 64,
        human_authorization_reference="REF", stores_base_dir="/tmp/s",
    )
    assert r["status"] != "UNKNOWN_CAPABILITY_V2", \
        "PC_V2_UIA_SET_TEXT_EXECUTE n'est pas enregistrée (G2-A non implémenté)"


def test_red_prepare_without_executor_rejected():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_TEXT_PREPARE",
        window_title=_WIN, control_name=_CTRL, target_value=_VALUE,
        stores_base_dir="/tmp/s",
    )
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")


def test_red_prepare_control_not_found():
    ex = _ex()
    ex.list_controls.return_value = {"ok": True, "window": _WIN, "controls": []}
    r = PC2.pc_v2_uia_set_text_prepare(
        _WIN, _CTRL, _VALUE, stores_base_dir="/tmp/s", executor=ex
    )
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "CONTROL_NOT_FOUND" in r.get("reason", "")


def test_red_prepare_set_text_not_called():
    ex = _ex()
    PC2.pc_v2_uia_set_text_prepare(
        _WIN, _CTRL, _VALUE, stores_base_dir="/tmp/s", executor=ex
    )
    ex.set_text.assert_not_called()


def test_red_bridge_has_list_controls():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "list_controls"), \
        "JarJarWindowsExecutor.list_controls missing (G2-A non implémenté)"


def test_red_bridge_has_set_text():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "set_text"), \
        "JarJarWindowsExecutor.set_text missing (G2-A non implémenté)"


def test_red_bridge_has_read_text():
    assert hasattr(BRIDGE.JarJarWindowsExecutor, "read_text"), \
        "JarJarWindowsExecutor.read_text missing (G2-A non implémenté)"


def test_red_execute_without_approval_rejected():
    ex = _ex()
    prep = PC2.pc_v2_uia_set_text_prepare(
        _WIN, _CTRL, _VALUE, stores_base_dir="/tmp/s", executor=ex
    )
    r = PC2.pc_v2_uia_set_text_execute(
        prep, "wrong_eah" * 8, "REF", stores_base_dir="/tmp/s", executor=ex
    )
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.set_text.assert_not_called()


def test_red_realized_state_proof_available(tmp_path):
    ex = _ex(pre_value="", post_value=_VALUE)
    prep = PC2.pc_v2_uia_set_text_prepare(
        _WIN, _CTRL, _VALUE, stores_base_dir=tmp_path / "s", executor=ex
    )
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_text_execute(
        prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex
    )
    assert r.get("proof_strength") == "STRONG", \
        "proof_strength STRONG requis pour G2-A"
