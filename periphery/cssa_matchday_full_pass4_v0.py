"""CSSA pass 04: comprehensive simulated matchday operations, fail-closed.

Reuses F3G-J assessment objects and Universal native intake plan builder.
Does not create tickets, payments, assignments, mail or native writes.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping
from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
from periphery.cssa_historical_native_intake_draft_v0 import draft_cssa_historical_native_intake_v0

STREAMS = ("TICKETING","SUBSCRIPTIONS","ACCESS","SAFETY","WELCOME","HOSPITALITY","BUVETTE","STOCK","SUPPLIERS","VOLUNTEERS","CASH")
SAFETY_STREAMS = frozenset(("SAFETY","ACCESS"))

@dataclass(frozen=True)
class MatchdayOperationalSignalV0:
    signal_id: str
    match_ref: str
    stream: str
    source_ref: str | None
    evidence_refs: tuple[str, ...]
    owner_ref: str | None
    occurred_at: str | None
    due_at: str | None
    ready: bool
    authority_verified: bool = False
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    human_reviewer_ref: str | None = None


def evaluate_cssa_matchday_v0(
    match_ref: str, signals: tuple[MatchdayOperationalSignalV0, ...],
    f3g_buvette_assessments: tuple[object, ...],
) -> dict:
    """Operational cockpit/read-only readiness snapshot; never opening approval."""
    if not match_ref or not isinstance(match_ref,str):
        raise ValueError("MATCHDAY_MATCH_REF_REQUIRED")
    if any(not isinstance(x,MatchdayOperationalSignalV0) for x in signals):
        raise ValueError("MATCHDAY_INVALID_SIGNAL")
    seen=set()
    items=[]
    for row in signals:
        if row.signal_id in seen or not row.signal_id:
            raise ValueError("MATCHDAY_DUPLICATE_OR_EMPTY_SIGNAL_ID")
        seen.add(row.signal_id)
        if row.stream not in STREAMS or row.match_ref!=match_ref:
            raise ValueError("MATCHDAY_STREAM_OR_MATCH_MISMATCH")
        reasons=[]
        if row.contradictions: reasons += ["CONTRADICTION:"+s for s in row.contradictions]
        if not row.ready: reasons.append("READINESS_NOT_PROVEN")
        if row.unknowns: reasons += ["UNKNOWN:"+s for s in row.unknowns]
        if not row.source_ref or not row.evidence_refs: reasons.append("SOURCE_OR_EVIDENCE_MISSING")
        if not row.owner_ref or not row.human_reviewer_ref: reasons.append("OWNER_OR_REVIEWER_MISSING")
        if not row.occurred_at or not row.due_at: reasons.append("TIMESTAMP_MISSING")
        if not row.authority_verified: reasons.append("OPERATIONAL_AUTHORITY_NOT_VERIFIED")
        verdict="BLOCK" if row.contradictions or (row.stream in SAFETY_STREAMS and not row.ready) else "HOLD" if reasons else "READY_FOR_HUMAN_REVIEW"
        items.append({"id":row.signal_id,"stream":row.stream,"status":verdict,"reasons":reasons,"priority":"SAFETY" if row.stream in SAFETY_STREAMS else "OPERATIONAL","actual_action":False})
    for assessment in f3g_buvette_assessments:
        if getattr(assessment,"match_ref",None)!=match_ref:
            raise ValueError("F3G_BUVETTE_MATCH_REF_MISMATCH")
        proposal=project_historical_cssa_assessment_v0(assessment)
        if proposal.source_family!="F3G_BUVETTE":
            raise ValueError("F3G_BUVETTE_TYPE_INVALID")
        status="BLOCK" if proposal.disposition=="BLOCK" else "HOLD"
        items.append({"id":"F3G:"+proposal.source_case_id,"stream":"BUVETTE","status":status,"reasons":list(proposal.reasons),"priority":"OPERATIONAL","actual_action":False})
    covered=set(x["stream"] for x in items)
    missing=tuple(s for s in STREAMS if s not in covered)
    counts=dict(Counter(x["status"] for x in items))
    blockers=tuple(x["id"] for x in items if x["status"]=="BLOCK")
    overall="BLOCK" if blockers else "HOLD" if missing or any(x["status"]=="HOLD" for x in items) else "REVIEW_REQUIRED"
    report={"schema":"CSSA_MATCHDAY_PASS04_READONLY_V0","match_ref":match_ref,
       "stream_count":len(covered),"missing_streams":missing,
       "items":items,"status":overall,"counts":counts,"blockers":blockers,
       "ready_to_open_stadium":False,"ready_to_sell_tickets":False,
       "real_approvals":0,"canonical_native_writes":0,"external_actions":0,
       "decision_authority":"KX108_ONLY","simulation_only":True}
    report["report_sha256"]=sha256(json.dumps(report,sort_keys=True,ensure_ascii=False,default=list,separators=(",",":")).encode()).hexdigest()
    return report


def draft_f3g_matchday_native_work_v0(assessment, *, source_ref, evidence_refs, owner_ref, occurred_at, due_at):
    """Bridge real historical F3G-J dataclass to existing native CASE/TASK draft."""
    proposal=project_historical_cssa_assessment_v0(assessment)
    if proposal.source_family!="F3G_BUVETTE": raise ValueError("MATCHDAY_F3G_ASSESSMENT_REQUIRED")
    return draft_cssa_historical_native_intake_v0(proposal,observed_source_ref=source_ref,
        observed_evidence_refs=evidence_refs,proposed_owner_ref=owner_ref,
        occurred_at=occurred_at,due_at=due_at)
