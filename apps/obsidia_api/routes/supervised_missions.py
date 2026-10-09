from __future__ import annotations

"""Read-only R12 supervised mission projection routes.

The API exposes a stable UI-facing projection of existing F5-A supervised
mission checkpoints. It does not create checkpoints, infer authority, replay
actions, approve execution, mutate memory, or read arbitrary files.
"""

import os
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from fastapi import APIRouter, HTTPException, Query

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_checkpoint_v1 import (  # noqa: E402
    CHECKPOINT_SCHEMA_VERSION,
    load_supervised_mission_checkpoint,
)
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402

router = APIRouter(prefix="/api/supervised-missions", tags=["supervised-missions"])

PROJECTION_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_READONLY_API_V1"
_DEFAULT_STORE = Path(os.getenv("OBSIDIA_SUPERVISED_MISSION_CHECKPOINT_DIR", "runtime_data/supervised_mission_checkpoints"))
_CHECKPOINT_ID = re.compile(r"^smc-[A-Za-z0-9_.:-]{1,80}$")
_MISSION_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")

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

