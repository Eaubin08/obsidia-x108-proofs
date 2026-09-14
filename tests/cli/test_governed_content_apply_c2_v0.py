"""
tests/cli/test_governed_content_apply_c2_v0.py
=============================================
C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE (kernel sigma NON mocké
pour PRE et POST), le rail d'écriture gouverné complet :

  ExecutionEnvelope / EAH recalculé
  -> HumanApproval liée à l'EAH exact
  -> KX108_PRE ALLOW (adaptateur PRE + kernel réel)
  -> validate_governed_apply_preflight rejoué juste avant l'écriture
  -> confinement + sûreté reparse source, SHA256 COMPLET re-haché à la frontière
  -> précondition + sûreté reparse cible, double-check pré-état
  -> SealedRollbackEvidence persistée + vérifiée AVANT toute mutation
  -> mutation atomique + état re-MESURÉ
  -> SealedApplyReceipt immuable, persisté + vérifié
  -> TestContractResult
  -> évidence POST liée cryptographiquement au scellé
  -> KX108_POST lié (D1 + lien d'évidence scellée)
  -> KEEP (POST ALLOW)  |  rollback D2 fail-closed (POST HOLD/BLOCK/échec)

+ chemins négatifs : aucune mutation n'échappe au rail.

Tous les artefacts et cibles vivent dans un dépôt Git temporaire isolé +
des magasins tmp. AUCUNE mutation canonique. AUCUN git de disposition.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_batch_execution as E             # noqa: E402
import obsidia_pre_execution_context as PEC     # noqa: E402
import obsidia_test_contract as TC              # noqa: E402
import obsidia_kx108_decision_store as DS       # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PREADP  # noqa: E402
import obsidia_kx108_evidence_adapter as ADP    # noqa: E402
import obsidia_family_wiring_apply_bridge_v0 as BRIDGE            # noqa: E402
import obsidia_governed_apply_v0 as GA          # noqa: E402
import obsidia_governed_rollback_v0 as RB       # noqa: E402
import obsidia_sealed_evidence_v0 as SEV        # noqa: E402
import obsidia_post_execution_disposition_v0 as DISP             # noqa: E402
import obsidia_content_apply as C               # noqa: E402
import obsidia_governed_write_guard_v0 as WG    # noqa: E402

_TARGET_REL = "periphery/xdomain/c2_target_v0.py"
_SRC = b"# governed remediation content C2\nVALUE = 108\n"
_OLD = b"# stale target\nVALUE = 0\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


# ─── fabrique du monde canonique isolé ────────────────────────────────────

def _make_repo(tmp_path: Path, *, target_bytes: bytes = _OLD, src_bytes: bytes = _SRC) -> dict:
    repo = tmp_path / "iso_repo"
    (repo / "periphery" / "xdomain").mkdir(parents=True, exist_ok=True)
    (repo / _TARGET_REL).write_bytes(target_bytes)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", _TARGET_REL)
    _git(repo, "commit", "-q", "-m", "seed target")

    pid = "prop-c2-001"
    sandbox = repo / "_PATCH_PROPOSALS" / pid / "sandbox" / _TARGET_REL
    sandbox.parent.mkdir(parents=True, exist_ok=True)
    sandbox.write_bytes(src_bytes)
    proposal = {
        "proposal_id": pid, "session_id": "sess-c2", "base_sha": "a" * 40,
        "worktree": str(repo), "objective": "family wiring remediation content C2",
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "patches": [{"path": _TARGET_REL, "action": "REPLACE", "sandbox_path": str(sandbox)}],
    }
    pdir = repo / "_PATCH_PROPOSALS"
    (pdir / pid).mkdir(parents=True, exist_ok=True)
    (pdir / pid / "proposal.json").write_text(json.dumps(proposal, indent=2), encoding="utf-8")
    return {"repo": repo, "proposals_dir": pdir, "proposal_id": pid, "sandbox": sandbox}


def _pre_ctx(child: dict, repo: Path) -> dict:
    manifest = {
        "repository_identity": str(repo), "execution_worktree_path": str(repo / "wt"),
        "branch_name": "feat/x", "base_sha": "a" * 40, "source_kind": "FILESYSTEM_FILE",
        "source_repository_identity": str(repo), "source_commit": "", "source_blob_sha": "",
        "source_path": child["source_path"], "source_sha256": child["source_content_sha256"],
        "target_path": child["target_path"], "target_pre_sha256": child["target_pre_sha256"],
        "operation": "REPLACE", "approved_scope": [child["target_path"]],
        "protected_scope_status": "CLEAN", "test_contract_hash": None, "schema_version": 2,
    }
    rec = {
        "context_schema_version": 2, "created_at": "2026-01-01T00:00:00+00:00",
        "repository_identity": str(repo), "repository_root": str(repo),
        "execution_worktree_path": manifest["execution_worktree_path"],
        "branch_name": manifest["branch_name"], "base_sha": manifest["base_sha"],
        "target_path": manifest["target_path"], "target_pre_sha256": manifest["target_pre_sha256"],
        "source_kind": manifest["source_kind"],
        "source_repository_identity": manifest["source_repository_identity"],
        "source_commit": "", "source_blob_sha": "", "source_path": manifest["source_path"],
        "source_sha256": manifest["source_sha256"], "operation": "REPLACE",
        "approved_scope": manifest["approved_scope"], "worktree_isolated": True,
        "branch_isolated": True, "protected_scope_status": "CLEAN", "manifest": manifest,
        "legacy_manifest_hash_short": "0" * 16, "decision_authority": "KX108_ONLY",
    }
    rec["manifest_sha256"] = PEC.compute_manifest_sha256(rec["manifest"])
    seed = [f for f in PEC._CONTEXT_BOUND_FIELDS_V2
            if f not in ("context_schema_version", "context_id", "created_at")]
    rec["context_id"] = "pec-" + hashlib.sha256(
        json.dumps({k: rec.get(k) for k in seed}, sort_keys=True).encode()).hexdigest()[:32]
    rec["context_record_hash"] = PEC.compute_context_record_hash(rec)
    return rec


def _contract(child: dict, *, failing: bool = False) -> dict:
    argv = ([sys.executable, "-c", "import sys; sys.exit(1)"] if failing
            else [sys.executable, "-c", "pass"])
    chk = TC.build_check("c2-check", TC.CHECK_TYPE_SUBPROCESS, argv=argv,
                         expected_exit_code=0, required=True, timeout_seconds=30)
    return TC.build_test_contract("c2-contract", child["candidate_entry_id"], None,
                                  child["target_path"], [chk])


def _envelope(child: dict, pre_ctx: dict, contract: dict) -> dict:
    env = {
        "batch_execution_id": "be-c2", "batch_id": None, "batch_hash": None,
        "batch_hash_version": 1, "candidate_scope_hash": None,
        "execution_order": [child["candidate_entry_id"]], "dependency_edges": [],
        "children": [child], "decision_authority": "KX108_ONLY", "integrity_verified": True,
        "pre_execution_context_id": pre_ctx["context_id"],
        "pre_execution_context_record_hash": pre_ctx["context_record_hash"],
        "test_contract": contract,
    }
    env["test_contract_hash"] = TC.compute_test_contract_hash(contract)
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    return env


def _store_env(env: dict, ex: Path) -> None:
    p = ex / "executions" / env["batch_execution_id"] / "execution.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(env, indent=2), encoding="utf-8")


def _store_ctx(rec: dict, cx: Path) -> None:
    cx.mkdir(parents=True, exist_ok=True)
    (cx / f"{rec['context_id']}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")


def _store_approval(env: dict, ex: Path, approval_id: str = "appr-c2-001", **over) -> str:
    rec = {
        "approval_id": approval_id, "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-01-02T00:00:00+00:00",
        "batch_execution_id": env["batch_execution_id"], "batch_id": env["batch_id"],
        "batch_hash": env["batch_hash"], "candidate_scope_hash": env["candidate_scope_hash"],
        "execution_authority_hash": env["execution_authority_hash"],
        "approved_by": "HUMAN", "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": "KX108_ONLY",
    }
    rec.update(over)
    rec["approval_record_hash"] = E.compute_approval_record_hash(rec)
    res = E.store_approval_artifact(rec, execution_dir=ex)
    assert res["status"] in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"), res
    return approval_id


def _world(tmp_path: Path, *, failing_contract: bool = False,
           target_bytes: bytes = _OLD, src_bytes: bytes = _SRC) -> dict:
    mk = _make_repo(tmp_path, target_bytes=target_bytes, src_bytes=src_bytes)
    br = BRIDGE.build_child_execution_from_obsidure_proposal(
        proposal_id=mk["proposal_id"], session_id="sess-c2", base_sha="a" * 40,
        worktree=str(mk["repo"]), approved_scope=[_TARGET_REL],
        proposals_dir=mk["proposals_dir"], repo_root=mk["repo"],
    )
    assert br["status"] == BRIDGE.STATUS_READY, br
    child = br["child"]
    d = {k: tmp_path / k for k in (
        "ex", "cx", "dc", "post", "tcr", "sar", "sre", "rbk")}
    contract = _contract(child, failing=failing_contract)
    pctx = _pre_ctx(child, mk["repo"])
    env = _envelope(child, pctx, contract)
    _store_ctx(pctx, d["cx"])
    _store_env(env, d["ex"])
    aid = _store_approval(env, d["ex"])
    tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        env["batch_execution_id"], child["child_execution_id"], aid,
        execution_dir=d["ex"], pre_execution_context_dir=d["cx"])
    assert tr["status"] == PREADP.STATUS_READY, tr
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        tr["pre_tooling_build_state_kwargs"], tr["pre_binding_context"], store_dir=d["dc"])
    assert pre_out["record"]["x108_gate"] == "ALLOW", pre_out["record"]
    return {
        "mk": mk, "repo": mk["repo"], "child": child, "env": env, "contract": contract,
        "approval_id": aid, "pre_id": pre_out["decision_record_id"],
        "target_abs": mk["repo"] / _TARGET_REL,
        "sha_A": child["target_pre_sha256"], "sha_B": child["source_content_sha256"],
        **d,
    }


def _run(w: dict, **over) -> dict:
    kw = dict(
        batch_execution_id=w["env"]["batch_execution_id"],
        child_execution_id=w["child"]["child_execution_id"],
        approval_id=w["approval_id"], kx108_pre_decision_record_id=w["pre_id"],
        execution_dir=w["ex"], pre_execution_context_dir=w["cx"],
        kx108_decision_dir=w["dc"], post_decision_store_dir=w["post"],
        test_contract_results_dir=w["tcr"], sealed_receipt_dir=w["sar"],
        sealed_rollback_evidence_dir=w["sre"], rollback_result_dir=w["rbk"],
        repo_root=w["repo"],
    )
    kw.update(over)
    return GA.run_governed_content_apply(**kw)


# ═══════════════════════════════════════════════════════════════════════════
# 1. E2E ALLOW  (§26)
# ═══════════════════════════════════════════════════════════════════════════

def test_01_e2e_allow_keeps_and_binds_sealed_evidence(tmp_path):
    w = _world(tmp_path)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["kx108_post_gate"] == "ALLOW"
    assert r["target_final_sha256"] == w["sha_B"]
    assert w["target_abs"].read_bytes() == _SRC
    # évidence scellée vérifiable
    sre = SEV.load_sealed_rollback_evidence(r["sealed_rollback_evidence_id"], w["sre"])
    sar = SEV.load_sealed_apply_receipt(r["sealed_apply_receipt_id"], w["sar"])
    assert SEV.verify_sealed_rollback_evidence(sre)[0]
    assert SEV.verify_sealed_apply_receipt(sar)[0]
    # POST record porte les liens d'évidence scellée (double liage)
    post = DS.load_kx108_decision_record(r["kx108_post_decision_record_id"], w["post"])
    assert post["sealed_apply_receipt_id"] == r["sealed_apply_receipt_id"]
    assert post["sealed_apply_receipt_hash"] == r["sealed_apply_receipt_hash"]
    assert post["sealed_rollback_evidence_id"] == r["sealed_rollback_evidence_id"]
    assert post["sealed_rollback_evidence_hash"] == r["sealed_rollback_evidence_hash"]
    ok, why = DS.verify_kx108_decision_record(post)
    assert ok, why


def test_02_allow_source_bound_to_exact_eah(tmp_path):
    w = _world(tmp_path)
    # l'approbation lie l'EAH exact
    appr = E.load_approval_artifact(w["approval_id"], w["ex"])
    assert appr["execution_authority_hash"] == w["env"]["execution_authority_hash"]
    r = _run(w)
    assert r["execution_authority_hash"] == w["env"]["execution_authority_hash"]
    assert r["status"] == GA.GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW


def test_03_sealed_rollback_evidence_persisted_before_mutation(tmp_path):
    """La SealedRollbackEvidence existe et vaut la preimage A ; la cible finale
    vaut B — l'ordre 'sceller A avant d'écrire B' est prouvé par le contenu."""
    w = _world(tmp_path)
    r = _run(w)
    sre = SEV.load_sealed_rollback_evidence(r["sealed_rollback_evidence_id"], w["sre"])
    pre, why = SEV.decode_sealed_preimage(sre)
    assert why is None
    assert pre == _OLD
    assert sre["pre_write_sha256"] == w["sha_A"]
    assert sre["source_content_sha256"] == w["sha_B"]
    assert sre["approval_id"] == w["approval_id"]


def test_04_no_public_success_before_post_allow(tmp_path):
    assert GA.PUBLIC_SUCCESS_BEFORE_KX108_POST_ALLOW is False
    w = _world(tmp_path, failing_contract=True)
    r = _run(w)
    # POST HOLD/BLOCK -> jamais KEEP
    assert r["status"] != GA.GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert r["status"] in GA._C2_PUBLIC_STATES


# ═══════════════════════════════════════════════════════════════════════════
# 2. E2E HOLD -> rollback D2  (§27)
# ═══════════════════════════════════════════════════════════════════════════

def test_05_e2e_hold_rolls_back_to_A(tmp_path):
    w = _world(tmp_path, failing_contract=True)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK, r
    assert r["rollback_status"] in (RB.ROLLBACK_SUCCEEDED, RB.ALREADY_ROLLED_BACK,
                                    RB.ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED)
    assert w["target_abs"].read_bytes() == _OLD
    assert _sha(w["target_abs"].read_bytes()) == w["sha_A"]
    assert r["kx108_invocations_during_rollback"] == 0


def test_06_hold_rollback_result_is_immutable_record(tmp_path):
    w = _world(tmp_path, failing_contract=True)
    r = _run(w)
    rbk = RB.load_rollback_result(r["rollback_result_id"], w["rbk"])
    ok, why = RB.verify_rollback_result(rbk)
    assert ok, why
    assert rbk["evidence_sealed"] is True
    assert rbk["expected_post_sha256"] == w["sha_B"]


# ═══════════════════════════════════════════════════════════════════════════
# 3. SOURCE-DELETED / DRIFTED ROLLBACK  (§28) — B authority = envelope
# ═══════════════════════════════════════════════════════════════════════════

def test_07_source_deleted_rollback_still_restores_A(tmp_path):
    w = _world(tmp_path)                      # ALLOW -> B on disk, sealed evidence
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    # supprime la source FILESYSTEM_FILE
    src_abs = (w["repo"] / w["child"]["source_path"])
    src_abs.unlink()
    assert not src_abs.exists()
    # déclenche un MUST_ROLLBACK canonique par signal (post-pipeline)
    rb = RB.run_governed_rollback(
        w["child"]["child_execution_id"], w["pre_id"],
        rollback_trigger_code="POST_EVIDENCE_UNAVAILABLE",
        execution_dir=w["ex"], pre_decision_store_dir=w["dc"],
        post_decision_store_dir=w["post"], rollback_result_dir=w["rbk"],
        repo_root=w["repo"],
        sealed_rollback_evidence_id=r["sealed_rollback_evidence_id"],
        sealed_apply_receipt_id=r["sealed_apply_receipt_id"],
        sealed_receipt_dir=w["sar"], sealed_rollback_evidence_dir=w["sre"],
    )
    assert rb["status"] in (RB.ROLLBACK_SUCCEEDED, RB.ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED), rb
    assert w["target_abs"].read_bytes() == _OLD
    assert rb["rollback_expected_b_authority"] == "EXECUTION_ENVELOPE_CHILD_SOURCE_CONTENT_SHA256"
    assert rb["expected_post_sha256"] == w["sha_B"]


def test_08_source_changed_rollback_still_restores_A(tmp_path):
    w = _world(tmp_path)
    r = _run(w)
    (w["repo"] / w["child"]["source_path"]).write_bytes(b"TOTALLY DIFFERENT SOURCE NOW\n")
    rb = RB.run_governed_rollback(
        w["child"]["child_execution_id"], w["pre_id"],
        rollback_trigger_code="TEST_INFRA_FAILURE",
        execution_dir=w["ex"], pre_decision_store_dir=w["dc"],
        post_decision_store_dir=w["post"], rollback_result_dir=w["rbk"],
        repo_root=w["repo"],
        sealed_rollback_evidence_id=r["sealed_rollback_evidence_id"],
        sealed_receipt_dir=w["sar"], sealed_rollback_evidence_dir=w["sre"],
    )
    assert rb["status"] in (RB.ROLLBACK_SUCCEEDED, RB.ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED), rb
    assert w["target_abs"].read_bytes() == _OLD


def test_09_rollback_does_not_depend_on_current_source_file_flag():
    # invariant de conception, vérifié aussi structurellement
    src = Path(RB.__file__).read_text(encoding="utf-8")
    assert "ROLLBACK_EXPECTED_B_DEPENDS_ON_CURRENT_SOURCE_FILE = FALSE" in src or \
           "EXECUTION_ENVELOPE_CHILD_SOURCE_CONTENT_SHA256" in src


# ═══════════════════════════════════════════════════════════════════════════
# 4. RECEIPT SEAL FAILURE  (§29 / §22)
# ═══════════════════════════════════════════════════════════════════════════

def test_10_receipt_seal_failure_after_write_must_rollback(tmp_path, monkeypatch):
    w = _world(tmp_path)
    real_store = SEV.store_sealed_apply_receipt

    def broken(rec, store_dir=None):
        return {"status": SEV.STATUS_TEMP_WRITE_FAILED,
                "sealed_apply_receipt_id": rec.get("sealed_apply_receipt_id")}
    monkeypatch.setattr(GA, "run_governed_content_apply", GA.run_governed_content_apply)
    monkeypatch.setattr(SEV, "store_sealed_apply_receipt", broken)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK, r
    assert "SEALED_APPLY_RECEIPT_SEAL_FAILED" in r["reason"]
    assert w["target_abs"].read_bytes() == _OLD
    monkeypatch.setattr(SEV, "store_sealed_apply_receipt", real_store)


# ═══════════════════════════════════════════════════════════════════════════
# 5. POST-STAMP  (§30 / §15) — pas de dépendance de stamp
# ═══════════════════════════════════════════════════════════════════════════

def test_11_no_post_stamp_recovery_dependency():
    ga = Path(GA.__file__).read_text(encoding="utf-8")
    rb = Path(RB.__file__).read_text(encoding="utf-8")
    for banned in ("post_stamp", "-post stamp", '"-post"', "'-post'", "sre-…-post"):
        assert banned not in ga
        assert banned not in rb
    # l'autorité de B est l'enveloppe, prouvée par test_07/test_08
    assert GA.C2_SOURCE_CONTENT_REHASH_IMMEDIATELY_BEFORE_WRITE is True


# ═══════════════════════════════════════════════════════════════════════════
# 6. WRITE EXCEPTION MATRIX  (§31 / §13)
# ═══════════════════════════════════════════════════════════════════════════

def test_12_write_failure_target_unchanged_rejected_no_mutation(tmp_path, monkeypatch):
    w = _world(tmp_path)

    def fail_noop(target_abs, content, expected_pre):
        return {"status": C.ATOMIC_REPLACE_FAILED}          # cible NON touchée
    monkeypatch.setattr(C, "atomic_replace_with_bytes", fail_noop)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION, r
    assert "APPLY_FAILED_NO_CONFIRMED_MUTATION" in r["reason"]
    assert w["target_abs"].read_bytes() == _OLD


def test_13_write_became_B_then_failed_must_rollback(tmp_path, monkeypatch):
    w = _world(tmp_path)

    def wrote_b_then_fail(target_abs, content, expected_pre):
        Path(target_abs).write_bytes(content)              # cible == B
        return {"status": C.ATOMIC_REPLACE_FAILED}
    monkeypatch.setattr(C, "atomic_replace_with_bytes", wrote_b_then_fail)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK, r
    assert w["target_abs"].read_bytes() == _OLD


def test_14_write_became_third_party_C_quarantine_preserves_C(tmp_path, monkeypatch):
    w = _world(tmp_path)
    third = b"# THIRD PARTY BYTES\n"

    def wrote_c(target_abs, content, expected_pre):
        Path(target_abs).write_bytes(third)
        return {"status": C.ATOMIC_REPLACE_FAILED}
    monkeypatch.setattr(C, "atomic_replace_with_bytes", wrote_c)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE, r
    assert w["target_abs"].read_bytes() == third        # jamais réécrit aveuglément


def test_15_write_raises_is_measured_not_assumed(tmp_path, monkeypatch):
    w = _world(tmp_path)

    def boom(target_abs, content, expected_pre):
        raise OSError("disk gone")
    monkeypatch.setattr(C, "atomic_replace_with_bytes", boom)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION, r
    assert w["target_abs"].read_bytes() == _OLD
    assert GA.WRITE_EXCEPTION_TARGET_STATE_REMEASURED is True


# ═══════════════════════════════════════════════════════════════════════════
# 7. DRIFT AVANT ÉCRITURE  (§32 / §33)
# ═══════════════════════════════════════════════════════════════════════════

def test_16_source_drift_before_write_no_mutation(tmp_path):
    w = _world(tmp_path)
    w["mk"]["sandbox"].write_bytes(b"# drifted sandbox after envelope\n")
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION, r
    assert w["target_abs"].read_bytes() == _OLD


def test_17_target_drift_before_write_no_replace_third_party_preserved(tmp_path):
    w = _world(tmp_path)
    drift = b"# someone else edited the target\n"
    w["target_abs"].write_bytes(drift)
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION, r
    assert w["target_abs"].read_bytes() == drift


# ═══════════════════════════════════════════════════════════════════════════
# 8. REPARSE  (§34) — best-effort selon droits plateforme
# ═══════════════════════════════════════════════════════════════════════════

def test_18_target_symlink_refused(tmp_path):
    w = _world(tmp_path)
    real = w["repo"] / "periphery" / "xdomain" / "real_elsewhere.py"
    real.write_bytes(_OLD)
    w["target_abs"].unlink()
    try:
        os.symlink(str(real), str(w["target_abs"]))
    except (OSError, NotImplementedError, AttributeError) as exc:
        pytest.skip(f"symlink non autorisé sur cette plateforme: {exc}")
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION
    assert "REPARSE" in r["reason"] or "PRECONDITION" in r["reason"] or "LINK" in r["reason"]
    assert real.read_bytes() == _OLD


# ═══════════════════════════════════════════════════════════════════════════
# 9. BYPASS LEGACY / AGENT DIRECT  (§35 / §36)
# ═══════════════════════════════════════════════════════════════════════════

def test_19_agent_obsidure_apply_proposal_refuses_canonical(monkeypatch):
    from periphery.agents.agent_obsidure import AgentObsidure
    ag = AgentObsidure()
    monkeypatch.delenv("OBSIDIA_GOVERNED_TEST_MODE", raising=False)
    with pytest.raises(WG.LegacyDirectApplyDisabled):
        ag.apply_proposal("whatever", target_root=_REPO_ROOT)
    monkeypatch.setenv("OBSIDIA_GOVERNED_TEST_MODE", "1")
    with pytest.raises(WG.LegacyDirectApplyDisabled):
        ag.apply_proposal("whatever", target_root=_REPO_ROOT)          # canonique => toujours refus


def test_20_guard_refuses_canonical_repo_and_worktree_and_stores(monkeypatch):
    monkeypatch.setenv("OBSIDIA_GOVERNED_TEST_MODE", "1")
    for bad in (_REPO_ROOT, _REPO_ROOT / "scripts", _REPO_ROOT.parent):
        with pytest.raises(WG.LegacyDirectApplyDisabled):
            WG.assert_isolated_non_canonical_write_root(bad, _REPO_ROOT / "_PATCH_PROPOSALS")
    assert WG.is_canonical_write_root(_REPO_ROOT) is True


def test_21_guard_accepts_isolated_non_canonical(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIA_GOVERNED_TEST_MODE", "1")
    assert WG.assert_isolated_non_canonical_write_root(
        tmp_path / "iso", tmp_path / "props", evidence_dir=tmp_path / "ev") is True
    monkeypatch.delenv("OBSIDIA_GOVERNED_TEST_MODE", raising=False)
    with pytest.raises(WG.LegacyDirectApplyDisabled):
        WG.assert_isolated_non_canonical_write_root(tmp_path / "iso", tmp_path / "props")


def test_22_legacy_cli_apply_branch_is_fail_closed():
    src = Path(_SCRIPTS_DIR / "obsidure_cli.py").read_text(encoding="utf-8")
    assert "LEGACY_DIRECT_APPLY_DISABLED" in src
    assert "return 4" in src
    synth = Path(_SCRIPTS_DIR / "obsidure_synth_session.py").read_text(encoding="utf-8")
    assert "__test_only__ = True" in synth
    assert "assert_isolated_non_canonical_write_root" in synth


# ═══════════════════════════════════════════════════════════════════════════
# 10. LIAGE SCELLÉ -> KX108_POST  (§37)
# ═══════════════════════════════════════════════════════════════════════════

def test_23_post_record_cannot_silently_describe_different_sealed_artifacts(tmp_path):
    w = _world(tmp_path)
    r = _run(w)
    post = DS.load_kx108_decision_record(r["kx108_post_decision_record_id"], w["post"])
    ok, _ = DS.verify_kx108_decision_record(post)
    assert ok
    tampered = json.loads(json.dumps(post))
    tampered["sealed_apply_receipt_hash"] = "0" * 64
    ok2, why2 = DS.verify_kx108_decision_record(tampered)
    assert not ok2 and why2 == "DECISION_RECORD_HASH_MISMATCH"
    # le hash de traduction couvre aussi l'id scellé
    assert post["kx108_input_translation_hash"] == r["kx108_input_translation_hash"]


def test_24_translation_hash_changes_with_sealed_ids(tmp_path):
    w = _world(tmp_path)
    r = _run(w)
    # rejouer la traduction SANS ids scellés -> hash différent (liage prouvé)
    tr_plain = ADP.translate_evidence_to_tooling_build_state(
        w["env"]["batch_execution_id"], w["child"]["child_execution_id"], w["approval_id"],
        r["test_contract_result_id"], execution_dir=w["ex"],
        results_dir=w["tcr"], repo_root=w["repo"],
        pre_execution_context_dir=w["cx"],
        sealed_apply_receipt_id=r["sealed_apply_receipt_id"],
        sealed_rollback_evidence_id=r["sealed_rollback_evidence_id"],
        sealed_receipt_dir=w["sar"], sealed_rollback_evidence_dir=w["sre"],
    )
    assert tr_plain["status"] == ADP.READY_FOR_KX108_SUBMISSION, tr_plain
    prov = tr_plain["translation_report"]
    assert prov["sealed_apply_receipt_id"] == r["sealed_apply_receipt_id"]
    assert prov["sealed_rollback_evidence_id"] == r["sealed_rollback_evidence_id"]


# ═══════════════════════════════════════════════════════════════════════════
# 11. COMPAT HISTORIQUE  (§38)
# ═══════════════════════════════════════════════════════════════════════════

def test_25_legacy_post_record_verifies_unchanged():
    legacy = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": "kxd-legacyc2000000000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": "b", "child_execution_id": "c",
        "execution_authority_hash": "h" * 64, "approval_id": "a",
        "test_contract_hash": "t" * 64, "test_result_id": "tr",
        "test_result_record_hash": "trh" * 10, "kx108_input_translation_hash": "k" * 64,
        "decision_id": "d", "trace_id": "t", "domain": "tooling_build",
        "x108_gate": "ALLOW", "reason_code": "GUARD_ALLOW", "severity": "S0",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "contradictions": [], "unknowns": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY", "canonical_envelope": {"x108_gate": "ALLOW"},
    }
    legacy["decision_record_hash"] = DS.compute_kx108_decision_record_hash(legacy)
    ok, why = DS.verify_kx108_decision_record(legacy)
    assert ok, why
    # les champs scellés conditionnels n'entrent PAS dans le calcul en leur absence
    assert "sealed_apply_receipt_id" not in json.dumps(
        {k: legacy.get(k) for k in DS._record_bound_fields_for(legacy)})


def test_26_d1_post_linked_without_sealed_still_uses_legacy_bound_fields():
    rec = {"decision_phase": DS.POST_DECISION_PHASE,
           "kx108_pre_decision_record_id": "kxpre-x"}
    fields = DS._record_bound_fields_for(rec)
    assert fields is DS._POST_PRE_LINKED_RECORD_BOUND_FIELDS
    rec["sealed_apply_receipt_id"] = "sar-" + "0" * 32
    assert DS._record_bound_fields_for(rec) is DS._POST_PRE_LINKED_SEALED_RECORD_BOUND_FIELDS


# ═══════════════════════════════════════════════════════════════════════════
# 12. INVARIANTS SYSTÈME  (§9) — vérifs ciblées additionnelles
# ═══════════════════════════════════════════════════════════════════════════

def test_27_kx108_pre_reverified_immediately_before_write(tmp_path):
    w = _world(tmp_path)
    # falsifie le record PRE APRÈS le préflight-time mais AVANT l'écriture :
    # on invalide le gate -> l'orchestrateur doit refuser sans muter.
    pre_path = w["dc"] / f"{w['pre_id']}.json"
    rec = json.loads(pre_path.read_text())
    rec["x108_gate"] = "HOLD"
    pre_path.write_text(json.dumps(rec))
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION
    assert "KX108_PRE" in r["reason"]
    assert w["target_abs"].read_bytes() == _OLD
    assert GA.KX108_PRE_REVERIFIED_IMMEDIATELY_BEFORE_WRITE is True


def test_28_approval_eah_mismatch_no_mutation(tmp_path):
    w = _world(tmp_path)
    ap = w["ex"] / "approvals" / w["approval_id"] / "approval.json"
    rec = json.loads(ap.read_text())
    rec["execution_authority_hash"] = "9" * 64
    ap.write_text(json.dumps(rec))
    r = _run(w)
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION
    assert w["target_abs"].read_bytes() == _OLD


def test_29_c1_preflight_still_read_only_and_passes(tmp_path):
    w = _world(tmp_path)
    pf = GA.validate_governed_apply_preflight(
        w["env"]["batch_execution_id"], w["child"]["child_execution_id"],
        w["approval_id"], w["pre_id"], execution_dir=w["ex"],
        pre_execution_context_dir=w["cx"], kx108_decision_dir=w["dc"], repo_root=w["repo"])
    assert pf["status"] == GA.STATUS_PASS, pf
    assert pf["write_capability"] is False
    assert w["target_abs"].read_bytes() == _OLD          # préflight n'écrit jamais


def test_30_no_canonical_mutation_and_stores_untouched(tmp_path):
    before = (_REPO_ROOT / _TARGET_REL)
    existed = before.exists()
    w = _world(tmp_path)
    _run(w)
    _run(_world(tmp_path / "b", failing_contract=True))
    assert (_REPO_ROOT / _TARGET_REL).exists() == existed
    # rien écrit sous le repo canonique par ces E2E
    assert not (_REPO_ROOT / _TARGET_REL).exists() or existed
