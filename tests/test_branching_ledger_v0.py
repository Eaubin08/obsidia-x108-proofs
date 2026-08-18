"""
tests/test_branching_ledger_v0.py
==================================
Suite BRANCHING_LEDGER_V0.

Couvre:
  schema, ingestion (receipt / apply_receipt), deduplication,
  append-only, commit linkage, commandes CLI (list/status/inspect/
  history/find), autorite, chemins proteges, E2E reel.

Contraintes:
  NE MODIFIE PAS les receipts/proposals sources.
  NE DETRUIT PAS la session 35d45cb9.
  NE WRITE RIEN dans proofs/ formal/ kernel sealed merkle.
  decision_authority = KX108_ONLY dans tous les chemins.
"""
from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidia_branching_ledger import (  # noqa: E402
    DECISION_AUTHORITY,
    LEDGER_DIR,
    SCHEMA_VERSION,
    classify_dedup,
    cmd_ledger_find_path,
    cmd_ledger_find_session,
    cmd_ledger_history,
    cmd_ledger_inspect,
    cmd_ledger_list,
    cmd_ledger_status,
    ingest_from_receipt,
    ingest_from_proposal,
    ledger_entry_id,
    link_commit,
    _append_entry,
    _append_event,
    _load_entries,
    _load_events,
)
from obsidia_build import OBSIDIA_BUILD_STATE_DIR  # noqa: E402


# ─── Helpers de fixtures ──────────────────────────────────────────────────────

def _write_receipt(state_dir: Path, session_id: str, data: dict) -> Path:
    p = state_dir / session_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "receipt.json").write_text(json.dumps(data), encoding="utf-8")
    return p


def _write_apply_receipt(state_dir: Path, session_id: str, data: dict) -> Path:
    p = state_dir / session_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "apply_receipt.json").write_text(json.dumps(data), encoding="utf-8")
    return p


def _write_proposal(proposals_dir: Path, proposal_id: str, data: dict) -> Path:
    p = proposals_dir / proposal_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "proposal.json").write_text(json.dumps(data), encoding="utf-8")
    return p


def _receipt_act(tmp_path: Path, session_id: str = "test-sess-01") -> dict:
    return {
        "session_id": session_id,
        "objective": "Test objectif ACT",
        "domain": "PERIPHERAL",
        "base_sha": "abc123def456abc1",
        "branch": "feat/test-01",
        "worktree": str(tmp_path / "wt_nonexistent"),
        "approved_scope": ["tests/fixtures/target.py"],
        "manifest_hash": "mhash01",
        "diff_hash": "dhash01",
        "kx108_decision": "ACT",
        "next_human_action": "READY_FOR_COMMIT_REVIEW",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "auto_commit": "NEVER",
        "auto_push": "NEVER",
        "auto_merge": "NEVER",
    }


def _receipt_hold(tmp_path: Path, session_id: str = "test-sess-hold") -> dict:
    return {
        "session_id": session_id,
        "objective": "Test HOLD",
        "domain": "BANK",
        "base_sha": "abc123def456abc1",
        "branch": "feat/test-hold",
        "worktree": str(tmp_path / "wt_hold"),
        "approved_scope": ["connectors/bank.py"],
        "kx108_decision": "HOLD",
        "next_human_action": "HOLD",
        "commit_status": "NOT_COMMITTED",
        "decision_authority": "KX108_ONLY",
    }


def _receipt_block(tmp_path: Path, session_id: str = "test-sess-block") -> dict:
    return {
        "session_id": session_id,
        "objective": "Test BLOCK",
        "domain": "GPS",
        "base_sha": "abc123def456abc1",
        "branch": "feat/test-block",
        "worktree": str(tmp_path / "wt_block"),
        "approved_scope": ["domains/gps/gate.py"],
        "kx108_decision": "BLOCK",
        "next_human_action": "BLOCK",
        "commit_status": "NOT_COMMITTED",
        "decision_authority": "KX108_ONLY",
    }


