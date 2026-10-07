from __future__ import annotations

import hashlib
from typing import Any, Mapping

from obsidia_pc_capabilities_v2 import (
    OP_APPLY_PATCH,
    PREPARED_AWAITING_HUMAN_APPROVAL,
    _parse_patch_targets,
    pc_v2_apply_patch_prepare,
)
from obsidure_builder_proposal_v1 import ObsidureBuilderProposalV1
from obsidure_governance_handoff_v1 import (
    ObsidureGovernanceHandoffV1,
    verify_governance_handoff,
)
from obsidure_proposal_manifest_v1 import ObsidureProposalManifestV1
from obsidure_proposal_validation_v1 import ProposalValidationResultV1


ADAPTER_SCHEMA_VERSION = "OBSIDURE_GOVERNED_PATCH_PREPARE_ADAPTER_V1"
STATUS_PREPARED = "PREPARED"
STATUS_REJECTED = "PREPARE_REJECTED"
REASON_STALE_HANDOFF = "STALE_HANDOFF"
REASON_PATCH_DRIFT = "PATCH_DRIFT"
REASON_SCOPE_WIDENING = "SCOPE_WIDENING"
REASON_SCOPE_MISMATCH = "TARGET_SCOPE_MISMATCH"
REASON_REPO_IDENTITY_MISMATCH = "REPO_IDENTITY_MISMATCH"
REASON_LEGACY_BYPASS_REJECTED = "B4_HANDOFF_REQUIRED"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _reject(reason: str, *, session_id: str = "", extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_REJECTED,
        "reason": reason,
        "session_id": session_id,
        "approval_created": False,
        "binder_runtime_called": False,
        "kx108_called": False,
        "executor_invoked": False,
        "physical_mutation": False,
        **dict(extra or {}),
    }


def _lineage_payload(
    handoff: ObsidureGovernanceHandoffV1,
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    validation: ProposalValidationResultV1,
) -> dict[str, str]:
    return {
        "lineage_schema_version": ADAPTER_SCHEMA_VERSION,
        "builder_proposal_id": proposal.proposal_id,
        "builder_manifest_id": manifest.manifest_id,
        "builder_validation_id": validation.validation_id,
        "builder_handoff_id": handoff.handoff_id,
    }


def prepare_obsidure_governed_patch_action(
    *,
    handoff: ObsidureGovernanceHandoffV1,
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    validation: ProposalValidationResultV1,
    patch_content: str,
    current_base_sha: str,
    current_repo_identity_ref: str,
    execution_worktree_path,
    main_worktree_path,
    branch_name: str,
    stores_base_dir,
    session_id: str = "",
) -> dict[str, Any]:
    if not isinstance(handoff, ObsidureGovernanceHandoffV1):
        return _reject(REASON_LEGACY_BYPASS_REJECTED, session_id=session_id)
    ok, reason = verify_governance_handoff(handoff, proposal, manifest, validation)
    if not ok:
        return _reject("HANDOFF_BINDING_INVALID:" + str(reason), session_id=session_id)

    payload = handoff.to_dict()
    if payload.get("requested_action_kind") != "APPLY_PATCH":
        return _reject("HANDOFF_ACTION_KIND_UNSUPPORTED", session_id=session_id)
    if payload.get("repo_identity_ref") != current_repo_identity_ref:
        return _reject(REASON_REPO_IDENTITY_MISMATCH, session_id=session_id)
    if payload.get("base_commit_sha") != str(current_base_sha).strip().lower():
        return _reject(REASON_STALE_HANDOFF, session_id=session_id)

    if not isinstance(patch_content, str):
        return _reject("PATCH_MUST_BE_STR", session_id=session_id)
    patch_sha = _sha256_text(patch_content)
    patch_ref = payload.get("candidate_patch_ref") or {}
    if patch_ref.get("sha256") != patch_sha:
        return _reject(REASON_PATCH_DRIFT, session_id=session_id)

    targets, err = _parse_patch_targets(patch_content, execution_worktree_path)
    if err:
        return _reject("PATCH_TARGETS_INVALID:" + str(err), session_id=session_id)
    approved = tuple(payload.get("target_scope") or ())
    target_tuple = tuple(sorted(targets or ()))
    if not set(target_tuple).issubset(set(approved)):
        return _reject(REASON_SCOPE_WIDENING, session_id=session_id)
    if target_tuple != tuple(sorted(approved)):
        return _reject(REASON_SCOPE_MISMATCH, session_id=session_id)

    lineage = _lineage_payload(handoff, proposal, manifest, validation)
    prepared = pc_v2_apply_patch_prepare(
        patch_content,
        execution_worktree_path=execution_worktree_path,
        main_worktree_path=main_worktree_path,
        branch_name=branch_name,
        base_sha=current_base_sha,
        stores_base_dir=stores_base_dir,
        session_id=session_id,
        descriptor_lineage=lineage,
    )
    out = dict(prepared)
    out["adapter_schema_version"] = ADAPTER_SCHEMA_VERSION
    out["handoff_to_governed_prepare"] = out.get("status") == PREPARED_AWAITING_HUMAN_APPROVAL
    out["existing_apply_patch_rail_reused"] = True
    out["builder_lineage"] = lineage
    out["proposal_id_bound"] = lineage["builder_proposal_id"]
    out["manifest_id_bound"] = lineage["builder_manifest_id"]
    out["validation_id_bound"] = lineage["builder_validation_id"]
    out["handoff_id_bound"] = lineage["builder_handoff_id"]
    out["approval_created"] = False
    out["binder_runtime_called"] = False
    out["kx108_called"] = False
    out["executor_invoked"] = False
    out["physical_mutation"] = False
    out["action_evidence_id_created"] = False
    out["action_evidence_id_canonical_stage"] = "CANONICAL_R8_EXECUTION_ENVELOPE"
    out["validation_equals_approval"] = False
    out["handoff_equals_authorization"] = False
    out["prepare_equals_authorization"] = False
    out["operation_type"] = out.get("operation_type", OP_APPLY_PATCH)
    return out
