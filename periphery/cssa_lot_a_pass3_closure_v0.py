"""Pass 03: actual F3E/F3F 904-event season and 11-role Lot A closure verdict.

Read-only evidence compilation only. Never creates KX108 authority or writes.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from typing import Any, Mapping

REQUIRED_ROLE_IDS = frozenset(("ADMINISTRATION_DAILY","INSTITUTIONAL_RELATIONS","PEOPLE_MANAGEMENT_DELEGATION","CROSS_POLE_COORDINATION","MATCHDAY_TICKETING","MATCHDAY_SECURITY","MATCHDAY_WELCOME_HOSPITALITY","MATCHDAY_BUVETTE_RESTAURATION","WRITTEN_PROCESS_RESPONSIBILITY","ROOT_CAUSE_DURABILITY","DECISION_EXECUTION"))

def close_cssa_lot_a_pass3_v0(*, corpus, stress_assessments, season_pressure: Mapping, role_contract: Mapping, admin_register: Mapping, native_review_proof: Mapping) -> dict[str, Any]:
    """Fail closed on absent/inconsistent evidence; no actual state mutation."""
    failures=[]
    events=tuple(corpus.events)
    rows=tuple(stress_assessments)
    if corpus.simulation_status != "SIMULATED_NOT_OBSERVED": failures.append("NON_SIMULATED_SEASON")
    if len(events)!=904: failures.append("SEASON_EVENT_COUNT_NOT_904")
    ids=[e.event_id for e in events]
    if len(set(ids))!=len(ids): failures.append("DUPLICATE_SEASON_EVENT_ID")
    if any(e.simulation_status!="SIMULATED_NOT_OBSERVED" for e in events): failures.append("UNVERIFIED_EVENT_TRUTH")
    gates=dict(Counter(e.expected_gate for e in events))
    if not any(e.privacy_blocked for e in events): failures.append("PRIVACY_GUARD_NOT_EXERCISED")
    if not any(e.expected_gate=="BLOCK" for e in events): failures.append("SEASON_BLOCK_NOT_EXERCISED")
    if not any(e.expected_gate=="HOLD" for e in events): failures.append("SEASON_HOLD_NOT_EXERCISED")
    sg=dict(Counter(x.expected_gate for x in rows))
    if len(rows)!=12: failures.append("STRESS_SCENARIOS_NOT_12")
    if sg!={"ALLOW":2,"HOLD":5,"BLOCK":5}: failures.append("STRESS_GATES_MISMATCH")
    if any(getattr(x,"simulation_status",None)!="SIMULATED_NOT_OBSERVED" for x in rows): failures.append("NON_SYNTHETIC_STRESS")
    if season_pressure.get("event_count")!=len(events): failures.append("SEASON_STRESS_SCAN_INCOMPLETE")
    if season_pressure.get("pressure_point_count")!=len(season_pressure.get("pressure_points",[])): failures.append("PRESSURE_COUNT_INCONSISTENT")
    if role_contract.get("status")!="PUBLIC_ANNOUNCED_ROLE_CONTRACT_READONLY": failures.append("ROLE_SOURCE_NOT_PUBLIC_READONLY")
    boundaries=role_contract.get("global_boundaries",{})
    if boundaries.get("real_field_evidence") is not False or boundaries.get("external_action") is not False or boundaries.get("decision_authority")!="KX108_ONLY": failures.append("ROLE_AUTHORITY_UNSAFE")
    actual_ids=[x["id"] for x in role_contract.get("requirements",[])]
    if len(actual_ids)!=11 or set(actual_ids)!=REQUIRED_ROLE_IDS: failures.append("ELEVEN_ROLE_MATRIX_INCOMPLETE")
    if admin_register.get("role_count")!=11 or admin_register.get("canonical_native_writes")!=0: failures.append("ADMIN_REGISTER_NOT_SAFE")
    if admin_register.get("field_authority_verified") is not False: failures.append("REAL_AUTHORITY_FABRICATED")
    if admin_register.get("family_count")!=6: failures.append("SIX_HISTORICAL_ENGINES_NOT_BOUND")
    if not all(x.get("operational_readiness")=="NOT_VERIFIED" for x in admin_register.get("role_matrix",[])): failures.append("ROLE_OPERATIONAL_STATUS_ESCALATION")
    if native_review_proof.get("canonical_native_writes")!=0 or native_review_proof.get("external_actions")!=0 or native_review_proof.get("human_approvals")!=0: failures.append("NATIVE_SIDE_EFFECT_OR_FALSE_APPROVAL")
    if native_review_proof.get("operational_club_readiness")!="NOT_VERIFIED": failures.append("FALSE_FIELD_READINESS")
    if native_review_proof.get("cases")!=6: failures.append("ADMIN_SIX_CASES_INCOMPLETE")
    summary={
      "schema":"CSSA_LOT_A_PASS3_CLOSURE_V0",
      "verdict":"LOT_A_CLOSED_SIMULATION" if not failures else "LOT_A_BLOCKED",
      "failures":failures,
      "season_event_count":len(events),"season_gate_counts":gates,
      "stress_scenario_count":len(rows),"stress_gate_counts":sg,
      "season_pressure_points":season_pressure.get("pressure_point_count"),
      "verified_public_role_count":len(set(actual_ids)&REQUIRED_ROLE_IDS),
      "original_assessment_families":admin_register.get("family_set"),
      "native_review_cases":native_review_proof.get("cases"),
      "external_effect":False,"native_writes":0,"real_authorizations":0,
      "field_readiness":"NOT_VERIFIED","decision_authority":"KX108_ONLY",
      "scope":"SYNTHETIC_STRUCTURAL_ONLY",
    }
    summary["receipt_sha256"]=sha256(json.dumps(summary,sort_keys=True,ensure_ascii=False,default=list,separators=(",",":")).encode()).hexdigest()
    return summary