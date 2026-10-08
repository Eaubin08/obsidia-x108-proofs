from __future__ import annotations

"""R10-B1 canonical repair adapter.

This module converts already-tested Obsidure repair evidence into the existing
R9 builder pipeline. It does not create a repair engine, approval, KX108
decision, executor call, commit, push, or merge.
"""

import dataclasses
import difflib
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL
from obsidure_builder_proposal_v1 import (
    BuilderPatchRef,
    ObsidureBuilderProposalV1,
    from_repair_proposal,
)
from obsidure_governance_handoff_v1 import build_governance_handoff
from obsidure_governed_patch_prepare_adapter_v1 import prepare_obsidure_governed_patch_action
from obsidure_proposal_manifest_v1 import (
    ArtifactRef,
    EVIDENCE_STATUS_DECLARED,
    EVIDENCE_STATUS_OBSERVED,
    EVIDENCE_STATUS_VERIFIED,
    EvidenceRecord,
    build_proposal_manifest,
)
from obsidure_proposal_validation_v1 import (
    ValidationObligation,
    ValidationPolicy,
    validate_obsidure_proposal,
)

from periphery.agents.obsidure_repair_contract import (
    RepairProposal,
    assert_repair_boundary,
    validate_repair_proposal,
)


ADAPTER_SCHEMA_VERSION = "OBSIDURE_REPAIR_R9_ADAPTER_V1"
STATUS_PREPARED = "R10_REPAIR_PREPARED"
STATUS_HELD = "R10_REPAIR_HELD"
STATUS_STOPPED = "R10_REPAIR_STOPPED"

RESULT_VALIDATED = "VALIDATED_REPAIR_SANDBOX_PASS"
REPO_REF_DEFAULT = "obsidia-openjarvis-install-v0"
PATCH_REF = "repair_candidate.patch"
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _g(obj: Any, field: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(field, default)
    return getattr(obj, field, default)


def _asdict(obj: Any) -> dict[str, Any]:
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, Mapping):
        return dict(obj)
    return dict(getattr(obj, "__dict__", {}))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
        **extra,
    }


def _stop(reason: str, **extra: Any) -> dict[str, Any]:
    out = _hold(reason, **extra)
    out["status"] = STATUS_STOPPED
    return out


def _repair_attempt_ids(request: Any, proposal: Any, verdict: Any, c278: Any) -> dict[str, str]:
    return {
        "repair_request_id": str(_g(request, "request_id", "") or ""),
        "repair_proposal_id": str(_g(proposal, "proposal_id", "") or ""),
        "repair_verdict_id": str(_g(verdict, "verdict_id", "") or ""),
        "c278_request_id": str(_g(c278, "request_id", "") or ""),
        "c278_proposal_id": str(_g(c278, "proposal_id", "") or ""),
    }


def _repair_failure_digest(request: Any) -> str:
    payload = {
        "failure_mode": _g(request, "failure_mode", ""),
        "summary": _g(request, "summary", ""),
        "error_contexts": _g(request, "error_contexts", ()) or (),
        "repo_targets": _g(request, "repo_targets", ()) or (),
        "attempts_spent": _g(request, "attempts_spent", 0) or 0,
    }
    return _sha256_text(_canonical_json(payload))


def _validate_stop_conditions(
    *,
    request: Any,
    tested_patch_hash: str,
    attempt_history: tuple[Mapping[str, Any], ...],
    repair_budget: int | None,
) -> tuple[bool, dict[str, Any]]:
    failure_digest = _repair_failure_digest(request)
    attempts_spent = int(_g(request, "attempts_spent", 0) or 0)
    if repair_budget is not None and attempts_spent >= repair_budget:
        return True, {
            "stop_reason": "REPAIR_BUDGET_EXHAUSTED",
            "failure_digest": failure_digest,
            "attempts_spent": attempts_spent,
            "repair_budget": repair_budget,
        }

    previous_failures = [str(item.get("failure_digest") or "") for item in attempt_history]
    if failure_digest in previous_failures:
        return True, {
            "stop_reason": "REPEATED_IDENTICAL_FAILURE",
            "failure_digest": failure_digest,
        }

    state_sequence = [
        str(item.get("repair_state_digest") or item.get("tested_patch_hash") or "")
        for item in attempt_history
    ]
    state_sequence.append(tested_patch_hash)
    state_sequence = [item for item in state_sequence if item]
    if len(state_sequence) >= 3 and state_sequence[-1] == state_sequence[-3] and state_sequence[-1] != state_sequence[-2]:
        return True, {
            "stop_reason": "OSCILLATING_REPAIR_STATE",
            "oscillation_state": state_sequence[-1],
        }
    oscillation_status = "UNKNOWN" if len(state_sequence) < 3 else "NOT_DETECTED"
    return False, {
        "failure_digest": failure_digest,
        "oscillation_status": oscillation_status,
    }


