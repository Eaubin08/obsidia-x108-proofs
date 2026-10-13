"""ENTERPRISE_SOURCE_SANDBOX_V0.

Deterministic synthetic office used to exercise native sources before any
real enterprise integration. This is test infrastructure, not a production
semantic classifier.

The sandbox contains:
- informational mail that must not create work;
- actionable mail with a deadline;
- incident mail;
- contradictory instructions;
- a duplicate/near-duplicate request;
- contract and supplier documents;
- calendar deadline and routine events;
- one missing-evidence case.

All data is synthetic.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SANDBOX_STATUS = "SIMULATED_NOT_OBSERVED"


@dataclass(frozen=True)
class EnterpriseSandboxPathsV0:
    root: Path
    mailbox: Path
    documents: Path
    calendar: Path
    truth_manifest: Path


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def materialize_enterprise_source_sandbox_v0(
    root: Path,
) -> EnterpriseSandboxPathsV0:
    root = root.resolve()
    mailbox = root / "mailbox"
    documents = root / "documents"
    calendar = root / "calendar"
    mailbox.mkdir(parents=True, exist_ok=True)
    documents.mkdir(parents=True, exist_ok=True)
    calendar.mkdir(parents=True, exist_ok=True)

    mails = [
        {
            "file": "001-info.json",
            "id": "mail-info-001",
            "sender": "communication@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Monthly information bulletin",
            "body": "General information only. No response or action required.",
            "received_at": "2026-10-01T08:00:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "INFORMATION_ONLY",
                "create_case": False,
                "create_task": False,
            },
        },
        {
            "file": "002-action-deadline.json",
            "id": "mail-action-001",
            "sender": "institution@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Action required: submit dossier",
            "body": (
                "Please submit the requested dossier by 2026-10-10 17:00 UTC. "
                "A response is required."
            ),
            "received_at": "2026-10-02T09:00:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "ACTION_WITH_DEADLINE",
                "create_case": True,
                "create_task": True,
                "calendar_candidate": True,
                "due_at": "2026-10-10T17:00:00+00:00",
            },
        },
        {
            "file": "003-incident.json",
            "id": "mail-incident-001",
            "sender": "ops@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Incident: access control unavailable",
            "body": (
                "Operational incident confirmed. Access control is unavailable. "
                "Immediate investigation is required."
            ),
            "received_at": "2026-10-03T07:30:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "INCIDENT",
                "create_case": True,
                "create_task": True,
                "calendar_candidate": False,
            },
        },
        {
            "file": "004-conflict-a.json",
            "id": "mail-conflict-a",
            "sender": "manager-a@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Supplier order instruction",
            "body": "Approve supplier order SO-77 today.",
            "received_at": "2026-10-03T08:00:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "CONFLICT_PART_A",
                "conflict_group": "supplier-order-so77",
                "expected_gate": "BLOCK",
            },
        },
        {
            "file": "005-conflict-b.json",
            "id": "mail-conflict-b",
            "sender": "manager-b@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Supplier order instruction",
            "body": "Do not approve supplier order SO-77 under any circumstance.",
            "received_at": "2026-10-03T08:05:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "CONFLICT_PART_B",
                "conflict_group": "supplier-order-so77",
                "expected_gate": "BLOCK",
            },
        },
        {
            "file": "006-duplicate.json",
            "id": "mail-action-001-duplicate",
            "sender": "institution@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Reminder: submit dossier",
            "body": (
                "Reminder: please submit the requested dossier by "
                "2026-10-10 17:00 UTC. A response is required."
            ),
            "received_at": "2026-10-04T09:00:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "DUPLICATE_ACTION",
                "duplicate_of": "mail-action-001",
                "must_not_create_second_case": True,
            },
        },
        {
            "file": "007-missing-evidence.json",
            "id": "mail-missing-evidence-001",
            "sender": "unknown@example.invalid",
            "recipients": ["office@example.invalid"],
            "subject": "Please process request",
            "body": "Please process the request as discussed.",
            "received_at": "2026-10-05T09:00:00+00:00",
            "attachment_count": 0,
            "truth": {
                "class": "MISSING_EVIDENCE",
                "expected_gate": "HOLD",
            },
        },
    ]

    for mail in mails:
        _write_json(
            mailbox / mail["file"],
            {
                key: mail[key]
                for key in (
                    "id",
                    "sender",
                    "recipients",
                    "subject",
                    "body",
                    "received_at",
                    "attachment_count",
                )
            },
        )

    (documents / "contract-renewal.md").write_text(
        (
            "# Contract CR-2026-04\n\n"
            "Renewal review required before 2026-10-12T12:00:00+00:00.\n"
            "Owner: operations.\n"
        ),
        encoding="utf-8",
    )
    (documents / "supplier-terms.md").write_text(
        (
            "# Supplier Terms\n\n"
            "Order SO-77 requires dual validation before approval.\n"
        ),
        encoding="utf-8",
    )
    (documents / "policy-info.md").write_text(
        (
            "# Information Policy\n\n"
            "Reference document only. No action required.\n"
        ),
        encoding="utf-8",
    )

    events = [
        {
            "file": "001-deadline.json",
            "id": "event-deadline-001",
            "title": "Dossier submission deadline",
            "description": "Deadline associated with mail-action-001.",
            "start_time": "2026-10-10T16:30:00+00:00",
            "end_time": "2026-10-10T17:00:00+00:00",
            "timezone": "UTC",
            "attendee_count": 0,
            "location": None,
            "truth": {"class": "DEADLINE_EVENT"},
        },
        {
            "file": "002-routine.json",
            "id": "event-routine-001",
            "title": "Weekly coordination",
            "description": "Routine meeting.",
            "start_time": "2026-10-06T09:00:00+00:00",
            "end_time": "2026-10-06T09:30:00+00:00",
            "timezone": "UTC",
            "attendee_count": 4,
            "location": "Meeting room",
            "truth": {"class": "ROUTINE_EVENT"},
        },
    ]
    for event in events:
        _write_json(
            calendar / event["file"],
            {
                key: event[key]
                for key in (
                    "id",
                    "title",
                    "description",
                    "start_time",
                    "end_time",
                    "timezone",
                    "attendee_count",
                    "location",
                )
            },
        )

    truth = {
        "schema": "OBSIDIA_ENTERPRISE_SOURCE_SANDBOX_V0",
        "status": SANDBOX_STATUS,
        "mail_count": len(mails),
        "document_count": 3,
        "calendar_event_count": len(events),
        "mail_truth": {
            mail["id"]: mail["truth"]
            for mail in mails
        },
        "document_truth": {
            "contract-renewal.md": {
                "class": "CONTRACT_DEADLINE",
                "create_case": True,
                "create_task": True,
                "due_at": "2026-10-12T12:00:00+00:00",
            },
            "supplier-terms.md": {
                "class": "SUPPLIER_CONSTRAINT",
                "supports_conflict_group": "supplier-order-so77",
            },
            "policy-info.md": {
                "class": "INFORMATION_ONLY",
                "create_case": False,
                "create_task": False,
            },
        },
        "calendar_truth": {
            event["id"]: event["truth"]
            for event in events
        },
        "expected_global": {
            "unique_actionable_cases": 3,
            "information_only_items": 2,
            "hold_groups": 1,
            "block_groups": 1,
            "duplicate_groups": 1,
            "external_mutation": False,
            "decision_authority": "KX108_ONLY",
        },
    }
    truth_manifest = root / "truth_manifest.json"
    _write_json(truth_manifest, truth)
    return EnterpriseSandboxPathsV0(
        root=root,
        mailbox=mailbox,
        documents=documents,
        calendar=calendar,
        truth_manifest=truth_manifest,
    )


def load_enterprise_sandbox_truth_v0(
    paths: EnterpriseSandboxPathsV0,
) -> dict[str, Any]:
    return json.loads(paths.truth_manifest.read_text(encoding="utf-8"))
