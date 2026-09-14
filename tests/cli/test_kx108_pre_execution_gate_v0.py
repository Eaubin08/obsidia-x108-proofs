"""
tests/cli/test_kx108_pre_execution_gate_v0.py
=============================================
TWO_PHASE_KX108_PRE_EXECUTION_CHECKPOINT_A1_V0

Ordre canonique gelé : ExecutionEnvelope -> HumanApproval (validée) -> KX108_PRE.

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE (aucun mock de la décision
KX108 pour le contrôle positif) :

  - obsidia_kx108_pre_execution_evidence_adapter_v0.
      translate_pre_execution_evidence_to_tooling_build_state(...)
    charge/vérifie/valide une HumanApproval canonique stockée AVANT de
    produire une évidence PRE honnête (human_approval_status="APPROVED" n'est
    posé qu'après validation canonique — jamais une chaîne arbitraire).
  - aucune évidence post-apply n'est requise ni lue (apply receipt,
    TestContractResult, target_post_sha256, git diff post-apply).
  - le kernel souverain INCHANGÉ (sigma.protocols.run_tooling_build_pipeline)
    évalue l'évidence PRE et — pour un paquet propre + approbation valide —
    rend x108_gate == "ALLOW".
  - obsidia_kx108_decision_store.run_and_persist_kx108_pre_execution_decision
    persiste un enregistrement decision_phase="PRE_EXECUTION" (portant
    approval_id, jamais test_result_*), rechargé + vérifié.
  - le chemin POST historique reste inchangé ; un enregistrement sans
    decision_phase se vérifie/s'interprète toujours comme POST_EXECUTION.

Tous les artefacts (approbation, contexte pré-exécution, enveloppe,
décision KX108 PRE) sont écrits UNIQUEMENT dans des magasins temporaires
isolés (tmp_path). AUCUNE mutation de cible. AUCUN git.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import obsidia_batch_execution as E          # noqa: E402
import obsidia_pre_execution_context as PEC  # noqa: E402
import obsidia_test_contract as TC           # noqa: E402
import obsidia_kx108_decision_store as DS    # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as ADP  # noqa: E402


# ─── fixtures canoniques isolées ────────────────────────────────────────────

_TARGET = "periphery/xdomain/pre_gate_target_v0.py"
_SRC_SHA = "b" * 64
_TGT_PRE_SHA = "c" * 64


def _make_pre_ctx_record(**over) -> dict:
    manifest = {
        "repository_identity": "repo-alpha",
        "execution_worktree_path": "/wt/exec",
        "branch_name": "feat/terminal-runtime-repair-and-bounded-build-v1",
        "base_sha": "a" * 40,
        "source_kind": "CONTENT",
        "source_repository_identity": "repo-alpha",
        "source_commit": "",
        "source_blob_sha": "",
        "source_path": "",
        "source_sha256": _SRC_SHA,
        "target_path": _TARGET,
        "target_pre_sha256": _TGT_PRE_SHA,
        "operation": "REPLACE",
        "approved_scope": [_TARGET],
        "protected_scope_status": "CLEAN",
        "test_contract_hash": None,  # rempli plus bas depuis l'enveloppe
        "schema_version": 2,
    }
    manifest.update(over.pop("manifest", {}))
    rec = {
        "context_schema_version": 2,
        "created_at": "2026-01-01T00:00:00+00:00",
        "repository_identity": manifest["repository_identity"],
        "repository_root": "/wt/main",
        "execution_worktree_path": manifest["execution_worktree_path"],
        "branch_name": manifest["branch_name"],
        "base_sha": manifest["base_sha"],
        "target_path": manifest["target_path"],
        "target_pre_sha256": manifest["target_pre_sha256"],
        "source_kind": manifest["source_kind"],
        "source_repository_identity": manifest["source_repository_identity"],
        "source_commit": manifest["source_commit"],
        "source_blob_sha": manifest["source_blob_sha"],
        "source_path": manifest["source_path"],
        "source_sha256": manifest["source_sha256"],
        "operation": manifest["operation"],
        "approved_scope": manifest["approved_scope"],
        "worktree_isolated": True,
        "branch_isolated": True,
        "protected_scope_status": "CLEAN",
        "manifest": manifest,
        "legacy_manifest_hash_short": "0" * 16,
        "decision_authority": "KX108_ONLY",
    }
    rec.update(over)
    rec["manifest_sha256"] = PEC.compute_manifest_sha256(rec["manifest"])
    seed_fields = [f for f in PEC._CONTEXT_BOUND_FIELDS_V2
                   if f not in ("context_schema_version", "context_id", "created_at")]
    rec["context_id"] = "pec-" + hashlib.sha256(
        json.dumps({k: rec.get(k) for k in seed_fields}, sort_keys=True).encode("utf-8")
    ).hexdigest()[:32]
    rec["context_record_hash"] = PEC.compute_context_record_hash(rec)
    return rec


def _make_envelope(pre_ctx: dict, **over) -> dict:
    child = {
        "candidate_entry_id": "cand-1",
        "child_execution_id": "child-1",
        "source_kind": "CONTENT",
        "source_hash": "d" * 16,
        "source_content_sha256": _SRC_SHA,
        "source_repository_identity": "repo-alpha",
        "source_git_commit_sha": "",
        "source_git_blob_sha": "",
        "source_git_historical_path": "",
        "target_path": pre_ctx["target_path"],
        "target_pre_hash": "e" * 16,
        "target_pre_sha256": pre_ctx["target_pre_sha256"],
        "operation_type": "REPLACE",
        "operation_reason": "pre-gate pilot child",
        "execution_status": "PLANNED",
    }
    child.update(over.pop("child", {}))
    env = {
        "batch_execution_id": "be-a1",
        "batch_id": "b-a1",
        "batch_hash": "f" * 16,
        "batch_hash_version": 1,
        "candidate_scope_hash": "9" * 16,
        "execution_order": ["cand-1"],
        "dependency_edges": [],
        "children": [child],
        "decision_authority": "KX108_ONLY",
        "integrity_verified": True,
        "pre_execution_context_id": pre_ctx["context_id"],
        "pre_execution_context_record_hash": pre_ctx["context_record_hash"],
    }
    tc = {
        "test_contract_schema_version": 1,
        "contract_id": "tc-a1",
        "candidate_entry_id": "cand-1",
        "batch_id": env["batch_id"],
        "target_path": child["target_path"],
        "checks": [],
        "decision_authority": "KX108_ONLY",
    }
    env["test_contract"] = tc
    env["test_contract_hash"] = TC.compute_test_contract_hash(tc)
    env.update(over)
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    return env


def _store_envelope(envelope: dict, execution_dir: Path) -> None:
    p = execution_dir / "executions" / envelope["batch_execution_id"] / "execution.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")


def _store_pre_ctx(rec: dict, ctx_dir: Path) -> None:
    ctx_dir.mkdir(parents=True, exist_ok=True)
    (ctx_dir / f"{rec['context_id']}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _store_canonical_approval(envelope: dict, execution_dir: Path,
                              approval_id: str = "appr-a1-001", **over) -> str:
    """Utilise la vraie machinerie d'approbation Obsidia (store_approval_artifact) —
    jamais un dict arbitraire."""
    rec = {
        "approval_id": approval_id,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-01-02T00:00:00+00:00",
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": envelope["batch_id"],
        "batch_hash": envelope["batch_hash"],
        "candidate_scope_hash": envelope["candidate_scope_hash"],
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approved_by": "HUMAN",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": "KX108_ONLY",
    }
    rec.update(over)
    rec["approval_record_hash"] = E.compute_approval_record_hash(rec)
    res = E.store_approval_artifact(rec, execution_dir=execution_dir)
    assert res["status"] in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"), res
    return approval_id


@pytest.fixture
def canon(tmp_path):
    exec_dir = tmp_path / "batch_execution"
    ctx_dir = tmp_path / "pre_execution_contexts"
    dec_dir = tmp_path / "kx108_decisions"
    pre_ctx = _make_pre_ctx_record()
    env = _make_envelope(pre_ctx)
    _store_pre_ctx(pre_ctx, ctx_dir)
    _store_envelope(env, exec_dir)
    approval_id = _store_canonical_approval(env, exec_dir)
    return {
        "exec_dir": exec_dir, "ctx_dir": ctx_dir, "dec_dir": dec_dir,
        "pre_ctx": pre_ctx, "env": env, "approval_id": approval_id,
    }


def _translate(canon, **over):
    kw = dict(
        batch_execution_id=canon["env"]["batch_execution_id"],
        child_execution_id="child-1",
        approval_id=canon["approval_id"],
        execution_dir=canon["exec_dir"],
        pre_execution_context_dir=canon["ctx_dir"],
    )
    kw.update(over)
    return ADP.translate_pre_execution_evidence_to_tooling_build_state(**kw)


# ─── 1-6 : approbation canonique ───────────────────────────────────────────

def test_1_valid_canonical_approval_loads(canon):
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_READY, r
    assert r["translation_report"]["human_approval_status"] == "APPROVED"
    assert r["translation_report"]["human_approval_bound_to_current_execution"] is True
    assert r["pre_tooling_build_state_kwargs"]["human_approval_status"] == "APPROVED"


def test_2_arbitrary_caller_dict_cannot_act_as_authority(canon):
    """L'adaptateur n'accepte qu'un approval_id : il n'y a AUCUN paramètre
    permettant d'injecter un dict d'approbation. Un id inexistant échoue fermé."""
    import inspect
    sig = inspect.signature(ADP.translate_pre_execution_evidence_to_tooling_build_state)
    assert "approval" not in sig.parameters  # pas d'entrée dict
    assert "approval_id" in sig.parameters
    r = _translate(canon, approval_id="appr-not-stored-xyz")
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"] == "HUMAN_APPROVAL_NOT_FOUND"


def test_3_missing_approval_fails_closed(canon):
    r = _translate(canon, approval_id="appr-absent-001")
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"] == "HUMAN_APPROVAL_NOT_FOUND"


def test_4_invalid_approval_artifact_fails_closed(canon):
    # approbation stockée avec un hash d'enregistrement corrompu
    _store_canonical_approval(canon["env"], canon["exec_dir"],
                              approval_id="appr-corrupt-001")
    p = canon["exec_dir"] / "approvals" / "appr-corrupt-001" / "approval.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    rec["approval_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec), encoding="utf-8")
    r = _translate(canon, approval_id="appr-corrupt-001")
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"].startswith("HUMAN_APPROVAL_ARTIFACT_INVALID")


def test_5_approval_for_wrong_execution_authority_hash_fails_closed(canon):
    _store_canonical_approval(canon["env"], canon["exec_dir"],
                              approval_id="appr-wrong-eah-001",
                              execution_authority_hash="f" * 64)
    r = _translate(canon, approval_id="appr-wrong-eah-001")
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"].startswith("HUMAN_APPROVAL_NOT_BOUND_TO_EXECUTION") \
        or r["reason"] == "HUMAN_APPROVAL_EXECUTION_AUTHORITY_HASH_MISMATCH"


def test_6_approved_status_only_after_canonical_validation(canon):
    """human_approval_status='APPROVED' n'apparaît QUE si l'approbation
    canonique valide ; sinon aucune évidence n'est produite."""
    r_ok = _translate(canon)
    assert r_ok["pre_tooling_build_state_kwargs"]["human_approval_status"] == "APPROVED"
    r_bad = _translate(canon, approval_id="appr-absent-002")
    assert r_bad["pre_tooling_build_state_kwargs"] is None


