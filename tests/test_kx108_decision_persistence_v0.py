"""
tests/test_kx108_decision_persistence_v0.py
===============================================
Suite CLOSE_KX108_DECISION_PERSISTENCE_GAP_V0.

Prouve la persistance immuable, append-only, hors dépôt, d'un
CanonicalDecisionEnvelope KX108 réel — sans jamais fabriquer de
décision et sans jamais réinvoquer KX108 en cas d'échec de
persistance.

Tout est synthétique/temporaire (tmp_path) — jamais les identités
réelles ACD-01. Les tests d'intégration production invoquent le vrai
sigma via un ToolingBuildState synthétique isolé (jamais les vraies
données ACD-01), en comptant les invocations réelles.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import obsidia_kx108_decision_store as S  # noqa: E402


def _base_record(**overrides) -> dict:
    envelope = {
        "domain": "tooling_build",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "x108_gate": "ALLOW",
        "reason_code": "GUARD_ALLOW",
        "severity": "S0",
        "decision_id": "synthetic-decision-0001",
        "trace_id": "synthetic-trace-0001",
        "contradictions": [],
        "unknowns": [],
        "risk_flags": [],
        "metrics": {"vote_count": 4, "contradiction_count": 0, "unknown_count": 0},
        "raw_engine": {"consensus": {"formal_result": {"final_decision": "ALLOW"}}},
    }
    envelope.update(overrides.pop("envelope_overrides", {}))
    record = {
        "decision_record_schema_version": S.SCHEMA_VERSION,
        "decision_record_id": "kxd-deadbeef00000000000000000000000000",
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": "synthetic-batch-exec",
        "child_execution_id": "synthetic-child",
        "execution_authority_hash": "a" * 64,
        "approval_id": "synthetic-approval",
        "test_contract_hash": "b" * 64,
        "test_result_id": "tcr-synthetic",
        "test_result_record_hash": "c" * 64,
        "kx108_input_translation_hash": "d" * 64,
        "decision_id": envelope["decision_id"],
        "trace_id": envelope["trace_id"],
        "domain": envelope["domain"],
        "x108_gate": envelope["x108_gate"],
        "reason_code": envelope["reason_code"],
        "severity": envelope["severity"],
        "market_verdict": envelope["market_verdict"],
        "contradictions": envelope["contradictions"],
        "unknowns": envelope["unknowns"],
        "risk_flags": envelope["risk_flags"],
        "decision_authority": S.DECISION_AUTHORITY,
        "canonical_envelope": envelope,
    }
    record.update(overrides)
    record["decision_record_hash"] = S.compute_kx108_decision_record_hash(record)
    return record


# ─── 1-3. Persistance ALLOW / HOLD / BLOCK ───────────────────────────────────

class TestPersistenceByGate:
    def test_allow_record_stores_and_reloads(self, tmp_path):
        record = _base_record()
        result = S.store_kx108_decision_record(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded == record

    def test_hold_record_stores_and_reloads(self, tmp_path):
        record = _base_record(
            x108_gate="HOLD", reason_code="UNKNOWN_THRESHOLD",
            unknowns=["BASE_SHA_MISSING"],
            envelope_overrides={"x108_gate": "HOLD", "unknowns": ["BASE_SHA_MISSING"]},
        )
        result = S.store_kx108_decision_record(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded["x108_gate"] == "HOLD"

    def test_block_record_stores_and_reloads(self, tmp_path):
        record = _base_record(
            x108_gate="BLOCK", reason_code="CONTRADICTION_THRESHOLD_REACHED",
            contradictions=["WORKTREE_NOT_ISOLATED", "BRANCH_NOT_ISOLATED"],
            envelope_overrides={
                "x108_gate": "BLOCK",
                "contradictions": ["WORKTREE_NOT_ISOLATED", "BRANCH_NOT_ISOLATED"],
            },
        )
        result = S.store_kx108_decision_record(record, tmp_path)
        assert result["status"] == "STORED"
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded["x108_gate"] == "BLOCK"
        assert reloaded["contradictions"] == ["WORKTREE_NOT_ISOLATED", "BRANCH_NOT_ISOLATED"]


# ─── 4. Hash déterministe ────────────────────────────────────────────────────

class TestHashDeterminism:
    def test_hash_is_deterministic(self):
        r1 = _base_record()
        r2 = _base_record()
        assert S.compute_kx108_decision_record_hash(r1) == S.compute_kx108_decision_record_hash(r2)

    def test_hash_is_full_sha256(self):
        record = _base_record()
        assert len(record["decision_record_hash"]) == 64
        int(record["decision_record_hash"], 16)  # ne lève pas


# ─── 5-11. Sensibilité du hash à chaque champ lié ────────────────────────────

class TestHashSensitivity:
    def _mutated_hash(self, **overrides):
        base = _base_record()
        base_hash = base["decision_record_hash"]
        mutated = dict(base)
        mutated.update(overrides)
        return base_hash, S.compute_kx108_decision_record_hash(mutated)

    def test_x108_gate_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(x108_gate="BLOCK")
        assert base_hash != mutated_hash

    def test_execution_authority_hash_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(execution_authority_hash="f" * 64)
        assert base_hash != mutated_hash

    def test_test_result_record_hash_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(test_result_record_hash="f" * 64)
        assert base_hash != mutated_hash

    def test_translation_hash_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(kx108_input_translation_hash="f" * 64)
        assert base_hash != mutated_hash

    def test_contradiction_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(contradictions=["SOMETHING_ELSE"])
        assert base_hash != mutated_hash

    def test_unknown_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(unknowns=["SOMETHING_ELSE"])
        assert base_hash != mutated_hash

    def test_decision_id_mutation_changes_hash(self):
        base_hash, mutated_hash = self._mutated_hash(decision_id="other-decision")
        assert base_hash != mutated_hash


# ─── 12-13. Détection d'altération / artefact partiel jamais accepté ────────

class TestTamperDetection:
    def test_tampered_artifact_detected(self, tmp_path):
        record = _base_record()
        S.store_kx108_decision_record(record, tmp_path)
        p = tmp_path / f"{record['decision_record_id']}.json"
        tampered = p.read_text(encoding="utf-8").replace('"ALLOW"', '"BLOCK"', 1)
        p.write_text(tampered, encoding="utf-8")
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        ok, reason = S.verify_kx108_decision_record(reloaded)
        assert ok is False
        assert reason == "DECISION_RECORD_HASH_MISMATCH"

    def test_partial_artifact_never_accepted(self, tmp_path):
        record = _base_record()
        p = tmp_path / f"{record['decision_record_id']}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"decision_record_id": "kxd-partial", "x108_gate": "ALL', encoding="utf-8")
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded is None


# ─── 14-15. Publication idempotente / conflit rejeté ─────────────────────────

class TestPublicationSemantics:
    def test_identical_publication_is_idempotent(self, tmp_path):
        record = _base_record()
        first = S.store_kx108_decision_record(record, tmp_path)
        second = S.store_kx108_decision_record(record, tmp_path)
        assert first["status"] == "STORED"
        assert second["status"] == "IDEMPOTENT_EXISTING_IDENTICAL"

    def test_conflicting_same_id_rejected(self, tmp_path):
        record = _base_record()
        S.store_kx108_decision_record(record, tmp_path)
        conflicting = dict(record)
        conflicting["reason_code"] = "DIFFERENT_REASON"
        conflicting["decision_record_hash"] = S.compute_kx108_decision_record_hash(conflicting)
        result = S.store_kx108_decision_record(conflicting, tmp_path)
        assert result["status"] == "IMMUTABILITY_VIOLATION"
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded["reason_code"] == record["reason_code"]

    def test_invalid_decision_record_id_rejected(self, tmp_path):
        record = _base_record(decision_record_id="../escape")
        result = S.store_kx108_decision_record(record, tmp_path)
        assert result["status"] == "INVALID_DECISION_RECORD_ID"


# ─── 16-17. Multiples décisions coexistent, aucune écrasée ──────────────────

class TestMultipleAttemptsCoexist:
    def test_multiple_decisions_for_same_child_coexist(self, tmp_path):
        r1 = _base_record(x108_gate="HOLD", reason_code="FIRST_ATTEMPT")
        r2 = _base_record(
            x108_gate="BLOCK", reason_code="SECOND_ATTEMPT",
            decision_record_id="kxd-second00000000000000000000000000",
        )
        assert r1["decision_record_id"] != r2["decision_record_id"]
        S.store_kx108_decision_record(r1, tmp_path)
        S.store_kx108_decision_record(r2, tmp_path)
        assert S.load_kx108_decision_record(r1["decision_record_id"], tmp_path)["x108_gate"] == "HOLD"
        assert S.load_kx108_decision_record(r2["decision_record_id"], tmp_path)["x108_gate"] == "BLOCK"

    def test_earlier_attempt_never_overwritten(self, tmp_path):
        r1 = _base_record(reason_code="FIRST")
        S.store_kx108_decision_record(r1, tmp_path)
        r2 = _base_record(
            reason_code="SECOND",
            decision_record_id="kxd-second00000000000000000000000000",
        )
        r2["decision_record_hash"] = S.compute_kx108_decision_record_hash(r2)
        S.store_kx108_decision_record(r2, tmp_path)
        assert S.load_kx108_decision_record(r1["decision_record_id"], tmp_path)["reason_code"] == "FIRST"


# ─── 18-19. ALLOW/HOLD/BLOCK distincts ; souverain != surface preuve ────────

class TestSovereignDistinctFromProofSurface:
    def test_allow_hold_block_remain_distinct(self, tmp_path):
        gates = {}
        for i, gate in enumerate(["ALLOW", "HOLD", "BLOCK"]):
            rec = _base_record(
                x108_gate=gate,
                decision_record_id=f"kxd-{i:032x}",
            )
            S.store_kx108_decision_record(rec, tmp_path)
            gates[gate] = S.load_kx108_decision_record(rec["decision_record_id"], tmp_path)["x108_gate"]
        assert gates == {"ALLOW": "ALLOW", "HOLD": "HOLD", "BLOCK": "BLOCK"}

    def test_sovereign_gate_distinct_from_aggregate4_surface(self, tmp_path):
        record = _base_record(
            x108_gate="BLOCK",
            envelope_overrides={
                "x108_gate": "BLOCK",
                "raw_engine": {"consensus": {
                    "formal_result": {"final_decision": "HOLD", "supermajority": True},
                    "authority": "PROOF_SURFACE_ONLY",
                    "does_not_override_x108_gate": True,
                }},
            },
        )
        S.store_kx108_decision_record(record, tmp_path)
        reloaded = S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        assert reloaded["x108_gate"] == "BLOCK"
        surface = reloaded["canonical_envelope"]["raw_engine"]["consensus"]
        assert surface["formal_result"]["final_decision"] == "HOLD"
        assert surface["authority"] == "PROOF_SURFACE_ONLY"
        assert surface["does_not_override_x108_gate"] is True
        # Le résultat souverain n'est jamais remplacé par la surface preuve.
        assert reloaded["x108_gate"] != surface["formal_result"]["final_decision"]


# ─── 20-21. Persistance n'émet aucune nouvelle décision, ne mute rien ───────

class TestPersistenceEmitsNothing:
    def test_persistence_emits_no_new_decision(self, tmp_path):
        record = _base_record()
        before = dict(record)
        S.store_kx108_decision_record(record, tmp_path)
        assert record == before

    def test_target_repo_never_mutated(self, tmp_path, monkeypatch):
        import subprocess
        before = subprocess.run(
            ["git", "status", "--short"], cwd=str(_REPO_ROOT),
            capture_output=True, text=True,
        ).stdout
        record = _base_record()
        S.store_kx108_decision_record(record, tmp_path)
        S.load_kx108_decision_record(record["decision_record_id"], tmp_path)
        after = subprocess.run(
            ["git", "status", "--short"], cwd=str(_REPO_ROOT),
            capture_output=True, text=True,
        ).stdout
        assert before == after


# ─── 22-24. Primitif de production : invocation KX108 comptée ───────────────

class TestProductionRunAndPersistInvocationCount:
    def _synthetic_kwargs(self, **overrides):
        kwargs = {
            "session_id": "synthetic-session",
            "objective": "synthetic objective",
            "base_sha": "e" * 40, "manifest_hash": "f" * 64, "diff_hash": "0" * 64,
            "approved_scope": ["synthetic/file.py"],
            "actual_touched_files": ["synthetic/file.py"],
            "new_files": [], "deleted_files": [],
            "protected_scope_status": "CLEAN",
            "human_approval_status": "APPROVED",
            "obsidure_status": "CLEAN",
            "worktree_isolated": True, "branch_isolated": True,
            "auto_commit_disabled": True, "auto_push_disabled": True, "auto_merge_disabled": True,
            "tests_results": {"synthetic_check": "PASS"},
            "gates_results": {"synthetic_check": "PASS"}, "first_failure": None,
            "commit_status": "NOT_COMMITTED", "push_status": "NOT_PUSHED", "merge_status": "NOT_MERGED",
            "unknowns": [], "contradictions": [], "risk_flags": [],
            "decision_authority": "KX108_ONLY",
        }
        kwargs.update(overrides)
        return kwargs

    def _binding_context(self, **overrides):
        ctx = {
            "batch_execution_id": "synthetic-batch-exec",
            "child_execution_id": "synthetic-child",
            "execution_authority_hash": "a" * 64,
            "approval_id": "synthetic-approval",
            "test_contract_hash": "b" * 64,
            "test_result_id": "tcr-synthetic",
            "test_result_record_hash": "c" * 64,
            "kx108_input_translation_hash": "d" * 64,
        }
        ctx.update(overrides)
        return ctx

    def test_production_run_and_persist_invokes_kx108_exactly_once(self, tmp_path, monkeypatch):
        import obsidia_kx108_decision_store as store_mod

        call_count = {"n": 0}
        import sigma.protocols as real_protocols

        real_pipeline = real_protocols.run_tooling_build_pipeline

        def counting_pipeline(state):
            call_count["n"] += 1
            return real_pipeline(state)

        monkeypatch.setattr(real_protocols, "run_tooling_build_pipeline", counting_pipeline)

        outcome = store_mod.run_and_persist_kx108_decision(
            self._synthetic_kwargs(), self._binding_context(), tmp_path,
        )
        assert call_count["n"] == 1
        assert outcome["verify_ok"] is True
        assert outcome["record"]["decision_authority"] == "KX108_ONLY"

    def test_failure_during_persistence_does_not_reinvoke_kx108(self, tmp_path, monkeypatch):
        import obsidia_kx108_decision_store as store_mod
        import sigma.protocols as real_protocols

        call_count = {"n": 0}
        real_pipeline = real_protocols.run_tooling_build_pipeline

        def counting_pipeline(state):
            call_count["n"] += 1
            return real_pipeline(state)

        monkeypatch.setattr(real_protocols, "run_tooling_build_pipeline", counting_pipeline)

        def failing_store(record, store_dir=None):
            raise RuntimeError("SIMULATED_STORE_FAILURE")

        monkeypatch.setattr(store_mod, "store_kx108_decision_record", failing_store)

        with pytest.raises(RuntimeError):
            store_mod.run_and_persist_kx108_decision(
                self._synthetic_kwargs(), self._binding_context(), tmp_path,
            )
        assert call_count["n"] == 1

    def test_output_record_retains_kx108_only(self, tmp_path):
        import obsidia_kx108_decision_store as store_mod
        outcome = store_mod.run_and_persist_kx108_decision(
            self._synthetic_kwargs(), self._binding_context(), tmp_path,
        )
        assert outcome["record"]["decision_authority"] == "KX108_ONLY"
        assert outcome["record"]["canonical_envelope"]["metrics"]["decision_authority"] == "KX108_ONLY"

    def test_missing_binding_context_field_rejected_before_any_kx108_call(self, tmp_path, monkeypatch):
        import obsidia_kx108_decision_store as store_mod
        import sigma.protocols as real_protocols

        call_count = {"n": 0}

        def counting_pipeline(state):
            call_count["n"] += 1
            raise AssertionError("KX108 must not be invoked when binding context is incomplete")

        monkeypatch.setattr(real_protocols, "run_tooling_build_pipeline", counting_pipeline)

        incomplete_ctx = self._binding_context()
        del incomplete_ctx["execution_authority_hash"]

        outcome = store_mod.run_and_persist_kx108_decision(
            self._synthetic_kwargs(), incomplete_ctx, tmp_path,
        )
        assert outcome["status"] == "REJECTED"
        assert call_count["n"] == 0
