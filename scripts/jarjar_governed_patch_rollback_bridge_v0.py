from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from jarjar_executor_bridge_v0 import JarJarFilesystemExecutor

PREPARED_AWAITING_HUMAN_APPROVAL = "PREPARED_AWAITING_HUMAN_APPROVAL"
ROLLBACK_EXECUTED_OK = "ROLLBACK_EXECUTED_OK"
PREPARE_REJECTED = "PREPARE_REJECTED"
EXECUTE_REJECTED = "EXECUTE_REJECTED"
DECISION_AUTHORITY = "KX108_ONLY"
ROLLBACK_AUTHORITY = "SEALED_EVIDENCE_BOUND_RECOVERY"
OPERATION_TYPE = "V2_APPLY_PATCH"


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


def _decode_preimage(sre: dict[str, Any]) -> tuple[bytes | None, str | None]:
    try:
        raw = base64.b64decode(str(sre.get("pre_write_bytes_b64", "")), validate=True)
    except Exception:
        return None, "PREIMAGE_BASE64_INVALID"
    if _sha256_bytes(raw) != str(sre.get("pre_write_sha256", "")):
        return None, "PREIMAGE_SHA256_MISMATCH"
    if len(raw) != sre.get("pre_write_size"):
        return None, "PREIMAGE_SIZE_MISMATCH"
    return raw, None


def governed_rollback_patch_prepare(
    sealed_rollback_evidence_id: str,
    sealed_apply_receipt_id: str,
    *,
    sre_dir: Path,
    sar_dir: Path,
    v2exec_dir: Path,
    repo_root: Path,
    session_id: str = "",
) -> dict[str, Any]:
    rr = Path(repo_root).resolve()
    rr_str = str(rr)

    sre = _load_json(Path(sre_dir) / f"{sealed_rollback_evidence_id}.json")
    if sre is None:
        return {"status": PREPARE_REJECTED, "reason": "SRE_NOT_FOUND_OR_INVALID", "session_id": session_id}
    if sre.get("sealed_rollback_evidence_id") != sealed_rollback_evidence_id:
        return {"status": PREPARE_REJECTED, "reason": "SRE_ID_MISMATCH", "session_id": session_id}
    if sre.get("sealed") is not True:
        return {"status": PREPARE_REJECTED, "reason": "SRE_NOT_SEALED", "session_id": session_id}
    if sre.get("operation_type") != OPERATION_TYPE:
        return {"status": PREPARE_REJECTED, "reason": "UNSUPPORTED_OP:" + str(sre.get("operation_type")), "session_id": session_id}
    if sre.get("decision_authority") != DECISION_AUTHORITY:
        return {"status": PREPARE_REJECTED, "reason": "SRE_AUTHORITY_MISMATCH", "session_id": session_id}

    sar = _load_json(Path(sar_dir) / f"{sealed_apply_receipt_id}.json")
    if sar is None:
        return {"status": PREPARE_REJECTED, "reason": "SAR_NOT_FOUND_OR_INVALID", "session_id": session_id}
    if sar.get("sealed_apply_receipt_id") != sealed_apply_receipt_id:
        return {"status": PREPARE_REJECTED, "reason": "SAR_ID_MISMATCH", "session_id": session_id}
    if sar.get("sealed") is not True:
        return {"status": PREPARE_REJECTED, "reason": "SAR_NOT_SEALED", "session_id": session_id}
    if sar.get("operation_type") != OPERATION_TYPE:
        return {"status": PREPARE_REJECTED, "reason": "SAR_UNSUPPORTED_OP:" + str(sar.get("operation_type")), "session_id": session_id}
    if sar.get("decision_authority") != DECISION_AUTHORITY:
        return {"status": PREPARE_REJECTED, "reason": "SAR_AUTHORITY_MISMATCH", "session_id": session_id}

    target = str(sre.get("target_path", ""))
    if not target or target != str(sar.get("target_path", "")):
        return {"status": PREPARE_REJECTED, "reason": "SRE_SAR_TARGET_MISMATCH", "session_id": session_id}
    if sar.get("sealed_rollback_evidence_id") != sealed_rollback_evidence_id:
        return {"status": PREPARE_REJECTED, "reason": "SRE_SAR_ID_CROSSLINK_MISMATCH", "session_id": session_id}

    sre_hash = _sha256_json(sre)
    if str(sar.get("sealed_rollback_evidence_hash", "")) != sre_hash:
        return {"status": PREPARE_REJECTED, "reason": "SRE_SAR_HASH_CROSSLINK_MISMATCH", "session_id": session_id}

    if sre.get("batch_execution_id") != sar.get("batch_execution_id"):
        return {"status": PREPARE_REJECTED, "reason": "BATCH_ID_MISMATCH", "session_id": session_id}
    v2id = str(sre.get("batch_execution_id", ""))
    desc = _load_json(Path(v2exec_dir) / f"{v2id}.json")
    if desc is None:
        return {"status": PREPARE_REJECTED, "reason": "DESCRIPTOR_NOT_FOUND_OR_INVALID", "session_id": session_id}
    descriptor = desc.get("descriptor") or {}
    targets = descriptor.get("target_paths") or []
    if descriptor.get("operation_type") != OPERATION_TYPE:
        return {"status": PREPARE_REJECTED, "reason": "DESCRIPTOR_OPERATION_MISMATCH", "session_id": session_id}
    if len(targets) != 1 or targets[0] != target:
        return {"status": PREPARE_REJECTED, "reason": "G5A_SINGLE_TARGET_REQUIRED", "session_id": session_id}

    preimage, pre_err = _decode_preimage(sre)
    if preimage is None:
        return {"status": PREPARE_REJECTED, "reason": pre_err, "session_id": session_id}
    pre_sha = _sha256_bytes(preimage)
    if pre_sha != str(sar.get("target_pre_sha256", "")):
        return {"status": PREPARE_REJECTED, "reason": "PREIMAGE_NEQ_SAR_PRE_STATE", "session_id": session_id}

    try:
        target_abs = (rr / target).resolve()
    except OSError as exc:
        return {"status": PREPARE_REJECTED, "reason": "PATH_RESOLVE_ERROR:" + exc.__class__.__name__, "session_id": session_id}
    if not (str(target_abs) == rr_str or str(target_abs).startswith(rr_str + os.sep)):
        return {"status": PREPARE_REJECTED, "reason": "TARGET_PATH_TRAVERSAL", "session_id": session_id}
    if not target_abs.exists() or not target_abs.is_file():
        return {"status": PREPARE_REJECTED, "reason": "TARGET_FILE_NOT_FOUND_FOR_ROLLBACK", "session_id": session_id}

    expected_post = str(sar.get("target_post_sha256", ""))
    actual = _sha256_bytes(target_abs.read_bytes())
    if actual != expected_post:
        return {"status": PREPARE_REJECTED, "reason": "CURRENT_CONTENT_MISMATCH:" + actual, "session_id": session_id}

    binding = {
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "sealed_apply_receipt_id": sealed_apply_receipt_id,
        "target_path": target,
        "pre_write_sha256": pre_sha,
        "expected_post_sha256": expected_post,
        "current_sha256": actual,
        "descriptor_sha256": _sha256_json(desc),
        "session_id": session_id,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
    }
    rah = _sha256_json(binding)

    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "session_id": session_id,
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "sealed_apply_receipt_id": sealed_apply_receipt_id,
        "target_path": target,
        "pre_write_sha256": pre_sha,
        "expected_post_sha256": expected_post,
        "rollback_authority_hash": rah,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
        "kx108_invocations_during_rollback": 0,
    }


