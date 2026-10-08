"""CSSA-only cross-component offline audit. No native apply, send, or dispatch."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping

from periphery.cssa_synthetic_intake_v0 import ingest_synthetic_batch
from periphery.cssa_admin_e2e_synthetic_v0 import build_cssa_admin_case, verify_cssa_admin_case
from periphery.cssa_native_crm_candidate_v0 import prepare_cssa_supporter_crm
from periphery.cssa_calendar_email_candidates_v0 import prepare_cssa_followup_candidates


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def build_cssa_cross_component_batch(
    messages: list[Mapping[str, str]],
    *,
    explicit_followups: Mapping[str, str] | None = None,
) -> dict:
    """Link synthetic intake, native candidate and email/calendar suggestions.

    Identity collisions fail closed across the entire collision group. A date
    can only be associated with a non-conflicting source message identifier.
    """
    intake = ingest_synthetic_batch(messages)
    conflicts = set(intake["conflicts"])
    dates = dict(explicit_followups or {})
    if any(not isinstance(key, str) or not isinstance(val, str)
           for key, val in dates.items()):
        raise ValueError("CSSA_INVALID_FOLLOWUP_BINDING")
    unique = {}
    for message in messages:
        mid = message["message_id"].strip()
        if mid not in unique:
            unique[mid] = message
    if any(mid not in unique or mid in conflicts for mid in dates):
        raise ValueError("CSSA_FOLLOWUP_SOURCE_NOT_UNAMBIGUOUS")

    results = []
    for candidate in intake["candidates"]:
        mid = candidate["message_id"]
        if mid in conflicts:
            continue
        message = unique[mid]
        admin = build_cssa_admin_case(message)
        if not verify_cssa_admin_case(admin):
            raise ValueError("CSSA_E2E_RECEIPT_INVALID")
        crm = prepare_cssa_supporter_crm(dict(message))
        calendar_email = prepare_cssa_followup_candidates(
            dict(message), requested_followup_at=dates.get(mid))
        fingerprint = candidate["source_fingerprint"]
        if (admin["case"]["input"]["source_fingerprint"] != fingerprint
                or calendar_email["source_sha256"] != fingerprint
                or crm["status"] != "HOLD"
                or calendar_email["status"] != "HOLD"
                or crm["kx108_decision"] is not None
                or calendar_email["kx108_decision"] is not None
                or crm["external_actions"] != []
                or calendar_email["external_actions"] != []):
            raise ValueError("CSSA_CROSS_COMPONENT_BOUNDARY_MISMATCH")
        if candidate["category_candidate"] == "SUPPORTER_REQUEST":
            mutation = crm["crm_mutation"]
            request = crm["task_request"]
            if (mutation is None or request is None
                    or mutation.payload["fields"]["source_sha256"] != fingerprint
                    or mutation.payload["fields"]["proposed_task_id"]
                    != request["connector_args"]["entity_id"]
                    or crm["crm_request"]["allowed_to_act"] is not False
                    or request["allowed_to_act"] is not False):
                raise ValueError("CSSA_CROSS_COMPONENT_LINK_MISMATCH")
        elif (crm["crm_mutation"] is not None
              or calendar_email["calendar_event"] is not None
              or calendar_email["email_draft"] is not None):
            raise ValueError("CSSA_NON_SUPPORTER_PROPOSAL_MISMATCH")
        results.append({
            "message_id": mid,
            "source_sha256": fingerprint,
            "category": candidate["category_candidate"],
            "admin_case_sha256": admin["receipt"]["case_sha256"],
            "crm_candidate_id": (
                crm["crm_mutation"].entity_id if crm["crm_mutation"] is not None else None
            ),
            "task_candidate_id": (
                crm["task_request"]["connector_args"]["entity_id"]
                if crm["task_request"] is not None else None
            ),
            "calendar_candidate": calendar_email["calendar_event"],
            "email_draft_candidate": calendar_email["email_draft"],
            "status": "HOLD",
            "external_actions": [],
        })
    report = {
        "schema": "CSSA_CROSS_COMPONENT_OFFLINE_V0",
        "cases": results,
        "duplicate_ids": intake["duplicates"],
        "conflicting_ids": sorted(conflicts),
        "status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "external_actions": [],
        "execution_proven": False,
        "historical_evidence_replaced": False,
    }
    return {"report": report, "audit_sha256": _hash(report)}


def verify_cssa_cross_component_batch(bundle: Mapping[str, object]) -> bool:
    if not isinstance(bundle, Mapping) or set(bundle) != {"report", "audit_sha256"}:
        return False
    report = bundle["report"]
    if not isinstance(report, dict):
        return False
    try:
        return (
            bundle["audit_sha256"] == _hash(report)
            and report["schema"] == "CSSA_CROSS_COMPONENT_OFFLINE_V0"
            and report["status"] == "HOLD"
            and report["decision_authority"] == "KX108_ONLY"
            and report["kx108_decision"] is None
            and report["human_approval"] is None
            and report["external_actions"] == []
            and report["execution_proven"] is False
            and report["historical_evidence_replaced"] is False
            and all(case["status"] == "HOLD" and case["external_actions"] == []
                    for case in report["cases"])
        )
    except (KeyError, TypeError, ValueError):
        return False
