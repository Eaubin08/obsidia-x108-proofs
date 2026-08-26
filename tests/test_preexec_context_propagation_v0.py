"""
tests/test_preexec_context_propagation_v0.py
===============================================
Suite CLOSE_PREEXEC_CONTEXT_PROPAGATION_GAP_V0.

Prouve trois choses que la revue humaine precedente avait trouvees
absentes :

1. prepare_execution(...) REEL (pas une injection manuelle de dict)
   peut propager pre_execution_context_id/record_hash dans une VRAIE
   ExecutionEnvelope, uniquement apres avoir charge + verifie le
   PreExecutionContext canonique reference.
2. manifest_sha256 se recalcule desormais UNIQUEMENT depuis les octets
   persistes (record["manifest"], schema V2) — plus de connaissance
   hors-bande requise.
3. Le mecanisme GENERIQUE existant (build_test_contract /
   compute_test_contract_hash) produit deja un hash different et
   deterministe pour une nouvelle identite candidate_entry_id/batch_id,
   a semantique de checks strictement identique — sans code nouveau.

Tout synthetique (tmp_path, depots Git temporaires reels) — jamais le
vrai ACD-01/ACD-02 reel.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_pre_execution_context as PEC  # noqa: E402
import obsidia_batch_execution as E  # noqa: E402
import obsidia_branching_ledger as L  # noqa: E402
import obsidia_batch_selector as S  # noqa: E402
import obsidia_test_contract as TC  # noqa: E402
import obsidia_kx108_evidence_adapter as A  # noqa: E402
import obsidia_content_apply as C  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


@pytest.fixture
def isolated_pair(tmp_path: Path):
    main_repo = tmp_path / "main_repo"
    main_repo.mkdir()
    _git(main_repo, "init", "-q")
    _git(main_repo, "config", "user.email", "test@example.com")
    _git(main_repo, "config", "user.name", "Test")
    (main_repo / "src").mkdir()
    (main_repo / "src" / "module.py").write_bytes(b"NEW_SOURCE_CONTENT\n")
    _git(main_repo, "add", "src/module.py")
    _git(main_repo, "commit", "-q", "-m", "source commit")
    source_commit = _git(main_repo, "rev-parse", "HEAD")
    source_blob = _git(main_repo, "rev-parse", "HEAD:src/module.py")
    _git(main_repo, "branch", "candidate", source_commit)

    (main_repo / "dst").mkdir()
    (main_repo / "dst" / "target.py").write_bytes(b"OLD_TARGET_CONTENT\n")
    _git(main_repo, "add", "dst/target.py")
    _git(main_repo, "commit", "-q", "-m", "add target")
    base_sha = _git(main_repo, "rev-parse", "HEAD")
    _git(main_repo, "checkout", "-q", "-b", "main-dev")

    worktree_path = tmp_path / "isolated_worktree"
    _git(main_repo, "worktree", "add", "-b", "pilot/isolated-v0", str(worktree_path), base_sha)

    target_pre_sha256 = __import__("hashlib").sha256(b"OLD_TARGET_CONTENT\n").hexdigest()
    source_sha256 = __import__("hashlib").sha256(b"NEW_SOURCE_CONTENT\n").hexdigest()

    return {
        "main_repo": main_repo, "worktree_path": worktree_path, "base_sha": base_sha,
        "branch_name": "pilot/isolated-v0", "target_path": "dst/target.py",
        "target_pre_sha256": target_pre_sha256,
        "source_commit": source_commit, "source_blob": source_blob, "source_sha256": source_sha256,
    }


def _make_context(p, tmp_path, **overrides):
    kwargs = dict(
        execution_worktree_path=p["worktree_path"], branch_name=p["branch_name"],
        base_sha=p["base_sha"], main_worktree_path=p["main_repo"],
        repository_identity="synthetic-repo", target_path=p["target_path"],
        target_pre_sha256=p["target_pre_sha256"], source_kind="GIT_BLOB",
        source_repository_identity="synthetic-repo", source_commit=p["source_commit"],
        source_blob_sha=p["source_blob"], source_path=p["target_path"],
        source_sha256=p["source_sha256"], operation="UPDATE_TARGET_FROM_SOURCE",
        approved_scope=[p["target_path"]], protected_scope_status="CLEAN",
        legacy_manifest_hash_short="short1234567890a",
        store_dir=tmp_path / "pec_store",
    )
    kwargs.update(overrides)
    return PEC.create_pre_execution_context(**kwargs)


# ─── 1. Manifeste auto-porteur (self-contained) ──────────────────────────────

class TestManifestSelfContained:
    def test_manifest_recomputes_solely_from_persisted_record(self, isolated_pair, tmp_path):
        outcome = _make_context(isolated_pair, tmp_path)
        rec = outcome["record"]
        assert rec["context_schema_version"] == 2
        recomputed = PEC.compute_manifest_sha256(rec["manifest"])
        assert recomputed == rec["manifest_sha256"]
        assert len(rec["manifest_sha256"]) == 64

    def test_verify_recomputes_manifest_and_detects_tamper(self, isolated_pair, tmp_path):
        outcome = _make_context(isolated_pair, tmp_path)
        rec = dict(outcome["record"])
        rec["manifest"] = dict(rec["manifest"], branch_name="tampered-branch")
        # manifest_sha256 et context_record_hash restent les ANCIENNES valeurs
        # (attaque : seul le sous-dict manifest a ete modifie en memoire).
        ok, reason = PEC.verify_pre_execution_context_record(rec)
        assert ok is False
        # Soit le hash de contexte global detecte la mutation (manifest fait
        # partie de _CONTEXT_BOUND_FIELDS_V2), soit a defaut le recalcul de
        # manifest_sha256 la detecte independamment.
        assert reason in (
            "CONTEXT_RECORD_HASH_MISMATCH",
            "MANIFEST_SHA256_NOT_SELF_CONTAINED_RECOMPUTATION_MISMATCH",
        )

    def test_legacy_manifest_hash_short_never_authoritative(self, isolated_pair, tmp_path):
        outcome = _make_context(isolated_pair, tmp_path)
        rec = outcome["record"]
        assert rec["legacy_manifest_hash_short"] == "short1234567890a"
        assert rec["manifest_sha256"] != rec["legacy_manifest_hash_short"]
        assert len(rec["manifest_sha256"]) == 64
        assert len(rec["legacy_manifest_hash_short"]) != 64

    def test_v1_schema_record_remains_readable(self, isolated_pair, tmp_path):
        """Un enregistrement V1 historique (sans 'manifest' imbrique) reste
        chargeable/verifiable sous ses propres regles — jamais reinterprete
        silencieusement sous le schema V2."""
        v1_fields = {k: "x" for k in PEC._CONTEXT_BOUND_FIELDS_V1}
        v1_fields["context_schema_version"] = 1
        v1_fields["decision_authority"] = PEC.DECISION_AUTHORITY
        v1_fields["context_id"] = "pec-legacyv1000000000000000000000000"
        v1_fields["context_record_hash"] = PEC.compute_context_record_hash(v1_fields)
        store_dir = tmp_path / "v1_store"
        result = PEC.store_pre_execution_context_record(v1_fields, store_dir)
        assert result["status"] == PEC.STATUS_STORED
        reloaded = PEC.load_pre_execution_context_record(v1_fields["context_id"], store_dir)
        ok, reason = PEC.verify_pre_execution_context_record(reloaded)
        assert ok is True, reason

    def test_mutation_fields_change_manifest_hash(self, isolated_pair, tmp_path):
        outcome = _make_context(isolated_pair, tmp_path)
        base_manifest = outcome["record"]["manifest"]
        base_hash = PEC.compute_manifest_sha256(base_manifest)
        for field, new_value in (
            ("branch_name", "other-branch"),
            ("base_sha", "f" * 40),
            ("target_pre_sha256", "0" * 64),
            ("source_sha256", "1" * 64),
            ("approved_scope", ["other/path.py"]),
        ):
            mutated = dict(base_manifest, **{field: new_value})
            assert PEC.compute_manifest_sha256(mutated) != base_hash


# ─── 2. Propagation reelle via prepare_execution ─────────────────────────────

def _prepare_ledger_and_batch(main_repo, tmp_path, target_rel):
    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "selector"
    reg = L.register_git_blob_source(
        "candidate", "src/module.py", target_path=target_rel,
        target_domain="TOOLING", reason="preexec propagation test",
        provenance_refs={"operation_type": "UPDATE_TARGET_FROM_SOURCE"},
        repo_root=main_repo, ledger_dir=ledger_dir,
    )
    assert reg["status"] == "DISCOVERED"
    proposal = S.propose_batch(
        objective="PROPAGATION TEST", max_batch_size=1,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[reg["ledger_entry_id"]],
    )
    assert proposal["selected_count"] == 1
    return ledger_dir, selector_dir, proposal


class TestRealPrepareExecutionPropagation:
    def test_valid_context_propagated_into_real_envelope(self, isolated_pair, tmp_path):
        p = isolated_pair
        pec_outcome = _make_context(p, tmp_path)
        assert pec_outcome["verify_ok"] is True

        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"

        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
            pre_execution_context={
                "context_id": pec_outcome["context_id"],
                "context_record_hash": pec_outcome["record"]["context_record_hash"],
            },
            pre_execution_context_dir=tmp_path / "pec_store",
        )
        assert envelope["integrity_verified"] is True
        assert envelope["pre_execution_context_id"] == pec_outcome["context_id"]
        assert envelope["pre_execution_context_record_hash"] == pec_outcome["record"]["context_record_hash"]
        # execution_authority_hash lie bien ces champs (recompute independant).
        assert envelope["execution_authority_hash"] == E.compute_execution_authority_hash(envelope)
        without_ctx = dict(envelope)
        del without_ctx["pre_execution_context_id"]
        del without_ctx["pre_execution_context_record_hash"]
        assert E.compute_execution_authority_hash(without_ctx) != envelope["execution_authority_hash"]

    def test_context_absent_legacy_path_unaffected(self, isolated_pair, tmp_path):
        p = isolated_pair
        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
        )
        assert "pre_execution_context_id" not in envelope
        assert "pre_execution_context_record_hash" not in envelope

    def test_invalid_context_id_rejects_before_envelope_authority(self, isolated_pair, tmp_path):
        p = isolated_pair
        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
            pre_execution_context={"context_id": "pec-nonexistent0000000000000000000000000", "context_record_hash": "a" * 64},
            pre_execution_context_dir=tmp_path / "pec_store",
        )
        assert envelope["aggregate_status"] == E.BATCH_HOLD
        assert "PRE_EXECUTION_CONTEXT_INVALID" in envelope["integrity_error"]
        assert "pre_execution_context_id" not in envelope

    def test_tampered_context_record_rejected(self, isolated_pair, tmp_path):
        p = isolated_pair
        pec_outcome = _make_context(p, tmp_path)
        pec_store = tmp_path / "pec_store"
        # Falsifie l'artefact stocke sur disque APRES capture.
        path = pec_store / f"{pec_outcome['context_id']}.json"
        tampered = path.read_text(encoding="utf-8").replace('"CLEAN"', '"VIOLATED"', 1)
        # os.link rend le fichier immuable via l'API normale — on modifie
        # directement le fichier pour simuler une alteration hors-API.
        path.unlink()
        path.write_text(tampered, encoding="utf-8")

        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
            pre_execution_context={
                "context_id": pec_outcome["context_id"],
                "context_record_hash": pec_outcome["record"]["context_record_hash"],
            },
            pre_execution_context_dir=pec_store,
        )
        assert envelope["aggregate_status"] == E.BATCH_HOLD
        assert "PRE_EXECUTION_CONTEXT_INVALID" in envelope["integrity_error"]

    def test_wrong_supplied_record_hash_rejected(self, isolated_pair, tmp_path):
        p = isolated_pair
        pec_outcome = _make_context(p, tmp_path)
        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
            pre_execution_context={"context_id": pec_outcome["context_id"], "context_record_hash": "f" * 64},
            pre_execution_context_dir=tmp_path / "pec_store",
        )
        assert envelope["aggregate_status"] == E.BATCH_HOLD
        assert "PRE_EXECUTION_CONTEXT_REFERENCE_MISMATCH" in envelope["integrity_error"]

    def test_context_store_unavailable_rejected(self, isolated_pair, tmp_path):
        p = isolated_pair
        pec_outcome = _make_context(p, tmp_path)
        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"],
            pre_execution_context={
                "context_id": pec_outcome["context_id"],
                "context_record_hash": pec_outcome["record"]["context_record_hash"],
            },
            pre_execution_context_dir=tmp_path / "nonexistent_store_dir",
        )
        assert envelope["aggregate_status"] == E.BATCH_HOLD
        assert "PRE_EXECUTION_CONTEXT_INVALID" in envelope["integrity_error"]

    def test_caller_cannot_inject_isolation_or_facts_directly(self):
        import inspect
        sig = inspect.signature(E.prepare_execution)
        for forbidden in ("worktree_isolated", "branch_isolated", "base_sha", "manifest_hash"):
            assert forbidden not in sig.parameters
        # Le seul point d'entree est une REFERENCE (context_id + hash),
        # jamais des faits directs.
        assert "pre_execution_context" in sig.parameters


# ─── 3. Bout-en-bout production -> adaptateur ────────────────────────────────

def _minimal_contract(candidate_entry_id: str, batch_id: str, target_path: str) -> dict:
    check = TC.build_check(
        "trivial-noop", TC.CHECK_TYPE_SUBPROCESS,
        argv=[sys.executable, "-c", "pass"], expected_exit_code=0, required=True, timeout_seconds=10,
    )
    return TC.build_test_contract("synthetic-contract", candidate_entry_id, batch_id, target_path, [check])


def _build_synthetic_approval_record(envelope: dict, approval_id: str) -> dict:
    record = {
        "approval_id": approval_id,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": envelope["batch_id"],
        "batch_hash": envelope["batch_hash"],
        "candidate_scope_hash": envelope["candidate_scope_hash"],
        "execution_authority_hash": envelope.get("execution_authority_hash"),
        "approved_by": "HUMAN",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": E.DECISION_AUTHORITY,
    }
    record["approval_record_hash"] = E.compute_approval_record_hash(record)
    return record


class TestEndToEndProductionToAdapter:
    def test_real_prepare_execution_through_adapter_derives_true_isolation(self, isolated_pair, tmp_path):
        p = isolated_pair
        pec_outcome = _make_context(p, tmp_path)
        assert pec_outcome["verify_ok"] is True

        ledger_dir, selector_dir, proposal = _prepare_ledger_and_batch(p["main_repo"], tmp_path, p["target_path"])
        execution_dir = tmp_path / "exec"
        results_dir = tmp_path / "results"
        evidence_dir = tmp_path / "evidence"

        contract = _minimal_contract(proposal["selected_entries"][0]["candidate_id"], proposal["batch_id"], p["target_path"])

        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=p["main_repo"], test_contract=contract,
            pre_execution_context={
                "context_id": pec_outcome["context_id"],
                "context_record_hash": pec_outcome["record"]["context_record_hash"],
            },
            pre_execution_context_dir=tmp_path / "pec_store",
        )
        assert envelope["integrity_verified"] is True
        assert envelope["pre_execution_context_id"] == pec_outcome["context_id"]

        child = envelope["children"][0]
        approval_id = "e2e-approval"
        approval_record = _build_synthetic_approval_record(envelope, approval_id)
        E.store_approval_artifact(approval_record, execution_dir)

        apply_result = C.apply_validated_source_content(
            envelope["batch_execution_id"], child["child_execution_id"], approval_id,
            execution_dir=execution_dir, selector_dir=selector_dir, ledger_dir=ledger_dir,
            repo_root=p["main_repo"], evidence_dir=evidence_dir,
        )
        assert apply_result["status"] == "CONTENT_APPLIED"

        outcome = TC.run_and_persist_test_contract(
            contract, p["main_repo"],
            batch_execution_id=envelope["batch_execution_id"],
            child_execution_id=child["child_execution_id"],
            execution_authority_hash=envelope["execution_authority_hash"],
            approval_id=approval_id,
            results_dir=results_dir,
        )
        assert outcome["verify_ok"] is True

        result = A.translate_evidence_to_tooling_build_state(
            batch_execution_id=envelope["batch_execution_id"],
            child_execution_id=child["child_execution_id"],
            approval_id=approval_id,
            test_contract_result_id=outcome["result_id"],
            execution_dir=execution_dir, selector_dir=selector_dir,
            ledger_dir=ledger_dir, results_dir=results_dir,
            evidence_dir=evidence_dir, repo_root=p["main_repo"],
            pre_execution_context_dir=tmp_path / "pec_store",
        )
        assert result["status"] == A.READY_FOR_KX108_SUBMISSION
        kwargs = result["tooling_build_state_kwargs"]
        assert kwargs["worktree_isolated"] is True
        assert kwargs["branch_isolated"] is True
        assert kwargs["base_sha"] == p["base_sha"]
        assert len(kwargs["manifest_hash"]) == 64
        assert kwargs["manifest_hash"] != "b481a49917a1f4e0"


# ─── 4. Mecanisme generique de contrat de test : nouvelle identite ──────────

class TestGenericTestContractMechanismForNewIdentity:
    def _acd01_shaped_checks(self, target_path: str) -> list:
        return [
            TC.build_check("TARGET_POST_SHA256", TC.CHECK_TYPE_TARGET_SHA256,
                            target_path=target_path, expected_target_sha256="6" * 64,
                            required=True, timeout_seconds=10),
            TC.build_check("REAL_SCANNER_EXIT_ZERO", TC.CHECK_TYPE_SUBPROCESS,
                            argv=[sys.executable, target_path], expected_exit_code=0,
                            required=True, timeout_seconds=60),
            TC.build_check("P59_POSITIVE_REGRESSION", TC.CHECK_TYPE_SUBPROCESS,
                            argv=[sys.executable, "-m", "pytest", "tests/test_p59_safe_batch_1_import.py", "-q"],
                            expected_exit_code=0, required=True, timeout_seconds=60),
            TC.build_check("NEGATIVE_SECURITY_REGRESSION", TC.CHECK_TYPE_SUBPROCESS,
                            argv=[sys.executable, "-m", "pytest", "tests/test_check_forbidden_content_negative_contract_v0.py", "-q"],
                            expected_exit_code=0, required=True, timeout_seconds=60),
            TC.build_check("DIFF_SCOPE_EXACT_ONE_TARGET", TC.CHECK_TYPE_DIFF_SCOPE,
                            expected_diff_paths=[target_path], required=True, timeout_seconds=30),
            TC.build_check("DIFF_CHECK", TC.CHECK_TYPE_SUBPROCESS,
                            argv=["git", "diff", "--check"], expected_exit_code=0,
                            required=True, timeout_seconds=30),
            TC.build_check("FULL_CANONICAL_REGRESSION", TC.CHECK_TYPE_SUBPROCESS,
                            argv=[sys.executable, "-m", "pytest", "-q"], expected_exit_code=0,
                            required=True, timeout_seconds=600),
        ]

    def test_same_semantics_new_identity_produces_new_deterministic_hash(self):
        target_path = "scripts/check_forbidden_content.py"
        checks = self._acd01_shaped_checks(target_path)

        acd01_shaped_contract = TC.build_test_contract(
            "ACD01-EXECUTION-TEST-CONTRACT-V0", "c73920aeada4f234", "1f9b780ffb57f5a6", target_path, checks,
        )
        acd01_shaped_hash = TC.compute_test_contract_hash(acd01_shaped_contract)

        acd02_contract_v1 = TC.build_test_contract(
            "ACD02-EXECUTION-TEST-CONTRACT-V0", "synthetic-candidate-acd02", "synthetic-batch-acd02",
            target_path, checks,
        )
        acd02_hash_v1 = TC.compute_test_contract_hash(acd02_contract_v1)

        acd02_contract_v2 = TC.build_test_contract(
            "ACD02-EXECUTION-TEST-CONTRACT-V0", "synthetic-candidate-acd02", "synthetic-batch-acd02",
            target_path, checks,
        )
        acd02_hash_v2 = TC.compute_test_contract_hash(acd02_contract_v2)

        # Semantique IDENTIQUE (memes checks) mais identite differente ->
        # hash different de l'ACD-01 reel.
        assert acd02_hash_v1 != acd01_shaped_hash
        # Deterministe : meme identite + memes checks -> meme hash.
        assert acd02_hash_v1 == acd02_hash_v2

    def test_new_candidate_or_batch_id_alone_changes_hash(self):
        target_path = "scripts/check_forbidden_content.py"
        checks = self._acd01_shaped_checks(target_path)
        base = TC.build_test_contract("X", "cand-a", "batch-a", target_path, checks)
        diff_candidate = TC.build_test_contract("X", "cand-b", "batch-a", target_path, checks)
        diff_batch = TC.build_test_contract("X", "cand-a", "batch-b", target_path, checks)
        h_base = TC.compute_test_contract_hash(base)
        assert TC.compute_test_contract_hash(diff_candidate) != h_base
        assert TC.compute_test_contract_hash(diff_batch) != h_base


# ─── 5. Non-regression historique ACD-01 ────────────────────────────────────

class TestHistoricalNonRegression:
    def test_real_historical_acd01_execution_authority_hash_still_recomputes(self):
        envelope = {
            "batch_execution_id": "107e815d99d9d336",
            "batch_id": "1f9b780ffb57f5a6",
            "batch_hash": "033ab1f43cc3f167",
            "batch_hash_version": 2,
            "candidate_scope_hash": "402d8dff206c77bb",
            "execution_order": ["c73920aeada4f234"],
            "dependency_edges": [],
            "children": [{
                "candidate_entry_id": "c73920aeada4f234",
                "child_execution_id": "25aebb708ba900c5",
                "source_path": "scripts/check_forbidden_content.py",
                "source_hash": "63aced1180c95d28",
                "source_kind": "GIT_BLOB",
                "source_git_commit_sha": "e07dc6480f5ed3142f98a8e64eea0c674c6c5071",
                "source_git_blob_sha": "3d376d40c2e395b1332348cb7de89787d01fe9e8",
                "source_git_historical_path": "scripts/check_forbidden_content.py",
                "source_repository_identity": "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs_TERMINAL_BOUNDED_V1",
                "source_content_sha256": "63aced1180c95d28f53331126b6ef0666376ebfdd255f943f1fceb6b684c5220",
                "target_path": "scripts/check_forbidden_content.py",
                "target_pre_hash": "ff0df0b4b38cbb09",
                "target_pre_sha256": "ff0df0b4b38cbb09b366d1d1eabe619be2f6286cb6dceee1760414d3ff3d44d0",
                "operation_type": "UPDATE_TARGET_FROM_SOURCE",
                "operation_reason": None,
                "materiality_status": "MEANINGFUL_DELTA",
                "dependencies": [],
                "dependency_status": "NOT_APPLICABLE",
                "execution_position": 0,
                "session_id": None,
                "proposal_id": None,
                "kx108_decision": None,
                "execution_status": "PLANNED",
                "decision_authority": "KX108_ONLY",
                "precondition_integrity_hash": "c2142d74e4e73dec",
            }],
            "test_contract_hash": "b2cd7200d0b9fe19d2c880625e07feb0cdd78bc3e66ef54c32b1f9f711bb911c",
            "decision_authority": "KX108_ONLY",
        }
        assert "pre_execution_context_id" not in envelope
        recomputed = E.compute_execution_authority_hash(envelope)
        assert recomputed == "bfce79776be58c174e705a2e8ab2d62d1595bd5510352432240a2a1e9e89df37"
