"""CSSA V0.1 in-process provider sandbox, intentionally WITHOUT network or writes.

Models inbound mail delivery and downstream queue intentions only. Never uses
a provider SDK, mutates Native CRM/TASKS, sends email or creates calendar events.
The frozen CSSA V0 remains unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Mapping

from periphery.cssa_cross_component_offline_v0 import (
    build_cssa_cross_component_batch, verify_cssa_cross_component_batch,
)


def _hash(data: object) -> str:
    return sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def simulate_cssa_sandbox(
    messages: list[Mapping[str, str]], *,
    followups: Mapping[str, str] | None = None,
    failure_at: str | None = None,
) -> dict:
    if failure_at not in (None, "mailbox", "crm", "calendar", "email"):
        raise ValueError("CSSA_UNKNOWN_FAILURE_POINT")
    if failure_at == "mailbox":
        return _blocked("MAILBOX_UNAVAILABLE")
    batch = build_cssa_cross_component_batch(messages, explicit_followups=followups)
    if not verify_cssa_cross_component_batch(batch):
        return _blocked("INTEGRITY_VERIFICATION_FAILED")
    events = []
    for case in batch["report"]["cases"]:
        events.append({"surface": "MAILBOX_FAKE", "kind": "INBOUND_OBSERVED",
                       "source_sha256": case["source_sha256"]})
        if case["crm_candidate_id"] is not None:
            events.append({"surface": "CRM_FAKE", "kind": "PROPOSAL_INSPECTED",
                           "source_sha256": case["source_sha256"],
                           "entity_ref": case["crm_candidate_id"],
                           "result": "UNAVAILABLE" if failure_at == "crm" else "HELD"})
        if case["calendar_candidate"] is not None:
            events.append({"surface": "CALENDAR_FAKE", "kind": "PROPOSAL_INSPECTED",
                           "source_sha256": case["source_sha256"],
                           "result": "UNAVAILABLE" if failure_at == "calendar" else "HELD"})
        if case["email_draft_candidate"] is not None:
            events.append({"surface": "EMAIL_FAKE", "kind": "DRAFT_INSPECTED",
                           "source_sha256": case["source_sha256"],
                           "result": "UNAVAILABLE" if failure_at == "email" else "HELD"})
    status = "BLOCK" if any(e.get("result") == "UNAVAILABLE" for e in events) else "HOLD"
    report = {
        "schema": "CSSA_PROVIDER_SANDBOX_V01",
        "mode": "OFFLINE_IN_PROCESS_ONLY",
        "status": status,
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "source_batch_sha256": batch["audit_sha256"],
        "events": events,
        "duplicate_ids": batch["report"]["duplicate_ids"],
        "conflicting_ids": batch["report"]["conflicting_ids"],
        "external_actions": [],
        "provider_writes": False,
        "native_store_writes": False,
        "execution_proven": False,
    }
    return {"report": report, "receipt_sha256": _hash(report)}


def _blocked(reason: str) -> dict:
    report = {
        "schema": "CSSA_PROVIDER_SANDBOX_V01",
        "mode": "OFFLINE_IN_PROCESS_ONLY",
        "status": "BLOCK",
        "reason": reason,
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "source_batch_sha256": None,
        "events": [],
        "duplicate_ids": [],
        "conflicting_ids": [],
        "external_actions": [],
        "provider_writes": False,
        "native_store_writes": False,
        "execution_proven": False,
    }
    return {"report": report, "receipt_sha256": _hash(report)}


def verify_cssa_sandbox(bundle: Mapping[str, object]) -> bool:
    if not isinstance(bundle, Mapping) or set(bundle) != {"report", "receipt_sha256"}:
        return False
    report = bundle["report"]
    if not isinstance(report, dict):
        return False
    try:
        return (
            _hash(report) == bundle["receipt_sha256"]
            and report["schema"] == "CSSA_PROVIDER_SANDBOX_V01"
            and report["mode"] == "OFFLINE_IN_PROCESS_ONLY"
            and report["status"] in ("HOLD", "BLOCK")
            and report["decision_authority"] == "KX108_ONLY"
            and report["kx108_decision"] is None
            and report["human_approval"] is None
            and report["external_actions"] == []
            and report["provider_writes"] is False
            and report["native_store_writes"] is False
            and report["execution_proven"] is False
            and all(e["surface"] in ("MAILBOX_FAKE", "CRM_FAKE", "CALENDAR_FAKE", "EMAIL_FAKE")
                    for e in report["events"])
        )
    except (KeyError, TypeError, ValueError):
        return False
