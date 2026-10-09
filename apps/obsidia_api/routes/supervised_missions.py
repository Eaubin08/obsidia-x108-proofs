from __future__ import annotations

"""Read-only R12 supervised mission projection routes.

The API exposes a stable UI-facing projection of existing F5-A supervised
mission checkpoints. It does not create checkpoints, infer authority, replay
actions, approve execution, mutate memory, or read arbitrary files.
"""

import os
import re
import subprocess
import sys
import json
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_checkpoint_v1 import (  # noqa: E402
    CHECKPOINT_SCHEMA_VERSION,
    load_supervised_mission_checkpoint,
    save_supervised_mission_checkpoint,
)
from obsidure_mission_candidate_supervised_state_adapter_v1 import (  # noqa: E402
    STATUS_PROJECTED as F2_STATUS_PROJECTED,
    adapt_mission_candidate_to_supervised_state,
)
from obsidure_mission_semantic_bridge_v1 import build_real_brody_obsidure_mission_candidate  # noqa: E402
from obsidure_supervised_dependency_state_integration_v1 import (  # noqa: E402
    STATUS_UPDATED as F4B_STATUS_UPDATED,
    integrate_supervised_dependency_state,
)
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_supervised_prepare_handoff_v1 import (  # noqa: E402
    STATUS_PREPARED as F3B_STATUS_PREPARED,
    prepare_supervised_mission_handoff,
)

router = APIRouter(prefix="/api/supervised-missions", tags=["supervised-missions"])

PROJECTION_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_READONLY_API_V1"
PREPARE_INGRESS_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_PREPARE_INGRESS_API_V1"
PREPARE_STATUS_ACCEPTED = "R12_F6_C1_PREPARE_ONLY_ACCEPTED"
PREPARE_STATUS_HELD = "R12_F6_C1_PREPARE_ONLY_HELD"
PREPARE_STATUS_REJECTED = "R12_F6_C1_PREPARE_ONLY_REJECTED"
_DEFAULT_STORE = Path(os.getenv("OBSIDIA_SUPERVISED_MISSION_CHECKPOINT_DIR", "runtime_data/supervised_mission_checkpoints"))
_DEFAULT_PREPARE_STORE = Path(os.getenv("OBSIDIA_SUPERVISED_MISSION_PREPARE_STORE_DIR", "runtime_data/supervised_mission_prepare"))
_CHECKPOINT_ID = re.compile(r"^smc-[A-Za-z0-9_.:-]{1,80}$")
_MISSION_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")

