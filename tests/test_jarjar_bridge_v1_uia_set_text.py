"""G2-A-R: governed UIA set_text bound to the JarJar G2-0 stable identity (matrix A-T).

The target is (window_hwnd, process_id, runtime_id) + drift guards, never a title or a
control name (an Edit's name is its mutable content: the realistic fake below changes
the name on every write while the identity stays stable). EAH = intended action
(identity + target hash); PHYSICAL_PRE_STATE V1 = observed pre-state (identity, flags,
pre_value_sha256, never the target). Receipts carry hashes only. STRONG only after the
same-identity readback hash equals the approved target hash.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import jarjar_executor_bridge_v0 as BRIDGE
import obsidia_pc_capabilities_v2 as PC2

HWND, PID = 4242, 77
TARGET, SECRET_PRE = "Bonjour G2-A-R", "previous secret value"


def _h(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _identity(**over):
    ident = {"window_hwnd": HWND, "process_id": PID, "runtime_id": [42, 5001], "native_handle": 5001,
             "automation_id": "101", "control_type": "Edit", "class_name": "Edit",
             "framework_id": "Win32", "parent_runtime_id": [42, HWND]}
    ident.update(over)
    return ident


class RealisticFakeExecutor:
    """Stateful: one Edit whose displayed name IS its value (like win32), stable identity."""
    EXECUTOR_PROVIDER = "JARJAR"
    EXECUTOR_BACKEND = "StructuredUIBackend"

    def __init__(self, value="", **flags):
        self.identity = _identity()
        self.value = value
        self.flags = {"enabled": True, "is_password": False, "is_read_only": False, "patterns": ["value"], **flags}
        self.extra_controls = []
        self.calls = []
        self.drop_after_write = False
        self.transform = None

    def _control(self):
        return {"identity": dict(self.identity), "name": self.value, "visible": True, "bounds": {}, **self.flags}

    def list_controls_uia(self, window_hwnd):
        self.calls.append("list_controls_uia")
        if window_hwnd != HWND:
            return {"ok": False, "error": "window not found"}
        return {"ok": True, "controls": [self._control()] + list(self.extra_controls)}

    def find_control_by_identity(self, identity):
        self.calls.append("find_control_by_identity")
        if identity.get("runtime_id") != self.identity["runtime_id"]:
            return {"ok": False, "error": "target control not found"}
        for k in ("window_hwnd", "process_id"):
            if identity.get(k) != self.identity[k]:
                return {"ok": False, "error": "process drift"}
        return {"ok": True, **self._control()}

    def read_value_by_identity(self, identity):
        self.calls.append("read_value_by_identity")
        if identity.get("runtime_id") != self.identity["runtime_id"]:
            return {"ok": False, "error": "target control not found"}
        if self.flags["is_password"]:
            return {"ok": False, "error": "password control"}
        return {"ok": True, "target_identity": dict(self.identity), "value_sha256": _h(self.value)}

    def set_text_by_identity(self, identity, exact_text):
        self.calls.append(("set_text_by_identity", exact_text))
        self.value = self.transform(exact_text) if self.transform else exact_text
        if self.drop_after_write:
            self.identity = _identity(runtime_id=[42, 9999])
        return {"ok": True, "target_identity": dict(identity), "requested_text_sha256": _h(exact_text),
                "readback_text_sha256": _h(self.value), "value_match": self.value == exact_text}


def _prepare(ex, base, ident=None, value=TARGET):
    return PC2.pc_v2_uia_set_text_prepare(HWND, ident or _identity(), value, stores_base_dir=base,
                                          executor=ex, window_title="Fixture", control_label="Nom")


def _execute(prep, ex, base):
    return PC2.pc_v2_uia_set_text_execute(prep, prep["execution_authority_hash"], "HUMAN-REF",
                                          stores_base_dir=base, executor=ex)


def _writes(ex):
    return [c for c in ex.calls if isinstance(c, tuple)]


# A / B. exact stable identity frozen, PREPARE never writes
def test_a_b_prepare_freezes_stable_identity_without_mutation(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    ident = prep["target_identity"]
    assert (ident["window_hwnd"], ident["process_id"], ident["runtime_id"]) == (HWND, PID, [42, 5001])
    assert prep["scope_id"] == "UIA_CONTROL:4242:77:42.5001"
    assert _writes(ex) == []


# C / D. EAH binds identity and target hash
def test_c_d_eah_binds_identity_and_target_hash(tmp_path):
    base = _prepare(RealisticFakeExecutor(SECRET_PRE), tmp_path / "a")["execution_authority_hash"]
    other_target = _prepare(RealisticFakeExecutor(SECRET_PRE), tmp_path / "b", value="autre")
    ex = RealisticFakeExecutor(SECRET_PRE)
    ex.identity = _identity(runtime_id=[42, 5002])
    other_ident = _prepare(ex, tmp_path / "c", ident=_identity(runtime_id=[42, 5002]))
    assert len({base, other_target["execution_authority_hash"], other_ident["execution_authority_hash"]}) == 3
    assert _prepare(RealisticFakeExecutor(SECRET_PRE), tmp_path / "d")["execution_authority_hash"] == base


# E / F. PSA = observed pre-state only
def test_e_f_psa_has_pre_hash_and_no_target(tmp_path):
    prep = _prepare(RealisticFakeExecutor(SECRET_PRE), tmp_path)
    snapshot, anchor = PC2._uia_pre_state(prep["target_identity"],
                                          {"enabled": True, "is_password": False, "is_read_only": False},
                                          _h(SECRET_PRE))
    assert anchor == prep["physical_state_anchor"] != prep["execution_authority_hash"]
    assert snapshot["pre_value_sha256"] == _h(SECRET_PRE) == prep["pre_value_sha256"]
    blob = json.dumps(snapshot)
    assert TARGET not in blob and _h(TARGET) not in blob and "target" not in blob
    assert prep["state_anchor_kind"] == "PHYSICAL_PRE_STATE"


# G. receipts never leak plaintext pre / target / post values
def test_g_receipts_carry_hashes_only(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    done = _execute(prep, ex, tmp_path)
    assert done["status"] == PC2.EXECUTED_OK
    for blob in (json.dumps(prep), json.dumps(done)):
        assert TARGET not in blob and SECRET_PRE not in blob
    assert done["receipt"]["readback_value_sha256"] == _h(TARGET)


# H. same name / text, different runtime_id -> never this target
def test_h_same_name_other_runtime_id_rejected(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path, ident=_identity(runtime_id=[42, 7777]))
    assert prep["status"] == PC2.PREPARE_REJECTED and prep["reason"] == "CONTROL_NOT_FOUND"


# I / J. prepared runtime_id absent or drifted at EXECUTE
@pytest.mark.parametrize("drift", ["absent", "recreated"])
def test_i_j_runtime_id_absent_or_drifted(tmp_path, drift):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    ex.identity = _identity(runtime_id=[42, 5003])  # element destroyed / recreated
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and "TARGET_IDENTITY_NOT_REACQUIRED" in r["reason"]
    assert _writes(ex) == []


# K. process drift
def test_k_process_drift_rejected(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    ex.identity = _identity(process_id=88)
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and _writes(ex) == []


def test_k_guard_drift_rejected(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    ex.identity = _identity(class_name="RichEdit")
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and r["reason"] == "CONTROL_IDENTITY_DRIFTED" and _writes(ex) == []


# L. pre-value hash drift
def test_l_pre_value_drift_rejected(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    ex.value = "changed by someone else"
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and r["reason"] == "PRE_STATE_DRIFT" and _writes(ex) == []


# M / N / O. password, read-only, unsupported control
@pytest.mark.parametrize("flags,ident,reason", [
    ({"is_password": True}, {}, "PASSWORD_FIELD_REJECTED"),
    ({"is_read_only": True}, {}, "READONLY_FIELD_REJECTED"),
    ({"is_read_only": None, "patterns": []}, {}, "VALUE_PATTERN_REQUIRED"),
    ({}, {"control_type": "TitleBar", "class_name": ""}, "UNSUPPORTED_CONTROL_TYPE"),
    ({"enabled": False}, {}, "CONTROL_DISABLED"),
])
def test_m_n_o_unsafe_targets_rejected_at_prepare(tmp_path, flags, ident, reason):
    ex = RealisticFakeExecutor(SECRET_PRE, **flags)
    ex.identity = _identity(**ident)
    prep = _prepare(ex, tmp_path, ident=_identity(**ident))
    assert prep["status"] == PC2.PREPARE_REJECTED and prep["reason"] == reason and _writes(ex) == []


def test_m_password_appearing_before_execute_rejected(tmp_path):
    ex = RealisticFakeExecutor(SECRET_PRE)
    prep = _prepare(ex, tmp_path)
    ex.flags["is_password"] = True
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and r["reason"] == "PASSWORD_FIELD_REJECTED" and _writes(ex) == []


# P / T. realistic success: the name changes, the identity does not, readback proves it
def test_p_t_stable_write_with_same_identity_readback_is_strong(tmp_path):
    ex = RealisticFakeExecutor("")
    prep = _prepare(ex, tmp_path)
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTED_OK and r["proof_strength"] == "STRONG"
    assert _writes(ex) == [("set_text_by_identity", TARGET)]
    assert ex._control()["name"] == TARGET  # displayed name changed after the write
    assert r["target_identity"]["runtime_id"] == [42, 5001] and r["readback_value_sha256"] == _h(TARGET)
    assert r["executor_capability"] == "control.set_text_by_identity"
    assert ex.calls[-1] == "read_value_by_identity"  # independent post-write observation


# Q. executor ok but value differs -> fail closed
def test_q_readback_mismatch_fails_closed(tmp_path):
    ex = RealisticFakeExecutor("")
    ex.transform = str.upper
    prep = _prepare(ex, tmp_path)
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and r["reason"] == "REALIZED_STATE_MISMATCH"
    assert r.get("proof_strength") != "STRONG"


def test_q_identity_lost_after_write_fails_closed(tmp_path):
    ex = RealisticFakeExecutor("")
    ex.drop_after_write = True
    prep = _prepare(ex, tmp_path)
    r = _execute(prep, ex, tmp_path)
    assert r["status"] == PC2.EXECUTE_REJECTED and r["reason"] == "REALIZED_STATE_MISMATCH"


# R. no title / name fallback anywhere in the governed path
def test_r_no_title_or_name_targeting():
    src = inspect.getsource(PC2.pc_v2_uia_set_text_prepare) + inspect.getsource(PC2.pc_v2_uia_set_text_execute)
    for legacy in ("list_controls(", "read_text(", ".set_text(", "_find_edit_control", "control_name"):
        assert legacy not in src, legacy
    assert not hasattr(PC2, "_find_edit_control")


# S. no keyboard / clipboard / shell path
def test_s_no_keyboard_clipboard_or_shell():
    src = inspect.getsource(PC2.pc_v2_uia_set_text_execute) + inspect.getsource(BRIDGE.JarJarWindowsExecutor)
    for forbidden in ("type_keys", "send_keys", "pyautogui", "clipboard", "subprocess", "os.system", "keyboard"):
        assert forbidden not in src, forbidden


def test_graph_registration_unchanged_ids():
    import obsidia_capability_graph_v0 as G
    for cid in ("PC_V2_UIA_SET_TEXT_PREPARE", "PC_V2_UIA_SET_TEXT_EXECUTE"):
        assert cid in G._GRAPH
    assert "target_identity" in G._GRAPH["PC_V2_UIA_SET_TEXT_PREPARE"]["accepted_input_shape"]
