"""
tests/cli/test_relay_first_v0.py
================================
Relay-First vertical cutover V0 : Claude = TRANSPORT + COGNITIVE_RESOURCE_ON_DEMAND,
authority NONE. The stack owns execution, resolves stack-native FIRST, requests
cognition only when required (result = EVIDENCE|PROPOSAL, never authority),
supports HOLD/resume and UNKNOWN resolution with no scope expansion, and emits
receipts for every transition.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_relay_v0 as R                      # noqa: E402
import obsidia_stack_native_routes_v0 as NAT     # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "no_router"))
    yield


def _sd(tmp_path):
    return tmp_path / "store"


# ══════════════════════════════════════════════════════════════════════════
#  §35 — rôles & bornes
# ══════════════════════════════════════════════════════════════════════════

def test_roles_and_bounds():
    assert R.CLAUDE_PRIMARY_ROLE == "TRANSPORT_INTERFACE"
    assert R.CLAUDE_SECONDARY_ROLE == "COGNITIVE_RESOURCE_ON_DEMAND"
    assert R.CLAUDE_EXECUTION_AUTHORITY == "NONE"
    assert R.CLAUDE_HUMAN_AUTHORITY == "NONE"
    assert R.CLAUDE_KX_AUTHORITY == "NONE"
    assert R.CLAUDE_MISSION_AUTHORITY == "NONE"
    assert R.CLAUDE_SCOPE_AUTHORITY == "NONE"
    assert R.CLAUDE_GIT_AUTHORITY == "NONE"
    assert R.STACK_OPERATION_OWNER == "OBSIDIA_CANONICAL_STACK"
    assert R.STACK_NATIVE_FIRST is True
    assert R.KX_DECISION_AUTHORITY == "KX108_ONLY"
    assert R.COGNITIVE_RESULT_IS_EXECUTION_AUTHORITY is False
    assert R.COGNITIVE_RESULT_IS_HUMAN_AUTHORITY is False
    assert R.COGNITIVE_RESULT_IS_KX_AUTHORITY is False
    assert R.MISSION_RELAY == "ACTIVE"
    assert R.HOLD_RESUME == "ACTIVE"
    assert R.UNKNOWN_RESOLUTION == "ACTIVE"
    assert R.MISSION_RECEIPTS == "ACTIVE"
    assert R.OPTIONAL_CLAUDE_DIRECT_TOOL_MODE == "NOT_ACTIVE"
    # CGE-1/CGE-2 reclassified, NOT claimed solved
    assert R.OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_1 == "OPEN"
    assert R.OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_2 == "OPEN"
    assert R.MAX_GOVERNED_MUTATION_OPERATION_V0 == "UPDATE_TARGET_FROM_SOURCE"
    assert R.MULTI_OPERATION_GENERALIZATION == "NOT_YET_PROVEN"


def test_native_routes_are_read_only_no_authority():
    assert NAT.ROUTE_IS_EXECUTION_AUTHORITY is False
    assert NAT.ROUTE_IS_KX_AUTHORITY is False
    assert NAT.ROUTE_MUTATES_REPO is False
    assert NAT.ROUTE_ACCEPTS_ARBITRARY_SHELL is False


# ══════════════════════════════════════════════════════════════════════════
#  §24 — E2E native mission (cognitive_request_count == 0)
# ══════════════════════════════════════════════════════════════════════════

def test_e2e_native_git_state_mission_zero_cognition(tmp_path):
    out = R.relay_submit_mission(requested_outcome="report git disposition",
                                 mission_kind=R.KIND_GIT_STATE_READ, store_dir=_sd(tmp_path))
    assert out["mission_state"] == R.MISSION_COMPLETE
    assert out["metrics"]["cognitive_request_count"] == 0
    assert out["metrics"]["native_route_count"] == 1
    ev = out["native_evidence"]
    assert ev["ok"] is True and ev["is_execution_authority"] is False and ev["mutated_repo"] is False
    assert isinstance(ev["head"], str) and len(ev["head"]) == 40
    st = R.relay_get_status(out["relay_mission_id"], store_dir=_sd(tmp_path))
    assert st["mission_state"] == R.MISSION_COMPLETE and st["claude_authority"] == "NONE"
    assert st["metrics"]["receipt_count"] >= 2
    # receipts are auditable
    for rid in st["receipt_ids"]:
        rc = R.relay_get_receipt(rid, store_dir=_sd(tmp_path))
        assert rc is not None and rc["is_execution_authority"] is False
        assert rc["relay_receipt_id"] == rid


def test_e2e_native_test_family_route(tmp_path):
    tgt = "tests/cli/test_gateway_route_decision_cgb_v0.py"
    assert tgt in NAT.authorized_test_targets()
    out = R.relay_submit_mission(requested_outcome=f"run {tgt}",
                                 mission_kind=R.KIND_TEST_FAMILY_RUN, target=tgt,
                                 store_dir=_sd(tmp_path))
    assert out["mission_state"] == R.MISSION_COMPLETE
    assert out["metrics"]["cognitive_request_count"] == 0
    assert out["native_evidence"]["native_route_kind"] == "TEST_FAMILY_RUN"
    assert out["native_evidence"]["exit_code"] == 0


def test_native_test_family_rejects_unauthorized_target(tmp_path):
    out = R.relay_submit_mission(requested_outcome="run everything",
                                 mission_kind=R.KIND_TEST_FAMILY_RUN,
                                 target="tests/cli/", store_dir=_sd(tmp_path))
    assert out["mission_state"] == R.MISSION_FAILED
    assert "TARGET_NOT_AUTHORIZED" in (out["native_evidence"]["reason"])


def test_native_lean_rejects_unauthorized_module():
    ev = NAT.run_lean_target("Obsidia.Nope")
    assert ev["ok"] is False and "MODULE_NOT_AUTHORIZED" in ev["reason"]


# ══════════════════════════════════════════════════════════════════════════
#  §25 — E2E Claude cognition (SIMULATED, no network)
# ══════════════════════════════════════════════════════════════════════════

def test_e2e_cognitive_roundtrip_evidence(tmp_path):
    c = R.relay_submit_mission(requested_outcome="explain module X",
                               mission_kind=R.KIND_ENGINEERING_REASONING, store_dir=_sd(tmp_path))
    assert c["mission_state"] == R.MISSION_WAITING_CAPABILITY
    assert c["capability_request_ref"].startswith("gcap-")
    assert c["metrics"]["cognitive_request_count"] == 1
    # SIMULATED Claude cognitive result — clearly not a real provider call
    res = R.submit_capability_result(
        relay_mission_id=c["relay_mission_id"], capability_request_ref=c["capability_request_ref"],
        result_kind=R.CAPRESULT_EVIDENCE, summary="SIMULATED_CLAUDE_COGNITIVE_RESULT: analysis",
        produced_by=R.RESOURCE_COGNITIVE_CLAUDE, store_dir=_sd(tmp_path))
    assert res["mission_state"] == R.MISSION_COMPLETE
    assert res["claude_gained_authority"] is False
    crslt = json.loads((_sd(tmp_path) / "relay_missions" / "capability_results"
                        / f"{res['capability_result_id']}.json").read_text(encoding="utf-8"))
    assert crslt["is_execution_authority"] is False and crslt["is_human_authority"] is False
    assert crslt["is_kx_authority"] is False and crslt["grants_scope"] is False


# ══════════════════════════════════════════════════════════════════════════
#  §26 — E2E engineering proposal (Claude gains NO authority)
# ══════════════════════════════════════════════════════════════════════════

def test_e2e_engineering_proposal_no_authority_no_apply(tmp_path):
    c = R.relay_submit_mission(requested_outcome="fix bug in Y",
                               mission_kind=R.KIND_ENGINEERING_REASONING, store_dir=_sd(tmp_path))
    res = R.submit_capability_result(
        relay_mission_id=c["relay_mission_id"], capability_request_ref=c["capability_request_ref"],
        result_kind=R.CAPRESULT_PROPOSAL, summary="patch proposal: change line 42",
        produced_by=R.RESOURCE_COGNITIVE_CLAUDE, store_dir=_sd(tmp_path))
    assert res["mission_state"] == R.MISSION_COMPLETE
    assert res["result_kind"] == R.CAPRESULT_PROPOSAL
    assert res["claude_gained_authority"] is False
    m = json.loads((_sd(tmp_path) / "relay_missions" / f"{c['relay_mission_id']}.json").read_text(encoding="utf-8"))
    assert m["proposal_recorded"] is True
    # governed apply is the Stage 4 rail — NOT invoked by relay V0
    assert m["proposal_apply_route"] == "STAGE4_GOVERNED_RAIL_NOT_INVOKED_IN_RELAY_V0"
    # a PROPOSAL_RECORDED_NO_APPLY receipt exists and says no authority gained
    txs = [R.relay_get_receipt(r, store_dir=_sd(tmp_path))["transition"] for r in m["receipt_ids"]]
    assert "PROPOSAL_RECORDED_NO_APPLY" in txs
    rc = next(R.relay_get_receipt(r, store_dir=_sd(tmp_path)) for r in m["receipt_ids"]
             if R.relay_get_receipt(r, store_dir=_sd(tmp_path))["transition"] == "PROPOSAL_RECORDED_NO_APPLY")
    assert rc["detail"]["claude_gained_authority"] is False


# ══════════════════════════════════════════════════════════════════════════
#  §27 — HOLD / resume (same mission, no restart, no scope expansion)
# ══════════════════════════════════════════════════════════════════════════

def test_hold_resume_same_mission(tmp_path):
    h = R.relay_submit_mission(requested_outcome="authorize production change",
                               mission_kind=R.KIND_HUMAN_DECISION, store_dir=_sd(tmp_path))
    assert h["mission_state"] == R.MISSION_HOLD and h["hold_reason"] == "HUMAN_AUTHORITY_REQUIRED"
    assert h["metrics"]["hold_count"] == 1
    same_id = h["relay_mission_id"]
    hr = R.relay_respond_to_hold(relay_mission_id=same_id, human_decision_ref="human-decision-42",
                                 resolution="approved by operator", store_dir=_sd(tmp_path))
    assert hr["relay_mission_id"] == same_id            # SAME mission
    assert hr["same_mission_resumed"] is True
    assert hr["scope_expanded"] is False
    assert hr["mission_state"] == R.MISSION_COMPLETE
    assert hr["claude_authority"] == "NONE"
    # responding to a non-held mission is rejected
    bad = R.relay_respond_to_hold(relay_mission_id=same_id, human_decision_ref="x",
                                  resolution="y", store_dir=_sd(tmp_path))
    assert bad["status"] == "RELAY_REJECTED"


def test_hold_requires_human_decision_ref(tmp_path):
    h = R.relay_submit_mission(requested_outcome="approve", mission_kind=R.KIND_HUMAN_DECISION,
                               store_dir=_sd(tmp_path))
    bad = R.relay_respond_to_hold(relay_mission_id=h["relay_mission_id"],
                                  human_decision_ref="  ", resolution="ok", store_dir=_sd(tmp_path))
    assert bad["status"] == "RELAY_REJECTED" and bad["reason"] == "HUMAN_DECISION_REF_REQUIRED"


# ══════════════════════════════════════════════════════════════════════════
#  §28 — UNKNOWN resolution (evidence only, no scope expansion, never LLM)
# ══════════════════════════════════════════════════════════════════════════

def test_unknown_goes_to_hold_never_llm(tmp_path):
    u = R.relay_submit_mission(requested_outcome="do the thing",
                               mission_kind=R.KIND_UNKNOWN, store_dir=_sd(tmp_path))
    assert u["mission_state"] == R.MISSION_HOLD
    assert u["hold_reason"] == "UNKNOWN_AUTHORITY"
    assert u["metrics"]["cognitive_request_count"] == 0   # never routed to a model


def test_unknown_resolution_evidence_no_scope_expansion(tmp_path):
    u = R.relay_submit_mission(requested_outcome="need a missing fact",
                               mission_kind=R.KIND_UNKNOWN, store_dir=_sd(tmp_path))
    r = R.resolve_unknown(relay_mission_id=u["relay_mission_id"],
                          missing_fact="which branch is canonical",
                          evidence_summary="branch=feat/... from read_git_state",
                          evidence_resource=R.RESOURCE_STACK_NATIVE, store_dir=_sd(tmp_path))
    assert r["scope_expanded"] is False
    m = json.loads((_sd(tmp_path) / "relay_missions" / f"{u['relay_mission_id']}.json").read_text(encoding="utf-8"))
    assert m["unknown_resolutions"][0]["scope_expanded"] is False
    txs = [R.relay_get_receipt(x, store_dir=_sd(tmp_path))["transition"] for x in m["receipt_ids"]]
    assert "UNKNOWN_EVIDENCE_REINTEGRATED" in txs


def test_unknown_resolution_rejects_unauthorized_evidence_resource(tmp_path):
    u = R.relay_submit_mission(requested_outcome="x", mission_kind=R.KIND_UNKNOWN,
                               store_dir=_sd(tmp_path))
    bad = R.resolve_unknown(relay_mission_id=u["relay_mission_id"], missing_fact="f",
                            evidence_summary="s", evidence_resource="CLAUDE", store_dir=_sd(tmp_path))
    assert bad["status"] == "RELAY_REJECTED"
    assert "EVIDENCE_RESOURCE_NOT_AUTHORIZED" in bad["reason"]


# ══════════════════════════════════════════════════════════════════════════
#  §29 — metrics
# ══════════════════════════════════════════════════════════════════════════

def test_metrics_native_zero_cognition_and_cognitive_counts(tmp_path):
    n = R.relay_submit_mission(requested_outcome="git", mission_kind=R.KIND_GIT_STATE_READ,
                               store_dir=_sd(tmp_path))
    assert n["metrics"] == {"native_route_count": 1, "cognitive_request_count": 0,
                            "hold_count": 0, "receipt_count": n["metrics"]["receipt_count"]}
    assert n["metrics"]["receipt_count"] >= 3
    c = R.relay_submit_mission(requested_outcome="reason", mission_kind=R.KIND_ENGINEERING_REASONING,
                               store_dir=_sd(tmp_path))
    assert c["metrics"]["cognitive_request_count"] == 1 and c["metrics"]["native_route_count"] == 0
    h = R.relay_submit_mission(requested_outcome="decide", mission_kind=R.KIND_HUMAN_DECISION,
                               store_dir=_sd(tmp_path))
    assert h["metrics"]["hold_count"] == 1


# ══════════════════════════════════════════════════════════════════════════
#  §33 self-review invariants / §30 frozen
# ══════════════════════════════════════════════════════════════════════════

def test_submit_capability_result_rejects_authority_producers(tmp_path):
    c = R.relay_submit_mission(requested_outcome="x", mission_kind=R.KIND_ENGINEERING_REASONING,
                               store_dir=_sd(tmp_path))
    bad = R.submit_capability_result(relay_mission_id=c["relay_mission_id"],
                                     capability_request_ref=c["capability_request_ref"],
                                     result_kind="EXECUTION_AUTHORITY", summary="s",
                                     produced_by="HUMAN", store_dir=_sd(tmp_path))
    assert bad["status"] == "RELAY_REJECTED"


def test_capability_result_ref_mismatch_rejected(tmp_path):
    c = R.relay_submit_mission(requested_outcome="x", mission_kind=R.KIND_ENGINEERING_REASONING,
                               store_dir=_sd(tmp_path))
    bad = R.submit_capability_result(relay_mission_id=c["relay_mission_id"],
                                     capability_request_ref="gcap-" + "0" * 32,
                                     result_kind=R.CAPRESULT_EVIDENCE, summary="s",
                                     produced_by=R.RESOURCE_COGNITIVE_CLAUDE, store_dir=_sd(tmp_path))
    assert bad["status"] == "RELAY_REJECTED" and bad["reason"] == "CAPABILITY_REQUEST_REF_MISMATCH"


def test_relay_modules_do_not_import_or_touch_sovereign_semantics():
    for mod in ("obsidia_relay_v0.py", "obsidia_stack_native_routes_v0.py"):
        src = (_SCRIPTS / mod).read_text(encoding="utf-8")
        for banned in ("import obsidia_mission_authority_v0", "run_and_persist_kx108",
                       "GuardX108", "atomic_replace_with_bytes",
                       "run_governed_content_apply", "record_mission_authority_revocation",
                       "shell=True", "os.system"):
            assert banned not in src, f"{mod}:{banned}"


def test_frozen_paths_clean():
    r = subprocess.run(
        ["git", "status", "--porcelain", ".claude/", "proofs/lean/", "formal/", "CLAUDE.md",
         "audit/merkle_seal.json", "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_cognitive_capability_lease_v0.py",
         "scripts/obsidia_mission_capability_scope_v0.py",
         "scripts/obsidia_gateway_route_decision_v0.py",
         "scripts/obsidia_pretool_shadow_v0.py",
         "scripts/obsidia_mission_sequencer_v0.py"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"gelé modifié: {r.stdout}"


def test_host_permission_profile_is_proposal_only():
    p = R.RELAY_FIRST_HOST_PERMISSION_PROFILE_PROPOSAL_V0
    assert "PROPOSAL ONLY" in p["note"]
    assert "Edit(**)" in p["permissions"]["deny"] and "Write(**)" in p["permissions"]["deny"]
    # not applied anywhere: no settings mutation performed by the module
    src = (_SCRIPTS / "obsidia_relay_v0.py").read_text(encoding="utf-8")
    assert "settings.local.json" in src  # only referenced in the proposal comment
    assert ".write_text" in src  # writes only to its own relay store, verified elsewhere


def test_cli_self_check_runs(tmp_path):
    r = subprocess.run([sys.executable, str(_SCRIPTS / "obsidia_relay_v0.py"), "--self-check"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    d = json.loads(r.stdout)
    assert d["CLAUDE_EXECUTION_AUTHORITY"] == "NONE"
    assert d["KX_DECISION_AUTHORITY"] == "KX108_ONLY"
    assert d["OPTIONAL_CLAUDE_DIRECT_TOOL_MODE"] == "NOT_ACTIVE"
