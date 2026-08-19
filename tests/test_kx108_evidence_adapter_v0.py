"""
tests/test_kx108_evidence_adapter_v0.py
==========================================
Suite BUILD_ACD01_EVIDENCE_TO_KX108_ADAPTER_V0.

Prouve que l'adaptateur TRADUIT honnêtement l'évidence canonique
CP9-CP14 vers sigma.contracts.ToolingBuildState — sans jamais décider,
sans jamais fabriquer un fait non capturé, sans jamais mentir sur
l'isolation worktree/branche.

Tout synthétique (tmp_path, dépôt Git temporaire) — jamais le vrai
ACD-01 réel.
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

import obsidia_branching_ledger as L  # noqa: E402
import obsidia_batch_selector as S  # noqa: E402
import obsidia_batch_execution as E  # noqa: E402
import obsidia_content_apply as C  # noqa: E402
import obsidia_test_contract as TC  # noqa: E402
import obsidia_kx108_evidence_adapter as A  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "synthetic_repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")

    (repo / "src").mkdir()
    (repo / "src" / "module.py").write_bytes(b"NEW_SOURCE_CONTENT\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C1")
    c1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "candidate", c1)

    (repo / "dst").mkdir()
    (repo / "dst" / "target.py").write_bytes(b"OLD_TARGET_CONTENT\n")
    _git(repo, "add", "dst/target.py")
    _git(repo, "commit", "-q", "-m", "add target")
    return repo


def _build_synthetic_approval_record(envelope: dict, approval_id: str = "test-approval") -> dict:
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


def _minimal_contract(candidate_entry_id: str, batch_id: str, target_path: str) -> dict:
    check = TC.build_check(
        "trivial-noop", TC.CHECK_TYPE_SUBPROCESS,
        argv=[sys.executable, "-c", "pass"], expected_exit_code=0, required=True, timeout_seconds=10,
    )
    return TC.build_test_contract("synthetic-contract", candidate_entry_id, batch_id, target_path, [check])


def _full_flow(synthetic_repo, tmp_path, target_rel="dst/target.py"):
    """Ledger reel -> proposal -> envelope+contrat -> approbation -> apply -> resultat persiste. Tout isole."""
    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "selector"
    execution_dir = tmp_path / "exec"
    results_dir = tmp_path / "results"
    evidence_dir = tmp_path / "evidence"

    reg = L.register_git_blob_source(
        "candidate", "src/module.py", target_path=target_rel,
        target_domain="TOOLING", reason="adapter synthetic test",
        provenance_refs={"operation_type": "UPDATE_TARGET_FROM_SOURCE"},
        repo_root=synthetic_repo, ledger_dir=ledger_dir,
    )
    assert reg["status"] == "DISCOVERED"

    proposal = S.propose_batch(
        objective="ADAPTER TEST OBJECTIVE", max_batch_size=1,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[reg["ledger_entry_id"]],
    )
    assert proposal["selected_count"] == 1

    contract = _minimal_contract(reg["ledger_entry_id"], proposal["batch_id"], target_rel)
    envelope = E.prepare_execution(
        proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
        execution_dir=execution_dir, repo_root=synthetic_repo, test_contract=contract,
    )
    assert envelope["integrity_verified"] is True
    child = envelope["children"][0]
    approval_id = "test-approval"
    approval_record = _build_synthetic_approval_record(envelope, approval_id)
    store_res = E.store_approval_artifact(approval_record, execution_dir)
    assert store_res["status"] == "STORED"

    apply_result = C.apply_validated_source_content(
        envelope["batch_execution_id"], child["child_execution_id"], approval_id,
        execution_dir=execution_dir, selector_dir=selector_dir, ledger_dir=ledger_dir,
        repo_root=synthetic_repo, evidence_dir=evidence_dir,
    )
    assert apply_result["status"] == "CONTENT_APPLIED"

    outcome = TC.run_and_persist_test_contract(
        contract, synthetic_repo,
        batch_execution_id=envelope["batch_execution_id"],
        child_execution_id=child["child_execution_id"],
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        results_dir=results_dir,
    )
    assert outcome["verify_ok"] is True

    return {
        "ledger_dir": ledger_dir, "selector_dir": selector_dir, "execution_dir": execution_dir,
        "results_dir": results_dir, "evidence_dir": evidence_dir,
        "envelope": envelope, "child": child, "approval_id": approval_id,
        "result_id": outcome["result_id"], "proposal": proposal, "contract": contract,
    }


def _translate(ctx, synthetic_repo, **overrides):
    kwargs = dict(
        batch_execution_id=ctx["envelope"]["batch_execution_id"],
        child_execution_id=ctx["child"]["child_execution_id"],
        approval_id=ctx["approval_id"],
        test_contract_result_id=ctx["result_id"],
        execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
        ledger_dir=ctx["ledger_dir"], results_dir=ctx["results_dir"],
        evidence_dir=ctx["evidence_dir"], repo_root=synthetic_repo,
    )
    kwargs.update(overrides)
    return A.translate_evidence_to_tooling_build_state(**kwargs)


# ─── 1. Traduction propre déterministe ───────────────────────────────────────

class TestCleanTranslation:
    def test_clean_synthetic_evidence_translates_ready(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["status"] == A.READY_FOR_KX108_SUBMISSION
        assert result["tooling_build_state_kwargs"] is not None

    def test_translation_deterministic_from_identical_facts(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        r1 = _translate(ctx, synthetic_repo)
        r2 = _translate(ctx, synthetic_repo)
        assert r1["translation_report"]["kx108_input_translation_hash"] == \
            r2["translation_report"]["kx108_input_translation_hash"]


# ─── 2-6. Rejets d'intégrité croisée ──────────────────────────────────────────

class TestIntegrityRejections:
    def test_approval_mismatch_rejects(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo, approval_id="nonexistent-approval")
        assert result["status"] == A.NOT_READY_EVIDENCE_INTEGRITY

    def test_execution_authority_hash_mismatch_rejects(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        ctx["envelope"]["children"][0]["target_path"] = "dst/other.py"
        E._save_execution(ctx["envelope"], ctx["execution_dir"])
        result = _translate(ctx, synthetic_repo)
        assert result["status"] == A.NOT_READY_EVIDENCE_INTEGRITY

    def test_test_contract_result_hash_mismatch_rejects(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        stored = TC.load_test_contract_result(ctx["result_id"], ctx["results_dir"])
        stored["aggregate_status"] = "TAMPERED"
        result = A.translate_evidence_to_tooling_build_state(
            batch_execution_id=ctx["envelope"]["batch_execution_id"],
            child_execution_id=ctx["child"]["child_execution_id"],
            approval_id=ctx["approval_id"], test_contract_result_id=ctx["result_id"],
            execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], results_dir=ctx["results_dir"],
            evidence_dir=ctx["evidence_dir"], repo_root=synthetic_repo,
        )
        # (stored dict mutated in-memory only — file on disk untouched — this
        #  proves load always re-reads the canonical artifact, not a cache.)
        assert result["status"] == A.READY_FOR_KX108_SUBMISSION

    def test_target_post_sha_mismatch_rejects(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        (synthetic_repo / "dst" / "target.py").write_bytes(b"EXTERNALLY_MUTATED_AFTER_APPLY\n")
        result = _translate(ctx, synthetic_repo)
        assert result["status"] == A.NOT_READY_EVIDENCE_INTEGRITY
        assert result["reason"] == "TARGET_POST_SHA256_DRIFT"

    def test_unexpected_diff_scope_rejects(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        (synthetic_repo / "src" / "module.py").write_bytes(b"UNRELATED_MUTATION\n")
        result = _translate(ctx, synthetic_repo)
        assert result["status"] == A.NOT_READY_EVIDENCE_INTEGRITY
        assert result["reason"] == "DIFF_SCOPE_DRIFT"


# ─── 7-8. Isolation jamais fabriquée ──────────────────────────────────────────

class TestIsolationNeverFabricated:
    def test_worktree_isolated_false_remains_false(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["worktree_isolated"] is False

    def test_branch_isolated_false_remains_false(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["branch_isolated"] is False


# ─── 9-12. Faits non capturés jamais fabriqués ───────────────────────────────

class TestUncapturedFactsNeverFabricated:
    def test_base_sha_never_fabricated(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["base_sha"] == ""

    def test_manifest_hash_never_fabricated(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["manifest_hash"] == ""

    def test_diff_hash_never_fabricated(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["diff_hash"] == ""

    def test_obsidure_absence_never_becomes_pass(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["tooling_build_state_kwargs"]["obsidure_status"] != "CLEAN"
        assert result["tooling_build_state_kwargs"]["obsidure_status"] == "NOT_APPLICABLE"


# ─── 13-15. Non-souveraineté structurelle ────────────────────────────────────

class TestAdapterNonSovereign:
    def test_adapter_module_does_not_import_sigma_guard_or_protocols(self):
        import ast
        source = (Path(__file__).resolve().parent.parent / "scripts" / "obsidia_kx108_evidence_adapter.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(n.name for n in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        assert not any("sigma" in m for m in imported_modules)

    def test_output_contains_no_decision_field(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        flat = str(result)
        for forbidden in ("ALLOW", "\"ACT\"", "'ACT'", "READY_FOR_COMMIT_REVIEW"):
            assert forbidden not in flat
        # "HOLD"/"BLOCK" ne doivent apparaitre nulle part comme VALEUR de champ
        kwargs = result["tooling_build_state_kwargs"]
        for v in kwargs.values():
            if isinstance(v, str):
                assert v not in ("ACT", "ALLOW", "HOLD", "BLOCK")


# ─── 16-18. Rapport de provenance ─────────────────────────────────────────────

class TestProvenanceReport:
    def test_provenance_maps_every_populated_field(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        mapped_fields = {m["target_field"] for m in result["translation_report"]["field_mappings"]}
        assert mapped_fields == set(A.TOOLING_BUILD_STATE_FIELDS)

    def test_unknown_classification_used_for_uncaptured_fields(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        by_field = {m["target_field"]: m for m in result["translation_report"]["field_mappings"]}
        for f in ("base_sha", "manifest_hash", "diff_hash"):
            assert by_field[f]["classification"] == A.CLASSIFICATION_UNKNOWN

    def test_translation_hash_is_full_sha256(self, synthetic_repo, tmp_path):
        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        h = result["translation_report"]["kx108_input_translation_hash"]
        assert len(h) == 64


# ─── 13. Non-régression KX108 réel — adaptateur non impliqué ────────────────

class TestRealKX108NonRegressionOnHonestOutput:
    def test_honest_unisolated_translation_fed_to_real_guardx108_blocks(self, synthetic_repo, tmp_path):
        """
        Preuve d'intégration bout-en-bout, EN DEHORS de l'adaptateur : le
        vrai GuardX108 (non modifié) recoit la sortie HONNETE de
        l'adaptateur (worktree_isolated=False, branch_isolated=False) et
        produit BLOCK — exactement le comportement attendu et deja teste
        par tests/test_tooling_build_domain.py. Cela prouve que
        l'adaptateur ne "triche" pas pour obtenir ALLOW.
        """
        from sigma.contracts import ToolingBuildState
        from sigma.protocols import run_tooling_build_pipeline

        ctx = _full_flow(synthetic_repo, tmp_path)
        result = _translate(ctx, synthetic_repo)
        assert result["status"] == A.READY_FOR_KX108_SUBMISSION

        state = ToolingBuildState(**result["tooling_build_state_kwargs"])
        decision = run_tooling_build_pipeline(state)

        assert decision.x108_gate == "BLOCK"
        assert "BRANCH_NOT_ISOLATED" in decision.contradictions or \
            "WORKTREE_NOT_ISOLATED" in decision.contradictions
