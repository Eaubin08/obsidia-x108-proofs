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
            "operations": ["MOVE_FILE", "CREATE_DIR", "CREATE_FILE", "APPLY_PATCH", "ROLLBACK_MOVE_FILE"],
            "generic_shell_enabled": False, "arbitrary_filesystem": False,
            "makes_authorization_decisions": False, "is_execution_authority": False,
            "is_kx_authority": False, "new_parallel_mutation_engine": False}
