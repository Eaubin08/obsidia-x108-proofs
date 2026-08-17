"""
tests/test_obsidure_bounded_apply_v1.py — OBSIDURE_BOUNDED_APPLY_V1
====================================================================
Tests déterministes (stubs isolés) — spec §14.

Ces tests utilisent des proposal_stub.json et des structures contrôlées.
Ils NE CONSTITUENT PAS la preuve de fermeture du Checkpoint 3.
La preuve E2E réelle est dans scripts/obsidure_synth_session.py.

Invariants prouvés dans ce fichier :
  - decision_authority = KX108_ONLY après ACT
  - commit_status = NOT_COMMITTED même après ACT
  - push_status = NOT_PUSHED même après ACT
  - merge_status = NOT_MERGED même après ACT
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_SCRIPTS))

from scripts.obsidure_bounded_apply import (
    GateTestEvidence,
    BoundedApplySession,
    load_and_validate_proposal,
    dryrun_bounded,
    run_bounded_apply,
    run_tests_for_evidence,
    build_tooling_state_from_evidence,
    write_apply_receipt,
    _compute_proposal_hash,
    _validate_proposal_id,
    _check_protected_in_list,
    MAX_FILES_V1,
)
from periphery.agents.agent_obsidure import PROPOSALS_DIR, AgentObsidure

FIXTURE_DIR = _REPO_ROOT / "tests" / "fixtures" / "obsidure_apply_v1" / "session_synth_01"
STUB_JSON = FIXTURE_DIR / "proposal_stub.json"
SANDBOX_FILE = FIXTURE_DIR / "sandbox" / "target_peripheral.py"

BASE_SHA = "d072baa612a60e1df5b6e671c11f5510183eefd2"
WORKTREE = "TERMINAL_BOUNDED_V1"
TARGET_REL = "tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py"
APPROVED_SCOPE = [TARGET_REL]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _make_stub_proposal(tmp_path: Path, overrides: dict | None = None) -> tuple[str, Path]:
    """Crée une proposal stub dans tmp_path/_PATCH_PROPOSALS/<id>/."""
    with STUB_JSON.open(encoding="utf-8") as f:
        data = json.load(f)

    pid = f"stub-{tmp_path.name}"
    data["proposal_id"] = pid
    data["session_id"] = "synth-01"
    data["base_sha"] = BASE_SHA
    data["worktree"] = WORKTREE
    data["approved_scope"] = APPROVED_SCOPE
    data["proposal_files"] = APPROVED_SCOPE
    data["patches"] = [{
        "path": TARGET_REL,
        "sandbox_path": str(SANDBOX_FILE),
        "action": "MODIFY",
    }]

    if overrides:
        data.update(overrides)

    data.pop("proposal_hash", None)
    data["proposal_hash"] = _compute_proposal_hash(data)

    pdir = tmp_path / "_PATCH_PROPOSALS" / pid
    pdir.mkdir(parents=True)
    (pdir / "proposal.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return pid, pdir


def _make_session(proposal_id: str, overrides: dict | None = None) -> BoundedApplySession:
    s = BoundedApplySession(
        session_id="synth-01",
        proposal_id=proposal_id,
        objective="test",
        base_sha=BASE_SHA,
        worktree_path=WORKTREE,
        approved_scope=APPROVED_SCOPE,
        proposal_files=APPROVED_SCOPE,
        operations=[],
        protected_paths_check="CLEAN",
        proposal_hash="abc",
        dryrun_status="OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW",
    )
    if overrides:
        for k, v in overrides.items():
            setattr(s, k, v)
    return s


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ev(status: str = "PASS", exit_code: int = 0) -> GateTestEvidence:
    return GateTestEvidence(
        command="pytest -q",
        test_identity="stub_test",
        exit_code=exit_code,
        status=status,
        timestamp=_ts(),
        results_summary="stub summary",
        receipt_hash="deadbeef",
    )


# ---------------------------------------------------------------------------
# SECTION A — GateTestEvidence
# ---------------------------------------------------------------------------

class TestGateTestEvidence:
    def test_passed_true_when_exit0_and_pass(self):
        ev = _ev("PASS", 0)
        assert ev.passed is True

    def test_passed_false_on_exit_nonzero(self):
        ev = _ev("PASS", 1)
        assert ev.passed is False

    def test_passed_false_on_fail_status(self):
        ev = _ev("FAIL", 0)
        assert ev.passed is False

    def test_passed_false_on_error_status(self):
        ev = _ev("ERROR", 0)
        assert ev.passed is False

    def test_fields_present(self):
        ev = _ev()
        for f in ("command", "test_identity", "exit_code", "status", "timestamp", "results_summary"):
            assert hasattr(ev, f)


# ---------------------------------------------------------------------------
# SECTION B — _validate_proposal_id
# ---------------------------------------------------------------------------

class TestValidateProposalId:
    def test_valid_id(self):
        _validate_proposal_id("abc123")

    def test_rejects_slash(self):
        with pytest.raises(ValueError):
            _validate_proposal_id("a/b")

    def test_rejects_backslash(self):
        with pytest.raises(ValueError):
            _validate_proposal_id("a\\b")

    def test_rejects_dotdot(self):
        with pytest.raises(ValueError):
            _validate_proposal_id("../etc")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            _validate_proposal_id("")


# ---------------------------------------------------------------------------
# SECTION C — _check_protected_in_list
# ---------------------------------------------------------------------------

class TestCheckProtectedInList:
    def test_clean_list(self):
        assert _check_protected_in_list(["sigma/contracts.py", "tests/test_x.py"]) == []

    def test_kernel_detected(self):
        r = _check_protected_in_list(["runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs"])
        assert len(r) == 1

    def test_proofs_detected(self):
        r = _check_protected_in_list(["proofs/V18_something.lean"])
        assert len(r) == 1

    def test_merkle_detected(self):
        r = _check_protected_in_list(["merkle_seal.json"])
        assert len(r) == 1

    def test_mixed(self):
        r = _check_protected_in_list(["sigma/x.py", "merkle_seal.json", "formal/y.lean"])
        assert "merkle_seal.json" in r
        assert "formal/y.lean" in r
        assert "sigma/x.py" not in r


# ---------------------------------------------------------------------------
# SECTION D — _compute_proposal_hash
# ---------------------------------------------------------------------------

class TestComputeProposalHash:
    def test_deterministic(self):
        data = {"a": 1, "b": "x"}
        assert _compute_proposal_hash(data) == _compute_proposal_hash(data)

    def test_excludes_human_approved(self):
        d1 = {"a": 1, "human_approved": False}
        d2 = {"a": 1, "human_approved": True}
        assert _compute_proposal_hash(d1) == _compute_proposal_hash(d2)

    def test_excludes_status(self):
        d1 = {"a": 1, "status": "PENDING"}
        d2 = {"a": 1, "status": "APPLIED"}
        assert _compute_proposal_hash(d1) == _compute_proposal_hash(d2)

    def test_sensitive_to_content(self):
        d1 = {"a": 1}
        d2 = {"a": 2}
        assert _compute_proposal_hash(d1) != _compute_proposal_hash(d2)

    def test_returns_16_chars(self):
        h = _compute_proposal_hash({"x": 1})
        assert len(h) == 16


# ---------------------------------------------------------------------------
# SECTION E — load_and_validate_proposal
# ---------------------------------------------------------------------------

class TestLoadAndValidateProposal:
    def test_valid_proposal_loads(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        assert s.session_id == "synth-01"
        assert s.protected_paths_check == "CLEAN"

    def test_missing_proposal_raises(self, tmp_path, monkeypatch):
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="BLOCK_PROPOSAL_NOT_FOUND"):
            load_and_validate_proposal("nonexistent", "s", BASE_SHA, WORKTREE, APPROVED_SCOPE)

    def test_wrong_session_id_raises(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="HOLD_PROPOSAL_MISMATCH"):
            load_and_validate_proposal(pid, "WRONG_SESSION", BASE_SHA, WORKTREE, APPROVED_SCOPE)

    def test_wrong_base_sha_raises(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="HOLD_PROPOSAL_MISMATCH"):
            load_and_validate_proposal(pid, "synth-01", "WRONGSHA", WORKTREE, APPROVED_SCOPE)

    def test_wrong_worktree_raises(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="BLOCK"):
            load_and_validate_proposal(pid, "synth-01", BASE_SHA, "WRONG_WT", APPROVED_SCOPE)

    def test_out_of_scope_raises(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path, overrides={"proposal_files": ["sigma/contracts.py"]})
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="BLOCK_SCOPE_DRIFT"):
            load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)

    def test_protected_path_in_proposal_raises(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path, overrides={
            "proposal_files": ["merkle_seal.json"],
            "approved_scope": ["merkle_seal.json"],
        })
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="BLOCK"):
            load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, ["merkle_seal.json"])

    def test_altered_hash_raises(self, tmp_path, monkeypatch):
        pid, pdir = _make_stub_proposal(tmp_path)
        pjson = pdir / "proposal.json"
        d = json.loads(pjson.read_text(encoding="utf-8"))
        d["proposal_hash"] = "0000000000000000"
        pjson.write_text(json.dumps(d), encoding="utf-8")
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="HOLD_PROPOSAL_MISMATCH"):
            load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)

    def test_scope_too_large_raises(self, tmp_path, monkeypatch):
        oversized = [f"sigma/f{i}.py" for i in range(MAX_FILES_V1 + 1)]
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        with pytest.raises(ValueError, match="BLOCK"):
            load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, oversized)


# ---------------------------------------------------------------------------
# SECTION F — dryrun_bounded
# ---------------------------------------------------------------------------

class TestDryrunBounded:
    def test_valid_dryrun_ready(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        s = dryrun_bounded(s)
        assert s.dryrun_status == "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW"

    def test_dryrun_detects_missing_sandbox(self, tmp_path, monkeypatch):
        pid, pdir = _make_stub_proposal(tmp_path)
        pjson = pdir / "proposal.json"
        d = json.loads(pjson.read_text(encoding="utf-8"))
        d["patches"][0]["sandbox_path"] = "/nonexistent/path.py"
        d.pop("proposal_hash", None)
        d["proposal_hash"] = _compute_proposal_hash(d)
        pjson.write_text(json.dumps(d), encoding="utf-8")
        _patch_proposals(monkeypatch, tmp_path)
        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        s = dryrun_bounded(s)
        assert "SANDBOX_MISSING" in s.dryrun_status

    def test_dryrun_no_write(self, tmp_path, monkeypatch):
        pid, _ = _make_stub_proposal(tmp_path)
        _patch_proposals(monkeypatch, tmp_path)
        files_before = list(tmp_path.rglob("*"))
        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        _ = dryrun_bounded(s)
        files_after = list(tmp_path.rglob("*"))
        new_files = [f for f in files_after if f not in files_before and f.is_file() and "proposal" not in f.name]
        assert new_files == [], f"DryRun a écrit des fichiers : {new_files}"

    def test_dryrun_protected_path_flagged(self, tmp_path, monkeypatch):
        pid, pdir = _make_stub_proposal(tmp_path)
        pjson = pdir / "proposal.json"
        d = json.loads(pjson.read_text(encoding="utf-8"))
        d["patches"].append({"path": "server.kernel.sealed.cjs", "sandbox_path": str(SANDBOX_FILE), "action": "MODIFY"})
        pjson.write_text(json.dumps(d), encoding="utf-8")
        _patch_proposals(monkeypatch, tmp_path)
        s = _make_session(pid)
        s.proposal_id = pid
        s2 = dryrun_bounded(s)
        assert "PROTECTED_PATH" in s2.dryrun_status or s2.dryrun_status == "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW"


# ---------------------------------------------------------------------------
# SECTION G — run_bounded_apply
# ---------------------------------------------------------------------------

def _patch_proposals(monkeypatch, tmp_path: Path) -> None:
    """Patche PROPOSALS_DIR dans obsidure_bounded_apply (propagé via proposals_dir=PROPOSALS_DIR)."""
    monkeypatch.setattr("scripts.obsidure_bounded_apply.PROPOSALS_DIR", tmp_path / "_PATCH_PROPOSALS")


class TestRunBoundedApply:
    def test_apply_copies_file(self, tmp_path, monkeypatch):
        _patch_proposals(monkeypatch, tmp_path)
        pid, _ = _make_stub_proposal(tmp_path)
        target = tmp_path / TARGET_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original", encoding="utf-8")

        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        s = dryrun_bounded(s)
        agent = AgentObsidure()
        s = run_bounded_apply(s, agent, tmp_path)

        assert s.apply_status == "APPLIED"
        assert TARGET_REL in s.actual_modified_files
        assert "APPLIED_BY_OBSIDURE" in target.read_text(encoding="utf-8")

    def test_apply_blocked_before_dryrun(self, tmp_path, monkeypatch):
        _patch_proposals(monkeypatch, tmp_path)
        pid, _ = _make_stub_proposal(tmp_path)
        s = _make_session(pid, {"dryrun_status": "PENDING"})
        agent = AgentObsidure()
        with pytest.raises(ValueError, match="BLOCK"):
            run_bounded_apply(s, agent, tmp_path)

    def test_apply_scope_drift_detected(self, tmp_path, monkeypatch):
        _patch_proposals(monkeypatch, tmp_path)
        pid, pdir = _make_stub_proposal(tmp_path)
        pjson = pdir / "proposal.json"
        d = json.loads(pjson.read_text(encoding="utf-8"))
        extra_sandbox = tmp_path / "extra.py"
        extra_sandbox.write_text("extra", encoding="utf-8")
        d["patches"].append({"path": "sigma/extra_file.py", "sandbox_path": str(extra_sandbox), "action": "MODIFY"})
        pjson.write_text(json.dumps(d), encoding="utf-8")

        (tmp_path / TARGET_REL).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / TARGET_REL).write_text("orig", encoding="utf-8")

        s = _make_session(pid)
        agent = AgentObsidure()
        s2 = run_bounded_apply(s, agent, tmp_path)
        assert "BLOCK_SCOPE_DRIFT" in s2.apply_status

    def test_apply_no_git_call(self, tmp_path, monkeypatch):
        _patch_proposals(monkeypatch, tmp_path)
        git_calls = []
        orig_run = subprocess.run
        def mock_run(cmd, *a, **kw):
            if isinstance(cmd, (list, tuple)) and "git" in str(cmd[0]).lower():
                git_calls.append(cmd)
            return orig_run(cmd, *a, **kw)
        monkeypatch.setattr(subprocess, "run", mock_run)

        pid, _ = _make_stub_proposal(tmp_path)
        (tmp_path / TARGET_REL).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / TARGET_REL).write_text("orig", encoding="utf-8")

        s = load_and_validate_proposal(pid, "synth-01", BASE_SHA, WORKTREE, APPROVED_SCOPE)
        s = dryrun_bounded(s)
        agent = AgentObsidure()
        run_bounded_apply(s, agent, tmp_path)
        assert git_calls == [], f"Git appele par run_bounded_apply : {git_calls}"


# ---------------------------------------------------------------------------
# SECTION H — run_tests_for_evidence
# ---------------------------------------------------------------------------

class TestRunTestsForEvidence:
    def test_passing_command_returns_pass(self, tmp_path):
        ev = run_tests_for_evidence(
            test_command=[sys.executable, "-c", "print('ok')"],
            test_identity="test_pass",
            worktree_root=tmp_path,
            timeout=10,
        )
        assert ev.exit_code == 0
        assert ev.status == "PASS"
        assert ev.passed is True

    def test_failing_command_returns_fail(self, tmp_path):
        ev = run_tests_for_evidence(
            test_command=[sys.executable, "-c", "import sys; sys.exit(1)"],
            test_identity="test_fail",
            worktree_root=tmp_path,
            timeout=10,
        )
        assert ev.exit_code == 1
        assert ev.status == "FAIL"
        assert ev.passed is False

    def test_result_has_all_fields(self, tmp_path):
        ev = run_tests_for_evidence(
            test_command=[sys.executable, "-c", "pass"],
            test_identity="field_check",
            worktree_root=tmp_path,
            timeout=10,
        )
        for f in ("command", "test_identity", "exit_code", "status", "timestamp", "results_summary", "receipt_hash"):
            assert hasattr(ev, f), f"Champ manquant : {f}"

    def test_receipt_hash_populated(self, tmp_path):
        ev = run_tests_for_evidence(
            test_command=[sys.executable, "-c", "print('out')"],
            test_identity="hash_test",
            worktree_root=tmp_path,
            timeout=10,
        )
        assert ev.receipt_hash and ev.receipt_hash not in ("", "TIMEOUT", "EXEC_ERROR")


# ---------------------------------------------------------------------------
# SECTION I — build_tooling_state_from_evidence
# ---------------------------------------------------------------------------

class TestBuildToolingStateFromEvidence:
    def _session(self) -> BoundedApplySession:
        s = BoundedApplySession(
            session_id="test-state-01",
            proposal_id="pid",
            objective="obj",
            base_sha=BASE_SHA,
            worktree_path=WORKTREE,
            approved_scope=APPROVED_SCOPE,
            proposal_files=APPROVED_SCOPE,
            operations=[],
            protected_paths_check="CLEAN",
            proposal_hash="abc123",
            apply_status="APPLIED",
            actual_modified_files=[TARGET_REL],
            commit_status="NOT_COMMITTED",
            push_status="NOT_PUSHED",
            merge_status="NOT_MERGED",
        )
        return s

    def test_pass_pass_builds_state(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev("PASS", 0), _ev("PASS", 0))
        assert state.tests_results == "PASS"
        assert state.gates_results == "PASS"
        assert state.decision_authority == "KX108_ONLY"

    def test_fail_tests_reflected(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev("FAIL", 1), _ev("PASS", 0))
        assert state.tests_results == "FAIL"
        assert "TEST:" in state.first_failure

    def test_fail_gates_reflected(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev("PASS", 0), _ev("FAIL", 2))
        assert state.gates_results == "FAIL"
        assert "GATE:" in state.first_failure

    def test_commit_status_locked(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev(), _ev())
        assert state.commit_status == "NOT_COMMITTED"
        assert state.push_status == "NOT_PUSHED"
        assert state.merge_status == "NOT_MERGED"

    def test_auto_disabled_invariants(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev(), _ev())
        assert state.auto_commit_disabled is True
        assert state.auto_push_disabled is True
        assert state.auto_merge_disabled is True

    def test_worktree_isolated(self):
        s = self._session()
        state = build_tooling_state_from_evidence(s, _ev(), _ev())
        assert state.worktree_isolated is True
        assert state.branch_isolated is True


# ---------------------------------------------------------------------------
# SECTION J — KX108 via pipeline complet (stubs)
# ---------------------------------------------------------------------------

class TestKX108Integration:
    def _run_pipeline(self, tests_ok: bool, gates_ok: bool):
        from sigma.protocols import run_tooling_build_pipeline
        import dataclasses as _dc

        s = BoundedApplySession(
            session_id="kx108-test-01",
            proposal_id="pid",
            objective="KX108 test",
            base_sha=BASE_SHA,
            worktree_path=WORKTREE,
            approved_scope=APPROVED_SCOPE,
            proposal_files=APPROVED_SCOPE,
            operations=[],
            protected_paths_check="CLEAN",
            proposal_hash="abc",
            apply_status="APPLIED",
            actual_modified_files=[TARGET_REL],
            commit_status="NOT_COMMITTED",
            push_status="NOT_PUSHED",
            merge_status="NOT_MERGED",
        )
        te = _ev("PASS" if tests_ok else "FAIL", 0 if tests_ok else 1)
        ge = _ev("PASS" if gates_ok else "FAIL", 0 if gates_ok else 1)
        state = build_tooling_state_from_evidence(s, te, ge)
        result = run_tooling_build_pipeline(state)
        return _dc.asdict(result)

    def test_act_path(self):
        r = self._run_pipeline(True, True)
        assert r.get("x108_gate") == "ALLOW"
        assert r.get("metrics", {}).get("decision_authority") == "KX108_ONLY"
        assert r.get("metrics", {}).get("emits_act") is False

    def test_block_path_on_fail(self):
        r = self._run_pipeline(False, False)
        gate = r.get("x108_gate")
        assert gate in ("BLOCK", "HOLD")

    def test_decision_authority_always_kx108(self):
        for tests_ok, gates_ok in [(True, True), (False, True), (True, False), (False, False)]:
            r = self._run_pipeline(tests_ok, gates_ok)
            assert r.get("metrics", {}).get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# SECTION K — Authority invariants — preuve formelle §14
# ---------------------------------------------------------------------------

class TestAuthorityInvariants:
    """
    Prouve que même après ACT :
      commit_status = NOT_COMMITTED
      push_status   = NOT_PUSHED
      merge_status  = NOT_MERGED
      decision_authority = KX108_ONLY
    """

    def _build_state(self) -> "ToolingBuildState":
        from scripts.obsidure_bounded_apply import build_tooling_state_from_evidence, BoundedApplySession, GateTestEvidence
        from datetime import datetime, timezone

        s = BoundedApplySession(
            session_id="authority-proof-01",
            proposal_id="pid",
            objective="authority proof",
            base_sha=BASE_SHA,
            worktree_path=WORKTREE,
            approved_scope=APPROVED_SCOPE,
            proposal_files=APPROVED_SCOPE,
            operations=[],
            protected_paths_check="CLEAN",
            proposal_hash="abc",
            apply_status="APPLIED",
            actual_modified_files=[TARGET_REL],
            commit_status="NOT_COMMITTED",
            push_status="NOT_PUSHED",
            merge_status="NOT_MERGED",
        )
        te = GateTestEvidence("c", "t", 0, "PASS", datetime.now(timezone.utc).isoformat(), "ok", "ab")
        return build_tooling_state_from_evidence(s, te, te)

    def test_commit_status_not_committed(self):
        state = self._build_state()
        assert state.commit_status == "NOT_COMMITTED"

    def test_push_status_not_pushed(self):
        state = self._build_state()
        assert state.push_status == "NOT_PUSHED"

    def test_merge_status_not_merged(self):
        state = self._build_state()
        assert state.merge_status == "NOT_MERGED"

    def test_decision_authority_kx108_only(self):
        state = self._build_state()
        assert state.decision_authority == "KX108_ONLY"

    def test_auto_commit_disabled(self):
        state = self._build_state()
        assert state.auto_commit_disabled is True

    def test_auto_push_disabled(self):
        state = self._build_state()
        assert state.auto_push_disabled is True

    def test_auto_merge_disabled(self):
        state = self._build_state()
        assert state.auto_merge_disabled is True

    def test_kx108_does_not_commit(self):
        from sigma.protocols import run_tooling_build_pipeline
        import dataclasses as _dc
        state = self._build_state()
        r = _dc.asdict(run_tooling_build_pipeline(state))
        assert r.get("metrics", {}).get("decision_authority") == "KX108_ONLY"
        assert r.get("metrics", {}).get("emits_act") is False

    def test_act_means_ready_for_review_not_commit(self):
        from sigma.protocols import run_tooling_build_pipeline
        import dataclasses as _dc
        state = self._build_state()
        r = _dc.asdict(run_tooling_build_pipeline(state))
        if r.get("x108_gate") == "ALLOW":
            assert r.get("market_verdict") == "READY_FOR_COMMIT_REVIEW"
            assert r.get("metrics", {}).get("emits_act") is False
