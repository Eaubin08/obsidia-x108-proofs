"""Pass4: all stadium operational streams + real original F3G-J outputs."""
import importlib
import json
import os
import sys
from datetime import date
from pathlib import Path
import pytest
from periphery.cssa_matchday_full_pass4_v0 import (
    STREAMS, MatchdayOperationalSignalV0, evaluate_cssa_matchday_v0,
    draft_f3g_matchday_native_work_v0,
)
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0

def signal(stream, **changes):
    data=dict(signal_id="s:"+stream,match_ref="sim:match:001",stream=stream,
        source_ref="sim:source:"+stream,evidence_refs=("sim:proof:"+stream,),
        owner_ref="SIMULATED:OWNER",occurred_at="2026-10-07T10:00:00+00:00",
        due_at="2026-10-09T15:00:00+00:00",ready=True,authority_verified=False,
        human_reviewer_ref="SIMULATED:REVIEWER")
    data.update(changes)
    return MatchdayOperationalSignalV0(**data)

def test_eleven_workstreams_cannot_open_without_authority():
    report=evaluate_cssa_matchday_v0("sim:match:001",tuple(signal(s) for s in STREAMS),())
    assert report["stream_count"]==11
    assert report["missing_streams"]==()
    assert report["status"]=="HOLD"
    assert report["canonical_native_writes"]==0
    assert report["ready_to_open_stadium"] is False
    assert report["real_approvals"]==0
    assert len(report["report_sha256"])==64

def test_safety_conflict_overrides_other_ready_streams():
    rows=tuple(signal(s,contradictions=("CAPACITY_CONFLICT",) if s=="SAFETY" else ()) for s in STREAMS)
    report=evaluate_cssa_matchday_v0("sim:match:001",rows,())
    assert report["status"]=="BLOCK"
    assert "s:SAFETY" in report["blockers"]

def test_missing_security_and_access_is_not_readiness():
    report=evaluate_cssa_matchday_v0("sim:match:001",(signal("BUVETTE"),),())
    assert "SAFETY" in report["missing_streams"]
    assert report["status"]=="HOLD"

def test_safety_not_ready_blocks():
    rows=tuple(signal(s,ready=False if s=="SAFETY" else True) for s in STREAMS)
    assert evaluate_cssa_matchday_v0("sim:match:001",rows,())["status"]=="BLOCK"

def test_duplicate_and_wrong_match_rejected():
    with pytest.raises(ValueError,match="DUPLICATE"):
        evaluate_cssa_matchday_v0("sim:match:001",(signal("TICKETING"),signal("TICKETING")),())
    with pytest.raises(ValueError,match="MATCH_MISMATCH"):
        evaluate_cssa_matchday_v0("sim:match:001",(signal("TICKETING",match_ref="other"),),())

def _historical():
    root=os.environ.get("CSSA_HISTORICAL_REPO")
    if not root:
        pytest.skip("CSSA_HISTORICAL_REPO not configured")
    path=Path(root)
    if str(path) not in sys.path: sys.path.insert(0,str(path))
    m=importlib.import_module("organizations.cssa.matchday_food.buvette_restauration_v0")
    catalog=json.loads((path/"organizations/cssa/matchday_food/buvette_restauration_cases_v0.json").read_text(encoding="utf-8"))
    assert catalog["status"]=="SIMULATED_NOT_OBSERVED"
    rows=m.assess_buvette_catalog_v0(catalog,as_of=date.fromisoformat(catalog["as_of"]))
    return rows

def test_real_f3g_j_catalog_all_cases_remain_non_executing():
    rows=_historical()
    assert len(rows)==16
    for row in rows:
        assert row.external_action is False
        assert row.decision_authority=="KX108_ONLY"
        draft=draft_f3g_matchday_native_work_v0(row,source_ref="sim:historic:source",
            evidence_refs=("sim:historic:proof",),owner_ref="SIMULATED:OWNER",
            occurred_at="2026-10-07T10:00:00+00:00",
            due_at="2026-10-09T15:00:00+00:00")
        assert draft["canonical_intake_committed"] is False
        assert draft["approval_granted"] is False
        if draft["native_plan"] is not None:
            assert verify_native_case_task_intake_plan_v0(draft["native_plan"])==(True,None)
        else:
            assert draft["status"] in ("HOLD","BLOCK")

def test_actual_f3g_j_buvette_joins_matchday_without_false_match():
    rows=_historical()
    selected=tuple(x for x in rows if x.match_ref=="sim:match:001")
    assert selected
    report=evaluate_cssa_matchday_v0("sim:match:001",
        tuple(signal(s) for s in STREAMS),selected)
    assert report["status"] in ("HOLD","BLOCK")
    assert report["external_actions"]==0
    assert any(x["id"].startswith("F3G:") for x in report["items"])

def test_mismatched_historical_match_cannot_join():
    rows=_historical()
    selected=next(x for x in rows if x.match_ref not in (None,"sim:match:001"))
    with pytest.raises(ValueError,match="MATCH_REF_MISMATCH"):
        evaluate_cssa_matchday_v0("sim:match:001",(),(selected,))
