from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import obsidia_pc_capabilities_v1 as PC1
import obsidia_governed_execution_driver_v0 as DRV
import obsidia_test_contract as TC

_CONTENT_A = b"state: BEFORE" + bytes([10]) + b"version: 1" + bytes([10])
_CONTENT_B = b"state: AFTER_GOVERNED_APPLY" + bytes([10]) + b"version: 2" + bytes([10])
_SOURCE_REL = "periphery/source.txt"
_TARGET_REL = "periphery/target.txt"

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {args}: {proc.stderr}"
    return proc.stdout.strip()

@pytest.fixture
def gov_world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / _TARGET_REL).write_bytes(_CONTENT_A)
    (main / _SOURCE_REL).write_bytes(_CONTENT_B)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "v1t@example.com")
    _git(main, "config", "user.name", "v1test")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET_REL, _SOURCE_REL)
    _git(main, "commit", "-q", "-m", "v1 seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "v1-test-br", base_sha)
    stores_base = tmp_path / "stores"
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha,
            "stores_base": stores_base, "target_abs": exec_wt / _TARGET_REL}

def _positive_contract() -> dict:
    marker = ("import pathlib,sys;"
               + "c=pathlib.Path(" + repr(_TARGET_REL) + ").read_text();"
               + "sys.exit(0 if chr(65)+chr(70)+chr(84)+chr(69)+chr(82)"
               + "+chr(95)+chr(71)+chr(79)+chr(86)+chr(69)+chr(82)"
               + "+chr(78)+chr(69)+chr(68)+chr(95)+chr(65)+chr(80)"
               + "+chr(80)+chr(76)+chr(89) in c else 1)")
    checks = [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256,
                        target_path=_TARGET_REL, expected_target_sha256=_sha(_CONTENT_B), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                        expected_diff_paths=[_TARGET_REL], required=True),
        TC.build_check("marker", TC.CHECK_TYPE_SUBPROCESS,
                        argv=[sys.executable, "-c", marker],
                        expected_exit_code=0, required=True),
    ]
    return TC.build_test_contract("v1-positive", "v1test", "v1-batch", _TARGET_REL, checks)

def _do_prepare(w, *, session_id=""):
    return PC1.pc_governed_prepare(
        source_git_commit=w["base_sha"],
        source_historical_path=_SOURCE_REL,
        target_path=_TARGET_REL,
        test_contract=_positive_contract(),
        execution_worktree_path=w["exec_wt"],
        main_worktree_path=w["main"],
        branch_name="v1-test-br",
        base_sha=w["base_sha"],
        stores_base_dir=w["stores_base"],
        session_id=session_id,
    )

# ---- module invariants --------------------------------------------------
def test_v1_self_check_invariants():
    sc = PC1.self_check_v1()
    assert sc["mode"] == "GOVERNED_WRITE"
    assert sc["is_execution_authority"] is False
    assert sc["is_kx_authority"] is False
    assert sc["decision_authority"] == "KX108_ONLY"
    assert sc["human_approval_required"] is True
    assert sc["auto_execute"] is False
    assert sc["jarvis_authority"] == "NONE"
    assert sc["mutates_filesystem"] is True
    assert sc["accepts_arbitrary_shell"] is False
    assert sc["generic_shell_enabled"] is False
    assert set(sc["capabilities"]) == {"PC_GOVERNED_PREPARE", "PC_GOVERNED_EXECUTE"}

