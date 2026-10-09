"""CSSA Pass 06 — cross-lot season incident propagation and Lot B verdict.

Combines evaluated original Lot A, all matchday streams and communication
cases. Pure read-only evaluation: never sends, writes, authorizes or executes.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from typing import Mapping
from periphery.cssa_matchday_full_pass4_v0 import evaluate_cssa_matchday_v0, STREAMS
from periphery.cssa_supporters_partners_communications_pass5_v0 import build_cssa_communication_campaign_v0

INCIDENTS={
 "MATCH_POSTPONED":("TICKETING","ACCESS","WELCOME","PARTNER_INVITATION","MATCH_INFORMATION"),
 "SAFETY_ALERT":("SAFETY","ACCESS","WELCOME","MATCH_INFORMATION"),
 "VOLUNTEER_ABSENCE":("VOLUNTEERS","BUVETTE","WELCOME"),
 "SUPPLIER_FAILURE":("SUPPLIERS","STOCK","BUVETTE","PARTNER_DELIVERY"),
 "BUDGET_OVERRUN":("CASH","HOSPITALITY","SPONSOR_CONTRACT"),
 "TICKET_REFUND":("TICKETING","SUBSCRIPTIONS","REFUND_REQUEST"),
 "ADMIN_DEADLINE_COLLISION":("INSTITUTIONAL_MESSAGE","OPERATIONAL_REQUEST","VOLUNTEERS"),
}
COMMS=set(("PARTNER_INVITATION","MATCH_INFORMATION","PARTNER_DELIVERY","SPONSOR_CONTRACT","REFUND_REQUEST","INSTITUTIONAL_MESSAGE","OPERATIONAL_REQUEST"))

def close_cssa_lot_b_pass6_v0(*, lot_a_verdict:Mapping, match_ref:str,
    matchday_signals:tuple, communication_cases:tuple,
    original_f3g_buvette_assessments:tuple=(),
    incidents:tuple[str,...]=tuple(INCIDENTS)) -> dict:
    """Block closure on missing coverage, broken authority or chain linkage."""
    errors=[]
    if lot_a_verdict.get("verdict")!="LOT_A_CLOSED_SIMULATION":
        errors.append("LOT_A_NOT_CLOSED_IN_SIMULATION")
    if lot_a_verdict.get("native_writes")!=0 or lot_a_verdict.get("real_authorizations")!=0:
        errors.append("LOT_A_AUTHORITY_CONTRADICTION")
    if lot_a_verdict.get("season_event_count")!=904 or lot_a_verdict.get("verified_public_role_count")!=11:
        errors.append("LOT_A_EVIDENCE_INCOMPLETE")
    matchday=evaluate_cssa_matchday_v0(match_ref,matchday_signals,original_f3g_buvette_assessments)
    comm=build_cssa_communication_campaign_v0(communication_cases)
    if matchday["missing_streams"] or matchday["stream_count"]!=len(STREAMS):
        errors.append("MATCHDAY_STREAM_COVERAGE_INCOMPLETE")
    if not original_f3g_buvette_assessments:
        errors.append("ORIGINAL_F3G_J_NOT_LINKED")
    if matchday["canonical_native_writes"] or matchday["external_actions"] or comm["emails_sent"] or comm["crm_writes"] or comm["publications"]:
        errors.append("SIDE_EFFECT_FORBIDDEN")
    if not comm["count"] or not any(x["classification"]=="PERSONAL_TRANSACTION_ONLY" for x in comm["entries"]):
        errors.append("PERSONAL_TRANSACTION_SEPARATION_NOT_PROVEN")
    ids=[r.case_id for r in communication_cases]
    if len(ids)!=len(set(ids)): errors.append("DUPLICATE_COMMUNICATION")
    covered_streams={x.stream for x in matchday_signals}
    covered_comms={x.kind for x in communication_cases}
    propagated=[]
    for incident in incidents:
        if incident not in INCIDENTS:
            errors.append("UNKNOWN_INCIDENT:"+str(incident))
            continue
        effects=INCIDENTS[incident]
        missing=tuple(x for x in effects if x not in (covered_comms if x in COMMS else covered_streams))
        if missing: errors.append("UNROUTED_INCIDENT:"+incident)
        propagated.append({"incident":incident,"affected":effects,"unrouted":missing,
             "intervention":"HUMAN_REVIEW_REQUIRED","executed":False})
    if len(set(incidents))!=len(INCIDENTS):
        errors.append("SEVEN_INCIDENT_FAMILIES_NOT_FULLY_EXERCISED")
    if not any(x["status"] in ("HOLD","BLOCK") for x in matchday["items"]):
        errors.append("MATCHDAY_FAIL_CLOSED_NOT_EXERCISED")
    if not any(x["status"] in ("HOLD","BLOCK") for x in comm["entries"]):
        errors.append("COMMUNICATION_FAIL_CLOSED_NOT_EXERCISED")
    report={"schema":"CSSA_PASS06_CROSS_LOT_A_B_V0",
      "verdict":"LOT_B_CLOSED_SIMULATION" if not errors else "LOT_B_BLOCKED",
      "failures":errors,"match_ref":match_ref,
      "matchday_stream_count":matchday["stream_count"],
      "communications_count":comm["count"],
      "f3g_j_assessment_count":len(original_f3g_buvette_assessments),
      "incident_routes":propagated,
      "lot_a_verdict":lot_a_verdict.get("verdict"),
      "mail_sent":0,"crm_writes":0,"external_actions":0,
      "real_approvals":0,"world_action_allowed":False,
      "scope":"SYNTHETIC_STRUCTURAL_ONLY","decision_authority":"KX108_ONLY"}
    report["diagnostic_sha256"]=sha256(json.dumps(report,sort_keys=True,ensure_ascii=False,default=list,separators=(",",":")).encode()).hexdigest()
    return report
