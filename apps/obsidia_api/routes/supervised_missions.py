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
import hashlib
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
from obsidure_supervised_execution_outcome_bridge_v1 import (  # noqa: E402
    HOLD_AWAITING_VALID_AUTHORIZATION,
    STATUS_EXECUTION_OUTCOME as F5B_STATUS_EXECUTION_OUTCOME,
    STATUS_HELD as F5B_STATUS_HELD,
    execute_supervised_governed_ticket,
)
from obsidure_supervised_execution_feedback_projection_v1 import (  # noqa: E402
    STATUS_PROJECTED as F5C1_STATUS_PROJECTED,
    project_supervised_execution_feedback,
)
from obsidure_supervised_independent_verification_v1 import (  # noqa: E402
    STATUS_HELD as F5C2_STATUS_HELD,
    STATUS_REJECTED as F5C2_STATUS_REJECTED,
    STATUS_VERIFIED as F5C2_STATUS_VERIFIED,
    verify_supervised_ticket_and_mission_closure,
)
from obsidia_pc_capabilities_v2 import (  # noqa: E402
    OP_APPLY_PATCH,
    PREPARED_AWAITING_HUMAN_APPROVAL,
    _descriptor_record_hash,
    _sha16,
    _v2id,
)

router = APIRouter(prefix="/api/supervised-missions", tags=["supervised-missions"])

PROJECTION_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_READONLY_API_V1"
PREPARE_INGRESS_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_PREPARE_INGRESS_API_V1"
PREPARE_STATUS_ACCEPTED = "R12_F6_C1_PREPARE_ONLY_ACCEPTED"
PREPARE_STATUS_HELD = "R12_F6_C1_PREPARE_ONLY_HELD"
PREPARE_STATUS_REJECTED = "R12_F6_C1_PREPARE_ONLY_REJECTED"
AUTH_HANDOFF_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_AUTHORIZATION_HANDOFF_API_V1"
AUTH_STATUS_ACCEPTED = "R12_F6_D1_EXECUTION_OUTCOME_ACCEPTED"
AUTH_STATUS_HELD = "R12_F6_D1_EXECUTION_HELD"
AUTH_STATUS_REJECTED = "R12_F6_D1_EXECUTION_REJECTED"
VERIFICATION_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_VERIFICATION_OPERATOR_API_V1"
VERIFICATION_STATUS_PROJECTED = "R12_F6_D2_VERIFICATION_PROJECTED"
VERIFICATION_STATUS_ASSESSED = "R12_F6_D2_VERIFICATION_ASSESSED"
VERIFICATION_STATUS_HELD = "R12_F6_D2_VERIFICATION_HELD"
VERIFICATION_STATUS_REJECTED = "R12_F6_D2_VERIFICATION_REJECTED"
_DEFAULT_STORE = Path(os.getenv("OBSIDIA_SUPERVISED_MISSION_CHECKPOINT_DIR", "runtime_data/supervised_mission_checkpoints"))
_DEFAULT_PREPARE_STORE = Path(os.getenv("OBSIDIA_SUPERVISED_MISSION_PREPARE_STORE_DIR", "runtime_data/supervised_mission_prepare"))
_CHECKPOINT_ID = re.compile(r"^smc-[A-Za-z0-9_.:-]{1,80}$")
_MISSION_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

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



import math
import dataclasses
from enum import Enum
from types import MappingProxyType

def api_projection(value: Any, active: set[int] = None) -> Any:
    if active is None:
        active = set()
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite float")
        return value

    vid = id(value)
    if vid in active:
        raise ValueError(f"recursive container")

    active.add(vid)
    try:
        if isinstance(value, dict):
            return {k: api_projection(v, active) for k, v in value.items()}
        elif isinstance(value, MappingProxyType):
            return {k: api_projection(v, active) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [api_projection(v, active) for v in value]
        elif isinstance(value, (set, frozenset)):
            return sorted([api_projection(v, active) for v in value], key=lambda x: str(x))
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, Path):
            return str(value)
        elif dataclasses.is_dataclass(value) and not isinstance(value, type):
            return {k: api_projection(v, active) for k, v in ((f.name, getattr(value, f.name)) for f in dataclasses.fields(value))}
        elif hasattr(value, "dict") and callable(getattr(value, "dict")):
            return {k: api_projection(v, active) for k, v in value.dict().items()}
        elif hasattr(value, "model_dump") and callable(getattr(value, "model_dump")):
            return {k: api_projection(v, active) for k, v in value.model_dump().items()}
        elif hasattr(value, "to_dict"):
            return {k: api_projection(v, active) for k, v in value.to_dict().items()}

        return str(value)
    finally:
        active.discard(vid)


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
        raise HTTPException(status_code=http_status, detail=api_projection(body))
    return api_projection(body)


