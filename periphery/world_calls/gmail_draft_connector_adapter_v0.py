"""Gmail governed draft adapter contract V0.

Low-risk real-provider pilot:
- CREATE_DRAFT only
- authenticated account -> authenticated self only
- no send
- no CC/BCC
- no attachments
- no reply threading
- plain text only
- subject prefixed with [OBSIDIA PILOT]

The raw authenticated email address is transport-local and never persisted.
The invocation binds AUTHENTICATED_SELF plus the expected SHA-256 of the
resolved recipient.

No credentials are stored and no network library is imported here.
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

INVOCATION_SCHEMA = "GMAIL_DRAFT_INVOCATION_ENVELOPE_V0"
REAL_RECEIPT_SCHEMA = "GMAIL_DRAFT_REAL_PROVIDER_RECEIPT_V0"

CONNECTOR_ID = "GMAIL"
CONNECTOR_ACTION_CREATE_DRAFT = "CREATE_DRAFT"
REQUIRED_SCOPE_CREATE_DRAFT = "gmail:draft:create:pilot"
RECIPIENT_BINDING_SELF = "AUTHENTICATED_SELF"
PILOT_SUBJECT_PREFIX = "[OBSIDIA PILOT]"

# Privacy-preserving identity binding for the connected pilot account.
EXPECTED_SELF_RECIPIENT_SHA256 = (
    "3d2d101e26445848ef9a9a38953eb358cdce8a184aec4b408acfbc9f3722cde5"
)


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


def canonical_gmail_draft_call_hash(args: Mapping[str, Any]) -> str:
    return _hash(
        {
            "connector_id": CONNECTOR_ID,
            "connector_action": CONNECTOR_ACTION_CREATE_DRAFT,
            "connector_args": dict(args),
        }
    )


def validate_pilot_draft_args_v0(
    args: Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    required = {
        "recipient_binding",
        "recipient_sha256",
        "subject",
        "body",
        "content_type",
        "cc",
        "bcc",
        "reply_message_id",
        "attachment_count",
    }
    if set(args) != required:
        return False, "GMAIL_DRAFT_ARGS_SHAPE_INVALID"
    if args["recipient_binding"] != RECIPIENT_BINDING_SELF:
        return False, "GMAIL_DRAFT_RECIPIENT_MUST_BE_AUTHENTICATED_SELF"
    if args["recipient_sha256"] != EXPECTED_SELF_RECIPIENT_SHA256:
        return False, "GMAIL_DRAFT_SELF_RECIPIENT_HASH_MISMATCH"
    if not str(args["subject"]).startswith(PILOT_SUBJECT_PREFIX):
        return False, "GMAIL_DRAFT_PILOT_SUBJECT_PREFIX_REQUIRED"
    if not str(args["body"]).strip():
        return False, "GMAIL_DRAFT_BODY_REQUIRED"
    if args["content_type"] != "text/plain":
        return False, "GMAIL_DRAFT_PILOT_PLAIN_TEXT_ONLY"
    if args["cc"] != "":
        return False, "GMAIL_DRAFT_CC_FORBIDDEN"
    if args["bcc"] != "":
        return False, "GMAIL_DRAFT_BCC_FORBIDDEN"
    if args["reply_message_id"] is not None:
        return False, "GMAIL_DRAFT_REPLY_THREAD_FORBIDDEN"
    if args["attachment_count"] != 0:
        return False, "GMAIL_DRAFT_ATTACHMENTS_FORBIDDEN"
    return True, None


@dataclass(frozen=True)
class GmailDraftInvocationEnvelopeV0:
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
class GmailDraftRealProviderReceiptV0:
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
    recipient_sha256: str
    provider_draft_id_sha256: str
    provider_message_id_sha256: str
    draft_created: bool
    draft_readback_verified: bool
    draft_cleanup_verified: bool
    sent_message_created: bool
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


def build_gmail_draft_invocation_v0(
    *,
    ticket: LiveSovereignTicketV0,
    activation_policy: ExternalRuntimeActivationPolicyV0,
    connector_args: Mapping[str, Any],
    observed_target_ref: str,
    observed_target_prestate_hash: str,
    now: str | None = None,
) -> GmailDraftInvocationEnvelopeV0:
    ok, reason = validate_pilot_draft_args_v0(connector_args)
    if not ok:
        raise ValueError(reason)
    if ticket.connector_id != CONNECTOR_ID:
        raise ValueError("GMAIL_DRAFT_TICKET_CONNECTOR_ID_MISMATCH")
    if ticket.connector_action != CONNECTOR_ACTION_CREATE_DRAFT:
        raise ValueError("GMAIL_DRAFT_TICKET_ACTION_MISMATCH")
    if ticket.required_scope != REQUIRED_SCOPE_CREATE_DRAFT:
        raise ValueError("GMAIL_DRAFT_TICKET_SCOPE_MISMATCH")

    call_hash = canonical_gmail_draft_call_hash(connector_args)
    gateway = ObsidiaLiveGatewayV0().check(
        ticket=ticket,
        activation_policy=activation_policy,
        observed_connector_id=CONNECTOR_ID,
        observed_connector_action=CONNECTOR_ACTION_CREATE_DRAFT,
        observed_connector_call_hash=call_hash,
        observed_target_ref=observed_target_ref,
        observed_target_prestate_hash=observed_target_prestate_hash,
        observed_required_scope=REQUIRED_SCOPE_CREATE_DRAFT,
        observed_idempotency_key=ticket.idempotency_key,
        now=now,
    )
    if gateway.gate_result != "LIVE_PREFLIGHT_READY":
        raise ValueError(f"GMAIL_DRAFT_GATEWAY_BLOCK:{gateway.reason}")

    observed = datetime.datetime.fromisoformat(
        now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    if observed.tzinfo is None:
        raise ValueError("GMAIL_DRAFT_INVOCATION_TIME_INVALID")

    seed = {
        "ticket_hash": ticket.ticket_hash,
        "call_hash": call_hash,
        "idempotency_key": ticket.idempotency_key,
        "issued_at": observed.isoformat(),
    }
    invocation_id = f"gmaildraft-{_hash(seed)[:32]}"
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
        "connector_action": CONNECTOR_ACTION_CREATE_DRAFT,
        "connector_args": dict(connector_args),
        "issued_at": observed.isoformat(),
        "decision_authority": DECISION_AUTHORITY,
        "external_invocation_ready": True,
        "network_call_performed": False,
    }
    payload["invocation_hash"] = _hash(_invocation_payload(payload))
    return GmailDraftInvocationEnvelopeV0(**payload)


def verify_invocation_v0(
    invocation: GmailDraftInvocationEnvelopeV0 | Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    data = (
        invocation.to_dict()
        if isinstance(invocation, GmailDraftInvocationEnvelopeV0)
        else dict(invocation)
    )
    if data.get("schema") != INVOCATION_SCHEMA:
        return False, "GMAIL_DRAFT_INVOCATION_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "GMAIL_DRAFT_INVOCATION_AUTHORITY_INVALID"
    if data.get("external_invocation_ready") is not True:
        return False, "GMAIL_DRAFT_INVOCATION_NOT_READY"
    if data.get("network_call_performed") is not False:
        return False, "GMAIL_DRAFT_INVOCATION_PRECALL_FLAG_INVALID"
    ok, reason = validate_pilot_draft_args_v0(data.get("connector_args") or {})
    if not ok:
        return False, reason
    expected_call_hash = canonical_gmail_draft_call_hash(
        data["connector_args"]
    )
    if data.get("connector_call_hash") != expected_call_hash:
        return False, "GMAIL_DRAFT_INVOCATION_CALL_HASH_MISMATCH"
    if data.get("invocation_hash") != _hash(_invocation_payload(data)):
        return False, "GMAIL_DRAFT_INVOCATION_HASH_MISMATCH"
    return True, None


def _receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
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
            "recipient_sha256",
            "provider_draft_id_sha256",
            "provider_message_id_sha256",
            "draft_created",
            "draft_readback_verified",
            "draft_cleanup_verified",
            "sent_message_created",
            "observed_at",
            "real_external_effect",
            "obsidia_governed_invocation",
            "decision_authority",
        )
    }


def ingest_gmail_draft_provider_result_v0(
    *,
    invocation: GmailDraftInvocationEnvelopeV0 | Mapping[str, Any],
    provider_draft_id: str,
    provider_message_id: str,
    resolved_recipient: str,
    draft_created: bool,
    draft_readback_verified: bool,
    draft_cleanup_verified: bool,
    sent_message_created: bool,
    observed_at: str,
) -> GmailDraftRealProviderReceiptV0:
    ok, reason = verify_invocation_v0(invocation)
    if not ok:
        raise ValueError(f"INVALID_GMAIL_DRAFT_INVOCATION:{reason}")
    data = (
        invocation.to_dict()
        if isinstance(invocation, GmailDraftInvocationEnvelopeV0)
        else dict(invocation)
    )
    recipient_hash = hashlib.sha256(
        resolved_recipient.encode("utf-8")
    ).hexdigest()
    if recipient_hash != EXPECTED_SELF_RECIPIENT_SHA256:
        raise ValueError("GMAIL_DRAFT_RESOLVED_SELF_HASH_MISMATCH")
    if not provider_draft_id or not provider_message_id:
        raise ValueError("GMAIL_DRAFT_PROVIDER_IDENTIFIERS_REQUIRED")
    if draft_created is not True:
        raise ValueError("GMAIL_DRAFT_CREATE_NOT_CONFIRMED")
    if draft_readback_verified is not True:
        raise ValueError("GMAIL_DRAFT_READBACK_REQUIRED")
    if draft_cleanup_verified is not True:
        raise ValueError("GMAIL_DRAFT_CLEANUP_REQUIRED")
    if sent_message_created is not False:
        raise ValueError("GMAIL_DRAFT_SEND_MUST_REMAIN_FALSE")

    datetime.datetime.fromisoformat(observed_at)
    draft_hash = hashlib.sha256(
        provider_draft_id.encode("utf-8")
    ).hexdigest()
    message_hash = hashlib.sha256(
        provider_message_id.encode("utf-8")
    ).hexdigest()
    seed = {
        "invocation_hash": data["invocation_hash"],
        "provider_draft_id_sha256": draft_hash,
        "observed_at": observed_at,
    }
    receipt_id = f"gmaildraftreceipt-{_hash(seed)[:32]}"
    payload = {
        "schema": REAL_RECEIPT_SCHEMA,
        "receipt_id": receipt_id,
        "invocation_id": data["invocation_id"],
        "invocation_hash": data["invocation_hash"],
        "action_id": data["action_id"],
        "sovereign_ticket_hash": data["sovereign_ticket_hash"],
        "world_action_request_hash": data["world_action_request_hash"],
        "connector_call_hash": data["connector_call_hash"],
        "idempotency_key": data["idempotency_key"],
        "provider": "GMAIL",
        "recipient_sha256": recipient_hash,
        "provider_draft_id_sha256": draft_hash,
        "provider_message_id_sha256": message_hash,
        "draft_created": True,
        "draft_readback_verified": True,
        "draft_cleanup_verified": True,
        "sent_message_created": False,
        "observed_at": observed_at,
        "real_external_effect": True,
        "obsidia_governed_invocation": True,
        "decision_authority": DECISION_AUTHORITY,
    }
    payload["receipt_hash"] = _hash(_receipt_payload(payload))
    return GmailDraftRealProviderReceiptV0(**payload)


def verify_real_provider_receipt_v0(
    receipt: GmailDraftRealProviderReceiptV0 | Mapping[str, Any],
    *,
    expected_invocation_hash: str,
) -> tuple[bool, Optional[str]]:
    data = (
        receipt.to_dict()
        if isinstance(receipt, GmailDraftRealProviderReceiptV0)
        else dict(receipt)
    )
    if data.get("schema") != REAL_RECEIPT_SCHEMA:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_SCHEMA_INVALID"
    if data.get("invocation_hash") != expected_invocation_hash:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_INVOCATION_MISMATCH"
    if data.get("provider") != "GMAIL":
        return False, "GMAIL_DRAFT_REAL_RECEIPT_PROVIDER_INVALID"
    if data.get("recipient_sha256") != EXPECTED_SELF_RECIPIENT_SHA256:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_RECIPIENT_INVALID"
    if data.get("draft_created") is not True:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_CREATE_INVALID"
    if data.get("draft_readback_verified") is not True:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_READBACK_INVALID"
    if data.get("draft_cleanup_verified") is not True:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_CLEANUP_INVALID"
    if data.get("sent_message_created") is not False:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_SEND_OCCURRED"
    if data.get("real_external_effect") is not True:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_EFFECT_NOT_PROVEN"
    if data.get("obsidia_governed_invocation") is not True:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_GOVERNANCE_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "GMAIL_DRAFT_REAL_RECEIPT_AUTHORITY_INVALID"
    if data.get("receipt_hash") != _hash(_receipt_payload(data)):
        return False, "GMAIL_DRAFT_REAL_RECEIPT_HASH_MISMATCH"
    return True, None
