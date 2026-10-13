"""Canonical WORLD_ACTION_PRE_EXECUTION context V0.

Freezes one exact external-world action request and its exact human approval
before KX108 is invoked. This module grants no authority and performs no
external action.

The business domain remains in source_domain. KX108 evaluates only structural
facts translated into the universal world_action domain.

decision_authority = KX108_ONLY
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"
DECISION_PHASE = "WORLD_ACTION_PRE_EXECUTION"

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT_EXISTING_IDENTICAL = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_CONTEXT_ID = "INVALID_CONTEXT_ID"

WORLD_ACTION_PRE_CONTEXT_DIR = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Obsidia"
    / "world_action_pre_execution_contexts"
)

_CONTEXT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

_REQUEST_REQUIRED_FIELDS = (
    "request_id",
    "request_hash",
    "proposal_id",
    "proposal_hash",
    "domain_id",
    "surface_id",
    "operation_id",
    "effect_class",
    "connector_id",
    "connector_action",
    "connector_args",
    "connector_call_hash",
    "target_ref",
    "target_prestate_hash",
    "required_scope",
    "world_call_class",
    "action_risk_class",
    "autonomy_level",
    "irreversible",
    "retry_policy",
    "idempotency_key",
    "decision_authority",
)

_APPROVAL_REQUIRED_FIELDS = (
    "schema",
    "approval_id",
    "approved_by",
    "approval_reference",
    "request_id",
    "request_hash",
    "proposal_hash",
    "domain_id",
    "surface_id",
    "operation_id",
    "connector_id",
    "connector_action",
    "connector_call_hash",
    "target_ref",
    "target_prestate_hash",
    "required_scope",
    "idempotency_key",
    "decision_authority",
    "is_execution_authority",
    "approval_hash",
)

_SECRET_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "private_key",
    "access_key",
    "credential",
)


_CONTEXT_BOUND_FIELDS = (
    "context_schema_version",
    "context_id",
    "created_at",
    "decision_phase",
    "source_domain",
    "action_id",
    "proposal_id",
    "proposal_hash",
    "world_action_request_hash",
    "connector_id",
    "connector_action",
    "connector_call_hash",
    "target_ref",
    "target_prestate_hash",
    "human_approval_id",
    "human_approval_hash",
    "required_scope",
    "world_call_class",
    "action_risk_class",
    "autonomy_level",
    "irreversible",
    "retry_policy",
    "idempotency_key",
    "unknowns",
    "contradictions",
    "risk_flags",
    "evidence_refs",
    "runtime_allowed_now",
    "emits_act",
    "memory_write",
    "kernel_mutation",
    "decision_authority",
)


class WorldActionPreContextError(Exception):
    pass


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _assert_no_secret_fields(value: Any, path: str = "connector_args") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in _SECRET_KEY_FRAGMENTS):
                raise WorldActionPreContextError(
                    f"SECRET_FIELD_FORBIDDEN_IN_WORLD_ACTION:{path}.{key}"
                )
            _assert_no_secret_fields(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_no_secret_fields(child, f"{path}[{index}]")


def _expected_connector_call_hash(request: Mapping[str, Any]) -> str:
    return _sha256_json({
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_args": dict(request["connector_args"]),
    })


def _expected_idempotency_key(request: Mapping[str, Any]) -> str:
    return _sha256_json({
        "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
        "proposal_hash": request["proposal_hash"],
        "connector_call_hash": request["connector_call_hash"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
    })


def _expected_request_hash(request: Mapping[str, Any]) -> str:
    return _sha256_json({
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
        "connector_args": dict(request["connector_args"]),
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
    })


def verify_world_action_request_mapping(
    request: Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if request is None:
        return False, "WORLD_ACTION_REQUEST_MISSING"
    for field in _REQUEST_REQUIRED_FIELDS:
        if field not in request:
            return False, f"WORLD_ACTION_REQUEST_FIELD_MISSING:{field}"
    if request.get("decision_authority") != DECISION_AUTHORITY:
        return False, "WORLD_ACTION_REQUEST_AUTHORITY_INVALID"
    if request.get("allowed_to_decide") not in (None, False):
        return False, "WORLD_ACTION_REQUEST_ALLOWED_TO_DECIDE_INVALID"
    if request.get("allowed_to_act") not in (None, False):
        return False, "WORLD_ACTION_REQUEST_ALLOWED_TO_ACT_INVALID"
    if request.get("emits_act") not in (None, False):
        return False, "WORLD_ACTION_REQUEST_EMITS_ACT_INVALID"
    for field in (
        "request_hash",
        "proposal_hash",
        "connector_call_hash",
        "target_prestate_hash",
        "idempotency_key",
    ):
        value = request.get(field)
        if not isinstance(value, str) or len(value) != 64:
            return False, f"WORLD_ACTION_REQUEST_HASH_INVALID:{field}"
    if not isinstance(request.get("autonomy_level"), int):
        return False, "WORLD_ACTION_REQUEST_AUTONOMY_LEVEL_INVALID"
    if request.get("autonomy_level") not in (3, 4, 5):
        return False, "WORLD_ACTION_REQUEST_AUTONOMY_LEVEL_UNSUPPORTED"
    if not isinstance(request.get("connector_args"), Mapping):
        return False, "WORLD_ACTION_REQUEST_CONNECTOR_ARGS_INVALID"
    try:
        _assert_no_secret_fields(request["connector_args"])
    except WorldActionPreContextError as exc:
        return False, str(exc)
    if request["connector_call_hash"] != _expected_connector_call_hash(request):
        return False, "WORLD_ACTION_REQUEST_CONNECTOR_CALL_HASH_MISMATCH"
    if request["idempotency_key"] != _expected_idempotency_key(request):
        return False, "WORLD_ACTION_REQUEST_IDEMPOTENCY_KEY_MISMATCH"
    if request["request_hash"] != _expected_request_hash(request):
        return False, "WORLD_ACTION_REQUEST_HASH_MISMATCH"
    return True, None


def verify_world_action_human_approval(
    approval: Mapping[str, Any] | None,
    request: Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    if approval is None:
        return False, "WORLD_ACTION_HUMAN_APPROVAL_MISSING"
    for field in _APPROVAL_REQUIRED_FIELDS:
        if field not in approval:
            return False, f"WORLD_ACTION_HUMAN_APPROVAL_FIELD_MISSING:{field}"
    if approval.get("schema") != "UNIVERSAL_WORLD_ACTION_HUMAN_APPROVAL_V0":
        return False, "WORLD_ACTION_HUMAN_APPROVAL_SCHEMA_INVALID"
    if approval.get("decision_authority") != DECISION_AUTHORITY:
        return False, "WORLD_ACTION_HUMAN_APPROVAL_AUTHORITY_INVALID"
    if approval.get("is_execution_authority") is not False:
        return False, "WORLD_ACTION_HUMAN_APPROVAL_CANNOT_BE_SOVEREIGN"

    expected_pairs = {
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
    }
    for field, expected in expected_pairs.items():
        if approval.get(field) != expected:
            return False, (
                f"WORLD_ACTION_HUMAN_APPROVAL_{field.upper()}_MISMATCH"
            )

    candidate = dict(approval)
    stored = candidate.pop("approval_hash", None)
    if not isinstance(stored, str) or len(stored) != 64:
        return False, "WORLD_ACTION_HUMAN_APPROVAL_HASH_INVALID"
    if _sha256_json(candidate) != stored:
        return False, "WORLD_ACTION_HUMAN_APPROVAL_HASH_MISMATCH"
    return True, None


def compute_world_action_pre_context_hash(record: Mapping[str, Any]) -> str:
    return _sha256_json(
        {field: record.get(field) for field in _CONTEXT_BOUND_FIELDS}
    )


def _compute_context_identity(record: Mapping[str, Any]) -> str:
    digest = compute_world_action_pre_context_hash(record)
    return f"wapre-{digest[:32]}"


def _context_path(
    context_id: str | None,
    store_dir: Optional[Path] = None,
) -> Path:
    if not context_id or not _CONTEXT_ID_RE.match(context_id):
        raise ValueError("INVALID_CONTEXT_ID")
    return (store_dir or WORLD_ACTION_PRE_CONTEXT_DIR) / f"{context_id}.json"


def create_world_action_pre_execution_context(
    *,
    request: Mapping[str, Any],
    human_approval: Mapping[str, Any],
    evidence_refs: list[str],
    unknowns: Optional[list[str]] = None,
    contradictions: Optional[list[str]] = None,
    risk_flags: Optional[list[str]] = None,
) -> dict:
    ok, reason = verify_world_action_request_mapping(request)
    if not ok:
        raise WorldActionPreContextError(reason or "WORLD_ACTION_REQUEST_INVALID")

    ok, reason = verify_world_action_human_approval(
        human_approval,
        request,
    )
    if not ok:
        raise WorldActionPreContextError(
            reason or "WORLD_ACTION_HUMAN_APPROVAL_INVALID"
        )

    if not evidence_refs:
        raise WorldActionPreContextError(
            "WORLD_ACTION_PRE_EVIDENCE_REFS_REQUIRED"
        )

    record = {
        "context_schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "decision_phase": DECISION_PHASE,
        "source_domain": str(request["domain_id"]),
        "action_id": str(request["request_id"]),
        "proposal_id": str(request["proposal_id"]),
        "proposal_hash": str(request["proposal_hash"]),
        "world_action_request_hash": str(request["request_hash"]),
        "connector_id": str(request["connector_id"]),
        "connector_action": str(request["connector_action"]),
        "connector_call_hash": str(request["connector_call_hash"]),
        "target_ref": str(request["target_ref"]),
        "target_prestate_hash": str(request["target_prestate_hash"]),
        "human_approval_id": str(human_approval["approval_id"]),
        "human_approval_hash": str(human_approval["approval_hash"]),
        "required_scope": str(request["required_scope"]),
        "world_call_class": str(request["world_call_class"]),
        "action_risk_class": str(request["action_risk_class"]),
        "autonomy_level": int(request["autonomy_level"]),
        "irreversible": bool(request["irreversible"]),
        "retry_policy": str(request["retry_policy"]),
        "idempotency_key": str(request["idempotency_key"]),
        "unknowns": sorted(set(unknowns or [])),
        "contradictions": sorted(set(contradictions or [])),
        "risk_flags": sorted(set(risk_flags or [])),
        "evidence_refs": sorted(set(evidence_refs)),
        "runtime_allowed_now": False,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    record["context_id"] = _compute_context_identity(record)
    record["context_record_hash"] = compute_world_action_pre_context_hash(record)
    return record


def store_world_action_pre_execution_context(
    record: Mapping[str, Any],
    store_dir: Optional[Path] = None,
) -> dict:
    context_id = record.get("context_id")
    try:
        path = _context_path(context_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_CONTEXT_ID, "context_id": context_id}

    payload = json.dumps(dict(record), ensure_ascii=False, indent=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (
        f".{path.name}.{os.getpid()}."
        f"{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    )
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return {"status": STATUS_STORED, "context_id": context_id}
    except FileExistsError:
        if path.read_text(encoding="utf-8") == payload:
            return {
                "status": STATUS_IDEMPOTENT_EXISTING_IDENTICAL,
                "context_id": context_id,
            }
        return {
            "status": STATUS_IMMUTABILITY_VIOLATION,
            "context_id": context_id,
        }
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_world_action_pre_execution_context(
    context_id: str,
    store_dir: Optional[Path] = None,
) -> Optional[dict]:
    try:
        path = _context_path(context_id, store_dir)
    except ValueError:
        return None
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_world_action_pre_execution_context(
    record: Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if record is None:
        return False, "WORLD_ACTION_PRE_CONTEXT_MISSING"
    if record.get("context_schema_version") != SCHEMA_VERSION:
        return False, "WORLD_ACTION_PRE_CONTEXT_SCHEMA_UNSUPPORTED"
    for field in _CONTEXT_BOUND_FIELDS:
        if field not in record:
            return False, f"WORLD_ACTION_PRE_CONTEXT_FIELD_MISSING:{field}"
    if record.get("decision_phase") != DECISION_PHASE:
        return False, "WORLD_ACTION_PRE_CONTEXT_PHASE_INVALID"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "WORLD_ACTION_PRE_CONTEXT_AUTHORITY_INVALID"
    for flag in (
        "runtime_allowed_now",
        "emits_act",
        "memory_write",
        "kernel_mutation",
    ):
        if record.get(flag) is not False:
            return False, f"WORLD_ACTION_PRE_CONTEXT_INVARIANT_VIOLATED:{flag}"
    expected = compute_world_action_pre_context_hash(record)
    if record.get("context_record_hash") != expected:
        return False, "WORLD_ACTION_PRE_CONTEXT_HASH_MISMATCH"
    return True, None


def decision_binding_context(record: Mapping[str, Any]) -> dict:
    ok, reason = verify_world_action_pre_execution_context(record)
    if not ok:
        raise WorldActionPreContextError(
            reason or "WORLD_ACTION_PRE_CONTEXT_INVALID"
        )
    return {
        "world_action_pre_context_id": record["context_id"],
        "world_action_pre_context_record_hash": record["context_record_hash"],
        "world_action_request_hash": record["world_action_request_hash"],
        "connector_call_hash": record["connector_call_hash"],
        "human_approval_hash": record["human_approval_hash"],
        "target_prestate_hash": record["target_prestate_hash"],
        "required_scope": record["required_scope"],
        "idempotency_key": record["idempotency_key"],
        "source_domain": record["source_domain"],
        "action_id": record["action_id"],
    }
