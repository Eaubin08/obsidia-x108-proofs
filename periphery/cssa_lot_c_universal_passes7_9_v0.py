"""CSSA Lot C (passes 7-9): CRM, sources, governed automation and Monde.

Pure orchestration of existing Universal read-only/proposal contracts.
No real provider calls, sends, native writes, approval or world action.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Mapping
from periphery.native_ops.intake_bundle_v0 import (
    build_native_case_task_intake_plan_v0, verify_native_case_task_intake_plan_v0,
)

SUPPORTED={"MAIL","CALENDAR","DOCUMENT","CRM"}
PERSONAL={"PERSONAL_INBOX","PERSONAL_TRANSACTION"}
MODES={"SIMULATED_FIXTURE","PUBLIC_READONLY","CSSA_OPERATIONAL_UNVERIFIED"}

@dataclass(frozen=True)
class CSSAEnterpriseSourceV0:
    source_id: str
    kind: str
    mode: str
    scope: str
    reference: str | None
    evidence_refs: tuple[str,...]
    owner_ref: str | None
    observed_at: str | None
    due_at: str | None
    task_kind: str
    title: str
    summary: str
    classified_operational: bool = False
    human_review_ref: str | None = None
    known_contradictions: tuple[str,...] = ()
    unknowns: tuple[str,...] = ()
    external_permission_verified: bool = False

def _time(s):
    if not isinstance(s,str): return False
    try:
        d=datetime.fromisoformat(s)
        return d.tzinfo is not None and d.utcoffset() is not None
    except ValueError: return False

def route_cssa_universal_source_v0(row: CSSAEnterpriseSourceV0) -> dict:
    if not isinstance(row,CSSAEnterpriseSourceV0): raise ValueError("CSSA_C_SOURCE_TYPE")
    if not row.source_id or row.kind not in SUPPORTED or row.mode not in MODES:
        raise ValueError("CSSA_C_SOURCE_CONTRACT")
    reasons=[]
    if row.known_contradictions: reasons.extend("CONTRADICTION:"+s for s in row.known_contradictions)
    if row.unknowns: reasons.extend("UNKNOWN:"+s for s in row.unknowns)
    if row.scope in PERSONAL:
        return {"id":row.source_id,"status":"PERSONAL_READONLY","reasons":("PERSONAL_DATA_NOT_CLUB_AUTHORITY",),
           "plan":None,"calendar_candidate":None,"email_candidate":None,
           "crm_writes":0,"external_effect":False}
    if not row.classified_operational: reasons.append("NOT_PROVEN_OPERATIONAL")
    if not row.reference or not row.evidence_refs: reasons.append("MISSING_PROVENANCE")
    if not row.owner_ref or not row.human_review_ref: reasons.append("HUMAN_OWNERSHIP_MISSING")
    if not _time(row.observed_at) or not _time(row.due_at): reasons.append("DATE_NOT_VALIDATED")
    if not row.title.strip() or not row.summary.strip(): reasons.append("DESCRIPTION_MISSING")
    if row.mode=="CSSA_OPERATIONAL_UNVERIFIED": reasons.append("EXTERNAL_SOURCE_AUTHORITY_NOT_ATTESTED")
    if row.external_permission_verified: reasons.append("EXTERNAL_PERMISSION_CLAIM_NOT_ACCEPTED_IN_SIMULATION")
    status="BLOCK" if row.known_contradictions else "HOLD"
    plan=None
    if not reasons and row.mode=="SIMULATED_FIXTURE":
        digest=sha256((row.source_id+"|"+str(row.reference)).encode()).hexdigest()[:20]
        plan=build_native_case_task_intake_plan_v0(
            intake_id="cssa-c-intake:"+digest,case_id="cssa-c-case:"+digest,
            task_id="cssa-c-task:"+digest,interaction_id="cssa-c-interaction:"+digest,
            followup_id="cssa-c-followup:"+digest,case_type="CSSA_"+row.task_kind,
            title=row.title,summary=row.summary,owner_ref=row.owner_ref,
            priority="NORMAL",occurred_at=row.observed_at,due_at=row.due_at,
            source_refs=(row.reference,),evidence_refs=row.evidence_refs,
            tags=("CSSA","LOT_C","SIMULATED","REVIEW_ONLY",row.kind))
        if verify_native_case_task_intake_plan_v0(plan)!=(True,None):
            raise ValueError("CSSA_C_NATIVE_PLAN_INVALID")
        status="DRAFT_REVIEW_ONLY"
    return {"id":row.source_id,"status":status,"reasons":tuple(reasons),
       "plan":plan,"calendar_candidate":{"event_kind":"FOLLOWUP_PROPOSAL","due_at":row.due_at,
         "source_ref":row.reference,"created":False} if plan else None,
       "email_candidate":{"kind":"REVIEW_DRAFT","source_ref":row.reference,
         "sent":False,"recipient":None} if plan and row.kind=="MAIL" else None,
       "crm_writes":0,"external_effect":False}

def build_cssa_lot_c_cockpit_v0(*, lot_a:Mapping,lot_b:Mapping,
    observations:tuple[CSSAEnterpriseSourceV0,...],sandbox_proof:Mapping|None=None,
    portable_config:Mapping|None=None) -> dict:
    errors=[]
    if lot_a.get("verdict")!="LOT_A_CLOSED_SIMULATION" or lot_a.get("season_event_count")!=904:
        errors.append("LOT_A_EVIDENCE_INVALID")
    if lot_b.get("verdict")!="LOT_B_CLOSED_SIMULATION" or lot_b.get("matchday_stream_count")!=11:
        errors.append("LOT_B_EVIDENCE_INVALID")
    if lot_a.get("native_writes")!=0 or lot_b.get("crm_writes")!=0:
        errors.append("HISTORIC_SIDE_EFFECT_CLAIM_INVALID")
    seen=set()
    entries=[]
    for x in observations:
        if x.source_id in seen: raise ValueError("CSSA_C_DUPLICATE_SOURCE")
        seen.add(x.source_id)
        entries.append(route_cssa_universal_source_v0(x))
    coverage={x.kind for x in observations}
    if coverage!=SUPPORTED: errors.append("FOUR_NATIVE_SOURCE_KINDS_NOT_COVERED")
    if not any(x["status"]=="PERSONAL_READONLY" for x in entries):
        errors.append("PERSONAL_INBOX_ISOLATION_UNTESTED")
    if not any(x["status"]=="DRAFT_REVIEW_ONLY" for x in entries):
        errors.append("NATIVE_INTAKE_DRAFT_NOT_EXERCISED")
    if not any(x["status"] in ("HOLD","BLOCK") for x in entries):
        errors.append("FAIL_CLOSED_NOT_EXERCISED")
    # Actual Universal sandbox proof only; no fake approval or KX108 outcome.
    proof=sandbox_proof or {}
    if not proof: errors.append("UNIVERSAL_KX108_SANDBOX_PROOF_MISSING")
    else:
        if (proof.get("status")!="CSSA_LOT_A_SANDBOX_E2E_PROVEN"
           or proof.get("decision_authority")!="KX108_ONLY"
           or proof.get("sandbox_operator_approval_simulated") is not True
           or proof.get("real_operator_approval") is not False
           or proof.get("real_external_effect") is not False
           or proof.get("network_call_performed") is not False
           or proof.get("execution",{}).get("execution_replay_ok") is not True
           or proof.get("execution",{}).get("duplicate_adapter_called") is not False):
            errors.append("SOVEREIGN_SANDBOX_PROOF_NOT_VALID")
    config=portable_config or {}
    if (config.get("run_mode")!="OFFLINE_READONLY"
        or config.get("branch")!="feat/cssa-v01-active"
        or config.get("provider_network_allowed") is not False
        or config.get("real_club_credentials_loaded") is not False
        or config.get("shared_kernel_mutable") is not False):
        errors.append("PORTABLE_PROFILE_UNSAFE")
    nodes=[{"node_id":"cssa-source:"+e["id"],"kind":"source",
      "state":e["status"],"native_draft":e["plan"] is not None}
      for e in entries]
    report={"schema":"CSSA_LOT_C_PASSES_07_09_COCKPIT_V0",
       "verdict":"LOT_C_CLOSED_SIMULATION" if not errors else "LOT_C_BLOCKED",
       "failures":errors,"source_kinds":sorted(coverage),"sources":nodes,
       "crm_plan_count":sum(e["plan"] is not None for e in entries),
       "calendar_candidate_count":sum(e["calendar_candidate"] is not None for e in entries),
       "email_draft_count":sum(e["email_candidate"] is not None for e in entries),
       "kx108_sandbox_evidence":bool(proof),"native_writes":0,
       "mail_sends":0,"calendar_writes":0,"external_calls":0,
       "real_operator_approval":False,"actual_world_action":False,
       "decision_authority":"KX108_ONLY","scope":"SIMULATED_OFFLINE_ONLY"}
    report["diagnostic_sha256"]=sha256(json.dumps(report,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    return report
