"""X108 routes — readonly status, ingress, cognitive & math endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

from dataclasses import asdict

from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
from periphery.cognitive_trees.shazam_cognitif import shazam_cognitif
from periphery.cognitive_trees.dominant_trees import find_dominant_trees
from periphery.math_core.governed_state import GovernedStateVector, DecisionEnvelopeTheta
from periphery.math_core.lyapunov import compute_lyapunov, LyapunovResult
from periphery.math_core.proof_of_governance import proof_of_governance
from periphery.blockchain.oracle_freshness_gate import evaluate_oracle_freshness
from periphery.timeverse import run_timeverse
from periphery.common import ActionCandidate
from periphery.math_core.multi_agent_consensus import multi_agent_consensus
from periphery.consciousness_regimes.regime_classifier import classify_regime
from periphery.memory.memory_candidate_ledger import append_memory_candidate, read_memory_candidates
from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_source_types import MemorySourceType
from periphery.math_core.trust_path import build_trust_path
from periphery.brody_memory_readonly.memory_replay_query_regression_readonly.brody_memory_replay_query_regression_readonly_v1 import classify_record as _classify_replay_record, assert_boundary as _assert_replay_boundary, DEFAULT_QUERIES as _REPLAY_DEFAULT_QUERIES
from periphery.brody_memory_readonly.session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2 import validate_brody_response as _validate_ledger_response
from periphery.brody_memory_readonly.session_trace_ledger.brody_session_trace_ledger_readonly_v1_6_3 import BOUNDARY as _TRACE_LEDGER_BOUNDARY

router = APIRouter(prefix="/api/x108", tags=["x108"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}


class ActivationPayload(BaseModel):
    vector_id: str
    activations: list[float] = Field(default_factory=lambda: [0.1] * 34)
    theta: float = 0.15


class LyapunovPayload(BaseModel):
    action_id: str
    I: float = 1.0
    delta_E: float = 0.0
    delta_C: float = 0.0
    V_inst: float = 0.0
    delta_tau: float = 0.0
    F: float = 1.0


class TicketStub(BaseModel):
    input_hash: str = ""
    output_hash: str = ""
    trace_hash: str = ""
    merkle_root: str = ""


class AgentVote(BaseModel):
    agent_id: str
    vote: str


class PoGPayload(BaseModel):
    action_id: str
    theta_id: str
    x108_gate: str
    confidence: float = 1.0
    reason_code: str = "ROUTINE"
    lyapunov: LyapunovPayload
    ticket: TicketStub = Field(default_factory=TicketStub)
    votes: list[AgentVote] = Field(default_factory=list)


class MemoryCandidateAppendPayload(BaseModel):
    source_id: str
    source_type: str = "BRODY_RUNTIME"
    content: str


class TrustPathPayload(BaseModel):
    action_id: str
    input_hash: str = ""
    trace_hash: str = ""
    lyapunov_stable: bool = False
    pog_valid: bool = False


class RegimeClassifyPayload(BaseModel):
    regime_id: str
    coherence: float = 0.5
    integration: float = 0.5
    responsiveness: float = 0.5
    claim_text: str = ""


class OracleFreshnessPayload(BaseModel):
    oracle_id: str
    last_update_iso: str | None = None
    threshold_seconds: float = 300.0


class TimeverseSyncPayload(BaseModel):
    action_id: str
    domain: str = "TIMEVERSE"
    actor_id: str = "BRODY"
    intent: str = "SYNC"
    action_type: str = "TEMPORAL_SYNC"
    irreversible: bool = False
    timestamp_plan: str = ""
    trajectory_score: float = 1.0
    trajectory_divergence: float = 0.0
    context_drift: float = 0.0
    async_action: bool = False


@router.post("/cognitive/shazam")
async def x108_cognitive_shazam(payload: ActivationPayload):
    try:
        vector = build_activation_vector(payload.vector_id, payload.activations)
        result = shazam_cognitif(vector, theta=payload.theta)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/cognitive/dominant-trees")
async def x108_cognitive_dominant_trees(payload: ActivationPayload):
    try:
        vector = build_activation_vector(payload.vector_id, payload.activations)
        result = find_dominant_trees(vector, theta=payload.theta)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/math/lyapunov")
async def x108_math_lyapunov(payload: LyapunovPayload):
    sv = GovernedStateVector(
        I=payload.I,
        delta_E=payload.delta_E,
        delta_C=payload.delta_C,
        V_inst=payload.V_inst,
        delta_tau=payload.delta_tau,
        F=payload.F,
    )
    result = compute_lyapunov(payload.action_id, sv)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/math/pog")
async def x108_math_pog(payload: PoGPayload):
    sv = GovernedStateVector(
        I=payload.lyapunov.I,
        delta_E=payload.lyapunov.delta_E,
        delta_C=payload.lyapunov.delta_C,
        V_inst=payload.lyapunov.V_inst,
        delta_tau=payload.lyapunov.delta_tau,
        F=payload.lyapunov.F,
    )
    if payload.votes:
        raw_votes = [{"agent_id": v.agent_id, "vote": v.vote} for v in payload.votes]
    else:
        raw_votes = [
            {"agent_id": "LYAPUNOV_AGENT", "vote": "HOLD" if sv.V_inst > 0.5 else "ALLOW"},
            {"agent_id": "ENERGY_AGENT",   "vote": "HOLD" if sv.delta_E > 0.5 else "ALLOW"},
            {"agent_id": "DRIFT_AGENT",    "vote": "HOLD" if sv.delta_tau > 0.5 else "ALLOW"},
        ]
    consensus = multi_agent_consensus(raw_votes)
    if consensus.consensus == "BLOCK":
        return safe_backend_response({
            "action_id": payload.action_id,
            "pog_valid": False,
            "reason": "CONSENSUS_BLOCK",
            "consensus": consensus.to_dict(),
            **_BOUNDARY,
        }, source="REAL_BACKEND")

    lyapunov_result = compute_lyapunov(payload.lyapunov.action_id, sv)
    theta = DecisionEnvelopeTheta(
        theta_id=payload.theta_id,
        x108_gate=payload.x108_gate,
        confidence=payload.confidence,
        reason_code=payload.reason_code,
    )
    result = proof_of_governance(payload.action_id, theta, lyapunov_result, payload.ticket)
    return safe_backend_response({
        **result.to_dict(),
        "consensus": consensus.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.get("/memory/candidates/read")
async def x108_memory_candidates_read():
    candidates = read_memory_candidates()
    return safe_backend_response({
        "candidates": candidates,
        "count": len(candidates),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/memory/candidates/append")
async def x108_memory_candidates_append(payload: MemoryCandidateAppendPayload):
    try:
        src_type = MemorySourceType(payload.source_type)
    except ValueError:
        src_type = MemorySourceType.UNKNOWN
    candidate = build_memory_candidate_v2(
        source_id=payload.source_id,
        source_type=src_type,
        content=payload.content,
    )
    append_memory_candidate(candidate)
    return safe_backend_response({
        **candidate.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/math/trust-path")
async def x108_math_trust_path(payload: TrustPathPayload):
    from types import SimpleNamespace
    ticket = SimpleNamespace(
        input_hash=payload.input_hash,
        trace_hash=payload.trace_hash,
    )
    pog = SimpleNamespace(
        lyapunov_stable=payload.lyapunov_stable,
        pog_valid=payload.pog_valid,
    )
    result = build_trust_path(payload.action_id, ticket, pog)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/cognitive/regime-classify")
async def x108_cognitive_regime_classify(payload: RegimeClassifyPayload):
    result = classify_regime(
        regime_id=payload.regime_id,
        coherence=payload.coherence,
        integration=payload.integration,
        responsiveness=payload.responsiveness,
        claim_text=payload.claim_text,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/oracle/freshness")
async def x108_oracle_freshness(payload: OracleFreshnessPayload):
    result = evaluate_oracle_freshness(
        oracle_id=payload.oracle_id,
        last_update_iso=payload.last_update_iso,
        threshold_seconds=payload.threshold_seconds,
    )
    d = result.to_dict()
    if isinstance(d.get("data_age_seconds"), float) and not (d["data_age_seconds"] == d["data_age_seconds"]):
        d["data_age_seconds"] = None
    elif d.get("data_age_seconds") == float("inf"):
        d["data_age_seconds"] = None
    return safe_backend_response({**d, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/timeverse/sync")
async def x108_timeverse_sync(payload: TimeverseSyncPayload):
    from datetime import datetime, timezone
    ts = payload.timestamp_plan or datetime.now(timezone.utc).isoformat()

    oracle = evaluate_oracle_freshness(
        oracle_id=payload.domain,
        last_update_iso=ts if payload.timestamp_plan else None,
    )
    if oracle.gate == "HOLD":
        d = oracle.to_dict()
        if d.get("data_age_seconds") == float("inf"):
            d["data_age_seconds"] = None
        return safe_backend_response({
            "action_id": payload.action_id,
            "status": "ABORTED_ORACLE_STALE",
            "oracle": d,
            **_BOUNDARY,
        }, source="REAL_BACKEND")

    candidate = ActionCandidate(
        action_id=payload.action_id,
        domain=payload.domain,
        actor_id=payload.actor_id,
        intent=payload.intent,
        action_type=payload.action_type,
        irreversible=payload.irreversible,
        timestamp_plan=ts,
        payload={
            "trajectory_score": payload.trajectory_score,
            "trajectory_divergence": payload.trajectory_divergence,
            "context_drift": payload.context_drift,
            "async_action": payload.async_action,
        },
    )
    result = run_timeverse(candidate)
    result.assert_non_sovereign()
    return safe_backend_response({
        "action_id": result.action_id,
        "domain": result.domain,
        "recommended_gate": result.recommended_gate,
        "risk_flags": result.risk_flags,
        "unknowns": result.unknowns,
        "extra_metrics": result.extra_metrics,
        "can_emit_act": result.can_emit_act,
        "oracle": oracle.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


class ReplayRecord(BaseModel):
    query: str
    payload: dict[str, Any] = Field(default_factory=dict)
    stdout_sha256: str = ""


class SessionReplayPayload(BaseModel):
    session_id: str
    records: list[ReplayRecord] = Field(default_factory=list)


class CoherencePayload(BaseModel):
    session_id: str
    records: list[ReplayRecord] = Field(default_factory=list)


@router.post("/memory/replay/session")
async def x108_memory_replay_session(payload: SessionReplayPayload):
    classified = []
    boundary_violations = []
    for rec in payload.records:
        record_dict = {
            "query": rec.query,
            "payload": rec.payload,
            "stdout_sha256": rec.stdout_sha256,
        }
        try:
            _assert_replay_boundary(rec.payload)
            boundary_ok = True
        except RuntimeError as exc:
            boundary_ok = False
            boundary_violations.append({"query": rec.query, "error": str(exc)})
        classification = _classify_replay_record(record_dict)
        classification["boundary_ok"] = boundary_ok
        classified.append(classification)

    total = len(classified)
    boundary_ok_count = sum(1 for c in classified if c.get("boundary_ok"))
    source_hit_count = sum(1 for c in classified if int(c.get("packet_results_count") or 0) > 0)
    status = "SESSION_REPLAY_READONLY_PASS" if not boundary_violations else "SESSION_REPLAY_BOUNDARY_VIOLATION"

    return safe_backend_response({
        "session_id": payload.session_id,
        "status": status,
        "record_count": total,
        "boundary_ok_count": boundary_ok_count,
        "source_hit_count": source_hit_count,
        "boundary_violations": boundary_violations,
        "classified_records": classified,
        "default_queries_available": len(_REPLAY_DEFAULT_QUERIES),
        "neo4j_write": False,
        "graphiti_index_write": False,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/memory/replay/coherence")
async def x108_memory_replay_coherence(payload: CoherencePayload):
    total = len(payload.records)
    if total == 0:
        return safe_backend_response({
            "session_id": payload.session_id,
            "coherence_score": 0.0,
            "record_count": 0,
            "status": "NO_RECORDS",
            **_BOUNDARY,
        }, source="REAL_BACKEND")

    boundary_ok = 0
    source_hits = 0
    ledger_ok = 0
    for rec in payload.records:
        try:
            _assert_replay_boundary(rec.payload)
            boundary_ok += 1
        except RuntimeError:
            pass
        try:
            _validate_ledger_response(rec.payload)
            ledger_ok += 1
        except RuntimeError:
            pass
        record_dict = {"query": rec.query, "payload": rec.payload, "stdout_sha256": rec.stdout_sha256}
        cls = _classify_replay_record(record_dict)
        if int(cls.get("packet_results_count") or 0) > 0:
            source_hits += 1

    boundary_ratio = boundary_ok / total
    source_ratio = source_hits / total
    ledger_ratio = ledger_ok / total
    coherence_score = round(0.5 * boundary_ratio + 0.3 * source_ratio + 0.2 * ledger_ratio, 4)

    return safe_backend_response({
        "session_id": payload.session_id,
        "coherence_score": coherence_score,
        "record_count": total,
        "boundary_ok_count": boundary_ok,
        "source_hit_count": source_hits,
        "ledger_ok_count": ledger_ok,
        "boundary_ratio": round(boundary_ratio, 4),
        "source_ratio": round(source_ratio, 4),
        "ledger_ratio": round(ledger_ratio, 4),
        "status": "COHERENCE_COMPUTED_READONLY",
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.get("/memory/logs/sealed")
async def x108_memory_logs_sealed():
    import os
    _AUDIT_PATHS = [
        "_local_audits/memory_candidate_ledger.jsonl",
        "audit/world_action_bus.jsonl",
        "audit/sovereign_tickets.jsonl",
    ]
    logs = []
    for path in _AUDIT_PATHS:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    record_count = sum(1 for line in fh if line.strip())
            except Exception:
                record_count = -1
            logs.append({"path": path, "exists": True, "record_count": record_count, "sealed": True, "write_protected": True})
        else:
            logs.append({"path": path, "exists": False, "record_count": 0, "sealed": True, "write_protected": True})
    return safe_backend_response({
        "log_count": len(logs),
        "logs": logs,
        "audit_boundary": {k: v for k, v in _TRACE_LEDGER_BOUNDARY.items() if k in ("readonly", "memory_decision", "decision_authority", "kernel_mutation", "emits_act")},
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/readonly-ingress")
async def x108_readonly_ingress():
    rt = load_runtime_components()
    boundary = rt["x108_ingress"]["status"]
    return safe_backend_response({
        "ingress_id": "x108_v5b",
        "status": "READONLY",
        "boundary_module": boundary,
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }, source="REAL_BACKEND" if boundary == "REAL_MODULE" else "BACKEND_STUB")
