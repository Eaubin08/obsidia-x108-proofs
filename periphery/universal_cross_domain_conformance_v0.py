"""Universal cross-domain conformance: isolated adapters, one invariant rail.

This is a deterministic contract campaign, NOT an execution of external GPS,
trading or industrial runtimes. Reuse actual domain engines in a later pinned
cross-repository runner; do not fabricate their sovereign receipts.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

DOMAINS={
 "CSSA": {"required":("organization","case","authority"),"surface":"TASKS","class":"ORGANIZATION"},
 "GPS_DEFENSE": {"required":("receiver","signal","rf_evidence"),"surface":"DEVICE","class":"PHYSICAL_SAFETY"},
 "TRADING": {"required":("portfolio","order","risk_limit"),"surface":"BROKER_PAPER","class":"FINANCIAL"},
 "INDUSTRIAL_MAINTENANCE": {"required":("machine","sensor","maintenance_rule"),"surface":"TASKS","class":"PHYSICAL_OPERATION"},
}
RISK={"CSSA":"NORMAL","GPS_DEFENSE":"CRITICAL","TRADING":"HIGH","INDUSTRIAL_MAINTENANCE":"HIGH"}
CAPABILITY={"CSSA":"TASK.CREATE","GPS_DEFENSE":"DEVICE.CONTROL.PROPOSE",
            "TRADING":"ORDER.PAPER.PROPOSE","INDUSTRIAL_MAINTENANCE":"MAINTENANCE.TASK.PROPOSE"}
FORBIDDEN_LIVE={"DEVICE.CONTROL.PROPOSE","ORDER.PAPER.PROPOSE"}

@dataclass(frozen=True)
class DomainEvidenceV0:
    case_id:str
    domain:str
    observed_facts:dict[str,Any]
    source_refs:tuple[str,...]
    evidence_refs:tuple[str,...]
    adapter_ref:str
    organization_scope:str
    observed_at:str
    proposed_intent:str
    unknowns:tuple[str,...]=()
    contradictions:tuple[str,...]=()
    requested_execution:str="OFFLINE_ONLY"
    policy_version:str="UDIP_V0"

def _digest(payload:dict)->str:
    return sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,
                             separators=(",",":"),default=str).encode()).hexdigest()

def interpret_domain_v0(case:DomainEvidenceV0)->dict:
    if not isinstance(case,DomainEvidenceV0): raise ValueError("DOMAIN_CASE_TYPE")
    if case.domain not in DOMAINS: raise ValueError("DOMAIN_NOT_REGISTERED")
    if not case.case_id or not case.adapter_ref or not case.organization_scope:
        raise ValueError("CASE_IDENTITY_MISSING")
    if case.requested_execution!="OFFLINE_ONLY":
        raise ValueError("EXTERNAL_EXECUTION_FORBIDDEN")
    spec=DOMAINS[case.domain]
    gaps=tuple(k for k in spec["required"] if not case.observed_facts.get(k))
    if not case.source_refs or not case.evidence_refs: gaps+=("provenance",)
    if not case.observed_at or not case.proposed_intent: gaps+=("intent_or_time",)
    if case.contradictions: status="BLOCK"
    elif gaps or case.unknowns: status="HOLD"
    elif CAPABILITY[case.domain] in FORBIDDEN_LIVE: status="HOLD"
    else: status="REVIEW_ONLY"
    # The common rail is only an intent envelope; no KX108 decision is
    # impersonated. Every case must still go through canonical KX108.
    common={"schema":"UNIVERSAL_CROSS_DOMAIN_INTENT_V0",
        "scope":case.organization_scope,"domain":case.domain,
        "capability":CAPABILITY[case.domain],"intent":case.proposed_intent,
        "risk":RISK[case.domain],"policy":case.policy_version,
        "source_refs":case.source_refs,"evidence_refs":case.evidence_refs,
        "observed_at":case.observed_at,"facts":case.observed_facts,
        "unknowns":case.unknowns,"contradictions":case.contradictions}
    return {"case_id":case.case_id,"domain":case.domain,"domain_class":spec["class"],
        "surface":spec["surface"],"capability":CAPABILITY[case.domain],
        "gate":status,"missing":gaps,"unknowns":case.unknowns,
        "contradictions":case.contradictions,
        "intent_hash":_digest(common),"proposal":common,
        "authority":"KX108_ONLY","kx108_decision":"NOT_INVOKED",
        "world_action_allowed":False,"provider_invoked":False,"real_effect":False}

def evaluate_cross_domain_conformance_v0(cases:tuple[DomainEvidenceV0,...],
                                          *,expected_domains:tuple[str,...]=tuple(DOMAINS))->dict:
    issues=[]
    if len({x.case_id for x in cases})!=len(cases): raise ValueError("DUPLICATE_CASE")
    rows=[interpret_domain_v0(x) for x in cases]
    present={x["domain"] for x in rows}
    if present!=set(expected_domains): issues.append("DOMAIN_COVERAGE_INCOMPLETE")
    if not any(x["gate"]=="HOLD" for x in rows): issues.append("HOLD_NOT_TESTED")
    if not any(x["gate"]=="BLOCK" for x in rows): issues.append("BLOCK_NOT_TESTED")
    if not any(x["gate"]=="REVIEW_ONLY" for x in rows): issues.append("POSITIVE_DRAFT_NOT_TESTED")
    if any(x["world_action_allowed"] or x["provider_invoked"] or x["real_effect"] for x in rows):
        issues.append("EXTERNAL_EFFECT_POLICY_BROKEN")
    if any(x["kx108_decision"]!="NOT_INVOKED" or x["authority"]!="KX108_ONLY" for x in rows):
        issues.append("FALSE_DECISION_AUTHORITY")
    result={"schema":"OBSIDIA_UNIVERSAL_CROSS_DOMAIN_CONFORMANCE_V0",
        "verdict":"CONTRACT_SIMULATION_PASS" if not issues else "CONTRACT_SIMULATION_BLOCKED",
        "issues":issues,"domain_count":len(present),"case_count":len(rows),
        "gate_counts":{g:sum(x["gate"]==g for x in rows)
                       for g in ("REVIEW_ONLY","HOLD","BLOCK")},
        "records":[{"id":x["case_id"],"domain":x["domain"],"gate":x["gate"],
                    "intent_hash":x["intent_hash"],"missing":x["missing"]}
                   for x in rows],
        "real_actions":0,"real_connector_calls":0,"kx108_calls":0,
        "external_repo_runtime_verified":False,
        "authority":"KX108_ONLY","scope":"SYNTHETIC_CONTRACT_CAMPAIGN_ONLY"}
    result["diagnostic_hash"]=_digest(result)
    return result