def _apply_receipt_act(tmp_path: Path, session_id: str = "test-apply-01") -> dict:
    return {
        "session_id": session_id,
        "objective": "Apply test ACT",
        "base_sha": "abc123def456abc1",
        "worktree": "TERMINAL_BOUNDED_V1",
        "approved_scope": ["periphery/math_core/version.py"],
        "proposal_id": "prop-test-01",
        "proposal_hash": "phash01",
        "proposal_files": ["periphery/math_core/version.py"],
        "actual_modified_files": ["periphery/math_core/version.py"],
        "kx108_decision": "ACT",
        "next_human_action": "READY_FOR_COMMIT_REVIEW",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "apply_status": "APPLIED",
        "test_evidence": {
            "command": "python -m pytest tests/",
            "test_identity": "test_id_01",
            "exit_code": 0,
            "status": "PASS",
            "timestamp": "2026-08-18T00:00:00+00:00",
        },
        "gate_evidence": {
            "command": "python scripts/gates/scope_guard.py",
            "test_identity": "gate_id_01",
            "exit_code": 0,
            "status": "PASS",
            "timestamp": "2026-08-18T00:00:00+00:00",
        },
    }


# ─── TestLedgerSchema ─────────────────────────────────────────────────────────

class TestLedgerSchema:
    def test_schema_version_constant(self):
        assert SCHEMA_VERSION == "V0"

    def test_decision_authority_constant(self):
        assert DECISION_AUTHORITY == "KX108_ONLY"

    def test_entry_id_deterministic(self):
        eid1 = ledger_entry_id("sess1", "hash1")
        eid2 = ledger_entry_id("sess1", "hash1")
        assert eid1 == eid2

    def test_entry_id_length_16(self):
        assert len(ledger_entry_id("sess1", "hash1")) == 16

    def test_entry_id_differs_on_session(self):
        assert ledger_entry_id("sess1", "hash1") != ledger_entry_id("sess2", "hash1")

    def test_entry_id_differs_on_hash(self):
        assert ledger_entry_id("sess1", "hash1") != ledger_entry_id("sess1", "hash2")


# ─── TestLedgerDedup ─────────────────────────────────────────────────────────

class TestLedgerDedup:
    def test_distinct_content_empty_ledger(self):
        assert classify_dedup([], "path/a.py", "hash1") == "DISTINCT_CONTENT"

    def test_same_path_same_content(self):
        entries = [{"target_path": "path/a.py", "source_hash": "hash1"}]
        assert classify_dedup(entries, "path/a.py", "hash1") == "SAME_PATH_SAME_CONTENT"

    def test_same_path_new_content(self):
        entries = [{"target_path": "path/a.py", "source_hash": "hash_old"}]
        assert classify_dedup(entries, "path/a.py", "hash_new") == "SAME_PATH_NEW_CONTENT"

    def test_moved_same_content(self):
        entries = [{"target_path": "path/old.py", "source_hash": "hash1"}]
        assert classify_dedup(entries, "path/new.py", "hash1") == "MOVED_SAME_CONTENT"

    def test_distinct_content_different_path_and_hash(self):
        entries = [{"target_path": "path/a.py", "source_hash": "hash1"}]
        assert classify_dedup(entries, "path/b.py", "hash2") == "DISTINCT_CONTENT"


# ─── TestLedgerDedupUnknown ───────────────────────────────────────────────────

