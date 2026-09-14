"""
tests/test_test_contract_result_persistence_v0.py
=====================================================
Suite CLOSE_TEST_CONTRACT_RESULT_PERSISTENCE_GAP_V0.

Prouve la persistance immuable, append-only, hors dépôt, de
TestContractResult — évidence POST-AUTORITÉ qui référence une
exécution/approbation/contrat déjà approuvés sans jamais les muter.

Tout est synthétique/temporaire (tmp_path) — jamais le vrai
ExecutionEnvelope/HumanApproval/Ledger réels.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_test_contract as TC  # noqa: E402


def _base_result(**overrides) -> dict:
    record = {
        "result_schema_version": TC.RESULT_SCHEMA_VERSION,
        "result_id": "tcr-deadbeef00000000000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "batch_execution_id": "synthetic-batch-exec",
        "child_execution_id": "synthetic-child",
        "execution_authority_hash": "a" * 64,
        "approval_id": "synthetic-approval",
        "test_contract_hash": "b" * 64,
        "aggregate_status": TC.AGGREGATE_ALL_REQUIRED_PASS,
        "required_check_count": 1,
        "check_count": 1,
        "checks": [{"check_id": "x", "result": TC.RESULT_PASS, "required": True}],
        "decision_authority": TC.DECISION_AUTHORITY,
    }
    record.update(overrides)
    record["result_record_hash"] = TC.compute_test_contract_result_hash(record)
    return record


# ─── 1-3. Persistance PASS / FAIL / ERROR ────────────────────────────────────

class TestPersistenceByOutcome:
    def test_pass_result_stores_and_reloads_identically(self, tmp_path):
        record = _base_result()
        result = TC.store_test_contract_result(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = TC.load_test_contract_result(record["result_id"], tmp_path)
        assert reloaded == record

    def test_fail_result_stores_canonically(self, tmp_path):
        record = _base_result(
            aggregate_status=TC.AGGREGATE_REQUIRED_TEST_FAILED,
            checks=[{"check_id": "x", "result": TC.RESULT_FAIL, "required": True}],
        )
        result = TC.store_test_contract_result(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = TC.load_test_contract_result(record["result_id"], tmp_path)
        assert reloaded["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED

    def test_error_result_stores_canonically(self, tmp_path):
        record = _base_result(
            aggregate_status=TC.AGGREGATE_TEST_EXECUTION_ERROR,
            checks=[{"check_id": "x", "result": TC.RESULT_ERROR, "required": True}],
        )
        result = TC.store_test_contract_result(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = TC.load_test_contract_result(record["result_id"], tmp_path)
        assert reloaded["aggregate_status"] == TC.AGGREGATE_TEST_EXECUTION_ERROR


# ─── 4-9. Déterminisme et sensibilité du hash ────────────────────────────────

class TestResultHashDeterminism:
    def test_full_sha256_deterministic(self):
        r1 = _base_result()
        r2 = _base_result()
        assert TC.compute_test_contract_result_hash(r1) == TC.compute_test_contract_result_hash(r2)
        assert len(r1["result_record_hash"]) == 64

    def test_single_check_mutation_changes_hash(self):
        r1 = _base_result()
        r2 = _base_result(checks=[{"check_id": "x", "result": TC.RESULT_FAIL, "required": True}])
        h1 = TC.compute_test_contract_result_hash({**r1, "result_record_hash": None})
        h2 = TC.compute_test_contract_result_hash({**r2, "result_record_hash": None})
        assert h1 != h2

    def test_child_execution_id_mutation_changes_hash(self):
        base = _base_result()
        mutated = dict(base, child_execution_id="different-child")
        h1 = TC.compute_test_contract_result_hash(base)
        h2 = TC.compute_test_contract_result_hash(mutated)
        assert h1 != h2

    def test_contract_hash_mutation_changes_hash(self):
        base = _base_result()
        mutated = dict(base, test_contract_hash="c" * 64)
        assert TC.compute_test_contract_result_hash(base) != TC.compute_test_contract_result_hash(mutated)

    def test_execution_authority_mutation_changes_hash(self):
        base = _base_result()
        mutated = dict(base, execution_authority_hash="d" * 64)
        assert TC.compute_test_contract_result_hash(base) != TC.compute_test_contract_result_hash(mutated)

    def test_approval_id_mutation_changes_hash(self):
        base = _base_result()
        mutated = dict(base, approval_id="different-approval")
        assert TC.compute_test_contract_result_hash(base) != TC.compute_test_contract_result_hash(mutated)


# ─── 10-11. Falsification / artefact partiel ─────────────────────────────────

class TestArtifactTamperDetection:
    def test_tampered_field_detected_on_verify(self, tmp_path):
        record = _base_result()
        TC.store_test_contract_result(record, tmp_path)
        reloaded = TC.load_test_contract_result(record["result_id"], tmp_path)
        reloaded["aggregate_status"] = TC.AGGREGATE_REQUIRED_TEST_FAILED  # falsifié sans recalcul du hash
        ok, reason = TC.verify_test_contract_result_artifact(reloaded)
        assert ok is False
        assert reason == "RESULT_RECORD_HASH_MISMATCH"

    def test_missing_required_field_fails_verify(self):
        record = _base_result()
        del record["execution_authority_hash"]
        ok, reason = TC.verify_test_contract_result_artifact(record)
        assert ok is False
        assert reason.startswith("RESULT_FIELD_MISSING")

    def test_partial_temp_artifact_never_accepted(self, tmp_path):
        record = _base_result()
        TC.store_test_contract_result(record, tmp_path)
        leftover_tmp_files = list(tmp_path.glob(".*tmp"))
        assert leftover_tmp_files == []  # nettoyé, jamais visible comme résultat final
        # Un ID inexistant ne charge jamais un artefact partiel/fantôme.
        assert TC.load_test_contract_result("tcr-" + "0" * 32, tmp_path) is None


# ─── 12-13. Publication idempotente / conflit ────────────────────────────────

class TestAtomicPublication:
    def test_identical_republication_idempotent(self, tmp_path):
        record = _base_result()
        r1 = TC.store_test_contract_result(record, tmp_path)
        r2 = TC.store_test_contract_result(record, tmp_path)
        assert r1["status"] == "STORED"
        assert r2["status"] == "IDEMPOTENT_EXISTING_IDENTICAL"

    def test_conflicting_publication_same_id_rejected(self, tmp_path):
        record = _base_result()
        TC.store_test_contract_result(record, tmp_path)
        conflicting = dict(record)
        conflicting["created_at"] = "2099-01-01T00:00:00+00:00"  # meme result_id, octets differents
        result = TC.store_test_contract_result(conflicting, tmp_path)
        assert result["status"] == "IMMUTABILITY_VIOLATION"
        # L'original reste intact.
        reloaded = TC.load_test_contract_result(record["result_id"], tmp_path)
        assert reloaded["created_at"] == "2026-01-01T00:00:00+00:00"

    def test_invalid_result_id_rejected(self, tmp_path):
        record = _base_result(result_id="../escape")
        result = TC.store_test_contract_result(record, tmp_path)
        assert result["status"] == "INVALID_RESULT_ID"


# ─── 14-15. Tentatives multiples / append-only ───────────────────────────────

class TestMultipleAttemptsCoexist:
    def test_multiple_attempts_for_same_child_coexist(self, tmp_path):
        attempt1 = _base_result(finished_at="2026-01-01T00:00:01+00:00")
        attempt2 = _base_result(
            finished_at="2026-01-01T00:05:00+00:00",
            aggregate_status=TC.AGGREGATE_REQUIRED_TEST_FAILED,
            checks=[{"check_id": "x", "result": TC.RESULT_FAIL, "required": True}],
        )
        # Recompute distinct identity-based IDs comme le ferait run_and_persist_test_contract.
        seed1 = {k: attempt1.get(k) for k in TC._RESULT_IDENTITY_SEED_FIELDS}
        seed2 = {k: attempt2.get(k) for k in TC._RESULT_IDENTITY_SEED_FIELDS}
        attempt1["result_id"] = TC._compute_result_identity(seed1)
        attempt2["result_id"] = TC._compute_result_identity(seed2)
        attempt1["result_record_hash"] = TC.compute_test_contract_result_hash(attempt1)
        attempt2["result_record_hash"] = TC.compute_test_contract_result_hash(attempt2)
        assert attempt1["result_id"] != attempt2["result_id"]

        r1 = TC.store_test_contract_result(attempt1, tmp_path)
        r2 = TC.store_test_contract_result(attempt2, tmp_path)
        assert r1["status"] == "STORED"
        assert r2["status"] == "STORED"

        loaded1 = TC.load_test_contract_result(attempt1["result_id"], tmp_path)
        loaded2 = TC.load_test_contract_result(attempt2["result_id"], tmp_path)
        assert loaded1["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
        assert loaded2["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED

    def test_no_overwrite_of_earlier_attempt(self, tmp_path):
        record = _base_result()
        TC.store_test_contract_result(record, tmp_path)
        before = TC.load_test_contract_result(record["result_id"], tmp_path)
        # Tentative de republication avec un contenu different sous le meme ID.
        forged = dict(record, aggregate_status=TC.AGGREGATE_TEST_EXECUTION_ERROR)
        TC.store_test_contract_result(forged, tmp_path)
        after = TC.load_test_contract_result(record["result_id"], tmp_path)
        assert before == after
        assert after["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS


# ─── 16-18. Bornage stdout / pas de shell=True / jamais ACT ─────────────────

class TestBoundedAndNonSovereign:
    def test_stdout_stderr_bounded(self, tmp_path):
        check = TC.build_check(
            "big-output", TC.CHECK_TYPE_SUBPROCESS,
            argv=[sys.executable, "-c", "print('X' * 10000)"], expected_exit_code=0,
        )
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        result = TC.run_test_contract(contract, tmp_path)
        assert len(result["checks"][0]["stdout"]) <= 4000

    def test_no_shell_true_in_persistence_module(self):
        import ast
        source = (Path(__file__).resolve().parent.parent / "scripts" / "obsidia_test_contract.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "shell":
                        assert not (isinstance(kw.value, ast.Constant) and kw.value.value is True)

    def test_run_and_persist_never_emits_act(self, tmp_path):
        check = TC.build_check("ok", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        outcome = TC.run_and_persist_test_contract(
            contract, tmp_path, "batch-x", "child-x", "e" * 64, "approval-x", results_dir=tmp_path,
        )
        assert outcome["verify_ok"] is True
        assert "kx108_decision" not in outcome["record"] or outcome["record"].get("kx108_decision") in (None,)
        assert outcome["record"]["decision_authority"] == "KX108_ONLY"
        assert outcome["record"]["aggregate_status"] in (
            TC.AGGREGATE_ALL_REQUIRED_PASS, TC.AGGREGATE_REQUIRED_TEST_FAILED, TC.AGGREGATE_TEST_EXECUTION_ERROR,
        )


# ─── 19-20. Ne mute jamais l'enveloppe ni l'approbation ─────────────────────

class TestNeverMutatesUpstreamArtifacts:
    def test_run_and_persist_does_not_touch_execution_or_approval_stores(self, tmp_path, monkeypatch):
        """
        run_and_persist_test_contract ne prend ni execution_dir ni
        selector_dir en paramètre — structurellement incapable d'écrire
        dans les magasins d'enveloppe/approbation (aucune fonction
        d'écriture de ces magasins n'est jamais appelée par ce chemin).
        """
        import inspect
        sig = inspect.signature(TC.run_and_persist_test_contract)
        assert "execution_dir" not in sig.parameters
        assert "approval" not in sig.parameters

        check = TC.build_check("ok", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        before_files = set((tmp_path).glob("*"))
        TC.run_and_persist_test_contract(
            contract, tmp_path, "batch-x", "child-x", "e" * 64, "approval-x", results_dir=tmp_path,
        )
        # Seul le magasin de resultats (tmp_path lui-meme, via results_dir) est modifie.
        after_files = set((tmp_path).glob("*.json"))
        assert len(after_files) == 1


# ─── Chemin de production complet ────────────────────────────────────────────

class TestRunAndPersistPipeline:
    def test_full_pipeline_pass(self, tmp_path):
        check = TC.build_check("ok", TC.CHECK_TYPE_SUBPROCESS, argv=[sys.executable, "-c", "pass"])
        contract = TC.build_test_contract("c", "e", "b", "t.py", [check])
        outcome = TC.run_and_persist_test_contract(
            contract, tmp_path, "batch-x", "child-x", "e" * 64, "approval-x", results_dir=tmp_path,
        )
        assert outcome["store_result"]["status"] == "STORED"
        assert outcome["verify_ok"] is True
        assert outcome["record"]["batch_execution_id"] == "batch-x"
        assert outcome["record"]["child_execution_id"] == "child-x"
        assert outcome["record"]["execution_authority_hash"] == "e" * 64
        assert outcome["record"]["approval_id"] == "approval-x"
        assert outcome["record"]["test_contract_hash"] == TC.compute_test_contract_hash(contract)
        assert outcome["record"]["required_check_count"] == 1
        assert outcome["record"]["check_count"] == 1
