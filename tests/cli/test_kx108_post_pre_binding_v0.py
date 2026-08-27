"""
tests/cli/test_kx108_post_pre_binding_v0.py
==========================================
KX108_POST_PRE_BINDING_D1_V0

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE (kernel sigma non mocké pour
les invocations positives) :

  - obsidia_kx108_decision_store.run_and_persist_kx108_post_execution_decision
    charge + vérifie CANONIQUEMENT la décision KX108_PRE référencée par id,
    recalcule l'execution_authority_hash courant depuis l'ExecutionEnvelope,
    exige pre.phase==PRE_EXECUTION / pre.x108_gate==ALLOW /
    pre.approval_id==binding.approval_id / pre.EAH==current_eah /
    binding.EAH==current_eah — AVANT toute invocation du kernel KX108_POST
    (kernel call count = 0 sur tout rejet). Le hash du record PRE est
    dérivé du record RECHARGÉ, jamais de l'appelant, et persisté dans
    l'enregistrement POST lié.
  - le chemin POST legacy (run_and_persist_kx108_decision) + les records
    POST historiques sans decision_phase restent vérifiables et inchangés.
  - obsidia_post_execution_disposition_v0.classify_post_execution_disposition
    (READ_ONLY, NON_SOVEREIGN) : x108_gate POST ALLOW ->
    KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW ; HOLD/BLOCK ou signal d'échec
    canonique -> MUST_ROLLBACK. AUCUN rollback exécuté. AUCUNE mutation.

Tous les artefacts en magasins temporaires isolés. AUCUNE mutation de
cible. AUCUN git commit/push/merge.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_batch_execution as E            # noqa: E402
import obsidia_kx108_decision_store as DS      # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PREADP  # noqa: E402
import obsidia_post_execution_disposition_v0 as DISP              # noqa: E402
import test_kx108_pre_execution_gate_v0 as A1T                    # noqa: E402  (helpers réutilisés)


def _clean_post_kwargs(child_id: str, target: str, **over) -> dict:
    kw = {
        "session_id": child_id, "objective": "",
        "base_sha": "a" * 40, "manifest_hash": "m" * 64, "diff_hash": "",
        "approved_scope": [target], "actual_touched_files": [target],
        "new_files": [], "deleted_files": [],
        "protected_scope_status": "CLEAN", "human_approval_status": "APPROVED",
        "obsidure_status": "NOT_APPLICABLE",
        "worktree_isolated": True, "branch_isolated": True,
        "auto_commit_disabled": True, "auto_push_disabled": True, "auto_merge_disabled": True,
        "tests_results": "PASS", "gates_results": "PASS", "first_failure": "",
        "commit_status": "NOT_COMMITTED", "push_status": "NOT_PUSHED", "merge_status": "NOT_MERGED",
        "unknowns": [], "contradictions": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY",
    }
    kw.update(over)
    return kw


@pytest.fixture
def chain(tmp_path):
    """Chaîne canonique isolée : envelope + pre_ctx + HumanApproval + KX108_PRE réel (ALLOW)."""
    ex, cx, pre_dc, post_dc = (tmp_path / "exec", tmp_path / "ctx",
                               tmp_path / "pre_dec", tmp_path / "post_dec")
    pre_ctx = A1T._make_pre_ctx_record()
    env = A1T._make_envelope(pre_ctx)
    A1T._store_pre_ctx(pre_ctx, cx)
    A1T._store_envelope(env, ex)
    approval_id = A1T._store_canonical_approval(env, ex)
    tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        env["batch_execution_id"], "child-1", approval_id,
        execution_dir=ex, pre_execution_context_dir=cx)
    assert tr["status"] == PREADP.STATUS_READY, tr
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        tr["pre_tooling_build_state_kwargs"], tr["pre_binding_context"], store_dir=pre_dc)
    assert pre_out["record"]["x108_gate"] == "ALLOW", pre_out["record"]
    child = env["children"][0]
    post_binding = {
        "batch_execution_id": env["batch_execution_id"],
        "child_execution_id": child["child_execution_id"],
        "execution_authority_hash": env["execution_authority_hash"],
        "approval_id": approval_id,
        "test_contract_hash": env["test_contract_hash"],
        "test_result_id": "tr-d1-0001",
        "test_result_record_hash": "trh-d1-0001-record-hash",
        "kx108_input_translation_hash": "k" * 64,
    }
    return {"tmp": tmp_path, "ex": ex, "cx": cx, "pre_dc": pre_dc, "post_dc": post_dc,
            "env": env, "child": child, "approval_id": approval_id,
            "pre_id": pre_out["decision_record_id"], "post_binding": post_binding,
            "target": child["target_path"]}


def _run_post(chain, *, kwargs=None, binding=None, pre_id=None):
    return DS.run_and_persist_kx108_post_execution_decision(
        kwargs if kwargs is not None else _clean_post_kwargs(chain["child"]["child_execution_id"], chain["target"]),
        binding if binding is not None else chain["post_binding"],
        pre_id if pre_id is not None else chain["pre_id"],
        execution_dir=chain["ex"],
        pre_decision_store_dir=chain["pre_dc"],
        post_decision_store_dir=chain["post_dc"],
    )


# ─── A-I : rejets AVANT invocation du kernel (kernel call count = 0) ─────────

def test_a_pre_id_missing_rejected_no_kernel_call(chain):
    r = _run_post(chain, pre_id="kxpre-does-not-exist-000000000000")
    assert r["status"] == "REJECTED" and r["reason"] == "KX108_PRE_DECISION_NOT_FOUND"
    assert r["kx108_kernel_call_count"] == 0


def test_a2_pre_id_empty_rejected(chain):
    r = _run_post(chain, pre_id="   ")
    assert r["status"] == "REJECTED" and r["reason"] == "KX108_PRE_DECISION_RECORD_ID_MISSING"
    assert r["kx108_kernel_call_count"] == 0


def test_b_pre_record_integrity_invalid_rejected(chain):
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text()); rec["decision_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec))
    r = _run_post(chain)
    assert r["status"] == "REJECTED" and r["reason"].startswith("KX108_PRE_DECISION_INVALID")
    assert r["kx108_kernel_call_count"] == 0


def test_c_referenced_record_is_post_phase_rejected(chain):
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec.pop("decision_phase", None)  # -> traité POST
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _run_post(chain)
    assert r["status"] == "REJECTED"
    assert (r["reason"] == "KX108_PRE_DECISION_NOT_PRE_EXECUTION_PHASE"
            or r["reason"].startswith("KX108_PRE_DECISION_INVALID"))
    assert r["kx108_kernel_call_count"] == 0


def test_d_e_pre_gate_hold_or_block_rejected(chain):
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    for gate in ("HOLD", "BLOCK"):
        rec = json.loads(p.read_text())
        rec["x108_gate"] = gate
        rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
        p.write_text(json.dumps(rec))
        r = _run_post(chain)
        assert r["status"] == "REJECTED" and r["reason"] == "KX108_PRE_GATE_NOT_ALLOW"
        assert r["kx108_kernel_call_count"] == 0


def test_f_pre_approval_id_mismatch_rejected(chain):
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec["approval_id"] = "some-other-approval"
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _run_post(chain)
    assert r["status"] == "REJECTED" and r["reason"] == "KX108_PRE_APPROVAL_ID_MISMATCH"
    assert r["kx108_kernel_call_count"] == 0


def test_g_pre_eah_mismatch_rejected(chain):
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec["execution_authority_hash"] = "e" * 64
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _run_post(chain)
    assert r["status"] == "REJECTED" and r["reason"] == "KX108_PRE_EXECUTION_AUTHORITY_HASH_MISMATCH"
    assert r["kx108_kernel_call_count"] == 0


def test_h_post_binding_eah_mismatch_rejected(chain):
    b = dict(chain["post_binding"]); b["execution_authority_hash"] = "f" * 64
    r = _run_post(chain, binding=b)
    assert r["status"] == "REJECTED"
    assert r["reason"] in ("POST_BINDING_EXECUTION_AUTHORITY_HASH_MISMATCH",
                           "KX108_PRE_EXECUTION_AUTHORITY_HASH_MISMATCH")
    assert r["kx108_kernel_call_count"] == 0


def test_i_tampered_envelope_eah_drift_rejected(chain):
    p = chain["ex"] / "executions" / chain["env"]["batch_execution_id"] / "execution.json"
    env = json.loads(p.read_text())
    # source_content_sha256 ∈ _EXECUTION_AUTHORITY_CHILD_FIELDS -> recompute EAH ≠ stocké
    env["children"][0]["source_content_sha256"] = "1" * 64
    p.write_text(json.dumps(env))
    r = _run_post(chain)
    assert r["status"] == "REJECTED" and r["reason"] == "EXECUTION_AUTHORITY_HASH_DRIFT"
    assert r["kx108_kernel_call_count"] == 0


def test_i2_missing_post_binding_field_rejected(chain):
    b = dict(chain["post_binding"]); b["test_result_id"] = ""
    r = _run_post(chain, binding=b)
    assert r["status"] == "REJECTED" and "test_result_id" in r["reason"]
    assert r["kx108_kernel_call_count"] == 0


# ─── J : chaîne exacte valide -> le kernel POST peut s'exécuter ─────────────

def test_j_valid_linked_post_executes_kernel_once(chain):
    r = _run_post(chain)
    assert r["status"] == "STORED", r
    assert r["kx108_kernel_call_count"] == 1
    assert r["decision_phase"] == "POST_EXECUTION"
    assert r["decision_record_id"].startswith("kxpost-")
    assert r["x108_gate"] == "ALLOW"  # état POST propre -> kernel réel -> ALLOW
    assert r["verify_ok"] is True


def test_j2_kernel_invoked_exactly_once(chain, monkeypatch):
    import sigma.protocols as SP
    calls = {"n": 0}; real = SP.run_tooling_build_pipeline
    monkeypatch.setattr(SP, "run_tooling_build_pipeline",
                        lambda s: (calls.__setitem__("n", calls["n"] + 1) or real(s)))
    _run_post(chain)
    assert calls["n"] == 1
    # un rejet amont -> 0 appel
    calls["n"] = 0
    _run_post(chain, pre_id="kxpre-nope-000000000000000000000")
    assert calls["n"] == 0


# ─── 19 : hash du record PRE — dérivé canoniquement, non surchargeable ──────

def test_19_pre_record_hash_bound_from_reloaded_record(chain):
    r = _run_post(chain)
    pre = DS.load_kx108_decision_record(chain["pre_id"], store_dir=chain["pre_dc"])
    assert r["kx108_pre_decision_record_id"] == chain["pre_id"]
    assert r["kx108_pre_decision_record_hash"] == pre["decision_record_hash"]
    assert r["record"]["kx108_pre_decision_record_id"] == chain["pre_id"]
    assert r["record"]["kx108_pre_decision_record_hash"] == pre["decision_record_hash"]


def test_19b_changing_pre_bytes_rejects_linked_post(chain):
    # 1er POST OK
    assert _run_post(chain)["status"] == "STORED"
    # falsifier le record PRE -> POST suivant rejeté (verify PRE échoue)
    p = chain["pre_dc"] / f"{chain['pre_id']}.json"
    rec = json.loads(p.read_text()); rec["reason_code"] = "TAMPERED"
    p.write_text(json.dumps(rec))
    r = _run_post(chain)
    assert r["status"] == "REJECTED" and r["reason"].startswith("KX108_PRE_DECISION_INVALID")
    assert r["kx108_kernel_call_count"] == 0


# ─── 11 : contenu du record POST lié ───────────────────────────────────────

def test_11_linked_post_record_fields(chain):
    rec = _run_post(chain)["record"]
    for f in ("decision_phase", "batch_execution_id", "child_execution_id",
              "execution_authority_hash", "approval_id", "test_contract_hash",
              "test_result_id", "test_result_record_hash", "kx108_input_translation_hash",
              "kx108_pre_decision_record_id", "kx108_pre_decision_record_hash",
              "x108_gate", "canonical_envelope", "decision_record_id", "decision_record_hash"):
        assert f in rec, f
    assert rec["decision_phase"] == "POST_EXECUTION"
    assert DS.decision_phase_of(rec) == "POST_EXECUTION"
    ok, reason = DS.verify_kx108_decision_record(rec)
    assert ok, reason


# ─── 22 : POST ALLOW / HOLD / BLOCK -> disposition ────────────────────────

def test_22_post_allow_keeps_eligible(chain):
    out = _run_post(chain)
    d = DISP.classify_post_execution_disposition(
        post_decision_record_id=out["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    assert d["status"] == DISP.DISPOSITION_CLASSIFIED
    assert d["disposition"] == DISP.KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert d["commit_review_eligible"] is True and d["rollback_required"] is False
    assert d["kx108_post_gate"] == "ALLOW"
    assert d["authority"] == "NON_SOVEREIGN" and d["write_capability"] is False


def test_22b_post_hold_must_rollback(chain):
    kw = _clean_post_kwargs(chain["child"]["child_execution_id"], chain["target"],
                            tests_results="FAIL")  # 1 unknown + TICKET_NOT_READY -> HOLD
    out = _run_post(chain, kwargs=kw)
    assert out["status"] == "STORED" and out["x108_gate"] == "HOLD", out
    d = DISP.classify_post_execution_disposition(
        post_decision_record_id=out["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    assert d["disposition"] == DISP.MUST_ROLLBACK
    assert d["commit_review_eligible"] is False and d["rollback_required"] is True


def test_22c_post_block_must_rollback(chain):
    kw = _clean_post_kwargs(chain["child"]["child_execution_id"], chain["target"],
                            worktree_isolated=False, branch_isolated=False)  # 2 contradictions -> BLOCK
    out = _run_post(chain, kwargs=kw)
    assert out["status"] == "STORED" and out["x108_gate"] == "BLOCK", out
    d = DISP.classify_post_execution_disposition(
        post_decision_record_id=out["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    assert d["disposition"] == DISP.MUST_ROLLBACK
    assert d["rollback_required"] is True and d["commit_review_eligible"] is False


# ─── 23 : classificateur — signaux d'échec canoniques -> MUST_ROLLBACK ─────

@pytest.mark.parametrize("sig", sorted(DISP.CANONICAL_FAILURE_SIGNALS))
def test_23_failure_signal_must_rollback(sig):
    d = DISP.classify_post_execution_disposition(failure_signal=sig)
    assert d["status"] == DISP.DISPOSITION_CLASSIFIED
    assert d["disposition"] == DISP.MUST_ROLLBACK
    assert d["commit_review_eligible"] is False and d["rollback_required"] is True


def test_23b_unknown_failure_signal_holds():
    d = DISP.classify_post_execution_disposition(failure_signal="MADE_UP_SIGNAL")
    assert d["status"] == DISP.DISPOSITION_HOLD and "UNKNOWN_FAILURE_SIGNAL" in d["reason"]


def test_23c_both_or_neither_input_holds():
    assert DISP.classify_post_execution_disposition()["status"] == DISP.DISPOSITION_HOLD
    assert DISP.classify_post_execution_disposition(
        post_decision_record_id="x", failure_signal="TEST_INFRA_FAILURE")["status"] == DISP.DISPOSITION_HOLD


def test_23d_missing_post_record_must_rollback():
    d = DISP.classify_post_execution_disposition(post_decision_record_id="kxpost-absent-00000000000000")
    assert d["disposition"] == DISP.MUST_ROLLBACK and d["rollback_required"] is True


def test_23e_invalid_post_record_must_rollback(chain, tmp_path):
    out = _run_post(chain)
    p = chain["post_dc"] / f"{out['decision_record_id']}.json"
    rec = json.loads(p.read_text()); rec["decision_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec))
    d = DISP.classify_post_execution_disposition(
        post_decision_record_id=out["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    assert d["disposition"] == DISP.MUST_ROLLBACK
    assert d["reason"].startswith("KX108_POST_RECORD_INVALID")


def test_23f_unlinked_post_record_holds(chain):
    """Un record POST legacy (non lié à une décision PRE) -> DISPOSITION_HOLD
    (le classificateur D1 exige la liaison PRE)."""
    # forge un record POST legacy minimal, hash correct via jeu POST d'origine
    legacy = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": "kxd-legacy-post-000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": "b", "child_execution_id": "c",
        "execution_authority_hash": "h" * 64, "approval_id": "a",
        "test_contract_hash": "tc", "test_result_id": "tr", "test_result_record_hash": "trh",
        "kx108_input_translation_hash": "k" * 64,
        "decision_id": "d", "trace_id": "t", "domain": "tooling_build",
        "x108_gate": "ALLOW", "reason_code": "GUARD_ALLOW", "severity": "S0",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "contradictions": [], "unknowns": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY", "canonical_envelope": {"x108_gate": "ALLOW"},
    }
    legacy["decision_record_hash"] = DS.compute_kx108_decision_record_hash(legacy)
    p = chain["post_dc"] / f"{legacy['decision_record_id']}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(legacy))
    d = DISP.classify_post_execution_disposition(
        post_decision_record_id=legacy["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    assert d["status"] == DISP.DISPOSITION_HOLD
    assert d["reason"] == "POST_RECORD_NOT_LINKED_TO_PRE_DECISION"


# ─── 3/27 : compatibilité POST legacy ─────────────────────────────────────

def test_27_legacy_post_record_still_verifies():
    legacy = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": "kxd-legacy-000000000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": "b", "child_execution_id": "c",
        "execution_authority_hash": "h" * 64, "approval_id": "a",
        "test_contract_hash": "tc", "test_result_id": "tr", "test_result_record_hash": "trh",
        "kx108_input_translation_hash": "k" * 64,
        "decision_id": "d", "trace_id": "t", "domain": "tooling_build",
        "x108_gate": "ALLOW", "reason_code": "GUARD_ALLOW", "severity": "S0",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "contradictions": [], "unknowns": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY", "canonical_envelope": {"x108_gate": "ALLOW"},
    }
    assert DS.decision_phase_of(legacy) == "POST_EXECUTION"
    legacy["decision_record_hash"] = DS.compute_kx108_decision_record_hash(legacy)
    ok, reason = DS.verify_kx108_decision_record(legacy)
    assert ok, reason
    # decision_phase / kx108_pre_* n'entrent PAS dans le hash POST legacy
    bound = json.dumps({k: legacy.get(k) for k in DS._record_bound_fields_for(legacy)})
    assert "kx108_pre_decision_record_id" not in bound
    assert "decision_phase" not in bound


def test_27b_legacy_post_entrypoint_signature_unchanged():
    import inspect
    sig = inspect.signature(DS.run_and_persist_kx108_decision)
    assert list(sig.parameters) == ["tooling_build_state_kwargs", "binding_context", "store_dir"]


# ─── 24/25 : aucune implémentation de rollback / aucune mutation cible ────

def test_24_25_no_rollback_no_target_mutation_symbols():
    for mod in (DS, DISP):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for banned in ("pre_write_bytes", "atomic_replace_with_bytes(",
                       "apply_validated_source_content(", "run_bounded_apply(", "apply_proposal(",
                       "shutil.copy", "os.remove(", "git commit", "git push", "git merge",
                       "rollback_result", "_save_rollback_evidence("):
            assert banned not in src, f"{mod.__name__}: {banned}"


def test_25b_disposition_never_writes(chain, tmp_path):
    import glob
    before = sorted(glob.glob(str(tmp_path / "**" / "*"), recursive=True))
    out = _run_post(chain)
    DISP.classify_post_execution_disposition(
        post_decision_record_id=out["decision_record_id"], post_decision_store_dir=chain["post_dc"])
    after = sorted(glob.glob(str(tmp_path / "**" / "*"), recursive=True))
    # le seul ajout est le record POST écrit par run_and_persist (pas par le classificateur)
    added = set(after) - set(before)
    assert all("post_dec" in a for a in added), added
