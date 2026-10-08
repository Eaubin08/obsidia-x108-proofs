from __future__ import annotations

"""R12-F5-A durable supervised mission checkpoints.

The checkpoint is a prepare-only, evidence-bearing snapshot of the accepted
F1-F4-B supervised mission state. It is durable and integrity checked, but it is
not memory, authority, approval, execution, verification, or mission closure.
Resume revalidates the checkpoint and recomputes F4-A dependency readiness and
F3-A NEXT; it never replays a previous prepare blindly.
"""

import hashlib
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_dependency_state_integration_v1 import STATUS_UPDATED as F4B_STATUS_UPDATED  # noqa: E402
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_transitive_hold_projection_v1 import (  # noqa: E402
    STATUS_PROJECTED as F4A_STATUS_PROJECTED,
    project_transitive_dependency_blocks,
)

CHECKPOINT_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_CHECKPOINT_V1"
STATUS_SAVED = "R12_F5_A_CHECKPOINT_SAVED"
STATUS_RESTORED = "R12_F5_A_CHECKPOINT_RESTORED"
STATUS_HELD = "R12_F5_A_CHECKPOINT_HELD"
STATUS_REJECTED = "R12_F5_A_CHECKPOINT_REJECTED"

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
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
    "autonomous_loop": False,
    "automatic_retry": False,
    "ticket_completed": False,
    "prepared_promoted_to_executed": False,
    "prepared_promoted_to_verified": False,
    "prepared_promoted_to_closed": False,
}

_BOUND_FIELDS = (
    "schema_version",
    "checkpoint_id",
    "mission_id",
    "human_mandate_reference",
    "project",
    "original_goal",
    "acceptance_criteria",
    "accepted_state",
    "accepted_state_hash",
    "dependency_projection_hash",
    "next_step_hash",
    "pending_approvals",
    "evidence_references",
    "checkpoint_kind",
    "decision_authority",
)


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "checkpoint_saved": False,
        "checkpoint_restored": False,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _safe_checkpoint_path(store_dir: Path, checkpoint_id: str) -> Path:
    if not isinstance(checkpoint_id, str) or not checkpoint_id.startswith("smc-") or len(checkpoint_id) > 80:
        raise ValueError("INVALID_CHECKPOINT_ID")
    path = (store_dir / f"{checkpoint_id}.json").resolve()
    path.relative_to(store_dir.resolve())
    return path


def _atomic_publish_json(path: Path, record: Mapping[str, Any]) -> str:
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{os.getpid()}.{_sha256(payload)[:16]}.tmp"
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return "STORED"
    except FileExistsError:
        existing = path.read_text(encoding="utf-8")
        return "IDEMPOTENT_EXISTING_IDENTICAL" if existing == payload else "IMMUTABILITY_VIOLATION"
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _record_hash(record: Mapping[str, Any]) -> str:
    return _sha256({key: record.get(key) for key in _BOUND_FIELDS})


def _pending_approvals(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    pending: list[dict[str, Any]] = []
    for ticket in state.get("tickets") or ():
        if not isinstance(ticket, Mapping):
            continue
        if ticket.get("status") == "HELD" and ticket.get("hold_reason") == "PREPARED_AWAITING_APPROVAL":
            pending.append(
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "hold_reason": ticket.get("hold_reason"),
                    "evidence_refs": _as_list(ticket.get("evidence_refs")),
                }
            )
    return pending