# ─── 7-12 : évidence pré-action pure ───────────────────────────────────────

def test_7_no_apply_receipt_required(canon):
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_READY
    src = Path(ADP.__file__).read_text(encoding="utf-8")
    # aucun APPEL à des helpers d'évidence post-apply
    assert "load_apply_receipt(" not in src
    assert "obsidia_content_apply" not in src


def test_8_no_test_contract_result_required(canon):
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_READY
    src = Path(ADP.__file__).read_text(encoding="utf-8")
    assert "load_test_contract_result(" not in src
    assert "run_and_persist_test_contract(" not in src


def test_9_no_post_action_fields_used(canon):
    r = _translate(canon)
    assert r["translation_report"]["post_action_fields_present"] == []
    kw = r["pre_tooling_build_state_kwargs"]
    assert kw["tests_results"] == "UNKNOWN"
    assert kw["gates_results"] == "UNKNOWN"
    assert kw["actual_touched_files"] == []
    assert kw["commit_status"] == "NOT_COMMITTED"
    assert kw["push_status"] == "NOT_PUSHED"
    assert kw["merge_status"] == "NOT_MERGED"
    assert "target_post_sha256" not in json.dumps(r)


def test_10_execution_authority_hash_drift_fails_closed(canon):
    p = canon["exec_dir"] / "executions" / "be-a1" / "execution.json"
    env = json.loads(p.read_text(encoding="utf-8"))
    env["execution_authority_hash"] = "0" * 64
    p.write_text(json.dumps(env), encoding="utf-8")
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"] == "EXECUTION_AUTHORITY_HASH_DRIFT"