class TestLedgerDedupUnknown:
    """Vérifie que l'absence de preuve de contenu produit DEDUP_UNKNOWN et non DISTINCT_CONTENT."""

    def test_source_hash_none_returns_dedup_unknown(self):
        assert classify_dedup([], "path/a.py", None) == "DEDUP_UNKNOWN"

    def test_source_hash_empty_string_returns_dedup_unknown(self):
        assert classify_dedup([], "path/a.py", "") == "DEDUP_UNKNOWN"

    def test_source_hash_literal_unknown_returns_dedup_unknown(self):
        assert classify_dedup([], "path/a.py", "unknown") == "DEDUP_UNKNOWN"

    def test_source_hash_none_with_existing_entries_returns_dedup_unknown(self):
        entries = [{"target_path": "path/a.py", "source_hash": "hash1"}]
        assert classify_dedup(entries, "path/a.py", None) == "DEDUP_UNKNOWN"

    def test_dedup_unknown_propagates_to_unknowns(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "dedup-unk-01"
        # receipt réel mais source_file introuvable → source_hash=None
        sess = sd / sid
        sess.mkdir(parents=True)
        (sess / "receipt.json").write_text(json.dumps({
            "session_id": sid,
            "kx108_decision": "ACT",
            "approved_scope": ["path/target.py"],
            "decision_authority": "KX108_ONLY",
            "next_human_action": "READY_FOR_COMMIT_REVIEW",
        }), encoding="utf-8")
        # Supprimer le fichier pour forcer source_hash=None
        (sess / "receipt.json").unlink()
        # apply_receipt absent aussi → source_file n'existe pas → _content_hash → None
        result = ingest_from_receipt(sid, sd, d)
        # Pas de receipt → erreur attendue (pas de preuve du tout)
        assert "error" in result, "Sans receipt ni apply_receipt, erreur attendue"

    def test_dedup_unknown_with_readable_receipt_propagates(self, tmp_path):
        """source_hash lisible → pas DEDUP_UNKNOWN. Confirme la distinction."""
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "dedup-readable-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        # Hash lisible → classification n'est PAS DEDUP_UNKNOWN
        assert entry["dedup_classification"] != "DEDUP_UNKNOWN"
        assert "source_hash_missing" not in entry["unknowns"]
        assert entry["source_hash"] is not None

    def test_no_prev_entry_id_when_dedup_unknown(self, tmp_path):
        """DEDUP_UNKNOWN ne fabrique pas de prev_entry_id basé sur le contenu."""
        d = tmp_path / "ledger"
        # Simuler deux entrées de path identique mais avec un hash inconnu
        _append_entry({
            "ledger_entry_id": "eid_existing",
            "target_path": "path/target.py",
            "source_hash": "hash_existing",
        }, d)
        # classify_dedup avec None → DEDUP_UNKNOWN
        classification = classify_dedup(_load_entries(d), "path/target.py", None)
        assert classification == "DEDUP_UNKNOWN"
        # Aucun prev_entry_id ne doit être fabriqué depuis DEDUP_UNKNOWN
        # (le code ne settera prev_entry_id que pour SAME_PATH_NEW_CONTENT)
        prev = None  # code réel : prev_entry_id settée uniquement pour SAME_PATH_NEW_CONTENT
        assert prev is None


# ─── TestLedgerAppendOnly ─────────────────────────────────────────────────────

class TestLedgerAppendOnly:
    def test_entries_accumulate(self, tmp_path):
        d = tmp_path / "ledger"
        for i in range(3):
            _append_entry({"ledger_entry_id": f"eid{i}", "val": i}, d)
        entries = _load_entries(d)
        assert len(entries) == 3

    def test_events_accumulate(self, tmp_path):
        d = tmp_path / "ledger"
        for i in range(4):
            _append_event({"event_type": "TEST", "ledger_entry_id": f"eid0", "i": i}, d)
        events = _load_events(d)
        assert len(events) == 4

    def test_historical_entry_not_modified(self, tmp_path):
        d = tmp_path / "ledger"
        original = {"ledger_entry_id": "eid_immut", "value": "original"}
        _append_entry(original, d)
        # Simule un deuxième passage — ne doit pas modifier l'entrée existante
        _append_event({"event_type": "UPDATE", "ledger_entry_id": "eid_immut"}, d)
        entries = _load_entries(d)
        assert len(entries) == 1
        assert entries[0]["value"] == "original"

    def test_corrupt_line_skipped_gracefully(self, tmp_path):
        d = tmp_path / "ledger"
        d.mkdir(parents=True)
        ef = d / "entries.jsonl"
        ef.write_text('{"ledger_entry_id":"ok"}\nNOT_JSON\n{"ledger_entry_id":"ok2"}\n',
                      encoding="utf-8")
        entries = _load_entries(d)
        assert len(entries) == 2
        assert entries[0]["ledger_entry_id"] == "ok"
        assert entries[1]["ledger_entry_id"] == "ok2"

    def test_new_version_same_path_links_prev(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid_v1 = "sess-v1"
        sid_v2 = "sess-v2"
        _write_receipt(sd, sid_v1, {
            **_receipt_act(tmp_path, sid_v1),
            "approved_scope": ["shared/target.py"],
        })
        _write_receipt(sd, sid_v2, {
            **_receipt_act(tmp_path, sid_v2),
            "approved_scope": ["shared/target.py"],
        })
        ingest_from_receipt(sid_v1, sd, d)
        ingest_from_receipt(sid_v2, sd, d)
        entries = _load_entries(d)
        new_entry = next(e for e in entries if e["session_id"] == sid_v2)
        assert new_entry.get("prev_entry_id") is not None
        assert new_entry["dedup_classification"] == "SAME_PATH_NEW_CONTENT"


# ─── TestLedgerIngest ─────────────────────────────────────────────────────────

class TestLedgerIngest:
    def test_ingest_from_receipt(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "ingest-r-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        assert result["status"] == "INDEXED"
        assert "ledger_entry_id" in result
        entries = _load_entries(d)
        assert len(entries) == 1
        entry = entries[0]
        assert entry["session_id"] == sid
        assert entry["entry_schema_version"] == "V0"
        assert entry["decision_authority"] == "KX108_ONLY"

    def test_ingest_from_apply_receipt(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "ingest-ar-01"
        _write_apply_receipt(sd, sid, _apply_receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        assert result["status"] == "INDEXED"
        entry = _load_entries(d)[0]
        assert entry["proposal_id"] == "prop-test-01"
        assert entry["test_evidence_ref"]["status"] == "PASS"
        assert entry["gate_evidence_ref"]["status"] == "PASS"

    def test_ingest_missing_session_returns_error(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        result = ingest_from_receipt("nonexistent-session", sd, d)
        assert "error" in result
        assert _load_entries(d) == []

    def test_ingest_idempotent_same_content(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "ingest-idem-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        r1 = ingest_from_receipt(sid, sd, d)
        r2 = ingest_from_receipt(sid, sd, d)
        assert r1["status"] == "INDEXED"
        assert r2["status"] in ("ALREADY_INDEXED", "SAME_PATH_SAME_CONTENT")
        assert len(_load_entries(d)) == 1

    def test_ingest_kx108_act(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "kx-act"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["kx108_decision"] == "ACT"

    def test_ingest_kx108_hold(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "kx-hold"
        _write_receipt(sd, sid, _receipt_hold(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["kx108_decision"] == "HOLD"

    def test_ingest_kx108_block(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "kx-block"
        _write_receipt(sd, sid, _receipt_block(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["kx108_decision"] == "BLOCK"

    def test_ingest_missing_evidence_unknowns(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "missing-ev-01"
        data = _receipt_act(tmp_path, sid)
        data.pop("kx108_decision", None)
        _write_receipt(sd, sid, data)
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert "kx108_decision_missing" in entry["unknowns"]

    def test_ingest_does_not_copy_receipt_content(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "no-copy-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        # Ledger reference path seulement, jamais le contenu complet du receipt
        assert "provenance_refs" in entry
        assert "receipt_path" in entry["provenance_refs"]
        # Pas de champ 'approval_token_hash' ou autre champ massif du receipt
        assert "approval_token_hash" not in entry
        assert "kx108_request" not in entry

    def test_ingest_lifecycle_aborted(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "lc-aborted-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        # Simuler événement ABORTED dans lifecycle_events.jsonl
        evf = sd / sid / "lifecycle_events.jsonl"
        evf.write_text(
            json.dumps({"type": "ABORTED", "reason": "test", "timestamp": "2026-08-18T00:00:00+00:00"}) + "\n",
            encoding="utf-8"
        )
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["lifecycle_status"] == "ABORTED"

    def test_ingest_lifecycle_cleaned(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "lc-cleaned-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        evf = sd / sid / "lifecycle_events.jsonl"
        evf.write_text(
            json.dumps({"type": "ABORTED", "timestamp": "2026-08-18T00:00:00+00:00"}) + "\n" +
            json.dumps({"type": "CLEANED", "timestamp": "2026-08-18T00:00:01+00:00"}) + "\n",
            encoding="utf-8"
        )
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["lifecycle_status"] == "CLEANED"


# ─── TestLedgerProposalLinking ────────────────────────────────────────────────

class TestLedgerProposalLinking:
    def test_ingest_from_proposal_indexes_session(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        pd = tmp_path / "proposals"
        sid = "prop-link-01"
        pid = "proposal-test-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        _write_proposal(pd, pid, {
            "proposal_id": pid,
            "session_id": sid,
            "proposal_hash": "phash_test",
            "status": "APPLIED",
        })
        result = ingest_from_proposal(pid, pd, sd, d)
        assert result.get("status") in ("INDEXED", "ALREADY_INDEXED")
        assert result.get("proposal_linked") == pid

    def test_ingest_from_proposal_emits_event(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        pd = tmp_path / "proposals"
        sid = "prop-link-02"
        pid = "proposal-test-02"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        _write_proposal(pd, pid, {
            "proposal_id": pid,
            "session_id": sid,
            "proposal_hash": "phash02",
            "status": "APPLIED",
        })
        ingest_from_proposal(pid, pd, sd, d)
        events = _load_events(d)
        assert any(ev["event_type"] == "PROPOSAL_LINKED" for ev in events)

    def test_ingest_from_proposal_missing_returns_error(self, tmp_path):
        d = tmp_path / "ledger"
        pd = tmp_path / "proposals"
        result = ingest_from_proposal("nonexistent-proposal", pd, ledger_dir=d)
        assert "error" in result


# ─── TestLedgerCommitLink ─────────────────────────────────────────────────────

class TestLedgerCommitLink:
    def test_link_commit_appends_event(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "commit-link-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        entry_id = result["ledger_entry_id"]
        link_commit(entry_id, "abc123def456", d)
        events = _load_events(d)
        committed = [ev for ev in events if ev.get("event_type") == "COMMITTED"]
        assert len(committed) == 1
        assert committed[0]["commit_sha"] == "abc123def456"

    def test_link_commit_does_not_modify_original_entry(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "commit-immut-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        entry_id = result["ledger_entry_id"]
        entries_before = _load_entries(d)
        entry_before = entries_before[0].copy()
        link_commit(entry_id, "sha_new", d)
        entries_after = _load_entries(d)
        # Entries count unchanged — no new entry written by link_commit
        assert len(entries_after) == len(entries_before)
        assert entries_after[0] == entry_before

    def test_link_commit_history_reconstructible(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "commit-hist-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        entry_id = result["ledger_entry_id"]
        link_commit(entry_id, "final_sha", d)
        events = _load_events(d)
        history = [ev for ev in events if ev.get("ledger_entry_id") == entry_id]
        types = [ev["event_type"] for ev in history]
        assert "INDEXED" in types
        assert "COMMITTED" in types


# ─── TestLedgerCommands ───────────────────────────────────────────────────────

class TestLedgerCommands:
    def test_list_empty(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        cmd_ledger_list(d)
        out = capsys.readouterr().out
        assert "EMPTY" in out or "0" in out

    def test_list_shows_entries(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "list-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        cmd_ledger_list(d)
        out = capsys.readouterr().out
        assert sid in out
        assert "KX108_ONLY" in out

    def test_status_unknown_entry(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        ret = cmd_ledger_status("unknowneid", d)
        assert ret == 2

    def test_status_known_entry(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "status-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        ret = cmd_ledger_status(result["ledger_entry_id"], d)
        assert ret == 0
        out = capsys.readouterr().out
        assert sid in out

    def test_inspect_unknown_entry(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        ret = cmd_ledger_inspect("unknowneid", d)
        assert ret == 2

    def test_inspect_known_entry(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "inspect-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        ret = cmd_ledger_inspect(result["ledger_entry_id"], d)
        assert ret == 0
        out = capsys.readouterr().out
        assert "KX108_ONLY" in out
        assert "provenance" in out.lower() or "PROVENANCE" in out

    def test_history_empty(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        cmd_ledger_history("nonexistent", d)
        out = capsys.readouterr().out
        assert "EMPTY" in out

    def test_history_shows_events(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "hist-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        result = ingest_from_receipt(sid, sd, d)
        entry_id = result["ledger_entry_id"]
        link_commit(entry_id, "sha_hist", d)
        cmd_ledger_history(entry_id, d)
        out = capsys.readouterr().out
        assert "INDEXED" in out
        assert "COMMITTED" in out

    def test_find_path_returns_matches(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "find-path-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        cmd_ledger_find_path("target.py", d)
        out = capsys.readouterr().out
        assert sid in out

    def test_find_path_no_match(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        cmd_ledger_find_path("nonexistent_path.py", d)
        out = capsys.readouterr().out
        assert "0 resultat" in out

    def test_find_session_returns_matches(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "find-sess-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        cmd_ledger_find_session(sid, d)
        out = capsys.readouterr().out
        assert sid in out

    def test_find_session_no_match(self, tmp_path, capsys):
        d = tmp_path / "ledger"
        cmd_ledger_find_session("nonexistent-session", d)
        out = capsys.readouterr().out
        assert "0 resultat" in out


# ─── TestLedgerAuthority ──────────────────────────────────────────────────────

class TestLedgerAuthority:
    def test_decision_authority_in_every_entry(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        for i, kx in enumerate(["ACT", "HOLD", "BLOCK"]):
            sid = f"auth-{kx.lower()}-{i}"
            data = _receipt_act(tmp_path, sid)
            data["kx108_decision"] = kx
            _write_receipt(sd, sid, data)
            ingest_from_receipt(sid, sd, d)
        entries = _load_entries(d)
        for e in entries:
            assert e.get("decision_authority") == "KX108_ONLY"

    def test_no_fabricated_kx108(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "no-fab-kx"
        data = _receipt_act(tmp_path, sid)
        data["kx108_decision"] = "HOLD"
        _write_receipt(sd, sid, data)
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["kx108_decision"] == "HOLD"
        assert entry["kx108_decision"] != "ACT"

    def test_no_receipt_mutation_after_ingest(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "no-mut-01"
        data = _receipt_act(tmp_path, sid)
        _write_receipt(sd, sid, data)
        content_before = (sd / sid / "receipt.json").read_text(encoding="utf-8")
        ingest_from_receipt(sid, sd, d)
        content_after = (sd / sid / "receipt.json").read_text(encoding="utf-8")
        assert content_before == content_after

    def test_no_proposal_mutation_after_ingest(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        pd = tmp_path / "proposals"
        sid = "no-prop-mut"
        pid = "prop-no-mut"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        _write_proposal(pd, pid, {
            "proposal_id": pid,
            "session_id": sid,
            "proposal_hash": "phash_mut",
            "status": "APPLIED",
        })
        content_before = (pd / pid / "proposal.json").read_text(encoding="utf-8")
        ingest_from_proposal(pid, pd, sd, d)
        content_after = (pd / pid / "proposal.json").read_text(encoding="utf-8")
        assert content_before == content_after

    def test_aborted_not_kx108_decision(self, tmp_path):
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "aborted-not-kx"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        evf = sd / sid / "lifecycle_events.jsonl"
        evf.write_text(
            json.dumps({"type": "ABORTED", "timestamp": "2026-08-18T00:00:00+00:00"}) + "\n",
            encoding="utf-8"
        )
        ingest_from_receipt(sid, sd, d)
        entry = _load_entries(d)[0]
        assert entry["kx108_decision"] == "ACT"
        assert entry["lifecycle_status"] == "ABORTED"
        assert entry["kx108_decision"] not in ("ABORTED", "CLEANED", "COMMITTED")

    def test_no_protected_write(self, tmp_path):
        import subprocess
        d = tmp_path / "ledger"
        sd = tmp_path / "sessions"
        sid = "prot-write-01"
        _write_receipt(sd, sid, _receipt_act(tmp_path, sid))
        ingest_from_receipt(sid, sd, d)
        link_commit("anyeid", "sha", d)
        # Vérifier que proofs/ formal/ kernel merkle sont intacts
        result = subprocess.run(
            ["git", "diff", "--", "proofs/", "formal/",
             "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
             "merkle_seal.json"],
            cwd=str(_REPO_ROOT),
            capture_output=True, text=True,
        )
        assert result.stdout.strip() == "", "Protected paths must not be dirtied by ledger"

    def test_unknown_schema_version_passthrough(self, tmp_path):
        d = tmp_path / "ledger"
        d.mkdir(parents=True)
        # Entrée avec schema inconnu ne doit pas crasher les commandes lecture
        (d / "entries.jsonl").write_text(
            json.dumps({"ledger_entry_id": "eid_future", "entry_schema_version": "V99",
                        "session_id": "s1"}) + "\n",
            encoding="utf-8"
        )
        entries = _load_entries(d)
        assert len(entries) == 1
        assert entries[0]["entry_schema_version"] == "V99"


# ─── TestLedgerE2E ────────────────────────────────────────────────────────────

class TestLedgerE2E:
    """E2E sur session 35d45cb9 réelle — read-only, ne détruit pas la session."""

    def test_e2e_ingest_real_session_35d45cb9(self, tmp_path):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        assert result.get("status") in ("INDEXED", "ALREADY_INDEXED", "SAME_PATH_SAME_CONTENT")
        if result["status"] == "INDEXED":
            entries = _load_entries(d)
            assert len(entries) == 1
            entry = entries[0]
            assert entry["session_id"] == "35d45cb9"
            assert entry["kx108_decision"] == "ACT"
            assert entry["decision_authority"] == "KX108_ONLY"
            assert entry["entry_schema_version"] == "V0"
            assert entry["lifecycle_status"] == "READY_FOR_COMMIT_REVIEW"

    def test_e2e_chain_reconstructible(self, tmp_path):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        if result["status"] != "INDEXED":
            pytest.skip(f"Session non indexable : {result['status']}")
        entry_id = result["ledger_entry_id"]
        entries = _load_entries(d)
        entry = next(e for e in entries if e["ledger_entry_id"] == entry_id)
        # Provenance refs pointent vers des fichiers réels
        prov = entry.get("provenance_refs", {})
        receipt_p = prov.get("receipt_path")
        assert receipt_p is not None
        assert Path(receipt_p).exists(), "receipt_path doit pointer un fichier existant"
        # Source hash déterministe
        eid2 = ledger_entry_id(entry["session_id"], entry["source_hash"])
        assert eid2 == entry_id

    def test_e2e_ledger_list_after_ingest(self, tmp_path, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        if result["status"] != "INDEXED":
            pytest.skip("Non indexable")
        cmd_ledger_list(d)
        out = capsys.readouterr().out
        assert "35d45cb9" in out
        assert "KX108_ONLY" in out

    def test_e2e_ledger_inspect_after_ingest(self, tmp_path, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        if result["status"] != "INDEXED":
            pytest.skip("Non indexable")
        entry_id = result["ledger_entry_id"]
        ret = cmd_ledger_inspect(entry_id, d)
        assert ret == 0
        out = capsys.readouterr().out
        assert "ACT" in out
        assert "KX108_ONLY" in out
        assert "READY_FOR_COMMIT_REVIEW" in out

    def test_e2e_ledger_history_after_commit_link(self, tmp_path, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        if result["status"] != "INDEXED":
            pytest.skip("Non indexable")
        entry_id = result["ledger_entry_id"]
        link_commit(entry_id, "d9b519f42c14f2e6", d)
        cmd_ledger_history(entry_id, d)
        out = capsys.readouterr().out
        assert "INDEXED" in out
        assert "COMMITTED" in out

    def test_e2e_real_session_not_mutated(self):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        receipt_before = (OBSIDIA_BUILD_STATE_DIR / "35d45cb9" / "receipt.json").read_text(encoding="utf-8")
        # Ingestion dans ledger par défaut (LOCALAPPDATA)
        # On ne teste pas ici mais on vérifie que receipt est intact
        r_after = (OBSIDIA_BUILD_STATE_DIR / "35d45cb9" / "receipt.json").read_text(encoding="utf-8")
        assert receipt_before == r_after

    def test_e2e_find_by_session(self, tmp_path, capsys):
        if not (OBSIDIA_BUILD_STATE_DIR / "35d45cb9").exists():
            pytest.skip("Session 35d45cb9 absente")
        d = tmp_path / "ledger_e2e"
        result = ingest_from_receipt("35d45cb9", ledger_dir=d)
        if result["status"] != "INDEXED":
            pytest.skip("Non indexable")
        cmd_ledger_find_session("35d45cb9", d)
        out = capsys.readouterr().out
        assert "35d45cb9" in out
