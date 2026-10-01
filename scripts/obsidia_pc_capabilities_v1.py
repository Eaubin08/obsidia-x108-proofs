from __future__ import annotations
import hashlib, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_cognitive_governed_runtime_handoff_v0 as _J3
import obsidia_jarvis_governed_mutation_v0 as _J5
import obsidia_governed_execution_driver_v0 as _DRV

PC_CAPABILITY_V1_VERSION          = "V1"
PC_CAPABILITY_V1_MODE             = "GOVERNED_WRITE"
PC_CAPABILITY_IS_EXECUTION_AUTHORITY = False
PC_CAPABILITY_IS_KX_AUTHORITY        = False
KX_DECISION_AUTHORITY                = "KX108_ONLY"
JARVIS_AUTHORITY                     = "NONE"
HUMAN_APPROVAL_REQUIRED              = True
AUTO_EXECUTE                         = False
MUTATES_FILESYSTEM                   = True
ACCEPTS_ARBITRARY_SHELL              = False
ACCEPTS_ARBITRARY_GIT                = False
GENERIC_SHELL_ENABLED                = False

CAPABILITY_ID  = "GOVERNED_UPDATE_TARGET_FROM_SOURCE"
_CAP_PREPARE   = "PC_GOVERNED_PREPARE"
_CAP_EXECUTE   = "PC_GOVERNED_EXECUTE"
_CAPABILITY_IDS_V1 = (_CAP_PREPARE, _CAP_EXECUTE)

class PCGovernedCapabilityError(RuntimeError):
    pass

def _make_receipt_v1(capability, arguments, result_status, result_summary, session_id="") -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    digest_src = capability + ":" + ts + ":" + result_status
    receipt_id = "pcrcp-v1-" + hashlib.sha256(digest_src.encode()).hexdigest()[:8]
    result_digest = "sha256:" + hashlib.sha256(str(result_summary).encode()).hexdigest()[:16]
    return {
        "receipt_id": receipt_id, "capability": capability,
        "version": PC_CAPABILITY_V1_VERSION, "mode": PC_CAPABILITY_V1_MODE,
        "session_id": session_id, "authority": "NONE",
        "decision_authority": KX_DECISION_AUTHORITY,
        "human_approval_required": HUMAN_APPROVAL_REQUIRED,
        "auto_execute": AUTO_EXECUTE, "jarvis_authority": JARVIS_AUTHORITY,
        "kx108_admission": "DRY_RUN", "result_status": result_status,
        "result_digest": result_digest, "timestamp_utc": ts,
    }

def _stores(stores_base_dir: Path) -> dict:
    names = ("ledger", "selector", "execution", "pec",
             "kxpre", "kxpost", "tcr", "sar", "sre", "rollback", "approval")
    dirs = {}
    for n in names:
        d = stores_base_dir / n
        d.mkdir(parents=True, exist_ok=True)
        dirs[n] = d
    return dirs

