"""
tests/cli/test_governed_execution_driver_v0.py
=============================================
GENERIC_GOVERNED_EXECUTION_INTERFACE_V0

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE (kernel sigma NON mocké
pour PRE et POST), que obsidia_governed_execution_driver_v0 :

  * PREPARE s'arrête AVANT toute autorité (aucune HumanApproval, aucun
    KX108, aucune mutation de cible) ;
  * EXECUTE exige un execution_authority_hash autorisé par l'humain qui
    correspond EXACTEMENT à l'enveloppe persistée rechargée + recalculée ;
  * ne fait confiance à AUCUNE valeur de l'appelant comme autorité
    (rechargement + revérification entre phases) ;
  * la seule voie de remédiation est run_governed_content_apply ;
  * KEEP réel (POST ALLOW) et rollback D2 réel (POST HOLD/BLOCK sur un
    contrat de test structurellement valide qui échoue légitimement) ;
  * ne fait AUCUNE écriture de cible directe, AUCUN rollback maison,
    AUCUN forçage KX108, AUCUNE disposition Git ;
  * n'a AUCUN couplage au pilote de conformité (aucun littéral pilote).

Tous les dépôts / worktrees / magasins sont temporaires et isolés.
AUCUNE mutation canonique. AUCUN artefact Event-2 canonique.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                 # noqa: E402
import obsidia_governed_execution_driver_v0 as DRV # noqa: E402
import obsidia_sealed_evidence_v0 as SEV           # noqa: E402
import obsidia_content_apply as C                  # noqa: E402

_TARGET_REL = "periphery/xdomain/drv_target_v0.txt"
_SOURCE_REL = "periphery/xdomain/drv_source_v0.txt"
_A = b"GOVERNED_EXECUTION_DRIVER_FIXTURE\nstate: BEFORE\n"
_B = b"GOVERNED_EXECUTION_DRIVER_FIXTURE\nstate: AFTER_GOVERNED_APPLY\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET_REL).write_bytes(_A)
    (main / _SOURCE_REL).write_bytes(_B)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET_REL, _SOURCE_REL)
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "drvbr", base_sha)
    stores = {k: tmp_path / k for k in (
        "ledger", "selector", "exec", "pec", "kxpre", "kxpost", "tcr",
        "sar", "sre", "rbk")}
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha, "stores": stores,
            "target_abs": exec_wt / _TARGET_REL}


def _positive_contract() -> dict:
    checks = [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET_REL,
                       expected_target_sha256=_sha(_B), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET_REL], required=True),
        TC.build_check("marker", TC.CHECK_TYPE_SUBPROCESS,
                       argv=[sys.executable, "-c",
                             "import pathlib,sys;"
                             "c=pathlib.Path('" + _TARGET_REL + "').read_text();"
                             "sys.exit(0 if 'AFTER_GOVERNED_APPLY' in c and 'state: BEFORE' not in c else 1)"],
                       expected_exit_code=0, required=True),
    ]
    return TC.build_test_contract("drv-positive-v0", "cand", "batch", _TARGET_REL, checks)


def _negative_contract() -> dict:
    # Contrat structurellement VALIDE dont l'assertion (« aucun changement
    # attendu ») est légitimement violée par la mutation gouvernée A->B.
    checks = [
        TC.build_check("no-change-expected", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[], required=True),
    ]
    return TC.build_test_contract("drv-negative-v0", "cand", "batch", _TARGET_REL, checks)


def _prepare(world, contract, **over):
    kw = dict(
        source_git_commit=world["base_sha"],
        source_historical_path=_SOURCE_REL,
        target_path=_TARGET_REL,
        test_contract=contract,
        execution_worktree_path=world["exec_wt"],
        main_worktree_path=world["main"],
        branch_name="drvbr",
        base_sha=world["base_sha"],
        objective="driver conformance",
        ledger_dir=world["stores"]["ledger"],
        selector_dir=world["stores"]["selector"],
        execution_dir=world["stores"]["exec"],
        pre_execution_context_dir=world["stores"]["pec"],
    )
    kw.update(over)
    return DRV.prepare_governed_execution(**kw)


def _execute(world, prep, eah=None, ref="human-turn-ref-0001"):
    s = world["stores"]
    return DRV.execute_governed_remediation(
        prep["batch_execution_id"], prep["child_execution_id"],
        eah if eah is not None else prep["execution_authority_hash"], ref,
        execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
        selector_dir=s["selector"], ledger_dir=s["ledger"],
        kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
        repo_root=world["exec_wt"],
    )


# ── 1. PREPARE stops before authority ────────────────────────────────────

def test_01_prepare_only_no_authority_no_mutation(world):
    p = _prepare(world, _positive_contract())
    assert p["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL, p
    assert len(p["execution_authority_hash"]) == 64
    assert p["test_contract_hash"] == TC.compute_test_contract_hash(p["test_contract"])
    assert p["human_approval_created"] is False
    assert p["kx108_invocations"] == 0
    assert world["target_abs"].read_bytes() == _A                       # target still A
    assert not list(world["stores"]["kxpre"].rglob("*.json"))           # no PRE decision
    assert not list(world["stores"]["sar"].rglob("*.json"))             # no sealed receipt
    assert not list(world["stores"]["sre"].rglob("*.json"))
    # no approval artifact persisted
    assert not list((world["stores"]["exec"]).rglob("approval.json"))


def test_02_prepare_isolation_not_verified_rejects(world):
    p = _prepare(world, _positive_contract(), branch_name="wrong-branch")
    assert p["status"] == DRV.PREPARE_REJECTED
    assert "PRE_EXECUTION_CONTEXT_NOT_VERIFIED" in p["reason"]
    assert world["target_abs"].read_bytes() == _A


# ── 2. EXECUTE authority gates ───────────────────────────────────────────

def test_03_execute_requires_matching_human_authorized_eah(world):
    p = _prepare(world, _positive_contract())
    r = _execute(world, p, eah="0" * 64)
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"].startswith("HUMAN_AUTHORIZED_EAH_MISMATCH")
    assert world["target_abs"].read_bytes() == _A
    assert not list(world["stores"]["kxpre"].rglob("*.json"))           # no KX108_PRE


def test_04_execute_rejects_missing_authorization_reference(world):
    p = _prepare(world, _positive_contract())
    r = _execute(world, p, ref="   ")
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] == "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"
    assert world["target_abs"].read_bytes() == _A


def test_05_execute_fails_closed_on_envelope_drift_between_phases(world):
    p = _prepare(world, _positive_contract())
    # falsifie le champ EAH stocké de l'enveloppe persistée -> recomputed != stored
    ep = world["stores"]["exec"] / "executions" / p["batch_execution_id"] / "execution.json"
    env = json.loads(ep.read_text())
    env["execution_authority_hash"] = "9" * 64
    ep.write_text(json.dumps(env))
    r = _execute(world, p, eah=p["execution_authority_hash"])
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] in ("ENVELOPE_EAH_DRIFT", "HUMAN_AUTHORIZED_EAH_MISMATCH")
    assert world["target_abs"].read_bytes() == _A
    assert not list(world["stores"]["kxpre"].rglob("*.json"))


# ── 3. Positive real-stack KEEP ─────────────────────────────────────────

def test_06_positive_real_stack_keep(world):
    p = _prepare(world, _positive_contract())
    r = _execute(world, p)
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["kx108_post_gate"] == "ALLOW"
    assert r["kx108_pre_gate"] == "ALLOW"
    assert world["target_abs"].read_bytes() == _B
    assert _sha(world["target_abs"].read_bytes()) == _sha(_B)
    # sealed evidence exists + verifies
    sre = SEV.load_sealed_rollback_evidence(r["sealed_rollback_evidence_id"], world["stores"]["sre"])
    sar = SEV.load_sealed_apply_receipt(r["sealed_apply_receipt_id"], world["stores"]["sar"])
    assert SEV.verify_sealed_rollback_evidence(sre)[0]
    assert SEV.verify_sealed_apply_receipt(sar)[0]
    # no git disposition: HEAD unchanged in exec worktree, only working diff = [target]
    assert _git(world["exec_wt"], "rev-parse", "HEAD") == world["base_sha"]
    assert _git(world["exec_wt"], "diff", "--name-only") == _TARGET_REL
    assert r["driver_git_disposition"] is False


# ── 4. Negative real-stack rollback (no bypass) ─────────────────────────

def test_07_negative_real_stack_rollback_to_A(world):
    p = _prepare(world, _negative_contract())
    r = _execute(world, p)
    assert r["status"] == DRV.REJECTED_ROLLED_BACK, r
    assert r["kx108_post_gate"] in ("HOLD", "BLOCK")
    assert world["target_abs"].read_bytes() == _A
    assert _git(world["exec_wt"], "diff", "--name-only") == ""
    assert r["rollback_status"] in ("ROLLBACK_SUCCEEDED", "ALREADY_ROLLED_BACK",
                                    "ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED")
    assert r["kx108_invocations_during_rollback"] == 0
    assert r["driver_authored_rollback"] is False


# ── 5. Post-pipeline failure routes through C2/D2 (driver has no recovery) ─

def test_08_receipt_seal_failure_routes_to_d2(world, monkeypatch):
    p = _prepare(world, _positive_contract())
    monkeypatch.setattr(SEV, "store_sealed_apply_receipt",
                        lambda rec, store_dir=None: {"status": SEV.STATUS_TEMP_WRITE_FAILED,
                                                     "sealed_apply_receipt_id": rec.get("sealed_apply_receipt_id")})
    r = _execute(world, p)
    assert r["status"] == DRV.REJECTED_ROLLED_BACK, r
    assert world["target_abs"].read_bytes() == _A


# ── 6. Third-party C preserved, never blind-overwritten ─────────────────

def test_09_third_party_C_preserved_quarantine(world, monkeypatch):
    p = _prepare(world, _positive_contract())
    third = b"THIRD PARTY CONTENT\n"

    def wrote_c(target_abs, content, expected_pre):
        Path(target_abs).write_bytes(third)
        return {"status": C.ATOMIC_REPLACE_FAILED}
    monkeypatch.setattr(C, "atomic_replace_with_bytes", wrote_c)
    r = _execute(world, p)
    assert r["status"] == DRV.APPLY_STATE_UNKNOWN_QUARANTINE, r
    assert world["target_abs"].read_bytes() == third


# ── 7. Static: no self-approval, no write bypass, no pilot coupling ─────

def test_10_no_automatic_prepare_to_approval_path():
    prep_src = inspect.getsource(DRV.prepare_governed_execution)
    for banned in ("store_approval_artifact", "run_and_persist_kx108",
                   "run_governed_content_apply", "translate_pre_execution_evidence"):
        assert banned not in prep_src, f"prepare must not reach {banned}"
    sig = inspect.signature(DRV.execute_governed_remediation)
    assert "human_authorized_execution_authority_hash" in sig.parameters
    assert "human_authorization_reference" in sig.parameters
    # Stage 4F : les deux paramètres deviennent Optional pour le dispatch de mode,
    # mais restent EXIGÉS au runtime en mode historique PER_ACTION_HUMAN_EAH
    # (défaut). Un appel sans EAH humain en mode historique -> rejet fermé.
    assert DRV.DEFAULT_AUTHORITY_MODE == "PER_ACTION_HUMAN_EAH"
    r = DRV.execute_governed_remediation(
        "be-x", "ch-x", None, None,
        execution_dir="/nonexistent", pre_execution_context_dir="/nonexistent",
        selector_dir="/nonexistent", ledger_dir="/nonexistent",
        kx108_pre_decision_dir="/nonexistent", kx108_post_decision_dir="/nonexistent",
        test_contract_results_dir="/nonexistent", sealed_receipt_dir="/nonexistent",
        sealed_rollback_evidence_dir="/nonexistent", rollback_result_dir="/nonexistent",
        repo_root=".")
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] == "HUMAN_AUTHORIZED_EAH_MISSING_OR_MALFORMED"


def test_11_no_target_write_no_rollback_no_kx108_force_no_git_disposition():
    src = Path(DRV.__file__).read_text(encoding="utf-8")
    for banned in ("open(", ".write_bytes(", ".write_text(", "shutil.copy", "os.replace(",
                   "atomic_replace_with_bytes(", "_atomic_restore(",
                   "run_tooling_build_pipeline", "ToolingBuildState(",
                   "git commit", "git add", "git push", "git merge", "git rebase",
                   "git cherry-pick", "git stash", "git reset", "git checkout"):
        assert banned not in src, banned
    assert src.count("run_governed_content_apply(") == 1
    # exactly one recovery entrypoint reference and it is NOT invoked here
    assert "run_governed_rollback" not in src


def test_12_no_pilot_literals_and_generic_reusable():
    src = Path(DRV.__file__).read_text(encoding="utf-8")
    for lit in ("pilot_target_v0", "pilot_source_v0", "governed_c2_conformance_pilot",
                "CANONICAL_C2_CONFORMANCE_PILOT", "d25dbd5", "7f40160",
                "BLK-W5", "8526a8f5", "53fa38dd"):
        assert lit not in src, lit
    # generic parameters only
    ps = inspect.signature(DRV.prepare_governed_execution).parameters
    for expected in ("source_git_commit", "source_historical_path", "target_path",
                     "test_contract", "ledger_dir", "selector_dir", "execution_dir",
                     "pre_execution_context_dir"):
        assert expected in ps


def test_13_all_store_roots_explicit_no_default_canonical_dependency():
    src = Path(DRV.__file__).read_text(encoding="utf-8")
    assert "LOCALAPPDATA" not in src
    for fn in (DRV.prepare_governed_execution, DRV.execute_governed_remediation):
        ps = inspect.signature(fn).parameters
        assert any("dir" in n for n in ps), fn.__name__
