"""C2.9 test-only authenticated record/ticket binding (not a trust service).

A MAC over a canonical record hash, action, scope and ticket identity checks
fixture integrity. Key possession alone cannot establish organization authority,
a KX108 issuer, revocation status or provider execution permission.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re

SCHEMA = "V01_C29_RECORD_BOUND_TICKET_ATTESTATION_FIXTURE"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

@dataclass(frozen=True)
class TicketRecordBindingFixtureV0:
    schema: str
    issuer_ref: str
    decision_record_id: str
    decision_record_hash: str
    action_id: str
    required_scope: str
    ticket_id: str
    ticket_hash: str
    expires_at: str
    signature: str


def _bytes(p):
    payload = {k: v for k, v in vars(p).items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sign_ticket_record_fixture_v0(binding, *, fixture_key):
    """Only for deterministic isolated tests; never a sovereign issuer."""
    if not isinstance(fixture_key, bytes) or len(fixture_key) < 32:
        raise ValueError("C29_FIXTURE_KEY_INVALID")
    return replace(binding, signature=hmac.new(fixture_key, _bytes(binding), hashlib.sha256).hexdigest())


def verify_ticket_record_fixture_v0(binding, *, trusted_fixture_issuer,
                                     verifier_key, record, ticket, now):
    if not isinstance(binding, TicketRecordBindingFixtureV0):
        return False, "C29_ATTESTATION_TYPE_INVALID"
    if binding.schema != SCHEMA or not binding.issuer_ref or binding.issuer_ref != trusted_fixture_issuer:
        return False, "C29_FIXTURE_ISSUER_MISMATCH"
    if not isinstance(record, dict) or ticket is None:
        return False, "C29_RECORD_OR_TICKET_ABSENT"
    if not all(isinstance(x, str) and SHA_RE.fullmatch(x) for x in
               (binding.decision_record_hash, binding.ticket_hash)):
        return False, "C29_HASH_INVALID"
    if (binding.decision_record_id != record.get("decision_record_id")
        or binding.decision_record_hash != record.get("decision_record_hash")
        or binding.action_id != record.get("action_id")
        or binding.required_scope != record.get("required_scope")
        or binding.action_id != getattr(ticket, "action_id", None)
        or binding.required_scope != getattr(ticket, "scope", None)
        or binding.ticket_id != getattr(ticket, "ticket_id", None)
        or binding.ticket_hash != getattr(ticket, "hash", None)):
        return False, "C29_RECORD_TICKET_BINDING_MISMATCH"
    if not isinstance(verifier_key, bytes) or len(verifier_key) < 32:
        return False, "C29_TRUST_ROOT_UNAVAILABLE"
    try:
        expiry = datetime.fromisoformat(binding.expires_at)
        if expiry.tzinfo is None or now.tzinfo is None:
            return False, "C29_TIMEZONE_REQUIRED"
        if now.astimezone(timezone.utc) >= expiry.astimezone(timezone.utc):
            return False, "C29_ATTESTATION_EXPIRED"
    except (ValueError, TypeError, AttributeError):
        return False, "C29_TIME_INVALID"
    mac = hmac.new(verifier_key, _bytes(binding), hashlib.sha256).hexdigest()
    if not isinstance(binding.signature, str) or not hmac.compare_digest(mac, binding.signature):
        return False, "C29_SIGNATURE_INVALID"
    return True, None