def _checkpoint_from_update(update_result: Mapping[str, Any]) -> dict[str, Any] | None:
    if update_result.get("status") != F4B_STATUS_UPDATED or update_result.get("mission_update_accepted") is not True:
        return None
    state = update_result.get("accepted_state")
    dep = update_result.get("dependency_projection")
    next_step = update_result.get("next_step")
    if not isinstance(state, Mapping) or not isinstance(dep, Mapping) or not isinstance(next_step, Mapping):
        return None
    project = {
        "repository_identity": state.get("repository_identity"),
        "local_root": state.get("local_root"),
        "worktree": state.get("worktree"),
        "branch": state.get("branch"),
        "base_sha": state.get("base_sha"),
    }
    state_hash = _sha256(state)
    checkpoint_id = "smc-" + _sha256(
        {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "mission_id": state.get("mission_id"),
            "state_hash": state_hash,
            "dependency_projection_hash": _sha256(dep),
            "next_step_hash": _sha256(next_step),
        }
    )[:32]
    evidence_refs = _dedupe(_as_list(state.get("evidence_refs")) + _as_list(update_result.get("evidence_references")))
    record = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_id": checkpoint_id,
        "mission_id": state.get("mission_id"),
        "human_mandate_reference": state.get("human_mandate_reference"),
        "project": project,
        "original_goal": state.get("original_goal"),
        "acceptance_criteria": list(_as_list(state.get("acceptance_criteria"))),
        "ticket_dag": [
            {
                "ticket_id": ticket.get("ticket_id"),
                "dependency_ids": _as_list(ticket.get("dependency_ids")),
                "status": ticket.get("status"),
            }
            for ticket in state.get("tickets") or ()
            if isinstance(ticket, Mapping)
        ],
        "accepted_state": deepcopy(dict(state)),
        "accepted_state_hash": state_hash,
        "dependency_projection": deepcopy(dict(dep)),
        "dependency_projection_hash": _sha256(dep),
        "next_step": deepcopy(dict(next_step)),
        "next_step_hash": _sha256(next_step),
        "blocker_root_causes": list(dep.get("root_dependency_blocks") or []) + list(dep.get("transitive_dependency_blocks") or []),
        "pending_approvals": _pending_approvals(state),
        "unique_next_ticket_id": dep.get("unique_next_ticket_id"),
        "hold_reason": dep.get("reason"),
        "budget": deepcopy(dict(state.get("global_budget") or {})),
        "timebox": deepcopy(dict(state.get("timebox") or {})),
        "semantic_unknowns": _as_list(state.get("explicit_unknowns")),
        "evidence_references": evidence_refs,
        "checkpoint_kind": "PREPARE_ONLY_SUPERVISED_STATE",
        "decision_authority": DECISION_AUTHORITY,
        "checkpoint_is_execution_authority": False,
        "checkpoint_is_human_approval": False,
        "checkpoint_marks_execution": False,
        "checkpoint_marks_verified_or_closed": False,
        **_NO_AUTHORITY_FIELDS,
    }
    record["integrity_digest"] = _record_hash(record)
    return record


def verify_supervised_mission_checkpoint(record: Mapping[str, Any] | None) -> tuple[bool, str | None]:
    if not isinstance(record, Mapping):
        return False, "CHECKPOINT_MISSING"
    if record.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        return False, "CHECKPOINT_SCHEMA_UNSUPPORTED"
    for key in _BOUND_FIELDS + ("integrity_digest",):
        if key not in record:
            return False, "CHECKPOINT_FIELD_MISSING:" + key.upper()
    if record.get("integrity_digest") != _record_hash(record):
        return False, "CHECKPOINT_DIGEST_MISMATCH"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "CHECKPOINT_DECISION_AUTHORITY_INVALID"
    for key in ("approval_created", "kx108_called", "binder_mutation", "executor_invoked", "memory_write", "native_memory_write"):
        if record.get(key) is True:
            return False, "CHECKPOINT_CARRIES_FORBIDDEN_AUTHORITY:" + key.upper()
    state = record.get("accepted_state")
    if not isinstance(state, Mapping):
        return False, "CHECKPOINT_ACCEPTED_STATE_REQUIRED"
    if _sha256(state) != record.get("accepted_state_hash"):
        return False, "CHECKPOINT_ACCEPTED_STATE_HASH_MISMATCH"
    dep = record.get("dependency_projection")
    if not isinstance(dep, Mapping) or _sha256(dep) != record.get("dependency_projection_hash"):
        return False, "CHECKPOINT_DEPENDENCY_PROJECTION_HASH_MISMATCH"
    next_step = record.get("next_step")
    if not isinstance(next_step, Mapping) or _sha256(next_step) != record.get("next_step_hash"):
        return False, "CHECKPOINT_NEXT_STEP_HASH_MISMATCH"
    return True, None