def test_11_pre_context_hash_mismatch_fails_closed(canon):
    p = canon["exec_dir"] / "executions" / "be-a1" / "execution.json"
    env = json.loads(p.read_text(encoding="utf-8"))
    env["pre_execution_context_record_hash"] = "0" * 64
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env), encoding="utf-8")
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_NOT_READY
    assert r["reason"] == "PRE_EXECUTION_CONTEXT_HASH_MISMATCH"


def test_12_source_content_binding_present_through_envelope(canon):
    r = _translate(canon)
    assert r["translation_report"]["source_content_sha256"] == _SRC_SHA
    # lié transitivement : recompute EAH dépend de source_content_sha256
    env = canon["env"]
    env2 = json.loads(json.dumps(env))
    env2["children"][0]["source_content_sha256"] = "1" * 64
    assert E.compute_execution_authority_hash(env2) != env["execution_authority_hash"]


# ─── 13-14 : hash de traduction + approval_id ─────────────────────────────

def test_13_translation_hash_deterministic(canon):
    a = _translate(canon)["kx108_input_translation_hash"]
    b = _translate(canon)["kx108_input_translation_hash"]
    assert a == b and len(a) == 64


def test_13b_authority_relevant_change_changes_translation_hash(canon):
    base = _translate(canon)["kx108_input_translation_hash"]
    # nouvelle enveloppe avec un source_content_sha256 différent -> EAH différent
    pre_ctx2 = _make_pre_ctx_record(manifest={"source_sha256": "7" * 64})
    env2 = _make_envelope(
        pre_ctx2,
        batch_execution_id="be-a1-alt",
        child={"source_content_sha256": "7" * 64},
    )
    _store_pre_ctx(pre_ctx2, canon["ctx_dir"])
    _store_envelope(env2, canon["exec_dir"])
    aid2 = _store_canonical_approval(env2, canon["exec_dir"], approval_id="appr-a1-alt")
    r2 = _translate(canon, batch_execution_id="be-a1-alt", approval_id=aid2)
    assert r2["status"] == ADP.STATUS_READY
    assert r2["kx108_input_translation_hash"] != base


