"""
Test: Brody Memory Intake Gate
===================================
Unit tests for scripts/brody_memory_intake_gate.py and
scripts/brody_memory_pipeline_locator.py.
No live Neo4j required.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import brody_memory_intake_gate as gate
import brody_memory_pipeline_locator as locator


# ── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def temp_audit_dir(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setattr(locator, "AUDIT_DIR", Path(d))
    monkeypatch.setattr(locator, "OUTPUT_DIR", Path(d) / "INTAKE_GATE_OUT")
    yield Path(d)
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def temp_gate_dir(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setattr(gate, "OUTPUT_DIR", Path(d))
    monkeypatch.setattr(gate, "SIDECAR_DIR", Path(d))
    yield Path(d)
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_candidates(temp_gate_dir):
    candidates = [
        {
            "id": "c-001", "status": "LOCAL_CANDIDATE_REVIEW_REQUIRED",
            "content": "X108 kernel est le verrou décisionnel",
            "candidate_type": "x108_info",
            "kernel_mutation": False, "memory_write": False,
            "graphiti_write": False, "neo4j_write": False,
        },
        {
            "id": "c-002", "status": "LOCAL_CANDIDATE_REVIEW_REQUIRED",
            "content": "Brody prépare mais ne décide pas",
            "candidate_type": "boundary_rule",
            "kernel_mutation": False, "memory_write": False,
            "graphiti_write": False, "neo4j_write": False,
        },
    ]
    path = temp_gate_dir / "pending_candidates.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")
    return path


# ── Locator tests ───────────────────────────────────────────────────────

class TestPipelineLocator:
    def test_locator_scans_audit_dir(self, temp_audit_dir):
        report = locator.locate_pipeline()
        assert "pipeline_found" in report
        assert "artifacts" in report

    def test_locator_detects_dry_run_plan(self, temp_audit_dir):
        plan = temp_audit_dir / "GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl"
        plan.write_text('{"test":1}\n{"test":2}\n')
        report = locator.locate_pipeline()
        assert report["pipeline_found"] is True
        assert report["expected_import_count"] == 2

    def test_locator_detects_rollback_plan(self, temp_audit_dir):
        rp = temp_audit_dir / "ROLLBACK_PLAN.cypher"
        rp.write_text("MATCH (n) DETACH DELETE n;")
        report = locator.locate_pipeline()
        assert report["rollback_plan"] is not None

    def test_locator_detects_post_write_validation(self, temp_audit_dir):
        pv = temp_audit_dir / "POST_WRITE_VALIDATION.json"
        pv.write_text('{"status":"PASS"}')
        report = locator.locate_pipeline()
        assert report["post_write_validation"] is not None

    def test_locator_controlled_write_marker(self, temp_audit_dir):
        cw = temp_audit_dir / "BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_report.json"
        cw.write_text("{}")
        report = locator.locate_pipeline()
        assert report["controlled_write_runner"] is not None


# ── Candidate conversion tests ──────────────────────────────────────────

class TestCandidateConversion:
    def test_conversion_preserves_content(self):
        c = {"content": "test info", "candidate_type": "note"}
        result = gate.convert_candidate(c)
        assert result is not None
        assert result["body"] == "test info"

    def test_conversion_sets_kx108(self):
        result = gate.convert_candidate({"content": "test"})
        assert result["decision_authority"] == "KX108_ONLY"

    def test_conversion_memory_write_false(self):
        result = gate.convert_candidate({"content": "test"})
        assert result["memory_write_allowed"] is False

    def test_conversion_graphiti_import_executed_false(self):
        result = gate.convert_candidate({"content": "test"})
        assert result["graphiti_import_executed"] is False

    def test_reject_empty_content(self):
        assert gate.convert_candidate({"content": ""}) is None
        assert gate.convert_candidate({"content": "   "}) is None

    def test_reject_kernel_mutation_true(self):
        assert gate.convert_candidate({"content": "x", "kernel_mutation": True}) is None

    def test_reject_memory_write_true(self):
        assert gate.convert_candidate({"content": "x", "memory_write": True}) is None

    def test_reject_graphiti_write_true(self):
        assert gate.convert_candidate({"content": "x", "graphiti_write": True}) is None

    def test_reject_neo4j_write_true(self):
        assert gate.convert_candidate({"content": "x", "neo4j_write": True}) is None

    def test_reject_non_kx108_authority(self):
        assert gate.convert_candidate({"content": "x", "decision_authority": "OTHER"}) is None

    def test_deduplication(self, sample_candidates):
        candidates = gate.load_candidates(sample_candidates)
        plan, rejected = gate.convert_all_candidates(candidates * 2)
        assert len(plan) == len(candidates)  # deduplicated


# ── Dry-run tests ───────────────────────────────────────────────────────

class TestDryRun:
    def test_dry_run_generates_plan(self, temp_gate_dir, sample_candidates):
        report = gate.run_dry_run(sample_candidates)
        assert report["mode"] == "dry-run"
        assert report["neo4j_write"] is False
        assert report["graphiti_write"] is False

    def test_dry_run_writes_no_neo4j(self, temp_gate_dir, sample_candidates):
        report = gate.run_dry_run(sample_candidates)
        assert report["neo4j_write"] is False


# ── Write approval tests ────────────────────────────────────────────────

class TestWriteApproval:
    def test_write_refused_without_env(self):
        approved, reason = gate.check_write_approval()
        assert approved is False
        assert "WRITE_REFUSED" in reason

    def test_write_refused_partial_env(self, monkeypatch):
        monkeypatch.setenv("BRODY_MEMORY_GATE_MODE", "WRITE")
        approved, reason = gate.check_write_approval()
        assert approved is False

    def test_write_approved_triple_env(self, monkeypatch):
        monkeypatch.setenv("BRODY_MEMORY_GATE_MODE", "WRITE")
        monkeypatch.setenv("BRODY_MEMORY_WRITE_APPROVED", "I_UNDERSTAND_LOCAL_NEO4J_WRITE")
        monkeypatch.setenv("BRODY_MEMORY_TARGET", "LOCAL_NEO4J_7688_ONLY")
        approved, reason = gate.check_write_approval()
        assert approved is True

    def test_no_hardcoded_password(self):
        import brody_memory_intake_gate as m
        source = Path(m.__file__).read_text()
        assert "obsidia-graphiti-dev" not in source.lower()
        assert "password" not in source.lower() or "NEO4J_PASSWORD" in source


# ── Prepare write tests ─────────────────────────────────────────────────

class TestPrepareWrite:
    def test_prepare_generates_rollback(self, temp_gate_dir, sample_candidates):
        report = gate.run_prepare_write(sample_candidates)
        assert "rollback_path" in report
        assert report["neo4j_write"] is False
        assert report["graphiti_write"] is False

    def test_prepare_generates_read_link(self, temp_gate_dir, sample_candidates):
        report = gate.run_prepare_write(sample_candidates)
        assert "read_link_path" in report

    def test_prepare_keeps_write_false(self, temp_gate_dir, sample_candidates):
        report = gate.run_prepare_write(sample_candidates)
        assert report["neo4j_write"] is False
        assert report["graphiti_write"] is False


# ── Write tests ─────────────────────────────────────────────────────────

class TestWrite:
    def test_write_refused_no_env(self, temp_gate_dir, sample_candidates):
        report = gate.run_write(sample_candidates)
        assert report["status"] == "WRITE_REFUSED"

    def test_write_approved_returns_planned(self, temp_gate_dir, sample_candidates, monkeypatch):
        monkeypatch.setenv("BRODY_MEMORY_GATE_MODE", "WRITE")
        monkeypatch.setenv("BRODY_MEMORY_WRITE_APPROVED", "I_UNDERSTAND_LOCAL_NEO4J_WRITE")
        monkeypatch.setenv("BRODY_MEMORY_TARGET", "LOCAL_NEO4J_7688_ONLY")
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USER", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "test")
        report = gate.run_write(sample_candidates)
        assert report["status"] == "REAL_IMPORT_PLANNED"
        assert report["decision_authority"] == "KX108_ONLY"


# ── Sovereign Envelope tests ───────────────────────────────────────────

class TestSovereignEnvelope:
    def test_envelope_has_kx108(self, temp_gate_dir):
        env = gate.build_sovereign_envelope("MEMORY_INTAKE_DRY_RUN")
        assert env["decision_authority"] == "KX108_ONLY"
        assert env["kernel_mutation"] is False

    def test_dry_run_has_no_write_requested(self, temp_gate_dir):
        env = gate.build_sovereign_envelope("MEMORY_INTAKE_DRY_RUN")
        assert env["graphiti_write_requested"] is False
        assert env["neo4j_write_requested"] is False

    def test_prepare_write_has_no_write_requested(self, temp_gate_dir):
        env = gate.build_sovereign_envelope(
            "MEMORY_INTAKE_PREPARE_WRITE", batch_id="test-batch"
        )
        assert env["neo4j_write_requested"] is False

    def test_controlled_write_requires_triple_env(self):
        env = gate.build_sovereign_envelope(
            "MEMORY_INTAKE_CONTROLLED_WRITE",
            batch_id="test", plan_sha256="abc", neo4j_write_requested=True,
        )
        assert env["triple_env_approval_required"] is True

    def test_save_and_load_envelope(self, temp_gate_dir):
        env = gate.build_sovereign_envelope("MEMORY_INTAKE_DRY_RUN")
        path = gate.save_sovereign_envelope(env)
        assert path.exists()
        loaded = gate.load_last_sovereign_envelope()
        assert loaded is not None
        assert loaded["envelope_type"] == "SOVEREIGN_MEMORY_INTAKE_GATE_V1"


# ── Sequence Governor tests ────────────────────────────────────────────

class TestSequenceGovernor:
    def test_dry_run_advances_sequence(self, temp_gate_dir):
        env = gate.advance_sequence("MEMORY_INTAKE_DRY_RUN")
        assert env["sequence_accepted"] is True
        assert env["sequence_step_count_after"] >= 1

    def test_prepare_write_requires_batch_id(self, temp_gate_dir):
        env = gate.advance_sequence("MEMORY_INTAKE_PREPARE_WRITE")
        assert env["sequence_accepted"] is False
        assert "batch_id" in env.get("sequence_rejection", "").lower()

    def test_prepare_write_with_batch_advances(self, temp_gate_dir):
        env = gate.advance_sequence("MEMORY_INTAKE_PREPARE_WRITE", batch_id="test-batch")
        assert env["sequence_accepted"] is True

    def test_write_without_env_blocks(self, temp_gate_dir):
        env = gate.advance_sequence(
            "MEMORY_INTAKE_CONTROLLED_WRITE",
            batch_id="test", plan_sha256="abc", neo4j_write_requested=True,
        )
        assert env["sequence_accepted"] is False

    def test_sequence_state_persists(self, temp_gate_dir):
        gate.advance_sequence("MEMORY_INTAKE_DRY_RUN")
        state = gate.get_sequence_state()
        assert state["sequence_step_count"] >= 1

    def test_invalid_payload_does_not_increment(self, temp_gate_dir):
        before = gate.get_sequence_state()["sequence_step_count"]
        gate.advance_sequence("MEMORY_INTAKE_PREPARE_WRITE")  # no batch_id → rejected
        after = gate.get_sequence_state()["sequence_step_count"]
        assert after == before

    def test_sequence_never_mutates_x108(self, temp_gate_dir):
        env = gate.advance_sequence("MEMORY_INTAKE_DRY_RUN")
        assert env["kernel_mutation"] is False
        assert env["decision_authority"] == "KX108_ONLY"
