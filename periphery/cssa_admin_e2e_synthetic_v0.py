"""CSSA administrative E2E *simulation*: intake -> proposed follow-up -> proof.

No production CRM/calendar/email connector, no real KX108 decision and no
authority inferred from fixture classification. All outputs are pure data.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping

from .cssa_synthetic_intake_v0 import classify_cssa_message, ingest_synthetic_batch

PROPOSALS = {
    "PAYMENT_CONFIRMATION": ("ARCHIVE_RECEIPT_REVIEW", "NO_NEW_PURCHASE"),
    "TICKET_ORDER": ("REVIEW_TICKET_RECORD", "CHECK_EXISTING_ORDER"),
    "SUBSCRIPTION": ("REVIEW_SUBSCRIPTION_RECORD", "CHECK_EXISTING_SUBSCRIPTION"),
    "CLUB_COMMUNICATION": ("CLASSIFY_INFORMATION", "NO_TASK_BY_DEFAULT"),
    "SUPPORTER_REQUEST": ("PROPOSE_SUPPORTER_FOLLOWUP", "HUMAN_REVIEW"),
    "UNKNOWN": ("ESCALATE_UNCLASSIFIED", "NO_ACTION"),
}


def _sha(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def build_cssa_admin_case(message: Mapping[str, str]) -> dict:
    intake = classify_cssa_message(message)
    proposal, treatment = PROPOSALS[intake["category_candidate"]]
    proposed_records = []
    if intake["category_candidate"] == "SUPPORTER_REQUEST":
        proposed_records = [{
            "kind": "TASK_CANDIDATE",
            "title": "Examiner la demande du supporter",
            "source_message_id": intake["message_id"],
            "state": "PROPOSED_NOT_CREATED",
        }]
    # Deliberately no calendar event without a real user-requested date and approval.
    case = {
        "schema": "CSSA_ADMIN_CASE_V0",
        "input": intake,
        "proposal": {
            "kind": proposal,
            "treatment": treatment,
            "crm": proposed_records,
            "calendar": [],
            "email_reply": None,
        },
        "governance": {
            "status": "HOLD",
            "reason": "NO_REAL_KX108_DECISION_OR_HUMAN_APPROVAL",
            "decision_authority": "KX108_ONLY",
            "kx108_decision": None,
            "human_approval": None,
            "external_dispatch": False,
        },
    }
    receipt = {
        "schema": "CSSA_OFFLINE_PROPOSAL_RECEIPT_V0",
        "case_sha256": _sha(case),
        "source_sha256": intake["source_fingerprint"],
        "proof_kind": "SYNTHETIC_PROPOSAL_ONLY",
        "execution_proven": False,
        "native_memory_write": False,
        "external_actions": [],
    }
    return {"case": case, "receipt": receipt}


def verify_cssa_admin_case(bundle: Mapping[str, object]) -> bool:
    if not isinstance(bundle, Mapping) or set(bundle) != {"case", "receipt"}:
        return False
    case, receipt = bundle["case"], bundle["receipt"]
    if not isinstance(case, dict) or not isinstance(receipt, dict):
        return False
    gov, inp = case.get("governance"), case.get("input")
    if not isinstance(gov, dict) or not isinstance(inp, dict):
        return False
    return (
        receipt.get("case_sha256") == _sha(case)
        and receipt.get("source_sha256") == inp.get("source_fingerprint")
        and receipt.get("proof_kind") == "SYNTHETIC_PROPOSAL_ONLY"
        and receipt.get("execution_proven") is False
        and receipt.get("native_memory_write") is False
        and receipt.get("external_actions") == []
        and gov.get("status") == "HOLD"
        and gov.get("kx108_decision") is None
        and gov.get("human_approval") is None
        and gov.get("external_dispatch") is False
        and gov.get("decision_authority") == "KX108_ONLY"
    )


def build_cssa_admin_batch(messages: list[Mapping[str, str]]) -> dict:
    batch = ingest_synthetic_batch(messages)
    # Do not generate proposals for conflicting identifiers.
    conflicts = set(batch["conflicts"])
    bundles = [
        build_cssa_admin_case(next(m for m in messages if m["message_id"].strip() == item["message_id"]))
        for item in batch["candidates"] if item["message_id"] not in conflicts
    ]
    return {
        "schema": "CSSA_ADMIN_OFFLINE_BATCH_V0",
        "bundles": bundles,
        "duplicate_ids": batch["duplicates"],
        "conflicting_ids": batch["conflicts"],
        "status": "HOLD",
        "external_actions": [],
    }
