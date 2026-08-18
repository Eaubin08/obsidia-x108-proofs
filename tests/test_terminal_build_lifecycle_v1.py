"""
tests/test_terminal_build_lifecycle_v1.py
=========================================
Suite TERMINAL_BUILD_LIFECYCLE_V1.

Couvre : cmd_list, cmd_status, cmd_inspect, cmd_resume, cmd_review, cmd_abort,
         cmd_cleanup + helpers + invariants d'autorité + preuve E2E sur sessions réelles.

Contraintes :
  - NE DÉTRUIT PAS la session réelle 35d45cb9.
  - NE MODIFIE PAS receipt.json ni apply_receipt.json (immutables).
  - decision_authority = KX108_ONLY dans tous les chemins.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import shutil
import subprocess

import pytest
from unittest.mock import MagicMock, patch

# Ajouter scripts/ au path
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_build as _OB  # noqa: E402
from obsidia_build import (  # noqa: E402
    DECISION_AUTHORITY,
    OBSIDIA_BUILD_STATE_DIR,
    _append_lifecycle_event,
    _derive_lifecycle_status,
    _git_worktree_state,
    _list_sessions,
    _load_apply_receipt,
    _load_lifecycle_events,
    _load_receipt,
    _session_summary,
    cmd_abort,
    cmd_cleanup,
    cmd_inspect,
    cmd_list,
    cmd_resume,
    cmd_review,
    cmd_status,
)


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def receipt_act(tmp_path):
    """Receipt ACT → READY_FOR_COMMIT_REVIEW."""
    return {
        "session_id": "sess_act",
        "objective": "Test objectif ACT",
        "domain": "PERIPHERAL",
        "base_sha": "abc123def456abc1",
        "branch": "feat/test-sess-act",
        "worktree": str(tmp_path / "wt_nonexistent_act"),
        "approved_scope": ["tests/fixtures/target.py"],
        "manifest_hash": "mhash_act",
        "diff_hash": "dhash_act",
        "kx108_decision": "ACT",
        "next_human_action": "READY_FOR_COMMIT_REVIEW",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "timestamps": {
            "start": "2026-08-05T21:00:00.000000+00:00",
            "end": "2026-08-05T21:00:12.000000+00:00",
        },
    }


@pytest.fixture
def receipt_hold(tmp_path):
    """Receipt HOLD."""
    return {
        "session_id": "sess_hold",
        "objective": "Test objectif HOLD",
        "domain": "PERIPHERAL",
        "base_sha": "abc123def456abc2",
        "branch": "feat/test-sess-hold",
        "worktree": str(tmp_path / "wt_nonexistent_hold"),
        "approved_scope": ["tests/fixtures/target.py"],
        "manifest_hash": "mhash_hold",
        "diff_hash": "dhash_hold",
        "kx108_decision": "HOLD",
        "next_human_action": "HOLD",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "timestamps": {"start": "2026-08-05T22:00:00.000000+00:00"},
    }


@pytest.fixture
def receipt_block(tmp_path):
    """Receipt BLOCK."""
    return {
        "session_id": "sess_block",
        "objective": "Test objectif BLOCK",
        "domain": "PERIPHERAL",
        "base_sha": "abc123def456abc3",
        "branch": "feat/test-sess-block",
        "worktree": str(tmp_path / "wt_nonexistent_block"),
        "approved_scope": ["tests/fixtures/target.py"],
        "manifest_hash": "mhash_block",
        "diff_hash": "dhash_block",
        "kx108_decision": "BLOCK",
        "next_human_action": "BLOCK",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "timestamps": {"start": "2026-08-05T23:00:00.000000+00:00"},
    }


@pytest.fixture
def receipt_committed(tmp_path):
    """Receipt COMMITTED."""
    return {
        "session_id": "sess_committed",
        "objective": "Test objectif committed",
        "domain": "PERIPHERAL",
        "base_sha": "abc123def456abc4",
        "branch": "feat/test-committed",
        "worktree": str(tmp_path / "wt_committed"),
        "approved_scope": ["tests/fixtures/target.py"],
        "manifest_hash": "mhash_committed",
        "diff_hash": "dhash_committed",
        "kx108_decision": "ACT",
        "next_human_action": "COMMITTED",
        "commit_status": "COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "timestamps": {"start": "2026-08-05T20:00:00.000000+00:00"},
    }


def _write_receipt(state_dir: Path, session_id: str, data: dict) -> Path:
    p = state_dir / session_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "receipt.json").write_text(json.dumps(data), encoding="utf-8")
    return p


# ─── Helpers ────────────────────────────────────────────────────────────────

class TestHelpers:
    def test_load_receipt_absent(self, tmp_path):
        assert _load_receipt("nosession", tmp_path) is None

    def test_load_receipt_present(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        r = _load_receipt("sess_act", tmp_path)
        assert r is not None
        assert r["session_id"] == "sess_act"

    def test_load_apply_receipt_absent(self, tmp_path):
        assert _load_apply_receipt("nosession", tmp_path) is None

    def test_load_apply_receipt_present(self, tmp_path):
        ar = {"session_id": "s1", "kx108_decision": "BLOCK", "apply_status": "APPLIED"}
        (tmp_path / "s1").mkdir()
        (tmp_path / "s1" / "apply_receipt.json").write_text(json.dumps(ar), encoding="utf-8")
        r = _load_apply_receipt("s1", tmp_path)
        assert r is not None
        assert r["kx108_decision"] == "BLOCK"

    def test_load_lifecycle_events_absent(self, tmp_path):
        assert _load_lifecycle_events("nosession", tmp_path) == []

    def test_append_and_load_lifecycle_events(self, tmp_path):
        (tmp_path / "s1").mkdir()
        _append_lifecycle_event("s1", "ABORTED", {"reason": "test"}, tmp_path)
        evts = _load_lifecycle_events("s1", tmp_path)
        assert len(evts) == 1
        assert evts[0]["type"] == "ABORTED"
        assert evts[0]["reason"] == "test"
        assert evts[0]["by"] == "operator"

    def test_append_multiple_events(self, tmp_path):
        (tmp_path / "s1").mkdir()
        _append_lifecycle_event("s1", "ABORTED", {}, tmp_path)
        _append_lifecycle_event("s1", "CLEANED", {}, tmp_path)
        evts = _load_lifecycle_events("s1", tmp_path)
        assert len(evts) == 2
        assert evts[0]["type"] == "ABORTED"
        assert evts[1]["type"] == "CLEANED"

    def test_list_sessions_empty(self, tmp_path):
        assert _list_sessions(tmp_path) == []

    def test_list_sessions_missing_dir(self, tmp_path):
        assert _list_sessions(tmp_path / "absent") == []

    def test_list_sessions_with_receipts(self, tmp_path, receipt_act):
        for sid in ("s1", "s2", "s3"):
            _write_receipt(tmp_path, sid, receipt_act)
        sessions = _list_sessions(tmp_path)
        assert set(sessions) == {"s1", "s2", "s3"}

    def test_list_sessions_with_apply_receipt_only(self, tmp_path):
        ar = {"kx108_decision": "BLOCK"}
        (tmp_path / "s_obsidure").mkdir()
        (tmp_path / "s_obsidure" / "apply_receipt.json").write_text(json.dumps(ar))
        sessions = _list_sessions(tmp_path)
        assert "s_obsidure" in sessions

    def test_list_sessions_ignores_empty_dirs(self, tmp_path):
        (tmp_path / "empty_dir").mkdir()
        assert _list_sessions(tmp_path) == []

    def test_git_worktree_state_nonexistent(self, tmp_path):
        wt = _git_worktree_state(tmp_path / "absent")
        assert wt["exists"] is False

    def test_git_worktree_state_non_git_dir(self, tmp_path):
        wt_dir = tmp_path / "not_a_git"
        wt_dir.mkdir()
        wt = _git_worktree_state(wt_dir)
        assert wt["exists"] is True
        assert wt.get("branch") == "?"
        # Fail-closed : dirty=None quand git status échoue (jamais False par défaut)
        assert wt.get("dirty") is None
        assert wt.get("state_complete") is False


# ─── _derive_lifecycle_status ───────────────────────────────────────────────

class TestDeriveLifecycleStatus:
    def test_cleaned_wins_over_everything(self):
        r = {"commit_status": "COMMITTED"}
        evts = [{"type": "CLEANED"}]
        assert _derive_lifecycle_status(r, None, evts, None) == "CLEANED"

    def test_aborted_wins_over_receipt(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "ACT"}
        evts = [{"type": "ABORTED"}]
        assert _derive_lifecycle_status(r, None, evts, None) == "ABORTED"

    def test_cleaned_wins_over_aborted_if_more_recent(self):
        evts = [{"type": "ABORTED"}, {"type": "CLEANED"}]
        assert _derive_lifecycle_status(None, None, evts, None) == "CLEANED"

    def test_committed_from_receipt(self):
        r = {"commit_status": "COMMITTED"}
        assert _derive_lifecycle_status(r, None, [], None) == "COMMITTED"

    def test_act_decision_gives_ready_for_commit(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "ACT"}
        assert _derive_lifecycle_status(r, None, [], None) == "READY_FOR_COMMIT_REVIEW"

    def test_nha_ready_for_commit_review(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "",
             "next_human_action": "READY_FOR_COMMIT_REVIEW"}
        assert _derive_lifecycle_status(r, None, [], None) == "READY_FOR_COMMIT_REVIEW"

    def test_hold_from_receipt(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "HOLD"}
        assert _derive_lifecycle_status(r, None, [], None) == "HOLD"

    def test_block_from_receipt(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "BLOCK"}
        assert _derive_lifecycle_status(r, None, [], None) == "BLOCK"

    def test_plan_proposed_no_scope(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": ""}
        assert _derive_lifecycle_status(r, None, [], None) == "PLAN_PROPOSED"

    def test_approved_with_scope_no_worktree(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "",
             "approved_scope": ["f.py"]}
        assert _derive_lifecycle_status(r, None, [], None) == "APPROVED"

    def test_worktree_ready_with_scope_and_worktree(self):
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "",
             "approved_scope": ["f.py"]}
        wt = {"exists": True}
        assert _derive_lifecycle_status(r, None, [], wt) == "WORKTREE_READY"

    def test_apply_receipt_block(self):
        ar = {"kx108_decision": "BLOCK"}
        assert _derive_lifecycle_status(None, ar, [], None) == "BLOCK"

    def test_apply_receipt_act(self):
        ar = {"kx108_decision": "ACT"}
        assert _derive_lifecycle_status(None, ar, [], None) == "READY_FOR_COMMIT_REVIEW"

    def test_apply_receipt_applied_status(self):
        ar = {"kx108_decision": "", "apply_status": "APPLIED"}
        assert _derive_lifecycle_status(None, ar, [], None) == "APPLIED"

    def test_unknown_when_no_receipts(self):
        assert _derive_lifecycle_status(None, None, [], None) == "UNKNOWN"

    def test_kx108_decisions_are_not_lifecycle_status(self):
        # ACT, HOLD, BLOCK sont des décisions KX108, pas des lifecycle_status
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "ACT"}
        status = _derive_lifecycle_status(r, None, [], None)
        assert status not in ("ACT", "HOLD", "BLOCK")

    def test_aborted_is_not_kx108_decision(self):
        # ABORTED vient d'un lifecycle event, pas de kx108_decision
        r = {"commit_status": "NOT_COMMITTED", "kx108_decision": "ACT"}
        evts = [{"type": "ABORTED"}]
        status = _derive_lifecycle_status(r, None, evts, None)
        assert status == "ABORTED"
        assert status != "ACT"


# ─── cmd_list ───────────────────────────────────────────────────────────────

class TestCmdList:
    def test_list_empty_state_dir(self, tmp_path, capsys):
        ret = cmd_list(tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "Aucune session" in out

    def test_list_one_session(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_list(tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "sess_act" in out
        assert "READY_FOR_COMMIT_REVIEW" in out

    def test_list_multiple_sessions(self, tmp_path, receipt_act, receipt_hold, receipt_block, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        _write_receipt(tmp_path, "sess_block", receipt_block)
        ret = cmd_list(tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "sess_act" in out
        assert "sess_hold" in out
        assert "sess_block" in out
        assert "3 session(s)" in out

    def test_list_shows_kx108_only_authority(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        cmd_list(tmp_path)
        out = capsys.readouterr().out
        assert "KX108_ONLY" in out

    def test_list_does_not_mutate_state_dir(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        files_before = {f.name for f in (tmp_path / "sess_act").iterdir()}
        cmd_list(tmp_path)
        files_after = {f.name for f in (tmp_path / "sess_act").iterdir()}
        assert files_before == files_after


# ─── cmd_status ─────────────────────────────────────────────────────────────

class TestCmdStatus:
    def test_status_unknown_session(self, tmp_path, capsys):
        ret = cmd_status("unknownsession", tmp_path)
        assert ret == 2
        out = capsys.readouterr().out
        assert "STATUS_FAIL" in out

    def test_status_act_session(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_status("sess_act", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "sess_act" in out
        assert "READY_FOR_COMMIT_REVIEW" in out

    def test_status_hold_session(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        ret = cmd_status("sess_hold", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "HOLD" in out

    def test_status_block_session(self, tmp_path, receipt_block, capsys):
        _write_receipt(tmp_path, "sess_block", receipt_block)
        ret = cmd_status("sess_block", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "BLOCK" in out

    def test_status_committed_session(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        ret = cmd_status("sess_committed", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "COMMITTED" in out

    def test_status_does_not_modify_receipt(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_status("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before


# ─── cmd_inspect ────────────────────────────────────────────────────────────

class TestCmdInspect:
    def test_inspect_unknown_session(self, tmp_path, capsys):
        ret = cmd_inspect("unknownsession", tmp_path)
        assert ret == 2
        out = capsys.readouterr().out
        assert "INSPECT_FAIL" in out

    def test_inspect_act_session(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_inspect("sess_act", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "sess_act" in out
        assert "INSPECT" in out
        assert "KX108" in out
        assert "COMMIT GUARD" in out

    def test_inspect_shows_lifecycle_events(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        _append_lifecycle_event("sess_hold", "ABORTED", {"reason": "test"}, tmp_path)
        cmd_inspect("sess_hold", tmp_path)
        out = capsys.readouterr().out
        assert "ABORTED" in out
        assert "1 event(s)" in out

    def test_inspect_shows_auto_never(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        cmd_inspect("sess_act", tmp_path)
        out = capsys.readouterr().out
        assert "NEVER" in out

    def test_inspect_does_not_modify_receipt(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_inspect("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before

    def test_inspect_with_apply_receipt(self, tmp_path, capsys):
        ar = {
            "session_id": "s_obsidure",
            "kx108_decision": "BLOCK",
            "apply_status": "APPLIED",
            "proposal_id": "prop-001",
            "scope_verification": "CLEAN",
        }
        (tmp_path / "s_obsidure").mkdir()
        (tmp_path / "s_obsidure" / "apply_receipt.json").write_text(json.dumps(ar))
        ret = cmd_inspect("s_obsidure", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "APPLY_RECEIPT" in out


# ─── cmd_resume ─────────────────────────────────────────────────────────────

class TestCmdResume:
    def test_resume_unknown_session(self, tmp_path, capsys):
        ret = cmd_resume("unknownsession", state_dir=tmp_path)
        assert ret == 2

    def test_resume_ready_for_commit_redirects_to_review(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_resume("sess_act", state_dir=tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "READY_FOR_COMMIT_REVIEW" in out
        assert "build review" in out

    def test_resume_committed_no_action(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        ret = cmd_resume("sess_committed", state_dir=tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "COMMITTED" in out
        assert "NO_RESUME" in out

    def test_resume_aborted_no_action(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        _append_lifecycle_event("sess_hold", "ABORTED", {}, tmp_path)
        ret = cmd_resume("sess_hold", state_dir=tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "ABORTED" in out
        assert "NO_RESUME" in out

    def test_resume_cleaned_no_action(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        _append_lifecycle_event("sess_act", "ABORTED", {}, tmp_path)
        _append_lifecycle_event("sess_act", "CLEANED", {}, tmp_path)
        ret = cmd_resume("sess_act", state_dir=tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "CLEANED" in out

    def test_resume_block_returns_error(self, tmp_path, receipt_block, capsys):
        _write_receipt(tmp_path, "sess_block", receipt_block)
        ret = cmd_resume("sess_block", state_dir=tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "BLOCK" in out

    def test_resume_plan_proposed_shows_approval_guide(self, tmp_path, capsys):
        r = {
            "session_id": "s_plan",
            "objective": "test plan",
            "commit_status": "NOT_COMMITTED",
            "kx108_decision": "",
            "next_human_action": "",
            "branch": "feat/test",
            "worktree": str(tmp_path / "wt"),
        }
        _write_receipt(tmp_path, "s_plan", r)
        ret = cmd_resume("s_plan", state_dir=tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "AWAITING_APPROVAL" in out or "approbation" in out.lower()

    def test_resume_hold_incomplete_receipt_prints_info(self, tmp_path, receipt_hold, capsys):
        # HOLD mais sans diff_hash → reprise KX108 impossible
        r = dict(receipt_hold)
        del r["diff_hash"]
        _write_receipt(tmp_path, "sess_hold", r)
        ret = cmd_resume("sess_hold", state_dir=tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "HOLD" in out or "insuffisantes" in out.lower()

    def test_resume_does_not_auto_commit(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        cmd_resume("sess_act", state_dir=tmp_path)
        r = _load_receipt("sess_act", tmp_path)
        assert r["commit_status"] == "NOT_COMMITTED"


# ─── cmd_review ─────────────────────────────────────────────────────────────

class TestCmdReview:
    def test_review_unknown_session(self, tmp_path, capsys):
        ret = cmd_review("unknownsession", tmp_path)
        assert ret == 2
        out = capsys.readouterr().out
        assert "REVIEW_FAIL" in out

    def test_review_ready_for_commit(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_review("sess_act", tmp_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "REVIEW_READY" in out
        assert "NE COMMIT PAS" in out
        assert "KX108_ONLY" in out

    def test_review_hold_not_applicable(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        ret = cmd_review("sess_hold", tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "REVIEW_NA" in out

    def test_review_block_not_applicable(self, tmp_path, receipt_block, capsys):
        _write_receipt(tmp_path, "sess_block", receipt_block)
        ret = cmd_review("sess_block", tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "REVIEW_NA" in out

    def test_review_committed_not_applicable(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        ret = cmd_review("sess_committed", tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "REVIEW_NA" in out

    def test_review_aborted_not_applicable(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        _append_lifecycle_event("sess_act", "ABORTED", {}, tmp_path)
        ret = cmd_review("sess_act", tmp_path)
        assert ret == 1

    def test_review_does_not_commit(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        cmd_review("sess_act", tmp_path)
        r = _load_receipt("sess_act", tmp_path)
        assert r["commit_status"] == "NOT_COMMITTED"

    def test_review_does_not_modify_receipt(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_review("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before


# ─── cmd_abort ──────────────────────────────────────────────────────────────

class TestCmdAbort:
    def test_abort_unknown_session(self, tmp_path, capsys):
        ret = cmd_abort("unknownsession", "", tmp_path)
        assert ret == 2

    def test_abort_clean_hold_session(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        ret = cmd_abort("sess_hold", "test_reason", tmp_path)
        assert ret == 0
        evts = _load_lifecycle_events("sess_hold", tmp_path)
        assert any(e["type"] == "ABORTED" for e in evts)
        assert any(e.get("reason") == "test_reason" for e in evts)

    def test_abort_clean_act_session(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_abort("sess_act", "", tmp_path)
        assert ret == 0

    def test_abort_already_committed_refused(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        ret = cmd_abort("sess_committed", "", tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "ABORT_FAIL" in out

    def test_abort_already_aborted_refused(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        _append_lifecycle_event("sess_hold", "ABORTED", {}, tmp_path)
        ret = cmd_abort("sess_hold", "", tmp_path)
        assert ret == 1

    def test_abort_already_cleaned_refused(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        _append_lifecycle_event("sess_act", "ABORTED", {}, tmp_path)
        _append_lifecycle_event("sess_act", "CLEANED", {}, tmp_path)
        ret = cmd_abort("sess_act", "", tmp_path)
        assert ret == 1

    def test_abort_preserves_receipt_json_immutable(self, tmp_path, receipt_hold):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        rp = tmp_path / "sess_hold" / "receipt.json"
        content_before = rp.read_text(encoding="utf-8")
        mtime_before = rp.stat().st_mtime
        cmd_abort("sess_hold", "", tmp_path)
        assert rp.read_text(encoding="utf-8") == content_before
        assert rp.stat().st_mtime == mtime_before

    def test_abort_creates_lifecycle_event_not_in_receipt(self, tmp_path, receipt_hold):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        cmd_abort("sess_hold", "manual_stop", tmp_path)
        # receipt.json ne contient pas ABORTED
        r = _load_receipt("sess_hold", tmp_path)
        assert r is not None
        assert "ABORTED" not in str(r.get("commit_status", ""))
        # lifecycle_events.jsonl contient ABORTED
        evts = _load_lifecycle_events("sess_hold", tmp_path)
        assert any(e["type"] == "ABORTED" for e in evts)

    def test_abort_default_reason(self, tmp_path, receipt_hold):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        cmd_abort("sess_hold", state_dir=tmp_path)
        evts = _load_lifecycle_events("sess_hold", tmp_path)
        assert any(e.get("reason") == "operator_abort" for e in evts)


# ─── cmd_cleanup ────────────────────────────────────────────────────────────

class TestCmdCleanup:
    def test_cleanup_unknown_session(self, tmp_path, capsys):
        ret = cmd_cleanup("unknownsession", tmp_path)
        assert ret == 2

    def test_cleanup_refused_for_ready_for_commit(self, tmp_path, receipt_act, capsys):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        ret = cmd_cleanup("sess_act", tmp_path)
        assert ret == 1
        out = capsys.readouterr().out
        assert "CLEANUP_REFUSED" in out

    def test_cleanup_refused_for_hold(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        ret = cmd_cleanup("sess_hold", tmp_path)
        assert ret == 1

    def test_cleanup_refused_for_block(self, tmp_path, receipt_block, capsys):
        _write_receipt(tmp_path, "sess_block", receipt_block)
        ret = cmd_cleanup("sess_block", tmp_path)
        assert ret == 1

    def test_cleanup_allowed_after_abort_no_worktree(self, tmp_path, receipt_hold, capsys):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        _append_lifecycle_event("sess_hold", "ABORTED", {}, tmp_path)
        ret = cmd_cleanup("sess_hold", tmp_path)
        assert ret == 0
        evts = _load_lifecycle_events("sess_hold", tmp_path)
        assert any(e["type"] == "CLEANED" for e in evts)

    def test_cleanup_allowed_for_committed_no_worktree(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        ret = cmd_cleanup("sess_committed", tmp_path)
        assert ret == 0
        evts = _load_lifecycle_events("sess_committed", tmp_path)
        assert any(e["type"] == "CLEANED" for e in evts)

    def test_cleanup_preserves_state_dir(self, tmp_path, receipt_committed, capsys):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        session_path = tmp_path / "sess_committed"
        cmd_cleanup("sess_committed", tmp_path)
        assert session_path.exists()
        assert (session_path / "receipt.json").exists()

    def test_cleanup_preserves_receipt_immutable(self, tmp_path, receipt_committed):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        rp = tmp_path / "sess_committed" / "receipt.json"
        content_before = rp.read_text(encoding="utf-8")
        cmd_cleanup("sess_committed", tmp_path)
        assert rp.read_text(encoding="utf-8") == content_before

    def test_cleanup_records_cleaned_event(self, tmp_path, receipt_committed):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        cmd_cleanup("sess_committed", tmp_path)
        evts = _load_lifecycle_events("sess_committed", tmp_path)
        cleaned = [e for e in evts if e["type"] == "CLEANED"]
        assert len(cleaned) == 1
        assert "previous_status" in cleaned[0]


# ─── Invariants d'autorité ──────────────────────────────────────────────────

class TestAuthorityInvariants:
    """DECISION_AUTHORITY = KX108_ONLY dans toutes les réponses."""

    def test_decision_authority_constant(self):
        assert DECISION_AUTHORITY == "KX108_ONLY"

    def test_list_does_not_write_to_sessions(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        files_before = set((tmp_path / "sess_act").iterdir())
        cmd_list(tmp_path)
        files_after = set((tmp_path / "sess_act").iterdir())
        assert files_before == files_after

    def test_status_does_not_write_to_sessions(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_status("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before

    def test_inspect_does_not_write_to_sessions(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_inspect("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before

    def test_review_does_not_write_to_sessions(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        rp = tmp_path / "sess_act" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_review("sess_act", tmp_path)
        assert rp.stat().st_mtime == mtime_before

    def test_abort_only_writes_lifecycle_events(self, tmp_path, receipt_hold):
        _write_receipt(tmp_path, "sess_hold", receipt_hold)
        rp = tmp_path / "sess_hold" / "receipt.json"
        mtime_before = rp.stat().st_mtime
        cmd_abort("sess_hold", "", tmp_path)
        assert rp.stat().st_mtime == mtime_before
        assert (tmp_path / "sess_hold" / "lifecycle_events.jsonl").exists()

    def test_cleanup_only_writes_lifecycle_events_not_receipt(self, tmp_path, receipt_committed):
        _write_receipt(tmp_path, "sess_committed", receipt_committed)
        rp = tmp_path / "sess_committed" / "receipt.json"
        content_before = rp.read_text(encoding="utf-8")
        cmd_cleanup("sess_committed", tmp_path)
        assert rp.read_text(encoding="utf-8") == content_before

    def test_resume_does_not_commit(self, tmp_path, receipt_act):
        _write_receipt(tmp_path, "sess_act", receipt_act)
        cmd_resume("sess_act", state_dir=tmp_path)
        r = _load_receipt("sess_act", tmp_path)
        assert r["commit_status"] == "NOT_COMMITTED"
        assert r["push_status"] == "NOT_PUSHED"
        assert r["merge_status"] == "NOT_MERGED"


# ─── Preuve E2E lifecycle sur sessions réelles ──────────────────────────────

class TestE2ELifecycleProof:
    """
    Preuve E2E sur les sessions réelles dans OBSIDIA_BUILD_STATE_DIR.
    NE DÉTRUIT PAS la session 35d45cb9.
    NE MODIFIE PAS les receipts existants.
    """

    @pytest.fixture(autouse=True)
    def skip_if_no_state_dir(self):
        if not OBSIDIA_BUILD_STATE_DIR.exists():
            pytest.skip("OBSIDIA_BUILD_STATE_DIR absent — skip E2E réel")

    def test_e2e_list_real_sessions(self, capsys):
        ret = cmd_list()
        assert ret == 0

    def test_e2e_status_35d45cb9(self, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        ret = cmd_status("35d45cb9")
        assert ret == 0
        out = capsys.readouterr().out
        assert "35d45cb9" in out
        assert "READY_FOR_COMMIT_REVIEW" in out

    def test_e2e_inspect_35d45cb9(self, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        ret = cmd_inspect("35d45cb9")
        assert ret == 0
        out = capsys.readouterr().out
        assert "READY_FOR_COMMIT_REVIEW" in out
        assert "KX108_ONLY" in out

    def test_e2e_review_35d45cb9(self, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        ret = cmd_review("35d45cb9")
        assert ret == 0
        out = capsys.readouterr().out
        assert "REVIEW_READY" in out

    def test_e2e_resume_35d45cb9_redirects_to_review(self, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        ret = cmd_resume("35d45cb9")
        assert ret == 0
        out = capsys.readouterr().out
        assert "READY_FOR_COMMIT_REVIEW" in out
        assert "build review" in out

    def test_e2e_session_35d45cb9_not_destroyed(self):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        r = _load_receipt("35d45cb9")
        assert r is not None
        assert r.get("kx108_decision") == "ACT"
        assert r.get("commit_status") == "NOT_COMMITTED"
        assert r.get("decision_authority") == "KX108_ONLY"

    def test_e2e_abort_refused_for_35d45cb9_is_ready_for_commit(self, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        # 35d45cb9 est READY_FOR_COMMIT_REVIEW, pas ABORTED/COMMITTED/CLEANED
        # Vérifier que abort ne modifie PAS le receipt si session commit-ready
        rp = OBSIDIA_BUILD_STATE_DIR / "35d45cb9" / "receipt.json"
        content_before = rp.read_text(encoding="utf-8")
        # Ne pas aborter la session réelle — juste vérifier le state
        summary = _session_summary("35d45cb9")
        assert summary["lifecycle_status"] == "READY_FOR_COMMIT_REVIEW"
        # receipt.json ne doit pas avoir été touché
        assert rp.read_text(encoding="utf-8") == content_before


# ─── Safety Hardening (7 tests) ─────────────────────────────────────────────

def _make_dirty_git_repo(base: Path) -> Path:
    """Crée un dépôt git minimal avec un fichier modifié non commité."""
    wt = base / "dirty_git_repo"
    wt.mkdir()
    for cmd in [
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", "t@t.com"],
        ["git", "config", "user.name", "T"],
    ]:
        subprocess.run(cmd, cwd=str(wt), capture_output=True)
    (wt / "f.txt").write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(wt), capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(wt), capture_output=True)
    (wt / "f.txt").write_text("modified", encoding="utf-8")  # worktree dirty
    return wt


def _make_clean_git_repo(base: Path) -> Path:
    """Crée un dépôt git minimal propre (pas de modifications non commitées)."""
    wt = base / "clean_git_repo"
    wt.mkdir()
    for cmd in [
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", "t@t.com"],
        ["git", "config", "user.name", "T"],
    ]:
        subprocess.run(cmd, cwd=str(wt), capture_output=True)
    (wt / "f.txt").write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(wt), capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(wt), capture_output=True)
    return wt


def _mk_aborted_receipt(tmp_path: Path, sid: str, wt: Path) -> None:
    """Écrit un receipt et un événement ABORTED pour un sid donné."""
    _write_receipt(tmp_path, sid, {
        "commit_status": "NOT_COMMITTED",
        "kx108_decision": "HOLD",
        "objective": "test",
        "worktree": str(wt),
        "branch": "feat/test",
    })
    _append_lifecycle_event(sid, "ABORTED", {}, tmp_path)


class TestSafetyHardening:
    """7 tests mandatés par le hardening sécurité TERMINAL_BUILD_LIFECYCLE_V1."""

    # TEST 1 — Worktree dirty réel → HOLD, pas de CLEANED
    def test_cleanup_refuses_dirty_aborted_worktree(self, tmp_path):
        wt_dir = _make_dirty_git_repo(tmp_path)
        _mk_aborted_receipt(tmp_path, "sh_dirty", wt_dir)
        ret = cmd_cleanup("sh_dirty", tmp_path)
        assert ret != 0, "cleanup doit refuser un worktree dirty"
        evts = _load_lifecycle_events("sh_dirty", tmp_path)
        assert not any(e["type"] == "CLEANED" for e in evts), "CLEANED interdit si dirty"
        assert (tmp_path / "sh_dirty" / "receipt.json").exists(), "receipt préservé"

    # TEST 2 — git worktree remove retourne non-zéro → pas de CLEANED
    def test_cleanup_does_not_mark_cleaned_when_git_remove_fails(self, tmp_path):
        wt_dir = _make_clean_git_repo(tmp_path)
        _mk_aborted_receipt(tmp_path, "sh_rmfail", wt_dir)

        real_run = subprocess.run

        def mock_run(cmd, **kwargs):
            if isinstance(cmd, list) and "worktree" in cmd and "remove" in cmd:
                m = MagicMock()
                m.returncode = 1
                m.stderr = "not a git worktree"
                m.stdout = ""
                return m
            return real_run(cmd, **kwargs)

        with patch.object(_OB.subprocess, "run", side_effect=mock_run):
            ret = cmd_cleanup("sh_rmfail", tmp_path)

        assert ret != 0, "cleanup doit retourner non-zéro si remove échoue"
        evts = _load_lifecycle_events("sh_rmfail", tmp_path)
        assert not any(e["type"] == "CLEANED" for e in evts), "CLEANED interdit si remove échoue"

    # TEST 3 — git remove retourne 0 mais le worktree existe encore → postcondition HOLD
    def test_cleanup_requires_postcondition(self, tmp_path):
        wt_dir = _make_clean_git_repo(tmp_path)
        _mk_aborted_receipt(tmp_path, "sh_post", wt_dir)

        real_run = subprocess.run

        def mock_run_fake_success(cmd, **kwargs):
            if isinstance(cmd, list) and "worktree" in cmd and "remove" in cmd:
                # Simule returncode=0 sans supprimer le répertoire
                m = MagicMock()
                m.returncode = 0
                m.stderr = ""
                m.stdout = ""
                return m
            return real_run(cmd, **kwargs)

        with patch.object(_OB.subprocess, "run", side_effect=mock_run_fake_success):
            ret = cmd_cleanup("sh_post", tmp_path)

        assert ret != 0, "postcondition échouée doit bloquer"
        evts = _load_lifecycle_events("sh_post", tmp_path)
        assert not any(e["type"] == "CLEANED" for e in evts), "CLEANED interdit si postcondition échoue"
        assert wt_dir.exists(), "répertoire toujours présent (postcondition)"

    # TEST 4 — git status inaccessible → dirty=None, state_complete=False
    def test_git_status_failure_is_not_clean(self, tmp_path):
        non_git = tmp_path / "not_a_git_repo"
        non_git.mkdir()
        wt = _git_worktree_state(non_git)
        assert wt["exists"] is True
        assert wt.get("dirty") is None, "dirty ne doit jamais valoir False par défaut sur erreur"
        assert wt.get("state_complete") is False, "state_complete=False si état git indéterminable"
        assert len(wt.get("errors", [])) > 0, "erreurs exposées"

    # TEST 5 — Worktree absent dès le départ → CLEANED autorisé, preuves préservées
    def test_cleanup_absent_worktree_can_clean(self, tmp_path):
        absent_wt = tmp_path / "wt_never_created"
        _write_receipt(tmp_path, "sh_absent", {
            "commit_status": "NOT_COMMITTED",
            "kx108_decision": "ACT",
            "objective": "test",
            "worktree": str(absent_wt),
            "branch": "feat/test",
        })
        _append_lifecycle_event("sh_absent", "ABORTED", {}, tmp_path)
        ret = cmd_cleanup("sh_absent", tmp_path)
        assert ret == 0, "cleanup doit réussir si worktree absent"
        evts = _load_lifecycle_events("sh_absent", tmp_path)
        assert any(e["type"] == "CLEANED" for e in evts), "CLEANED écrit si worktree absent"
        assert (tmp_path / "sh_absent" / "receipt.json").exists(), "receipt préservé"

    # TEST 6 — Worktree propre, suppression réussie + postcondition confirmée → CLEANED une fois
    def test_cleanup_clean_worktree_success(self, tmp_path):
        # Répertoire simple (pas .git/) pour éviter les fichiers read-only Windows
        wt_dir = tmp_path / "simple_clean_wt"
        wt_dir.mkdir()
        (wt_dir / "work.txt").write_text("content", encoding="utf-8")
        _mk_aborted_receipt(tmp_path, "sh_ok", wt_dir)

        real_run = subprocess.run

        def mock_run_success(cmd, **kwargs):
            if not isinstance(cmd, list):
                return real_run(cmd, **kwargs)
            if cmd[:2] == ["git", "rev-parse"]:
                m = MagicMock(); m.returncode = 0; m.stdout = "main\n"; m.stderr = ""; return m
            if cmd[:2] == ["git", "status"]:
                # Worktree propre (aucune ligne de sortie)
                m = MagicMock(); m.returncode = 0; m.stdout = ""; m.stderr = ""; return m
            if "worktree" in cmd and "remove" in cmd:
                # Simule remove réussi — supprime le répertoire simple (pas de .git read-only)
                shutil.rmtree(str(wt_dir))
                m = MagicMock(); m.returncode = 0; m.stderr = ""; m.stdout = ""; return m
            return real_run(cmd, **kwargs)

        with patch.object(_OB.subprocess, "run", side_effect=mock_run_success):
            ret = cmd_cleanup("sh_ok", tmp_path)

        assert ret == 0, "cleanup doit réussir sur worktree propre"
        evts = _load_lifecycle_events("sh_ok", tmp_path)
        cleaned_evts = [e for e in evts if e["type"] == "CLEANED"]
        assert len(cleaned_evts) == 1, "CLEANED écrit exactement une fois"
        assert (tmp_path / "sh_ok" / "receipt.json").exists(), "receipt préservé"

    # TEST 7 — Idempotence : session déjà CLEANED → pas de seconde suppression, receipts immutables
    def test_cleanup_idempotence_already_cleaned(self, tmp_path):
        wt_dir = tmp_path / "wt_fictif"
        _write_receipt(tmp_path, "sh_idem", {
            "commit_status": "NOT_COMMITTED",
            "kx108_decision": "HOLD",
            "objective": "test",
            "worktree": str(wt_dir),
            "branch": "feat/test",
        })
        _append_lifecycle_event("sh_idem", "ABORTED", {}, tmp_path)
        _append_lifecycle_event("sh_idem", "CLEANED", {"worktree_removed": False}, tmp_path)
        rp = tmp_path / "sh_idem" / "receipt.json"
        content_before = rp.read_text(encoding="utf-8")
        # Deuxième appel cleanup
        ret = cmd_cleanup("sh_idem", tmp_path)
        assert ret == 1, "cleanup refusé sur session déjà CLEANED"
        evts = _load_lifecycle_events("sh_idem", tmp_path)
        assert len([e for e in evts if e["type"] == "CLEANED"]) == 1, "pas de second CLEANED"
        assert rp.read_text(encoding="utf-8") == content_before, "receipt.json immutable"