def save_supervised_mission_checkpoint(update_result: Mapping[str, Any], *, checkpoint_store_dir: str | Path) -> dict[str, Any]:
    record = _checkpoint_from_update(update_result)
    if record is None:
        return _fail(STATUS_REJECTED, "ACCEPTED_F4B_UPDATE_REQUIRED")
    store_dir = Path(checkpoint_store_dir)
    try:
        path = _safe_checkpoint_path(store_dir, record["checkpoint_id"])
    except ValueError as exc:
        return _fail(STATUS_REJECTED, str(exc))
    store_status = _atomic_publish_json(path, record)
    if store_status == "IMMUTABILITY_VIOLATION":
        return _fail(STATUS_HELD, "CHECKPOINT_IMMUTABILITY_VIOLATION", checkpoint_id=record["checkpoint_id"])
    ok, reason = verify_supervised_mission_checkpoint(record)
    if not ok:
        return _fail(STATUS_REJECTED, reason or "CHECKPOINT_VERIFY_FAILED")
    return {
        "adapter_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "status": STATUS_SAVED,
        "reason": None,
        "checkpoint_saved": True,
        "checkpoint_id": record["checkpoint_id"],
        "checkpoint_path": str(path),
        "checkpoint": record,
        "integrity_digest": record["integrity_digest"],
        "store_status": store_status,
        "snapshot_reuse": "atomic_append_only_json_store",
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


def load_supervised_mission_checkpoint(checkpoint_id: str, *, checkpoint_store_dir: str | Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        path = _safe_checkpoint_path(Path(checkpoint_store_dir), checkpoint_id)
    except ValueError as exc:
        return None, str(exc)
    try:
        if not path.exists():
            return None, "CHECKPOINT_NOT_FOUND"
        record = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return None, "CHECKPOINT_UTF8_INVALID"
    except json.JSONDecodeError:
        return None, "CHECKPOINT_JSON_INVALID"
    except OSError:
        return None, "CHECKPOINT_UNREADABLE"
    ok, reason = verify_supervised_mission_checkpoint(record)
    if not ok:
        return None, reason
    return dict(record), None


def resume_supervised_mission_checkpoint(
    checkpoint_id: str,
    *,
    checkpoint_store_dir: str | Path,
    observed_project_head: str | None = None,
    mandate_revoked: bool = False,
    mandate_status: str | None = None,
    timebox_expired: bool = False,
    known_evidence_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    record, reason = load_supervised_mission_checkpoint(checkpoint_id, checkpoint_store_dir=checkpoint_store_dir)
    if record is None:
        return _fail(STATUS_HELD, reason or "CHECKPOINT_LOAD_FAILED", checkpoint_id=checkpoint_id)
    state = deepcopy(dict(record["accepted_state"]))
    if mandate_revoked or str(mandate_status or state.get("mandate_status") or "ACTIVE").upper() == "REVOKED":
        return _fail(STATUS_HELD, "HUMAN_MANDATE_REVOKED", checkpoint_id=checkpoint_id, checkpoint=record)
    if mandate_status is not None:
        state["mandate_status"] = mandate_status
    if timebox_expired:
        timebox = dict(state.get("timebox") or {})
        timebox["expired"] = True
        state["timebox"] = timebox
    if known_evidence_refs is not None:
        known = set(str(item) for item in known_evidence_refs)
        missing = [ref for ref in _as_list(record.get("evidence_references")) if ref not in known]
        if missing:
            return _fail(STATUS_HELD, "UNKNOWN_EVIDENCE_REFERENCE", checkpoint_id=checkpoint_id, missing_evidence_refs=missing, checkpoint=record)

    dependency_projection = project_transitive_dependency_blocks(state, observed_project_head=observed_project_head)
    if dependency_projection.get("status") != F4A_STATUS_PROJECTED:
        return _fail(
            STATUS_HELD,
            str(dependency_projection.get("reason") or "DEPENDENCY_REPROJECTION_HELD"),
            checkpoint_id=checkpoint_id,
            checkpoint=record,
            dependency_projection=dependency_projection,
        )
    next_step = propose_supervised_mission_step(dependency_projection, observed_project_head=observed_project_head)
    return {
        "adapter_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "status": STATUS_RESTORED,
        "reason": None,
        "checkpoint_restored": True,
        "checkpoint_id": checkpoint_id,
        "checkpoint": record,
        "restored_state": state,
        "restored_state_hash": _sha256(state),
        "dependency_projection": dependency_projection,
        "next_step": next_step,
        "unique_next_ticket_id": dependency_projection.get("unique_next_ticket_id"),
        "pending_approvals": _pending_approvals(state),
        "prepare_available": next_step.get("status") == F3A_STATUS_PROPOSED,
        "budget": deepcopy(dict(state.get("global_budget") or {})),
        "timebox": deepcopy(dict(state.get("timebox") or {})),
        "idempotent_resume": True,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "CHECKPOINT_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_REJECTED",
    "STATUS_RESTORED",
    "STATUS_SAVED",
    "load_supervised_mission_checkpoint",
    "resume_supervised_mission_checkpoint",
    "save_supervised_mission_checkpoint",
    "verify_supervised_mission_checkpoint",
]
