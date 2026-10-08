from __future__ import annotations

"""R11-B1 canonical self-build prepare adapter.

This module binds an existing Self-Build Phase1 candidate to the existing
R9 builder/governed-prepare path. It does not run Phase1, create a coding
engine, authorize execution, call KX108, invoke an executor, write memory,
commit, push, merge, or mutate a repository target.
"""

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL, _parse_patch_targets
from obsidure_builder_proposal_v1 import BuilderPatchRef, ObsidureBuilderProposalV1
from obsidure_governance_handoff_v1 import build_governance_handoff
from obsidure_governed_patch_prepare_adapter_v1 import prepare_obsidure_governed_patch_action
from obsidure_proposal_manifest_v1 import (
    ArtifactRef,
    EVIDENCE_STATUS_VERIFIED,
    EvidenceRecord,
    build_proposal_manifest,
)
from obsidure_proposal_validation_v1 import (
    ValidationObligation,
    ValidationPolicy,
    validate_obsidure_proposal,
)


ADAPTER_SCHEMA_VERSION = "OBSIDURE_SELF_BUILD_R9_PREPARE_ADAPTER_V1"
STATUS_PREPARED = "R11_SELF_BUILD_PREPARED"
STATUS_HELD = "R11_SELF_BUILD_HELD"
STATUS_REJECTED = "R11_SELF_BUILD_REJECTED"

PATCH_REF = "self_build_candidate.patch"
REPO_REF_DEFAULT = "obsidia-openjarvis-install-v0"
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

