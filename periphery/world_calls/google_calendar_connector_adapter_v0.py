"""Google Calendar real-provider adapter contract V0.

This is a peripheral connector adapter for one tightly bounded real pilot:
CREATE_EVENT on the authenticated user's primary calendar.

Architecture:
- Obsidia/KX108 produces an exact LIVE ticket.
- This adapter revalidates the LIVE Gateway and emits one exact invocation
  envelope for the external Google Calendar transport.
- The transport is outside the kernel and outside this module.
- Provider result is ingested back into an immutable real-provider receipt.

No credentials are stored here. No network library is imported here.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

from .external_runtime_activation_policy_v0 import (
    DECISION_AUTHORITY,
    ExternalRuntimeActivationPolicyV0,
)
from .live_sovereign_ticket_v0 import LiveSovereignTicketV0
from .obsidia_live_gateway_v0 import ObsidiaLiveGatewayV0

INVOCATION_SCHEMA = "GOOGLE_CALENDAR_INVOCATION_ENVELOPE_V0"
REAL_RECEIPT_SCHEMA = "GOOGLE_CALENDAR_REAL_PROVIDER_RECEIPT_V0"

CONNECTOR_ID = "GOOGLE_CALENDAR"
CONNECTOR_ACTION_CREATE = "CREATE_EVENT"
REQUIRED_SCOPE_CREATE = "calendar:event:create:pilot"

PILOT_TITLE_PREFIX = "[OBSIDIA PILOT]"
MAX_EVENT_DURATION_MINUTES = 30


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


def canonical_google_calendar_call_hash(
    args: Mapping[str, Any],
) -> str:
    return _hash(
        {
            "connector_id": CONNECTOR_ID,
            "connector_action": CONNECTOR_ACTION_CREATE,
            "connector_args": dict(args),
        }
    )


def _parse_time(value: str) -> datetime.datetime:
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("GOOGLE_CALENDAR_TIME_MUST_BE_TIMEZONE_AWARE")
    return parsed


def validate_pilot_create_args_v0(
    args: Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    required = {
        "calendar_id",
        "title",
        "attendees",
        "start_time",
        "end_time",
        "timezone_str",
        "description",
        "visibility",
        "transparency",
        "add_google_meet",
        "self_attendance",
        "reminders",
    }
    if set(args) != required:
        return False, "GOOGLE_CALENDAR_ARGS_SHAPE_INVALID"
    if args["calendar_id"] != "primary":
        return False, "GOOGLE_CALENDAR_PILOT_PRIMARY_ONLY"
    if not str(args["title"]).startswith(PILOT_TITLE_PREFIX):
        return False, "GOOGLE_CALENDAR_PILOT_TITLE_PREFIX_REQUIRED"
    if args["attendees"] != []:
        return False, "GOOGLE_CALENDAR_PILOT_ATTENDEES_FORBIDDEN"
    if args["visibility"] != "private":
        return False, "GOOGLE_CALENDAR_PILOT_VISIBILITY_MUST_BE_PRIVATE"
    if args["transparency"] != "transparent":
        return False, "GOOGLE_CALENDAR_PILOT_MUST_BE_TRANSPARENT"
    if args["add_google_meet"] is not False:
        return False, "GOOGLE_CALENDAR_PILOT_MEET_FORBIDDEN"
    if args["self_attendance"] != "omit":
        return False, "GOOGLE_CALENDAR_PILOT_SELF_ATTENDANCE_MUST_BE_OMIT"
    if args["reminders"] != {"use_default": False, "overrides": []}:
        return False, "GOOGLE_CALENDAR_PILOT_REMINDERS_MUST_BE_DISABLED"

    try:
        start = _parse_time(str(args["start_time"]))
        end = _parse_time(str(args["end_time"]))
    except ValueError as exc:
        return False, str(exc)
    if end <= start:
        return False, "GOOGLE_CALENDAR_PILOT_TIME_RANGE_INVALID"
    duration = (end - start).total_seconds() / 60.0
    if duration > MAX_EVENT_DURATION_MINUTES:
        return False, "GOOGLE_CALENDAR_PILOT_DURATION_TOO_LONG"
    if str(args["timezone_str"]) != "Europe/Paris":
        return False, "GOOGLE_CALENDAR_PILOT_TIMEZONE_INVALID"
    return True, None


@dataclass(frozen=True)
class GoogleCalendarInvocationEnvelopeV0:
    schema: str
    invocation_id: str
    action_id: str
    sovereign_ticket_id: str
    sovereign_ticket_hash: str
    activation_policy_hash: str
    world_action_request_hash: str
    connector_call_hash: str
    target_ref: str
    target_prestate_hash: str
    required_scope: str
    idempotency_key: str
    connector_id: str
    connector_action: str
    connector_args: Mapping[str, Any]
    issued_at: str
    decision_authority: str
    external_invocation_ready: bool
    network_call_performed: bool
    invocation_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GoogleCalendarRealProviderReceiptV0:
    schema: str
    receipt_id: str
    invocation_id: str
    invocation_hash: str
    action_id: str
    sovereign_ticket_hash: str
    world_action_request_hash: str
    connector_call_hash: str
    idempotency_key: str
    provider: str
    provider_event_id_sha256: str
    provider_status: str
    readback_verified: bool
    cleanup_status: str
    active_event_left: bool
    observed_at: str
    real_external_effect: bool
    obsidia_governed_invocation: bool
    decision_authority: str
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _invocation_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "schema",
            "invocation_id",
            "action_id",
            "sovereign_ticket_id",
            "sovereign_ticket_hash",
            "activation_policy_hash",
            "world_action_request_hash",
            "connector_call_hash",
            "target_ref",
            "target_prestate_hash",
            "required_scope",
            "idempotency_key",
            "connector_id",
            "connector_action",
            "connector_args",
            "issued_at",
            "decision_authority",
            "external_invocation_ready",
            "network_call_performed",
        )
    }


def build_google_calendar_invocation_v0(
    *,
    ticket: LiveSovereignTicketV0,
    activation_policy: ExternalRuntimeActivationPolicyV0,
    connector_args: Mapping[str, Any],
    observed_target_ref: str,
    observed_target_prestate_hash: str,
    now: str | None = None,
) -> GoogleCalendarInvocationEnvelopeV0:
    ok, reason = validate_pilot_create_args_v0(connector_args)
    if not ok:
        raise ValueError(reason)

    if ticket.connector_id != CONNECTOR_ID:
        raise ValueError("GOOGLE_CALENDAR_TICKET_CONNECTOR_ID_MISMATCH")
    if ticket.connector_action != CONNECTOR_ACTION_CREATE:
        raise ValueError("GOOGLE_CALENDAR_TICKET_ACTION_MISMATCH")
    if ticket.required_scope != REQUIRED_SCOPE_CREATE:
        raise ValueError("GOOGLE_CALENDAR_TICKET_SCOPE_MISMATCH")

    call_hash = canonical_google_calendar_call_hash(connector_args)
    gateway = ObsidiaLiveGatewayV0().check(
        ticket=ticket,
        activation_policy=activation_policy,
        observed_connector_id=CONNECTOR_ID,
        observed_connector_action=CONNECTOR_ACTION_CREATE,
        observed_connector_call_hash=call_hash,
        observed_target_ref=observed_target_ref,
        observed_target_prestate_hash=observed_target_prestate_hash,
        observed_required_scope=REQUIRED_SCOPE_CREATE,
        observed_idempotency_key=ticket.idempotency_key,
        now=now,
    )
    if gateway.gate_result != "LIVE_PREFLIGHT_READY":
        raise ValueError(f"GOOGLE_CALENDAR_GATEWAY_BLOCK:{gateway.reason}")

    observed = datetime.datetime.fromisoformat(
        now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    if observed.tzinfo is None:
        raise ValueError("GOOGLE_CALENDAR_INVOCATION_TIME_INVALID")

    seed = {
        "ticket_hash": ticket.ticket_hash,
        "call_hash": call_hash,
        "idempotency_key": ticket.idempotency_key,
        "issued_at": observed.isoformat(),
    }
    invocation_id = f"gcal-{_hash(seed)[:32]}"
    payload = {
        "schema": INVOCATION_SCHEMA,
        "invocation_id": invocation_id,
        "action_id": ticket.action_id,
        "sovereign_ticket_id": ticket.ticket_id,
        "sovereign_ticket_hash": ticket.ticket_hash,
        "activation_policy_hash": ticket.activation_policy_hash,
        "world_action_request_hash": ticket.world_action_request_hash,
        "connector_call_hash": call_hash,
        "target_ref": ticket.target_ref,
        "target_prestate_hash": ticket.target_prestate_hash,
        "required_scope": ticket.required_scope,
        "idempotency_key": ticket.idempotency_key,
        "connector_id": CONNECTOR_ID,
        "connector_action": CONNECTOR_ACTION_CREATE,
        "connector_args": dict(connector_args),
        "issued_at": observed.isoformat(),
        "decision_authority": DECISION_AUTHORITY,
        "external_invocation_ready": True,
        "network_call_performed": False,
    }
    payload["invocation_hash"] = _hash(_invocation_payload(payload))
    return GoogleCalendarInvocationEnvelopeV0(**payload)


def verify_invocation_v0(
    invocation: GoogleCalendarInvocationEnvelopeV0 | Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    data = (
        invocation.to_dict()
        if isinstance(invocation, GoogleCalendarInvocationEnvelopeV0)
        else dict(invocation)
    )
    if data.get("schema") != INVOCATION_SCHEMA:
        return False, "GOOGLE_CALENDAR_INVOCATION_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "GOOGLE_CALENDAR_INVOCATION_AUTHORITY_INVALID"
    if data.get("external_invocation_ready") is not True:
        return False, "GOOGLE_CALENDAR_INVOCATION_NOT_READY"
    if data.get("network_call_performed") is not False:
        return False, "GOOGLE_CALENDAR_INVOCATION_PRECALL_FLAG_INVALID"
    ok, reason = validate_pilot_create_args_v0(data.get("connector_args") or {})
    if not ok:
        return False, reason
    expected_call_hash = canonical_google_calendar_call_hash(
        data["connector_args"]
    )
    if data.get("connector_call_hash") != expected_call_hash:
        return False, "GOOGLE_CALENDAR_INVOCATION_CALL_HASH_MISMATCH"
    if data.get("invocation_hash") != _hash(_invocation_payload(data)):
        return False, "GOOGLE_CALENDAR_INVOCATION_HASH_MISMATCH"
    return True, None


def _real_receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "schema",
            "receipt_id",
            "invocation_id",
            "invocation_hash",
            "action_id",
            "sovereign_ticket_hash",
            "world_action_request_hash",
            "connector_call_hash",
            "idempotency_key",
            "provider",
            "provider_event_id_sha256",
            "provider_status",
            "readback_verified",
            "cleanup_status",
            "active_event_left",
            "observed_at",
            "real_external_effect",
            "obsidia_governed_invocation",
            "decision_authority",
        )
    }


def ingest_google_calendar_provider_result_v0(
    *,
    invocation: GoogleCalendarInvocationEnvelopeV0 | Mapping[str, Any],
    provider_event_id: str,
    provider_status: str,
    readback_verified: bool,
    cleanup_status: str,
    active_event_left: bool,
    observed_at: str,
) -> GoogleCalendarRealProviderReceiptV0:
    ok, reason = verify_invocation_v0(invocation)
    if not ok:
        raise ValueError(f"INVALID_GOOGLE_CALENDAR_INVOCATION:{reason}")
    invocation_data = (
        invocation.to_dict()
        if isinstance(invocation, GoogleCalendarInvocationEnvelopeV0)
        else dict(invocation)
    )
    if not provider_event_id:
        raise ValueError("GOOGLE_CALENDAR_PROVIDER_EVENT_ID_REQUIRED")
    if provider_status != "confirmed":
        raise ValueError("GOOGLE_CALENDAR_PROVIDER_CREATE_NOT_CONFIRMED")
    if readback_verified is not True:
        raise ValueError("GOOGLE_CALENDAR_PROVIDER_READBACK_REQUIRED")
    if cleanup_status != "cancelled":
        raise ValueError("GOOGLE_CALENDAR_PROVIDER_CLEANUP_NOT_CONFIRMED")
    if active_event_left is not False:
        raise ValueError("GOOGLE_CALENDAR_PROVIDER_ACTIVE_EVENT_LEFT")

    _parse_time(observed_at)
    event_hash = hashlib.sha256(provider_event_id.encode("utf-8")).hexdigest()
    seed = {
        "invocation_hash": invocation_data["invocation_hash"],
        "provider_event_id_sha256": event_hash,
        "observed_at": observed_at,
    }
    receipt_id = f"gcalreceipt-{_hash(seed)[:32]}"
    payload = {
        "schema": REAL_RECEIPT_SCHEMA,
        "receipt_id": receipt_id,
        "invocation_id": invocation_data["invocation_id"],
        "invocation_hash": invocation_data["invocation_hash"],
        "action_id": invocation_data["action_id"],
        "sovereign_ticket_hash": invocation_data["sovereign_ticket_hash"],
        "world_action_request_hash": invocation_data["world_action_request_hash"],
        "connector_call_hash": invocation_data["connector_call_hash"],
        "idempotency_key": invocation_data["idempotency_key"],
        "provider": "GOOGLE_CALENDAR",
        "provider_event_id_sha256": event_hash,
        "provider_status": provider_status,
        "readback_verified": True,
        "cleanup_status": cleanup_status,
        "active_event_left": False,
        "observed_at": observed_at,
        "real_external_effect": True,
        "obsidia_governed_invocation": True,
        "decision_authority": DECISION_AUTHORITY,
    }
    payload["receipt_hash"] = _hash(_real_receipt_payload(payload))
    return GoogleCalendarRealProviderReceiptV0(**payload)


def verify_real_provider_receipt_v0(
    receipt: GoogleCalendarRealProviderReceiptV0 | Mapping[str, Any],
    *,
    expected_invocation_hash: str,
) -> tuple[bool, Optional[str]]:
    data = (
        receipt.to_dict()
        if isinstance(receipt, GoogleCalendarRealProviderReceiptV0)
        else dict(receipt)
    )
    if data.get("schema") != REAL_RECEIPT_SCHEMA:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_AUTHORITY_INVALID"
    if data.get("invocation_hash") != expected_invocation_hash:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_INVOCATION_MISMATCH"
    if data.get("provider") != "GOOGLE_CALENDAR":
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_PROVIDER_INVALID"
    if data.get("provider_status") != "confirmed":
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_CREATE_INVALID"
    if data.get("readback_verified") is not True:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_READBACK_INVALID"
    if data.get("cleanup_status") != "cancelled":
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_CLEANUP_INVALID"
    if data.get("active_event_left") is not False:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_ACTIVE_EFFECT_REMAINS"
    if data.get("real_external_effect") is not True:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_EFFECT_NOT_PROVEN"
    if data.get("obsidia_governed_invocation") is not True:
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_GOVERNANCE_INVALID"
    if data.get("receipt_hash") != _hash(_real_receipt_payload(data)):
        return False, "GOOGLE_CALENDAR_REAL_RECEIPT_HASH_MISMATCH"
    return True, None