def _validate_mission_boundary(
    mission_context: Mapping[str, Any] | None,
    *,
    targets: tuple[str, ...],
    repair_budget: int | None,
    require_delegation: bool,
) -> tuple[bool, dict[str, Any]]:
    if mission_context is None:
        if require_delegation:
            return False, {"mission_status": "HELD", "mission_reason": "MISSION_CONTEXT_REQUIRED"}
        return True, {
            "mission_status": "EXPLICIT_HUMAN_AUTHORIZATION_RAIL_AVAILABLE",
            "mission_scope_bound": False,
            "mission_budget_bound": False,
            "mission_revocation_enforced": False,
        }

    state = str(mission_context.get("status") or mission_context.get("phase") or "").upper()
    revoked = bool(mission_context.get("revoked")) or state == "REVOKED"
    closed = state in {"CLOSED", "COMPLETED", "PLAN_COMPLETED"}
    if revoked:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_REVOKED"}
    if closed:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_CLOSED"}
    if state and state not in {"ACTIVE", "PLAN_BOUND", "MISSION_ACTIVE"}:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_NOT_ACTIVE", "mission_state": state}

    allowed_targets = tuple(str(v).replace("\\", "/").lstrip("./") for v in mission_context.get("allowed_targets", ()) or ())
    if allowed_targets and not set(targets).issubset(set(allowed_targets)):
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_TARGET_SCOPE_EXCEEDED"}

    allowed_operations = tuple(str(v).upper() for v in mission_context.get("allowed_operations", ()) or ())
    if allowed_operations and "APPLY_PATCH" not in allowed_operations and "REPAIR" not in allowed_operations:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_OPERATION_NOT_ALLOWED"}

    allowed_tools = tuple(str(v).upper() for v in mission_context.get("allowed_tools", ()) or ())
    if allowed_tools and "APPLY_PATCH" not in allowed_tools and "EDIT" not in allowed_tools:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_TOOL_NOT_ALLOWED"}

    max_attempts = mission_context.get("max_attempts")
    attempt_index = int(mission_context.get("attempt_index", 0) or 0)
    if isinstance(max_attempts, int) and attempt_index >= max_attempts:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_ATTEMPT_BUDGET_EXHAUSTED"}

    max_actions = mission_context.get("max_actions")
    executed_actions = int(mission_context.get("executed_actions", 0) or 0)
    if isinstance(max_actions, int) and executed_actions >= max_actions:
        return False, {"mission_status": "HELD", "mission_reason": "MISSION_ACTION_BUDGET_EXHAUSTED"}

    if repair_budget is not None and attempt_index >= repair_budget:
        return False, {"mission_status": "HELD", "mission_reason": "REPAIR_BUDGET_EXHAUSTED"}

    return True, {
        "mission_status": "MISSION_SCOPE_VERIFIED",
        "mission_scope_bound": bool(allowed_targets),
        "mission_budget_bound": isinstance(max_attempts, int) or isinstance(max_actions, int) or repair_budget is not None,
        "mission_revocation_enforced": True,
    }


def _candidate_records(proposal: Any) -> tuple[Mapping[str, Any], ...]:
    data = _asdict(proposal)
    candidates = data.get("candidate_files") or ()
    out: list[Mapping[str, Any]] = []
    for candidate in candidates:
        out.append(_asdict(candidate))
    return tuple(out)


def _target_path(candidate: Mapping[str, Any]) -> str:
    path = str(candidate.get("path") or "").replace("\\", "/").lstrip("./")
    if not path:
        raise ValueError("CANDIDATE_PATH_MISSING")
    return path


def _artifact_hashes(verdict: Any) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for artifact in _g(verdict, "tested_artifacts", ()) or ():
        path = str(_g(artifact, "path", "") or "").replace("\\", "/").lstrip("./")
        digest = str(_g(artifact, "sha256", "") or "").lower()
        if path and _HEX64.fullmatch(digest):
            hashes[path] = digest
    return hashes