_FORBIDDEN_NON_AMPLIFICATION_PATTERNS = (
    "subprocess",
    "os.system",
    "powershell",
    "cmd.exe",
    "shell=True",
    "requests.",
    "socket.",
    "git commit",
    "git push",
    "git merge",
    "HumanApproval",
    "KX108_PRE",
    "KX108_POST",
    "execution_authority_hash",
    "memory_write",
    "memory_written",
    "grants_authority",
    "is_execution_authority = True",
    "is_kx_authority = True",
    "CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY = True",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _canonical_hash(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _without_hash_fields(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(k): v
        for k, v in dict(record).items()
        if str(k) not in {"sha256", "hash", "evidence_hash", "record_hash", "inventory_snapshot_hash", "deficiency_evidence_hash", "validation_evidence_hash"}
    }


def _hold(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_HELD,
        "reason": reason,
        "handoff_created": False,
        "prepared": False,
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "memory_written": False,
        "capability_expansion": False,
        "automatic_permission_grant": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
        **extra,
    }


def _reject(reason: str, **extra: Any) -> dict[str, Any]:
    out = _hold(reason, **extra)
    out["status"] = STATUS_REJECTED
    return out


def _git_head(repo: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        timeout=20,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip().lower()


def _plain_mapping(value: Mapping[str, Any] | None, field_name: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(value, Mapping):
        return None, _hold(f"{field_name}_REQUIRED")
    return dict(value), None


def _evidence_id(record: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _verify_optional_declared_hash(record: Mapping[str, Any], hash_field: str) -> tuple[bool, str | None]:
    digest = record.get(hash_field)
    if digest in (None, ""):
        return True, None
    if not (isinstance(digest, str) and _HEX64.fullmatch(digest.lower())):
        return False, f"{hash_field.upper()}_INVALID"
    if _canonical_hash(_without_hash_fields(record)) != digest.lower():
        return False, f"{hash_field.upper()}_MISMATCH"
    return True, None


def _validate_mission(mission: Mapping[str, Any], targets: tuple[str, ...]) -> tuple[bool, dict[str, Any]]:
    mission_id = _evidence_id(mission, "mission_id", "human_mission_id")
    if not mission_id:
        return False, {"mission_reason": "MISSION_ID_REQUIRED"}

    state = str(mission.get("status") or mission.get("state") or mission.get("phase") or "").upper()
    if bool(mission.get("revoked")) or state == "REVOKED":
        return False, {"mission_reason": "MISSION_REVOKED", "mission_id": mission_id}
    if bool(mission.get("closed")) or state in {"CLOSED", "COMPLETED", "PLAN_COMPLETED", "ABORTED"}:
        return False, {"mission_reason": "MISSION_CLOSED", "mission_id": mission_id, "mission_state": state}
    if state and state not in {"ACTIVE", "MISSION_ACTIVE", "PLAN_BOUND", "WORKTREE_BOUND", "ACTION_PREPARED"}:
        return False, {"mission_reason": "MISSION_NOT_ACTIVE", "mission_id": mission_id, "mission_state": state}

    allowed_targets = tuple(
        str(v).replace("\\", "/").lstrip("./")
        for v in (mission.get("allowed_target_paths") or mission.get("allowed_targets") or ())
    )
    if not allowed_targets:
        return False, {"mission_reason": "MISSION_TARGET_SCOPE_REQUIRED", "mission_id": mission_id}
    if not set(targets).issubset(set(allowed_targets)):
        return False, {"mission_reason": "MISSION_TARGET_SCOPE_EXCEEDED", "mission_id": mission_id}

    operations = tuple(str(v).upper() for v in (mission.get("allowed_operation_shapes") or mission.get("allowed_operations") or ()))
    if operations and "UPDATE_TARGET_FROM_SOURCE" not in operations and "APPLY_PATCH" not in operations:
        return False, {"mission_reason": "MISSION_OPERATION_NOT_ALLOWED", "mission_id": mission_id}

    tools = tuple(str(v).upper() for v in (mission.get("allowed_tools") or ()))
    forbidden_tools = {"SHELL", "NETWORK", "GIT_COMMIT", "GIT_PUSH", "GIT_MERGE", "MEMORY_WRITE", "KX108", "HUMANAPPROVAL"}
    if set(tools) & forbidden_tools:
        return False, {"mission_reason": "MISSION_TOOL_ESCALATION", "mission_id": mission_id}

    max_actions = mission.get("max_actions")
    executed_actions = int(mission.get("executed_actions", mission.get("action_index", 0)) or 0)
    if isinstance(max_actions, int) and executed_actions >= max_actions:
        return False, {"mission_reason": "MISSION_ACTION_BUDGET_EXHAUSTED", "mission_id": mission_id}

    max_iterations = mission.get("max_iterations", mission.get("max_retries_per_action"))
    used_iterations = int(mission.get("used_iterations", mission.get("iteration_index", 0)) or 0)
    if isinstance(max_iterations, int) and used_iterations >= max_iterations:
        return False, {"mission_reason": "MISSION_ITERATION_BUDGET_EXHAUSTED", "mission_id": mission_id}

    return True, {
        "mission_id": mission_id,
        "mission_scope_bound": True,
        "mission_budget_bound": isinstance(max_actions, int) or isinstance(max_iterations, int),
        "mission_revocation_enforced": True,
        "allowed_target_paths": allowed_targets,
    }


def _require_bound_evidence(
    record: Mapping[str, Any] | None,
    *,
    kind: str,
    id_fields: tuple[str, ...],
    hash_field: str,
    candidate_patch_hash: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    if not isinstance(record, Mapping):
        return False, {"reason": f"{kind}_REQUIRED"}
    payload = dict(record)
    record_id = _evidence_id(payload, *id_fields)
    if not record_id:
        return False, {"reason": f"{kind}_ID_REQUIRED"}
    status = str(payload.get("status") or payload.get("verification_status") or payload.get("result") or "").upper()
    if status not in {"VERIFIED", "VALIDATED", "PASS", "PASSED"}:
        return False, {"reason": f"{kind}_NOT_VERIFIED", f"{kind.lower()}_id": record_id}
    ok, why = _verify_optional_declared_hash(payload, hash_field)
    if not ok:
        return False, {"reason": why or f"{kind}_HASH_INVALID", f"{kind.lower()}_id": record_id}
    if candidate_patch_hash is not None:
        bound = payload.get("candidate_patch_hash") or payload.get("tested_patch_hash")
        if bound != candidate_patch_hash:
            return False, {"reason": f"{kind}_PATCH_HASH_MISMATCH", f"{kind.lower()}_id": record_id}
    return True, {f"{kind.lower()}_id": record_id, f"{kind.lower()}_hash": payload.get(hash_field)}


def _phase1_plan(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    plan = candidate.get("plan")
    return plan if isinstance(plan, Mapping) else {}


def _phase1_targets(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    plan = _phase1_plan(candidate)
    files = candidate.get("candidate_files") or plan.get("candidate_patch_files") or plan.get("candidate_files") or ()
    return tuple(sorted(str(v).replace("\\", "/").lstrip("./") for v in files if str(v).strip()))


def _phase1_patch_source(candidate: Mapping[str, Any]) -> str:
    plan = _phase1_plan(candidate)
    value = plan.get("candidate_patch_source") or candidate.get("candidate_patch_source")
    return str(value or "").strip()


def _phase1_objective(candidate: Mapping[str, Any]) -> str:
    plan = _phase1_plan(candidate)
    return str(plan.get("display_objective") or candidate.get("objective") or "Bounded self-build candidate")


def _validate_phase1_candidate(
    phase1_candidate: Mapping[str, Any],
    *,
    base_commit_sha: str,
    execution_worktree_path: Path,
    repo_root: Path,
) -> tuple[bool, dict[str, Any]]:
    if phase1_candidate.get("status") != "PLAN_PROPOSED":
        return False, _hold("PHASE1_PLAN_NOT_PROPOSED", phase1_status=phase1_candidate.get("status"))
    if phase1_candidate.get("phase2_executed") is not False:
        return False, _reject("PHASE1_ALREADY_EXECUTED")
    if phase1_candidate.get("repo_mutation") is True or phase1_candidate.get("mutated_repo") is True:
        return False, _reject("PHASE1_REPO_MUTATION_REPORTED")
    if phase1_candidate.get("human_approval_synthesized") is True or phase1_candidate.get("approval_token_exposed") is True:
        return False, _reject("PHASE1_AUTHORIZATION_MATERIAL_PRESENT")

    patch_ref = _phase1_patch_source(phase1_candidate)
    if not patch_ref:
        return False, _hold("CANDIDATE_PATCH_SOURCE_REQUIRED")
    patch_path = Path(patch_ref).resolve()
    try:
        patch_path.relative_to(repo_root.resolve())
        return False, _reject("CANDIDATE_PATCH_INSIDE_REPO")
    except ValueError:
        pass
    if not patch_path.is_file():
        return False, _hold("CANDIDATE_PATCH_NOT_FOUND", candidate_patch_source=patch_ref)
    patch_content = patch_path.read_text(encoding="utf-8")
    patch_hash = _sha256_text(patch_content)
    expected_hash = str(phase1_candidate.get("candidate_patch_hash") or _phase1_plan(phase1_candidate).get("candidate_patch_hash") or "").lower()
    if not _HEX64.fullmatch(expected_hash):
        return False, _hold("CANDIDATE_PATCH_HASH_REQUIRED")
    if patch_hash != expected_hash:
        return False, _reject("CANDIDATE_PATCH_HASH_MISMATCH", expected=expected_hash, actual=patch_hash)

    plan_base = str(_phase1_plan(phase1_candidate).get("base_sha") or phase1_candidate.get("base_sha") or "").lower()
    if plan_base and plan_base != base_commit_sha:
        return False, _hold("BASE_SHA_MISMATCH", expected=base_commit_sha, actual=plan_base)
    worktree_head = _git_head(execution_worktree_path)
    if worktree_head and worktree_head != base_commit_sha:
        return False, _hold("WORKTREE_BASE_SHA_MISMATCH", expected=base_commit_sha, actual=worktree_head)

    declared_targets = _phase1_targets(phase1_candidate)
    if not declared_targets:
        return False, _hold("CANDIDATE_FILES_REQUIRED")
    patch_targets, err = _parse_patch_targets(patch_content, execution_worktree_path)
    if err:
        return False, _reject("PATCH_TARGETS_INVALID:" + str(err))
    parsed_targets = tuple(sorted(str(v).replace("\\", "/").lstrip("./") for v in patch_targets or ()))
    if parsed_targets != declared_targets:
        return False, _reject("CANDIDATE_TARGET_SUBSTITUTION", declared_targets=declared_targets, patch_targets=parsed_targets)

    lowered = patch_content.lower()
    matched = tuple(pattern for pattern in _FORBIDDEN_NON_AMPLIFICATION_PATTERNS if pattern.lower() in lowered)
    if matched:
        return False, _reject("NON_AMPLIFICATION_HOLD_REQUIRED", forbidden_patterns=matched)

    return True, {
        "patch_content": patch_content,
        "candidate_patch_hash": patch_hash,
        "candidate_targets": declared_targets,
        "candidate_patch_source": patch_ref,
    }


def adapt_self_build_candidate_to_r9_prepare(
    *,
    phase1_candidate: Mapping[str, Any],
    mission_context: Mapping[str, Any],
    inventory_snapshot: Mapping[str, Any] | None,
    deficiency_evidence: Mapping[str, Any] | None,
    validation_evidence: Mapping[str, Any] | None,
    base_commit_sha: str,
    repo_identity_ref: str = REPO_REF_DEFAULT,
    execution_worktree_path: str | Path,
    main_worktree_path: str | Path,
    branch_name: str,
    stores_base_dir: str | Path,
    session_id: str = "",
) -> dict[str, Any]:
    if not _HEX40.fullmatch(str(base_commit_sha or "").lower()):
        return _hold("BASE_COMMIT_SHA_INVALID")

    if not isinstance(phase1_candidate, Mapping):
        return _hold("PHASE1_CANDIDATE_REQUIRED")

    base_sha = str(base_commit_sha).lower()
    exec_root = Path(execution_worktree_path).resolve()
    main_root = Path(main_worktree_path).resolve()

    candidate_ok, candidate_payload = _validate_phase1_candidate(
        phase1_candidate,
        base_commit_sha=base_sha,
        execution_worktree_path=exec_root,
        repo_root=main_root,
    )
    if not candidate_ok:
        return candidate_payload

    targets = tuple(candidate_payload["candidate_targets"])
    mission_ok, mission_payload = _validate_mission(mission_context, targets)
    if not mission_ok:
        return _hold(mission_payload["mission_reason"], mission=mission_payload)

    inventory_ok, inventory_payload = _require_bound_evidence(
        inventory_snapshot,
        kind="INVENTORY_SNAPSHOT",
        id_fields=("inventory_snapshot_id", "snapshot_id", "id"),
        hash_field="inventory_snapshot_hash",
    )
    if not inventory_ok:
        return _hold(inventory_payload["reason"], mission=mission_payload)

    deficiency_ok, deficiency_payload = _require_bound_evidence(
        deficiency_evidence,
        kind="DEFICIENCY_EVIDENCE",
        id_fields=("deficiency_evidence_id", "deficiency_id", "id"),
        hash_field="deficiency_evidence_hash",
    )
    if not deficiency_ok:
        return _hold(deficiency_payload["reason"], mission=mission_payload, inventory=inventory_payload)

    validation_ok, validation_payload = _require_bound_evidence(
        validation_evidence,
        kind="VALIDATION_EVIDENCE",
        id_fields=("validation_evidence_id", "validation_id", "id"),
        hash_field="validation_evidence_hash",
        candidate_patch_hash=candidate_payload["candidate_patch_hash"],
    )
    if not validation_ok:
        return _hold(validation_payload["reason"], mission=mission_payload, inventory=inventory_payload, deficiency=deficiency_payload)

    patch_content = candidate_payload["patch_content"]
    patch_hash = candidate_payload["candidate_patch_hash"]

    r9_proposal = ObsidureBuilderProposalV1(
        objective=_phase1_objective(phase1_candidate),
        proposal_kind="BUILD",
        base_commit_sha=base_sha,
        target_scope=targets,
        files_touched=targets,
        candidate_patch_ref=BuilderPatchRef(PATCH_REF, patch_hash),
        source_context_refs=(
            mission_payload["mission_id"],
            inventory_payload["inventory_snapshot_id"],
            deficiency_payload["deficiency_evidence_id"],
            validation_payload["validation_evidence_id"],
        ),
        input_artifact_refs=(candidate_payload["candidate_patch_source"],),
        tests_proposed=("self-build-validation-evidence",),
        proof_obligations=("non-amplification-review",),
        risk_notes=("self-build prepare only; generated code grants no authority",),
        unknowns=("semantic non-amplification is bounded by explicit evidence and forbidden-pattern checks",),
        provider_ref="OBSIDIA_NATIVE_SELF_BUILD_PHASE1",
        builder_ref="OBSIDURE_SELF_BUILD_R11_B1",
        created_from="SelfBuildPhase1Candidate",
        declared_evidence={
            "phase1_status": phase1_candidate.get("status"),
            "phase2_executed": phase1_candidate.get("phase2_executed"),
            "repo_mutation": phase1_candidate.get("repo_mutation"),
            "candidate_patch_hash": patch_hash,
            "candidate_files": targets,
            "human_mission_id": mission_payload["mission_id"],
            "inventory_snapshot_id": inventory_payload["inventory_snapshot_id"],
            "deficiency_evidence_id": deficiency_payload["deficiency_evidence_id"],
            "validation_evidence_id": validation_payload["validation_evidence_id"],
            "plan_is_not_authority": True,
            "validated_is_not_authorized": True,
        },
        metadata={
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "non_amplification_check": "FORBIDDEN_PATTERN_AND_BOUNDARY_CHECK",
        },
    )

    patch_artifact = ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref=PATCH_REF,
        content_sha256=patch_hash,
        artifact_format="REAL_UNIFIED_DIFF_V1",
        schema_ref="REAL_UNIFIED_DIFF_V1",
    )
    validation_artifact = ArtifactRef(
        artifact_kind="TEST_RESULT",
        logical_ref=validation_payload["validation_evidence_id"],
        content_sha256=_canonical_hash(dict(validation_evidence or {})),
        artifact_format="SELF_BUILD_VALIDATION_EVIDENCE",
        schema_ref="R11_B1_VALIDATION_EVIDENCE",
    )
    inventory_artifact = ArtifactRef(
        artifact_kind="BUILD_MANIFEST",
        logical_ref=inventory_payload["inventory_snapshot_id"],
        content_sha256=_canonical_hash(dict(inventory_snapshot or {})),
        artifact_format="INVENTORY_SNAPSHOT",
        schema_ref="R11_B1_INVENTORY_SNAPSHOT",
    )
    deficiency_artifact = ArtifactRef(
        artifact_kind="PROVIDER_OUTPUT",
        logical_ref=deficiency_payload["deficiency_evidence_id"],
        content_sha256=_canonical_hash(dict(deficiency_evidence or {})),
        artifact_format="DEFICIENCY_EVIDENCE",
        schema_ref="R11_B1_DEFICIENCY_EVIDENCE",
    )
    validation_record = EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=r9_proposal.proposal_id,
        producer_ref="R11_B1_SELF_BUILD_VALIDATION",
        verification_status=EVIDENCE_STATUS_VERIFIED,
        artifact_ref=validation_artifact,
        scope=targets,
        result="PASS",
        provenance={
            "candidate_patch_hash": patch_hash,
            "inventory_snapshot_id": inventory_payload["inventory_snapshot_id"],
            "deficiency_evidence_id": deficiency_payload["deficiency_evidence_id"],
            "validation_evidence_id": validation_payload["validation_evidence_id"],
        },
    )
    non_amp_record = EvidenceRecord(
        evidence_kind="MANIFEST_EVIDENCE",
        subject_ref=r9_proposal.proposal_id,
        producer_ref="R11_B1_NON_AMPLIFICATION_CHECK",
        verification_status=EVIDENCE_STATUS_VERIFIED,
        artifact_ref=inventory_artifact,
        scope=targets,
        result="PASS",
        provenance={
            "forbidden_patterns_checked": list(_FORBIDDEN_NON_AMPLIFICATION_PATTERNS),
            "capability_expansion": False,
        },
    )
    manifest = build_proposal_manifest(
        r9_proposal,
        candidate_artifacts=(patch_artifact, validation_artifact, inventory_artifact, deficiency_artifact),
        evidence_records=(validation_record, non_amp_record),
        verification_obligations=("self-build-validation-evidence", "non-amplification-review"),
        repo_identity_ref=repo_identity_ref,
    )
    policy = ValidationPolicy(
        obligations=(
            ValidationObligation(
                obligation_kind="UNIT_TEST",
                target="self-build-validation-evidence",
                scope=targets,
                required=True,
                expected_evidence_kind="TEST_RESULT_EVIDENCE",
                allow_observed=False,
            ),
            ValidationObligation(
                obligation_kind="CUSTOM_TYPED",
                target="non-amplification-review",
                scope=targets,
                required=True,
                expected_evidence_kind="MANIFEST_EVIDENCE",
                allow_observed=False,
            ),
        )
    )
    validation = validate_obsidure_proposal(r9_proposal, manifest, validation_policy=policy)
    if validation.validation_verdict != "VALID":
        return {
            **_hold("R9_B3_VALIDATION_NOT_VALID"),
            "r9_proposal": r9_proposal,
            "r9_manifest": manifest,
            "r9_validation": validation,
            "validation_verdict": validation.validation_verdict,
            "mission": mission_payload,
            "inventory": inventory_payload,
            "deficiency": deficiency_payload,
        }

    handoff = build_governance_handoff(
        r9_proposal,
        manifest,
        validation,
        source_metadata={
            "r11_adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "mission_id": mission_payload["mission_id"],
            "inventory_snapshot_id": inventory_payload["inventory_snapshot_id"],
            "deficiency_evidence_id": deficiency_payload["deficiency_evidence_id"],
            "validation_evidence_id": validation_payload["validation_evidence_id"],
            "candidate_patch_hash": patch_hash,
        },
    )
    prepared = prepare_obsidure_governed_patch_action(
        handoff=handoff,
        proposal=r9_proposal,
        manifest=manifest,
        validation=validation,
        patch_content=patch_content,
        current_base_sha=base_sha,
        current_repo_identity_ref=repo_identity_ref,
        execution_worktree_path=execution_worktree_path,
        main_worktree_path=main_worktree_path,
        branch_name=branch_name,
        stores_base_dir=stores_base_dir,
        session_id=session_id,
    )
    ok = prepared.get("status") == PREPARED_AWAITING_HUMAN_APPROVAL
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PREPARED if ok else STATUS_HELD,
        "reason": None if ok else prepared.get("reason"),
        "phase1_candidate_bound": True,
        "inventory_snapshot_bound": True,
        "deficiency_evidence_bound": True,
        "human_mission_bound": True,
        "non_amplification_check": "PASS",
        "r9_proposal": r9_proposal,
        "r9_manifest": manifest,
        "r9_validation": validation,
        "r9_handoff": handoff,
        "prepared_action": prepared,
        "patch_content": patch_content,
        "candidate_patch_hash": patch_hash,
        "self_build_lineage": {
            "mission_id": mission_payload["mission_id"],
            "inventory_snapshot_id": inventory_payload["inventory_snapshot_id"],
            "deficiency_evidence_id": deficiency_payload["deficiency_evidence_id"],
            "validation_evidence_id": validation_payload["validation_evidence_id"],
            "r9_proposal_id": r9_proposal.proposal_id,
            "r9_manifest_id": manifest.manifest_id,
            "r9_validation_id": validation.validation_id,
            "r9_handoff_id": handoff.handoff_id,
        },
        "mission": mission_payload,
        "handoff_created": True,
        "prepared": ok,
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "memory_written": False,
        "capability_expansion": False,
        "automatic_permission_grant": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_PREPARED",
    "STATUS_REJECTED",
    "adapt_self_build_candidate_to_r9_prepare",
]
