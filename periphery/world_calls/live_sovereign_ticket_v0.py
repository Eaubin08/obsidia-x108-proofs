"""LIVE-capable SovereignTicket V0 for the external world rail.

This module issues no network call. A ticket can only be produced after:
- immutable WORLD_ACTION_PRE context verification
- immutable KX108 decision-record verification
- decision_phase == WORLD_ACTION_PRE_EXECUTION
- x108_gate == ALLOW
- exact activation-policy allow-list match

The existing V4 dry-run SovereignTicket remains untouched.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_kx108_decision_store as _DS  # noqa: E402
import obsidia_world_action_pre_execution_context_v0 as _CTX  # noqa: E402

from .external_runtime_activation_policy_v0 import (  # noqa: E402
    DECISION_AUTHORITY,
    ExternalRuntimeActivationPolicyV0,
    operation_allowed_v0,
)

SCHEMA = "LIVE_SOVEREIGN_TICKET_V0"
MAX_TTL_SECONDS = 300


def _hash(value: Any) -> str:
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
class LiveSovereignTicketV0:
    schema: str
    ticket_id: str
    action_id: str
    source_domain: str
    world_action_request_hash: str
    connector_id: str
    connector_action: str
    connector_call_hash: str
    target_ref: str
    target_prestate_hash: str
    human_approval_hash: str
    required_scope: str
    world_call_class: str
    action_risk_class: str
    autonomy_level: int
    idempotency_key: str
    kx108_decision_record_id: str
    kx108_decision_record_hash: str
    activation_policy_id: str
    activation_policy_hash: str
    issued_at: str
    expires_at: str
    x108_gate: str
    decision_authority: str
    dry_run_only: bool
    live_egress_preflight_capable: bool
    executor_bound: bool
    ticket_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LiveSovereignTicketError(Exception):
    pass


def _payload_for_hash(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "schema",
            "ticket_id",
            "action_id",
            "source_domain",
            "world_action_request_hash",
            "connector_id",
            "connector_action",
            "connector_call_hash",
            "target_ref",
            "target_prestate_hash",
            "human_approval_hash",
            "required_scope",
            "world_call_class",
            "action_risk_class",
            "autonomy_level",
            "idempotency_key",
            "kx108_decision_record_id",
            "kx108_decision_record_hash",
            "activation_policy_id",
            "activation_policy_hash",
            "issued_at",
            "expires_at",
            "x108_gate",
            "decision_authority",
            "dry_run_only",
            "live_egress_preflight_capable",
            "executor_bound",
        )
    }


def verify_live_sovereign_ticket_v0(
    ticket: LiveSovereignTicketV0,
    *,
    now: str | None = None,
) -> tuple[bool, Optional[str]]:
    if not isinstance(ticket, LiveSovereignTicketV0):
        return False, "LIVE_TICKET_TYPE_INVALID"
    if ticket.schema != SCHEMA:
        return False, "LIVE_TICKET_SCHEMA_INVALID"
    if ticket.decision_authority != DECISION_AUTHORITY:
        return False, "LIVE_TICKET_AUTHORITY_INVALID"
    if ticket.x108_gate != "ALLOW":
        return False, "LIVE_TICKET_KX108_GATE_NOT_ALLOW"
    if ticket.dry_run_only is not False:
        return False, "LIVE_TICKET_DRY_RUN_FLAG_INVALID"
    if ticket.live_egress_preflight_capable is not True:
        return False, "LIVE_TICKET_PREFLIGHT_CAPABILITY_INVALID"
    if ticket.executor_bound is not False:
        return False, "LIVE_TICKET_EXECUTOR_MUST_NOT_BE_BOUND_IN_V0"
    expected = _hash(_payload_for_hash(ticket.to_dict()))
    if ticket.ticket_hash != expected:
        return False, "LIVE_TICKET_HASH_MISMATCH"
    try:
        expires = datetime.datetime.fromisoformat(ticket.expires_at)
        observed = datetime.datetime.fromisoformat(
            now or datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
    except ValueError:
        return False, "LIVE_TICKET_TIME_INVALID"
    if expires.tzinfo is None or observed.tzinfo is None:
        return False, "LIVE_TICKET_TIME_MUST_BE_TIMEZONE_AWARE"
    if observed >= expires:
        return False, "LIVE_TICKET_EXPIRED"
    return True, None


def issue_live_sovereign_ticket_v0(
    *,
    decision_record_id: str,
    activation_policy: ExternalRuntimeActivationPolicyV0,
    decision_store_dir: Optional[Path] = None,
    context_store_dir: Optional[Path] = None,
    ttl_seconds: int = 120,
    now: str | None = None,
) -> LiveSovereignTicketV0:
    if ttl_seconds <= 0 or ttl_seconds > MAX_TTL_SECONDS:
        raise LiveSovereignTicketError("LIVE_TICKET_TTL_OUT_OF_BOUNDS")

    decision = _DS.load_kx108_decision_record(
        decision_record_id,
        decision_store_dir,
    )
    ok, reason = _DS.verify_kx108_decision_record(decision)
    if not ok:
        raise LiveSovereignTicketError(
            f"LIVE_TICKET_KX108_DECISION_INVALID:{reason}"
        )
    if _DS.decision_phase_of(decision) != (
        _DS.WORLD_ACTION_PRE_DECISION_PHASE
    ):
        raise LiveSovereignTicketError(
            "LIVE_TICKET_DECISION_NOT_WORLD_ACTION_PRE"
        )
    if decision.get("x108_gate") != "ALLOW":
        raise LiveSovereignTicketError("LIVE_TICKET_KX108_GATE_NOT_ALLOW")

    context_id = decision.get("world_action_pre_context_id")
    context = _CTX.load_world_action_pre_execution_context(
        context_id,
        context_store_dir,
    )
    ok, reason = _CTX.verify_world_action_pre_execution_context(context)
    if not ok:
        raise LiveSovereignTicketError(
            f"LIVE_TICKET_WORLD_ACTION_CONTEXT_INVALID:{reason}"
        )

    exact_pairs = {
        "context_record_hash": "world_action_pre_context_record_hash",
        "world_action_request_hash": "world_action_request_hash",
        "connector_call_hash": "connector_call_hash",
        "human_approval_hash": "human_approval_hash",
        "target_prestate_hash": "target_prestate_hash",
        "required_scope": "required_scope",
        "idempotency_key": "idempotency_key",
        "source_domain": "source_domain",
        "action_id": "action_id",
    }
    for context_field, decision_field in exact_pairs.items():
        if context.get(context_field) != decision.get(decision_field):
            raise LiveSovereignTicketError(
                "LIVE_TICKET_PRE_BINDING_MISMATCH:"
                f"{context_field}"
            )

    allowed, reason = operation_allowed_v0(
        activation_policy,
        connector_id=context["connector_id"],
        connector_action=context["connector_action"],
        required_scope=context["required_scope"],
        world_call_class=context["world_call_class"],
        action_risk_class=context["action_risk_class"],
        autonomy_level=context["autonomy_level"],
    )
    if not allowed:
        raise LiveSovereignTicketError(
            f"LIVE_TICKET_ACTIVATION_POLICY_BLOCK:{reason}"
        )

    observed = datetime.datetime.fromisoformat(
        now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    if observed.tzinfo is None:
        raise LiveSovereignTicketError(
            "LIVE_TICKET_TIME_MUST_BE_TIMEZONE_AWARE"
        )
    issued_at = observed.isoformat()
    expires_at = (
        observed + datetime.timedelta(seconds=ttl_seconds)
    ).isoformat()

    seed = {
        "schema": SCHEMA,
        "action_id": context["action_id"],
        "request_hash": context["world_action_request_hash"],
        "decision_record_hash": decision["decision_record_hash"],
        "activation_policy_hash": activation_policy.policy_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }
    ticket_id = f"svlive-{_hash(seed)[:32]}"

    payload = {
        "schema": SCHEMA,
        "ticket_id": ticket_id,
        "action_id": context["action_id"],
        "source_domain": context["source_domain"],
        "world_action_request_hash": context[
            "world_action_request_hash"
        ],
        "connector_id": context["connector_id"],
        "connector_action": context["connector_action"],
        "connector_call_hash": context["connector_call_hash"],
        "target_ref": context["target_ref"],
        "target_prestate_hash": context["target_prestate_hash"],
        "human_approval_hash": context["human_approval_hash"],
        "required_scope": context["required_scope"],
        "world_call_class": context["world_call_class"],
        "action_risk_class": context["action_risk_class"],
        "autonomy_level": context["autonomy_level"],
        "idempotency_key": context["idempotency_key"],
        "kx108_decision_record_id": decision[
            "decision_record_id"
        ],
        "kx108_decision_record_hash": decision[
            "decision_record_hash"
        ],
        "activation_policy_id": activation_policy.policy_id,
        "activation_policy_hash": activation_policy.policy_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "x108_gate": decision["x108_gate"],
        "decision_authority": DECISION_AUTHORITY,
        "dry_run_only": False,
        "live_egress_preflight_capable": True,
        "executor_bound": False,
    }
    payload["ticket_hash"] = _hash(_payload_for_hash(payload))
    ticket = LiveSovereignTicketV0(**payload)
    valid, reason = verify_live_sovereign_ticket_v0(
        ticket,
        now=issued_at,
    )
    if not valid:
        raise LiveSovereignTicketError(
            f"LIVE_TICKET_SELF_VERIFY_FAILED:{reason}"
        )
    return ticket
