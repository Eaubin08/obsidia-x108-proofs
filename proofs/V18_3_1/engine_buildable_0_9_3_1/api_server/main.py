from __future__ import annotations

from api_server.security import enforce_auth, mint_jwt, check_login, verify_hmac_signature
from api_server.audit_log import append_audit
import os
from fastapi import Header, HTTPException, Request as FastAPIRequest

_API_KEY = os.getenv("OBSIDIA_API_KEY", "").strip()

def _require_api_key(x_api_key: str | None):
    if not _API_KEY:
        return
    if not x_api_key or x_api_key.strip() != _API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


import os
import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from unified_interface.pipeline import run as unified_run
from obsidia_kernel.contract import result_to_dict

STORE_DIR = os.getenv("OBSIDIA_STORE_DIR", os.path.join(os.path.dirname(__file__), "..", "api_store"))
os.makedirs(STORE_DIR, exist_ok=True)

app = FastAPI(
    title="Obsidia Decision Gateway",
    version=os.getenv("OBSIDIA_API_VERSION", "v1"),
    description="Single governance interface: PROPOSE/ACTION -> BLOCK/HOLD/ACT + audit.",
)

def _store(trace_id: str, request_payload: Dict[str, Any], result_dict: Dict[str, Any]) -> None:
    path = os.path.join(STORE_DIR, f"{trace_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"request": request_payload, "result": result_dict}, f, indent=2)

@app.post("/v1/decision")
def decision(payload: Dict[str, Any]):
    # Unified pipeline returns Result dataclass
    res = unified_run(payload)
    out = result_to_dict(res)
    trace_id = out.get("meta", {}).get("trace_id")
    if trace_id:
        _store(trace_id, payload, out)
    return JSONResponse(out)

@app.get("/v1/replay/{trace_id}")
def replay(trace_id: str):
    path = os.path.join(STORE_DIR, f"{trace_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="trace_id not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
def health():
    res = {"status": "ok"}
    append_audit({'trace_id': res.get('meta',{}).get('trace_id','-'),'decision': res.get('decision'),'path': res.get('audit',{}).get('path',[])})
    return res

@app.post("/auth/token")
async def token(username: str = Form(...), password: str = Form(...)):
    if not check_login(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": mint_jwt(sub=username), "token_type": "bearer"}

@app.middleware("http")
async def obsidia_hmac_middleware(request: FastAPIRequest, call_next):
    # Only protect API endpoints (skip docs/health)
    path = request.url.path
    if path.startswith("/v1/") or path.startswith("/auth/"):
        body = await request.body()
        ts = request.headers.get("X-Obsidia-Timestamp")
        sig = request.headers.get("X-Obsidia-Signature")
        nonce = request.headers.get("X-Obsidia-Nonce")
        # If OBSIDIA_HMAC_SECRET is set, this enforces signing + anti-replay
        verify_hmac_signature(body, ts, sig, nonce)
    response = await call_next(request)
    return response


@app.get("/v1/audit/chain")
async def audit_chain(x_api_key: str | None = Header(default=None), authorization: str | None = Header(default=None)):
    enforce_auth(x_api_key, authorization)
    # Return last 200 chain entries
    import os
    store_dir = os.getenv("OBSIDIA_STORE_DIR", "api_store")
    chain_path = os.getenv("OBSIDIA_AUDIT_CHAIN", os.path.join(store_dir, "audit.chain"))
    if not os.path.exists(chain_path):
        return {"entries": []}
    with open(chain_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    tail = lines[-200:]
    return {"entries": tail}
