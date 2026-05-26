"""
Brody CLI Registry — monitoring endpoint for brody_memory_readonly scripts.
Exposes /api/periphery/monitoring/brody-cli-registry
"""
from __future__ import annotations

import ast, os
from fastapi import APIRouter
from pydantic import BaseModel
from apps.obsidia_api.safe_response import safe_backend_response
from periphery.adapters.bank_adapter import build_bank_action, build_bank_state
from periphery.adapters.gps_adapter import build_gps_action, build_gps_state
from periphery.adapters.trading_adapter import build_trading_action, build_trading_state
from periphery.hexaflux.ltcu_plus import compute_ltcu_plus
from periphery.hexaflux.transition_mapper import map_hexaflux_transition
from periphery.brody_memory_readonly.session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2 import (
    validate_brody_response, sha256_text as ledger_sha256, canonical_json,
    TRUE_KEYS, FALSE_KEYS, BOUNDARY as LEDGER_BOUNDARY
)
from periphery.brody_memory_readonly.session_trace_ledger.brody_session_trace_ledger_readonly_v1_6_3 import (
    read_pointer, sha256_text as trace_sha256
)

router = APIRouter(prefix="/api/periphery/monitoring", tags=["monitoring"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

BRODY_ROOT = "periphery/brody_memory_readonly"


class AdapterPayload(BaseModel):
    payload: dict = {}


class LTCUPayload(BaseModel):
    signal_id: str = ""
    context_drift: float = 0.0
    temporal_coherence: float = 1.0
    elapsed_steps: int = 1


class TransitionPayload(BaseModel):
    transition_id: str = ""
    from_phase: str = "LATENT"
    to_phase: str = "IGNITION"


class TraceAnalyzePayload(BaseModel):
    response_payload: dict = {}


class HistoricalConvergencePayload(BaseModel):
    session_records: list[dict] = []


def _scan_brody_registry() -> list[dict]:
    """Walk brody_memory_readonly/ and extract CLI registry."""
    entries = []
    for dp, dn, fn in sorted(os.walk(BRODY_ROOT)):
        py_files = [f for f in fn if f.endswith(".py") and not f.startswith("__")]
        ps1_files = [f for f in fn if f.endswith(".ps1")]

        for py_file in py_files:
            full_py = os.path.join(dp, py_file)
            funcs = []
            try:
                raw = open(full_py, encoding="utf-8-sig", errors="ignore").read()
                tree = ast.parse(raw)
                funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                         and not n.name.startswith("_")]
            except Exception:
                pass

            entry = {
                "directory": dp,
                "python_file": py_file,
                "ps1_runners": ps1_files,
                "exposed_functions": funcs[:10],
                "has_argparse": "argparse" in (open(full_py, encoding="utf-8-sig", errors="ignore").read()[:3000]) if os.path.exists(full_py) else False,
                "has_manifest": any(f.startswith("BRODY_") and f.endswith("MANIFEST.json") for f in fn),
                "has_smoke": any("smoke" in f.lower() for f in py_files),
                "integration_status": "NOT_CONNECTED",
            }
            entries.append(entry)
    return entries


@router.get("/brody-cli-registry")
async def brody_cli_registry():
    """Return full registry of brody_memory_readonly scripts."""
    entries = _scan_brody_registry()
    return safe_backend_response({
        "total_directories": len(set(e["directory"] for e in entries)),
        "total_scripts": len(entries),
        "scripts_with_functions": sum(1 for e in entries if e["exposed_functions"]),
        "scripts_with_ps1": sum(1 for e in entries if e["ps1_runners"]),
        "scripts_with_manifest": sum(1 for e in entries if e["has_manifest"]),
        "entries": entries,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/adapters/bank")
async def monitor_bank(payload: AdapterPayload):
    state = build_bank_state(payload.payload)
    action = build_bank_action(payload.payload)
    return safe_backend_response({
        "action": action.to_dict(),
        "state_keys": list(state.__dict__.keys()),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/adapters/gps")
async def monitor_gps(payload: AdapterPayload):
    state = build_gps_state(payload.payload)
    action = build_gps_action(payload.payload)
    return safe_backend_response({
        "action": action.to_dict(),
        "state_keys": list(state.__dict__.keys()),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/adapters/trading")
async def monitor_trading(payload: AdapterPayload):
    state = build_trading_state(payload.payload)
    action = build_trading_action(payload.payload)
    return safe_backend_response({
        "action": action.to_dict(),
        "state_keys": list(state.__dict__.keys()),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/hexaflux/ltcu-plus")
async def monitor_ltcu(payload: LTCUPayload):
    result = compute_ltcu_plus(
        signal_id=payload.signal_id or "ltcu-monitor",
        context_drift=payload.context_drift,
        temporal_coherence=payload.temporal_coherence,
        elapsed_steps=payload.elapsed_steps,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/hexaflux/transition-map")
async def monitor_transition(payload: TransitionPayload):
    result = map_hexaflux_transition(
        transition_id=payload.transition_id or "hexa-monitor",
        from_phase=payload.from_phase,
        to_phase=payload.to_phase,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/brody-trace-analyze")
async def monitor_brody_trace_analyze(payload: TraceAnalyzePayload):
    """Validate semantic structure of a Brody response payload against boundary invariants."""
    resp = payload.response_payload or {}
    
    try:
        validate_brody_response(resp)
        validation_result = {
            "status": "BOUNDARY_PASS",
            "true_keys_valid": {k: resp.get(k, "MISSING") for k in TRUE_KEYS},
            "false_keys_valid": {k: resp.get(k, "MISSING") for k in FALSE_KEYS},
            "decision_authority": resp.get("decision_authority", "UNSET"),
        }
    except RuntimeError as exc:
        validation_result = {
            "status": "BOUNDARY_VIOLATION",
            "error": str(exc),
            "true_keys_check": {k: resp.get(k, "MISSING") for k in TRUE_KEYS if resp.get(k) is not True},
            "false_keys_check": {k: resp.get(k, "MISSING") for k in FALSE_KEYS if resp.get(k) is not False},
            "decision_authority": resp.get("decision_authority", "UNSET"),
        }

    return safe_backend_response({
        "analysis_type": "BRODY_TRACE_ANALYZE",
        "validation": validation_result,
        "response_sha256": ledger_sha256(canonical_json(resp) if resp else "{}"),
        "required_true_keys": TRUE_KEYS,
        "required_false_keys": FALSE_KEYS,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/brody-historical-convergence")
async def monitor_brody_historical_convergence(payload: HistoricalConvergencePayload):
    """Compute semantic drift delta across past session records using hash-chain analysis."""
    records = payload.session_records or []

    if not records:
        return safe_backend_response({
            "analysis_type": "BRODY_HISTORICAL_CONVERGENCE",
            "status": "EMPTY_RECORDS",
            "record_count": 0,
            "chain_integrity": None,
            "drift_analysis": "NO_DATA",
            **_BOUNDARY,
        }, source="REAL_BACKEND")

    # Hash-chain integrity check
    chain_breaks = []
    prev_hash = "GENESIS"
    for i, rec in enumerate(records):
        expected_prev = rec.get("previous_event_hash", "GENESIS")
        if i > 0 and prev_hash != expected_prev:
            chain_breaks.append({
                "index": i,
                "expected": prev_hash,
                "actual": expected_prev,
                "gap": "CHAIN_BREAK",
            })
        # Compute record hash from content
        content = {k: v for k, v in rec.items() if k not in ("event_hash",)}
        computed = ledger_sha256(prev_hash + canonical_json(content))
        rec_event = rec.get("event_hash", "")
        if prev_hash == expected_prev and computed != rec_event:
            chain_breaks.append({
                "index": i,
                "chain_hash": prev_hash,
                "computed": computed,
                "stored": rec_event,
                "gap": "HASH_MISMATCH",
            })
        prev_hash = rec_event or prev_hash

    # Semantic drift: compare first/last record sha256 diff
    semantic_drift = 0.0
    if len(records) >= 2:
        first_resp = records[0].get("response_md", "")
        last_resp = records[-1].get("response_md", "")
        drift_hex = ledger_sha256(first_resp) != ledger_sha256(last_resp)
        semantic_drift = 1.0 if drift_hex else 0.0

    chain_status = "INTACT" if not chain_breaks else "DEGRADED"
    if len(chain_breaks) >= 3:
        chain_status = "BROKEN"

    return safe_backend_response({
        "analysis_type": "BRODY_HISTORICAL_CONVERGENCE",
        "record_count": len(records),
        "chain_integrity": chain_status,
        "chain_breaks": len(chain_breaks),
        "chain_break_details": chain_breaks[:5],
        "semantic_drift_delta": semantic_drift,
        "last_event_hash": prev_hash,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.get("/brody-cli-registry")
async def brody_cli_registry():
    """Return full registry of brody_memory_readonly scripts."""
    entries = _scan_brody_registry()
    return safe_backend_response({
        "total_directories": len(set(e["directory"] for e in entries)),
        "total_scripts": len(entries),
        "scripts_with_functions": sum(1 for e in entries if e["exposed_functions"]),
        "scripts_with_ps1": sum(1 for e in entries if e["ps1_runners"]),
        "scripts_with_manifest": sum(1 for e in entries if e["has_manifest"]),
        "entries": entries,
        **_BOUNDARY,
    }, source="REAL_BACKEND")