def _unified_diff_for_candidate(base_text: str, new_text: str, rel: str) -> str:
    diff = difflib.unified_diff(
        base_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"a/{rel}",
        tofile=f"b/{rel}",
        lineterm="\n",
    )
    text = "".join(diff)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def _build_patch_from_repair(
    *,
    proposal: Any,
    verdict: Any,
    execution_worktree_path: Path,
) -> tuple[str, tuple[str, ...], dict[str, str]]:
    artifacts = _artifact_hashes(verdict)
    chunks: list[str] = []
    targets: list[str] = []
    tested_hashes: dict[str, str] = {}

    for candidate in _candidate_records(proposal):
        rel = _target_path(candidate)
        if rel in targets:
            raise ValueError("DUPLICATE_REPAIR_TARGET")
        full_content = str(candidate.get("full_content") or "")
        if not full_content.strip():
            raise ValueError("CANDIDATE_CONTENT_EMPTY")
        target = execution_worktree_path / rel
        try:
            resolved = target.resolve()
            resolved.relative_to(execution_worktree_path.resolve())
        except (OSError, ValueError) as exc:
            raise ValueError("TARGET_PATH_ESCAPES_EXECUTION_WORKTREE") from exc
        if target.is_symlink():
            raise ValueError("TARGET_IS_SYMLINK")
        if not target.exists() or not target.is_file():
            raise ValueError("TARGET_MISSING_IN_EXECUTION_WORKTREE")
        before_bytes = target.read_bytes()
        before_hash = _sha256_bytes(before_bytes)
        base_hash = str(candidate.get("base_sha256") or "").lower()
        if base_hash and base_hash != before_hash:
            raise ValueError("BASE_SHA_DRIFT")
        tested = artifacts.get(rel)
        candidate_hash = _sha256_text(full_content)
        if not tested:
            raise ValueError("TESTED_ARTIFACT_HASH_MISSING")
        if tested != candidate_hash:
            raise ValueError("TESTED_PATCH_SUBSTITUTION")
        diff = _unified_diff_for_candidate(before_bytes.decode("utf-8"), full_content, rel)
        if not diff:
            raise ValueError("NO_REPAIR_PATCH_CHANGES")
        chunks.append(diff)
        targets.append(rel)
        tested_hashes[rel] = tested

    if not chunks:
        raise ValueError("NO_REPAIR_CANDIDATES")
    return "".join(chunks), tuple(targets), tested_hashes


def _normalize_verified_status(evidence_verification: str) -> str:
    status = str(evidence_verification or "").strip().upper()
    if status == EVIDENCE_STATUS_VERIFIED:
        return EVIDENCE_STATUS_VERIFIED
    if status == EVIDENCE_STATUS_OBSERVED:
        return EVIDENCE_STATUS_OBSERVED
    return EVIDENCE_STATUS_DECLARED


