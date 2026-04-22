# api_server/audit_log.py
from __future__ import annotations
import os, json, hashlib, datetime
from typing import Any, Dict, Optional

STORE_DIR = os.getenv("OBSIDIA_STORE_DIR", "api_store")
AUDIT_LOG = os.getenv("OBSIDIA_AUDIT_LOG", os.path.join(STORE_DIR, "audit.log"))
AUDIT_CHAIN = os.getenv("OBSIDIA_AUDIT_CHAIN", os.path.join(STORE_DIR, "audit.chain"))
os.makedirs(STORE_DIR, exist_ok=True)

def _utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _read_last_hash() -> str:
    if not os.path.exists(AUDIT_CHAIN):
        return "0" * 64
    try:
        with open(AUDIT_CHAIN, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        if not lines:
            return "0" * 64
        return lines[-1].split(" ", 1)[0]
    except Exception:
        return "0" * 64

def append_audit(event: Dict[str, Any]) -> str:
    # Append-only event log + hash chain: h_i = sha256(h_{i-1} || json(event))
    event = dict(event)
    event.setdefault("ts_utc", _utc_now())
    payload = json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")
    prev = _read_last_hash().encode("utf-8")
    h = hashlib.sha256(prev + payload).hexdigest()

    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")
    with open(AUDIT_CHAIN, "a", encoding="utf-8") as f:
        f.write(f"{h} {event.get('trace_id','-')}\n")
    return h
