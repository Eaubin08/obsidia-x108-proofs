"""Cross-lot A+B cascade validation using original F3G-J assessments."""
import importlib
import json
import os
import sys
from datetime import date
from pathlib import Path
import pytest
from periphery.cssa_cross_lot_ab_closure_pass6_v0 import close_cssa_lot_b_pass6_v0, INCIDENTS
from periphery.cssa_matchday_full_pass4_v0 import STREAMS, MatchdayOperationalSignalV0
from periphery.cssa_supporters_partners_communications_pass5_v0 import CSSACommunicationCaseV0

def a():
    return {"verdict":"LOT_A_CLOSED_SIMULATION","native_writes":0,"real_authorizations":0,
            "season_event_count":904,"verified_public_role_count":11}

def signal(stream):
    return MatchdayOperationalSignalV0(signal_id="sim:"+stream,match_ref="sim:match:001",
        stream=stream,source_ref="sim:source",evidence_refs=("sim:proof",),
        owner_ref="SIMULATED:OWNER",occurred_at="2026-10-07T10:00:00+00:00",
        due_at="2026-10-09T15:00:00+00:00",ready=True,
        human_reviewer_ref="SIMULATED:REVIEWER")

def comm(kind):
    return CSSACommunicationCaseV0(case_id="sim:"+kind,kind=kind,
        audience="TICKET_BUYER" if kind=="TICKET_CONFIRMATION" else "SUPPORTER",
        source_scope="PERSONAL_INBOX" if kind=="TICKET_CONFIRMATION" else "CSSA_OPERATIONAL_MAILBOX",
        source_ref="sim:source",evidence_refs=("sim:proof",),channel="EMAIL",
        subject="Synthetic "+kind,body="No actual send",owner_ref="SIMULATED:OWNER",
        human_reviewer_ref="SIMULATED:REVIEWER")

KINDS=("MATCH_INFORMATION","MARKETING","TICKET_CONFIRMATION","SUBSCRIPTION",
       "SUPPORTER_REQUEST","PARTNER_INVITATION","PARTNER_DELIVERY","SPONSOR_CONTRACT",
       "INSTITUTIONAL_MESSAGE","OPERATIONAL_REQUEST","REFUND_REQUEST")

def original_food():
    root=os.environ.get("CSSA_HISTORICAL_REPO")
    if not root: pytest.skip("CSSA_HISTORICAL_REPO not configured")
    root=Path(root)
    if str(root) not in sys.path: sys.path.insert(0,str(root))
    src=json.loads((root/"organizations/cssa/matchday_food/buvette_restauration_cases_v0.json").read_text(encoding="utf-8"))
    assert src["status"]=="SIMULATED_NOT_OBSERVED"
    m=importlib.import_module("organizations.cssa.matchday_food.buvette_restauration_v0")
    rows=m.assess_buvette_catalog_v0(src,as_of=date.fromisoformat(src["as_of"]))
    assert len(rows)==16
    return tuple(r for r in rows if r.match_ref=="sim:match:001")

def kwargs():
    return dict(lot_a_verdict=a(),match_ref="sim:match:001",
        matchday_signals=tuple(signal(x) for x in STREAMS),
        communication_cases=tuple(comm(x) for x in KINDS),
        original_f3g_buvette_assessments=original_food())

def test_complete_cross_lot_campaign_closes_synthetic_b():
    r=close_cssa_lot_b_pass6_v0(**kwargs())
    assert r["verdict"]=="LOT_B_CLOSED_SIMULATION",r["failures"]
    assert r["matchday_stream_count"]==11
    assert r["communications_count"]==11
    assert r["f3g_j_assessment_count"]>=1
    assert len(r["incident_routes"])==7
    assert all(x["unrouted"]==() and x["executed"] is False for x in r["incident_routes"])
    assert r["mail_sent"]==r["crm_writes"]==r["external_actions"]==0
    assert r["real_approvals"]==0 and not r["world_action_allowed"]

def test_lot_a_incomplete_blocks_b():
    p=kwargs()
    p["lot_a_verdict"]=dict(a(),season_event_count=903)
    assert close_cssa_lot_b_pass6_v0(**p)["verdict"]=="LOT_B_BLOCKED"

def test_missing_safety_flow_blocks_b():
    p=kwargs()
    p["matchday_signals"]=tuple(s for s in p["matchday_signals"] if s.stream!="SAFETY")
    r=close_cssa_lot_b_pass6_v0(**p)
    assert r["verdict"]=="LOT_B_BLOCKED"
    assert "MATCHDAY_STREAM_COVERAGE_INCOMPLETE" in r["failures"]

def test_missing_refund_notification_breaks_cascade():
    p=kwargs()
    p["communication_cases"]=tuple(c for c in p["communication_cases"] if c.kind!="REFUND_REQUEST")
    assert "UNROUTED_INCIDENT:TICKET_REFUND" in close_cssa_lot_b_pass6_v0(**p)["failures"]

def test_historical_f3g_j_required():
    p=kwargs()
    p["original_f3g_buvette_assessments"]=()
    r=close_cssa_lot_b_pass6_v0(**p)
    assert "ORIGINAL_F3G_J_NOT_LINKED" in r["failures"]

def test_missing_incident_scenario_blocks_closure():
    p=kwargs()
    p["incidents"]=tuple(INCIDENTS)[:-1]
    assert "SEVEN_INCIDENT_FAMILIES_NOT_FULLY_EXERCISED" in close_cssa_lot_b_pass6_v0(**p)["failures"]