def pc_governed_prepare(
    source_git_commit: str,
    source_historical_path: str,
    target_path: str,
    test_contract: dict,
    objective: str = "",
    mission_id: str = "",
    *,
    execution_worktree_path,
    main_worktree_path,
    branch_name: str,
    base_sha: str,
    stores_base_dir,
    session_id: str = "",
) -> dict:
    args = {"source_git_commit": source_git_commit, "target_path": target_path}
    exec_root = Path(execution_worktree_path).resolve()
    stores = _stores(Path(stores_base_dir))
    _mid = mission_id.strip() if mission_id.strip() else "pc-gov-prepare"
    try:
        proposal = _J3.prepare_cognitive_governed_handoff(
            mission_id=_mid, provider_id="pc-capability-v1",
            capability=_J5.CAPABILITY_ID,
            payload={
                "source_git_commit": source_git_commit,
                "source_historical_path": source_historical_path,
                "target_path": target_path,
                "test_contract": test_contract,
                "objective": str(objective or ""),
            },
            domain="PC_CAPABILITY_V1",
            action_id="pc-gov-prepare-" + _mid,
            intent="governed file update via PC capability V1",
            action_type=_J5.ACTION_TYPE,
            irreversible=False,
        )
    except Exception as exc:
        r = _make_receipt_v1(_CAP_PREPARE, args, "PROPOSAL_BUILD_FAILED", str(exc), session_id)
        return {"status": "PROPOSAL_BUILD_FAILED", "error": str(exc), "receipt": r}
    try:
        prepared = _J5.prepare_jarvis_governed_mutation(
            proposal,
            execution_worktree_path=exec_root,
            main_worktree_path=Path(main_worktree_path).resolve(),
            branch_name=branch_name, base_sha=base_sha,
            ledger_dir=stores["ledger"], selector_dir=stores["selector"],
            execution_dir=stores["execution"],
            pre_execution_context_dir=stores["pec"],
        )
    except _J5.JarvisGovernedMutationSeamError as exc:
        r = _make_receipt_v1(_CAP_PREPARE, args, "PREPARE_SEAM_ERROR", str(exc), session_id)
        return {"status": "PREPARE_SEAM_ERROR", "error": str(exc), "receipt": r}
    except Exception as exc:
        r = _make_receipt_v1(_CAP_PREPARE, args, "PREPARE_ERROR", str(exc), session_id)
        return {"status": "PREPARE_ERROR", "error": str(exc), "receipt": r}
    eah = prepared.get("execution_authority_hash", "")
    r = _make_receipt_v1(_CAP_PREPARE, args, prepared.get("status", "UNKNOWN"), eah, session_id)
    r["execution_authority_hash"] = eah
    r["human_approval_required"] = True
    r["auto_execute"] = False
    r["target_mutated"] = prepared.get("target_mutated", False)
    r["kx108_invocations"] = prepared.get("kx108_invocations", 0)
    return {
        "status": prepared.get("status", "UNKNOWN"),
        "j5_phase": prepared.get("j5_phase"),
        "jarvis_authority": prepared.get("jarvis_authority", "NONE"),
        "decision_authority": prepared.get("decision_authority", "KX108_ONLY"),
        "execution_authority_hash": eah,
        "target_mutated": prepared.get("target_mutated", False),
        "kx108_invocations": prepared.get("kx108_invocations", 0),
        "human_approval_created": prepared.get("human_approval_created", False),
        "human_authorization_consumed": prepared.get("human_authorization_consumed", False),
        "batch_execution_id": prepared.get("batch_execution_id"),
        "child_execution_id": prepared.get("child_execution_id"),
        "j5_target_pre_sha256": prepared.get("j5_target_pre_sha256"),
        "j5_plan_hash": prepared.get("j5_plan_hash"),
        "_prepared_internal": prepared,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": r,
    }

