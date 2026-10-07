"""Provider-neutral projections from canonical native TASKS/CRM state.

These projections are read-only transport payloads. They do not decide,
mutate native state, or authorize external synchronization.
"""
from __future__ import annotations

from typing import Any, Mapping

from .common_v0 import DECISION_AUTHORITY, canonical_hash


def project_task_for_external_sync_v0(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    if state.get("schema") != "TASK_NATIVE_V0":
        raise ValueError("TASK_SYNC_SOURCE_SCHEMA_INVALID")
    payload = {
        "task_id": state["task_id"],
        "title": state["title"],
        "description": state["description"],
        "status": state["status"],
        "priority": state["priority"],
        "assignee_ref": state["assignee_ref"],
        "due_at": state["due_at"],
        "dependency_ids": list(state["dependency_ids"]),
        "tags": list(state["tags"]),
        "version": state["version"],
    }
    return {
        "schema": "NATIVE_TASK_EXTERNAL_SYNC_PROJECTION_V0",
        "source_domain": "native_tasks",
        "source_entity_id": state["task_id"],
        "source_state_hash": canonical_hash(dict(state)),
        "payload": payload,
        "decision_authority": DECISION_AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }


def project_crm_record_for_external_sync_v0(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    if state.get("schema") != "CRM_RECORD_NATIVE_V0":
        raise ValueError("CRM_SYNC_SOURCE_SCHEMA_INVALID")
    payload = {
        "record_id": state["record_id"],
        "record_type": state["record_type"],
        "display_label": state["display_label"],
        "lifecycle_status": state["lifecycle_status"],
        "owner_ref": state["owner_ref"],
        "fields": dict(state["fields"]),
        "tags": list(state["tags"]),
        "version": state["version"],
    }
    return {
        "schema": "NATIVE_CRM_EXTERNAL_SYNC_PROJECTION_V0",
        "source_domain": "native_crm",
        "source_entity_id": state["record_id"],
        "source_state_hash": canonical_hash(dict(state)),
        "payload": payload,
        "decision_authority": DECISION_AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }
