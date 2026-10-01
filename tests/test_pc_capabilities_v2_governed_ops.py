from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import obsidia_sealed_evidence_v0 as SEV

_SHA = lambda b: hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture
def v2_world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / "periphery" / "alpha.txt").write_bytes(b"alpha v1\n")
    (main / "periphery" / "beta.txt").write_bytes(b"beta v1\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "v2t@test.com")
    _git(main, "config", "user.name", "v2test")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "v2 seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "v2-test-br", base_sha)
    stores = tmp_path / "stores"
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha, "stores": stores}


def _base(w):
    return dict(
        execution_worktree_path=w["exec_wt"],
        main_worktree_path=w["main"],
        branch_name="v2-test-br",
        base_sha=w["base_sha"],
        stores_base_dir=w["stores"],
    )


def _valid_patch_alpha():
    return (
        "--- a/periphery/alpha.txt\n"
        "+++ b/periphery/alpha.txt\n"
        "@@ -1 +1 @@\n"
        "-alpha v1\n"
        "+alpha v2\n"
    )


# ============================================================
# Module invariants + dispatcher
# ============================================================

def test_v2_self_check_invariants():
    sc = PC2.self_check_v2()
    assert sc["version"] == "V2"
    assert sc["mode"] == "GOVERNED_WRITE"
    assert sc["is_execution_authority"] is False
    assert sc["is_kx_authority"] is False
    assert sc["decision_authority"] == "KX108_ONLY"
    assert sc["jarvis_authority"] == "NONE"
    assert sc["human_approval_required"] is True
    assert sc["auto_execute"] is False
    assert sc["accepts_arbitrary_shell"] is False
    assert sc["generic_shell_enabled"] is False
    assert sc["governed_delete_file"] == "DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS"
    assert sc["new_parallel_mutation_engine"] is False
    assert sc["generic_write_file_enabled"] is False
    assert sc["openjarvis_authority"] == "NONE"
    assert sc["kx108_only"] is True


def test_v2_dispatcher_unknown():
    r = PC2.execute_pc_capability_v2("NO_SUCH_V2")
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"


# ============================================================
# Capability graph registration
# ============================================================

def test_v2_caps_registered_in_graph():
    import obsidia_capability_graph_v0 as G
    ids = set(G.capability_ids())
    for cid in PC2._CAPABILITY_IDS_V2:
        assert cid in ids, f"{cid} not in graph"


def test_v2_caps_authority_class():
    import obsidia_capability_graph_v0 as G
    for cid in PC2._CAPABILITY_IDS_V2:
        cap = G.get_capability(cid)
        assert cap["authority_class"] == "KX108_ONLY", cid
        assert cap["grants_authority"] is False, cid
        assert cap["family"] == "PC_GOVERNED_WRITE", cid


def test_v2_execute_caps_rw_governed():
    import obsidia_capability_graph_v0 as G
    for cid in ("PC_V2_CREATE_FILE_EXECUTE", "PC_V2_MOVE_FILE_EXECUTE", "PC_V2_APPLY_PATCH_EXECUTE"):
        cap = G.get_capability(cid)
        assert cap["read_write"] == "WRITE_GOVERNED", cid


def test_v2_prepare_caps_rw_none():
    import obsidia_capability_graph_v0 as G
    for cid in ("PC_V2_CREATE_FILE_PREPARE", "PC_V2_MOVE_FILE_PREPARE", "PC_V2_APPLY_PATCH_PREPARE"):
        cap = G.get_capability(cid)
        assert cap["read_write"] == "NONE", cid


# ============================================================
# GOVERNED_CREATE_FILE
# ============================================================

def test_create_file_prepare_no_mutation(v2_world):
    w = v2_world
    new_file = w["exec_wt"] / "periphery" / "new.txt"
    assert not new_file.exists()
    out = PC2.pc_v2_create_file_prepare("periphery/new.txt", b"hello world\n", **_base(w))
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert out["decision_authority"] == "KX108_ONLY"
    assert len(out["execution_authority_hash"]) == 64
    assert out["target_pre_sha256"] == PC2._EMPTY_SHA256
    assert not new_file.exists(), "PREPARE must not create target"
    r = out["receipt"]
    assert r["human_approval_required"] is True
    assert r["auto_execute"] is False


