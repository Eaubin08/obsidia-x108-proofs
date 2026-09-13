import hashlib,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]))
import pytest
from periphery.agents.obsidure_repair_execution_handoff import (
    STATUS_HOLD,STATUS_READY,build_repair_execution_handoff,
)

_B={"decision_authority":"KX108_ONLY","emits_act":False,"emits_verdict":False,
    "kernel_mutation":False,"memory_write":False,"canonical_write":False,
    "auto_apply":False,"auto_commit":False,"auto_push":False,
    "sandbox_mode":"HUMAN_APPROVED_WRITE","external_engine_role":"PROPOSE_ONLY"}
_TARGET="periphery/agents/foo_repair_target.py"
_CONTENT=b"x=42" + bytes([10])
_SHA256=hashlib.sha256(_CONTENT).hexdigest()

def _c278_ok(request_id="rr_t1",proposal_id="rp_t1"):
    return {"stage":"C278","phase":"PROPOSAL_MEANING","evidence":"CONTINUOUS",
            "proposal_id":proposal_id,"request_id":request_id,
            "readonly":True,"advisory_only":True,"allowed_to_decide":False,
            "allowed_to_act":False,"emits_act":False,"emits_verdict":False,
            "decision_authority":"KX108_ONLY"}

def _cand(path=_TARGET,base_sha256=""):
    return {"path":path,"full_content":_CONTENT.decode(),"base_sha256":base_sha256,"change_kind":"MODIFY"}

def _prop(proposal_id="rp_t1",request_id="rr_t1",candidates=None):
    return {"proposal_id":proposal_id,"request_id":request_id,
            "rationale":"fix the broken thing",
            "candidate_files":(candidates if candidates is not None else [_cand()]),
            "confidence":"HIGH","boundary":dict(_B)}

def _req(request_id="rr_t1"):
    return {"request_id":request_id,"objective":"fix the broken thing",
            "repo_targets":["periphery/"],"boundary":dict(_B)}

def _verdict(sandbox_dir,sha256=_SHA256,request_id="rr_t1",proposal_id="rp_t1",status="PASS"):
    return {"verdict_id":"rv_t1","request_id":request_id,"proposal_id":proposal_id,
            "status":status,"sandbox_dir":sandbox_dir,"errors":[],
            "tested_artifacts":[{"path":_TARGET,"sha256":sha256}],
            "boundary":dict(_B)}

def _write_sb(tmpdir,content=_CONTENT):
    sb=pathlib.Path(tmpdir)/"sb"
    t=sb/_TARGET; t.parent.mkdir(parents=True,exist_ok=True); t.write_bytes(content)
    return str(sb)

def test_happy_path(tmp_path):
    sb=_write_sb(tmp_path)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),
                                      c278_evidence=_c278_ok(),verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_READY
    assert r["write_capability"] is False
    assert r["authority"]=="NON_SOVEREIGN"
    # No child dict: handoff exposes verified source facts, not canonical ChildExecutionRecord
    assert "child" not in r
    assert r["source_content_sha256"]==_SHA256
    assert r["target_path"]==_TARGET
    assert r["sandbox_artifact_path"]  # non-empty absolute path
    p=r["provenance_refs"]
    assert p["repair_request_id"]=="rr_t1"
    assert p["repair_proposal_id"]=="rp_t1"
    assert p["repair_verdict_id"]=="rv_t1"
    assert p["c278_evidence"]=="CONTINUOUS"
    assert "human_approval" not in str(r).lower()
    assert "kx108" not in str(r).lower()

def test_hold_c278_absent(tmp_path):
    sb=_write_sb(tmp_path)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=None,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert r["reason"]=="C278_EVIDENCE_ABSENT"

def test_hold_c278_divergent(tmp_path):
    sb=_write_sb(tmp_path)
    ev=_c278_ok(); ev["evidence"]="DIVERGENT"
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=ev,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "C278_EVIDENCE_NOT_CONTINUOUS" in r["reason"]

def test_hold_c278_incomplete(tmp_path):
    sb=_write_sb(tmp_path)
    ev=_c278_ok(); ev["evidence"]="INCOMPLETE"
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=ev,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "C278_EVIDENCE_NOT_CONTINUOUS" in r["reason"]

def test_hold_verdict_blocked(tmp_path):
    sb=_write_sb(tmp_path)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=_verdict(sb,status="BLOCKED"),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert r["reason"]=="VERDICT_NOT_PASS"

def test_hold_verdict_partial(tmp_path):
    sb=_write_sb(tmp_path)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=_verdict(sb,status="PARTIAL"),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert r["reason"]=="VERDICT_NOT_PASS"

