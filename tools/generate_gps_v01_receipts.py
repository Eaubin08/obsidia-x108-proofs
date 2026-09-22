from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connectors.aviation_robo import (
    build_gps_payload,
    build_replay_attack_payload,
    build_spoofed_gps_payload,
    evaluate_local_gate,
)


OUT_DIR = ROOT / "artifacts" / "gps_v01_receipts"


def _receipt_bundle(name: str, packet: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_local_gate(packet)
    receipt = result.get("receipt", {})
    ticket = receipt.get("os3_ticket", {})
    return {
        "scenario": name,
        "claim_scope": "GPS_V01_DEMO_RUNTIME_RECEIPT_NOT_PRODUCTION_P4_07",
        "verdict": result.get("verdict"),
        "source": result.get("source"),
        "domain": result.get("domain"),
        "domain_state": result.get("ir_payload", {}).get("meta", {}).get("domain_state", {}),
        "receipt": receipt,
        "os3_ticket_summary": {
            "ticket_id": ticket.get("ticket_id"),
            "x108_gate": ticket.get("x108_gate"),
            "reason_code": ticket.get("reason_code"),
            "severity": ticket.get("severity"),
            "merkle_root": ticket.get("merkle_root"),
            "replay_status": ticket.get("replay_status"),
        },
    }


def build_all_receipts() -> dict[str, dict[str, Any]]:
    return {
        "nominal": _receipt_bundle("nominal", build_gps_payload()),
        "spoof": _receipt_bundle("spoof", build_spoofed_gps_payload()),
        "replay": _receipt_bundle("replay", build_replay_attack_payload()),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bundles = build_all_receipts()
    for name, bundle in bundles.items():
        target = OUT_DIR / f"{name}_gps_receipt.json"
        target.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )
        summary = bundle["os3_ticket_summary"]
        print(
            f"{target} verdict={bundle['verdict']} "
            f"ticket={summary['ticket_id']} replay={summary['replay_status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