def adapt_validated_repair_to_r9_prepare(
    *,
    repair_request: Any,
    repair_proposal: RepairProposal | Mapping[str, Any],
    c278_evidence: Any,
    repair_verdict: Any,
    base_commit_sha: str,
    repo_identity_ref: str = REPO_REF_DEFAULT,
    execution_worktree_path: str | Path,
    main_worktree_path: str | Path,
    branch_name: str,
    stores_base_dir: str | Path,
    session_id: str = "",
    evidence_verification: str = EVIDENCE_STATUS_VERIFIED,
    mission_context: Mapping[str, Any] | None = None,
    require_delegation: bool = False,
    attempt_history: tuple[Mapping[str, Any], ...] = (),
    repair_budget: int | None = None,
) -> dict[str, Any]:
    ids = _repair_attempt_ids(repair_request, repair_proposal, repair_verdict, c278_evidence)
    if not _HEX40.fullmatch(str(base_commit_sha or "").lower()):
        return _hold("BASE_COMMIT_SHA_INVALID", **ids)

    try:
        assert_repair_boundary(_g(repair_request, "boundary", {}) or {})
        assert_repair_boundary(_g(repair_proposal, "boundary", {}) or {})
        assert_repair_boundary(_g(repair_verdict, "boundary", {}) or {})
    except ValueError as exc:
        return _hold("REPAIR_BOUNDARY_VIOLATION", detail=str(exc), **ids)

    if not ids["repair_request_id"] or not ids["repair_proposal_id"]:
        return _hold("REPAIR_ATTEMPT_ID_MISSING", **ids)
    if _g(repair_proposal, "request_id", "") != ids["repair_request_id"]:
        return _hold("REPAIR_PROPOSAL_REQUEST_MISMATCH", **ids)
    if _g(repair_verdict, "request_id", "") != ids["repair_request_id"]:
        return _hold("REPAIR_VERDICT_REQUEST_MISMATCH", **ids)
    if _g(repair_verdict, "proposal_id", "") != ids["repair_proposal_id"]:
        return _hold("REPAIR_VERDICT_PROPOSAL_MISMATCH", **ids)
    if ids["c278_request_id"] != ids["repair_request_id"] or ids["c278_proposal_id"] != ids["repair_proposal_id"]:
        return _hold("C278_REPAIR_ATTEMPT_MISMATCH", **ids)
    if str(_g(c278_evidence, "evidence", "") or "").upper() != "CONTINUOUS":
        return _hold("C278_NOT_CONTINUOUS", c278_evidence=str(_g(c278_evidence, "evidence", "")), **ids)
    if str(_g(repair_verdict, "status", "") or "").upper() != "PASS":
        return _hold("REPAIR_VERDICT_NOT_PASS", verdict_status=str(_g(repair_verdict, "status", "")), **ids)

    proposal_errors = validate_repair_proposal(repair_proposal if isinstance(repair_proposal, RepairProposal) else RepairProposal(**dict(repair_proposal)))
    if proposal_errors:
        return _hold("REPAIR_PROPOSAL_INVALID", proposal_errors=proposal_errors, **ids)

    exec_root = Path(execution_worktree_path).resolve()
    try:
        patch_content, targets, tested_hashes = _build_patch_from_repair(
            proposal=repair_proposal,
            verdict=repair_verdict,
            execution_worktree_path=exec_root,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return _hold(str(exc), **ids)
    patch_hash = _sha256_text(patch_content)

    stopped, stop_payload = _validate_stop_conditions(
        request=repair_request,
        tested_patch_hash=patch_hash,
        attempt_history=tuple(attempt_history or ()),
        repair_budget=repair_budget,
    )
    if stopped:
        return _stop(stop_payload["stop_reason"], tested_patch_hash=patch_hash, **ids, **stop_payload)

    mission_ok, mission_payload = _validate_mission_boundary(
        mission_context,
        targets=targets,
        repair_budget=repair_budget,
        require_delegation=require_delegation,
    )
    if not mission_ok:
        return _hold(mission_payload["mission_reason"], tested_patch_hash=patch_hash, **ids, **mission_payload)

    base_proposal = from_repair_proposal(repair_proposal, base_commit_sha=base_commit_sha)
    r9_proposal = ObsidureBuilderProposalV1(
        objective=base_proposal.objective,
        proposal_kind=base_proposal.proposal_kind,
        base_commit_sha=base_proposal.base_commit_sha,
        target_scope=targets,
        files_touched=targets,
        candidate_patch_ref=BuilderPatchRef(PATCH_REF, patch_hash),
        source_context_refs=tuple(str(v) for v in (ids["repair_request_id"], ids["repair_verdict_id"]) if v),
        input_artifact_refs=base_proposal.input_artifact_refs + (ids["repair_verdict_id"],),
        tests_proposed=("repair-sandbox-verdict",),
        proof_obligations=base_proposal.proof_obligations,
        risk_notes=base_proposal.risk_notes,
        unknowns=base_proposal.unknowns,
        provider_ref=base_proposal.provider_ref,
        builder_ref=base_proposal.builder_ref,
        created_from=base_proposal.created_from,
        declared_evidence={
            **dict(base_proposal.declared_evidence),
            "repair_request_id": ids["repair_request_id"],
            "repair_proposal_id": ids["repair_proposal_id"],
            "repair_verdict_id": ids["repair_verdict_id"],
            "c278_evidence": "CONTINUOUS",
            "tested_patch_hash": patch_hash,
            "tested_artifact_hashes": tested_hashes,
            "failure_digest": stop_payload["failure_digest"],
            "declared_not_verified_boundary": "DECLARED != OBSERVED != VERIFIED",
        },
        metadata={
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "oscillation_status": stop_payload.get("oscillation_status", "UNKNOWN"),
        },
    )

    patch_artifact = ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref=PATCH_REF,
        content_sha256=patch_hash,
        artifact_format="REAL_UNIFIED_DIFF_V1",
        schema_ref="REAL_UNIFIED_DIFF_V1",
    )
    test_artifact = ArtifactRef(
        artifact_kind="TEST_RESULT",
        logical_ref=ids["repair_verdict_id"],
        content_sha256=_sha256_text(_canonical_json(_asdict(repair_verdict))),
        artifact_format="REPAIR_VERDICT",
        schema_ref="RepairVerdict",
    )
    status = _normalize_verified_status(evidence_verification)
    evidence = EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=r9_proposal.proposal_id,
        producer_ref="OBSIDURE_REPAIR_SANDBOX",
        verification_status=status,
        artifact_ref=test_artifact if status != EVIDENCE_STATUS_DECLARED else None,
        scope=targets,
        result=RESULT_VALIDATED if status == EVIDENCE_STATUS_VERIFIED else "DECLARED_ONLY",
        provenance={
            "base_commit_sha": base_commit_sha,
            "repair_request_id": ids["repair_request_id"],
            "repair_proposal_id": ids["repair_proposal_id"],
            "repair_verdict_id": ids["repair_verdict_id"],
            "c278_evidence": "CONTINUOUS",
            "tested_artifact_hashes": tested_hashes,
            "tested_patch_hash": patch_hash,
        },
    )
    manifest = build_proposal_manifest(
        r9_proposal,
        candidate_artifacts=(patch_artifact, test_artifact),
        evidence_records=(evidence,),
        verification_obligations=("repair-sandbox-verdict",),
        repo_identity_ref=repo_identity_ref,
    )
    policy = ValidationPolicy(
        obligations=(
            ValidationObligation(
                obligation_kind="UNIT_TEST",
                target="repair-sandbox-verdict",
                scope=targets,
                required=True,
                expected_evidence_kind="TEST_RESULT_EVIDENCE",
                allow_observed=False,
            ),
        )
    )
    validation = validate_obsidure_proposal(r9_proposal, manifest, validation_policy=policy)
    if validation.validation_verdict != "VALID":
        return {
            **_hold("R9_B3_VALIDATION_NOT_VALID", **ids),
            "r9_proposal": r9_proposal,
            "r9_manifest": manifest,
            "r9_validation": validation,
            "validation_verdict": validation.validation_verdict,
            "tested_patch_hash": patch_hash,
            "mission": mission_payload,
            "stop_conditions": stop_payload,
        }

    handoff = build_governance_handoff(r9_proposal, manifest, validation, source_metadata={
        "repair_request_id": ids["repair_request_id"],
        "repair_proposal_id": ids["repair_proposal_id"],
        "repair_verdict_id": ids["repair_verdict_id"],
        "c278_evidence": "CONTINUOUS",
        "failure_digest": stop_payload["failure_digest"],
    })
    prepared = prepare_obsidure_governed_patch_action(
        handoff=handoff,
        proposal=r9_proposal,
        manifest=manifest,
        validation=validation,
        patch_content=patch_content,
        current_base_sha=base_commit_sha,
        current_repo_identity_ref=repo_identity_ref,
        execution_worktree_path=execution_worktree_path,
        main_worktree_path=main_worktree_path,
        branch_name=branch_name,
        stores_base_dir=stores_base_dir,
        session_id=session_id,
    )
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PREPARED if prepared.get("status") == PREPARED_AWAITING_HUMAN_APPROVAL else STATUS_HELD,
        "reason": None if prepared.get("status") == PREPARED_AWAITING_HUMAN_APPROVAL else prepared.get("reason"),
        "r9_proposal": r9_proposal,
        "r9_manifest": manifest,
        "r9_validation": validation,
        "r9_handoff": handoff,
        "prepared_action": prepared,
        "patch_content": patch_content,
        "tested_patch_hash": patch_hash,
        "repair_lineage": ids,
        "mission": mission_payload,
        "stop_conditions": stop_payload,
        "handoff_created": True,
        "prepared": prepared.get("status") == PREPARED_AWAITING_HUMAN_APPROVAL,
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_PREPARED",
    "STATUS_STOPPED",
    "adapt_validated_repair_to_r9_prepare",
]