def pc_governed_execute(
    prepared_result: dict,
    human_authorized_eah: str,
    human_authorization_reference: str,
    *,
    stores_base_dir,
    repo_root,
    session_id: str = "",
) -> dict:
    args = {"eah_prefix": human_authorized_eah[:8] if human_authorized_eah else ""}
    if prepared_result.get("j5_phase") != _J5.PREPARE_PHASE:
        r = _make_receipt_v1(_CAP_EXECUTE, args, "PREPARE_PHASE_REQUIRED", "", session_id)
        return {"status": "PREPARE_PHASE_REQUIRED", "receipt": r}
    if prepared_result.get("status") != _DRV.PREPARED_AWAITING_HUMAN_APPROVAL:
        r = _make_receipt_v1(_CAP_EXECUTE, args, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", "", session_id)
        return {"status": "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", "receipt": r}
    expected_eah = prepared_result.get("execution_authority_hash", "")
    if not expected_eah or human_authorized_eah != expected_eah:
        r = _make_receipt_v1(_CAP_EXECUTE, args, "EAH_MISMATCH", "", session_id)
        return {"status": "EAH_MISMATCH", "error": "HUMAN_AUTHORIZED_EAH_DOES_NOT_MATCH", "receipt": r}
    if not human_authorization_reference.strip():
        r = _make_receipt_v1(_CAP_EXECUTE, args, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", "", session_id)
        return {"status": "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", "receipt": r}
    stores = _stores(Path(stores_base_dir))
    prepared = prepared_result.get("_prepared_internal", {})
    try:
        result = _J5.execute_jarvis_governed_mutation(
            prepared,
            human_authorized_execution_authority_hash=human_authorized_eah,
            human_authorization_reference=human_authorization_reference,
            execution_dir=stores["execution"],
            pre_execution_context_dir=stores["pec"],
            selector_dir=stores["selector"],
            ledger_dir=stores["ledger"],
            kx108_pre_decision_dir=stores["kxpre"],
            kx108_post_decision_dir=stores["kxpost"],
            test_contract_results_dir=stores["tcr"],
            sealed_receipt_dir=stores["sar"],
            sealed_rollback_evidence_dir=stores["sre"],
            rollback_result_dir=stores["rollback"],
            repo_root=Path(repo_root),
            # approval_dir=None -> driver defaults to execution_dir (same store as PREPARE)
        )
    except _J5.JarvisGovernedMutationSeamError as exc:
        r = _make_receipt_v1(_CAP_EXECUTE, args, "EXECUTE_SEAM_ERROR", str(exc), session_id)
        return {"status": "EXECUTE_SEAM_ERROR", "error": str(exc), "receipt": r}
    except Exception as exc:
        r = _make_receipt_v1(_CAP_EXECUTE, args, "EXECUTE_ERROR", str(exc), session_id)
        return {"status": "EXECUTE_ERROR", "error": str(exc), "receipt": r}
    r = _make_receipt_v1(_CAP_EXECUTE, args, result.get("status", "UNKNOWN"),
                         result.get("sealed_apply_receipt_id", ""), session_id)
    r["kx108_pre_gate"] = result.get("kx108_pre_gate")
    r["kx108_post_gate"] = result.get("kx108_post_gate")
    r["human_authorization_consumed"] = result.get("human_authorization_consumed", False)
    r["sealed_apply_receipt_id"] = result.get("sealed_apply_receipt_id")
    r["sealed_rollback_evidence_id"] = result.get("sealed_rollback_evidence_id")
    return {
        "status": result.get("status"),
        "j5_phase": result.get("j5_phase"),
        "jarvis_authority": result.get("jarvis_authority", "NONE"),
        "decision_authority": result.get("decision_authority", "KX108_ONLY"),
        "kx108_pre_gate": result.get("kx108_pre_gate"),
        "kx108_post_gate": result.get("kx108_post_gate"),
        "human_authorization_consumed": result.get("human_authorization_consumed", False),
        "human_authorization_reference": result.get("human_authorization_reference"),
        "sealed_apply_receipt_id": result.get("sealed_apply_receipt_id"),
        "sealed_rollback_evidence_id": result.get("sealed_rollback_evidence_id"),
        "target_after_sha256": result.get("target_after_sha256"),
        "receipt": r,
    }

def execute_pc_capability_v1(capability_id: str, payload: dict, *, session_id: str = "") -> dict:
    if capability_id == _CAP_PREPARE:
        return pc_governed_prepare(
            source_git_commit=payload.get("source_git_commit", ""),
            source_historical_path=payload.get("source_historical_path", ""),
            target_path=payload.get("target_path", ""),
            test_contract=payload.get("test_contract", {}),
            objective=str(payload.get("objective", "")),
            mission_id=str(payload.get("mission_id", "")),
            execution_worktree_path=payload["execution_worktree_path"],
            main_worktree_path=payload["main_worktree_path"],
            branch_name=payload["branch_name"],
            base_sha=payload["base_sha"],
            stores_base_dir=payload["stores_base_dir"],
            session_id=session_id,
        )
    if capability_id == _CAP_EXECUTE:
        return pc_governed_execute(
            prepared_result=payload["prepared_result"],
            human_authorized_eah=payload.get("human_authorized_eah", ""),
            human_authorization_reference=payload.get("human_authorization_reference", ""),
            stores_base_dir=payload["stores_base_dir"],
            repo_root=payload["repo_root"],
            session_id=session_id,
        )
    return {"status": "CAPABILITY_NOT_FOUND_V1", "capability_id": capability_id, "known": list(_CAPABILITY_IDS_V1)}


def self_check_v1() -> dict:
    return {
        "module": "obsidia_pc_capabilities_v1",
        "version": PC_CAPABILITY_V1_VERSION,
        "mode": PC_CAPABILITY_V1_MODE,
        "decision_authority": KX_DECISION_AUTHORITY,
        "is_execution_authority": PC_CAPABILITY_IS_EXECUTION_AUTHORITY,
        "is_kx_authority": PC_CAPABILITY_IS_KX_AUTHORITY,
        "human_approval_required": HUMAN_APPROVAL_REQUIRED,
        "auto_execute": AUTO_EXECUTE,
        "jarvis_authority": JARVIS_AUTHORITY,
        "mutates_filesystem": MUTATES_FILESYSTEM,
        "accepts_arbitrary_shell": ACCEPTS_ARBITRARY_SHELL,
        "accepts_arbitrary_git": ACCEPTS_ARBITRARY_GIT,
        "generic_shell_enabled": GENERIC_SHELL_ENABLED,
        "capabilities": list(_CAPABILITY_IDS_V1),
        "capability_id": CAPABILITY_ID,
    }