_NO_AUTHORITY = {
    "readonly": True,
    "authority": "NONE",
    "decision_authority": DECISION_AUTHORITY,
    "supervisor_authority": "NONE",
    "emits_act": False,
    "approval_created": False,
    "automatic_approval": False,
    "kx108_called": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "repair_loop_invoked": False,
    "filesystem_execution": False,
    "network_or_model_call": False,
    "memory_write": False,
    "native_memory_write": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _json_default(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return dict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, type):
        return f"{value.__module__}.{value.__qualname__}"
    if isinstance(value, (set, tuple)):
        return list(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _json_response(value: Mapping[str, Any]) -> JSONResponse:
    body = json.loads(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            default=_json_default,
        )
    )
    return JSONResponse(content=body)


def _norm_rel(value: Any) -> str:
    return str(value or "").strip().replace("\\", "/").lstrip("./")


def _safe_rel(value: Any) -> bool:
    rel = _norm_rel(value)
    if not rel or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        return False
    return all(part not in {"", ".", ".."} and not part.startswith(".git") for part in rel.split("/"))


def _api_fail(status: str, reason: str, *, http_status: int = 200, **extra: Any) -> dict[str, Any]:
    body = {
        "schema_version": PREPARE_INGRESS_SCHEMA_VERSION,
        "status": status,
        "state": "HOLD" if status == PREPARE_STATUS_HELD else "REJECTED",
        "reason": reason,
        "mission_id": extra.pop("mission_id", None),
        "checkpoint_id": None,
        "checkpoint_projection_available": False,
        "hold_reasons": [reason],
        "evidence_references": [],
        "provider_provenance": {},
        **_NO_AUTHORITY,
        "readonly": False,
        "network_or_model_call": bool(extra.pop("network_or_model_call", False)),
        **extra,
    }
    if http_status >= 400:
        raise HTTPException(status_code=http_status, detail=body)
    return body


def _git(root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        capture_output=True,
        text=True,
        timeout=20,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _observed_worktree_identity(repository_context: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    worktree_raw = repository_context.get("worktree") or repository_context.get("local_root")
    branch = str(repository_context.get("branch") or "").strip()
    base_sha = str(repository_context.get("base_sha") or "").lower().strip()
    if not worktree_raw or not branch or not _HEX40.fullmatch(base_sha):
        return None, "PROJECT_IDENTITY_INCOMPLETE"
    worktree = Path(str(worktree_raw)).resolve()
    if not worktree.is_dir():
        return None, "WORKTREE_NOT_FOUND"
    head_code, head, _ = _git(worktree, "rev-parse", "HEAD")
    if head_code != 0 or not _HEX40.fullmatch(head.lower()):
        return None, "WORKTREE_HEAD_UNAVAILABLE"
    if head.lower() != base_sha:
        return None, "STALE_BASE_SHA"
    branch_code, observed_branch, _ = _git(worktree, "branch", "--show-current")
    if branch_code != 0 or observed_branch != branch:
        return None, "WORKTREE_BRANCH_MISMATCH"
    status_code, status, _ = _git(worktree, "status", "--short")
    if status_code != 0:
        return None, "WORKTREE_STATUS_UNAVAILABLE"
    if status.strip():
        return None, "WORKTREE_DIRTY"
    return {"worktree": str(worktree), "branch": branch, "base_sha": base_sha, "head": head.lower()}, None


def _validate_scope(proposed_scope: Mapping[str, Any], human_mandate: Mapping[str, Any]) -> str | None:
    proposed_targets = [_norm_rel(item) for item in _as_list(proposed_scope.get("target_paths"))]
    proposed_ops = [str(item).upper() for item in _as_list(proposed_scope.get("operations"))]
    authorized_targets = {_norm_rel(item) for item in _as_list(human_mandate.get("authorized_target_paths"))}
    authorized_ops = {str(item).upper() for item in _as_list(human_mandate.get("authorized_operations"))}
    if not proposed_targets or not proposed_ops or not authorized_targets or not authorized_ops:
        return "BOUNDED_SCOPE_REQUIRED"
    if any(not _safe_rel(target) for target in list(proposed_targets) + list(authorized_targets)):
        return "BOUNDED_SCOPE_PATH_INVALID"
    if not set(proposed_targets).issubset(authorized_targets):
        return "SCOPE_VIOLATION"
    if not set(proposed_ops).issubset(authorized_ops):
        return "OPERATION_SCOPE_VIOLATION"
    return None


def _validate_prepare_payload(payload: Mapping[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(payload, Mapping):
        return None, _api_fail(PREPARE_STATUS_REJECTED, "REQUEST_BODY_REQUIRED", http_status=422)
    human_request = str(payload.get("human_request") or payload.get("mission_goal") or "").strip()
    if not human_request:
        return None, _api_fail(PREPARE_STATUS_REJECTED, "MISSION_GOAL_REQUIRED", http_status=422)
    repository_context = payload.get("repository_context")
    proposed_scope = payload.get("proposed_scope")
    human_mandate = payload.get("human_mandate")
    provider_config = payload.get("provider_config")
    for name, value in (
        ("REPOSITORY_CONTEXT_REQUIRED", repository_context),
        ("PROPOSED_SCOPE_REQUIRED", proposed_scope),
        ("HUMAN_MANDATE_REQUIRED", human_mandate),
        ("PROVIDER_CONFIG_REQUIRED", provider_config),
    ):
        if not isinstance(value, Mapping):
            return None, _api_fail(PREPARE_STATUS_REJECTED, name, http_status=422)
    if human_mandate.get("revoked") is True or str(human_mandate.get("status") or "").upper() == "REVOKED":
        return None, _api_fail(PREPARE_STATUS_HELD, "HUMAN_MANDATE_REVOKED")
    if str(human_mandate.get("mission_authority") or "").upper() != DECISION_AUTHORITY:
        return None, _api_fail(PREPARE_STATUS_HELD, "MISSION_AUTHORITY_NOT_KX108_ONLY")
    scope_reason = _validate_scope(proposed_scope, human_mandate)
    if scope_reason:
        return None, _api_fail(PREPARE_STATUS_HELD, scope_reason)
    project, project_reason = _observed_worktree_identity(repository_context)
    if project_reason:
        return None, _api_fail(PREPARE_STATUS_HELD, project_reason)
    provider_status = str(provider_config.get("status") or provider_config.get("availability") or "").upper()
    if provider_status not in {"VERIFIED", "AVAILABLE", "READY"}:
        return None, _api_fail(PREPARE_STATUS_HELD, "PROVIDER_UNAVAILABLE")
    return {
        "human_request": human_request,
        "repository_context": dict(repository_context),
        "proposed_scope": dict(proposed_scope),
        "human_mandate": dict(human_mandate),
        "provider_config": dict(provider_config),
        "project": project,
        "explicit_references": payload.get("explicit_references") if isinstance(payload.get("explicit_references"), Mapping) else None,
        "phase1_candidate": payload.get("phase1_candidate"),
        "inventory_snapshot": payload.get("inventory_snapshot"),
        "deficiency_evidence": payload.get("deficiency_evidence"),
        "validation_evidence": payload.get("validation_evidence"),
        "session_id": str(payload.get("session_id") or human_mandate.get("mission_id") or "r12-f6-c1"),
        "language": str(payload.get("language") or "fr"),
        "require_local_model_evidence": bool(payload.get("require_local_model_evidence", False)),
    }, None


def _build_mission_candidate(validated: Mapping[str, Any]) -> dict[str, Any]:
    return build_real_brody_obsidure_mission_candidate(
        human_request=validated["human_request"],
        repository_context=validated["repository_context"],
        proposed_scope=validated["proposed_scope"],
        human_mandate=validated["human_mandate"],
        explicit_references=validated.get("explicit_references"),
        provider_config=validated["provider_config"],
        session_id=str(validated["session_id"]),
        language=str(validated["language"]),
        require_local_model_evidence=bool(validated.get("require_local_model_evidence")),
    )


def _provider_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    evidence = candidate.get("local_model_evidence") if isinstance(candidate.get("local_model_evidence"), Mapping) else {}
    return {
        "real_brody_runtime_verified": bool(candidate.get("real_brody_runtime_verified")),
        "real_local_model_verified": bool(candidate.get("real_local_model_verified")),
        "model_call_used": bool(candidate.get("model_call_used")),
        "source_ref": candidate.get("local_model_evidence_source_ref") or evidence.get("source_ref"),
        "provider": evidence.get("provider"),
        "model": evidence.get("model"),
    }


def _as_f1_projection(supervised_projection: Mapping[str, Any]) -> dict[str, Any]:
    projection = dict(supervised_projection)
    projection["status"] = str(projection.get("f1_projection_status") or projection.get("canonical_mission_status") or projection.get("status"))
    return projection


def _prepare_ingress_response(*, checkpoint: Mapping[str, Any], projection: Mapping[str, Any], candidate: Mapping[str, Any], handoff: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PREPARE_INGRESS_SCHEMA_VERSION,
        "status": PREPARE_STATUS_ACCEPTED,
        "state": "PREPARED_AWAITING_APPROVAL",
        "reason": None,
        "mission_id": checkpoint.get("mission_id"),
        "checkpoint_id": checkpoint.get("checkpoint_id"),
        "checkpoint_projection_available": True,
        "hold_reasons": [],
        "evidence_references": _as_list(checkpoint.get("evidence_references")),
        "provider_provenance": _provider_summary(candidate),
        "r9_candidate_reference": (
            handoff.get("handoff_feedback", {}).get("r9_candidate_reference")
            if isinstance(handoff.get("handoff_feedback"), Mapping)
            else {}
        ),
        "projection": {
            "status": projection.get("status"),
            "unique_next_ticket_id": projection.get("unique_next_ticket_id"),
            "pending_approvals": projection.get("pending_approvals", []),
            "binder_replay": projection.get("binder_replay", {}),
        },
        **_NO_AUTHORITY,
        "readonly": False,
        "network_or_model_call": bool(candidate.get("model_call_used")),
    }


def _public_project(project: Mapping[str, Any] | None) -> dict[str, Any]:
    project = project or {}
    return {
        "repository_identity": project.get("repository_identity"),
        "worktree": project.get("worktree"),
        "branch": project.get("branch"),
        "base_sha": project.get("base_sha"),
        "local_root_visible": bool(project.get("local_root")),
    }


def _ticket_phase(ticket: Mapping[str, Any]) -> str:
    if ticket.get("closed") is True:
        return "CLOSED"
    if ticket.get("verified") is True or ticket.get("independent_verification_status") == "PASS":
        return "VERIFIED"
    execution_phase = str(ticket.get("execution_phase") or "")
    if execution_phase:
        return execution_phase
    if ticket.get("action_evidence_id"):
        return "EXECUTED_OBSERVED"
    if ticket.get("status") == "HELD" and ticket.get("hold_reason") == "PREPARED_AWAITING_APPROVAL":
        return "PREPARED"
    return str(ticket.get("status") or "UNKNOWN")


def _verification_level(ticket: Mapping[str, Any]) -> str:
    return str(ticket.get("verification_level") or ticket.get("independent_verification_level") or "UNKNOWN")


def _safe_ticket(ticket: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": ticket.get("ticket_id"),
        "objective": ticket.get("objective"),
        "dependency_ids": _as_list(ticket.get("dependency_ids")),
        "status": ticket.get("status"),
        "phase": _ticket_phase(ticket),
        "hold_reason": ticket.get("hold_reason") or "",
        "blocked_reason": ticket.get("blocked_reason") or "",
        "verification_level": _verification_level(ticket),
        "pending_approval": ticket.get("status") == "HELD" and ticket.get("hold_reason") == "PREPARED_AWAITING_APPROVAL",
        "evidence_refs": _as_list(ticket.get("evidence_refs")),
        "action_evidence_id": ticket.get("action_evidence_id"),
        "receipt_refs": _as_list(ticket.get("receipt_refs") or ticket.get("r8_receipt_refs")),
        "closed": bool(ticket.get("closed")),
        "verified": bool(ticket.get("verified")),
    }


def _completion_reference(record: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any] | None:
    proof = state.get("mission_completion_proof")
    if isinstance(proof, Mapping):
        return {
            "schema_version": proof.get("schema_version"),
            "mission_id": proof.get("mission_id"),
            "completion_proof_digest": proof.get("completion_proof_digest"),
            "evidence_refs": _as_list(proof.get("evidence_refs")),
        }
    if record.get("checkpoint_marks_verified_or_closed") is True:
        return {"status": "UNKNOWN", "reason": "CHECKPOINT_CARRIES_UNSUPPORTED_CLOSURE_FLAG"}
    return None


def _binder_limitation(record: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any]:
    limitations = []
    for source in (record, state):
        for item in _as_list(source.get("binder_replay_limitations") or source.get("binder_limitations")):
            if item not in limitations:
                limitations.append(item)
    if not limitations:
        limitations.append("BINDER_INDEPENDENT_REPLAY_NOT_PROVEN")
    return {
        "independent_replay_available": False,
        "limitations": limitations,
    }


def _projection(record: Mapping[str, Any]) -> dict[str, Any]:
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    dep = record.get("dependency_projection") if isinstance(record.get("dependency_projection"), Mapping) else {}
    next_step = record.get("next_step") if isinstance(record.get("next_step"), Mapping) else {}
    tickets = [_safe_ticket(ticket) for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)]
    completion_ref = _completion_reference(record, state)
    mission_done = bool(completion_ref and state.get("mission_done_verified") is True)
    status = "MISSION_DONE_VERIFIED" if mission_done else str(dep.get("status") or record.get("status") or "UNKNOWN")
    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "checkpoint_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "status": status,
        "mission_id": record.get("mission_id") or state.get("mission_id"),
        "original_goal": record.get("original_goal") or state.get("original_goal"),
        "mandate": {
            "human_mandate_reference": record.get("human_mandate_reference") or state.get("human_mandate_reference"),
            "status": state.get("mandate_status", "UNKNOWN"),
            "revoked": bool(state.get("mandate_revoked")),
        },
        "project": _public_project(record.get("project") if isinstance(record.get("project"), Mapping) else None),
        "ticket_dag": [
            {"ticket_id": ticket["ticket_id"], "dependency_ids": ticket["dependency_ids"]}
            for ticket in tickets
        ],
        "tickets": tickets,
        "unique_next_ticket_id": dep.get("unique_next_ticket_id") or record.get("unique_next_ticket_id"),
        "eligible_ticket_ids": _as_list(dep.get("eligible_ticket_ids")),
        "hold": {
            "reason": dep.get("reason") or record.get("hold_reason"),
            "root_causes": list(record.get("blocker_root_causes") or dep.get("root_dependency_blocks") or []),
            "transitive_blocks": list(dep.get("transitive_dependency_blocks") or []),
        },
        "budget": deepcopy(dict(record.get("budget") or state.get("global_budget") or {})),
        "timebox": deepcopy(dict(record.get("timebox") or state.get("timebox") or {})),
        "pending_approvals": deepcopy(list(record.get("pending_approvals") or [])),
        "evidence": {
            "evidence_refs": _as_list(record.get("evidence_references") or state.get("evidence_refs")),
            "action_evidence_refs": [
                ticket["action_evidence_id"] for ticket in tickets if ticket.get("action_evidence_id")
            ],
            "receipt_refs": sorted({ref for ticket in tickets for ref in ticket["receipt_refs"]}),
        },
        "verification": {
            "ticket_levels": {ticket["ticket_id"]: ticket["verification_level"] for ticket in tickets},
            "mission_completion_proof_ref": completion_ref,
        },
        "binder_replay": _binder_limitation(record, state),
        "checkpoint": {
            "checkpoint_id": record.get("checkpoint_id"),
            "integrity_digest": record.get("integrity_digest"),
            "accepted_state_hash": record.get("accepted_state_hash"),
            "dependency_projection_hash": record.get("dependency_projection_hash"),
            "next_step_hash": record.get("next_step_hash"),
            "resume_status": "CHECKPOINT_VERIFIED_READONLY",
        },
        "next_step": {
            "status": next_step.get("status"),
            "selected_ticket_id": next_step.get("selected_ticket_id"),
            "requested_operation": next_step.get("requested_operation"),
            "hold_reason": next_step.get("reason"),
        },
        "status_distinctions": {
            "prepared_is_authorized": False,
            "executed_observed_is_verified": False,
            "verified_is_closed": False,
            "closed_is_mission_done_verified": False,
        },
        "serialization": {
            "canonical_json": canonical_json(
                {
                    "checkpoint_id": record.get("checkpoint_id"),
                    "integrity_digest": record.get("integrity_digest"),
                    "projection_schema_version": PROJECTION_SCHEMA_VERSION,
                }
            )
        },
        **_NO_AUTHORITY,
    }


def _load_projection(checkpoint_id: str) -> dict[str, Any]:
    if not _CHECKPOINT_ID.fullmatch(checkpoint_id):
        raise HTTPException(status_code=422, detail={"reason": "INVALID_CHECKPOINT_ID", **_NO_AUTHORITY})
    record, reason = load_supervised_mission_checkpoint(checkpoint_id, checkpoint_store_dir=_DEFAULT_STORE)
    if record is None:
        status = 404 if reason == "CHECKPOINT_NOT_FOUND" else 409
        raise HTTPException(status_code=status, detail={"reason": reason or "CHECKPOINT_LOAD_FAILED", **_NO_AUTHORITY})
    return _projection(record)


@router.post("/prepare-only", response_model=None)
async def prepare_supervised_mission_ingress(payload: Mapping[str, Any] = Body(...)) -> Any:
    """Create a governed PREPARE_ONLY supervised mission checkpoint.

    This route is an ingress adapter only. It validates an explicit human
    mandate and project identity, delegates semantic interpretation to the
    existing Brody/SENS bridge, delegates state projection to F2/F1, delegates
    governed preparation to F3-B/R11/R9, integrates the resulting F4-B state,
    and persists only the accepted prepare-only checkpoint through F5-A.
    """

    validated, failure = _validate_prepare_payload(payload)
    if failure is not None:
        return failure
    assert validated is not None

    try:
        mission_candidate = _build_mission_candidate(validated)
    except Exception as exc:
        return _api_fail(
            PREPARE_STATUS_HELD,
            "MISSION_CANDIDATE_BUILD_FAILED",
            error_type=type(exc).__name__,
            error=str(exc)[:240],
        )
    if mission_candidate.get("status") != "R12_MISSION_CANDIDATE_READY_FOR_R11_B2":
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(mission_candidate.get("reason") or "MISSION_CANDIDATE_NOT_READY"),
            mission_id=(mission_candidate.get("mission_contract") or {}).get("mission_id") if isinstance(mission_candidate.get("mission_contract"), Mapping) else None,
            provider_provenance=_provider_summary(mission_candidate),
            network_or_model_call=bool(mission_candidate.get("model_call_used")),
            mission_candidate_status=mission_candidate.get("status"),
        )

    observed_head = validated["project"]["head"]
    supervised_projection = adapt_mission_candidate_to_supervised_state(
        mission_candidate,
        observed_project_head=observed_head,
    )
    if supervised_projection.get("status") != F2_STATUS_PROJECTED:
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(supervised_projection.get("reason") or "SUPERVISED_STATE_NOT_PROJECTED"),
            mission_id=supervised_projection.get("mission_id"),
            provider_provenance=_provider_summary(mission_candidate),
            f2_status=supervised_projection.get("status"),
        )
    f1_projection = _as_f1_projection(supervised_projection)

    supervisor_step = propose_supervised_mission_step(f1_projection, observed_project_head=observed_head)
    if supervisor_step.get("status") != F3A_STATUS_PROPOSED:
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(supervisor_step.get("reason") or "SUPERVISOR_STEP_NOT_PROPOSED"),
            mission_id=supervisor_step.get("mission_id"),
            provider_provenance=_provider_summary(mission_candidate),
            f3a_status=supervisor_step.get("status"),
        )

    handoff = prepare_supervised_mission_handoff(
        supervisor_step=supervisor_step,
        mission_projection=f1_projection,
        phase1_candidate=validated.get("phase1_candidate"),
        inventory_snapshot=validated.get("inventory_snapshot"),
        deficiency_evidence=validated.get("deficiency_evidence"),
        validation_evidence=validated.get("validation_evidence"),
        stores_base_dir=_DEFAULT_PREPARE_STORE,
        session_id=str(validated["session_id"]),
    )
    if handoff.get("status") != F3B_STATUS_PREPARED:
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(handoff.get("reason") or "GOVERNED_PREPARE_HELD"),
            mission_id=handoff.get("mission_id") or supervised_projection.get("mission_id"),
            provider_provenance=_provider_summary(mission_candidate),
            f3b_status=handoff.get("status"),
            r9_prepare_result=handoff.get("r9_prepare_result"),
        )

    update = integrate_supervised_dependency_state(
        mission_projection=f1_projection,
        supervisor_step=supervisor_step,
        prepare_feedback=handoff.get("handoff_feedback"),
        observed_project_head=observed_head,
    )
    if update.get("status") != F4B_STATUS_UPDATED:
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(update.get("reason") or "F4B_DEPENDENCY_ADMISSION_HELD"),
            mission_id=update.get("mission_id") or supervised_projection.get("mission_id"),
            provider_provenance=_provider_summary(mission_candidate),
            f4b_status=update.get("status"),
        )

    saved = save_supervised_mission_checkpoint(update, checkpoint_store_dir=_DEFAULT_STORE)
    if saved.get("status") != "R12_F5_A_CHECKPOINT_SAVED":
        return _api_fail(
            PREPARE_STATUS_HELD,
            str(saved.get("reason") or "CHECKPOINT_SAVE_HELD"),
            mission_id=update.get("mission_id") or supervised_projection.get("mission_id"),
            provider_provenance=_provider_summary(mission_candidate),
            checkpoint_status=saved.get("status"),
        )

    projection = _projection(saved["checkpoint"])
    return _json_response(
        _prepare_ingress_response(
            checkpoint=saved["checkpoint"],
            projection=projection,
            candidate=mission_candidate,
            handoff=handoff,
        )
    )


@router.get("/{mission_id}/projection")
async def supervised_mission_projection(
    mission_id: str,
    checkpoint_id: str = Query(..., description="Canonical F5-A checkpoint id to project."),
) -> dict[str, Any]:
    if not _MISSION_ID.fullmatch(mission_id):
        raise HTTPException(status_code=422, detail={"reason": "INVALID_MISSION_ID", **_NO_AUTHORITY})
    projection = _load_projection(checkpoint_id)
    if projection.get("mission_id") != mission_id:
        raise HTTPException(status_code=404, detail={"reason": "MISSION_CHECKPOINT_MISMATCH", **_NO_AUTHORITY})
    return projection


@router.get("/checkpoints/{checkpoint_id}/projection")
async def supervised_checkpoint_projection(checkpoint_id: str) -> dict[str, Any]:
    return _load_projection(checkpoint_id)