# ---- PREPARE causes no mutation -----------------------------------------
def test_prepare_causes_no_mutation(gov_world):
    w = gov_world
    before = w["target_abs"].read_bytes()
    out = _do_prepare(w)
    assert out["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL, out
    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["target_mutated"] is False
    assert out["kx108_invocations"] == 0
    assert out["human_approval_created"] is False
    assert out["human_authorization_consumed"] is False
    assert len(out["execution_authority_hash"]) == 64
    assert w["target_abs"].read_bytes() == before
    assert out["receipt"]["human_approval_required"] is True
    assert out["receipt"]["auto_execute"] is False

def test_prepare_receipt_invariants(gov_world):
    w = gov_world
    out = _do_prepare(w, session_id="jws-0102030405060708090a")
    r = out["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["session_id"] == "jws-0102030405060708090a"
    assert r["receipt_id"].startswith("pcrcp-v1-")
    assert r["execution_authority_hash"] == out["execution_authority_hash"]

def test_before_digest_correct(gov_world):
    out = _do_prepare(gov_world)
    assert out["j5_target_pre_sha256"] == _sha(_CONTENT_A)

# ---- EXECUTE blocked tests -----------------------------------------------
def test_execute_blocked_without_eah(gov_world):
    w = gov_world
    out = _do_prepare(w)
    assert out["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    result = PC1.pc_governed_execute(out, "", "HUMAN_REF", stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == "EAH_MISMATCH"
    assert w["target_abs"].read_bytes() == _CONTENT_A

def test_execute_blocked_wrong_eah(gov_world):
    w = gov_world
    out = _do_prepare(w)
    result = PC1.pc_governed_execute(out, "a" * 64, "HUMAN_REF", stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == "EAH_MISMATCH"
    assert w["target_abs"].read_bytes() == _CONTENT_A

def test_execute_blocked_missing_human_ref(gov_world):
    w = gov_world
    out = _do_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC1.pc_governed_execute(out, eah, "", stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"
    assert w["target_abs"].read_bytes() == _CONTENT_A

def test_execute_blocked_wrong_phase():
    fake = {"j5_phase": "EXECUTE", "status": DRV.PREPARED_AWAITING_HUMAN_APPROVAL, "execution_authority_hash": "e"*64}
    result = PC1.pc_governed_execute(fake, "e"*64, "ref", stores_base_dir="/tmp", repo_root="/tmp")
    assert result["status"] == "PREPARE_PHASE_REQUIRED"

def test_execute_blocked_wrong_status():
    fake = {"j5_phase": "PREPARE", "status": "PREPARE_REJECTED", "execution_authority_hash": "e"*64}
    result = PC1.pc_governed_execute(fake, "e"*64, "ref", stores_base_dir="/tmp", repo_root="/tmp")
    assert result["status"] == "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED"

def test_dispatcher_unknown_v1():
    r = PC1.execute_pc_capability_v1("NO_SUCH_V1_CAP", {})
    assert r["status"] == "CAPABILITY_NOT_FOUND_V1"

# ---- e2e success (full chain) -------------------------------------------
def test_e2e_prepare_then_execute_keep(gov_world):
    w = gov_world
    assert w["target_abs"].read_bytes() == _CONTENT_A
    out = _do_prepare(w, session_id="jws-v1e2e00000000000000a")
    assert out["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL, out
    assert w["target_abs"].read_bytes() == _CONTENT_A
    eah = out["execution_authority_hash"]
    result = PC1.pc_governed_execute(
        out, eah, "HUMAN_EXPLICIT_V1_E2E_001",
        stores_base_dir=w["stores_base"],
        repo_root=w["exec_wt"],
        session_id="jws-v1e2e00000000000000a",
    )
    assert result["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, result
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result["kx108_post_gate"] == "ALLOW"
    assert result["j5_phase"] == "EXECUTE"
    assert result["jarvis_authority"] == "NONE"
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["human_authorization_consumed"] is True
    assert result["human_authorization_reference"] == "HUMAN_EXPLICIT_V1_E2E_001"
    assert result["sealed_apply_receipt_id"] is not None
    assert result["sealed_rollback_evidence_id"] is not None
    assert w["target_abs"].read_bytes() == _CONTENT_B
    r = result["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r["sealed_apply_receipt_id"] is not None

def test_after_digest_correct(gov_world):
    w = gov_world
    out = _do_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC1.pc_governed_execute(out, eah, "HUMAN_DIGEST_CHECK",
                                     stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert _sha(w["target_abs"].read_bytes()) == _sha(_CONTENT_B)

def test_dispatcher_routes_prepare(gov_world):
    w = gov_world
    payload = {"source_git_commit": w["base_sha"], "source_historical_path": _SOURCE_REL,
               "target_path": _TARGET_REL, "test_contract": _positive_contract(),
               "execution_worktree_path": str(w["exec_wt"]),
               "main_worktree_path": str(w["main"]),
               "branch_name": "v1-test-br", "base_sha": w["base_sha"],
               "stores_base_dir": str(w["stores_base"])}
    out = PC1.execute_pc_capability_v1("PC_GOVERNED_PREPARE", payload)
    assert out["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["target_mutated"] is False

# ---- rollback evidence + restore ----------------------------------------
def test_rollback_evidence_verifiable(gov_world):
    import obsidia_sealed_evidence_v0 as SEV
    w = gov_world
    out = _do_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC1.pc_governed_execute(out, eah, "HUMAN_ROLLBACK_CHECK",
                                     stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    sre_id = result["sealed_rollback_evidence_id"]
    stores = PC1._stores(w["stores_base"])
    sre = SEV.load_sealed_rollback_evidence(sre_id, stores["sre"])
    ok, reason = SEV.verify_sealed_rollback_evidence(sre)
    assert ok is True, reason

def test_rollback_restores_before_state(gov_world):
    import obsidia_sealed_evidence_v0 as SEV
    import obsidia_governed_rollback_v0 as RB
    w = gov_world
    assert w["target_abs"].read_bytes() == _CONTENT_A
    out = _do_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC1.pc_governed_execute(out, eah, "HUMAN_ROLLBACK_RESTORE",
                                     stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert w["target_abs"].read_bytes() == _CONTENT_B
    stores = PC1._stores(w["stores_base"])
    sre = SEV.load_sealed_rollback_evidence(result["sealed_rollback_evidence_id"], stores["sre"])
    rb = RB.run_governed_rollback(
        sre["child_execution_id"],
        sre["kx108_pre_decision_record_id"],
        rollback_trigger_code="KX108_POST_INVOCATION_FAILURE",
        sealed_rollback_evidence_id=result["sealed_rollback_evidence_id"],
        sealed_rollback_evidence_dir=stores["sre"],
        repo_root=w["exec_wt"],
        rollback_result_dir=stores["rollback"],
        pre_decision_store_dir=stores["kxpre"],
        execution_dir=stores["execution"],
        evidence_dir=stores["sar"],
    )
    assert rb.get("status") in (
        "ROLLBACK_SUCCEEDED", "ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED"), rb
    assert w["target_abs"].read_bytes() == _CONTENT_A

# ---- OpenJarvis cannot bypass PREPARE -----------------------------------
def test_openjarvis_cannot_bypass_prepare(gov_world):
    w = gov_world
    fake = {"j5_phase": "PREPARE", "status": DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "b"*64, "_prepared_internal": {}}
    result = PC1.pc_governed_execute(fake, "b"*64, "OJ_BYPASS_ATTEMPT",
                                     stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] not in (DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, "OK")
    assert w["target_abs"].read_bytes() == _CONTENT_A

# ---- Binder registration ------------------------------------------------
def test_pc_governed_caps_registered_in_graph():
    import obsidia_capability_graph_v0 as G
    ids = set(G.capability_ids())
    assert "PC_GOVERNED_PREPARE" in ids
    assert "PC_GOVERNED_EXECUTE" in ids

def test_pc_governed_authority_class():
    import obsidia_capability_graph_v0 as G
    prep = G.get_capability("PC_GOVERNED_PREPARE")
    exe  = G.get_capability("PC_GOVERNED_EXECUTE")
    assert prep["authority_class"] == "KX108_ONLY"
    assert exe["authority_class"] == "KX108_ONLY"
    assert prep["grants_authority"] is False
    assert exe["grants_authority"] is False
    assert exe["read_write"] == "WRITE_GOVERNED"
    assert prep["read_write"] == "NONE"
