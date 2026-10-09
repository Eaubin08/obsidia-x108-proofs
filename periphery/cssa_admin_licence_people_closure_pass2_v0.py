"""CSSA Pass 2 — bounded administrative closure: licence / people / delegation.

Only consumes synthetic/public structural cases; original CSSA/F3H engines
stay authoritative for métier and native mutations. No operational effects.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Mapping
from periphery.native_ops.intake_bundle_v0 import build_native_case_task_intake_plan_v0, verify_native_case_task_intake_plan_v0

KINDS = {"LICENCE","OFFICIAL_REGISTRATION","STAFF_AVAILABILITY","VOLUNTEER_ABSENCE","DELEGATION","SUBSTITUTION"}

@dataclass(frozen=True)
class CSSAAdminCaseV0:
    case_id: str
    kind: str
    source_ref: str | None
    evidence_refs: tuple[str, ...]
    responsible_role: str | None
    assigned_actor_ref: str | None
    delegation_authority_ref: str | None
    occurred_at: str | None
    due_at: str | None
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    real_club_access: bool = False
    simulation_only: bool = True

def _aware(value):
    if not isinstance(value, str): return False
    try:
        d=datetime.fromisoformat(value)
        return d.tzinfo is not None and d.utcoffset() is not None
    except ValueError: return False

def plan_cssa_admin_case_v0(case: CSSAAdminCaseV0) -> dict:
    if not isinstance(case,CSSAAdminCaseV0): raise ValueError("CSSA_ADMIN_CASE_TYPE")
    if case.kind not in KINDS or not case.case_id: raise ValueError("CSSA_ADMIN_KIND_OR_ID_INVALID")
    if case.real_club_access or not case.simulation_only:
        raise ValueError("CSSA_ADMIN_SIMULATION_ONLY")
    reasons=[]
    if case.contradictions: reasons.extend("CONTRADICTION:"+x for x in case.contradictions)
    if case.unknowns: reasons.extend("UNKNOWN:"+x for x in case.unknowns)
    if not case.source_ref or not case.source_ref.strip(): reasons.append("SOURCE_MISSING")
    if not case.evidence_refs or any(not isinstance(x,str) or not x.strip() for x in case.evidence_refs): reasons.append("EVIDENCE_MISSING")
    if not case.responsible_role: reasons.append("ROLE_MISSING")
    if not case.assigned_actor_ref: reasons.append("ACTOR_NOT_VERIFIED")
    if case.kind in {"DELEGATION","SUBSTITUTION"} and not case.delegation_authority_ref:
        reasons.append("DELEGATION_AUTHORITY_NOT_VERIFIED")
    if not _aware(case.occurred_at): reasons.append("OCCURRENCE_DATE_UNVERIFIED")
    if not _aware(case.due_at): reasons.append("DEADLINE_UNVERIFIED")
    if reasons:
        return {"case_id":case.case_id,"kind":case.kind,"status":"BLOCK" if case.contradictions else "HOLD",
                "reasons":tuple(reasons),"plan":None,"native_writes":0,"approved":False}
    digest=sha256(json.dumps([case.case_id,case.kind,case.source_ref,case.due_at],
        ensure_ascii=False,separators=(",",":")).encode()).hexdigest()[:24]
    plan=build_native_case_task_intake_plan_v0(
        intake_id="cssa-admin:"+digest,case_id="cssa-admin-case:"+digest,
        task_id="cssa-admin-task:"+digest,interaction_id="cssa-admin-int:"+digest,
        followup_id="cssa-admin-followup:"+digest,case_type=case.kind+"_REVIEW",
        title="CSSA "+case.kind+" review / "+case.case_id,
        summary="Simulated review; actor/authority refs unverified external to this test",
        owner_ref=case.assigned_actor_ref,priority="NORMAL",
        occurred_at=case.occurred_at,due_at=case.due_at,
        source_refs=(case.source_ref,),evidence_refs=case.evidence_refs,
        tags=("CSSA","ADMIN","SIMULATED","REVIEW_ONLY",case.kind))
    if verify_native_case_task_intake_plan_v0(plan)!=(True,None):
        raise ValueError("CSSA_ADMIN_NATIVE_PLAN_FAILED")
    return {"case_id":case.case_id,"kind":case.kind,"status":"DRAFT_REVIEW_ONLY",
            "reasons":("REAL_AUTHORITY_NOT_ATTESTED","KX108_GATE_NOT_INVOKED"),
            "plan":plan,"native_writes":0,"approved":False}

def close_cssa_pass2_admin_campaign_v0(cases: tuple[CSSAAdminCaseV0,...]) -> dict:
    entries=[]
    seen=set()
    for case in cases:
        if case.case_id in seen: raise ValueError("CSSA_ADMIN_DUPLICATE_CASE")
        seen.add(case.case_id)
        entries.append(plan_cssa_admin_case_v0(case))
    counts={key:sum(e["status"]==key for e in entries) for key in ("DRAFT_REVIEW_ONLY","HOLD","BLOCK")}
    return {"schema":"CSSA_PASS2_ADMIN_CLOSURE_SIMULATION_V0","entries":entries,
            "counts":counts,"cases":len(entries),"canonical_native_writes":0,
            "external_actions":0,"human_approvals":0,"decision_authority":"KX108_ONLY",
            "pass2_scope":"SIMULATED_READONLY_CLOSURE","operational_club_readiness":"NOT_VERIFIED"}