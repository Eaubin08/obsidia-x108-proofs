"""LOT A multi-case CSSA season campaign across the existing sovereign sandbox.

Preflight the *whole* synthetic batch before any sandbox mutation. Cases with
issues cannot reach native intake; clean cases require explicit fixture opt-in.
Each allowed case receives a separate isolated root to avoid cross-case leakage.
No real provider, real approval, or live action.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from periphery.cssa_season_campaign_lot_a_v0 import (
    run_cssa_season_campaign, verify_cssa_season_campaign,
)
from periphery.cssa_sovereign_sandbox_lot_a_v0 import (
    run_cssa_sovereign_sandbox_lot_a,
)


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def run_cssa_full_lot_a_campaign(
    events: list[dict], *, root: Path,
    simulated_approved_ids: tuple[str, ...] = (),
) -> dict:
    """Run linked preflight + multiple native/Universal sandbox journeys.

    Approval IDs here are explicit *synthetic test controls*, never human proof.
    Only proven synthetic regulatory DEADLINE cases can reach the existing rail.
    """
    if not isinstance(simulated_approved_ids, tuple):
        raise ValueError("CSSA_FULL_A_APPROVAL_LIST_INVALID")
    if len(simulated_approved_ids) != len(set(simulated_approved_ids)):
        raise ValueError("CSSA_FULL_A_DUPLICATE_APPROVAL")
    if any(not isinstance(x, str) or not x for x in simulated_approved_ids):
        raise ValueError("CSSA_FULL_A_APPROVAL_ID_INVALID")
    root = Path(root)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError("CSSA_FULL_A_ROOT_NOT_EMPTY")
    checked = run_cssa_season_campaign(events)
    if not verify_cssa_season_campaign(checked):
        raise ValueError("CSSA_FULL_A_CAMPAIGN_PRECHECK_INVALID")
    index = {case["id"]: case for case in checked["report"]["cases"]}
    if set(simulated_approved_ids) - index.keys():
        raise ValueError("CSSA_FULL_A_APPROVAL_NOT_IN_BATCH")
    reports = []
    for event in events:
        case = index[event["id"]]
        entry = {
            "id": event["id"], "kind": event["kind"],
            "source_hash": case["source_hash"],
            "preflight_status": case["status"], "issues": case["issues"],
            "status": case["status"], "kx108_gate": None,
            "native_mutation_count": 0, "receipt_hash": None,
            "replay_ok": False, "duplicate_blocked": False,
            "real_external_effect": False,
        }
        if case["issues"]:
            entry["reason"] = "CSSA_DOMAIN_PRECHECK_BLOCK"
        elif event["id"] not in simulated_approved_ids:
            entry["reason"] = "NO_SIMULATED_OPERATOR_APPROVAL"
        elif event["kind"] != "DEADLINE":
            entry["reason"] = "CSSA_NATIVE_SURFACE_NOT_PROVEN_FOR_KIND"
        elif (event.get("regulatory_basis_proven") is not True
              or not isinstance(event.get("due_at"), str)
              or not event["due_at"].endswith("+00:00")):
            entry["reason"] = "CSSA_DEADLINE_CANONICALIZATION_UNPROVEN"
        else:
            event_root = root / ("case-" + _hash(event)[:24])
            outcome = run_cssa_sovereign_sandbox_lot_a(
                [event], root=event_root, simulate_operator_approval=True,
            )
            if outcome["status"] != "CSSA_LOT_A_SANDBOX_E2E_PROVEN":
                raise ValueError("CSSA_FULL_A_NATIVE_EXECUTION_NOT_PROVEN")
            proof = outcome["execution"]
            entry.update({
                "status": "SANDBOX_EXECUTED",
                "reason": "TEST_ONLY_GOVERNED_SANDBOX",
                "kx108_gate": proof["kx108_gate"],
                "native_mutation_count": outcome["intake_mutations"],
                "receipt_hash": proof["execution_receipt_hash"],
                "replay_ok": proof["execution_replay_ok"],
                "duplicate_blocked": proof["duplicate_status"] == "BLOCKED"
                                    and proof["duplicate_adapter_called"] is False,
                "real_external_effect": outcome["real_external_effect"],
            })
        reports.append(entry)
    totals = {
        "events": len(reports),
        "blocked": sum(x["status"] == "BLOCK" for x in reports),
        "held": sum(x["status"] == "HOLD" for x in reports),
        "sandbox_executed": sum(x["status"] == "SANDBOX_EXECUTED" for x in reports),
        "replayed": sum(x["replay_ok"] for x in reports),
        "duplicate_blocked": sum(x["duplicate_blocked"] for x in reports),
    }
    report = {
        "schema": "CSSA_FULL_LOT_A_CAMPAIGN_V0",
        "status": "SYNTHETIC_SANDBOX_ONLY",
        "cases": reports, "totals": totals,
        "preflight_receipt_sha256": checked["receipt_sha256"],
        "decision_authority": "KX108_ONLY",
        "approval_type": "SIMULATED_TEST_OPERATOR_ONLY",
        "external_actions": [],
        "real_external_effect": False,
        "network_calls_real": 0,
        "f3f_904_events_replayed": False,
        "f3g_11_roles_closed": False,
    }
    return {"report": report, "receipt_sha256": _hash(report)}


def verify_cssa_full_lot_a_campaign(bundle: dict) -> bool:
    if not isinstance(bundle, dict) or set(bundle) != {"report", "receipt_sha256"}:
        return False
    report = bundle["report"]
    try:
        cases = report["cases"]
        totals = report["totals"]
        return (
            bundle["receipt_sha256"] == _hash(report)
            and report["schema"] == "CSSA_FULL_LOT_A_CAMPAIGN_V0"
            and report["decision_authority"] == "KX108_ONLY"
            and report["external_actions"] == []
            and report["real_external_effect"] is False
            and report["network_calls_real"] == 0
            and len(cases) == totals["events"]
            and totals["replayed"] == totals["sandbox_executed"]
            and totals["duplicate_blocked"] == totals["sandbox_executed"]
            and all(c["status"] in ("BLOCK", "HOLD", "SANDBOX_EXECUTED")
                    and c["real_external_effect"] is False
                    and (c["status"] != "SANDBOX_EXECUTED" or
                         (c["kx108_gate"] == "ALLOW" and c["replay_ok"]
                          and c["duplicate_blocked"] and c["receipt_hash"]))
                    for c in cases)
        )
    except (TypeError, KeyError, ValueError):
        return False
