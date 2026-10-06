from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path
from typing import Optional

_BRIDGE_VERSION = "V0"
_EXECUTOR_PROVIDER = "JARJAR"
_EXECUTOR_BACKEND = "NativeFilesystemBackend"

def _jarjar_src_default() -> Path:
    return (Path(__file__).resolve().parent.parent.parent / "Jarvis-iron-obsidia-" / "src")

def _ensure_jarjar_import(jarjar_src=None) -> str:
    override = os.environ.get("JARJAR_SRC_PATH")
    if override: src = str(Path(override).resolve())
    elif jarjar_src is not None: src = str(Path(jarjar_src).resolve())
    else: src = str(_jarjar_src_default().resolve())
    if src not in sys.path: sys.path.insert(0, src)
    return src

def _sha256(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

class JarJarFilesystemExecutor:
    EXECUTOR_PROVIDER = _EXECUTOR_PROVIDER
    EXECUTOR_BACKEND = _EXECUTOR_BACKEND
    BRIDGE_VERSION = _BRIDGE_VERSION
    def __init__(self, allowed_root: Path, *, jarjar_src=None) -> None:
        _ensure_jarjar_import(jarjar_src)
        from jarvis.filesystem import NativeFilesystemBackend, UserPathPolicy
        from jarvis.contracts import ActionRequest
        self._ActionRequest = ActionRequest
        self._backend = NativeFilesystemBackend(
            policy=UserPathPolicy(allowed_roots=(Path(allowed_root).resolve(),)))
        self._allowed_root = Path(allowed_root).resolve()
    def _req(self, capability: str, **kwargs: str):
        return self._ActionRequest(capability=capability, arguments=dict(kwargs), source="obsidia_bridge_v0")
    def move_file(self, source_abs: Path, dest_abs: Path) -> dict:
        req = self._req("file.move", source=str(source_abs), target=str(dest_abs))
        result = self._backend.execute(req)
        if not result.ok:
            return {"ok": False, "error": result.message, "executor": _EXECUTOR_BACKEND, "capability": "file.move"}
        return {"ok": True, "error": None, "executor": _EXECUTOR_BACKEND, "capability": "file.move", "data": result.data}
    def create_dir(self, dir_abs: Path) -> dict:
        if not dir_abs.parent.exists():
            return {"ok": False, "error": "PARENT_DIR_NOT_FOUND", "executor": _EXECUTOR_BACKEND, "capability": "folder.create"}
        req = self._req("folder.create", path=str(dir_abs))
        result = self._backend.execute(req)
        if not result.ok:
            return {"ok": False, "error": result.message, "executor": _EXECUTOR_BACKEND, "capability": "folder.create"}
        return {"ok": True, "error": None, "executor": _EXECUTOR_BACKEND, "capability": "folder.create", "data": result.data}
    def rollback_move_file(self, current_abs: Path, restore_to_abs: Path) -> dict:
        req = self._req("file.move", source=str(current_abs), target=str(restore_to_abs))
        result = self._backend.execute(req)
        if not result.ok:
            return {"ok": False, "error": result.message, "executor": _EXECUTOR_BACKEND, "capability": "file.move"}
        return {"ok": True, "error": None, "executor": _EXECUTOR_BACKEND, "capability": "file.move", "data": result.data}

def make_executor(repo_root: Path, *, jarjar_src=None) -> JarJarFilesystemExecutor:
    return JarJarFilesystemExecutor(Path(repo_root).resolve(), jarjar_src=jarjar_src)


def bridge_rollback_move_file_execute(
    sealed_rollback_evidence_id: str,
    *,
    sre_dir: Path,
    v2exec_dir: Path,
    executor: JarJarFilesystemExecutor,
    repo_root: Path,
) -> dict:
    _S = Path(__file__).resolve().parent
    if str(_S) not in sys.path: sys.path.insert(0, str(_S))
    rr = Path(repo_root).resolve(); rr_str = str(rr)
    sp = Path(sre_dir) / (sealed_rollback_evidence_id + ".json")
    if not sp.exists():
        return {"status": "ROLLBACK_FAILED", "reason": "SRE_NOT_FOUND"}
    try: sre = json.loads(sp.read_text("utf-8"))
    except Exception as exc: return {"status": "ROLLBACK_FAILED", "reason": "SRE_LOAD_ERROR:" + str(exc)}
    if sre.get("sealed_rollback_evidence_id") != sealed_rollback_evidence_id:
        return {"status": "ROLLBACK_FAILED", "reason": "SRE_ID_MISMATCH"}
    if sre.get("operation_type") != "V2_MOVE_FILE":
        return {"status": "ROLLBACK_FAILED", "reason": "UNSUPPORTED_OP:" + str(sre.get("operation_type"))}
    dest_pr = sre.get("target_path", ""); v2id = sre.get("batch_execution_id", ""); exp_sha = sre.get("pre_write_sha256", "")
    df = Path(v2exec_dir) / (v2id + ".json")
    if not df.exists():
        return {"status": "ROLLBACK_FAILED", "reason": "DESCRIPTOR_NOT_FOUND"}
    try: drec = json.loads(df.read_text("utf-8"))
    except Exception as exc: return {"status": "ROLLBACK_FAILED", "reason": "DESCRIPTOR_LOAD_ERROR:" + str(exc)}
    src_pr = drec.get("descriptor", {}).get("source_path", "")
    if not src_pr or not dest_pr:
        return {"status": "ROLLBACK_FAILED", "reason": "MISSING_PATHS_IN_DESCRIPTOR"}
    try:
        da = (rr / dest_pr).resolve(); sa = (rr / src_pr).resolve()
    except Exception as exc: return {"status": "ROLLBACK_FAILED", "reason": "PATH_RESOLVE_ERROR:" + str(exc)}
    if not (str(da) == rr_str or str(da).startswith(rr_str + os.sep)):
        return {"status": "ROLLBACK_FAILED", "reason": "DEST_PATH_TRAVERSAL"}
    if not (str(sa) == rr_str or str(sa).startswith(rr_str + os.sep)):
        return {"status": "ROLLBACK_FAILED", "reason": "SOURCE_PATH_TRAVERSAL"}
    if not da.exists() or not da.is_file():
        return {"status": "ROLLBACK_FAILED", "reason": "DEST_FILE_NOT_FOUND_FOR_ROLLBACK"}
    if sa.exists():
        return {"status": "ROLLBACK_FAILED", "reason": "SOURCE_ALREADY_EXISTS_CANNOT_ROLLBACK"}
    actual_sha = _sha256(da.read_bytes())
    if actual_sha != exp_sha:
        return {"status": "ROLLBACK_FAILED", "reason": "CURRENT_CONTENT_MISMATCH:" + actual_sha}
    rb = executor.rollback_move_file(da, sa)
    if not rb["ok"]:
        return {"status": "ROLLBACK_FAILED", "reason": "EXECUTOR_MOVE_FAILED:" + str(rb.get("error", ""))}
    if not sa.exists() or not sa.is_file():
        return {"status": "ROLLBACK_FAILED", "reason": "ROLLBACK_SOURCE_MISSING_AFTER_MOVE"}
    if da.exists():
        return {"status": "ROLLBACK_FAILED", "reason": "ROLLBACK_DEST_STILL_EXISTS"}
    restored = _sha256(sa.read_bytes())
    if restored != exp_sha:
        return {"status": "ROLLBACK_FAILED", "reason": "ROLLBACK_CONTENT_MISMATCH:" + restored}
    return {"status": "ROLLBACK_OK", "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
            "source_path": src_pr, "dest_path": dest_pr, "restored_sha256": restored,
            "executor_provider": _EXECUTOR_PROVIDER, "executor_backend": _EXECUTOR_BACKEND}


def self_check_bridge_v0() -> dict:
    return {"bridge_version": _BRIDGE_VERSION, "executor_provider": _EXECUTOR_PROVIDER,
            "executor_backend": _EXECUTOR_BACKEND, "openjarvis_authority": "NONE",
            "jarjar_authority": "NONE", "kx108_only": True, "human_approval_required": True,
            "operations": ["MOVE_FILE", "CREATE_DIR", "ROLLBACK_MOVE_FILE", "APP_OPEN_RESOLVE", "APP_OPEN_BY_TARGET", "AUDIO_STATUS", "AUDIO_SET_VOLUME", "UIA_LIST_CONTROLS_BY_IDENTITY", "UIA_FIND_BY_IDENTITY", "UIA_READ_VALUE_BY_IDENTITY", "UIA_SET_TEXT_BY_IDENTITY", "UIA_DISCOVER_CONTROLS_BY_WINDOW_TITLE", "UIA_READ_CHECKED", "UIA_SET_CHECKED"],
            "generic_shell_enabled": False, "arbitrary_filesystem": False,
            "makes_authorization_decisions": False, "is_execution_authority": False,
            "is_kx_authority": False, "new_parallel_mutation_engine": False}


# ============================================================
# G1-A : JarJarWindowsExecutor — window.focus
# ============================================================
class JarJarWindowsExecutor:
    """Wraps NativeWindowsBackend for governed window.focus operations.
    Physical execution + TOCTOU verification only. No authorization decisions.
    """
    EXECUTOR_PROVIDER = _EXECUTOR_PROVIDER
    EXECUTOR_BACKEND = "NativeWindowsBackend"
    BRIDGE_VERSION = _BRIDGE_VERSION

    def __init__(self, *, jarjar_src=None) -> None:
        _ensure_jarjar_import(jarjar_src)
        from jarvis.integrations.win32_driver import Win32Driver
        from jarvis.windows import NativeWindowsBackend
        from jarvis.structured_ui import StructuredUIBackend
        from jarvis.integrations.uia_driver import UIADriver
        from jarvis.integrations.uia_identity import StableUIAController
        from jarvis.contracts import ActionRequest
        self._ActionRequest = ActionRequest
        self._backend = NativeWindowsBackend(driver=Win32Driver())
        # G2-A-R: governed UIA writes only through JarJar G2-0 stable identity
        self._uia = StableUIAController()
        self._ui_backend = StructuredUIBackend(driver=UIADriver(), identity_driver=self._uia)

    def _req(self, capability: str, **kwargs: str):
        return self._ActionRequest(capability=capability, arguments=dict(kwargs),
                                   source="obsidia_bridge_v1")

    def audio_status(self) -> dict:
        """Read-only physical master-volume observation."""
        result = self._backend.execute(self._req("audio.status"))
        if not result.ok:
            return {"ok": False, "error": "AUDIO_STATUS_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "audio.status"}
        volume = result.data.get("volume_percent")
        muted = result.data.get("muted")
        if not isinstance(volume, int):
            return {"ok": False, "error": "AUDIO_STATUS_INVALID",
                    "executor": self.EXECUTOR_BACKEND, "capability": "audio.status"}
        return {"ok": True, "volume_percent": volume, "muted": bool(muted),
                "executor": self.EXECUTOR_BACKEND, "capability": "audio.status"}

    def set_volume(self, percent: int) -> dict:
        """Physical mutation only. Authorization is external and KX108-only."""
        if not isinstance(percent, int) or isinstance(percent, bool) or not 0 <= percent <= 100:
            return {"ok": False, "error": "VOLUME_PERCENT_INVALID",
                    "executor": self.EXECUTOR_BACKEND, "capability": "audio.set_volume"}
        result = self._backend.execute(self._req("audio.set_volume", percent=percent))
        if not result.ok:
            return {"ok": False, "error": result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "audio.set_volume"}
        observed = result.data.get("volume_percent")
        return {"ok": True, "requested_percent": percent, "volume_percent": observed,
                "muted": result.data.get("muted"),
                "executor": self.EXECUTOR_BACKEND, "capability": "audio.set_volume"}

    def find_window(self, title: str) -> dict:
        """Read-only. Enumerate visible windows and return the first hwnd whose title
        contains *title* (casefold). Never mutates focus."""
        result = self._backend.execute(self._req("window.list"))
        if not result.ok:
            return {"ok": False, "error": "WINDOW_LIST_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.list"}
        wanted = title.casefold()
        windows = result.data.get("windows", [])
        matches = [w for w in windows
                   if isinstance(w.get("title"), str) and wanted in w["title"].casefold()]
        if not matches:
            return {"ok": False, "error": "WINDOW_NOT_FOUND",
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.list"}
        w = matches[0]
        return {"ok": True, "hwnd": int(w["hwnd"]), "title": w["title"],
                "executor": self.EXECUTOR_BACKEND, "capability": "window.list"}

    def focus_window_by_hwnd(self, hwnd: int) -> dict:
        """TOCTOU-safe focus: re-verify hwnd still exists, focus by its current exact
        title, then confirm returned hwnd matches the expected hwnd.
        Fails closed if hwnd disappeared or a different window was focused."""
        list_result = self._backend.execute(self._req("window.list"))
        if not list_result.ok:
            return {"ok": False, "error": "WINDOW_LIST_FAILED:" + list_result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.list"}
        windows = list_result.data.get("windows", [])
        current = next((w for w in windows if int(w["hwnd"]) == hwnd), None)
        if current is None:
            return {"ok": False, "error": "TARGET_HWND_NOT_FOUND",
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.list"}
        current_title = current["title"]
        focus_result = self._backend.execute(self._req("window.focus", title=current_title))
        if not focus_result.ok:
            return {"ok": False, "error": "FOCUS_FAILED:" + focus_result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.focus"}
        returned_hwnd = int(focus_result.data.get("hwnd", 0))
        if returned_hwnd != hwnd:
            return {"ok": False,
                    "error": "HWND_MISMATCH:expected=%d,got=%d" % (hwnd, returned_hwnd),
                    "executor": self.EXECUTOR_BACKEND, "capability": "window.focus"}
        return {"ok": True, "hwnd": returned_hwnd,
                "title": focus_result.data.get("title", current_title),
                "executor": self.EXECUTOR_BACKEND, "capability": "window.focus"}

    def verify_focus(self, hwnd: int, resolved_title: str) -> dict:
        """Post-execute proof: verify hwnd is still visible and title is consistent
        with what was resolved at PREPARE time. Read-only (window.list)."""
        result = self._backend.execute(self._req("window.list"))
        if not result.ok:
            return {"ok": False, "error": "WINDOW_LIST_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        windows = result.data.get("windows", [])
        match = next((w for w in windows if int(w["hwnd"]) == hwnd), None)
        if match is None:
            return {"ok": False, "error": "HWND_NOT_FOUND_POST_FOCUS",
                    "executor": self.EXECUTOR_BACKEND}
        actual_title = match["title"]
        rt = resolved_title.casefold()
        at = actual_title.casefold()
        title_ok = rt in at or at in rt
        return {"ok": True, "hwnd": hwnd, "title": actual_title,
                "title_consistent": title_ok, "executor": self.EXECUTOR_BACKEND}


    # ── G1-B : app.open ───────────────────────────────────────────────────────

    def resolve_app(self, app_name: str) -> dict:
        """Read-only. Resolve app_name through WindowsAppInventory.
        Returns {"ok": True, "name": ..., "target": ..., "source": ...}
        or {"ok": False, "error": "APP_NOT_IN_INVENTORY"}.
        NEVER launches a process.
        """
        try:
            entry = self._backend.driver.app_inventory.resolve(app_name)
        except Exception as exc:
            return {"ok": False, "error": "INVENTORY_ERROR:" + str(exc),
                    "executor": self.EXECUTOR_BACKEND, "capability": "app.resolve"}
        if entry is None:
            return {"ok": False, "error": "APP_NOT_IN_INVENTORY",
                    "executor": self.EXECUTOR_BACKEND, "capability": "app.resolve"}
        return {
            "ok": True,
            "name": entry.name,
            "target": entry.target,
            "source": entry.source,
            "executor": self.EXECUTOR_BACKEND,
            "capability": "app.resolve",
        }

    def open_app_by_target(self, resolved_target: str) -> dict:
        """Execute app.open using the pre-validated resolved target path.
        Passes resolved_target as the `app` argument so the driver executes
        exactly that target (builtin .exe via PATH, or absolute .lnk / .exe).
        The driver's inventory re-resolution returns None for target paths,
        triggering its fallback — which is safe because the target was already
        validated through inventory at PREPARE time and bound to human approval.
        .lnk targets: pid=None (WEAK proof).
        .exe/builtin targets: pid returned (STRONG proof possible).
        """
        result = self._backend.execute(self._req("app.open", app=resolved_target))
        if not result.ok:
            return {"ok": False, "error": "APP_OPEN_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND, "capability": "app.open"}
        data = result.data or {}
        return {
            "ok": True,
            "pid": data.get("pid"),
            "target": data.get("target", resolved_target),
            "source": data.get("source", "unknown"),
            "executor": self.EXECUTOR_BACKEND,
            "capability": "app.open",
        }




    # ── G2-A-R : UIA operations by stable identity (JarJar G2-0) ───────────────
    # No title / control-name targeting: an Edit's name is its mutable content.
    # Values are reported as SHA-256 digests by JarJar; nothing here decides authority.

    def _ui(self, capability: str, arguments: dict) -> dict:
        result = self._ui_backend.execute(
            self._ActionRequest(capability=capability, arguments=arguments, source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False, "error": result.message,
                    "executor": "StructuredUIBackend", "capability": capability}
        return {"ok": True, **(result.data or {}),
                "executor": "StructuredUIBackend", "capability": capability}

    def list_controls_uia(self, window_hwnd: int) -> dict:
        """Read-only. Controls of the exact window with their stable UIA identity."""
        return self._ui("control.list_uia", {"window_hwnd": window_hwnd})

    def find_control_by_identity(self, identity: dict) -> dict:
        """Read-only. Re-find exactly this identity (no fuzzy fallback); fails if it drifted."""
        try:
            data = self._uia.find_control_by_identity(identity)
        except Exception as exc:
            return {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc),
                    "executor": "StructuredUIBackend", "capability": "control.find_by_identity"}
        return {**data, "executor": "StructuredUIBackend", "capability": "control.find_by_identity"}

    def read_value_by_identity(self, identity: dict) -> dict:
        """Read-only. SHA-256 of the exact control's value (password values are never read)."""
        return self._ui("control.read_value", {"target_identity": identity})

    def set_text_by_identity(self, identity: dict, exact_text: str) -> dict:
        """Physical mutation only (ValuePattern.SetValue + same-identity readback proof)."""
        return self._ui("control.set_text_by_identity", {"target_identity": identity, "text": exact_text})



    # ── G2-B1 : UIA stable-identity checkbox operations ──────────────────────

    def discover_controls_by_window_title(self, window_title: str) -> dict:
        """DISCOVERY ONLY (read-only): window title -> hwnd -> stable-identity listing.
        A title / label is UI metadata, never execution identity: callers must freeze and
        then use the returned stable identity. Distinct name on purpose: it must never
        shadow the canonical list_controls_uia(window_hwnd) used by G2-A-R."""
        hwnd_result = self._ui_backend.execute(
            self._ActionRequest(capability="control.get_window_hwnd",
                                arguments={"window_title": window_title},
                                source="obsidia_bridge_v1"))
        if not hwnd_result.ok:
            return {"ok": False,
                    "error": "HWND_RESOLVE_FAILED:" + hwnd_result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.get_window_hwnd"}
        hwnd = (hwnd_result.data or {}).get("hwnd")
        if not isinstance(hwnd, int) or hwnd <= 0:
            return {"ok": False, "error": "HWND_NOT_FOUND",
                    "executor": "StructuredUIBackend",
                    "capability": "control.get_window_hwnd"}
        result = self._ui_backend.execute(
            self._ActionRequest(capability="control.list_uia",
                                arguments={"window_hwnd": hwnd},
                                source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False,
                    "error": "UIA_LIST_FAILED:" + result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.list_uia"}
        data = result.data or {}
        return {"ok": True,
                "window": window_title,
                "controls": data.get("controls", []),
                "executor": "StructuredUIBackend",
                "capability": "control.list_uia"}

    def read_checked_by_identity(self, target_identity: dict) -> dict:
        result = self._ui_backend.execute(
            self._ActionRequest(capability="control.read_checked",
                                arguments={"target_identity": target_identity},
                                source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False,
                    "error": "READ_CHECKED_FAILED:" + result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.read_checked"}
        data = result.data or {}
        return {"ok": True,
                "toggle_state": data.get("toggle_state"),
                "checked": data.get("checked"),
                "indeterminate": data.get("indeterminate"),
                "target_identity": target_identity,
                "executor": "StructuredUIBackend",
                "capability": "control.read_checked"}

    def set_checked_by_identity(self, target_identity: dict, target_checked: bool) -> dict:
        result = self._ui_backend.execute(
            self._ActionRequest(capability="control.set_checked_by_identity",
                                arguments={"target_identity": target_identity,
                                           "target_checked": target_checked},
                                source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False,
                    "error": "SET_CHECKED_FAILED:" + result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.set_checked_by_identity"}
        data = result.data or {}
        return {"ok": True,
                "mutation_performed": data.get("mutation_performed"),
                "post_toggle_state": data.get("post_toggle_state"),
                "realized_state_verified": data.get("realized_state_verified"),
                "proof": data.get("proof"),
                "executor": "StructuredUIBackend",
                "capability": "control.set_checked_by_identity"}

    def read_selected_by_identity(self, target_identity: dict) -> dict:
        result = self._ui_backend.execute(
            self._ActionRequest(capability="control.read_selected",
                                arguments={"target_identity": target_identity},
                                source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False,
                    "error": "READ_SELECTED_FAILED:" + result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.read_selected"}
        data = result.data or {}
        return {"ok": True,
                "is_selected": data.get("is_selected"),
                "target_identity": target_identity,
                "executor": "StructuredUIBackend",
                "capability": "control.read_selected"}

    def select_radio_by_identity(self, target_identity: dict) -> dict:
        result = self._ui_backend.execute(
            self._ActionRequest(capability="control.select_radio_by_identity",
                                arguments={"target_identity": target_identity},
                                source="obsidia_bridge_v1"))
        if not result.ok:
            return {"ok": False,
                    "error": "SELECT_RADIO_FAILED:" + result.message,
                    "executor": "StructuredUIBackend",
                    "capability": "control.select_radio_by_identity"}
        data = result.data or {}
        return {"ok": True,
                "mutation_performed": data.get("mutation_performed"),
                "post_is_selected": data.get("post_is_selected"),
                "realized_state_verified": data.get("realized_state_verified"),
                "proof": data.get("proof"),
                "executor": "StructuredUIBackend",
                "capability": "control.select_radio_by_identity"}



# === G13 governed media ===
def _g13_media_execute(self, capability: str) -> dict:
    if capability not in {"media.play_pause", "media.next", "media.previous"}:
        return {"ok": False, "error": "MEDIA_CAPABILITY_UNSUPPORTED"}
    result = self._backend.execute(self._req(capability))
    return {
        "ok": bool(result.ok),
        "message": result.message,
        "data": dict(result.data or {}),
        "executor": self.EXECUTOR_BACKEND,
        "capability": capability,
    }

if not hasattr(JarJarWindowsExecutor, "media_execute"):
    JarJarWindowsExecutor.media_execute = _g13_media_execute


def make_windows_executor(*, jarjar_src=None) -> "JarJarWindowsExecutor":
    return JarJarWindowsExecutor(jarjar_src=jarjar_src)

# === G13 governed connectivity ===
def _g13_connectivity_status(self, family: str) -> dict:
    capability = {"wifi": "wifi.status", "bluetooth": "bluetooth.status"}.get(family)
    if capability is None:
        return {"ok": False, "error": "CONNECTIVITY_FAMILY_UNSUPPORTED"}
    result = self._backend.execute(self._req(capability))
    return {
        "ok": bool(result.ok),
        "message": result.message,
        "data": dict(result.data or {}),
        "executor": self.EXECUTOR_BACKEND,
        "capability": capability,
    }


def _g13_connectivity_set(self, family: str, enabled: bool) -> dict:
    table = {
        ("wifi", True): "wifi.enable",
        ("wifi", False): "wifi.disable",
        ("bluetooth", True): "bluetooth.enable",
        ("bluetooth", False): "bluetooth.disable",
    }
    capability = table.get((family, bool(enabled)))
    if capability is None:
        return {"ok": False, "error": "CONNECTIVITY_MUTATION_UNSUPPORTED"}
    result = self._backend.execute(self._req(capability))
    return {
        "ok": bool(result.ok),
        "message": result.message,
        "data": dict(result.data or {}),
        "executor": self.EXECUTOR_BACKEND,
        "capability": capability,
    }


if not hasattr(JarJarWindowsExecutor, "connectivity_status"):
    JarJarWindowsExecutor.connectivity_status = _g13_connectivity_status
if not hasattr(JarJarWindowsExecutor, "connectivity_set"):
    JarJarWindowsExecutor.connectivity_set = _g13_connectivity_set

# === G13 governed window control ===
def _g13_window_control_by_hwnd(self, hwnd: int, action: str, monitor_index: int | None = None) -> dict:
    if action in {"minimize", "maximize", "restore"}:
        result = self._backend.driver._window_state_hwnd(int(hwnd), action)
        return {"ok": True, "data": result, "action": action}
    if action == "move_monitor":
        if not isinstance(monitor_index, int) or monitor_index < 1:
            return {"ok": False, "error": "MONITOR_INDEX_REQUIRED"}
        result = self._backend.driver._move_window_to_monitor_hwnd(int(hwnd), monitor_index)
        return {"ok": True, "data": result, "action": action}
    return {"ok": False, "error": "WINDOW_CONTROL_UNSUPPORTED"}


def _g13_window_observe(self, hwnd: int) -> dict:
    try:
        import win32con
        import win32gui
    except ImportError as exc:
        return {"ok": False, "error": f"PYWIN32_MISSING:{exc}"}
    if not win32gui.IsWindow(int(hwnd)):
        return {"ok": False, "error": "WINDOW_NOT_FOUND"}

    rect = win32gui.GetWindowRect(int(hwnd))
    placement = win32gui.GetWindowPlacement(int(hwnd))
    show_cmd = int(placement[1])
    is_iconic = bool(win32gui.IsIconic(int(hwnd))) or show_cmd in {
        win32con.SW_SHOWMINIMIZED,
        win32con.SW_MINIMIZE,
        win32con.SW_SHOWMINNOACTIVE,
    }
    is_zoomed = show_cmd == win32con.SW_SHOWMAXIMIZED

    return {
        "ok": True,
        "hwnd": int(hwnd),
        "title": win32gui.GetWindowText(int(hwnd)).strip(),
        "is_iconic": is_iconic,
        "is_zoomed": is_zoomed,
        "show_cmd": show_cmd,
        "rect": tuple(int(v) for v in rect),
    }


if not hasattr(JarJarWindowsExecutor, "window_control_by_hwnd"):
    JarJarWindowsExecutor.window_control_by_hwnd = _g13_window_control_by_hwnd
if not hasattr(JarJarWindowsExecutor, "window_observe"):
    JarJarWindowsExecutor.window_observe = _g13_window_observe
