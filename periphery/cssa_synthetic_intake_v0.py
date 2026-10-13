"""CSSA synthetic administrative intake — offline classification, never dispatch.

This local fixture model is NOT the production OS IR pipeline and does not
produce a KX108 decision. It only prepares read-only candidate classifications.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping

CATEGORIES = frozenset({
    "PAYMENT_CONFIRMATION", "TICKET_ORDER", "SUBSCRIPTION",
    "CLUB_COMMUNICATION", "SUPPORTER_REQUEST", "UNKNOWN",
})


def _fingerprint(payload: Mapping[str, str]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def classify_cssa_message(message: Mapping[str, str]) -> dict:
    """Return a bounded, non-authoritative review packet for a synthetic email.

    Ambiguous or incomplete items fail closed. No external I/O, CRM writes,
    calendar events, email sending, or action authority are available here.
    """
    if not isinstance(message, Mapping):
        raise TypeError("message must be a mapping")
    fields = ("message_id", "subject", "body", "sender")
    if any(not isinstance(message.get(k), str) for k in fields):
        raise ValueError("missing or invalid message field")
    mid = message["message_id"].strip()
    if not mid or len(mid) > 160:
        raise ValueError("invalid message_id")
    subject, body = message["subject"].casefold(), message["body"].casefold()
    text = subject + " " + body
    # Only deliberate fixture signals, not general NLP or production routing.
    signals = {
        "PAYMENT_CONFIRMATION": ("confirmation de paiement", "paiement confirmé"),
        "TICKET_ORDER": ("billet commandé", "commande de billet"),
        "SUBSCRIPTION": ("confirmation abonnement", "abonnement saison"),
        "CLUB_COMMUNICATION": ("communiqué du club", "newsletter du club"),
        "SUPPORTER_REQUEST": ("question supporter", "demande de renseignement"),
    }
    matched = sorted(kind for kind, markers in signals.items()
                     if any(marker in text for marker in markers))
    category = matched[0] if len(matched) == 1 else "UNKNOWN"
    reason = ("SINGLE_SYNTHETIC_SIGNAL" if len(matched) == 1 else
              "AMBIGUOUS_MULTIPLE_SIGNALS" if matched else "NO_RECOGNIZED_SIGNAL")
    canonical = {k: message[k] for k in fields}
    return {
        "schema": "CSSA_SYNTHETIC_INTAKE_V0",
        "message_id": mid,
        "source_fingerprint": _fingerprint(canonical),
        "category_candidate": category,
        "classification_reason": reason,
        "matched_categories": matched,
        "review_status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_review_required": True,
        "send_email": False,
        "crm_external_write": False,
        "calendar_external_write": False,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "production_integration": "NOT_CONNECTED",
    }


def ingest_synthetic_batch(messages: list[Mapping[str, str]]) -> dict:
    """Prepare an immutable-looking candidate ledger; deduplicate by source ID.

    Conflicting reused IDs are held, never silently collapsed or overwritten.
    """
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    by_id: dict[str, dict] = {}
    conflicts: list[str] = []
    duplicates: list[str] = []
    for message in messages:
        item = classify_cssa_message(message)
        mid = item["message_id"]
        old = by_id.get(mid)
        if old is None:
            by_id[mid] = item
        elif old["source_fingerprint"] == item["source_fingerprint"]:
            duplicates.append(mid)
        else:
            conflicts.append(mid)
    return {
        "schema": "CSSA_SYNTHETIC_BATCH_V0",
        "candidates": list(by_id.values()),
        "duplicates": duplicates,
        "conflicts": conflicts,
        "batch_status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "external_actions": [],
        "historical_evidence_replaced": False,
    }