def test_hold_forged_proposal_id(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["proposal_id"]="rp_forged"
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "PROVENANCE_MISMATCH_PROPOSAL_ID" in r["reason"]

def test_hold_forged_request_id(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb,request_id="rr_forged")
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "PROVENANCE_MISMATCH_REQUEST_ID" in r["reason"]

def test_verdict_id_in_provenance(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["verdict_id"]="rv_forged_check"
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_READY
    assert r["provenance_refs"]["repair_verdict_id"]=="rv_forged_check"

def test_hold_zero_candidates(tmp_path):
    sb=_write_sb(tmp_path)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(candidates=[]),
                                      c278_evidence=_c278_ok(),verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert r["reason"]=="NO_CANDIDATE_FILES"

def test_hold_multi_candidate(tmp_path):
    sb=_write_sb(tmp_path)
    p=_prop(candidates=[_cand(),_cand(path="periphery/agents/bar.py")])
    r=build_repair_execution_handoff(request=_req(),proposal=p,c278_evidence=_c278_ok(),
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert r["reason"]=="MULTI_PATCH_AMBIGUITY"
    assert r["patch_count"]==2

def test_hold_sandbox_bytes_changed(tmp_path):
    sb=_write_sb(tmp_path,content=b"x=42" + bytes([10]))
    wrong=hashlib.sha256(b"x=999" + bytes([10])).hexdigest()
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=_verdict(sb,sha256=wrong),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "SANDBOX_BYTES_CHANGED_SINCE_VERDICT" in r["reason"]

def test_hold_malformed_sha256(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["tested_artifacts"]=[{"path":_TARGET,"sha256":"tooshort"}]
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "MALFORMED" in r["reason"]

def test_hold_tested_artifacts_absent(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["tested_artifacts"]=[]
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD; assert "TESTED_ARTIFACT_SHA256_ABSENT" in r["reason"]

def test_target_drift_fails_closed(tmp_path):
    t=tmp_path/_TARGET; t.parent.mkdir(parents=True,exist_ok=True)
    t.write_bytes(b"different content" + bytes([10]))
    base=hashlib.sha256(b"original" + bytes([10])).hexdigest()
    sb=_write_sb(tmp_path)
    p=_prop(candidates=[_cand(base_sha256=base)])
    r=build_repair_execution_handoff(request=_req(),proposal=p,c278_evidence=_c278_ok(),
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="TARGET_DRIFT_SINCE_REPAIR_TEST"
    assert r["write_capability"] is False

# ===== R2 Issue 8: new tests =====

def test_hold_c278_request_id_absent(tmp_path):
    sb=_write_sb(tmp_path)
    ev=_c278_ok(); ev["request_id"]=""
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=ev,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="C278_REQUEST_ID_ABSENT"

def test_hold_c278_wrong_request_id(tmp_path):
    sb=_write_sb(tmp_path)
    ev=_c278_ok(request_id="rr_wrong")
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=ev,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="C278_REQUEST_ID_MISMATCH"

def test_hold_c278_wrong_proposal_id(tmp_path):
    sb=_write_sb(tmp_path)
    ev=_c278_ok(proposal_id="rp_wrong")
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=ev,
                                      verdict=_verdict(sb),repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="C278_PROPOSAL_ID_MISMATCH"

def test_hold_verdict_id_absent(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["verdict_id"]=""
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="VERDICT_ID_ABSENT"

def test_hold_verdict_proposal_id_absent(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["proposal_id"]=""
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert r["reason"]=="VERDICT_PROPOSAL_ID_ABSENT"

def test_hold_sha256_uppercase_rejected(tmp_path):
    sb=_write_sb(tmp_path)
    upper_sha=_SHA256.upper()
    v=_verdict(sb,sha256=upper_sha)
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert "MALFORMED" in r["reason"]

def test_hold_sha256_nonhex_rejected(tmp_path):
    sb=_write_sb(tmp_path)
    v=_verdict(sb); v["tested_artifacts"]=[{"path":_TARGET,"sha256":"x"*64}]
    r=build_repair_execution_handoff(request=_req(),proposal=_prop(),c278_evidence=_c278_ok(),
                                      verdict=v,repo_root=tmp_path)
    assert r["status"]==STATUS_HOLD
    assert "MALFORMED" in r["reason"]

def test_end_to_end_requires_canonical_execution_context(tmp_path):
    import sys
    import pathlib as _pl

    sys.path.insert(
        0,
        str(_pl.Path(__file__).resolve().parents[2] / "scripts"),
    )

    from obsidia_repair_execution_adapter_v0 import (
        prepare_repair_governed_execution,
        STATUS_PREP_HOLD,
    )

    # R3A couvre volontairement REPLACE uniquement.
    # Mat?rialiser une vraie pr?image cible afin que le handoff transporte
    # target_pre_sha256 ; le test v?rifie ensuite sp?cifiquement l'absence
    # du contexte/worktree canonique.
    target = tmp_path / _TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"original target bytes\n")

    sb = _write_sb(tmp_path)

    handoff = build_repair_execution_handoff(
        request=_req(),
        proposal=_prop(),
        c278_evidence=_c278_ok(),
        verdict=_verdict(sb),
        repo_root=tmp_path,
    )

    assert handoff["status"] == STATUS_READY

    # L'ancien appel R2, sans worktree/PEC, doit d?sormais ?chouer ferm?.
    result = prepare_repair_governed_execution(
        handoff=handoff,
        ledger_dir=tmp_path / "ledger",
        selector_dir=tmp_path / "selector",
        execution_dir=tmp_path / "execution",
    )

    assert result["status"] == STATUS_PREP_HOLD
    assert result["reason"] == "EXECUTION_WORKTREE_PATH_ABSENT"
    assert result["write_capability"] is False
    assert result["kx108_invoked"] is False
    assert result["human_approval_present"] is False
