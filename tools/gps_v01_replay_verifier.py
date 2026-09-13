from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPTS_DIR = ROOT / "artifacts" / "gps_v01_receipts"
REPORT_PATH = ROOT / "artifacts" / "gps_v01_replay_report.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _non_empty_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


def verify_receipt(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    receipt = data.get("receipt", {})
    ticket = receipt.get("os3_ticket", {})
    domain_state = data.get("domain_state", {})
    nuisances = set(domain_state.get("nuisances", []) or [])

    checks = {
        "claim_scope_is_demo": data.get("claim_scope") == "GPS_V01_DEMO_RUNTIME_RECEIPT_NOT_PRODUCTION_P4_07",
        "receipt_domain_ok": receipt.get("domain") == "gps_defense_aviation",
        "receipt_contract_ok": receipt.get("contract") == "DOMAIN_BRIDGE_ONLY",
        "receipt_authority_ok": receipt.get("decision_authority") == "KX108_ONLY",
        "connector_non_sovereign": receipt.get("connector_decides") is False,
        "local_signature_present": _non_empty_hash(receipt.get("signed_decision_receipt_sha256")),
        "ticket_present": bool(ticket),
        "ticket_domain_ok": ticket.get("domain") == "gps_defense_aviation",
        "ticket_gate_matches_verdict": ticket.get("x108_gate") == data.get("verdict"),
        "ticket_hash_chain_present": all(
            _non_empty_hash(ticket.get(k))
            for k in ("input_hash", "output_hash", "trace_hash", "merkle_root")
        ),
        "ticket_replay_not_claimed": ticket.get("replay_status") == "NOT_RUN",
    }

    scenario = data.get("scenario") or path.stem.replace("_gps_receipt", "")
    if scenario == "spoof":
        checks["spoof_nuisance_preserved"] = "GPS_SPOOFING" in nuisances
    if scenario == "replay":
        checks["replay_nuisance_preserved"] = "REPLAY_ATTACK" in nuisances

    passed = all(checks.values())
    return {
        "file": str(path.relative_to(ROOT)),
        "scenario": scenario,
        "status": "PASS" if passed else "FAIL",
        "mode": "DRY_RUN_REPLAY_VERIFIER_NOT_PRODUCTION",
        "ticket_id": ticket.get("ticket_id"),
        "x108_gate": ticket.get("x108_gate"),
        "reason_code": ticket.get("reason_code"),
        "merkle_root": ticket.get("merkle_root"),
        "replay_status_observed": ticket.get("replay_status"),
        "checks": checks,
    }


def build_report() -> dict[str, Any]:
    files = sorted(RECEIPTS_DIR.glob("*_gps_receipt.json"))
    results = [verify_receipt(path) for path in files]
    return {
        "status": "PASS" if results and all(r["status"] == "PASS" for r in results) else "FAIL",
        "mode": "DRY_RUN_REPLAY_VERIFIER_NOT_PRODUCTION",
        "claim_boundary": "Does not mutate OS3 replay_status; production replay remains NOT_RUN until a real verifier updates it.",
        "receipts_dir": str(RECEIPTS_DIR.relative_to(ROOT)),
        "receipt_count": len(results),
        "results": results,
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"{REPORT_PATH} status={report['status']} mode={report['mode']} receipts={report['receipt_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
