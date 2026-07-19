# api_server/attestation.py
from __future__ import annotations
import os, json, hashlib, datetime, pathlib
from typing import Dict, Any, Optional

STORE_DIR = pathlib.Path(os.getenv("OBSIDIA_STORE_DIR", "api_store"))
ATTEST_DIR = pathlib.Path(os.getenv("OBSIDIA_ATTEST_DIR", str(STORE_DIR / "attestations")))
ATTEST_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_LOG = STORE_DIR / "audit.log"
AUDIT_CHAIN = STORE_DIR / "audit.chain"

def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _utc_day() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _read_prev_attestation_hash() -> str:
    latest = sorted(ATTEST_DIR.glob("attestation_*.json"))
    if not latest:
        return "0" * 64
    last = latest[-1]
    try:
        obj = json.loads(last.read_text(encoding="utf-8"))
        return obj.get("attestation_hash", "0"*64)
    except Exception:
        return "0" * 64

def build_attestation() -> Dict[str, Any]:
    if not AUDIT_LOG.exists() or not AUDIT_CHAIN.exists():
        raise RuntimeError("audit.log/audit.chain missing; generate some traffic first")

    payload = {
        "ts_utc": _utc_now(),
        "day": _utc_day(),
        "audit_log_sha256": sha256_file(AUDIT_LOG),
        "audit_chain_sha256": sha256_file(AUDIT_CHAIN),
        "prev_attestation_hash": _read_prev_attestation_hash(),
        "kernel_version": os.getenv("OBSIDIA_KERNEL_VERSION", ""),
        "gateway_version": os.getenv("OBSIDIA_GATEWAY_VERSION", ""),
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload["attestation_hash"] = sha256_bytes(raw)
    return payload

def write_attestation(att: Dict[str, Any], signature_b64: Optional[str], public_key_pem: Optional[str]) -> pathlib.Path:
    out = dict(att)
    if signature_b64:
        out["signature_b64"] = signature_b64
    if public_key_pem:
        out["public_key_pem"] = public_key_pem

    fn = ATTEST_DIR / f"attestation_{att['day']}_{att['attestation_hash'][:12]}.json"
    fn.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    return fn