def _auth_fail(reason: str, *, status: str = AUTH_STATUS_HELD, http_status: int = 200, **extra: Any) -> dict[str, Any]:
    body = {
        "schema_version": AUTH_HANDOFF_SCHEMA_VERSION,
        "status": status,
        "state": "HOLD" if status == AUTH_STATUS_HELD else "REJECTED",
        "reason": reason,
        "mission_id": extra.pop("mission_id", None),
        "checkpoint_id": extra.pop("checkpoint_id", None),
        "ticket_id": extra.pop("ticket_id", None),
        "checkpoint_projection_available": False,
        "hold_reasons": [reason],
        "execution_phase": "HOLD",
        "execution_outcome": None,
        "execution_authority_hash": extra.pop("execution_authority_hash", None),
        "human_authorization_reference_hash": extra.pop("human_authorization_reference_hash", None),
        "supervisor_approval_created": False,
        "no_false_verification": True,
        "no_automatic_retry": True,
        **_NO_AUTHORITY,
        "readonly": False,
        **extra,
    }
    if http_status >= 400:
        raise HTTPException(status_code=http_status, detail=api_projection(body))
    return api_projection(body)


def _verification_fail(reason: str, *, status: str = VERIFICATION_STATUS_HELD, http_status: int = 200, **extra: Any) -> dict[str, Any]:
    body = {
        "schema_version": VERIFICATION_SCHEMA_VERSION,
        "status": status,
        "state": "HOLD" if status == VERIFICATION_STATUS_HELD else "REJECTED",
        "reason": reason,
        "mission_id": extra.pop("mission_id", None),
        "checkpoint_id": extra.pop("checkpoint_id", None),
        "ticket_id": extra.pop("ticket_id", None),
        "closure_eligibility": "CLOSURE_BLOCKED",
        "hold_reasons": [reason],
        "verification_projection": None,
        "verification_assessment": None,
        "no_false_closure": True,
        **_NO_AUTHORITY,
        "readonly": True,
        **extra,
    }
    if http_status >= 400:
        raise HTTPException(status_code=http_status, detail=api_projection(body))
    return api_projection(body)


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


def _auth_ref_hash(reference: str | None) -> str | None:
    if not reference:
        return None
    return hashlib.sha256(reference.encode("utf-8")).hexdigest()