def governed_rollback_patch_execute(
    prepared_result: dict[str, Any],
    human_authorized_rollback_hash: str,
    human_authorization_reference: str,
    *,
    sre_dir: Path,
    sar_dir: Path,
    v2exec_dir: Path,
    executor: JarJarFilesystemExecutor,
    repo_root: Path,
    session_id: str = "",
) -> dict[str, Any]:
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return {"status": EXECUTE_REJECTED, "reason": "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED"}

    expected_hash = str(prepared_result.get("rollback_authority_hash", ""))
    if not expected_hash or human_authorized_rollback_hash != expected_hash:
        return {"status": EXECUTE_REJECTED, "reason": "ROLLBACK_AUTHORITY_HASH_MISMATCH"}
    if not str(human_authorization_reference or "").strip():
        return {"status": EXECUTE_REJECTED, "reason": "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"}

    fresh = governed_rollback_patch_prepare(
        str(prepared_result.get("sealed_rollback_evidence_id", "")),
        str(prepared_result.get("sealed_apply_receipt_id", "")),
        sre_dir=sre_dir,
        sar_dir=sar_dir,
        v2exec_dir=v2exec_dir,
        repo_root=repo_root,
        session_id=session_id,
    )
    if fresh.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return {"status": EXECUTE_REJECTED, "reason": "ROLLBACK_PRECONDITION_CHANGED:" + str(fresh.get("reason", ""))}
    if fresh.get("rollback_authority_hash") != expected_hash:
        return {"status": EXECUTE_REJECTED, "reason": "ROLLBACK_BINDING_CHANGED_AFTER_PREPARE"}

    sre = _load_json(Path(sre_dir) / f"{prepared_result['sealed_rollback_evidence_id']}.json")
    preimage, pre_err = _decode_preimage(sre or {})
    if preimage is None:
        return {"status": EXECUTE_REJECTED, "reason": pre_err or "PREIMAGE_INVALID"}

    target_abs = (Path(repo_root).resolve() / str(prepared_result["target_path"])).resolve()
    rb = executor.restore_file_bytes_guarded(
        target_abs,
        preimage,
        str(prepared_result["expected_post_sha256"]),
    )
    if not rb.get("ok"):
        return {"status": EXECUTE_REJECTED, "reason": "JARJAR_EXECUTOR_FAILED:" + str(rb.get("error", "")), "executor_result": rb}

    restored = _sha256_bytes(target_abs.read_bytes())
    if restored != str(prepared_result["pre_write_sha256"]):
        return {"status": EXECUTE_REJECTED, "reason": "ROLLBACK_CONTENT_MISMATCH:" + restored}

    return {
        "status": ROLLBACK_EXECUTED_OK,
        "session_id": session_id,
        "sealed_rollback_evidence_id": prepared_result["sealed_rollback_evidence_id"],
        "sealed_apply_receipt_id": prepared_result["sealed_apply_receipt_id"],
        "target_path": prepared_result["target_path"],
        "restored_sha256": restored,
        "human_authorization_consumed": True,
        "human_authorization_reference": human_authorization_reference,
        "decision_authority": DECISION_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
        "kx108_invocations_during_rollback": 0,
        "executor_provider": rb.get("executor"),
        "executor_backend": rb.get("executor"),
    }
