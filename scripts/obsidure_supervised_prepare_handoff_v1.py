from __future__ import annotations

"""R12-F3-B governed prepare handoff.

This adapter binds one validated R12-F3-A PREPARE_ONLY step proposal to the
existing R11-B1 -> R9 governed prepare path. It returns independently checkable
prepare feedback and never promotes PREPARED to EXECUTED, VERIFIED, CLOSED, or
mission completion.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_self_build_r9_prepare_adapter_v1 import (  # noqa: E402
    STATUS_PREPARED as R11_PREPARED,
    adapt_self_build_candidate_to_r9_prepare,
)
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    REQUESTED_OPERATION,
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_PREPARE_HANDOFF_V1"
STATUS_PREPARED = "R12_F3_B_GOVERNED_PREPARE_HANDOFF_PREPARED"
STATUS_HELD = "R12_F3_B_GOVERNED_PREPARE_HANDOFF_HELD"
STATUS_REJECTED = "R12_F3_B_GOVERNED_PREPARE_HANDOFF_REJECTED"
EXPECTED_NEXT_STATE = "PREPARED_AWAITING_VALIDATED_FEEDBACK"

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
    "kx108_called": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "repair_loop_invoked": False,
    "physical_mutation": False,
    "filesystem_execution": False,
    "network_or_model_call": False,
    "memory_write": False,
    "native_memory_write": False,
    "ticket_completed": False,
    "mission_executed": False,
    "mission_verified": False,
    "mission_closed": False,
    "autonomous_retry": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
}


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "prepare_handoff": False,
        "prepared": False,
        "expected_next_state": None,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _candidate_targets(phase1_candidate: Mapping[str, Any]) -> tuple[str, ...]:
    plan = phase1_candidate.get("plan") if isinstance(phase1_candidate.get("plan"), Mapping) else {}
    values = phase1_candidate.get("candidate_files") or phase1_candidate.get("targets") or plan.get("candidate_patch_files") or ()
    return tuple(sorted(str(v).replace("\\", "/").lstrip("./") for v in values if str(v).strip()))


def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _proposal_from_step(supervisor_step: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if supervisor_step.get("status") == F3A_STATUS_PROPOSED and isinstance(supervisor_step.get("step_proposal"), Mapping):
        return supervisor_step["step_proposal"]
    if supervisor_step.get("requested_operation") == REQUESTED_OPERATION and supervisor_step.get("proposal_id"):
        return supervisor_step
    return None


def _expected_dependencies(state: Mapping[str, Any], ticket: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_id = {t.get("ticket_id"): t for t in state.get("tickets") or () if isinstance(t, Mapping)}
    refs: list[dict[str, Any]] = []
    for dep_id in _as_tuple(ticket.get("dependency_ids")):
        dep = by_id.get(dep_id)
        refs.append(
            {
                "dependency_id": dep_id,
                "status": dep.get("status") if isinstance(dep, Mapping) else "MISSING",
                "evidence_refs": list(_as_tuple(dep.get("evidence_refs"))) if isinstance(dep, Mapping) else [],
            }
        )
    return refs


def _validate_proposal_binding(
    *,
    proposal: Mapping[str, Any],
    recomputed_step: Mapping[str, Any],
    projection: Mapping[str, Any],
    phase1_candidate: Mapping[str, Any],
) -> tuple[bool, dict[str, Any]]:
    if recomputed_step.get("status") != F3A_STATUS_PROPOSED:
        return False, _fail(STATUS_HELD, str(recomputed_step.get("reason") or "SUPERVISOR_STEP_NOT_PROPOSED"), supervisor_step=recomputed_step)
    expected = recomputed_step["step_proposal"]
    fields = ("proposal_id", "mission_id", "selected_ticket_id", "mandate_reference", "requested_operation", "projection_hash")
    for field in fields:
        if proposal.get(field) != expected.get(field):
            return False, _fail(STATUS_REJECTED, "SUPERVISOR_PROPOSAL_BINDING_MISMATCH:" + field.upper())
    if proposal.get("requested_operation") != REQUESTED_OPERATION:
        return False, _fail(STATUS_REJECTED, "REQUESTED_OPERATION_NOT_PREPARE_ONLY")
    if proposal.get("proposal_does_not_complete_ticket") is not True or proposal.get("ticket_completed") is not False:
        return False, _fail(STATUS_REJECTED, "SUPERVISOR_PROPOSAL_COMPLETION_FORBIDDEN")

    project = proposal.get("project") if isinstance(proposal.get("project"), Mapping) else {}
    expected_project = expected.get("project") if isinstance(expected.get("project"), Mapping) else {}
    for field in ("repository_identity", "local_root", "worktree", "branch", "base_sha"):
        if project.get(field) != expected_project.get(field):
            return False, _fail(STATUS_REJECTED, "PROJECT_BINDING_MISMATCH:" + field.upper())

    state = projection.get("canonical_state") if isinstance(projection.get("canonical_state"), Mapping) else {}
    ticket = _ticket_by_id(state, str(proposal.get("selected_ticket_id") or ""))
    if not isinstance(ticket, Mapping):
        return False, _fail(STATUS_REJECTED, "SELECTED_TICKET_NOT_FOUND")
    if proposal.get("dependency_references") != _expected_dependencies(state, ticket):
        return False, _fail(STATUS_REJECTED, "DEPENDENCY_BINDING_MISMATCH")
    budget = proposal.get("budget_available") if isinstance(proposal.get("budget_available"), Mapping) else {}
    for field in ("remaining_actions", "remaining_attempts", "remaining_tickets"):
        value = budget.get(field)
        if isinstance(value, int) and value <= 0:
            return False, _fail(STATUS_HELD, "MISSION_BUDGET_EXHAUSTED")

    targets = _candidate_targets(phase1_candidate)
    allowed = set(_as_tuple(ticket.get("authorized_paths")))
    if not targets:
        return False, _fail(STATUS_HELD, "PHASE1_CANDIDATE_TARGETS_REQUIRED")
    if not set(targets).issubset(allowed):
        return False, _fail(STATUS_HELD, "TICKET_TARGET_SCOPE_EXCEEDED", candidate_targets=list(targets), allowed_target_paths=sorted(allowed))
    return True, {"ticket": ticket, "candidate_targets": targets}


def _mission_context_from_ticket(proposal: Mapping[str, Any], ticket: Mapping[str, Any], candidate_targets: tuple[str, ...]) -> dict[str, Any]:
    budget = proposal.get("budget_available") if isinstance(proposal.get("budget_available"), Mapping) else {}
    remaining_actions = budget.get("remaining_actions") if isinstance(budget.get("remaining_actions"), int) else 1
    remaining_attempts = budget.get("remaining_attempts") if isinstance(budget.get("remaining_attempts"), int) else 1
    return {
        "mission_id": proposal["mission_id"],
        "status": "ACTIVE",
        "allowed_target_paths": list(candidate_targets),
        "allowed_operation_shapes": list(_as_tuple(ticket.get("authorized_operations")) or ("UPDATE_TARGET_FROM_SOURCE",)),
        "allowed_tools": ["EDIT"],
        "max_actions": max(1, int(remaining_actions)),
        "executed_actions": 0,
        "max_iterations": max(1, int(remaining_attempts)),
        "used_iterations": 0,
    }


def _feedback_from_prepare(
    *,
    proposal: Mapping[str, Any],
    projection: Mapping[str, Any],
    prepared: Mapping[str, Any],
) -> dict[str, Any]:
    lineage = prepared.get("self_build_lineage") if isinstance(prepared.get("self_build_lineage"), Mapping) else {}
    prepared_action = prepared.get("prepared_action") if isinstance(prepared.get("prepared_action"), Mapping) else {}
    proposal_hash = _sha256(proposal)
    feedback = {
        "feedback_id": "fb-" + hashlib.sha256((proposal_hash + str(prepared.get("status"))).encode("utf-8")).hexdigest()[:24],
        "proposal_id": proposal.get("proposal_id"),
        "proposal_hash": proposal_hash,
        "mission_id": proposal.get("mission_id"),
        "selected_ticket_id": proposal.get("selected_ticket_id"),
        "mandate_reference": proposal.get("mandate_reference"),
        "project": dict(proposal.get("project") or {}),
        "preparation_outcome": prepared.get("status"),
        "r9_candidate_reference": {
            "r9_proposal_id": lineage.get("r9_proposal_id"),
            "r9_manifest_id": lineage.get("r9_manifest_id"),
            "r9_validation_id": lineage.get("r9_validation_id"),
            "r9_handoff_id": lineage.get("r9_handoff_id"),
            "candidate_patch_hash": prepared.get("candidate_patch_hash"),
        },
        "evidence_references": list(
            dict.fromkeys(
                _as_tuple(proposal.get("evidence_references"))
                + _as_tuple(lineage.get("inventory_snapshot_id"))
                + _as_tuple(lineage.get("deficiency_evidence_id"))
                + _as_tuple(lineage.get("validation_evidence_id"))
            )
        ),
        "prepared_action_reference": {
            "status": prepared_action.get("status"),
            "execution_authority_hash": prepared_action.get("execution_authority_hash"),
            "v2_exec_id": prepared_action.get("v2_exec_id"),
            "handoff_to_governed_prepare": prepared_action.get("handoff_to_governed_prepare"),
            "executor_invoked": prepared_action.get("executor_invoked"),
            "physical_mutation": prepared_action.get("physical_mutation"),
        },
        "expected_next_state": EXPECTED_NEXT_STATE,
        "canonical_state_json": projection.get("canonical_state_json"),
        "preparation_is_execution": False,
        "prepared_not_verified": True,
        "prepared_not_closed": True,
        **_NO_AUTHORITY_FIELDS,
    }
    return feedback


def prepare_supervised_mission_handoff(
    *,
    supervisor_step: Mapping[str, Any],
    mission_projection: Mapping[str, Any],
    phase1_candidate: Mapping[str, Any],
    inventory_snapshot: Mapping[str, Any] | None,
    deficiency_evidence: Mapping[str, Any] | None,
    validation_evidence: Mapping[str, Any] | None,
    stores_base_dir: str | Path,
    session_id: str,
    prior_feedback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(supervisor_step, Mapping):
        return _fail(STATUS_REJECTED, "SUPERVISOR_STEP_REQUIRED")
    if not isinstance(mission_projection, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PROJECTION_REQUIRED")
    if not isinstance(phase1_candidate, Mapping):
        return _fail(STATUS_HELD, "PHASE1_CANDIDATE_REQUIRED")
    proposal = _proposal_from_step(supervisor_step)
    if not isinstance(proposal, Mapping):
        reason = str(supervisor_step.get("reason") or "VALID_PREPARE_ONLY_PROPOSAL_REQUIRED")
        status = STATUS_HELD if supervisor_step.get("status") else STATUS_REJECTED
        return _fail(status, reason, supervisor_step=supervisor_step)
    if isinstance(prior_feedback, Mapping):
        proposal_hash = _sha256(proposal)
        if prior_feedback.get("proposal_hash") == proposal_hash and prior_feedback.get("proposal_id") == proposal.get("proposal_id"):
            return _fail(STATUS_HELD, "DUPLICATE_PREPARE_FEEDBACK", prior_feedback_id=prior_feedback.get("feedback_id"))
        if prior_feedback.get("proposal_id") == proposal.get("proposal_id") and prior_feedback.get("proposal_hash") != proposal_hash:
            return _fail(STATUS_REJECTED, "FORGED_PREPARE_FEEDBACK")

    recomputed_step = propose_supervised_mission_step(mission_projection)
    binding_ok, binding = _validate_proposal_binding(
        proposal=proposal,
        recomputed_step=recomputed_step,
        projection=mission_projection,
        phase1_candidate=phase1_candidate,
    )
    if not binding_ok:
        return binding

    project = proposal.get("project") if isinstance(proposal.get("project"), Mapping) else {}
    main_worktree = project.get("local_root")
    execution_worktree = project.get("worktree")
    base_sha = str(project.get("base_sha") or "").lower()
    branch = str(project.get("branch") or "")
    repo_identity = str(project.get("repository_identity") or "")

    prepared = adapt_self_build_candidate_to_r9_prepare(
        phase1_candidate=phase1_candidate,
        mission_context=_mission_context_from_ticket(proposal, binding["ticket"], binding["candidate_targets"]),
        inventory_snapshot=inventory_snapshot,
        deficiency_evidence=deficiency_evidence,
        validation_evidence=validation_evidence,
        base_commit_sha=base_sha,
        repo_identity_ref=repo_identity,
        execution_worktree_path=execution_worktree,
        main_worktree_path=main_worktree,
        branch_name=branch,
        stores_base_dir=stores_base_dir,
        session_id=session_id,
    )
    feedback = _feedback_from_prepare(proposal=proposal, projection=mission_projection, prepared=prepared)
    ok = prepared.get("status") == R11_PREPARED
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PREPARED if ok else STATUS_HELD,
        "reason": None if ok else prepared.get("reason") or "R9_PREPARE_HELD",
        "prepare_handoff": ok,
        "prepared": ok,
        "proposal_id": proposal.get("proposal_id"),
        "proposal_hash": feedback["proposal_hash"],
        "mission_id": proposal.get("mission_id"),
        "selected_ticket_id": proposal.get("selected_ticket_id"),
        "r9_prepare_result": prepared,
        "handoff_feedback": feedback,
        "expected_next_state": EXPECTED_NEXT_STATE if ok else None,
        "evidence_preserved": True,
        "semantic_unknowns": list(_as_tuple(proposal.get("semantic_unknowns"))),
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "EXPECTED_NEXT_STATE",
    "STATUS_HELD",
    "STATUS_PREPARED",
    "STATUS_REJECTED",
    "prepare_supervised_mission_handoff",
]
