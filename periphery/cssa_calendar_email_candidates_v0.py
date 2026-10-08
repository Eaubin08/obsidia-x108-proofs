"""CSSA-only offline calendar and reply candidate preparation.

Fixtures only. No connected mailbox/calendar, no delivery, no KX108 decision.
A due date is accepted only as an explicit structured input, never inferred
from newsletter, event marketing, or natural-language text.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from periphery.cssa_admin_e2e_synthetic_v0 import build_cssa_admin_case, verify_cssa_admin_case


def prepare_cssa_followup_candidates(
    message: dict[str, str], *, requested_followup_at: str | None = None,
) -> dict:
    bundle = build_cssa_admin_case(message)
    if not verify_cssa_admin_case(bundle):
        raise ValueError("CSSA_SOURCE_PROPOSAL_INVALID")
    intake = bundle["case"]["input"]
    category = intake["category_candidate"]
    base = {
        "schema": "CSSA_CALENDAR_EMAIL_CANDIDATES_V0",
        "source_sha256": intake["source_fingerprint"],
        "category_candidate": category,
        "status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "calendar_event": None,
        "email_draft": None,
        "calendar_external_write": False,
        "email_send": False,
        "external_actions": [],
    }
    # Do not infer consent or approval from ticket/receipt/marketing email.
    if category != "SUPPORTER_REQUEST":
        return {**base, "reason": "NO_SUPPORTER_FOLLOWUP_OR_AMBIGUOUS"}
    if requested_followup_at is not None:
        if not isinstance(requested_followup_at, str):
            raise ValueError("CSSA_FOLLOWUP_DATE_INVALID")
        try:
            dt = datetime.fromisoformat(requested_followup_at)
        except ValueError as exc:
            raise ValueError("CSSA_FOLLOWUP_DATE_INVALID") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("CSSA_FOLLOWUP_DATE_MUST_HAVE_TIMEZONE")
        base["calendar_event"] = {
            "kind": "FOLLOWUP_REMINDER_CANDIDATE",
            "start_at": requested_followup_at,
            "title": "Revoir la demande supporter CSSA",
            "source_sha256": intake["source_fingerprint"],
            "state": "PROPOSED_NOT_CREATED",
        }
    base["email_draft"] = {
        "kind": "REPLY_DRAFT_CANDIDATE",
        "subject": "Re: " + message["subject"][:160],
        "body": "Bonjour,\n\nVotre demande est en cours d'examen par le club.\n\nCordialement,\nÉquipe CSSA",
        "recipient": message["sender"],
        "source_sha256": intake["source_fingerprint"],
        "state": "DRAFT_NOT_SENT",
        "template_only": True,
        "human_review_required": True,
    }
    base["reason"] = "NO_KX108_DECISION_OR_HUMAN_APPROVAL"
    return base
