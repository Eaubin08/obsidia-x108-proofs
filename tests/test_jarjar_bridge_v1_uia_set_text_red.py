"""
tests/test_jarjar_bridge_v1_uia_set_text_red.py
RED SUITE – G2-A governed UIA set_text (e98b0160), requalified for G2-A-R.

Classification:
  STILL_VALID      registration PREPARE / EXECUTE, no-executor reject, PREPARE never writes,
                   missing / wrong approval reject.
  REQUALIFIED      the target is now a JarJar G2-0 stable UIA identity (window_hwnd,
                   process_id, runtime_id), not window_title + control_name (an Edit's name is
                   its mutable content); bridge methods are the *_by_identity ones; STRONG proof
                   requires the same-identity readback hash.
  NEW_G2AR         see tests/test_jarjar_bridge_v1_uia_set_text.py (matrix A-T).
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import jarjar_executor_bridge_v0 as BRIDGE

_HWND  = 4242
_VALUE = "hello world"
_IDENT = {"window_hwnd": _HWND, "process_id": 77, "runtime_id": [42, 5001], "native_handle": 5001,
          "automation_id": "101", "control_type": "Edit", "class_name": "Edit",
          "framework_id": "Win32", "parent_runtime_id": [42, _HWND]}


def _h(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _ctrl(name=""):
    return {"identity": dict(_IDENT), "name": name, "enabled": True, "visible": True,
            "is_password": False, "is_read_only": False, "bounds": {}, "patterns": ["value"]}


def _ex(*, pre_value="", post_value=None):
    post = post_value if post_value is not None else pre_value
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "StructuredUIBackend"
    ex.list_controls_uia.return_value = {"ok": True, "controls": [_ctrl(pre_value)]}
    ex.find_control_by_identity.return_value = {"ok": True, **_ctrl(pre_value)}
    ex.read_value_by_identity.side_effect = [{"ok": True, "value_sha256": _h(pre_value)},
                                             {"ok": True, "value_sha256": _h(pre_value)},
                                             {"ok": True, "value_sha256": _h(post)}]
    ex.set_text_by_identity.return_value = {"ok": True, "target_identity": dict(_IDENT),
                                            "requested_text_sha256": _h(_VALUE),
                                            "readback_text_sha256": _h(post), "value_match": post == _VALUE}
    return ex


def _prepare(ex, base):
    return PC2.pc_v2_uia_set_text_prepare(_HWND, dict(_IDENT), _VALUE, stores_base_dir=base, executor=ex)


def test_red_uia_set_text_prepare_is_registered():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_UIA_SET_TEXT_PREPARE",
        window_hwnd=_HWND, target_identity=dict(_IDENT), target_value=_VALUE,
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
        window_hwnd=_HWND, target_identity=dict(_IDENT), target_value=_VALUE,
        stores_base_dir="/tmp/s",
    )
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")


def test_red_prepare_control_not_found(tmp_path):
    ex = _ex()
    ex.list_controls_uia.return_value = {"ok": True, "controls": []}
    r = _prepare(ex, tmp_path / "s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "CONTROL_NOT_FOUND" in r.get("reason", "")


def test_red_prepare_set_text_not_called(tmp_path):
    ex = _ex()
    _prepare(ex, tmp_path / "s")
    ex.set_text_by_identity.assert_not_called()


def test_red_bridge_has_identity_methods_and_no_title_writer():
    # REQUALIFIED: list_controls / set_text / read_text by title were replaced
    for name in ("list_controls_uia", "find_control_by_identity", "read_value_by_identity",
                 "set_text_by_identity"):
        assert hasattr(BRIDGE.JarJarWindowsExecutor, name), name
    for legacy in ("set_text", "list_controls", "read_text"):
        assert not hasattr(BRIDGE.JarJarWindowsExecutor, legacy), legacy


def test_red_execute_without_approval_rejected(tmp_path):
    ex = _ex()
    prep = _prepare(ex, tmp_path / "s")
    r = PC2.pc_v2_uia_set_text_execute(
        prep, "wrong_eah" * 8, "REF", stores_base_dir=tmp_path / "s", executor=ex
    )
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.set_text_by_identity.assert_not_called()


def test_red_realized_state_proof_available(tmp_path):
    ex = _ex(pre_value="", post_value=_VALUE)
    prep = _prepare(ex, tmp_path / "s")
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_uia_set_text_execute(
        prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex
    )
    assert r.get("proof_strength") == "STRONG", r
    assert r["readback_value_sha256"] == _h(_VALUE)
