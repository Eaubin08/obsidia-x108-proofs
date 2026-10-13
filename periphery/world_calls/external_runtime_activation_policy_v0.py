"""Explicit external-runtime activation policy V0.

Non-sovereign infrastructure policy. It cannot decide ALLOW/HOLD/BLOCK and
cannot execute anything. It only constrains whether an already verified
WORLD_ACTION_PRE KX108 ALLOW may proceed to a LIVE-capable sovereign ticket.

Default posture: disabled.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping

SCHEMA = "EXTERNAL_RUNTIME_ACTIVATION_POLICY_V0"
DECISION_AUTHORITY = "KX108_ONLY"

DEFAULT_ALLOWED_WORLD_CALL_CLASSES = (
    "READ_ONLY_WORLD_CALL",
    "REVERSIBLE_WORLD_CALL",
)
DEFAULT_ALLOWED_ACTION_RISK_CLASSES = (
    "ACTION_READ_ONLY",
    "ACTION_EXTERNAL_API",
)
DEFAULT_MAX_AUTONOMY_LEVEL = 4


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExternalRuntimeActivationPolicyV0:
    schema: str
    policy_id: str
    environment: str
    enabled: bool
    allowed_operations: tuple[tuple[str, str, str], ...]
    allowed_world_call_classes: tuple[str, ...]
    allowed_action_risk_classes: tuple[str, ...]
    max_autonomy_level: int
    created_at: str
    expires_at: str
    operator_approval_ref: str
    decision_authority: str
    is_execution_authority: bool
    policy_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_operations"] = [
            list(item) for item in self.allowed_operations
        ]
        data["allowed_world_call_classes"] = list(
            self.allowed_world_call_classes
        )
        data["allowed_action_risk_classes"] = list(
            self.allowed_action_risk_classes
        )
        return data


def _normalize_operations(
    operations: Iterable[Mapping[str, str] | tuple[str, str, str]],
) -> tuple[tuple[str, str, str], ...]:
    normalized: list[tuple[str, str, str]] = []
    for item in operations:
        if isinstance(item, Mapping):
            connector_id = str(item.get("connector_id", "")).strip()
            connector_action = str(item.get("connector_action", "")).strip()
            required_scope = str(item.get("required_scope", "")).strip()
        else:
            connector_id, connector_action, required_scope = (
                str(x).strip() for x in item
            )
        if not connector_id or not connector_action or not required_scope:
            raise ValueError("ACTIVATION_POLICY_OPERATION_INCOMPLETE")
        normalized.append(
            (connector_id, connector_action, required_scope)
        )
    return tuple(sorted(set(normalized)))


def _payload_for_hash(policy_like: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": policy_like["schema"],
        "policy_id": policy_like["policy_id"],
        "environment": policy_like["environment"],
        "enabled": bool(policy_like["enabled"]),
        "allowed_operations": [
            list(item) for item in policy_like["allowed_operations"]
        ],
        "allowed_world_call_classes": list(
            policy_like["allowed_world_call_classes"]
        ),
        "allowed_action_risk_classes": list(
            policy_like["allowed_action_risk_classes"]
        ),
        "max_autonomy_level": int(policy_like["max_autonomy_level"]),
        "created_at": policy_like["created_at"],
        "expires_at": policy_like["expires_at"],
        "operator_approval_ref": policy_like["operator_approval_ref"],
        "decision_authority": policy_like["decision_authority"],
        "is_execution_authority": bool(
            policy_like["is_execution_authority"]
        ),
    }


def build_activation_policy_v0(
    *,
    policy_id: str,
    environment: str,
    enabled: bool = False,
    allowed_operations: Iterable[
        Mapping[str, str] | tuple[str, str, str]
    ] = (),
    created_at: str,
    expires_at: str,
    operator_approval_ref: str,
    allowed_world_call_classes: Iterable[str] = (
        DEFAULT_ALLOWED_WORLD_CALL_CLASSES
    ),
    allowed_action_risk_classes: Iterable[str] = (
        DEFAULT_ALLOWED_ACTION_RISK_CLASSES
    ),
    max_autonomy_level: int = DEFAULT_MAX_AUTONOMY_LEVEL,
) -> ExternalRuntimeActivationPolicyV0:
    if not policy_id.strip():
        raise ValueError("ACTIVATION_POLICY_ID_REQUIRED")
    if not environment.strip():
        raise ValueError("ACTIVATION_POLICY_ENVIRONMENT_REQUIRED")
    if not operator_approval_ref.strip():
        raise ValueError("ACTIVATION_POLICY_OPERATOR_APPROVAL_REF_REQUIRED")
    if max_autonomy_level < 0 or max_autonomy_level > 4:
        raise ValueError("ACTIVATION_POLICY_MAX_AUTONOMY_UNSAFE")

    ops = _normalize_operations(allowed_operations)
    world_classes = tuple(sorted(set(allowed_world_call_classes)))
    risk_classes = tuple(sorted(set(allowed_action_risk_classes)))

    if any(
        item in world_classes
        for item in (
            "IRREVERSIBLE_WORLD_CALL",
            "CRITICAL_WORLD_CALL",
            "FORBIDDEN_WORLD_CALL",
        )
    ):
        raise ValueError("ACTIVATION_POLICY_UNSAFE_WORLD_CALL_CLASS")
    if any(
        item in risk_classes
        for item in (
            "ACTION_FINANCIAL",
            "ACTION_COMPLIANCE_BOUND",
            "ACTION_SENSITIVE",
            "ACTION_IRREVERSIBLE",
            "ACTION_FORBIDDEN",
        )
    ):
        raise ValueError("ACTIVATION_POLICY_UNSAFE_ACTION_RISK_CLASS")

    payload = {
        "schema": SCHEMA,
        "policy_id": policy_id.strip(),
        "environment": environment.strip(),
        "enabled": bool(enabled),
        "allowed_operations": ops,
        "allowed_world_call_classes": world_classes,
        "allowed_action_risk_classes": risk_classes,
        "max_autonomy_level": int(max_autonomy_level),
        "created_at": created_at,
        "expires_at": expires_at,
        "operator_approval_ref": operator_approval_ref.strip(),
        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
    }
    policy_hash = _canonical_hash(_payload_for_hash(payload))
    return ExternalRuntimeActivationPolicyV0(
        **payload,
        policy_hash=policy_hash,
    )


def verify_activation_policy_v0(
    policy: ExternalRuntimeActivationPolicyV0,
    *,
    now: str | None = None,
) -> tuple[bool, str | None]:
    if policy.schema != SCHEMA:
        return False, "ACTIVATION_POLICY_SCHEMA_INVALID"
    if policy.decision_authority != DECISION_AUTHORITY:
        return False, "ACTIVATION_POLICY_AUTHORITY_INVALID"
    if policy.is_execution_authority is not False:
        return False, "ACTIVATION_POLICY_CANNOT_BE_SOVEREIGN"
    if policy.max_autonomy_level < 0 or policy.max_autonomy_level > 4:
        return False, "ACTIVATION_POLICY_MAX_AUTONOMY_UNSAFE"

    expected = _canonical_hash(_payload_for_hash(policy.to_dict()))
    if policy.policy_hash != expected:
        return False, "ACTIVATION_POLICY_HASH_MISMATCH"

    try:
        created = datetime.datetime.fromisoformat(policy.created_at)
        expires = datetime.datetime.fromisoformat(policy.expires_at)
        observed = datetime.datetime.fromisoformat(
            now or datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
    except ValueError:
        return False, "ACTIVATION_POLICY_TIME_INVALID"

    if created.tzinfo is None or expires.tzinfo is None or observed.tzinfo is None:
        return False, "ACTIVATION_POLICY_TIME_MUST_BE_TIMEZONE_AWARE"
    if expires <= created:
        return False, "ACTIVATION_POLICY_EXPIRY_INVALID"
    if observed >= expires:
        return False, "ACTIVATION_POLICY_EXPIRED"

    if not policy.enabled:
        return False, "EXTERNAL_RUNTIME_ACTIVATION_DISABLED"

    if not policy.allowed_operations:
        return False, "ACTIVATION_POLICY_NO_ALLOWED_OPERATION"

    if any(
        item in policy.allowed_world_call_classes
        for item in (
            "IRREVERSIBLE_WORLD_CALL",
            "CRITICAL_WORLD_CALL",
            "FORBIDDEN_WORLD_CALL",
        )
    ):
        return False, "ACTIVATION_POLICY_UNSAFE_WORLD_CALL_CLASS"

    if any(
        item in policy.allowed_action_risk_classes
        for item in (
            "ACTION_FINANCIAL",
            "ACTION_COMPLIANCE_BOUND",
            "ACTION_SENSITIVE",
            "ACTION_IRREVERSIBLE",
            "ACTION_FORBIDDEN",
        )
    ):
        return False, "ACTIVATION_POLICY_UNSAFE_ACTION_RISK_CLASS"

    return True, None


def operation_allowed_v0(
    policy: ExternalRuntimeActivationPolicyV0,
    *,
    connector_id: str,
    connector_action: str,
    required_scope: str,
    world_call_class: str,
    action_risk_class: str,
    autonomy_level: int,
) -> tuple[bool, str | None]:
    ok, reason = verify_activation_policy_v0(policy)
    if not ok:
        return False, reason

    if (
        connector_id,
        connector_action,
        required_scope,
    ) not in policy.allowed_operations:
        return False, "ACTIVATION_POLICY_OPERATION_NOT_ALLOWED"
    if world_call_class not in policy.allowed_world_call_classes:
        return False, "ACTIVATION_POLICY_WORLD_CALL_CLASS_NOT_ALLOWED"
    if action_risk_class not in policy.allowed_action_risk_classes:
        return False, "ACTIVATION_POLICY_ACTION_RISK_CLASS_NOT_ALLOWED"
    if autonomy_level > policy.max_autonomy_level:
        return False, "ACTIVATION_POLICY_AUTONOMY_LEVEL_TOO_HIGH"
    return True, None
