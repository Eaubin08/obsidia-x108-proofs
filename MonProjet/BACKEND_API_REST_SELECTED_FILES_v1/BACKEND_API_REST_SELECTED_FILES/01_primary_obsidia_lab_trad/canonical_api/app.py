from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json, os, hashlib

# Import real engine functions (pure)
from core.engine.obsidia_os2.metrics import compute_metrics_core_fixed, decision_act_hold, Metrics

# Phase 6 — Institutional lock
from core.api.security.nonce import check_and_store_nonce
from core.api.security.signature import sign_hash, get_public_key_hex

APP = FastAPI(title="Obsidia API", version="0.2")

AUDIT_PATH = os.path.join(os.path.dirname(__file__), "audit_log.jsonl")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def append_audit(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Append-only hash-chained audit log.
    If client provides deterministic timestamp, the chain is replayable.
    """
    prev_hash = None
    if os.path.exists(AUDIT_PATH):
        with open(AUDIT_PATH, "rb") as f:
            # read last non-empty line
            lines = f.read().splitlines()
            for line in reversed(lines):
                if line.strip():
                    try:
                        prev_hash = json.loads(line.decode("utf-8")).get("entry_hash")
                    except Exception:
                        prev_hash = None
                    break
    entry["prev_hash"] = prev_hash
    payload = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")
    entry_hash = sha256_bytes(payload)
    entry["entry_hash"] = entry_hash
    with open(AUDIT_PATH, "ab") as f:
        f.write(json.dumps(entry, ensure_ascii=False).encode("utf-8") + b"\n")
    return entry

class MetricsIn(BaseModel):
    T_mean: float
    H_score: float
    A_score: float
    S: float

class DecisionRequest(BaseModel):
    # Option A: provide matrix + core nodes to compute metrics
    W_full: Optional[List[List[float]]] = Field(default=None, description="Full adjacency/weight matrix")
    core_nodes: Optional[List[int]] = Field(default=None, description="Indices of core nodes")
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 0.5

    # Option B: provide metrics directly
    metrics: Optional[MetricsIn] = None

    # Decision threshold
    theta_S: float = 0.25

    # Phase 6 — Nonce obligatoire (anti-replay)
    nonce: str

    # Optional audit metadata
    request_id: Optional[str] = None
    client_time: Optional[str] = Field(default=None, description="ISO timestamp provided by client for deterministic logs")
    tags: Optional[Dict[str, str]] = None

class DecisionResponse(BaseModel):
    decision: str
    theta_S: float
    metrics: MetricsIn
    audit: Optional[Dict[str, Any]] = None

@APP.post("/v1/decision", response_model=DecisionResponse)
def v1_decision(req: DecisionRequest):
    # Phase 6 — Anti-replay: vérifier et stocker le nonce
    try:
        check_and_store_nonce(req.nonce)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Build metrics
    if req.metrics is not None:
        m = Metrics(req.metrics.T_mean, req.metrics.H_score, req.metrics.A_score, req.metrics.S)
    else:
        if req.W_full is None or req.core_nodes is None:
            raise HTTPException(status_code=400, detail="Provide either metrics or (W_full + core_nodes).")
        m = compute_metrics_core_fixed(req.W_full, req.core_nodes, alpha=req.alpha, beta=req.beta, gamma=req.gamma)

    decision = decision_act_hold(m, theta_S=req.theta_S)

    audit_entry = {
        "request_id": req.request_id,
        "client_time": req.client_time,
        "nonce": req.nonce,
        "theta_S": req.theta_S,
        "decision": decision,
        "metrics": {"T_mean": m.T_mean, "H_score": m.H_score, "A_score": m.A_score, "S": m.S},
        "tags": req.tags or {},
    }
    audit = append_audit(audit_entry)

    # Phase 6 — Signature ED25519 sur entry_hash
    signature = sign_hash(audit["entry_hash"])
    audit["signature"] = signature
    audit["public_key"] = get_public_key_hex()

    return DecisionResponse(
        decision=decision,
        theta_S=req.theta_S,
        metrics=MetricsIn(T_mean=m.T_mean, H_score=m.H_score, A_score=m.A_score, S=m.S),
        audit=audit,
    )

@APP.get("/health")
def health():
    return {"ok": True}
