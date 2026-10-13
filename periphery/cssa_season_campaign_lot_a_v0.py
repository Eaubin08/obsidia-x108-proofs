"""CSSA Lot A: coherent season/administration synthetic campaign, no effects.

Only canonical source evidence and issue proposals are emitted. No committed
CRM/TASK/FOLLOW-UP or KX108 authorization is fabricated.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping


def _sha(x):
    return sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def run_cssa_season_campaign(events: list[Mapping[str, object]]) -> dict:
    if not isinstance(events, list) or len(events) > 2000:
        raise ValueError("CSSA_A_EVENTS_INVALID")
    ids = set()
    schedule = {}
    owners = {}
    reports = []
    seen_conflicts = set()
    for event in events:
        if not isinstance(event, Mapping):
            raise ValueError("CSSA_A_EVENT_INVALID")
        key, kind, owner, slot = [event.get(x) for x in ("id", "kind", "owner", "slot")]
        if (not isinstance(key, str) or not key or key in ids
                or kind not in ("MATCH", "DEADLINE", "STAFF", "PROCUREMENT", "COMMUNICATION")
                or not isinstance(owner, str) or not isinstance(slot, str)):
            raise ValueError("CSSA_A_EVENT_IDENTITY_OR_SHAPE_INVALID")
        ids.add(key)
        issues = []
        if not event.get("source_ref"):
            issues.append("SOURCE_UNPROVEN")
        if not owner:
            issues.append("OWNER_UNKNOWN")
        if event.get("owner_available") is False:
            issues.append("OWNER_UNAVAILABLE")
        if event.get("delegated_to") and not event.get("delegation_proven"):
            issues.append("DELEGATION_UNPROVEN")
        if not slot:
            issues.append("SLOT_UNKNOWN")
        if event.get("deadline_known") is False:
            issues.append("DEADLINE_UNKNOWN")
        budget, limit = event.get("cost_eur"), event.get("budget_eur")
        if budget is not None or limit is not None:
            if (type(budget) not in (int, float) or type(limit) not in (int, float)
                    or budget < 0 or limit < 0):
                issues.append("BUDGET_UNVERIFIED")
            elif budget > limit:
                issues.append("BUDGET_EXCEEDED")
        resource = event.get("resource")
        if resource:
            if not isinstance(resource, str):
                raise ValueError("CSSA_A_RESOURCE_INVALID")
            pair = (slot, resource)
            if pair in schedule:
                issues.append("RESOURCE_COLLISION_WITH:" + schedule[pair])
                seen_conflicts.add(tuple(sorted((key, schedule[pair]))))
            else:
                schedule[pair] = key
        if kind == "COMMUNICATION" and event.get("publication_facts_proven") is not True:
            issues.append("PUBLICATION_FACTS_UNPROVEN")
        if kind == "DEADLINE" and event.get("regulatory_basis_proven") is not True:
            issues.append("REGULATORY_BASIS_UNPROVEN")
        if event.get("contradicted") is True:
            issues.append("SOURCE_CONTRADICTION")
        if slot and owner:
            owner_slot = (owner, slot)
            if owner_slot in owners:
                issues.append("OWNER_COLLISION_WITH:" + owners[owner_slot])
            else:
                owners[owner_slot] = key
        # A risk in the record is not an instruction to decide or dispatch.
        reports.append({
            "id": key,
            "kind": kind,
            "source_hash": _sha(dict(event)),
            "issues": sorted(set(issues)),
            "status": "BLOCK" if issues else "HOLD",
            "proposal": "REVIEW_BLOCKERS" if issues else "HUMAN_REVIEW_REQUIRED",
            "kx108_decision": None,
            "external_actions": [],
        })
    report = {
        "schema": "CSSA_SEASON_LOT_A_SYNTHETIC_V0",
        "cases": reports,
        "totals": {
            "events": len(reports),
            "held": sum(x["status"] == "HOLD" for x in reports),
            "blocked": sum(x["status"] == "BLOCK" for x in reports),
            "resource_collision_pairs": len(seen_conflicts),
        },
        "status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "external_actions": [],
        "native_store_writes": False,
        "provider_writes": False,
        "execution_proven": False,
        "historical_f3f_904_claimed": False,
    }
    return {"report": report, "receipt_sha256": _sha(report)}


def verify_cssa_season_campaign(bundle: Mapping[str, object]) -> bool:
    if not isinstance(bundle, Mapping) or set(bundle) != {"report", "receipt_sha256"}:
        return False
    report = bundle["report"]
    if not isinstance(report, dict):
        return False
    try:
        return (bundle["receipt_sha256"] == _sha(report)
                and report["schema"] == "CSSA_SEASON_LOT_A_SYNTHETIC_V0"
                and report["status"] == "HOLD"
                and report["decision_authority"] == "KX108_ONLY"
                and report["kx108_decision"] is None
                and report["human_approval"] is None
                and report["external_actions"] == []
                and report["native_store_writes"] is False
                and report["provider_writes"] is False
                and report["execution_proven"] is False
                and all(case["status"] in ("HOLD", "BLOCK")
                        and case["kx108_decision"] is None
                        and case["external_actions"] == []
                        for case in report["cases"]))
    except (KeyError, TypeError, ValueError):
        return False
