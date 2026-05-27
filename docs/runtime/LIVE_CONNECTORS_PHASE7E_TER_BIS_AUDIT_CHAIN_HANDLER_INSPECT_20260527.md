# LIVE_CONNECTORS_PHASE7E_TER_BIS_AUDIT_CHAIN_HANDLER_INSPECT_20260527

Status: READ_ONLY_HANDLER_INSPECTION

## HTTP result
- GET /v1/audit/chain code=500
- body=

## Handler source

### main.py lines 70-110
-   70: 
-   71: @app.middleware("http")
-   72: async def obsidia_hmac_middleware(request: FastAPIRequest, call_next):
-   73:     # Only protect API endpoints (skip docs/health)
-   74:     path = request.url.path
-   75:     if path.startswith("/v1/") or path.startswith("/auth/"):
-   76:         body = await request.body()
-   77:         ts = request.headers.get("X-Obsidia-Timestamp")
-   78:         sig = request.headers.get("X-Obsidia-Signature")
-   79:         nonce = request.headers.get("X-Obsidia-Nonce")
-   80:         # If OBSIDIA_HMAC_SECRET is set, this enforces signing + anti-replay
-   81:         verify_hmac_signature(body, ts, sig, nonce)
-   82:     response = await call_next(request)
-   83:     return response
-   84: 
-   85: 
-   86: @app.get("/v1/audit/chain")
-   87: async def audit_chain(x_api_key: str | None = Header(default=None), authorization: str | None = Header(default=None)):
-   88:     enforce_auth(x_api_key, authorization)
-   89:     # Return last 200 chain entries
-   90:     import os
-   91:     store_dir = os.getenv("OBSIDIA_STORE_DIR", "api_store")
-   92:     chain_path = os.getenv("OBSIDIA_AUDIT_CHAIN", os.path.join(store_dir, "audit.chain"))
-   93:     if not os.path.exists(chain_path):
-   94:         return {"entries": []}
-   95:     with open(chain_path, "r", encoding="utf-8") as f:
-   96:         lines = [ln.strip() for ln in f.readlines() if ln.strip()]
-   97:     tail = lines[-200:]
-   98:     return {"entries": tail}

### audit_log.py
-    1: # api_server/audit_log.py
-    2: from __future__ import annotations
-    3: import os, json, hashlib, datetime
-    4: from typing import Any, Dict, Optional
-    5: 
-    6: STORE_DIR = os.getenv("OBSIDIA_STORE_DIR", "api_store")
-    7: AUDIT_LOG = os.getenv("OBSIDIA_AUDIT_LOG", os.path.join(STORE_DIR, "audit.log"))
-    8: AUDIT_CHAIN = os.getenv("OBSIDIA_AUDIT_CHAIN", os.path.join(STORE_DIR, "audit.chain"))
-    9: os.makedirs(STORE_DIR, exist_ok=True)
-   10: 
-   11: def _utc_now():
-   12:     return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
-   13: 
-   14: def _read_last_hash() -> str:
-   15:     if not os.path.exists(AUDIT_CHAIN):
-   16:         return "0" * 64
-   17:     try:
-   18:         with open(AUDIT_CHAIN, "r", encoding="utf-8") as f:
-   19:             lines = [ln.strip() for ln in f.readlines() if ln.strip()]
-   20:         if not lines:
-   21:             return "0" * 64
-   22:         return lines[-1].split(" ", 1)[0]
-   23:     except Exception:
-   24:         return "0" * 64
-   25: 
-   26: def append_audit(event: Dict[str, Any]) -> str:
-   27:     # Append-only event log + hash chain: h_i = sha256(h_{i-1} || json(event))
-   28:     event = dict(event)
-   29:     event.setdefault("ts_utc", _utc_now())
-   30:     payload = json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")
-   31:     prev = _read_last_hash().encode("utf-8")
-   32:     h = hashlib.sha256(prev + payload).hexdigest()
-   33: 
-   34:     with open(AUDIT_LOG, "a", encoding="utf-8") as f:
-   35:         f.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")
-   36:     with open(AUDIT_CHAIN, "a", encoding="utf-8") as f:
-   37:         f.write(f"{h} {event.get('trace_id','-')}\n")
-   38:     return h

## Process 8001
- pid=17116 process=wslrelay path=C:\Program Files\WSL\wslrelay.exe command= --mode 1 --vm-id {f19e595e-e2e8-45bb-af37-9e01cb5ec9bb} --handle 1624
- pid=17252 process=com.docker.backend path=C:\Program Files\Docker\Docker\resources\com.docker.backend.exe command="C:\Program Files\Docker\Docker\resources\com.docker.backend.exe" services

## Environment
- OBSIDIA_AUDIT_CHAIN=
- OBSIDIA_STORE_DIR=
- OBSIDIA_API_KEY=

## Audit files found
- NO_AUDIT_CHAIN_OR_LOG_FILE_FOUND_IN_TARGET_SCAN

## Boundary
- Diagnostic only.
- No POST executed.
- No token request sent.
- No decision request sent.
- No mutation.
- KX108_ONLY remains sole decision authority.

## Next
- If handler reads a missing audit.chain directly, patch candidate must be explicit fallback/read-only empty chain.
- If process path points outside target repo, inspect that service source/logs before patch.
- Do not patch before confirming exact exception.