def test_14_approval_id_in_translation_and_binding(canon):
    r = _translate(canon)
    assert r["pre_binding_context"]["approval_id"] == canon["approval_id"]
    assert r["translation_report"]["approval_id"] == canon["approval_id"]


# ─── 15-19 : décision PRE réelle (kernel canonique) ───────────────────────

def test_15_pre_decision_invokes_kx108_exactly_once(canon, monkeypatch):
    r = _translate(canon)
    calls = {"n": 0}
    import sigma.protocols as SP
    real = SP.run_tooling_build_pipeline

    def counting(state):
        calls["n"] += 1
        return real(state)

    monkeypatch.setattr(SP, "run_tooling_build_pipeline", counting)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    assert calls["n"] == 1, calls
    assert out["verify_ok"] is True, out


def test_16_17_real_clean_approved_pre_state_yields_allow(canon):
    r = _translate(canon)
    assert r["status"] == ADP.STATUS_READY
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    rec = out["record"]
    assert rec is not None
    # résultat RÉEL du kernel souverain canonique — non forcé
    assert rec["x108_gate"] == "ALLOW", (
        f"gate={rec['x108_gate']} unknowns={rec['unknowns']} "
        f"contradictions={rec['contradictions']} risk_flags={rec['risk_flags']}"
    )
    assert rec["canonical_envelope"]["x108_gate"] == "ALLOW"


def test_18_hold_or_block_never_authorizes(canon):
    """Un 2e unknown injecté dans l'état PRE -> le kernel canonique rend HOLD,
    et l'enregistrement porte fidèlement ce gate non-autorisant."""
    r = _translate(canon)
    kw = dict(r["pre_tooling_build_state_kwargs"])
    kw["base_sha"] = ""  # SessionIntegrityAgent -> BASE_SHA_MISSING (2e unknown)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        kw, r["pre_binding_context"], store_dir=canon["dec_dir"],
    )
    assert out["record"]["x108_gate"] in ("HOLD", "BLOCK")
    assert out["record"]["x108_gate"] != "ALLOW"


def test_19_pre_decision_record_persisted_reloaded_verified(canon):
    r = _translate(canon)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    assert out["store_result"]["status"] in ("STORED", "IDEMPOTENT_EXISTING_IDENTICAL")
    reloaded = DS.load_kx108_decision_record(out["decision_record_id"], store_dir=canon["dec_dir"])
    ok, reason = DS.verify_kx108_decision_record(reloaded)
    assert ok, reason
    assert out["decision_record_id"].startswith("kxpre-")


# ─── 20-22 : schéma PRE ───────────────────────────────────────────────────