def _find_ticket(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _mission_update_from_checkpoint(record: Mapping[str, Any]) -> dict[str, Any]:
    dep = record.get("dependency_projection") if isinstance(record.get("dependency_projection"), Mapping) else {}
    return {
        "status": F4B_STATUS_UPDATED,
        "mission_update_accepted": True,
        "mission_id": record.get("mission_id"),
        "accepted_state": deepcopy(dict(record.get("accepted_state") or {})),
        "dependency_projection": deepcopy(dict(dep)),
        "next_step": deepcopy(dict(record.get("next_step") or {})),
        "transitive_dependency_blocks": deepcopy(list(dep.get("transitive_dependency_blocks") or [])),
        "root_dependency_blocks": deepcopy(list(dep.get("root_dependency_blocks") or [])),
        "evidence_refs": _as_list(record.get("evidence_references")),
    }


def _load_descriptor_by_eah(execution_authority_hash: str) -> tuple[dict[str, Any] | None, str | None]:
    v2exec = _DEFAULT_PREPARE_STORE / "v2exec"
    if not v2exec.is_dir():
        return None, "PREPARE_DESCRIPTOR_STORE_NOT_FOUND"
    for path in sorted(v2exec.glob("v2x-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(record, Mapping) and record.get("eah") == execution_authority_hash:
            result = dict(record)
            result["_descriptor_path"] = str(path)
            return result, None
    return None, "PREPARED_DESCRIPTOR_NOT_FOUND"


def _project_from_state(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "repository_identity": state.get("repository_identity"),
        "local_root": state.get("local_root"),
        "worktree": state.get("worktree"),
        "branch": state.get("branch"),
        "base_sha": state.get("base_sha"),
    }


def _validate_descriptor_binding(
    *,
    descriptor_record: Mapping[str, Any],
    state: Mapping[str, Any],
    ticket: Mapping[str, Any],
) -> str | None:
    descriptor = descriptor_record.get("descriptor")
    if not isinstance(descriptor, Mapping):
        return "PREPARE_DESCRIPTOR_PAYLOAD_REQUIRED"
    if descriptor_record.get("operation_type") != OP_APPLY_PATCH:
        return "PREPARE_DESCRIPTOR_OPERATION_UNSUPPORTED"
    expected_project = _project_from_state(state)
    for descriptor_key, expected in (
        ("execution_worktree", expected_project.get("worktree")),
        ("main_worktree", expected_project.get("local_root")),
        ("branch_name", expected_project.get("branch")),
        ("base_sha", expected_project.get("base_sha")),
    ):
        if str(descriptor.get(descriptor_key) or "") != str(expected or ""):
            return "PREPARE_DESCRIPTOR_PROJECT_MISMATCH:" + descriptor_key.upper()
    targets = {_norm_rel(item) for item in _as_list(descriptor.get("target_paths"))}
    allowed_targets = {_norm_rel(item) for item in _as_list(ticket.get("authorized_paths") or ticket.get("target_paths"))}
    if not targets:
        return "PREPARED_DESCRIPTOR_TARGETS_REQUIRED"
    if not allowed_targets or not targets.issubset(allowed_targets):
        return "TICKET_TARGET_SCOPE_EXCEEDED"
    operations = {str(item).upper() for item in _as_list(ticket.get("authorized_operations") or ticket.get("operations"))}
    if operations and OP_APPLY_PATCH.upper() not in operations and "UPDATE_TARGET_FROM_SOURCE" not in operations:
        return "TICKET_OPERATION_SCOPE_EXCEEDED"
    v2id = str(descriptor_record.get("v2_exec_id") or "")
    patch_path = _DEFAULT_PREPARE_STORE / "v2exec" / f"{v2id}.patch"
    if not patch_path.is_file():
        return "PREPARED_PATCH_ARTIFACT_MISSING"
    patch_hash = hashlib.sha256(patch_path.read_bytes()).hexdigest()
    if patch_hash != str(descriptor.get("patch_sha256") or ""):
        return "PREPARED_PATCH_ARTIFACT_HASH_MISMATCH"
    evidence_refs = set(_as_list(ticket.get("evidence_refs")) + _as_list(state.get("evidence_refs")))
    patch_sha = str(descriptor.get("patch_sha256") or "")
    if patch_sha and patch_sha not in evidence_refs:
        return "PREPARED_PATCH_HASH_NOT_IN_TICKET_EVIDENCE"
    return None


def _handoff_from_checkpoint(
    *,
    record: Mapping[str, Any],
    ticket_id: str,
    execution_authority_hash: str,
) -> tuple[dict[str, Any] | None, str | None]:
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    ticket = _find_ticket(state, ticket_id)
    if ticket is None:
        return None, "PREPARED_TICKET_NOT_FOUND"
    descriptor_record, reason = _load_descriptor_by_eah(execution_authority_hash)
    if descriptor_record is None:
        return None, reason
    bind_reason = _validate_descriptor_binding(descriptor_record=descriptor_record, state=state, ticket=ticket)
    if bind_reason:
        return None, bind_reason
    descriptor = descriptor_record["descriptor"]
    descriptor_hash_record = {key: value for key, value in descriptor_record.items() if not str(key).startswith("_")}
    v2id = str(descriptor_record.get("v2_exec_id"))
    patch_sha = str(descriptor.get("patch_sha256"))
    child = _v2id("chd", execution_authority_hash + patch_sha)
    proposal_id = next((ref for ref in _as_list(ticket.get("evidence_refs")) if ref.startswith("step-")), None)
    if not proposal_id:
        proposal_id = "recovered-proposal-" + _sha16(str(record.get("checkpoint_id")) + ticket_id + execution_authority_hash)
    prepared_action = {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_APPLY_PATCH,
        "execution_authority_hash": execution_authority_hash,
        "patch_sha256": patch_sha,
        "target_paths": _as_list(descriptor.get("target_paths")),
        "before_digests": dict(descriptor.get("before_digests") or {}),
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": _sha16(json.dumps(descriptor, sort_keys=True)),
        "desc_hash": _descriptor_record_hash(descriptor_hash_record),
        "_stores_base_dir": str(_DEFAULT_PREPARE_STORE),
    }
    feedback = {
        "mission_id": state.get("mission_id") or record.get("mission_id"),
        "selected_ticket_id": ticket_id,
        "proposal_id": proposal_id,
        "proposal_hash": _sha16(proposal_id + execution_authority_hash + patch_sha),
        "mandate_reference": state.get("human_mandate_reference") or record.get("human_mandate_reference"),
        "project": _project_from_state(state),
        "r9_candidate_reference": {
            "candidate_patch_hash": patch_sha,
            "r9_proposal_id": next((ref for ref in _as_list(ticket.get("evidence_refs")) if ref.startswith("obp-")), None),
            "manifest_id": next((ref for ref in _as_list(ticket.get("evidence_refs")) if ref.startswith("obm-")), None),
            "validation_id": next((ref for ref in _as_list(ticket.get("evidence_refs")) if ref.startswith("obv-")), None),
            "handoff_id": next((ref for ref in _as_list(ticket.get("evidence_refs")) if ref.startswith("obh-")), None),
        },
        "prepared_action_reference": prepared_action,
        "evidence_refs": _as_list(ticket.get("evidence_refs")),
    }
    return {
        "status": F3B_STATUS_PREPARED,
        "prepare_handoff": True,
        "mission_id": feedback["mission_id"],
        "selected_ticket_id": ticket_id,
        "handoff_feedback": feedback,
        "r9_prepare_result": {
            "status": "RECONSTRUCTED_FROM_CANONICAL_DESCRIPTOR",
            "descriptor_path": descriptor_record.get("_descriptor_path"),
            "v2_exec_id": v2id,
            "prepared_action": prepared_action,
        },
    }, None


def _execution_feedback_projection_from_checkpoint(record: Mapping[str, Any], ticket_id: str) -> tuple[dict[str, Any] | None, str | None]:
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    ticket = _find_ticket(state, ticket_id)
    if ticket is None:
        return None, "VERIFICATION_TICKET_NOT_FOUND"
    action_evidence_id = ticket.get("action_evidence_id") or record.get("action_evidence_id")
    execution_attempt_id = ticket.get("execution_attempt_id") or record.get("execution_attempt_id")
    if not action_evidence_id:
        return None, "EXECUTION_OBSERVATION_REQUIRED"
    dep = record.get("dependency_projection") if isinstance(record.get("dependency_projection"), Mapping) else {}
    return {
        "status": F5C1_STATUS_PROJECTED,
        "mission_update_accepted": True,
        "execution_feedback_projected": True,
        "mission_id": record.get("mission_id") or state.get("mission_id"),
        "selected_ticket_id": ticket_id,
        "accepted_state": deepcopy(dict(state)),
        "dependency_projection": deepcopy(dict(dep)),
        "next_step": deepcopy(dict(record.get("next_step") or {})),
        "action_evidence_id": action_evidence_id,
        "execution_attempt_id": execution_attempt_id,
        "execution_phase": ticket.get("execution_phase") or record.get("execution_phase"),
        "git_base_evolution": deepcopy(dict(record.get("git_base_evolution") or {})),
        "transitive_dependency_blocks": deepcopy(list(dep.get("transitive_dependency_blocks") or [])),
        "root_dependency_blocks": deepcopy(list(dep.get("root_dependency_blocks") or [])),
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY,
    }, None


def _verification_projection(record: Mapping[str, Any], ticket_id: str, assessment: Mapping[str, Any] | None = None) -> dict[str, Any]:
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    ticket = _find_ticket(state, ticket_id) or {}
    replay = assessment.get("verification_evidence", {}).get("r8_replay") if isinstance(assessment, Mapping) and isinstance(assessment.get("verification_evidence"), Mapping) else None
    if not isinstance(replay, Mapping) and isinstance(assessment, Mapping):
        replay = assessment.get("r8_replay") if isinstance(assessment.get("r8_replay"), Mapping) else None
    reconciliation = assessment.get("verification_evidence", {}).get("realized_state_reconciliation") if isinstance(assessment, Mapping) and isinstance(assessment.get("verification_evidence"), Mapping) else None
    if not isinstance(reconciliation, Mapping) and isinstance(assessment, Mapping):
        reconciliation = assessment.get("realized_state_reconciliation") if isinstance(assessment.get("realized_state_reconciliation"), Mapping) else None
    binder_status = str((replay or {}).get("binder_replay_status") or "")
    replay_verdict = str((replay or {}).get("replay_verdict") or "UNKNOWN")
    assessment_status = str((assessment or {}).get("status") or "")
    assessment_reason = str((assessment or {}).get("reason") or "")
    closure = "CLOSURE_BLOCKED"
    if assessment_status == F5C2_STATUS_VERIFIED:
        closure = "MISSION_CLOSURE_ELIGIBLE" if assessment.get("mission_done") is True else "TICKET_CLOSURE_ELIGIBLE"
    elif ticket.get("closed") is True and state.get("mission_done_verified") is True:
        closure = "MISSION_DONE_VERIFIED"
    reason = assessment_reason or ticket.get("hold_reason") or record.get("hold_reason")
    if binder_status == "INLINE_STATUS_ONLY" or "BINDER_DECISION_RECONSTRUCTION_REQUIRED" in str(reason or ""):
        reason = "BINDER_DECISION_RECONSTRUCTION_REQUIRED"
        closure = "CLOSURE_BLOCKED"
    action_evidence_id = ticket.get("action_evidence_id") or record.get("action_evidence_id")
    receipt_refs = _as_list(ticket.get("receipt_refs") or ticket.get("r8_receipt_refs"))
    return {
        "schema_version": "OBSIDURE_SUPERVISED_MISSION_VERIFICATION_PROJECTION_V1",
        "mission_id": record.get("mission_id") or state.get("mission_id"),
        "ticket_id": ticket_id,
        "execution_observation": {
            "phase": ticket.get("execution_phase") or record.get("execution_phase") or "UNKNOWN",
            "action_evidence_id": action_evidence_id,
            "execution_attempt_id": ticket.get("execution_attempt_id") or record.get("execution_attempt_id"),
            "executed_observed_is_verified": False,
        },
        "receipt_integrity": {
            "receipt_refs": receipt_refs,
            "r8_replay_verdict": replay_verdict,
            "realized_state_reconciliation": (reconciliation or {}).get("reconciliation_status", "UNKNOWN"),
        },
        "r8_replay": {
            "replay_verdict": replay_verdict,
            "binder_replay_status": binder_status or "UNKNOWN",
            "verified_with_limits": replay_verdict == "VERIFIED_WITH_LIMITS",
        },
        "binder_independence": {
            "fully_independent": bool(replay_verdict == "VERIFIED" and binder_status not in {"INLINE_STATUS_ONLY", "NOT_REACHED", "UNKNOWN", ""}),
            "limitation": "BINDER_DECISION_RECONSTRUCTION_REQUIRED" if binder_status == "INLINE_STATUS_ONLY" else None,
        },
        "independent_verification": {
            "status": ticket.get("independent_verification_status") or assessment_status or "UNKNOWN",
            "level": ticket.get("verification_level") or (assessment or {}).get("verification_level") or "UNKNOWN",
            "assessment_status": assessment_status or None,
            "assessment_reason": assessment_reason or None,
        },
        "closure_eligibility": closure,
        "hold_reasons": [reason] if reason else [],
        "mission_completion_proof_ref": _completion_reference(record, state),
        "status_distinctions": {
            "executed_observed_is_verified": False,
            "verified_is_closed": False,
            "closed_is_mission_done_verified": False,
            "http_success_is_closure": False,
        },
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


@router.post("/{mission_id}/authorize-execution", response_model=None)
async def authorize_supervised_ticket_execution(
    mission_id: str,
    payload: Mapping[str, Any] = Body(...),
) -> Any:
    if not _MISSION_ID.fullmatch(mission_id):
        return _auth_fail("INVALID_MISSION_ID", status=AUTH_STATUS_REJECTED, http_status=422, mission_id=mission_id)
    if not isinstance(payload, Mapping):
        return _auth_fail("REQUEST_BODY_REQUIRED", status=AUTH_STATUS_REJECTED, http_status=422, mission_id=mission_id)
    checkpoint_id = str(payload.get("checkpoint_id") or "").strip()
    ticket_id = str(payload.get("ticket_id") or payload.get("selected_ticket_id") or "").strip()
    execution_authority_hash = str(payload.get("execution_authority_hash") or "").lower().strip()
    human_authorization_reference = str(payload.get("human_authorization_reference") or "").strip()
    auth_hash = _auth_ref_hash(human_authorization_reference)
    if not _CHECKPOINT_ID.fullmatch(checkpoint_id):
        return _auth_fail("INVALID_CHECKPOINT_ID", status=AUTH_STATUS_REJECTED, http_status=422, mission_id=mission_id, ticket_id=ticket_id)
    if not ticket_id:
        return _auth_fail("TICKET_ID_REQUIRED", status=AUTH_STATUS_REJECTED, http_status=422, mission_id=mission_id, checkpoint_id=checkpoint_id)
    if not _HEX64.fullmatch(execution_authority_hash) or not human_authorization_reference:
        return _auth_fail(
            HOLD_AWAITING_VALID_AUTHORIZATION,
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash or None,
            human_authorization_reference_hash=auth_hash,
        )
    record, load_reason = load_supervised_mission_checkpoint(checkpoint_id, checkpoint_store_dir=_DEFAULT_STORE)
    if record is None:
        status = 404 if load_reason == "CHECKPOINT_NOT_FOUND" else 409
        return _auth_fail(
            str(load_reason or "CHECKPOINT_LOAD_FAILED"),
            status=AUTH_STATUS_REJECTED if status == 404 else AUTH_STATUS_HELD,
            http_status=status,
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash,
            human_authorization_reference_hash=auth_hash,
        )
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    if record.get("mission_id") != mission_id and state.get("mission_id") != mission_id:
        return _auth_fail("MISSION_CHECKPOINT_MISMATCH", status=AUTH_STATUS_REJECTED, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    ticket = _find_ticket(state, ticket_id)
    if ticket is None:
        return _auth_fail("PREPARED_TICKET_NOT_FOUND", status=AUTH_STATUS_REJECTED, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    if ticket.get("action_evidence_id"):
        return _auth_fail(
            "DUPLICATE_EXECUTION_REQUIRES_RECONCILIATION",
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash,
            human_authorization_reference_hash=auth_hash,
            prior_action_evidence_id=ticket.get("action_evidence_id"),
        )
    project, project_reason = _observed_worktree_identity(_project_from_state(state))
    if project_reason:
        return _auth_fail(project_reason, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id, execution_authority_hash=execution_authority_hash, human_authorization_reference_hash=auth_hash)
    assert project is not None
    mission_update = _mission_update_from_checkpoint(record)
    handoff, handoff_reason = _handoff_from_checkpoint(record=record, ticket_id=ticket_id, execution_authority_hash=execution_authority_hash)
    if handoff is None:
        return _auth_fail(str(handoff_reason or "PREPARE_HANDOFF_RECONSTRUCTION_FAILED"), mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id, execution_authority_hash=execution_authority_hash, human_authorization_reference_hash=auth_hash)
    outcome = execute_supervised_governed_ticket(
        mission_update=mission_update,
        prepare_handoff_result=handoff,
        human_authorized_execution_authority_hash=execution_authority_hash,
        human_authorization_reference=human_authorization_reference,
        stores_base_dir=_DEFAULT_PREPARE_STORE,
        repo_root=project["worktree"],
        observed_project_head=project["head"],
        session_id=str(payload.get("session_id") or "r12-f6-d1"),
    )
    if outcome.get("status") == F5B_STATUS_HELD and outcome.get("execution_phase") != "OUTCOME_UNCERTAIN":
        body = _auth_fail(
            str(outcome.get("reason") or "GOVERNED_EXECUTION_HELD"),
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash,
            human_authorization_reference_hash=auth_hash,
            execution_outcome=outcome,
            executor_invoked=bool(outcome.get("executor_invoked")),
        )
        body["execution_phase"] = str(outcome.get("execution_phase") or "HOLD")
        return _json_response(body)
    post_code, post_head, _ = _git(Path(project["worktree"]), "rev-parse", "HEAD")
    observed_post_action_head = post_head.lower() if post_code == 0 and _HEX40.fullmatch(post_head.lower()) else project["head"]
    projected = project_supervised_execution_feedback(
        mission_update=mission_update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        checkpoint_store_dir=_DEFAULT_STORE,
        observed_post_action_head=observed_post_action_head,
    )
    if projected.get("status") != F5C1_STATUS_PROJECTED:
        body = _auth_fail(
            str(projected.get("reason") or "EXECUTION_FEEDBACK_PROJECTION_HELD"),
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash,
            human_authorization_reference_hash=auth_hash,
            execution_outcome=outcome,
            feedback_projection=projected,
            executor_invoked=bool(outcome.get("executor_invoked")),
        )
        body["execution_phase"] = str(outcome.get("execution_phase") or "HOLD")
        return _json_response(body)
    saved = projected.get("checkpoint") if isinstance(projected.get("checkpoint"), Mapping) else {}
    saved_record = saved.get("checkpoint") if isinstance(saved.get("checkpoint"), Mapping) else None
    checkpoint_projection = _projection(saved_record) if isinstance(saved_record, Mapping) else None
    return _json_response(
        {
            "schema_version": AUTH_HANDOFF_SCHEMA_VERSION,
            "status": AUTH_STATUS_ACCEPTED,
            "state": str(outcome.get("execution_phase") or "EXECUTION_ATTEMPTED"),
            "reason": None,
            "mission_id": mission_id,
            "ticket_id": ticket_id,
            "checkpoint_id": saved_record.get("checkpoint_id") if isinstance(saved_record, Mapping) else checkpoint_id,
            "input_checkpoint_id": checkpoint_id,
            "checkpoint_projection_available": checkpoint_projection is not None,
            "checkpoint_projection": checkpoint_projection,
            "execution_phase": outcome.get("execution_phase"),
            "execution_outcome": outcome,
            "action_evidence_id": outcome.get("action_evidence_id"),
            "r8_receipt": outcome.get("r8_receipt_ref"),
            "r8_replay": outcome.get("r8_replay"),
            "realized_state_reconciliation": outcome.get("realized_state_reconciliation"),
            "r10_repair_classification": outcome.get("r10_repair_advice")
            or {"classification": "NOT_APPLICABLE", "repair_launch_allowed": False, "automatic_retry": False},
            "execution_authority_hash": execution_authority_hash,
            "human_authorization_reference_hash": auth_hash,
            "supervisor_approval_created": False,
            "no_false_verification": True,
            "no_automatic_retry": True,
            "readonly": False,
            "authority": "NONE",
            "decision_authority": DECISION_AUTHORITY,
            "supervisor_authority": "NONE",
            "emits_act": False,
            "approval_created": False,
            "automatic_approval": False,
            "kx108_called": bool(outcome.get("kx108_called")),
            "binder_mutation": False,
            "executor_invoked": bool(outcome.get("executor_invoked")),
            "repair_loop_invoked": False,
            "filesystem_execution": bool(outcome.get("executor_invoked")),
            "network_or_model_call": False,
            "memory_write": False,
            "native_memory_write": False,
            "commit_created": False,
            "push_performed": False,
            "merge_performed": False,
        }
    )


@router.get("/{mission_id}/verification-projection")
async def supervised_verification_projection(
    mission_id: str,
    checkpoint_id: str = Query(..., description="Canonical F5-A checkpoint id to inspect."),
    ticket_id: str = Query(..., description="Prepared or executed supervised ticket id."),
) -> dict[str, Any]:
    if not _MISSION_ID.fullmatch(mission_id):
        raise HTTPException(status_code=422, detail={"reason": "INVALID_MISSION_ID", **_NO_AUTHORITY})
    if not _CHECKPOINT_ID.fullmatch(checkpoint_id):
        raise HTTPException(status_code=422, detail={"reason": "INVALID_CHECKPOINT_ID", **_NO_AUTHORITY})
    record, reason = load_supervised_mission_checkpoint(checkpoint_id, checkpoint_store_dir=_DEFAULT_STORE)
    if record is None:
        status = 404 if reason == "CHECKPOINT_NOT_FOUND" else 409
        raise HTTPException(status_code=status, detail={"reason": reason or "CHECKPOINT_LOAD_FAILED", **_NO_AUTHORITY})
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    if record.get("mission_id") != mission_id and state.get("mission_id") != mission_id:
        raise HTTPException(status_code=404, detail={"reason": "MISSION_CHECKPOINT_MISMATCH", **_NO_AUTHORITY})
    projection, projection_reason = _execution_feedback_projection_from_checkpoint(record, ticket_id)
    verification = _verification_projection(record, ticket_id)
    status = VERIFICATION_STATUS_PROJECTED if projection is not None else VERIFICATION_STATUS_HELD
    if projection_reason:
        verification["hold_reasons"] = [projection_reason]
        verification["closure_eligibility"] = "CLOSURE_BLOCKED"
    return api_projection(
        {
            "schema_version": VERIFICATION_SCHEMA_VERSION,
            "status": status,
            "state": "PROJECTED" if projection is not None else "HOLD",
            "reason": projection_reason,
            "mission_id": mission_id,
            "checkpoint_id": checkpoint_id,
            "ticket_id": ticket_id,
            "verification_projection": verification,
            "execution_feedback_projection_available": projection is not None,
            "closure_eligibility": verification.get("closure_eligibility"),
            "no_false_closure": True,
            **_NO_AUTHORITY,
            "readonly": True,
        }
    )


@router.post("/{mission_id}/verify-ticket", response_model=None)
async def verify_supervised_ticket_operator_projection(
    mission_id: str,
    payload: Mapping[str, Any] = Body(...),
) -> Any:
    if not _MISSION_ID.fullmatch(mission_id):
        return _verification_fail("INVALID_MISSION_ID", status=VERIFICATION_STATUS_REJECTED, http_status=422, mission_id=mission_id)
    if not isinstance(payload, Mapping):
        return _verification_fail("REQUEST_BODY_REQUIRED", status=VERIFICATION_STATUS_REJECTED, http_status=422, mission_id=mission_id)
    checkpoint_id = str(payload.get("checkpoint_id") or "").strip()
    ticket_id = str(payload.get("ticket_id") or "").strip()
    if not _CHECKPOINT_ID.fullmatch(checkpoint_id):
        return _verification_fail("INVALID_CHECKPOINT_ID", status=VERIFICATION_STATUS_REJECTED, http_status=422, mission_id=mission_id, ticket_id=ticket_id)
    if not ticket_id:
        return _verification_fail("TICKET_ID_REQUIRED", status=VERIFICATION_STATUS_REJECTED, http_status=422, mission_id=mission_id, checkpoint_id=checkpoint_id)
    evidence = payload.get("verification_evidence")
    if not isinstance(evidence, Mapping):
        return _verification_fail("VERIFICATION_EVIDENCE_REQUIRED", status=VERIFICATION_STATUS_REJECTED, http_status=422, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    record, load_reason = load_supervised_mission_checkpoint(checkpoint_id, checkpoint_store_dir=_DEFAULT_STORE)
    if record is None:
        status = 404 if load_reason == "CHECKPOINT_NOT_FOUND" else 409
        return _verification_fail(str(load_reason or "CHECKPOINT_LOAD_FAILED"), status=VERIFICATION_STATUS_REJECTED if status == 404 else VERIFICATION_STATUS_HELD, http_status=status, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    state = record.get("accepted_state") if isinstance(record.get("accepted_state"), Mapping) else {}
    if record.get("mission_id") != mission_id and state.get("mission_id") != mission_id:
        return _verification_fail("MISSION_CHECKPOINT_MISMATCH", status=VERIFICATION_STATUS_REJECTED, mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    execution_projection, projection_reason = _execution_feedback_projection_from_checkpoint(record, ticket_id)
    if execution_projection is None:
        return _verification_fail(projection_reason or "EXECUTION_FEEDBACK_PROJECTION_REQUIRED", mission_id=mission_id, checkpoint_id=checkpoint_id, ticket_id=ticket_id)
    assessment = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=execution_projection,
        verification_evidence=dict(evidence),
        prior_verification_evidence=payload.get("prior_verification_evidence") if isinstance(payload.get("prior_verification_evidence"), Mapping) else None,
        checkpoint_store_dir=None,
        observed_project_head=str(payload.get("observed_project_head") or "") or None,
    )
    verification = _verification_projection(record, ticket_id, {**assessment, "verification_evidence": dict(evidence)})
    status = VERIFICATION_STATUS_ASSESSED if assessment.get("status") == F5C2_STATUS_VERIFIED else VERIFICATION_STATUS_HELD
    if assessment.get("status") == F5C2_STATUS_REJECTED:
        status = VERIFICATION_STATUS_REJECTED
    return _json_response(
        {
            "schema_version": VERIFICATION_SCHEMA_VERSION,
            "status": status,
            "state": verification.get("closure_eligibility"),
            "reason": assessment.get("reason"),
            "mission_id": mission_id,
            "checkpoint_id": checkpoint_id,
            "ticket_id": ticket_id,
            "verification_projection": verification,
            "verification_assessment": assessment,
            "receipt_integrity": verification.get("receipt_integrity"),
            "r8_replay": verification.get("r8_replay"),
            "binder_independence": verification.get("binder_independence"),
            "closure_eligibility": verification.get("closure_eligibility"),
            "persisted": False,
            "no_false_closure": True,
            **_NO_AUTHORITY,
            "readonly": True,
        }
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
    return api_projection(projection)


@router.get("/checkpoints/{checkpoint_id}/projection")
async def supervised_checkpoint_projection(checkpoint_id: str) -> dict[str, Any]:
    return _load_projection(checkpoint_id)
