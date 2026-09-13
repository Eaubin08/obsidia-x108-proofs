from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPTS_DIR = ROOT / "artifacts" / "gps_v01_receipts"
OUT = ROOT / "artifacts" / "gps_v01_p4_07_receipt_manifest.json"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    ticket = data.get("receipt", {}).get("os3_ticket", {})
    return {
        "file": str(path.relative_to(ROOT)),
        "scenario": data.get("scenario"),
        "verdict": data.get("verdict"),
        "source": data.get("source"),
        "ticket_id": ticket.get("ticket_id"),
        "x108_gate": ticket.get("x108_gate"),
        "reason_code": ticket.get("reason_code"),
        "merkle_root": ticket.get("merkle_root"),
        "replay_status": ticket.get("replay_status"),
        "file_sha256": _sha256_bytes(raw),
    }


def build_manifest() -> dict[str, Any]:
    receipts = [_load_receipt(path) for path in sorted(RECEIPTS_DIR.glob("*_gps_receipt.json"))]
    unsigned = {
        "claim_scope": "P4_07_DEMO_RECEIPT_MANIFEST_NOT_RFC3161_NOT_PRODUCTION_CERTIFICATION",
        "domain": "gps_defense_aviation",
        "receipt_count": len(receipts),
        "receipts": receipts,
        "replay_status_policy": "preserve_NOT_RUN_until_real_replay_verifier_mutates_status",
    }
    canonical = json.dumps(unsigned, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    key = os.environ.get("OBSIDIA_P4_07_DEMO_SIGNING_KEY", "OBSIDIA_GPS_V01_DEMO_LOCAL_KEY").encode("utf-8")
    signature = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    return {
        **unsigned,
        "signature_kind": "LOCAL_HMAC_SHA256_DEMO_NOT_RFC3161_NOT_PRODUCTION",
        "signature_env_key": "OBSIDIA_P4_07_DEMO_SIGNING_KEY",
        "manifest_sha256": _sha256_bytes(canonical),
        "manifest_hmac_sha256": signature,
    }


def main() -> int:
    manifest = build_manifest()
    OUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"{OUT} receipts={manifest['receipt_count']} signature_kind={manifest['signature_kind']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
