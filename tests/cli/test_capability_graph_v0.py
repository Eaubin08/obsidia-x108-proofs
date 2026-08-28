"""
tests/cli/test_capability_graph_v0.py
=====================================
Relay-only boundary + native capability expansion V1.

Covers what this mandate ADDS on top of Relay-First V0 (already exercised by
test_relay_first_v0.py):

  * the canonical runtime capability graph  (lookup, never an authority)
  * named test-family / lean-target registries  (CG-1 / CG-2 : no raw path)
  * CAPABILITY_RESOLVED receipt on every mission
  * CG-4 boundary : KIND_GOVERNED_UPDATE -> HOLD for a human EAH; the relay
    orchestrates the HOLD but builds no ExecutionEnvelope and mints no EAH/HMA
  * host permission profile is a PROPOSAL only
    (CLAUDE_DIRECT_REPO_MUTATION_DEFAULT truthfully NOT_PROVEN)
  * operation algebra frozen at UPDATE_TARGET_FROM_SOURCE
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

import obsidia_relay_v0 as R                    # noqa: E402
import obsidia_stack_native_routes_v0 as NAT   # noqa: E402
import obsidia_capability_graph_v0 as G        # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "no_router"))
    yield


def _sd(tmp_path):
    return tmp_path / "store"


# ══════════════════════════════════════════════════════════════════════════
#  §8 / §9 — capability graph : a lookup table, never an authority
# ══════════════════════════════════════════════════════════════════════════

def test_graph_is_not_authority():
    assert G.CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY is False
    assert G.CAPABILITY_GRAPH_IS_KX_AUTHORITY is False
    assert G.KX_DECISION_AUTHORITY == "KX108_ONLY"
    snap = G.graph_snapshot()
    assert snap["is_execution_authority"] is False and snap["is_kx_authority"] is False
    assert set(snap["capabilities"]) == set(G.capability_ids())
    for cap in snap["capabilities"].values():
        assert cap["grants_authority"] is False
        assert cap["is_execution_authority"] is False


@pytest.mark.parametrize("cid,owner,route", [
    ("GIT_STATE_READ", "OBSIDIA_STACK", "STACK_NATIVE_ROUTE"),
    ("TEST_FAMILY_RUN", "OBSIDIA_STACK", "STACK_NATIVE_ROUTE"),
    ("LEAN_BUILD", "OBSIDIA_STACK/FORMAL", "STACK_NATIVE_ROUTE"),
    ("ENGINEERING_REASONING", "COGNITIVE_RESOURCE", "COGNITIVE_CAPABILITY_REQUEST"),
    ("GOVERNED_UPDATE_TARGET_FROM_SOURCE", "OBSIDIA_STACK/STAGE4_RAIL", "STAGE4_GOVERNED_RAIL"),
    ("HUMAN_AUTHORITY", "HUMAN", "HOLD"),
    ("UNKNOWN_AUTHORITY", "HUMAN", "HOLD"),
    ("CONVERSATION", "COGNITIVE_RESOURCE", "COGNITIVE_CAPABILITY_REQUEST"),
])
def test_graph_entries_shape(cid, owner, route):
    c = G.get_capability(cid)
    assert c is not None and c["owner"] == owner and c["route"] == route
    for k in ("capability_id", "family", "mode", "authority_class", "read_write",
              "accepted_input_shape", "availability", "proof_test_status"):
        assert k in c


def test_governed_capability_is_kx_only_and_partial():
    c = G.get_capability("GOVERNED_UPDATE_TARGET_FROM_SOURCE")
    assert c["authority_class"] == "KX108_ONLY"
    assert c["mode"] == "GOVERNED_RAIL"
    assert c["availability"].startswith("PARTIAL_STAGE4_RAIL")
    assert "UPDATE_TARGET_FROM_SOURCE" in c["notes"]
    assert "no CREATE/DELETE/MOVE/RENAME" in c["notes"]
    assert c["is_execution_authority"] is False


def test_resolve_capability_for_kind_and_gap():
    r = G.resolve_capability_for_kind("GIT_STATE_READ")
    assert r["capability_id"] == "GIT_STATE_READ" and r["grants_authority"] is False
    gap = G.resolve_capability_for_kind("SOMETHING_UNMAPPED")
    assert gap["route"] == "HOLD" and gap["gap"] == "STACK_NATIVE_CAPABILITY_GAP"
    assert gap["authority_class"] == "HUMAN" and gap["capability_id"] is None


def test_relay_exposes_graph_surface():
    assert R.relay_capability_graph()["is_execution_authority"] is False
    assert R.relay_resolve_capability(R.KIND_GIT_STATE_READ)["capability_id"] == "GIT_STATE_READ"
    assert R.relay_resolve_capability("NOT_A_KIND")["gap"] == "STACK_NATIVE_CAPABILITY_GAP"


# ══════════════════════════════════════════════════════════════════════════
#  §11 / §12 — named registries only (CG-1 / CG-2), never a model-supplied path
# ══════════════════════════════════════════════════════════════════════════

def test_test_family_registry_named_only():
    ids = NAT.test_family_ids()
    assert "GOVERNANCE_CG_SUITE" in ids and "STAGE4_AUTHORITY_GUARD" in ids
    bad = NAT.run_test_family_by_id("tests/cli/test_relay_first_v0.py")   # raw path
    assert bad["ok"] is False and "TEST_FAMILY_ID_NOT_REGISTERED" in bad["reason"]
    for _fam, targets in NAT.TEST_FAMILY_REGISTRY.items():
        for t in targets:
            assert t.startswith("tests/cli/") and (_REPO_ROOT / t).is_file()


def test_lean_registry_named_only():
    assert set(NAT.lean_target_ids()) == {"MISSION_AUTHORITY", "OBSIDIA_AGGREGATE"}
    bad = NAT.run_lean_by_id("Obsidia.Whatever")
    assert bad["ok"] is False and "LEAN_TARGET_ID_NOT_REGISTERED" in bad["reason"]
    assert set(NAT.LEAN_TARGET_REGISTRY.values()) <= {"Obsidia.MissionAuthority", "Obsidia"}


# ══════════════════════════════════════════════════════════════════════════
#  §21 — E2E pure native (git state) : 0 cognition, CAPABILITY_RESOLVED receipt
# ══════════════════════════════════════════════════════════════════════════

def test_e2e_pure_native_git_state_emits_capability_resolved(tmp_path):
    out = R.relay_submit_mission(requested_outcome="git disposition",
                                 mission_kind=R.KIND_GIT_STATE_READ, store_dir=_sd(tmp_path))
    assert out["mission_state"] == R.MISSION_COMPLETE
    assert out["metrics"]["cognitive_request_count"] == 0
    ev = out["native_evidence"]
    assert ev["ok"] is True and ev["mutated_repo"] is False and len(ev["head"]) == 40
    st = R.relay_get_status(out["relay_mission_id"], store_dir=_sd(tmp_path))
    receipts = [R.relay_get_receipt(r, store_dir=_sd(tmp_path)) for r in st["receipt_ids"]]
    txs = [rc["transition"] for rc in receipts]
    assert "CAPABILITY_RESOLVED" in txs and "NATIVE_CAPABILITY_INVOKED" in txs
    cap_rc = next(rc for rc in receipts if rc["transition"] == "CAPABILITY_RESOLVED")
    assert cap_rc["detail"]["capability_id"] == "GIT_STATE_READ"
    assert cap_rc["detail"]["grants_authority"] is False


# ══════════════════════════════════════════════════════════════════════════
#  §14 / §25 — CG-4 : governed apply HOLDs for a human EAH; relay builds nothing
# ══════════════════════════════════════════════════════════════════════════

def test_cg4_governed_update_holds_for_human_eah(tmp_path):
    g = R.relay_submit_mission(requested_outcome="apply governed update to fixture",
                               mission_kind=R.KIND_GOVERNED_UPDATE, store_dir=_sd(tmp_path))
    assert g["mission_state"] == R.MISSION_HOLD
    assert g["hold_reason"] == "HUMAN_EAH_AUTHORIZATION_REQUIRED"
    m = R._load(_sd(tmp_path), g["relay_mission_id"])
    assert m["governed_apply_route"] == "STAGE4_GOVERNED_RAIL"
    assert m["governed_apply_operation"] == "UPDATE_TARGET_FROM_SOURCE"
    assert m["governed_apply_relay_builds_envelope"] is False
    hold_rc = next(R.relay_get_receipt(r, store_dir=_sd(tmp_path)) for r in m["receipt_ids"]
                   if R.relay_get_receipt(r, store_dir=_sd(tmp_path))["transition"] == "HOLD_OPENED")
    assert hold_rc["detail"]["relay_mints_eah_or_hma"] is False
    assert hold_rc["detail"]["relay_constructs_envelope"] is False
    # a human EAH decision reference resumes the SAME mission (relay never synthesizes it)
    hr = R.relay_respond_to_hold(relay_mission_id=g["relay_mission_id"],
                                 human_decision_ref="human-eah-auth-1",
                                 resolution="operator authorized the exact EAH",
                                 store_dir=_sd(tmp_path))
    assert hr["same_mission_resumed"] is True and hr["scope_expanded"] is False


def test_operation_algebra_frozen():
    for banned in ("CREATE", "DELETE", "MOVE", "RENAME"):
        assert banned not in R._MISSION_KINDS
    assert R.MAX_GOVERNED_MUTATION_OPERATION_V0 == "UPDATE_TARGET_FROM_SOURCE"
    assert R.MULTI_OPERATION_GENERALIZATION == "NOT_YET_PROVEN"


# ══════════════════════════════════════════════════════════════════════════
#  §6 / §7 — host permission boundary : PROPOSAL only, NOT_PROVEN
# ══════════════════════════════════════════════════════════════════════════

def test_host_permission_boundary_is_proposal_and_not_proven():
    assert R.CLAUDE_DIRECT_REPO_MUTATION_DEFAULT == "NOT_PROVEN"
    assert R.CLAUDE_DIRECT_GIT_MUTATION_DEFAULT == "NOT_PROVEN"
    assert R.CLAUDE_ARBITRARY_ENGINEERING_BASH_DEFAULT == "NOT_PROVEN"
    p = R.RELAY_FIRST_HOST_PERMISSION_PROFILE_PROPOSAL_V0
    assert "PROPOSAL ONLY" in p["note"] and "not applied" in p["note"]
    deny = p["permissions"]["deny"]
    for must in ("Edit(**)", "Write(**)", "Bash(git add:*)", "Bash(git commit:*)",
                 "Bash(git push:*)", "Bash(rm:*)"):
        assert must in deny
    for keep in ("Read", "Grep", "Glob", "Task"):
        assert keep in p["permissions"]["allow"]
    assert len(p["verification_steps"]) >= 4


# ══════════════════════════════════════════════════════════════════════════
#  §31 — static / frozen
# ══════════════════════════════════════════════════════════════════════════

def test_capability_graph_module_has_no_sovereign_import_no_shell():
    src = (_SCRIPTS / "obsidia_capability_graph_v0.py").read_text(encoding="utf-8")
    for banned in ("import obsidia_mission_authority_v0", "run_and_persist_kx108",
                   "GuardX108", "atomic_replace_with_bytes", "run_governed_content_apply",
                   "shell=True", "os.system", "subprocess"):
        assert banned not in src, banned


def test_frozen_paths_clean():
    r = subprocess.run(
        ["git", "status", "--porcelain", ".claude/", "proofs/lean/", "formal/", "CLAUDE.md",
         "audit/merkle_seal.json", "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_governed_execution_driver_v0.py",
         "scripts/obsidia_cognitive_capability_lease_v0.py",
         "scripts/obsidia_mission_capability_scope_v0.py",
         "scripts/obsidia_gateway_route_decision_v0.py",
         "scripts/obsidia_pretool_shadow_v0.py"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"frozen modified: {r.stdout}"


def test_cli_self_check_reports_graph_active():
    r = subprocess.run([sys.executable, str(_SCRIPTS / "obsidia_relay_v0.py"), "--self-check"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    d = json.loads(r.stdout)
    assert d["CAPABILITY_GRAPH"] == "ACTIVE"
    assert d["CLAUDE_DIRECT_REPO_MUTATION_DEFAULT"] == "NOT_PROVEN"
    assert "GOVERNED_UPDATE_TARGET_FROM_SOURCE" in d["capability_ids"]
    r2 = subprocess.run([sys.executable, str(_SCRIPTS / "obsidia_capability_graph_v0.py"),
                         "--self-check"], capture_output=True, text=True, timeout=30)
    assert r2.returncode == 0 and json.loads(r2.stdout)["KX_DECISION_AUTHORITY"] == "KX108_ONLY"
