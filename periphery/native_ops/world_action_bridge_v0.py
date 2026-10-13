"""Bridge native Obsidia state mutations to the canonical KX108 PRE rail V0."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_kx108_decision_store as DS  # noqa: E402
import obsidia_world_action_pre_execution_context_v0 as CTX  # noqa: E402

from .common_v0 import (
    DECISION_AUTHORITY,
    NativeMutationV0,
    canonical_hash,
)

_NATIVE_CONNECTORS = {
    "native_tasks": ("OBSIDIA_NATIVE_TASKS", "native:tasks:write"),
    "native_crm": ("OBSIDIA_NATIVE_CRM", "native:crm:write"),
}


def _request_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def build_native_world_action_request_v0(
    mutation: NativeMutationV0,
) -> dict[str, Any]:
    try:
        connector_id, scope = _NATIVE_CONNECTORS[mutation.domain_id]
    except KeyError as exc:
        raise ValueError(
            f"NATIVE_DOMAIN_UNSUPPORTED:{mutation.domain_id}"
        ) from exc

    connector_args = {
        "mutation_id": mutation.mutation_id,
        "mutation_hash": mutation.mutation_hash,
        "entity_kind": mutation.entity_kind,
        "entity_id": mutation.entity_id,
        "operation": mutation.operation,
        "payload": dict(mutation.payload),
        "expected_prestate_hash": mutation.expected_prestate_hash,
    }
    connector_call_hash = canonical_hash(
        {
            "connector_id": connector_id,
            "connector_action": mutation.operation,
            "connector_args": connector_args,
        }
    )
    proposal_hash = canonical_hash(
        {
            "schema": "NATIVE_MUTATION_PROPOSAL_V0",
            "mutation_hash": mutation.mutation_hash,
            "domain_id": mutation.domain_id,
            "entity_kind": mutation.entity_kind,
            "entity_id": mutation.entity_id,
            "operation": mutation.operation,
        }
    )
    idempotency_key = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
            "proposal_hash": proposal_hash,
            "connector_call_hash": connector_call_hash,
            "target_prestate_hash": mutation.expected_prestate_hash,
            "required_scope": scope,
        }
    )
    request = {
        "request_id": f"native:{mutation.mutation_id}",
        "proposal_id": f"native-proposal:{mutation.mutation_id}",
        "proposal_hash": proposal_hash,
        "domain_id": mutation.domain_id,
        "surface_id": (
            "TASKS" if mutation.domain_id == "native_tasks" else "CRM"
        ),
        "operation_id": mutation.operation,
        "effect_class": "INTERNAL_BOUNDED",
        "connector_id": connector_id,
        "connector_action": mutation.operation,
        "connector_args": connector_args,
        "connector_call_hash": connector_call_hash,
        "target_ref": (
            f"{mutation.domain_id}:{mutation.entity_kind}:{mutation.entity_id}"
        ),
        "target_prestate_hash": mutation.expected_prestate_hash,
        "required_scope": scope,
        "world_call_class": "REVERSIBLE_WORLD_CALL",
        "action_risk_class": "ACTION_PLAN",
        "autonomy_level": 3,
        "irreversible": False,
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "idempotency_key": idempotency_key,
        "decision_authority": DECISION_AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["request_hash"] = _request_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_REQUEST_V0",
            "request_id": request["request_id"],
            "proposal_id": request["proposal_id"],
            "proposal_hash": request["proposal_hash"],
            "domain_id": request["domain_id"],
            "surface_id": request["surface_id"],
            "operation_id": request["operation_id"],
            "effect_class": request["effect_class"],
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
            "connector_call_hash": request["connector_call_hash"],
            "target_ref": request["target_ref"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
            "world_call_class": request["world_call_class"],
            "action_risk_class": request["action_risk_class"],
            "autonomy_level": request["autonomy_level"],
            "irreversible": request["irreversible"],
            "retry_policy": request["retry_policy"],
            "idempotency_key": request["idempotency_key"],
            "decision_authority": request["decision_authority"],
        }
    )
    ok, reason = CTX.verify_world_action_request_mapping(request)
    if not ok:
        raise ValueError(f"NATIVE_WORLD_ACTION_REQUEST_INVALID:{reason}")
    return request


def build_native_human_approval_v0(
    request: Mapping[str, Any],
    *,
    approval_id: str,
    approved_by: str,
    approval_reference: str,
) -> dict[str, Any]:
    if not approval_id or not approved_by or not approval_reference:
        raise ValueError("NATIVE_HUMAN_APPROVAL_EXPLICIT_FIELDS_REQUIRED")
    if approved_by == "MACHINE":
        raise ValueError("NATIVE_HUMAN_APPROVAL_MACHINE_FORBIDDEN")
    approval = {
        "schema": "UNIVERSAL_WORLD_ACTION_HUMAN_APPROVAL_V0",
        "approval_id": approval_id,
        "approved_by": approved_by,
        "approval_reference": approval_reference,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "proposal_hash": request["proposal_hash"],
        "domain_id": request["domain_id"],
        "surface_id": request["surface_id"],
        "operation_id": request["operation_id"],
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_call_hash": request["connector_call_hash"],
        "target_ref": request["target_ref"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "idempotency_key": request["idempotency_key"],
        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
    }
    approval["approval_hash"] = canonical_hash(approval)
    ok, reason = CTX.verify_world_action_human_approval(approval, request)
    if not ok:
        raise ValueError(f"NATIVE_HUMAN_APPROVAL_INVALID:{reason}")
    return approval


def verify_native_apply_authority_v0(
    *,
    mutation: NativeMutationV0,
    request: Mapping[str, Any],
    decision_record_id: str,
    decision_store_dir: Optional[Path],
    context_store_dir: Optional[Path],
) -> tuple[bool, Optional[str], Optional[dict[str, Any]]]:
    expected_request = build_native_world_action_request_v0(mutation)
    if dict(request) != expected_request:
        return False, "NATIVE_REQUEST_MUTATION_BINDING_MISMATCH", None

    decision = DS.load_kx108_decision_record(
        decision_record_id,
        decision_store_dir,
    )
    ok, reason = DS.verify_kx108_decision_record(decision)
    if not ok:
        return False, f"NATIVE_KX108_DECISION_INVALID:{reason}", None
    if DS.decision_phase_of(decision) != DS.WORLD_ACTION_PRE_DECISION_PHASE:
        return False, "NATIVE_KX108_DECISION_PHASE_INVALID", None
    if decision.get("x108_gate") != "ALLOW":
        return False, "NATIVE_KX108_GATE_NOT_ALLOW", None
    if decision.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_KX108_AUTHORITY_INVALID", None
    if decision.get("world_action_request_hash") != request["request_hash"]:
        return False, "NATIVE_KX108_REQUEST_HASH_MISMATCH", None
    if decision.get("connector_call_hash") != request["connector_call_hash"]:
        return False, "NATIVE_KX108_CONNECTOR_CALL_HASH_MISMATCH", None
    if decision.get("source_domain") != mutation.domain_id:
        return False, "NATIVE_KX108_SOURCE_DOMAIN_MISMATCH", None
    if decision.get("action_id") != request["request_id"]:
        return False, "NATIVE_KX108_ACTION_ID_MISMATCH", None

    context = CTX.load_world_action_pre_execution_context(
        decision["world_action_pre_context_id"],
        context_store_dir,
    )
    ok, reason = CTX.verify_world_action_pre_execution_context(context)
    if not ok:
        return False, f"NATIVE_KX108_CONTEXT_INVALID:{reason}", None
    if context.get("world_action_request_hash") != request["request_hash"]:
        return False, "NATIVE_CONTEXT_REQUEST_HASH_MISMATCH", None
    if context.get("target_prestate_hash") != mutation.expected_prestate_hash:
        return False, "NATIVE_CONTEXT_PRESTATE_HASH_MISMATCH", None
    return True, None, decision
