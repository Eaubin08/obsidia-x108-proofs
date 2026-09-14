"""
tests/test_execution_test_contract_v0.py
============================================
Suite PREPARE_ACD01_EXECUTION_TEST_CONTRACT_V0.

Couvre :
  A. Déterminisme de compute_test_contract_hash (SHA256 complet)
  B. Runner borné (argv réel, jamais shell=True, PASS/FAIL/ERROR)
  C. Le runner n'émet jamais ACT
  D. Liaison du contrat de test dans execution_authority_hash
  E. Falsification du contrat après approbation → refus fermé
  F. Suppression d'un check requis après approbation → refus fermé
  G. NOT_READY_TEST_CONTRACT_REQUIRED (production sans contrat)
  H. Construction du contrat ACD-01 proposé (lecture seule, non préparé)
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


def _create_synthetic_approval(envelope: dict, execution_dir: Path, approval_id: str = "test-approval") -> str:
    record = _build_synthetic_approval_record(envelope, approval_id)
    result = E.store_approval_artifact(record, execution_dir)
    assert result["status"] == "STORED"
    return record["approval_id"]


def _two_check_contract(candidate_entry_id: str, batch_id: str, target_path: str) -> dict:
    checks = [
        TC.build_check(
            "positive", TC.CHECK_TYPE_SUBPROCESS,
            argv=[sys.executable, "-c", "pass"], required=True, expected_exit_code=0,
        ),
        TC.build_check(
            "negative-safety", TC.CHECK_TYPE_SUBPROCESS,
            argv=[sys.executable, "-c", "pass"], required=True, expected_exit_code=0,
        ),
    ]
    return TC.build_test_contract("contract-2checks", candidate_entry_id, batch_id, target_path, checks)


def _prepare_git_flow(synthetic_repo, tmp_path, contract_builder=_two_check_contract, target_rel="dst/target.py"):
    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "selector"
    execution_dir = tmp_path / "exec"

    reg = L.register_git_blob_source(
        "candidate", "src/module.py", target_path=target_rel,
        target_domain="TOOLING", reason="test contract synthetic",
        provenance_refs={"operation_type": "UPDATE_TARGET_FROM_SOURCE"},
        repo_root=synthetic_repo, ledger_dir=ledger_dir,
    )
    assert reg["status"] == "DISCOVERED"

    proposal = S.propose_batch(
        objective="synthetic", max_batch_size=1,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[reg["ledger_entry_id"]],
    )
    assert proposal["selected_count"] == 1

    contract = contract_builder(reg["ledger_entry_id"], proposal["batch_id"], target_rel)
    envelope = E.prepare_execution(
        proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
        execution_dir=execution_dir, repo_root=synthetic_repo, test_contract=contract,
    )
    assert envelope["integrity_verified"] is True
    child = envelope["children"][0]
    approval_id = _create_synthetic_approval(envelope, execution_dir)

    return {
        "ledger_dir": ledger_dir, "selector_dir": selector_dir, "execution_dir": execution_dir,
        "envelope": envelope, "child": child, "approval_id": approval_id, "reg": reg,
        "proposal": proposal, "contract": contract,
    }


# ─── A. Déterminisme du hash de contrat ──────────────────────────────────────

class TestContractHashDeterminism:
    def test_identical_contract_same_hash(self):
        c1 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python", "-c", "pass"])
        contract = TC.build_test_contract("id1", "entry1", "batch1", "t.py", [c1])
        assert TC.compute_test_contract_hash(contract) == TC.compute_test_contract_hash(contract)

    def test_full_sha256_not_truncated(self):
        c1 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python", "-c", "pass"])
        contract = TC.build_test_contract("id1", "entry1", "batch1", "t.py", [c1])
        h = TC.compute_test_contract_hash(contract)
        assert len(h) == 64

    def test_different_argv_different_hash(self):
        c1 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python", "-c", "pass"])
        c2 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python", "-c", "print(1)"])
        h1 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c1]))
        h2 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c2]))
        assert h1 != h2

    def test_different_expected_exit_code_different_hash(self):
        c1 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"], expected_exit_code=0)
        c2 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"], expected_exit_code=1)
        h1 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c1]))
        h2 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c2]))
        assert h1 != h2

    def test_different_required_flag_different_hash(self):
        c1 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"], required=True)
        c2 = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"], required=False)
        h1 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c1]))
        h2 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "b", "t.py", [c2]))
        assert h1 != h2

    def test_check_order_matters(self):
        a = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"])
        b = TC.build_check("b", TC.CHECK_TYPE_SUBPROCESS, argv=["python2"])
        h1 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "batch", "t.py", [a, b]))
        h2 = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "batch", "t.py", [b, a]))
        assert h1 != h2

    def test_removing_a_check_changes_hash(self):
        a = TC.build_check("a", TC.CHECK_TYPE_SUBPROCESS, argv=["python"])
        b = TC.build_check("b", TC.CHECK_TYPE_SUBPROCESS, argv=["python2"])
        h_full = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "batch", "t.py", [a, b]))
        h_reduced = TC.compute_test_contract_hash(TC.build_test_contract("id1", "e", "batch", "t.py", [a]))
        assert h_full != h_reduced


# ─── B. Runner borné — argv réel, jamais shell=True ──────────────────────────

class TestBoundedRunner:
    def test_subprocess_check_pass(self, tmp_path):
        check = TC.build_check("ok", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_PASS
        assert result["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS

    def test_subprocess_check_fail_wrong_exit_code(self, tmp_path):
        check = TC.build_check(
            "bad", TC.CHECK_TYPE_SUBPROCESS,
            argv=[sys.executable, "-c", "import sys; sys.exit(1)"], expected_exit_code=0,
        )
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_FAIL
        assert result["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED

    def test_optional_check_failure_does_not_fail_aggregate(self, tmp_path):
        check = TC.build_check(
            "optional-fail", TC.CHECK_TYPE_SUBPROCESS,
            argv=[sys.executable, "-c", "import sys; sys.exit(1)"], expected_exit_code=0, required=False,
        )
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_FAIL
        assert result["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS

    def test_missing_argv_is_error(self, tmp_path):
        check = TC.build_check("noargv", TC.CHECK_TYPE_SUBPROCESS, argv=None)
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_ERROR
        assert result["aggregate_status"] == TC.AGGREGATE_TEST_EXECUTION_ERROR

    def test_target_sha256_check_pass(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_bytes(b"HELLO\n")
        import hashlib
        expected = hashlib.sha256(b"HELLO\n").hexdigest()
        check = TC.build_check(
            "sha", TC.CHECK_TYPE_TARGET_SHA256, target_path="file.txt", expected_target_sha256=expected,
        )
        contract = TC.build_test_contract("c", "e", "b", "file.txt", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_PASS

    def test_target_sha256_check_fail(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_bytes(b"HELLO\n")
        check = TC.build_check(
            "sha", TC.CHECK_TYPE_TARGET_SHA256, target_path="file.txt", expected_target_sha256="0" * 64,
        )
        contract = TC.build_test_contract("c", "e", "b", "file.txt", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["checks"][0]["result"] == TC.RESULT_FAIL

    def test_diff_scope_check(self, synthetic_repo):
        (synthetic_repo / "dst" / "target.py").write_bytes(b"MUTATED\n")
        check = TC.build_check(
            "diffscope", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=["dst/target.py"],
        )
        contract = TC.build_test_contract("c", "e", "b", "dst/target.py", [check])
        result = TC.run_test_contract(contract, synthetic_repo)
        assert result["checks"][0]["result"] == TC.RESULT_PASS

    def test_diff_scope_check_fail_extra_file(self, synthetic_repo):
        (synthetic_repo / "dst" / "target.py").write_bytes(b"MUTATED\n")
        (synthetic_repo / "src" / "module.py").write_bytes(b"ALSO_MUTATED\n")
        check = TC.build_check(
            "diffscope", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=["dst/target.py"],
        )
        contract = TC.build_test_contract("c", "e", "b", "dst/target.py", [check])
        result = TC.run_test_contract(contract, synthetic_repo)
        assert result["checks"][0]["result"] == TC.RESULT_FAIL

    def test_no_shell_true_used(self):
        """Audit statique : aucun appel subprocess n'utilise shell=True (hors docstring)."""
        import ast
        source = (Path(__file__).resolve().parent.parent / "scripts" / "obsidia_test_contract.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "shell":
                        assert not (isinstance(kw.value, ast.Constant) and kw.value.value is True), (
                            "subprocess call uses shell=True"
                        )


# ─── C. Le runner n'émet jamais ACT ───────────────────────────────────────────

class TestRunnerNeverEmitsAct:
    def test_result_never_contains_act_decision(self, tmp_path):
        check = TC.build_check("ok", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert result["kx108_decision"] is None
        assert result["decision_authority"] == "KX108_ONLY"
        assert result["aggregate_status"] in (
            TC.AGGREGATE_ALL_REQUIRED_PASS, TC.AGGREGATE_REQUIRED_TEST_FAILED, TC.AGGREGATE_TEST_EXECUTION_ERROR,
        )


# ─── D. Liaison du contrat dans execution_authority_hash ────────────────────

class TestContractBoundToExecutionAuthority:
    def test_envelope_carries_test_contract_hash(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        assert ctx["envelope"]["test_contract_hash"] == TC.compute_test_contract_hash(ctx["contract"])

    def test_different_contract_different_execution_authority_hash(self, synthetic_repo, tmp_path):
        ctx1 = _prepare_git_flow(synthetic_repo, tmp_path)

        def _other_contract(cid, bid, tp):
            check = TC.build_check("different", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
            return TC.build_test_contract("other", cid, bid, tp, [check])

        tmp_path2 = tmp_path / "second"
        tmp_path2.mkdir()
        ctx2 = _prepare_git_flow(synthetic_repo, tmp_path2, contract_builder=_other_contract)
        assert ctx1["envelope"]["execution_authority_hash"] != ctx2["envelope"]["execution_authority_hash"]


# ─── E. Falsification du contrat après approbation ──────────────────────────

class TestMutatedTestContractAfterApprovalRejected:
    def test_changed_argv_after_approval_rejected(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        ctx["child"]["target_pre_sha256"] = ctx["child"]["target_pre_sha256"]  # no-op, garde la cible valide
        ctx["envelope"]["test_contract"]["checks"][0]["argv"] = [sys.executable, "-c", "import sys; sys.exit(1)"]
        ctx["envelope"]["test_contract_hash"] = TC.compute_test_contract_hash(ctx["envelope"]["test_contract"])
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.APPROVAL_EXECUTION_CONTENT_MISMATCH
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


class TestRemovingRequiredTestAfterApprovalRejected:
    def test_removing_negative_safety_check_after_approval_rejected(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        assert len(ctx["envelope"]["test_contract"]["checks"]) == 2
        del ctx["envelope"]["test_contract"]["checks"][1]  # retire le check de securite negatif
        ctx["envelope"]["test_contract_hash"] = TC.compute_test_contract_hash(ctx["envelope"]["test_contract"])
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.APPROVAL_EXECUTION_CONTENT_MISMATCH
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


# ─── G. NOT_READY_TEST_CONTRACT_REQUIRED ─────────────────────────────────────

class TestNotReadyTestContractRequired:
    def test_apply_without_test_contract_refused(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"
        execution_dir = tmp_path / "exec"

        reg = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="dst/target.py",
            target_domain="TOOLING", reason="no contract",
            provenance_refs={"operation_type": "UPDATE_TARGET_FROM_SOURCE"},
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        proposal = S.propose_batch(
            objective="no-contract", max_batch_size=1,
            ledger_dir=ledger_dir, selector_dir=selector_dir,
            candidate_entry_ids=[reg["ledger_entry_id"]],
        )
        envelope = E.prepare_execution(
            proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, repo_root=synthetic_repo,
        )  # pas de test_contract
        assert envelope["test_contract_hash"] is None
        approval_id = _create_synthetic_approval(envelope, execution_dir)

        result = C.apply_validated_source_content(
            envelope["batch_execution_id"], envelope["children"][0]["child_execution_id"],
            approval_id, execution_dir=execution_dir, selector_dir=selector_dir,
            ledger_dir=ledger_dir, repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.NOT_READY_TEST_CONTRACT_REQUIRED
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"
