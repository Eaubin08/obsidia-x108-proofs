"""TASKS_NATIVE_V0 — canonical Obsidia task state and governed mutations."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Mapping, Optional

from .common_v0 import (
    ABSENT_STATE_HASH,
    NativeEntityStoreV0,
    NativeMutationReceiptV0,
    NativeMutationV0,
    build_native_mutation_v0,
)
from .world_action_bridge_v0 import verify_native_apply_authority_v0

DOMAIN_ID = "native_tasks"
ENTITY_KIND = "task"

STATUS_TODO = "TODO"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_BLOCKED = "BLOCKED"
STATUS_DONE = "DONE"
STATUS_CANCELLED = "CANCELLED"

VALID_STATUSES = {
    STATUS_TODO,
    STATUS_IN_PROGRESS,
    STATUS_BLOCKED,
    STATUS_DONE,
    STATUS_CANCELLED,
}
TERMINAL_STATUSES = {STATUS_DONE, STATUS_CANCELLED}

VALID_PRIORITIES = {"LOW", "NORMAL", "HIGH", "CRITICAL"}

_ALLOWED_TRANSITIONS = {
    STATUS_TODO: {STATUS_IN_PROGRESS, STATUS_BLOCKED, STATUS_CANCELLED},
    STATUS_IN_PROGRESS: {STATUS_BLOCKED, STATUS_DONE, STATUS_CANCELLED},
    STATUS_BLOCKED: {STATUS_TODO, STATUS_IN_PROGRESS, STATUS_CANCELLED},
    STATUS_DONE: set(),
    STATUS_CANCELLED: set(),
}

OPERATIONS = {
    "CREATE_TASK",
    "UPDATE_TASK",
    "ASSIGN_TASK",
    "SET_STATUS",
    "SET_DUE_AT",
    "ADD_DEPENDENCY",
    "REMOVE_DEPENDENCY",
    "ADD_TAG",
    "REMOVE_TAG",
}


def _require_time(value: str) -> str:
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("TASK_TIME_MUST_BE_TIMEZONE_AWARE")
    return value


def build_task_mutation_v0(
    *,
    mutation_id: str,
    task_id: str,
    operation: str,
    payload: Mapping[str, Any],
    expected_prestate_hash: str,
    source_refs: tuple[str, ...],
    requested_by: str,
) -> NativeMutationV0:
    if operation not in OPERATIONS:
        raise ValueError(f"TASK_OPERATION_UNSUPPORTED:{operation}")
    if "occurred_at" not in payload:
        raise ValueError("TASK_MUTATION_OCCURRED_AT_REQUIRED")
    _require_time(str(payload["occurred_at"]))
    return build_native_mutation_v0(
        mutation_id=mutation_id,
        domain_id=DOMAIN_ID,
        entity_kind=ENTITY_KIND,
        entity_id=task_id,
        operation=operation,
        payload=payload,
        expected_prestate_hash=expected_prestate_hash,
        source_refs=source_refs,
        requested_by=requested_by,
    )


def _validate_create_payload(payload: Mapping[str, Any]) -> None:
    required = {
        "occurred_at",
        "title",
        "description",
        "priority",
        "assignee_ref",
        "due_at",
        "dependency_ids",
        "tags",
    }
    if set(payload) != required:
        raise ValueError("TASK_CREATE_PAYLOAD_SHAPE_INVALID")
    if not str(payload["title"]).strip():
        raise ValueError("TASK_TITLE_REQUIRED")
    if payload["priority"] not in VALID_PRIORITIES:
        raise ValueError("TASK_PRIORITY_INVALID")
    if payload["due_at"] is not None:
        _require_time(str(payload["due_at"]))
    if len(set(payload["dependency_ids"])) != len(payload["dependency_ids"]):
        raise ValueError("TASK_DEPENDENCY_DUPLICATE")
    if len(set(payload["tags"])) != len(payload["tags"]):
        raise ValueError("TASK_TAG_DUPLICATE")


def _base_state_from_create(
    task_id: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_create_payload(payload)
    return {
        "schema": "TASK_NATIVE_V0",
        "task_id": task_id,
        "title": str(payload["title"]),
        "description": str(payload["description"]),
        "status": STATUS_TODO,
        "priority": str(payload["priority"]),
        "assignee_ref": payload["assignee_ref"],
        "due_at": payload["due_at"],
        "dependency_ids": sorted(set(payload["dependency_ids"])),
        "tags": sorted(set(payload["tags"])),
        "created_at": payload["occurred_at"],
        "updated_at": payload["occurred_at"],
        "version": 1,
    }


def _validate_dependencies_exist(
    store: NativeEntityStoreV0,
    task_id: str,
    dependency_ids: list[str],
) -> None:
    for dependency_id in dependency_ids:
        if dependency_id == task_id:
            raise ValueError("TASK_SELF_DEPENDENCY_FORBIDDEN")
        if store.load_state(DOMAIN_ID, ENTITY_KIND, dependency_id) is None:
            raise ValueError(
                f"TASK_DEPENDENCY_NOT_FOUND:{dependency_id}"
            )


def _next_state(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    payload = mutation.payload
    occurred_at = str(payload["occurred_at"])

    if mutation.operation == "CREATE_TASK":
        if current is not None:
            raise ValueError("TASK_ALREADY_EXISTS")
        state = _base_state_from_create(mutation.entity_id, payload)
        _validate_dependencies_exist(
            store, mutation.entity_id, list(state["dependency_ids"])
        )
        return state

    if current is None:
        raise ValueError("TASK_NOT_FOUND")
    if current["status"] in TERMINAL_STATUSES:
        raise ValueError("TASK_TERMINAL_STATE_IMMUTABLE")

    state = dict(current)
    state["version"] = int(current["version"]) + 1
    state["updated_at"] = occurred_at

    if mutation.operation == "UPDATE_TASK":
        allowed = {"occurred_at", "title", "description", "priority"}
        if not set(payload).issubset(allowed) or len(payload) <= 1:
            raise ValueError("TASK_UPDATE_PAYLOAD_INVALID")
        if "title" in payload:
            if not str(payload["title"]).strip():
                raise ValueError("TASK_TITLE_REQUIRED")
            state["title"] = str(payload["title"])
        if "description" in payload:
            state["description"] = str(payload["description"])
        if "priority" in payload:
            if payload["priority"] not in VALID_PRIORITIES:
                raise ValueError("TASK_PRIORITY_INVALID")
            state["priority"] = str(payload["priority"])

    elif mutation.operation == "ASSIGN_TASK":
        if set(payload) != {"occurred_at", "assignee_ref"}:
            raise ValueError("TASK_ASSIGN_PAYLOAD_INVALID")
        state["assignee_ref"] = payload["assignee_ref"]

    elif mutation.operation == "SET_STATUS":
        if set(payload) != {"occurred_at", "status"}:
            raise ValueError("TASK_STATUS_PAYLOAD_INVALID")
        new_status = str(payload["status"])
        if new_status not in VALID_STATUSES:
            raise ValueError("TASK_STATUS_INVALID")
        if new_status == current["status"]:
            raise ValueError("TASK_STATUS_NOOP")
        if new_status not in _ALLOWED_TRANSITIONS[current["status"]]:
            raise ValueError(
                f"TASK_STATUS_TRANSITION_INVALID:"
                f"{current['status']}->{new_status}"
            )
        state["status"] = new_status

    elif mutation.operation == "SET_DUE_AT":
        if set(payload) != {"occurred_at", "due_at"}:
            raise ValueError("TASK_DUE_PAYLOAD_INVALID")
        if payload["due_at"] is not None:
            _require_time(str(payload["due_at"]))
        state["due_at"] = payload["due_at"]

    elif mutation.operation == "ADD_DEPENDENCY":
        if set(payload) != {"occurred_at", "dependency_id"}:
            raise ValueError("TASK_DEPENDENCY_PAYLOAD_INVALID")
        dependency_id = str(payload["dependency_id"])
        _validate_dependencies_exist(
            store, mutation.entity_id, [dependency_id]
        )
        deps = set(current["dependency_ids"])
        if dependency_id in deps:
            raise ValueError("TASK_DEPENDENCY_ALREADY_PRESENT")
        deps.add(dependency_id)
        state["dependency_ids"] = sorted(deps)

    elif mutation.operation == "REMOVE_DEPENDENCY":
        if set(payload) != {"occurred_at", "dependency_id"}:
            raise ValueError("TASK_DEPENDENCY_PAYLOAD_INVALID")
        dependency_id = str(payload["dependency_id"])
        deps = set(current["dependency_ids"])
        if dependency_id not in deps:
            raise ValueError("TASK_DEPENDENCY_NOT_PRESENT")
        deps.remove(dependency_id)
        state["dependency_ids"] = sorted(deps)

    elif mutation.operation == "ADD_TAG":
        if set(payload) != {"occurred_at", "tag"}:
            raise ValueError("TASK_TAG_PAYLOAD_INVALID")
        tag = str(payload["tag"]).strip()
        if not tag:
            raise ValueError("TASK_TAG_REQUIRED")
        tags = set(current["tags"])
        if tag in tags:
            raise ValueError("TASK_TAG_ALREADY_PRESENT")
        tags.add(tag)
        state["tags"] = sorted(tags)

    elif mutation.operation == "REMOVE_TAG":
        if set(payload) != {"occurred_at", "tag"}:
            raise ValueError("TASK_TAG_PAYLOAD_INVALID")
        tag = str(payload["tag"]).strip()
        tags = set(current["tags"])
        if tag not in tags:
            raise ValueError("TASK_TAG_NOT_PRESENT")
        tags.remove(tag)
        state["tags"] = sorted(tags)

    else:
        raise ValueError("TASK_OPERATION_UNSUPPORTED")

    return state


def apply_task_mutation_v0(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    request: Mapping[str, Any],
    decision_record_id: str,
    decision_store_dir: Optional[Path],
    context_store_dir: Optional[Path],
) -> NativeMutationReceiptV0:
    if mutation.domain_id != DOMAIN_ID or mutation.entity_kind != ENTITY_KIND:
        raise ValueError("TASK_MUTATION_DOMAIN_INVALID")
    ok, reason, decision = verify_native_apply_authority_v0(
        mutation=mutation,
        request=request,
        decision_record_id=decision_record_id,
        decision_store_dir=decision_store_dir,
        context_store_dir=context_store_dir,
    )
    if not ok:
        raise ValueError(reason or "TASK_KX108_AUTHORITY_INVALID")

    current_hash = store.state_hash(DOMAIN_ID, ENTITY_KIND, mutation.entity_id)
    if current_hash != mutation.expected_prestate_hash:
        raise ValueError("TASK_PRESTATE_CHANGED")
    current = store.load_state(DOMAIN_ID, ENTITY_KIND, mutation.entity_id)
    after = _next_state(store=store, mutation=mutation, current=current)
    return store.commit(
        mutation=mutation,
        world_action_request_hash=request["request_hash"],
        kx108_decision_record_id=decision["decision_record_id"],
        kx108_decision_record_hash=decision["decision_record_hash"],
        after_state=after,
        created_at=str(mutation.payload["occurred_at"]),
    )
