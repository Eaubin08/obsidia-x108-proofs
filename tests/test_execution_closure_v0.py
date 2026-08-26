"""
tests/test_execution_closure_v0.py
===============================================
Suite CLOSE_REAL_ACD01_BLOCKED_PILOT_V0.

Prouve la persistance immuable, append-only, hors dépôt, d'un
ClosureRecord figeant le résultat final d'une exécution bornée déjà
décidée par KX108 — sans jamais réinvoquer KX108, sans jamais exécuter
de rollback, sans jamais toucher au dépôt.

Tout est synthétique/temporaire (tmp_path) — jamais les identités
réelles ACD-01.
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

import obsidia_execution_closure as C  # noqa: E402


def _binding_context(**overrides) -> dict:
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


def _kx108_decision_record(**overrides) -> dict:
    rec = {
        "decision_record_id": "kxd-deadbeef00000000000000000000000000",
        "decision_record_hash": "e" * 64,
        "x108_gate": "BLOCK",
        "reason_code": "CONTRADICTION_THRESHOLD_REACHED",
    }
    rec.update(overrides)
    return rec


def _create(tmp_path, **overrides):
    kwargs = dict(
        kx108_decision_record=_kx108_decision_record(),
        binding_context=_binding_context(),
        target_path="synthetic/target.py",
        target_pre_apply_sha256="1" * 64,
        target_post_apply_sha256="2" * 64,
        final_disposition="ROLLBACK_PENDING_HUMAN_AUTHORIZATION",
        rollback_status="NOT_EXECUTED",
        store_dir=tmp_path,
    )
    kwargs.update(overrides)
    return C.create_execution_closure_record(**kwargs)


# ─── 1-3. Représentation ALLOW / HOLD / BLOCK ────────────────────────────────

class TestClosureByGate:
    def test_block_closure_stores_and_reloads(self, tmp_path):
        outcome = _create(tmp_path)
        assert outcome["store_result"]["status"] == "STORED"
        assert outcome["record"]["kx108_gate"] == "BLOCK"
        assert outcome["record"]["governance_status"] == "BLOCK"
        assert outcome["record"]["functional_status"] == "PASS"
        assert outcome["record"]["pilot_status"] == "FUNCTIONAL_PASS_GOVERNANCE_BLOCK"

    def test_allow_closure_can_be_represented(self, tmp_path):
        outcome = _create(
            tmp_path,
            kx108_decision_record=_kx108_decision_record(
                decision_record_id="kxd-allow0000000000000000000000000000",
                x108_gate="ALLOW", reason_code="GUARD_ALLOW",
            ),
        )
        assert outcome["record"]["pilot_status"] == "FUNCTIONAL_PASS_GOVERNANCE_ALLOW"

    def test_hold_closure_can_be_represented(self, tmp_path):
        outcome = _create(
            tmp_path,
            kx108_decision_record=_kx108_decision_record(
                decision_record_id="kxd-hold00000000000000000000000000000",
                x108_gate="HOLD", reason_code="UNKNOWN_THRESHOLD",
            ),
        )
        assert outcome["record"]["pilot_status"] == "FUNCTIONAL_PASS_GOVERNANCE_HOLD"


# ─── 4. Hash déterministe ────────────────────────────────────────────────────

class TestHashDeterminism:
    def test_hash_is_deterministic(self):
        base = {k: "x" for k in C._CLOSURE_BOUND_FIELDS}
        h1 = C.compute_execution_closure_hash(base)
        h2 = C.compute_execution_closure_hash(dict(base))
        assert h1 == h2
        assert len(h1) == 64
        int(h1, 16)


# ─── 5-9. Sensibilité du hash à chaque champ lié ─────────────────────────────

class TestHashSensitivity:
    def _base(self):
        return {k: "x" for k in C._CLOSURE_BOUND_FIELDS}

    def test_kx108_decision_record_hash_mutation_changes_hash(self):
        base = self._base()
        base_hash = C.compute_execution_closure_hash(base)
        mutated = dict(base, kx108_decision_record_hash="y")
        assert base_hash != C.compute_execution_closure_hash(mutated)

    def test_test_result_record_hash_mutation_changes_hash(self):
        base = self._base()
        base_hash = C.compute_execution_closure_hash(base)
        mutated = dict(base, test_result_record_hash="y")
        assert base_hash != C.compute_execution_closure_hash(mutated)

    def test_target_pre_sha_mutation_changes_hash(self):
        base = self._base()
        base_hash = C.compute_execution_closure_hash(base)
        mutated = dict(base, target_pre_apply_sha256="y")
        assert base_hash != C.compute_execution_closure_hash(mutated)

    def test_target_post_sha_mutation_changes_hash(self):
        base = self._base()
        base_hash = C.compute_execution_closure_hash(base)
        mutated = dict(base, target_post_apply_sha256="y")
        assert base_hash != C.compute_execution_closure_hash(mutated)

    def test_disposition_mutation_changes_hash(self):
        base = self._base()
        base_hash = C.compute_execution_closure_hash(base)
        mutated = dict(base, final_disposition="y")
        assert base_hash != C.compute_execution_closure_hash(mutated)


# ─── 10-12. Publication immuable / idempotente / conflit rejeté ─────────────

class TestPublicationSemantics:
    def test_immutable_publication(self, tmp_path):
        outcome = _create(tmp_path)
        p = tmp_path / f"{outcome['closure_id']}.json"
        assert p.exists()

    def test_identical_publication_is_idempotent(self, tmp_path):
        record = dict(_create(tmp_path)["record"])
        first = C.store_execution_closure_record(record, tmp_path)
        second = C.store_execution_closure_record(record, tmp_path)
        assert first["status"] == "IDEMPOTENT_EXISTING_IDENTICAL"
        assert second["status"] == "IDEMPOTENT_EXISTING_IDENTICAL"

    def test_conflicting_same_closure_id_rejected(self, tmp_path):
        record = dict(_create(tmp_path)["record"])
        conflicting = dict(record)
        conflicting["rollback_status"] = "DIFFERENT"
        conflicting["closure_record_hash"] = C.compute_execution_closure_hash(conflicting)
        result = C.store_execution_closure_record(conflicting, tmp_path)
        assert result["status"] == "IMMUTABILITY_VIOLATION"
        reloaded = C.load_execution_closure_record(record["closure_id"], tmp_path)
        assert reloaded["rollback_status"] == record["rollback_status"]


# ─── 13-14. Le store n'émet aucune décision, autorité préservée ─────────────

class TestClosureEmitsNoDecision:
    def test_closure_store_never_emits_act_hold_block(self, tmp_path):
        outcome = _create(tmp_path)
        assert not hasattr(C, "decide")
        assert "decide" not in dir(C)
        assert outcome["record"]["kx108_gate"] == "BLOCK"  # reflété, jamais recalculé

    def test_decision_authority_preserved_kx108_only(self, tmp_path):
        outcome = _create(tmp_path)
        assert outcome["record"]["decision_authority"] == "KX108_ONLY"


# ─── 15-16. Aucune invocation KX108, aucun staging/commit dépôt ─────────────

class TestClosureNeverActsOnRepoOrKx108:
    def test_closure_creation_never_performs_rollback(self, tmp_path):
        outcome = _create(tmp_path)
        assert outcome["record"]["rollback_status"] == "NOT_EXECUTED"

    def test_closure_creation_never_stages_or_commits(self, tmp_path, monkeypatch):
        import subprocess
        before = subprocess.run(
            ["git", "status", "--short"], cwd=str(_REPO_ROOT),
            capture_output=True, text=True,
        ).stdout
        _create(tmp_path)
        after = subprocess.run(
            ["git", "status", "--short"], cwd=str(_REPO_ROOT),
            capture_output=True, text=True,
        ).stdout
        assert before == after


# ─── 17. Blocked pilot reste explicitement fonctionnellement PASS ──────────

class TestBlockedPilotRemainsFunctionalPass:
    def test_blocked_pilot_can_explicitly_remain_functional_pass(self, tmp_path):
        outcome = _create(tmp_path)
        rec = outcome["record"]
        assert rec["functional_status"] == "PASS"
        assert rec["governance_status"] == "BLOCK"
        assert rec["pilot_status"] not in ("FAILED_PATCH", "SECURITY_REJECT", "CONTENT_REJECT")


# ─── 18. L'artefact d'origine n'est jamais réécrit après rollback ──────────

class TestOriginalClosureNeverRewritten:
    def test_original_closure_cannot_be_rewritten_after_rollback(self, tmp_path):
        first = _create(tmp_path)
        record = first["record"]

        attempted_rewrite = dict(record)
        attempted_rewrite["rollback_status"] = "EXECUTED"
        attempted_rewrite["final_disposition"] = "ROLLED_BACK"
        attempted_rewrite["closure_record_hash"] = C.compute_execution_closure_hash(attempted_rewrite)

        result = C.store_execution_closure_record(attempted_rewrite, tmp_path)
        assert result["status"] == "IMMUTABILITY_VIOLATION"

        reloaded = C.load_execution_closure_record(record["closure_id"], tmp_path)
        assert reloaded["rollback_status"] == "NOT_EXECUTED"
        assert reloaded["final_disposition"] == "ROLLBACK_PENDING_HUMAN_AUTHORIZATION"
