from __future__ import annotations

"""R11-B2 local developer mission adapter.

This module connects an explicitly bounded local development mission to the
existing Obsidure developer stack. It validates mission authority and scope,
optionally asks the existing native tooling session to produce a Phase1
candidate, hands the candidate to the certified R11-B1 -> R9 prepare path,
and only executes a prepared patch when an independent human/KX108
authorization reference is supplied.

It does not define a CLI, mint approval, call KX108 by itself, write memory,
commit, push, merge, or broaden Obsidure authority.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
for _path in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from obsidia_pc_capabilities_v2 import pc_v2_apply_patch_execute
from obsidure_self_build_r9_prepare_adapter_v1 import (
    STATUS_PREPARED as R11_B1_STATUS_PREPARED,
    adapt_self_build_candidate_to_r9_prepare,
)
from scripts.providers.obsidia_native_tooling_session_v1 import (
    NativeToolingTarget,
    run_native_multi_target_phase1,
)


ADAPTER_SCHEMA_VERSION = "OBSIDURE_LOCAL_DEVELOPER_MISSION_ADAPTER_V1"
STATUS_HELD = "R11_LOCAL_DEVELOPER_MISSION_HELD"
STATUS_REJECTED = "R11_LOCAL_DEVELOPER_MISSION_REJECTED"
STATUS_PREPARED = "R11_LOCAL_DEVELOPER_MISSION_PREPARED"
STATUS_EXECUTED = "R11_LOCAL_DEVELOPER_MISSION_EXECUTED"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]{1,96}$")
_ALLOWED_OPERATIONS = {"UPDATE_TARGET_FROM_SOURCE", "APPLY_PATCH"}
_SAFE_TOOL_IDS = {
    "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
    "OBSIDIA_NATIVE_SOLVE_STACK_V1",
    "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
    "PYTEST",
    "GIT_APPLY_CHECK",
}
_FORBIDDEN_TOOLS = {
    "SHELL",
    "NETWORK",
    "GIT_COMMIT",
    "GIT_PUSH",
    "GIT_MERGE",
    "MEMORY_WRITE",
    "KX108",
    "HUMANAPPROVAL",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _canonical_hash(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _hold(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_HELD,
        "reason": reason,
        "mission_adapter": "BACKEND_ONLY",
        "mission_kind": "LOCAL_DEVELOPER",
        "existing_engine_reused": True,
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "memory_written": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
        "cli_obsidure_modified": False,
        "cli_global_modified": False,
        **extra,
    }


def _reject(reason: str, **extra: Any) -> dict[str, Any]:
    out = _hold(reason, **extra)
    out["status"] = STATUS_REJECTED
    return out


def _git(root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _git_head(root: Path) -> str | None:
    code, out, _ = _git(root, "rev-parse", "HEAD")
    return out.lower() if code == 0 else None


def _git_branch(root: Path) -> str | None:
    code, out, _ = _git(root, "branch", "--show-current")
    return out if code == 0 else None


def _rel(value: str) -> str:
    return str(value or "").strip().replace("\\", "/").lstrip("./")


def _safe_rel(value: str) -> bool:
    rel = _rel(value)
    parts = rel.split("/")
    return bool(rel) and not rel.startswith("/") and not re.match(r"^[A-Za-z]:", rel) and all(
        part not in {"", ".", ".."} and not part.startswith(".git") for part in parts
    )


def _evidence_id(record: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _verify_declared_hash(record: Mapping[str, Any], hash_field: str) -> tuple[bool, str | None]:
    digest = record.get(hash_field)
    if digest in (None, ""):
        return True, None
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest.lower()):
        return False, f"{hash_field.upper()}_INVALID"
    payload = {str(k): v for k, v in dict(record).items() if str(k) != hash_field}
    if _canonical_hash(payload) != digest.lower():
        return False, f"{hash_field.upper()}_MISMATCH"
    return True, None


def _require_evidence(record: Mapping[str, Any] | None, *, kind: str, ids: tuple[str, ...]) -> tuple[bool, dict[str, Any]]:
    if not isinstance(record, Mapping):
        return False, {"reason": f"{kind}_REQUIRED"}
    payload = dict(record)
    record_id = _evidence_id(payload, *ids)
    if not record_id:
        return False, {"reason": f"{kind}_ID_REQUIRED"}
    status = str(payload.get("status") or payload.get("verification_status") or payload.get("result") or "").upper()
    if status not in {"VERIFIED", "VALIDATED", "PASS", "PASSED"}:
        return False, {"reason": f"{kind}_NOT_VERIFIED", f"{kind.lower()}_id": record_id}
    ok, why = _verify_declared_hash(payload, f"{kind.lower()}_hash")
    if not ok:
        return False, {"reason": why or f"{kind}_HASH_INVALID", f"{kind.lower()}_id": record_id}
    return True, {f"{kind.lower()}_id": record_id, f"{kind.lower()}_hash": payload.get(f"{kind.lower()}_hash")}


def _validate_mission_contract(mission: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    if not isinstance(mission, Mapping):
        return False, {"reason": "MISSION_CONTRACT_REQUIRED"}

    mission_id = _evidence_id(mission, "mission_id", "human_mission_id")
    if not mission_id:
        return False, {"reason": "MISSION_ID_REQUIRED"}

    state = str(mission.get("status") or mission.get("state") or "").upper()
    if bool(mission.get("revoked")) or state == "REVOKED":
        return False, {"reason": "MISSION_REVOKED", "mission_id": mission_id}
    if bool(mission.get("closed")) or state in {"CLOSED", "COMPLETED", "ABORTED"}:
        return False, {"reason": "MISSION_CLOSED", "mission_id": mission_id}
    if state and state not in {"ACTIVE", "MISSION_ACTIVE", "PLAN_BOUND", "WORKTREE_BOUND"}:
        return False, {"reason": "MISSION_NOT_ACTIVE", "mission_id": mission_id, "mission_state": state}

    repo_identity_ref = str(mission.get("repository_identity") or mission.get("repo_identity_ref") or "").strip()
    local_root = Path(str(mission.get("local_root") or "")).resolve()
    worktree = Path(str(mission.get("worktree") or mission.get("execution_worktree_path") or "")).resolve()
    main_worktree = Path(str(mission.get("main_worktree") or mission.get("main_worktree_path") or local_root)).resolve()
    branch = str(mission.get("branch") or "").strip()
    base_sha = str(mission.get("base_sha") or mission.get("base_commit_sha") or "").lower()
    objective = str(mission.get("objective") or "").strip()
    acceptance = tuple(str(v).strip() for v in (mission.get("acceptance_criteria") or ()) if str(v).strip())
    allowed_targets = tuple(_rel(v) for v in (mission.get("allowed_target_paths") or mission.get("allowed_targets") or ()))
    allowed_operations = tuple(str(v).upper() for v in (mission.get("allowed_operations") or mission.get("allowed_operation_shapes") or ()))
    approved_tools = tuple(str(v).upper() for v in (mission.get("approved_tools") or mission.get("allowed_tools") or ()))
    tests = tuple(str(v).strip() for v in (mission.get("test_commands") or ()) if str(v).strip())
    budget = mission.get("mission_budget")
    attempt_limit = mission.get("attempt_limit", mission.get("max_attempts"))
    authority = str(mission.get("mission_authority") or mission.get("decision_authority") or "").upper()

    required = {
        "REPOSITORY_IDENTITY_REQUIRED": bool(repo_identity_ref),
        "LOCAL_ROOT_REQUIRED": str(local_root) not in {"", "."},
        "WORKTREE_REQUIRED": str(worktree) not in {"", "."},
        "BRANCH_REQUIRED": bool(branch),
        "BASE_SHA_INVALID": bool(_HEX40.fullmatch(base_sha)),
        "OBJECTIVE_REQUIRED": bool(objective),
        "ACCEPTANCE_CRITERIA_REQUIRED": bool(acceptance),
        "ALLOWED_TARGET_PATHS_REQUIRED": bool(allowed_targets),
        "ALLOWED_OPERATIONS_REQUIRED": bool(allowed_operations),
        "APPROVED_TOOLS_REQUIRED": bool(approved_tools),
        "TEST_COMMANDS_REQUIRED": bool(tests),
        "MISSION_BUDGET_REQUIRED": isinstance(budget, int),
        "ATTEMPT_LIMIT_REQUIRED": isinstance(attempt_limit, int),
    }
    for reason, ok in required.items():
        if not ok:
            return False, {"reason": reason, "mission_id": mission_id}

    if not local_root.exists() or not local_root.is_dir():
        return False, {"reason": "LOCAL_ROOT_NOT_FOUND", "mission_id": mission_id}
    if not worktree.exists() or not worktree.is_dir():
        return False, {"reason": "WORKTREE_NOT_FOUND", "mission_id": mission_id}
    if authority != "KX108_ONLY":
        return False, {"reason": "MISSION_AUTHORITY_NOT_KX108_ONLY", "mission_id": mission_id}
    if budget <= 0 or attempt_limit <= 0:
        return False, {"reason": "MISSION_BUDGET_EXHAUSTED", "mission_id": mission_id}
    if int(mission.get("attempt_index", 0) or 0) >= attempt_limit:
        return False, {"reason": "MISSION_ATTEMPT_LIMIT_EXHAUSTED", "mission_id": mission_id}
    if any(not _safe_rel(target) for target in allowed_targets):
        return False, {"reason": "ALLOWED_TARGET_PATH_INVALID", "mission_id": mission_id}
    if not set(allowed_operations).issubset(_ALLOWED_OPERATIONS):
        return False, {"reason": "MISSION_OPERATION_NOT_ALLOWED", "mission_id": mission_id}
    if set(approved_tools) & _FORBIDDEN_TOOLS:
        return False, {"reason": "MISSION_TOOL_ESCALATION", "mission_id": mission_id}
    if not set(approved_tools).issubset(_SAFE_TOOL_IDS):
        return False, {"reason": "MISSION_TOOL_NOT_APPROVED", "mission_id": mission_id}

    if _git_head(worktree) != base_sha:
        return False, {"reason": "WORKTREE_BASE_SHA_MISMATCH", "mission_id": mission_id}
    if _git_branch(worktree) != branch:
        return False, {"reason": "WORKTREE_BRANCH_MISMATCH", "mission_id": mission_id}
    code, status, _ = _git(worktree, "status", "--short")
    if code != 0:
        return False, {"reason": "WORKTREE_STATUS_FAILED", "mission_id": mission_id}
    if status.strip():
        return False, {"reason": "WORKTREE_DIRTY", "mission_id": mission_id}

    return True, {
        "mission_id": mission_id,
        "repo_identity_ref": repo_identity_ref,
        "local_root": local_root,
        "worktree": worktree,
        "main_worktree": main_worktree,
        "branch": branch,
        "base_sha": base_sha,
        "objective": objective,
        "acceptance_criteria": acceptance,
        "allowed_target_paths": allowed_targets,
        "allowed_operations": allowed_operations,
        "approved_tools": approved_tools,
        "test_commands": tests,
        "mission_budget": budget,
        "attempt_limit": attempt_limit,
    }


def _validate_provider(provider_config: Mapping[str, Any] | None) -> tuple[bool, dict[str, Any]]:
    if not isinstance(provider_config, Mapping):
        return False, {"reason": "PROVIDER_CONFIG_REQUIRED"}
    provider_id = str(provider_config.get("provider_id") or "").strip()
    if provider_id != "OBSIDIA_NATIVE_TOOLING_SESSION_V1":
        return False, {"reason": "PROVIDER_NOT_SUPPORTED", "provider_id": provider_id}
    status = str(provider_config.get("status") or provider_config.get("availability") or "").upper()
    if status not in {"VERIFIED", "AVAILABLE"}:
        return False, {"reason": "MODEL_UNAVAILABLE", "provider_id": provider_id, "provider_status": status}
    availability_id = _evidence_id(provider_config, "availability_evidence_id", "provider_evidence_id", "id")
    if not availability_id:
        return False, {"reason": "PROVIDER_AVAILABILITY_EVIDENCE_REQUIRED", "provider_id": provider_id}
    return True, {"provider_id": provider_id, "availability_evidence_id": availability_id}


def _mission_context_for_r11_b1(mission: Mapping[str, Any], targets: Sequence[str]) -> dict[str, Any]:
    return {
        "mission_id": mission["mission_id"],
        "status": "ACTIVE",
        "allowed_target_paths": list(targets),
        "allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
        "allowed_tools": ["EDIT"],
        "max_actions": int(mission["mission_budget"]),
        "executed_actions": int(mission.get("executed_actions", 0) or 0),
        "max_iterations": int(mission["attempt_limit"]),
        "used_iterations": int(mission.get("attempt_index", 0) or 0),
    }


def run_local_developer_mission(
    *,
    mission_contract: Mapping[str, Any],
    provider_config: Mapping[str, Any] | None,
    inventory_snapshot: Mapping[str, Any] | None,
    deficiency_evidence: Mapping[str, Any] | None,
    validation_evidence: Mapping[str, Any] | None = None,
    phase1_candidate: Mapping[str, Any] | None = None,
    artifact_root: str | Path,
    stores_base_dir: str | Path,
    session_id: str,
    execute_authorized: bool = False,
    human_authorized_eah: str = "",
    human_authorization_reference: str = "",
    repair_feedback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    mission_ok, mission = _validate_mission_contract(mission_contract)
    if not mission_ok:
        return _hold(mission["reason"], mission=mission)

    provider_ok, provider = _validate_provider(provider_config)
    if not provider_ok:
        return _hold(provider["reason"], mission=mission, provider=provider)

    inventory_ok, inventory = _require_evidence(
        inventory_snapshot,
        kind="INVENTORY_SNAPSHOT",
        ids=("inventory_snapshot_id", "snapshot_id", "id"),
    )
    if not inventory_ok:
        return _hold(inventory["reason"], mission=mission, provider=provider)

    deficiency_ok, deficiency = _require_evidence(
        deficiency_evidence,
        kind="DEFICIENCY_EVIDENCE",
        ids=("deficiency_evidence_id", "deficiency_id", "id"),
    )
    if not deficiency_ok:
        return _hold(deficiency["reason"], mission=mission, provider=provider, inventory=inventory)

    if phase1_candidate is None:
        targets = [
            NativeToolingTarget(target_path=target, objective=mission["objective"])
            for target in mission["allowed_target_paths"]
        ]
        try:
            phase1_candidate = run_native_multi_target_phase1(
                repo_root=mission["worktree"],
                targets=targets,
                artifact_root=Path(artifact_root),
                session_id=session_id,
            )
        except Exception as exc:
            return _hold(
                "PROVIDER_CANDIDATE_GENERATION_FAILED",
                mission=mission,
                provider=provider,
                detail=f"{type(exc).__name__}: {exc}",
            )
    elif not isinstance(phase1_candidate, Mapping):
        return _hold("PHASE1_CANDIDATE_REQUIRED", mission=mission, provider=provider)

    candidate_targets = tuple(_rel(v) for v in (phase1_candidate.get("candidate_files") or phase1_candidate.get("targets") or ()))
    if not candidate_targets:
        return _hold("PHASE1_CANDIDATE_TARGETS_REQUIRED", mission=mission, provider=provider)
    if not set(candidate_targets).issubset(set(mission["allowed_target_paths"])):
        return _hold("MISSION_TARGET_SCOPE_EXCEEDED", mission=mission, provider=provider, candidate_targets=candidate_targets)

    candidate_patch_hash = str(phase1_candidate.get("candidate_patch_hash") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", candidate_patch_hash):
        return _hold("CANDIDATE_PATCH_HASH_REQUIRED", mission=mission, provider=provider)

    if validation_evidence is None:
        return _hold("VALIDATION_EVIDENCE_REQUIRED", mission=mission, provider=provider)
    validation_payload = dict(validation_evidence)
    observed_hash = validation_payload.get("candidate_patch_hash") or validation_payload.get("tested_patch_hash")
    if observed_hash != candidate_patch_hash:
        return _hold("VALIDATION_EVIDENCE_PATCH_HASH_MISMATCH", mission=mission, provider=provider)

    prepared = adapt_self_build_candidate_to_r9_prepare(
        phase1_candidate=phase1_candidate,
        mission_context=_mission_context_for_r11_b1(mission, candidate_targets),
        inventory_snapshot=inventory_snapshot,
        deficiency_evidence=deficiency_evidence,
        validation_evidence=validation_evidence,
        base_commit_sha=mission["base_sha"],
        repo_identity_ref=mission["repo_identity_ref"],
        execution_worktree_path=mission["worktree"],
        main_worktree_path=mission["main_worktree"],
        branch_name=mission["branch"],
        stores_base_dir=stores_base_dir,
        session_id=session_id,
    )

    if prepared.get("status") != R11_B1_STATUS_PREPARED:
        return {
            **_hold(prepared.get("reason") or "R11_B1_PREPARE_NOT_READY", mission=mission, provider=provider),
            "r11_b1_result": prepared,
        }

    result: dict[str, Any] = {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PREPARED,
        "reason": None,
        "mission_adapter": "BACKEND_ONLY",
        "mission_kind": "LOCAL_DEVELOPER",
        "mission": mission,
        "provider": provider,
        "inventory": inventory,
        "deficiency": deficiency,
        "phase1_candidate": phase1_candidate,
        "r11_b1_result": prepared,
        "prepared_action": prepared["prepared_action"],
        "r11_b1_integration": True,
        "r9_governed_prepare": True,
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "memory_written": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
        "cli_obsidure_modified": False,
        "cli_global_modified": False,
        "local_provider_verified": True,
        "real_local_model_e2e": False,
        "disposable_e2e": False,
    }

    if not execute_authorized:
        return result

    expected_eah = prepared["prepared_action"].get("execution_authority_hash")
    if not human_authorized_eah or not human_authorization_reference:
        return {**result, "status": STATUS_HELD, "reason": "HUMAN_AUTHORIZATION_REQUIRED"}
    if human_authorized_eah != expected_eah:
        return {**result, "status": STATUS_REJECTED, "reason": "HUMAN_AUTHORIZED_EAH_MISMATCH"}

    execution = pc_v2_apply_patch_execute(
        prepared["prepared_action"],
        human_authorized_eah,
        human_authorization_reference,
        stores_base_dir=stores_base_dir,
        repo_root=mission["worktree"],
        session_id=session_id,
    )
    result.update(
        {
            "status": STATUS_EXECUTED if execution.get("status") == "EXECUTED_OK" else STATUS_HELD,
            "reason": None if execution.get("status") == "EXECUTED_OK" else execution.get("reason"),
            "execution_result": execution,
            "action_evidence_id": execution.get("action_evidence_id", ""),
            "executor_invoked": execution.get("status") == "EXECUTED_OK",
            "physical_mutation": execution.get("status") == "EXECUTED_OK",
            "r9_b6_authorized_execution": execution.get("status") == "EXECUTED_OK",
            "r8_evidence": bool(execution.get("action_evidence_id")),
            "disposable_e2e": execution.get("status") == "EXECUTED_OK",
        }
    )

    if repair_feedback is not None and execution.get("action_evidence_id"):
        agent = repair_feedback.get("agent")
        prepared_repair = repair_feedback.get("prepared_repair")
        if agent is not None and prepared_repair:
            result["r10_feedback"] = agent.ingest_repair_execution_outcome(
                action_evidence_id=execution["action_evidence_id"],
                stores_base_dir=stores_base_dir,
                prepared_repair=prepared_repair,
                mission_context=dict(mission_contract),
                repair_budget=repair_feedback.get("repair_budget"),
                attempt_history=tuple(repair_feedback.get("attempt_history") or ()),
            )
    return result


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_REJECTED",
    "STATUS_PREPARED",
    "STATUS_EXECUTED",
    "run_local_developer_mission",
]