def test_20_decision_phase_is_pre_execution(canon):
    r = _translate(canon)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    assert out["record"]["decision_phase"] == "PRE_EXECUTION"
    assert DS.decision_phase_of(out["record"]) == "PRE_EXECUTION"


def test_21_approval_id_preserved_in_pre_record(canon):
    r = _translate(canon)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    assert out["record"]["approval_id"] == canon["approval_id"]
    assert out["record"]["execution_authority_hash"] == canon["env"]["execution_authority_hash"]


def test_22_no_test_result_fields_in_pre_record(canon):
    r = _translate(canon)
    out = DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    rec = out["record"]
    assert "test_result_id" not in rec
    assert "test_result_record_hash" not in rec
    assert "approval_id" not in DS._PRE_BINDING_CONTEXT_FIELDS or True  # approval_id IS present
    assert "approval_id" in DS._PRE_BINDING_CONTEXT_FIELDS
    assert "test_result_id" not in DS._PRE_BINDING_CONTEXT_FIELDS


# ─── 23-24 : compatibilité POST / legacy ─────────────────────────────────

def test_23_legacy_missing_phase_record_still_post_compatible():
    """Un enregistrement sans clé decision_phase : hash + vérification via le
    jeu de champs POST d'origine, exactement comme avant ce checkpoint."""
    legacy = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": "kxd-legacy0000000000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": "be-x", "child_execution_id": "ch-x",
        "execution_authority_hash": "h" * 64,
        "approval_id": "ap-x", "test_contract_hash": "tc" * 32,
        "test_result_id": "tr-x", "test_result_record_hash": "trh" * 10,
        "kx108_input_translation_hash": "kx" * 32,
        "decision_id": "d-x", "trace_id": "t-x", "domain": "tooling_build",
        "x108_gate": "ALLOW", "reason_code": "GUARD_ALLOW", "severity": "S0",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "contradictions": [], "unknowns": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY", "canonical_envelope": {"x108_gate": "ALLOW"},
    }
    assert DS.decision_phase_of(legacy) == "POST_EXECUTION"
    legacy["decision_record_hash"] = DS.compute_kx108_decision_record_hash(legacy)
    ok, reason = DS.verify_kx108_decision_record(legacy)
    assert ok, reason
    # le hash POST n'utilise PAS decision_phase / pre_execution_context_id
    assert "decision_phase" not in json.dumps(
        {k: legacy.get(k) for k in DS._RECORD_BOUND_FIELDS}
    )


def test_24_post_binding_context_still_requires_full_post_evidence():
    """_validate_binding_context (POST) refuse toujours en l'absence des champs
    post-apply — aucune relaxation."""
    incomplete_post = {
        "batch_execution_id": "b", "child_execution_id": "c",
        "execution_authority_hash": "e", "approval_id": "a",
        "test_contract_hash": "t", "kx108_input_translation_hash": "k",
        # test_result_id / test_result_record_hash ABSENTS
    }
    err = DS._validate_binding_context(incomplete_post)
    assert err is not None and "test_result_id" in err


# ─── 25-26 : zéro mutation / zéro git ────────────────────────────────────

def test_25_zero_target_mutation(canon, tmp_path):
    # crée un faux fichier cible hors des magasins isolés et vérifie qu'il
    # n'est jamais touché par le chemin PRE
    fake_target = tmp_path / "fake_repo" / _TARGET
    fake_target.parent.mkdir(parents=True, exist_ok=True)
    fake_target.write_bytes(b"ORIGINAL BYTES\n")
    before = fake_target.read_bytes()
    r = _translate(canon, repo_root=tmp_path / "fake_repo")
    DS.run_and_persist_kx108_pre_execution_decision(
        r["pre_tooling_build_state_kwargs"], r["pre_binding_context"],
        store_dir=canon["dec_dir"],
    )
    assert fake_target.read_bytes() == before


def test_26_no_git_and_no_apply_symbols_in_pre_path():
    adp_src = Path(ADP.__file__).read_text(encoding="utf-8")
    for banned in ("import subprocess", "subprocess.run", "import shutil",
                   "shutil.copy", "apply_proposal", "run_bounded_apply",
                   "apply_validated_source_content", "os.link", "write_text(",
                   "write_bytes("):
        assert banned not in adp_src, banned
    ds_src = Path(DS.__file__).read_text(encoding="utf-8")
    for banned in ("git commit", "git push", "git merge", "apply_proposal",
                   "run_bounded_apply", "shutil.copy"):
        assert banned not in ds_src, banned
