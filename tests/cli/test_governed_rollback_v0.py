"""
tests/cli/test_governed_rollback_v0.py
=====================================
GOVERNED_ROLLBACK_D2_V0

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE (kernel sigma non mocké
pour la création PRE/POST) :

  - obsidia_governed_rollback_v0.run_governed_rollback restaure la cible
    d'une exécution bornée gouvernée à son état d'AVANT l'application,
    UNIQUEMENT si le classificateur D1 recalculé énonce MUST_ROLLBACK et
    si toute la chaîne d'identité + preimage + post-state + sécurité de
    chemin sont exactes ; sinon statut REFUSED_*/FAILED avec quarantaine.
  - garde d'état courant fail-closed : cible == B -> rollback ; cible == A
    -> ALREADY_ROLLED_BACK (aucune réécriture) ; cible == autre -> DRIFT
    (octets tiers préservés).
  - double garde TOCTOU (avant et immédiatement avant os.replace) ;
    sécurité lien/reparse cible + composants parent ; RollbackResult
    IMMUABLE (os.link) rechargé + vérifié.
  - N'INVOQUE JAMAIS KX108. Ne mute NI execution_status NI closure.

Toutes les mutations concernent UNIQUEMENT une cible fixture tmp.
Aucun fichier cible du projet canonique n'est touché.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_batch_execution as E              # noqa: E402
import obsidia_pre_execution_context as PEC      # noqa: E402
import obsidia_test_contract as TC               # noqa: E402
import obsidia_kx108_decision_store as DS        # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PREADP  # noqa: E402
import obsidia_governed_rollback_v0 as GR        # noqa: E402

_REL = "periphery/xdomain/rb_target_v0.py"
_A = b"# state A (pre-apply)\nVALUE = 0\n"
_B = b"# state B (governed apply result)\nVALUE = 1\n"
_C = b"# state C (third-party drift)\nZZ = 9\n"
_SRC = b"# governed remediation source bytes\nVALUE = 1\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _make_pre_ctx(rel: str, sha_a: str, sha_src: str, repo: Path) -> dict:
    manifest = {
        "repository_identity": str(repo), "execution_worktree_path": str(repo / "wt"),
        "branch_name": "feat/x", "base_sha": "a" * 40,
        "source_kind": "FILESYSTEM_FILE", "source_repository_identity": str(repo),
        "source_commit": "", "source_blob_sha": "", "source_path": "sbx/src.py",
        "source_sha256": sha_src, "target_path": rel, "target_pre_sha256": sha_a,
        "operation": "UPDATE_TARGET_FROM_SOURCE", "approved_scope": [rel],
        "protected_scope_status": "CLEAN", "test_contract_hash": None, "schema_version": 2,
    }
    rec = {
        "context_schema_version": 2, "created_at": "2026-01-01T00:00:00+00:00",
        "repository_identity": manifest["repository_identity"], "repository_root": str(repo),
        "execution_worktree_path": manifest["execution_worktree_path"],
        "branch_name": manifest["branch_name"], "base_sha": manifest["base_sha"],
        "target_path": rel, "target_pre_sha256": sha_a,
        "source_kind": manifest["source_kind"],
        "source_repository_identity": manifest["source_repository_identity"],
        "source_commit": "", "source_blob_sha": "", "source_path": manifest["source_path"],
        "source_sha256": sha_src, "operation": manifest["operation"], "approved_scope": [rel],
        "worktree_isolated": True, "branch_isolated": True, "protected_scope_status": "CLEAN",
        "manifest": manifest, "legacy_manifest_hash_short": "0" * 16, "decision_authority": "KX108_ONLY",
    }
    rec["manifest_sha256"] = PEC.compute_manifest_sha256(rec["manifest"])
    seed = [f for f in PEC._CONTEXT_BOUND_FIELDS_V2
            if f not in ("context_schema_version", "context_id", "created_at")]
    rec["context_id"] = "pec-" + hashlib.sha256(
        json.dumps({k: rec.get(k) for k in seed}, sort_keys=True).encode()).hexdigest()[:32]
    rec["context_record_hash"] = PEC.compute_context_record_hash(rec)
    return rec


def _make_envelope(pre_ctx: dict, rel: str, sha_a: str, sha_src: str) -> dict:
    child = {
        "candidate_entry_id": "cand-rb", "child_execution_id": "child-rb",
        "source_kind": "FILESYSTEM_FILE", "source_hash": sha_src[:16],
        "source_content_sha256": sha_src, "source_repository_identity": "repo",
        "source_git_commit_sha": "", "source_git_blob_sha": "", "source_git_historical_path": "",
        "target_path": rel, "target_pre_hash": sha_a[:16], "target_pre_sha256": sha_a,
        "operation_type": "UPDATE_TARGET_FROM_SOURCE", "operation_reason": "rb pilot",
        "execution_status": "PLANNED",
    }
    env = {
        "batch_execution_id": "be-rb", "batch_id": None, "batch_hash": None,
        "batch_hash_version": 1, "candidate_scope_hash": None,
        "execution_order": ["cand-rb"], "dependency_edges": [], "children": [child],
        "decision_authority": "KX108_ONLY", "integrity_verified": True,
        "pre_execution_context_id": pre_ctx["context_id"],
        "pre_execution_context_record_hash": pre_ctx["context_record_hash"],
    }
    tc = {"test_contract_schema_version": 1, "contract_id": "tc-rb", "candidate_entry_id": "cand-rb",
          "batch_id": None, "target_path": rel, "checks": [], "decision_authority": "KX108_ONLY"}
    env["test_contract"] = tc
    env["test_contract_hash"] = TC.compute_test_contract_hash(tc)
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    return env


def _store_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _store_approval(env: dict, exec_dir: Path, approval_id: str = "appr-rb", **over) -> str:
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
    res = E.store_approval_artifact(rec, execution_dir=exec_dir)
    assert res["status"] in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"), res
    return approval_id


def _post_kwargs(child_id: str, rel: str, **over) -> dict:
    kw = {
        "session_id": child_id, "objective": "", "base_sha": "a" * 40, "manifest_hash": "m" * 64,
        "diff_hash": "", "approved_scope": [rel], "actual_touched_files": [rel],
        "new_files": [], "deleted_files": [], "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED", "obsidure_status": "NOT_APPLICABLE",
        "worktree_isolated": True, "branch_isolated": True,
        "auto_commit_disabled": True, "auto_push_disabled": True, "auto_merge_disabled": True,
        "tests_results": "PASS", "gates_results": "PASS", "first_failure": "",
        "commit_status": "NOT_COMMITTED", "push_status": "NOT_PUSHED", "merge_status": "NOT_MERGED",
        "unknowns": [], "contradictions": [], "risk_flags": [], "decision_authority": "KX108_ONLY",
    }
    kw.update(over)
    return kw


@pytest.fixture
def chain(tmp_path):
    repo = tmp_path / "repo"
    (repo / "periphery" / "xdomain").mkdir(parents=True)
    tgt = repo / _REL
    tgt.write_bytes(_B)  # état B "déjà appliqué"

    sha_a, sha_b, sha_src = _sha(_A), _sha(_B), _sha(_SRC)
    pre_ctx = _make_pre_ctx(_REL, sha_a, sha_src, repo)
    env = _make_envelope(pre_ctx, _REL, sha_a, sha_src)

    ex, cx, pdc, qdc, evd, rrd = (tmp_path / "exec", tmp_path / "ctx", tmp_path / "pre_dec",
                                  tmp_path / "post_dec", tmp_path / "evidence", tmp_path / "rb_results")
    _store_json(cx / f"{pre_ctx['context_id']}.json", pre_ctx)
    _store_json(ex / "executions" / env["batch_execution_id"] / "execution.json", env)
    approval_id = _store_approval(env, ex)

    tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        env["batch_execution_id"], "child-rb", approval_id, execution_dir=ex, pre_execution_context_dir=cx)
    assert tr["status"] == PREADP.STATUS_READY, tr
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        tr["pre_tooling_build_state_kwargs"], tr["pre_binding_context"], store_dir=pdc)
    assert pre_out["record"]["x108_gate"] == "ALLOW", pre_out["record"]

    receipt = {
        "schema_version": "V0", "child_execution_id": "child-rb",
        "batch_execution_id": env["batch_execution_id"], "batch_id": env["batch_id"],
        "target_path": _REL, "target_pre_sha256": sha_a, "source_full_sha256": sha_src,
        "target_post_sha256": sha_b, "bytes_written": len(_B),
        "operation_type": "UPDATE_TARGET_FROM_SOURCE", "source_kind": "FILESYSTEM_FILE",
        "source_identity": {"source_git_commit_sha": "", "source_git_blob_sha": "",
                            "source_git_historical_path": "", "source_path": "sbx/src.py"},
        "status": "CONTENT_APPLIED", "timestamp": "2026-01-03T00:00:00+00:00",
        "decision_authority": "KX108_ONLY",
    }
    evidence = {
        "schema_version": "V0", "child_execution_id": "child-rb",
        "batch_execution_id": env["batch_execution_id"], "target_path": _REL,
        "pre_write_sha256": sha_a, "pre_write_size": len(_A),
        "pre_write_bytes_b64": base64.b64encode(_A).decode("ascii"),
        "timestamp": "2026-01-03T00:00:00+00:00", "source_kind": "FILESYSTEM_FILE",
        "source_identity": receipt["source_identity"],
        "operation_type": "UPDATE_TARGET_FROM_SOURCE", "decision_authority": "KX108_ONLY",
    }
    _store_json(evd / "receipts" / "child-rb.json", receipt)
    _store_json(evd / "rollback" / "child-rb.json", evidence)

    binding = {
        "batch_execution_id": env["batch_execution_id"], "child_execution_id": "child-rb",
        "execution_authority_hash": env["execution_authority_hash"], "approval_id": approval_id,
        "test_contract_hash": env["test_contract_hash"], "test_result_id": "tr-rb",
        "test_result_record_hash": "trh-rb", "kx108_input_translation_hash": "k" * 64,
    }

    def make_post(**over):
        return DS.run_and_persist_kx108_post_execution_decision(
            _post_kwargs("child-rb", _REL, **over), binding, pre_out["decision_record_id"],
            execution_dir=ex, pre_decision_store_dir=pdc, post_decision_store_dir=qdc)

    return {"tmp": tmp_path, "repo": repo, "tgt": tgt, "env": env,
            "ex": ex, "cx": cx, "pdc": pdc, "qdc": qdc, "evd": evd, "rrd": rrd,
            "approval_id": approval_id, "pre_id": pre_out["decision_record_id"],
            "sha_a": sha_a, "sha_b": sha_b, "make_post": make_post,
            "receipt_p": evd / "receipts" / "child-rb.json",
            "evidence_p": evd / "rollback" / "child-rb.json"}


def _rb(chain, **over):
    kw = dict(child_execution_id="child-rb", kx108_pre_decision_record_id=chain["pre_id"],
              execution_dir=chain["ex"], evidence_dir=chain["evd"],
              pre_decision_store_dir=chain["pdc"], post_decision_store_dir=chain["qdc"],
              rollback_result_dir=chain["rrd"], repo_root=chain["repo"])
    kw.update(over)
    return GR.run_governed_rollback(**kw)


def _hold_post(chain):
    out = chain["make_post"](tests_results="FAIL")  # 1 unknown + TICKET_NOT_READY -> HOLD
    assert out["status"] == "STORED" and out["x108_gate"] == "HOLD", out
    return out["decision_record_id"]


# ═══ A-H : refus avant toute écriture ═══

def test_a_no_trigger_refused(chain):
    r = _rb(chain)  # ni post id ni code
    assert r["status"] == GR.ROLLBACK_REFUSED_NOT_MUST_ROLLBACK
    assert chain["tgt"].read_bytes() == _B


def test_a2_both_triggers_refused(chain):
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain), rollback_trigger_code="TEST_INFRA_FAILURE")
    assert r["status"] == GR.ROLLBACK_REFUSED_NOT_MUST_ROLLBACK
    assert chain["tgt"].read_bytes() == _B


def test_a3_unknown_trigger_code_refused(chain):
    r = _rb(chain, rollback_trigger_code="MADE_UP")
    assert r["status"] == GR.ROLLBACK_REFUSED_NOT_MUST_ROLLBACK
    assert "UNKNOWN" in r["reason"]
    assert chain["tgt"].read_bytes() == _B


def test_b_pre_invalid_refused(chain):
    p = chain["pdc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text()); rec["decision_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec))
    r = _rb(chain, kx108_post_decision_record_id="kxpost-whatever-000000000000000000")
    assert r["status"] == GR.ROLLBACK_REFUSED_PRE_DECISION_INVALID
    assert chain["tgt"].read_bytes() == _B


def test_c_post_invalid_refused(chain):
    pid = _hold_post(chain)
    p = chain["qdc"] / f"{pid}.json"
    rec = json.loads(p.read_text()); rec["decision_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec))
    r = _rb(chain, kx108_post_decision_record_id=pid)
    assert r["status"] == GR.ROLLBACK_REFUSED_POST_DECISION_INVALID
    assert chain["tgt"].read_bytes() == _B


def test_d_post_allow_refused(chain):
    out = chain["make_post"]()  # kwargs propres -> ALLOW
    assert out["x108_gate"] == "ALLOW"
    r = _rb(chain, kx108_post_decision_record_id=out["decision_record_id"])
    assert r["status"] == GR.ROLLBACK_REFUSED_NOT_MUST_ROLLBACK
    assert chain["tgt"].read_bytes() == _B


def test_e_receipt_absent_refused(chain):
    chain["receipt_p"].unlink()
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_IDENTITY_MISMATCH
    assert r["reason"] == "APPLY_RECEIPT_NOT_FOUND"
    assert chain["tgt"].read_bytes() == _B


def test_f_receipt_tampered_refused(chain):
    pid = _hold_post(chain)
    # source_full_sha256 falsifié -> ne recoupe plus child.source_content_sha256
    rec = json.loads(chain["receipt_p"].read_text()); rec["source_full_sha256"] = "9" * 64
    chain["receipt_p"].write_text(json.dumps(rec))
    r = _rb(chain, kx108_post_decision_record_id=pid)
    assert r["status"] == GR.ROLLBACK_REFUSED_IDENTITY_MISMATCH
    assert r["reason"] == "APPLY_RECEIPT_CROSS_LINK_MISMATCH"
    assert chain["tgt"].read_bytes() == _B
    # target_post_sha256 falsifié -> D2 ne peut pas confirmer current==B -> DRIFT (fail-closed)
    rec2 = json.loads(chain["receipt_p"].read_text())
    rec2["source_full_sha256"] = _sha(_SRC); rec2["target_post_sha256"] = "9" * 64
    chain["receipt_p"].write_text(json.dumps(rec2))
    r2 = _rb(chain, kx108_post_decision_record_id=pid)
    assert r2["status"] == GR.ROLLBACK_REFUSED_POST_STATE_DRIFT
    assert chain["tgt"].read_bytes() == _B


def test_g_evidence_absent_refused(chain):
    chain["evidence_p"].unlink()
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_IDENTITY_MISMATCH
    assert r["reason"] == "ROLLBACK_EVIDENCE_NOT_FOUND"
    assert chain["tgt"].read_bytes() == _B


def test_h_l_m_n_preimage_invalid(chain):
    pid = _hold_post(chain)
    ev = json.loads(chain["evidence_p"].read_text())
    # H : bytes falsifiés (sha ne correspond plus)
    bad = dict(ev); bad["pre_write_bytes_b64"] = base64.b64encode(b"TAMPERED").decode()
    chain["evidence_p"].write_text(json.dumps(bad))
    assert _rb(chain, kx108_post_decision_record_id=pid)["status"] == GR.ROLLBACK_REFUSED_PREIMAGE_INVALID
    # L : base64 invalide
    bad = dict(ev); bad["pre_write_bytes_b64"] = "!!!not-base64!!!"
    chain["evidence_p"].write_text(json.dumps(bad))
    assert _rb(chain, kx108_post_decision_record_id=pid)["status"] == GR.ROLLBACK_REFUSED_PREIMAGE_INVALID
    # M : sha annoncé faux
    bad = dict(ev); bad["pre_write_sha256"] = "1" * 64
    chain["evidence_p"].write_text(json.dumps(bad))
    assert _rb(chain, kx108_post_decision_record_id=pid)["status"] == GR.ROLLBACK_REFUSED_PREIMAGE_INVALID
    # N : taille annoncée fausse
    bad = dict(ev); bad["pre_write_size"] = 999999
    chain["evidence_p"].write_text(json.dumps(bad))
    assert _rb(chain, kx108_post_decision_record_id=pid)["status"] == GR.ROLLBACK_REFUSED_PREIMAGE_INVALID
    assert chain["tgt"].read_bytes() == _B


# ═══ I / J / K : garde d'état courant ═══

def test_i_valid_hold_chain_rollback_succeeds(chain):
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_SUCCEEDED, r
    assert chain["tgt"].read_bytes() == _A                     # cible restaurée à la preimage exacte
    assert r["observed_before_rollback_sha256"] == chain["sha_b"]
    assert r["observed_after_rollback_sha256"] == chain["sha_a"]
    assert r["kx108_invocations_during_rollback"] == 0
    assert r["commit_review_eligible"] is False
    assert r["rollback_result_persisted"] is True
    rec = r["rollback_result"]
    assert rec["rollback_trigger_type"] == "KX108_POST_DECISION"
    assert rec["rollback_trigger_code"] == "HOLD"
    assert rec["evidence_sealed"] is False
    ok, reason = GR.verify_rollback_result(rec)
    assert ok, reason


def test_j_target_already_at_preimage(chain):
    chain["tgt"].write_bytes(_A)  # déjà rollback
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ALREADY_ROLLED_BACK
    assert chain["tgt"].read_bytes() == _A
    assert r["rollback_required"] is False and r["quarantine_required"] is False


def test_k_third_party_drift_preserved(chain):
    chain["tgt"].write_bytes(_C)  # drift tiers
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_POST_STATE_DRIFT
    assert chain["tgt"].read_bytes() == _C                     # octets tiers PRÉSERVÉS exactement
    assert r["quarantine_required"] is True


# ═══ O-U : sécurité de chemin + TOCTOU + échecs ═══

def test_o_target_path_escape_refused(chain):
    pid = _hold_post(chain)  # créer le POST HOLD AVANT de casser l'enveloppe
    p = chain["ex"] / "executions" / "be-rb" / "execution.json"
    env = json.loads(p.read_text())
    env["children"][0]["target_path"] = "../../outside.py"
    p.write_text(json.dumps(env))  # EAH stocké inchangé -> IDENTITY_MISMATCH (drift) en amont
    r = _rb(chain, kx108_post_decision_record_id=pid)
    assert r["status"] in (GR.ROLLBACK_REFUSED_PATH_SAFETY, GR.ROLLBACK_REFUSED_IDENTITY_MISMATCH)
    assert chain["tgt"].read_bytes() == _B


def test_p_target_symlink_refused(chain):
    outside = chain["tmp"] / "elsewhere.py"
    outside.write_bytes(_B)
    chain["tgt"].unlink()
    try:
        os.symlink(str(outside), str(chain["tgt"]))
    except (OSError, NotImplementedError):
        pytest.skip("symlink non supporté sur cette plateforme/permission")
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_PATH_SAFETY
    assert outside.read_bytes() == _B  # la cible du lien n'est pas touchée


def test_r_parent_component_reparse_refused(chain):
    outside_dir = chain["tmp"] / "elsewhere_dir"
    outside_dir.mkdir()
    parent = chain["repo"] / "periphery" / "xdomain"
    tgt_bytes = chain["tgt"].read_bytes()
    import shutil
    shutil.rmtree(parent)
    try:
        os.symlink(str(outside_dir), str(parent), target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink de répertoire non supporté")
    (parent).mkdir(exist_ok=True)  # via le lien
    (chain["repo"] / _REL).write_bytes(tgt_bytes)
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_PATH_SAFETY


def test_s_temp_write_failure_target_preserved(chain, monkeypatch):
    def boom(*a, **k):
        raise OSError("no fsync")
    monkeypatch.setattr(GR.os, "fsync", boom)
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_FAILED and r["reason"] == "TEMP_WRITE_FAILED"
    assert chain["tgt"].read_bytes() == _B                     # état B préservé
    assert r["quarantine_required"] is True


def test_t_drift_between_gates_aborts(chain, monkeypatch):
    real = GR._read_target_sha256
    calls = {"n": 0}
    def sneaky(path):
        calls["n"] += 1
        return real(path) if calls["n"] == 1 else "d" * 64  # drift au 2e appel (avant os.replace)
    monkeypatch.setattr(GR, "_read_target_sha256", sneaky)
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_REFUSED_POST_STATE_DRIFT
    assert chain["tgt"].read_bytes() == _B                     # non écrasé


def test_u_post_restore_hash_mismatch(chain, monkeypatch):
    real = GR._read_target_sha256
    calls = {"n": 0}
    def sim(path):
        calls["n"] += 1
        return "d" * 64 if calls["n"] >= 3 else real(path)     # observed_after (3e appel) faux
    monkeypatch.setattr(GR, "_read_target_sha256", sim)
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_FAILED and r["reason"] == "POST_RESTORE_HASH_MISMATCH"


# ═══ V : RollbackResult immuable ═══

def test_v_rollback_result_immutable(chain, tmp_path):
    d = tmp_path / "rr_store"
    rec = {
        "rollback_result_schema_version": GR.RESULT_SCHEMA_VERSION,
        "created_at": "2026-01-01T00:00:00+00:00", "status": GR.ROLLBACK_SUCCEEDED, "reason": None,
        "batch_execution_id": "b", "child_execution_id": "c", "execution_authority_hash": "e" * 64,
        "approval_id": "a", "kx108_pre_decision_record_id": "kxpre-x", "kx108_pre_decision_record_hash": "h" * 64,
        "rollback_trigger_type": "KX108_POST_DECISION", "rollback_trigger_code": "HOLD",
        "kx108_post_decision_record_id": "kxpost-x", "kx108_post_decision_record_hash": "p" * 64,
        "apply_receipt_sha256": "r" * 64, "rollback_evidence_sha256": "v" * 64,
        "target_path": "periphery/x.py", "expected_post_sha256": "b" * 64,
        "observed_before_rollback_sha256": "b" * 64, "restored_pre_sha256": "0" * 64,
        "observed_after_rollback_sha256": "0" * 64, "preimage_size": 3, "evidence_sealed": False,
        "decision_authority": "KX108_ONLY",
    }
    seed = {k: rec.get(k) for k in GR._IDENTITY_SEED_FIELDS}
    rec["rollback_result_id"] = GR._compute_rollback_result_identity(seed)
    rec["rollback_result_hash"] = GR.compute_rollback_result_hash(rec)
    assert GR.store_rollback_result(rec, d)["status"] == "STORED"
    assert GR.store_rollback_result(rec, d)["status"] == "IDEMPOTENT_EXISTING_IDENTICAL"
    tampered = dict(rec); tampered["reason"] = "MUTATED"
    tampered["rollback_result_hash"] = GR.compute_rollback_result_hash(tampered)
    assert GR.store_rollback_result(tampered, d)["status"] == "IMMUTABILITY_VIOLATION"
    reloaded = GR.load_rollback_result(rec["rollback_result_id"], d)
    ok, reason = GR.verify_rollback_result(reloaded)
    assert ok, reason


# ═══ W : idempotence ═══

def test_w_second_rollback_already_rolled_back(chain):
    pid = _hold_post(chain)
    assert _rb(chain, kx108_post_decision_record_id=pid)["status"] == GR.ROLLBACK_SUCCEEDED
    assert chain["tgt"].read_bytes() == _A
    r2 = _rb(chain, kx108_post_decision_record_id=pid)
    assert r2["status"] == GR.ALREADY_ROLLED_BACK
    assert chain["tgt"].read_bytes() == _A                     # aucune réécriture


# ═══ X : statique — aucune mutation d'autorité ═══

def test_x_static_no_forbidden_symbols():
    src = Path(GR.__file__).read_text(encoding="utf-8")
    for banned in ('git commit', 'git push', 'git merge', 'git reset', 'git clean',
                   'run_tooling_build_pipeline(', 'create_execution_closure_record(',
                   'build_family_remediation_candidate(', 'ingest_from_receipt(',
                   'apply_validated_source_content(', 'atomic_replace_with_bytes(',
                   'run_and_persist_kx108_decision(', 'run_and_persist_kx108_post_execution_decision(',
                   '["execution_status"]', "['execution_status']", '.execution_status ='):
        assert banned not in src, banned
    # aucune invocation KX108, aucune mutation closure/execution_status/family wiring/ledger
    assert "import sigma" not in src


# ═══ Y : déclencheur POST_PIPELINE_FAILURE ═══

@pytest.mark.parametrize("code", ["TEST_INFRA_FAILURE", "POST_EVIDENCE_UNAVAILABLE",
                                  "KX108_POST_INVOCATION_FAILURE", "KX108_POST_STORE_FAILURE",
                                  "KX108_POST_RECORD_INVALID"])
def test_y_failure_signal_rollback_succeeds(chain, code):
    chain["tgt"].write_bytes(_B)
    r = _rb(chain, rollback_trigger_code=code)
    assert r["status"] == GR.ROLLBACK_SUCCEEDED, r
    assert chain["tgt"].read_bytes() == _A
    rec = r["rollback_result"]
    assert rec["rollback_trigger_type"] == "POST_PIPELINE_FAILURE"
    assert rec["rollback_trigger_code"] == code
    assert rec["kx108_post_decision_record_id"] is None
    assert rec["kx108_post_decision_record_hash"] is None


# ═══ result verification API ═══

def test_result_api_persisted_reloaded_verified(chain):
    r = _rb(chain, kx108_post_decision_record_id=_hold_post(chain))
    assert r["status"] == GR.ROLLBACK_SUCCEEDED
    reloaded = GR.load_rollback_result(r["rollback_result_id"], chain["rrd"])
    ok, reason = GR.verify_rollback_result(reloaded)
    assert ok, reason
    assert reloaded["rollback_result_id"].startswith("rbk-")
    assert reloaded["decision_authority"] == "KX108_ONLY"
