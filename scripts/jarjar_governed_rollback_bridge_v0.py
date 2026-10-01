from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from jarjar_executor_bridge_v0 import (
    JarJarFilesystemExecutor,
    bridge_rollback_move_file_execute,
)

PREPARED_AWAITING_HUMAN_APPROVAL = "PREPARED_AWAITING_HUMAN_APPROVAL"
ROLLBACK_EXECUTED_OK = "ROLLBACK_EXECUTED_OK"
PREPARE_REJECTED = "PREPARE_REJECTED"
EXECUTE_REJECTED = "EXECUTE_REJECTED"
DECISION_AUTHORITY = "KX108_ONLY"
ROLLBACK_AUTHORITY = "SEALED_EVIDENCE_BOUND_RECOVERY"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_json(data: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def governed_rollback_move_prepare(
    sealed_rollback_evidence_id: str,
    *,
    sre_dir: Path,
    v2exec_dir: Path,
    repo_root: Path,
    session_id: str = "",
) -> dict[str, Any]:
    rr = Path(repo_root).resolve()
    rr_str = str(rr)
    sp = Path(sre_dir) / (sealed_rollback_evidence_id + ".json")
    sre = _load_json(sp)
    if sre is None:
        return {
            "status": PREPARE_REJECTED,
            "reason": "SRE_NOT_FOUND_OR_INVALID",
            "session_id": session_id,
        }
    if sre.get("sealed_rollback_evidence_id") != sealed_rollback_evidence_id:
        return {
            "status": PREPARE_REJECTED,
            "reason": "SRE_ID_MISMATCH",
            "session_id": session_id,
        }
    if sre.get("operation_type") != "V2_MOVE_FILE":
        return {
            "status": PREPARE_REJECTED,
            "reason": "UNSUPPORTED_OP:" + str(sre.get("operation_type")),
            "session_id": session_id,
        }

    dest_pr = str(sre.get("target_path", ""))
    v2id = str(sre.get("batch_execution_id", ""))
    expected_sha = str(sre.get("pre_write_sha256", ""))
    df = Path(v2exec_dir) / (v2id + ".json")
    desc_rec = _load_json(df)
    if desc_rec is None:
        return {
            "status": PREPARE_REJECTED,
            "reason": "DESCRIPTOR_NOT_FOUND_OR_INVALID",
            "session_id": session_id,
        }
    source_pr = str(desc_rec.get("descriptor", {}).get("source_path", ""))
    if not source_pr or not dest_pr:
        return {
            "status": PREPARE_REJECTED,
            "reason": "MISSING_PATHS_IN_DESCRIPTOR",
            "session_id": session_id,
        }

    try:
        dest_abs = (rr / dest_pr).resolve()
        source_abs = (rr / source_pr).resolve()
    except OSError as exc:
        return {
            "status": PREPARE_REJECTED,
            "reason": "PATH_RESOLVE_ERROR:" + exc.__class__.__name__,
            "session_id": session_id,
        }

    if not (str(dest_abs) == rr_str or str(dest_abs).startswith(rr_str + os.sep)):
        return {
            "status": PREPARE_REJECTED,
            "reason": "DEST_PATH_TRAVERSAL",
            "session_id": session_id,
        }
    if not (str(source_abs) == rr_str or str(source_abs).startswith(rr_str + os.sep)):
        return {
            "status": PREPARE_REJECTED,
            "reason": "SOURCE_PATH_TRAVERSAL",
            "session_id": session_id,
        }
    if not dest_abs.exists() or not dest_abs.is_file():
        return {
            "status": PREPARE_REJECTED,
            "reason": "DEST_FILE_NOT_FOUND_FOR_ROLLBACK",
            "session_id": session_id,
        }
    if source_abs.exists():
        return {
            "status": PREPARE_REJECTED,
            "reason": "SOURCE_ALREADY_EXISTS_CANNOT_ROLLBACK",
            "session_id": session_id,
        }

    actual_sha = _sha256_bytes(dest_abs.read_bytes())
    if actual_sha != expected_sha:
        return {
            "status": PREPARE_REJECTED,
            "reason": "CURRENT_CONTENT_MISMATCH:" + actual_sha,
            "session_id": session_id,
        }

    binding = {
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "source_path": source_pr,
        "dest_path": dest_pr,
        "expected_sha256": expected_sha,
        "current_sha256": actual_sha,
        "descriptor_sha256": _sha256_json(desc_rec),
        "session_id": session_id,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
    }
    rollback_authority_hash = _sha256_json(binding)

    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "session_id": session_id,
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "source_path": source_pr,
        "dest_path": dest_pr,
        "expected_sha256": expected_sha,
        "rollback_authority_hash": rollback_authority_hash,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
        "kx108_invocations_during_rollback": 0,
    }


def governed_rollback_move_execute(
    prepared_result: dict[str, Any],
    human_authorized_rollback_hash: str,
    human_authorization_reference: str,
    *,
    sre_dir: Path,
    v2exec_dir: Path,
    executor: JarJarFilesystemExecutor,
    repo_root: Path,
    session_id: str = "",
) -> dict[str, Any]:
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return {
            "status": EXECUTE_REJECTED,
            "reason": "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED",
        }

    expected_hash = str(prepared_result.get("rollback_authority_hash", ""))
    if not expected_hash or human_authorized_rollback_hash != expected_hash:
        return {"status": EXECUTE_REJECTED, "reason": "ROLLBACK_AUTHORITY_HASH_MISMATCH"}
    if not str(human_authorization_reference or "").strip():
        return {
            "status": EXECUTE_REJECTED,
            "reason": "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED",
        }

    fresh = governed_rollback_move_prepare(
        str(prepared_result.get("sealed_rollback_evidence_id", "")),
        sre_dir=sre_dir,
        v2exec_dir=v2exec_dir,
        repo_root=repo_root,
        session_id=session_id,
    )
    if fresh.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return {
            "status": EXECUTE_REJECTED,
            "reason": "ROLLBACK_PRECONDITION_CHANGED:" + str(fresh.get("reason", "")),
        }
    if fresh.get("rollback_authority_hash") != expected_hash:
        return {
            "status": EXECUTE_REJECTED,
            "reason": "ROLLBACK_BINDING_CHANGED_AFTER_PREPARE",
        }

    legacy = bridge_rollback_move_file_execute(
        str(prepared_result["sealed_rollback_evidence_id"]),
        sre_dir=sre_dir,
        v2exec_dir=v2exec_dir,
        executor=executor,
        repo_root=repo_root,
    )
    if legacy.get("status") != "ROLLBACK_OK":
        return {
            "status": EXECUTE_REJECTED,
            "reason": legacy.get("reason") or legacy.get("status"),
            "legacy_result": legacy,
        }

    return {
        "status": ROLLBACK_EXECUTED_OK,
        "session_id": session_id,
        "sealed_rollback_evidence_id": prepared_result["sealed_rollback_evidence_id"],
        "source_path": legacy.get("source_path"),
        "dest_path": legacy.get("dest_path"),
        "restored_sha256": legacy.get("restored_sha256"),
        "human_authorization_consumed": True,
        "human_authorization_reference": human_authorization_reference,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
        "kx108_invocations_during_rollback": 0,
        "executor_provider": legacy.get("executor_provider"),
        "executor_backend": legacy.get("executor_backend"),
    }