def test_create_file_prepare_rejects_existing_target(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_file_prepare("periphery/alpha.txt", b"new content", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "TARGET_ALREADY_EXISTS" in out["reason"]


def test_create_file_prepare_rejects_traversal(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_file_prepare("../escape.txt", b"evil", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED


def test_create_file_prepare_rejects_non_bytes(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_file_prepare("periphery/new.txt", "string not bytes", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "CONTENT_MUST_BE_BYTES" in out["reason"]


def test_create_file_prepare_receipt_invariants(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_file_prepare(
        "periphery/new2.txt", b"x", **_base(w), session_id="jws-v2create00000000000")
    r = out["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["session_id"] == "jws-v2create00000000000"
    assert r["receipt_id"].startswith("pcrcp-v2-")
    assert r["execution_authority_hash"] == out["execution_authority_hash"]


def test_create_file_execute_blocked_eah_mismatch(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_file_prepare("periphery/new.txt", b"hello\n", **_base(w))
    result = PC2.pc_v2_create_file_execute(
        prep, "a" * 64, "HUMAN_REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED
    assert not (w["exec_wt"] / "periphery" / "new.txt").exists()


def test_create_file_execute_blocked_missing_ref(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_file_prepare("periphery/new.txt", b"hello\n", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_file_execute(
        prep, eah, "", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED
    assert not (w["exec_wt"] / "periphery" / "new.txt").exists()


def test_create_file_execute_blocked_wrong_phase(v2_world):
    w = v2_world
    fake = {"j5_phase": "EXECUTE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "e" * 64}
    result = PC2.pc_v2_create_file_execute(
        fake, "e" * 64, "REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED


def test_create_file_execute_blocked_wrong_status(v2_world):
    w = v2_world
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARE_REJECTED,
            "execution_authority_hash": "e" * 64}
    result = PC2.pc_v2_create_file_execute(
        fake, "e" * 64, "REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED


def test_create_file_e2e(v2_world):
    w = v2_world
    content = b"created by V2 governed\n"
    prep = PC2.pc_v2_create_file_prepare("periphery/new.txt", content, **_base(w))
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_file_execute(
        prep, eah, "HUMAN_EXPLICIT_V2_CREATE_001",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result["human_authorization_consumed"] is True
    assert result["jarvis_authority"] == "NONE"
    assert result["decision_authority"] == "KX108_ONLY"
    new_file = w["exec_wt"] / "periphery" / "new.txt"
    assert new_file.exists()
    assert new_file.read_bytes() == content
    assert result["target_post_sha256"] == _SHA(content)
    assert result["sealed_apply_receipt_id"] is not None
    assert result["sealed_rollback_evidence_id"] is not None


def test_create_file_execute_receipt_invariants(v2_world):
    w = v2_world
    content = b"receipt check\n"
    prep = PC2.pc_v2_create_file_prepare(
        "periphery/rcpt.txt", content, **_base(w), session_id="jws-rcptcheck000000000")
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_file_execute(
        prep, eah, "HUMAN_RCPT_V2",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"],
        session_id="jws-rcptcheck000000000")
    assert result["status"] == PC2.EXECUTED_OK
    r = result["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r["sealed_apply_receipt_id"] is not None


def test_create_file_creates_parent_dirs(v2_world):
    w = v2_world
    content = b"nested file\n"
    prep = PC2.pc_v2_create_file_prepare("newdir/subdir/file.txt", content, **_base(w))
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_file_execute(
        prep, eah, "HUMAN_NESTED_DIR",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    assert (w["exec_wt"] / "newdir" / "subdir" / "file.txt").read_bytes() == content


def test_create_file_rollback_evidence_verifiable(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_file_prepare("periphery/rbv.txt", b"rbv\n", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_file_execute(
        prep, eah, "HUMAN_RBV", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK
    sre_id = result["sealed_rollback_evidence_id"]
    st = PC2._stores(w["stores"])
    sre = SEV.load_sealed_rollback_evidence(sre_id, st["sre"])
    assert sre is not None, f"SRE not found: {sre_id}"
    assert sre["sealed"] is True
    assert sre["sealed_rollback_evidence_id"] == sre_id
    assert sre["decision_authority"] == "KX108_ONLY"
    assert sre["pre_write_sha256"] == PC2._EMPTY_SHA256


# ============================================================
# GOVERNED_MOVE_FILE
# ============================================================

def test_move_file_prepare_no_mutation(v2_world):
    w = v2_world
    src = w["exec_wt"] / "periphery" / "alpha.txt"
    dst = w["exec_wt"] / "periphery" / "alpha_moved.txt"
    assert src.exists()
    assert not dst.exists()
    out = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_moved.txt", **_base(w))
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert out["decision_authority"] == "KX108_ONLY"
    assert len(out["execution_authority_hash"]) == 64
    assert src.exists(), "source must not be touched by PREPARE"
    assert not dst.exists(), "dest must not be created by PREPARE"


def test_move_file_prepare_source_not_found(v2_world):
    w = v2_world
    out = PC2.pc_v2_move_file_prepare(
        "periphery/nonexistent.txt", "periphery/dest.txt", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "SOURCE_NOT_FOUND" in out["reason"]


def test_move_file_prepare_dest_already_exists(v2_world):
    w = v2_world
    out = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/beta.txt", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "DEST_ALREADY_EXISTS" in out["reason"]


def test_move_file_prepare_source_equals_dest(v2_world):
    w = v2_world
    out = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha.txt", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert out["reason"] in ("DEST_ALREADY_EXISTS", "SOURCE_EQUALS_DEST")


def test_move_file_prepare_unsafe_source_path(v2_world):
    w = v2_world
    out = PC2.pc_v2_move_file_prepare("../escape.txt", "periphery/dest.txt", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED


def test_move_file_execute_blocked_eah_mismatch(v2_world):
    w = v2_world
    prep = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_moved.txt", **_base(w))
    result = PC2.pc_v2_move_file_execute(
        prep, "b" * 64, "HUMAN_REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED
    assert (w["exec_wt"] / "periphery" / "alpha.txt").exists(), "source unchanged"
    assert not (w["exec_wt"] / "periphery" / "alpha_moved.txt").exists()


def test_move_file_execute_blocked_missing_ref(v2_world):
    w = v2_world
    prep = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_moved.txt", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        prep, eah, "", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED


def test_move_file_e2e(v2_world):
    w = v2_world
    src_bytes = b"alpha v1\n"
    prep = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_moved.txt", **_base(w))
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert prep["source_sha256"] == _SHA(src_bytes)
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        prep, eah, "HUMAN_EXPLICIT_V2_MOVE_001",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result["human_authorization_consumed"] is True
    assert not (w["exec_wt"] / "periphery" / "alpha.txt").exists()
    moved = w["exec_wt"] / "periphery" / "alpha_moved.txt"
    assert moved.exists()
    assert moved.read_bytes() == src_bytes
    assert result["sealed_apply_receipt_id"] is not None
    assert result["sealed_rollback_evidence_id"] is not None


def test_move_file_rollback_evidence_contains_source_bytes(v2_world):
    w = v2_world
    src_bytes = b"alpha v1\n"
    prep = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_rb.txt", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        prep, eah, "HUMAN_MOVE_RB",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK
    sre_id = result["sealed_rollback_evidence_id"]
    st = PC2._stores(w["stores"])
    sre = SEV.load_sealed_rollback_evidence(sre_id, st["sre"])
    assert sre is not None, f"SRE not found: {sre_id}"
    assert sre["sealed"] is True
    import base64
    stored = base64.b64decode(sre["pre_write_bytes_b64"])
    assert stored == src_bytes


def test_move_file_receipt_invariants(v2_world):
    w = v2_world
    prep = PC2.pc_v2_move_file_prepare(
        "periphery/alpha.txt", "periphery/alpha_rcpt.txt", **_base(w),
        session_id="jws-movercpt000000000000")
    r = prep["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["session_id"] == "jws-movercpt000000000000"
    assert r["receipt_id"].startswith("pcrcp-v2-")
    assert r["execution_authority_hash"] == prep["execution_authority_hash"]


# ============================================================
# GOVERNED_APPLY_PATCH
# ============================================================

def test_apply_patch_rejects_binary(v2_world):
    w = v2_world
    bad = "--- a/periphery/alpha.txt\n+++ b/periphery/alpha.txt\nGIT binary patch\nliteral 10\n"
    out = PC2.pc_v2_apply_patch_prepare(bad, **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "BINARY_PATCH_NOT_ALLOWED" in out["reason"]


def test_apply_patch_rejects_non_unified_diff(v2_world):
    w = v2_world
    out = PC2.pc_v2_apply_patch_prepare("not a diff at all", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "PATCH_NOT_UNIFIED_DIFF" in out["reason"]


def test_apply_patch_rejects_non_string(v2_world):
    w = v2_world
    out = PC2.pc_v2_apply_patch_prepare(b"bytes not str", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "PATCH_MUST_BE_STR" in out["reason"]


def test_apply_patch_dry_run_fail(v2_world):
    w = v2_world
    bad_patch = (
        "--- a/periphery/alpha.txt\n"
        "+++ b/periphery/alpha.txt\n"
        "@@ -1 +1 @@\n"
        "-this line does not exist in file\n"
        "+replacement\n"
    )
    out = PC2.pc_v2_apply_patch_prepare(bad_patch, **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "PATCH_DRY_RUN_FAILED" in out["reason"]


def test_apply_patch_target_not_found(v2_world):
    w = v2_world
    patch = (
        "--- a/periphery/nonexistent.txt\n"
        "+++ b/periphery/nonexistent.txt\n"
        "@@ -1 +1 @@\n"
        "-old line\n"
        "+new line\n"
    )
    out = PC2.pc_v2_apply_patch_prepare(patch, **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "TARGET_NOT_FOUND" in out["reason"]


def test_apply_patch_prepare_no_mutation(v2_world):
    w = v2_world
    before = (w["exec_wt"] / "periphery" / "alpha.txt").read_bytes()
    out = PC2.pc_v2_apply_patch_prepare(_valid_patch_alpha(), **_base(w))
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert out["decision_authority"] == "KX108_ONLY"
    assert len(out["execution_authority_hash"]) == 64
    after = (w["exec_wt"] / "periphery" / "alpha.txt").read_bytes()
    assert after == before, "PREPARE must not apply the patch"


def test_apply_patch_execute_blocked_eah_mismatch(v2_world):
    w = v2_world
    prep = PC2.pc_v2_apply_patch_prepare(_valid_patch_alpha(), **_base(w))
    result = PC2.pc_v2_apply_patch_execute(
        prep, "c" * 64, "HUMAN_REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED
    assert (w["exec_wt"] / "periphery" / "alpha.txt").read_bytes() == b"alpha v1\n"


def test_apply_patch_execute_blocked_missing_ref(v2_world):
    w = v2_world
    prep = PC2.pc_v2_apply_patch_prepare(_valid_patch_alpha(), **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_apply_patch_execute(
        prep, eah, "", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED


def test_apply_patch_e2e(v2_world):
    w = v2_world
    prep = PC2.pc_v2_apply_patch_prepare(_valid_patch_alpha(), **_base(w))
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert "periphery/alpha.txt" in prep["target_paths"]
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_apply_patch_execute(
        prep, eah, "HUMAN_EXPLICIT_V2_PATCH_001",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result["human_authorization_consumed"] is True
    assert result["jarvis_authority"] == "NONE"
    assert result["decision_authority"] == "KX108_ONLY"
    patched = (w["exec_wt"] / "periphery" / "alpha.txt").read_bytes()
    assert b"alpha v2" in patched
    after = result["after_digests"]
    assert "periphery/alpha.txt" in after
    assert after["periphery/alpha.txt"] == _SHA(patched)
    assert result["sealed_apply_receipt_id"] is not None
    assert len(result["sealed_rollback_evidence_ids"]) >= 1


def test_apply_patch_before_digests_correct(v2_world):
    w = v2_world
    alpha_bytes = (w["exec_wt"] / "periphery" / "alpha.txt").read_bytes()
    prep = PC2.pc_v2_apply_patch_prepare(_valid_patch_alpha(), **_base(w))
    assert prep["before_digests"]["periphery/alpha.txt"] == _SHA(alpha_bytes)


def test_apply_patch_receipt_invariants(v2_world):
    w = v2_world
    prep = PC2.pc_v2_apply_patch_prepare(
        _valid_patch_alpha(), **_base(w), session_id="jws-patchrcpt000000000")
    r = prep["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["session_id"] == "jws-patchrcpt000000000"
    assert r["receipt_id"].startswith("pcrcp-v2-")
    assert r["execution_authority_hash"] == prep["execution_authority_hash"]


# ============================================================
# GOVERNED_CREATE_DIR
# ============================================================

def test_create_dir_prepare_no_mutation(v2_world):
    w = v2_world
    new_dir = w["exec_wt"] / "periphery" / "newsubdir"
    assert not new_dir.exists()
    out = PC2.pc_v2_create_dir_prepare("periphery/newsubdir", **_base(w))
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert out["decision_authority"] == "KX108_ONLY"
    assert len(out["execution_authority_hash"]) == 64
    assert not new_dir.exists(), "PREPARE must not create directory"


def test_create_dir_prepare_rejects_existing(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_dir_prepare("periphery", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED
    assert "DIR_ALREADY_EXISTS" in out["reason"]


def test_create_dir_prepare_rejects_unsafe_path(v2_world):
    w = v2_world
    out = PC2.pc_v2_create_dir_prepare("../evil_dir", **_base(w))
    assert out["status"] == PC2.PREPARE_REJECTED


def test_create_dir_execute_blocked_eah_mismatch(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_dir_prepare("periphery/newsubdir", **_base(w))
    result = PC2.pc_v2_create_dir_execute(
        prep, "d" * 64, "HUMAN_REF", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED
    assert not (w["exec_wt"] / "periphery" / "newsubdir").exists()


def test_create_dir_execute_blocked_missing_ref(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_dir_prepare("periphery/newsubdir", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        prep, eah, "", stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTE_REJECTED


def test_create_dir_e2e(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_dir_prepare("periphery/newsubdir", **_base(w))
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        prep, eah, "HUMAN_EXPLICIT_V2_CDIR_001",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result["human_authorization_consumed"] is True
    assert result["jarvis_authority"] == "NONE"
    assert result["decision_authority"] == "KX108_ONLY"
    new_dir = w["exec_wt"] / "periphery" / "newsubdir"
    assert new_dir.exists()
    assert new_dir.is_dir()


def test_create_dir_no_sre_sar(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_dir_prepare("periphery/nosredir", **_base(w))
    eah = prep["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        prep, eah, "HUMAN_NOSRE",
        stores_base_dir=w["stores"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK
    assert "sealed_apply_receipt_id" not in result
    assert "sealed_rollback_evidence_id" not in result


def test_create_dir_receipt_invariants(v2_world):
    w = v2_world
    prep = PC2.pc_v2_create_dir_prepare(
        "periphery/dirrcpt", **_base(w), session_id="jws-dirrcpt0000000000000")
    r = prep["receipt"]
    assert r["mode"] == "GOVERNED_WRITE"
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["session_id"] == "jws-dirrcpt0000000000000"
    assert r["receipt_id"].startswith("pcrcp-v2-")
    assert r["execution_authority_hash"] == prep["execution_authority_hash"]


# ============================================================
# Dispatcher routing tests
# ============================================================

def test_dispatcher_routes_create_file_prepare(v2_world):
    w = v2_world
    out = PC2.execute_pc_capability_v2(
        "PC_V2_CREATE_FILE_PREPARE",
        target_path="periphery/dispatch_new.txt",
        content=b"dispatched\n",
        **_base(w)
    )
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["operation_type"] == PC2.OP_CREATE_FILE


def test_dispatcher_routes_move_file_prepare(v2_world):
    w = v2_world
    out = PC2.execute_pc_capability_v2(
        "PC_V2_MOVE_FILE_PREPARE",
        source_path="periphery/alpha.txt",
        dest_path="periphery/alpha_dispatch.txt",
        **_base(w)
    )
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["operation_type"] == PC2.OP_MOVE_FILE


def test_dispatcher_routes_apply_patch_prepare(v2_world):
    w = v2_world
    out = PC2.execute_pc_capability_v2(
        "PC_V2_APPLY_PATCH_PREPARE",
        patch_content=_valid_patch_alpha(),
        **_base(w)
    )
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["operation_type"] == PC2.OP_APPLY_PATCH


def test_dispatcher_routes_create_dir_prepare(v2_world):
    w = v2_world
    out = PC2.execute_pc_capability_v2(
        "PC_V2_CREATE_DIR_PREPARE",
        dir_path="periphery/dispatch_dir",
        **_base(w)
    )
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["operation_type"] == PC2.OP_CREATE_DIR

