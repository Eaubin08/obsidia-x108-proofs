"""CRM_NATIVE_V0 — canonical Obsidia CRM records, relations and timeline."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Mapping, Optional

from .common_v0 import (
    NativeEntityStoreV0,
    NativeMutationReceiptV0,
    NativeMutationV0,
    build_native_mutation_v0,
)
from .world_action_bridge_v0 import verify_native_apply_authority_v0

DOMAIN_ID = "native_crm"

KIND_RECORD = "record"
KIND_RELATIONSHIP = "relationship"
KIND_INTERACTION = "interaction"
KIND_FOLLOWUP = "followup"

RECORD_TYPES = {"PERSON", "ORGANIZATION", "CASE"}
RECORD_STATUSES = {
    "NEW", "ACTIVE", "INACTIVE", "OPEN", "CLOSED", "ARCHIVED"
}
INTERACTION_TYPES = {
    "NOTE", "EMAIL", "CALL", "MEETING", "FORM", "SYSTEM_EVENT"
}
FOLLOWUP_STATUSES = {"OPEN", "DONE", "CANCELLED"}

OPERATIONS = {
    "CREATE_RECORD",
    "UPDATE_FIELDS",
    "SET_OWNER",
    "SET_RECORD_STATUS",
    "ADD_RECORD_TAG",
    "REMOVE_RECORD_TAG",
    "CREATE_RELATIONSHIP",
    "DEACTIVATE_RELATIONSHIP",
    "APPEND_INTERACTION",
    "CREATE_FOLLOWUP",
    "CLOSE_FOLLOWUP",
    "CANCEL_FOLLOWUP",
}

_SECRET_FRAGMENTS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "authorization", "private_key", "access_key", "credential",
)


def _require_time(value: str) -> str:
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("CRM_TIME_MUST_BE_TIMEZONE_AWARE")
    return value


def _assert_no_secret_fields(value: Any, path: str = "fields") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in _SECRET_FRAGMENTS):
                raise ValueError(f"CRM_SECRET_FIELD_FORBIDDEN:{path}.{key}")
            _assert_no_secret_fields(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_no_secret_fields(child, f"{path}[{index}]")


def build_crm_mutation_v0(
    *,
    mutation_id: str,
    entity_kind: str,
    entity_id: str,
    operation: str,
    payload: Mapping[str, Any],
    expected_prestate_hash: str,
    source_refs: tuple[str, ...],
    requested_by: str,
) -> NativeMutationV0:
    if entity_kind not in {
        KIND_RECORD, KIND_RELATIONSHIP, KIND_INTERACTION, KIND_FOLLOWUP
    }:
        raise ValueError(f"CRM_ENTITY_KIND_UNSUPPORTED:{entity_kind}")
    if operation not in OPERATIONS:
        raise ValueError(f"CRM_OPERATION_UNSUPPORTED:{operation}")
    if "occurred_at" not in payload:
        raise ValueError("CRM_MUTATION_OCCURRED_AT_REQUIRED")
    _require_time(str(payload["occurred_at"]))
    _assert_no_secret_fields(payload)
    return build_native_mutation_v0(
        mutation_id=mutation_id,
        domain_id=DOMAIN_ID,
        entity_kind=entity_kind,
        entity_id=entity_id,
        operation=operation,
        payload=payload,
        expected_prestate_hash=expected_prestate_hash,
        source_refs=source_refs,
        requested_by=requested_by,
    )


def _record_exists(store: NativeEntityStoreV0, record_id: str) -> bool:
    return store.load_state(DOMAIN_ID, KIND_RECORD, record_id) is not None


def _task_exists(store: NativeEntityStoreV0, task_id: str) -> bool:
    return store.load_state("native_tasks", "task", task_id) is not None


def _record_next(
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> dict[str, Any]:
    p = mutation.payload
    occurred_at = str(p["occurred_at"])

    if mutation.operation == "CREATE_RECORD":
        if current is not None:
            raise ValueError("CRM_RECORD_ALREADY_EXISTS")
        required = {
            "occurred_at", "record_type", "display_label",
            "lifecycle_status", "owner_ref", "fields", "tags",
        }
        if set(p) != required:
            raise ValueError("CRM_RECORD_CREATE_PAYLOAD_INVALID")
        if p["record_type"] not in RECORD_TYPES:
            raise ValueError("CRM_RECORD_TYPE_INVALID")
        if p["lifecycle_status"] not in RECORD_STATUSES:
            raise ValueError("CRM_RECORD_STATUS_INVALID")
        if not str(p["display_label"]).strip():
            raise ValueError("CRM_RECORD_DISPLAY_LABEL_REQUIRED")
        _assert_no_secret_fields(p["fields"])
        return {
            "schema": "CRM_RECORD_NATIVE_V0",
            "record_id": mutation.entity_id,
            "record_type": p["record_type"],
            "display_label": str(p["display_label"]),
            "lifecycle_status": p["lifecycle_status"],
            "owner_ref": p["owner_ref"],
            "fields": dict(p["fields"]),
            "tags": sorted(set(p["tags"])),
            "created_at": occurred_at,
            "updated_at": occurred_at,
            "version": 1,
        }

    if current is None:
        raise ValueError("CRM_RECORD_NOT_FOUND")
    if current["lifecycle_status"] == "ARCHIVED":
        raise ValueError("CRM_ARCHIVED_RECORD_IMMUTABLE")

    state = dict(current)
    state["version"] = int(current["version"]) + 1
    state["updated_at"] = occurred_at

    if mutation.operation == "UPDATE_FIELDS":
        if set(p) != {"occurred_at", "fields"} or not p["fields"]:
            raise ValueError("CRM_UPDATE_FIELDS_PAYLOAD_INVALID")
        _assert_no_secret_fields(p["fields"])
        fields = dict(current["fields"])
        fields.update(dict(p["fields"]))
        state["fields"] = fields
    elif mutation.operation == "SET_OWNER":
        if set(p) != {"occurred_at", "owner_ref"}:
            raise ValueError("CRM_SET_OWNER_PAYLOAD_INVALID")
        state["owner_ref"] = p["owner_ref"]
    elif mutation.operation == "SET_RECORD_STATUS":
        if set(p) != {"occurred_at", "lifecycle_status"}:
            raise ValueError("CRM_SET_STATUS_PAYLOAD_INVALID")
        if p["lifecycle_status"] not in RECORD_STATUSES:
            raise ValueError("CRM_RECORD_STATUS_INVALID")
        if p["lifecycle_status"] == current["lifecycle_status"]:
            raise ValueError("CRM_RECORD_STATUS_NOOP")
        state["lifecycle_status"] = p["lifecycle_status"]
    elif mutation.operation == "ADD_RECORD_TAG":
        if set(p) != {"occurred_at", "tag"}:
            raise ValueError("CRM_TAG_PAYLOAD_INVALID")
        tag = str(p["tag"]).strip()
        if not tag:
            raise ValueError("CRM_TAG_REQUIRED")
        tags = set(current["tags"])
        if tag in tags:
            raise ValueError("CRM_TAG_ALREADY_PRESENT")
        tags.add(tag)
        state["tags"] = sorted(tags)
    elif mutation.operation == "REMOVE_RECORD_TAG":
        if set(p) != {"occurred_at", "tag"}:
            raise ValueError("CRM_TAG_PAYLOAD_INVALID")
        tag = str(p["tag"]).strip()
        tags = set(current["tags"])
        if tag not in tags:
            raise ValueError("CRM_TAG_NOT_PRESENT")
        tags.remove(tag)
        state["tags"] = sorted(tags)
    else:
        raise ValueError("CRM_RECORD_OPERATION_INVALID")
    return state


def _relationship_next(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> dict[str, Any]:
    p = mutation.payload
    occurred_at = str(p["occurred_at"])
    if mutation.operation == "CREATE_RELATIONSHIP":
        if current is not None:
            raise ValueError("CRM_RELATIONSHIP_ALREADY_EXISTS")
        required = {
            "occurred_at", "from_record_id", "to_record_id",
            "relation_type",
        }
        if set(p) != required:
            raise ValueError("CRM_RELATIONSHIP_CREATE_PAYLOAD_INVALID")
        if p["from_record_id"] == p["to_record_id"]:
            raise ValueError("CRM_RELATIONSHIP_SELF_LINK_FORBIDDEN")
        if not _record_exists(store, str(p["from_record_id"])):
            raise ValueError("CRM_RELATIONSHIP_FROM_RECORD_NOT_FOUND")
        if not _record_exists(store, str(p["to_record_id"])):
            raise ValueError("CRM_RELATIONSHIP_TO_RECORD_NOT_FOUND")
        if not str(p["relation_type"]).strip():
            raise ValueError("CRM_RELATIONSHIP_TYPE_REQUIRED")
        return {
            "schema": "CRM_RELATIONSHIP_NATIVE_V0",
            "relationship_id": mutation.entity_id,
            "from_record_id": str(p["from_record_id"]),
            "to_record_id": str(p["to_record_id"]),
            "relation_type": str(p["relation_type"]),
            "active": True,
            "created_at": occurred_at,
            "updated_at": occurred_at,
            "version": 1,
        }
    if current is None:
        raise ValueError("CRM_RELATIONSHIP_NOT_FOUND")
    if mutation.operation != "DEACTIVATE_RELATIONSHIP":
        raise ValueError("CRM_RELATIONSHIP_OPERATION_INVALID")
    if set(p) != {"occurred_at"}:
        raise ValueError("CRM_RELATIONSHIP_DEACTIVATE_PAYLOAD_INVALID")
    if current["active"] is False:
        raise ValueError("CRM_RELATIONSHIP_ALREADY_INACTIVE")
    state = dict(current)
    state["active"] = False
    state["updated_at"] = occurred_at
    state["version"] = int(current["version"]) + 1
    return state


def _interaction_next(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if mutation.operation != "APPEND_INTERACTION":
        raise ValueError("CRM_INTERACTION_OPERATION_INVALID")
    if current is not None:
        raise ValueError("CRM_INTERACTION_IMMUTABLE")
    p = mutation.payload
    required = {
        "occurred_at", "record_id", "interaction_type",
        "summary", "evidence_refs",
    }
    if set(p) != required:
        raise ValueError("CRM_INTERACTION_PAYLOAD_INVALID")
    if not _record_exists(store, str(p["record_id"])):
        raise ValueError("CRM_INTERACTION_RECORD_NOT_FOUND")
    if p["interaction_type"] not in INTERACTION_TYPES:
        raise ValueError("CRM_INTERACTION_TYPE_INVALID")
    if not str(p["summary"]).strip():
        raise ValueError("CRM_INTERACTION_SUMMARY_REQUIRED")
    if not p["evidence_refs"]:
        raise ValueError("CRM_INTERACTION_EVIDENCE_REQUIRED")
    return {
        "schema": "CRM_INTERACTION_NATIVE_V0",
        "interaction_id": mutation.entity_id,
        "record_id": str(p["record_id"]),
        "interaction_type": p["interaction_type"],
        "summary": str(p["summary"]),
        "occurred_at": p["occurred_at"],
        "evidence_refs": sorted(set(p["evidence_refs"])),
        "created_at": p["occurred_at"],
        "version": 1,
    }


def _followup_next(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> dict[str, Any]:
    p = mutation.payload
    occurred_at = str(p["occurred_at"])
    if mutation.operation == "CREATE_FOLLOWUP":
        if current is not None:
            raise ValueError("CRM_FOLLOWUP_ALREADY_EXISTS")
        required = {"occurred_at", "record_id", "task_ref", "due_at"}
        if set(p) != required:
            raise ValueError("CRM_FOLLOWUP_CREATE_PAYLOAD_INVALID")
        if not _record_exists(store, str(p["record_id"])):
            raise ValueError("CRM_FOLLOWUP_RECORD_NOT_FOUND")
        _require_time(str(p["due_at"]))
        if p["task_ref"] is not None and not _task_exists(
            store, str(p["task_ref"])
        ):
            raise ValueError("CRM_FOLLOWUP_TASK_NOT_FOUND")
        return {
            "schema": "CRM_FOLLOWUP_NATIVE_V0",
            "followup_id": mutation.entity_id,
            "record_id": str(p["record_id"]),
            "task_ref": p["task_ref"],
            "due_at": p["due_at"],
            "status": "OPEN",
            "created_at": occurred_at,
            "updated_at": occurred_at,
            "version": 1,
        }
    if current is None:
        raise ValueError("CRM_FOLLOWUP_NOT_FOUND")
    if current["status"] != "OPEN":
        raise ValueError("CRM_FOLLOWUP_TERMINAL")
    if set(p) != {"occurred_at"}:
        raise ValueError("CRM_FOLLOWUP_CLOSE_PAYLOAD_INVALID")
    if mutation.operation == "CLOSE_FOLLOWUP":
        new_status = "DONE"
    elif mutation.operation == "CANCEL_FOLLOWUP":
        new_status = "CANCELLED"
    else:
        raise ValueError("CRM_FOLLOWUP_OPERATION_INVALID")
    state = dict(current)
    state["status"] = new_status
    state["updated_at"] = occurred_at
    state["version"] = int(current["version"]) + 1
    return state


def _next_state(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    current: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if mutation.entity_kind == KIND_RECORD:
        return _record_next(mutation, current)
    if mutation.entity_kind == KIND_RELATIONSHIP:
        return _relationship_next(
            store=store, mutation=mutation, current=current
        )
    if mutation.entity_kind == KIND_INTERACTION:
        return _interaction_next(
            store=store, mutation=mutation, current=current
        )
    if mutation.entity_kind == KIND_FOLLOWUP:
        return _followup_next(
            store=store, mutation=mutation, current=current
        )
    raise ValueError("CRM_ENTITY_KIND_UNSUPPORTED")


def apply_crm_mutation_v0(
    *,
    store: NativeEntityStoreV0,
    mutation: NativeMutationV0,
    request: Mapping[str, Any],
    decision_record_id: str,
    decision_store_dir: Optional[Path],
    context_store_dir: Optional[Path],
) -> NativeMutationReceiptV0:
    if mutation.domain_id != DOMAIN_ID:
        raise ValueError("CRM_MUTATION_DOMAIN_INVALID")
    ok, reason, decision = verify_native_apply_authority_v0(
        mutation=mutation,
        request=request,
        decision_record_id=decision_record_id,
        decision_store_dir=decision_store_dir,
        context_store_dir=context_store_dir,
    )
    if not ok:
        raise ValueError(reason or "CRM_KX108_AUTHORITY_INVALID")
    current_hash = store.state_hash(
        DOMAIN_ID, mutation.entity_kind, mutation.entity_id
    )
    if current_hash != mutation.expected_prestate_hash:
        raise ValueError("CRM_PRESTATE_CHANGED")
    current = store.load_state(
        DOMAIN_ID, mutation.entity_kind, mutation.entity_id
    )
    after = _next_state(store=store, mutation=mutation, current=current)
    return store.commit(
        mutation=mutation,
        world_action_request_hash=request["request_hash"],
        kx108_decision_record_id=decision["decision_record_id"],
        kx108_decision_record_hash=decision["decision_record_hash"],
        after_state=after,
        created_at=str(mutation.payload["occurred_at"]),
    )


def crm_timeline_v0(
    store: NativeEntityStoreV0,
    record_id: str,
) -> list[dict[str, Any]]:
    if not _record_exists(store, record_id):
        raise ValueError("CRM_TIMELINE_RECORD_NOT_FOUND")
    events: list[dict[str, Any]] = []

    for receipt in store.receipts(DOMAIN_ID, KIND_RECORD, record_id):
        events.append({
            "occurred_at": receipt["created_at"],
            "kind": "RECORD_MUTATION",
            "entity_id": record_id,
            "operation": receipt["operation"],
            "receipt_id": receipt["receipt_id"],
        })

    domain_root = store.root / DOMAIN_ID
    for kind in (KIND_RELATIONSHIP, KIND_INTERACTION, KIND_FOLLOWUP):
        kind_root = domain_root / kind
        if not kind_root.exists():
            continue
        for entity_dir in sorted(kind_root.iterdir()):
            if not entity_dir.is_dir():
                continue
            state_path = entity_dir / "state.json"
            if not state_path.exists():
                continue
            import json
            state = json.loads(state_path.read_text(encoding="utf-8"))
            related = False
            if kind == KIND_RELATIONSHIP:
                related = (
                    state["from_record_id"] == record_id
                    or state["to_record_id"] == record_id
                )
            else:
                related = state["record_id"] == record_id
            if not related:
                continue
            for receipt in store.receipts(
                DOMAIN_ID, kind, entity_dir.name
            ):
                events.append({
                    "occurred_at": receipt["created_at"],
                    "kind": kind.upper(),
                    "entity_id": entity_dir.name,
                    "operation": receipt["operation"],
                    "receipt_id": receipt["receipt_id"],
                })
    return sorted(
        events,
        key=lambda item: (
            item["occurred_at"],
            item["kind"],
            item["entity_id"],
            item["receipt_id"],
        ),
    )
