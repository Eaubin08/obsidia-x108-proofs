"""
tests/test_batch_selector_v0.py
================================
Suite BATCH_SELECTOR_V0.

Sections couvertes (spec §27-29) :
  A. Ingestion candidats
  B. Eligibilite (fail-closed)
  C. Deduplication (5 classifications)
  D. Dependances / cycles
  E. Batch size / hard max
  F. Selection deterministe
  G. BatchProposal schema
  H. Append-only / immutabilite
  I. Source integrity
  J. CLI routing réel
  K. Autorite
  + Fail-closed §28
  + E2E synthetique §29
  + E2E ledger réel READ_ONLY §30
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidia_batch_selector import (  # noqa: E402
    BATCH_PROPOSED,
    BATCH_HOLD,
    DECISION_AUTHORITY,
    DEFAULT_MAX_BATCH_SIZE,
    DEPENDENCY_CONFIRMED,
    DEPENDENCY_CYCLE,
    DEPENDENCY_PROBABLE,
    DEPENDENCY_UNKNOWN,
    HARD_MAX_BATCH_SIZE,
    NO_DEPENDENCY_KNOWN,
    SELECTOR_VERSION,
    ELIGIBLE,
    HOLD_UNKNOWN,
    INELIGIBLE,
    ALREADY_PROCESSED,
    PROTECTED,
    UNSUPPORTED,
    batch_hash_from_proposal,
    batch_id_from_selection,
    build_candidate,
    build_candidates_from_ledger,
    cmd_batch_candidates,
    cmd_batch_inspect,
    cmd_batch_list,
    cmd_batch_status,
    compute_metrics,
    detect_cycles,
    detect_dependencies,
    propose_batch,
    select_batch,
    _check_eligibility,
    _dedup_candidates,
    _is_protected,
    _load_batch,
    _save_batch,
    _list_batches,
)


# ─── Fixtures helpers ─────────────────────────────────────────────────────────

def _entry(
    eid: str = "eid01",
    path: str = "periphery/module_a.py",
    source_hash: str = "abcd1234ef567890",
    kx108: str = "ACT",
    lifecycle: str = "READY_FOR_COMMIT_REVIEW",
    dedup: str = "DISTINCT_CONTENT",
    unknowns: list | None = None,
    prev: str | None = None,
    domain: str = "PERIPHERAL",
    schema: str = "V0",
) -> dict:
    return {
        "ledger_entry_id": eid,
        "entry_schema_version": schema,
        "target_path": path,
        "source_hash": source_hash,
        "source_type": "receipt",
        "target_domain": domain,
        "session_id": f"sess-{eid}",
        "prev_entry_id": prev,
        "dedup_classification": dedup,
        "lifecycle_status": lifecycle,
        "kx108_decision": kx108,
        "proposal_id": None,
        "proposal_hash": None,
        "risk_flags": [],
        "unknowns": unknowns or [],
    }


# ─── A. Candidate ingestion ───────────────────────────────────────────────────

class TestCandidateIngestion:
    def test_valid_candidate_builds(self):
        e = _entry()
        c = build_candidate(e)
        assert c["candidate_id"] == "eid01"
        assert c["eligibility"] == ELIGIBLE
        assert c["target_path"] == "periphery/module_a.py"

    def test_missing_ledger_dir_returns_empty(self, tmp_path):
        candidates = build_candidates_from_ledger(tmp_path / "nonexistent")
        assert candidates == []

    def test_corrupt_ledger_entry_skipped(self, tmp_path):
        ledger = tmp_path / "ledger"
        ledger.mkdir()
        (ledger / "entries.jsonl").write_text(
            '{"ledger_entry_id":"eid_ok","target_path":"a.py","source_hash":"h1","kx108_decision":"ACT","lifecycle_status":"READY_FOR_COMMIT_REVIEW","dedup_classification":"DISTINCT_CONTENT","unknowns":[],"risk_flags":[]}\nNOT_JSON\n',
            encoding="utf-8"
        )
        candidates = build_candidates_from_ledger(ledger)
        assert len(candidates) == 1
        assert candidates[0]["candidate_id"] == "eid_ok"

    def test_unknown_schema_returns_unsupported(self):
        e = _entry(schema="V99")
        c = build_candidate(e)
        assert c["eligibility"] == UNSUPPORTED

    def test_additional_candidates_injected(self, tmp_path):
        ledger = tmp_path / "empty_ledger"
        extra = [_entry("extra01")]
        candidates = build_candidates_from_ledger(ledger, additional_candidates=extra)
        assert len(candidates) == 1
        assert candidates[0]["candidate_id"] == "extra01"


# ─── B. Eligibility ───────────────────────────────────────────────────────────

class TestEligibility:
    def test_eligible(self):
        e, _ = _check_eligibility(_entry())
        assert e == ELIGIBLE

    def test_protected_proofs(self):
        e, _ = _check_eligibility(_entry(path="proofs/V18/some_file.lean"))
        assert e == PROTECTED

    def test_protected_formal(self):
        e, _ = _check_eligibility(_entry(path="formal/tla/spec.tla"))
        assert e == PROTECTED

    def test_protected_kernel_sealed(self):
        e, _ = _check_eligibility(_entry(
            path="runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs"
        ))
        assert e == PROTECTED

    def test_protected_merkle(self):
        e, _ = _check_eligibility(_entry(path="merkle_seal.json"))
        assert e == PROTECTED

    def test_missing_source_hash_hold(self):
        e, reasons = _check_eligibility(_entry(source_hash=None))
        assert e == HOLD_UNKNOWN
        assert "source_hash_missing" in reasons

    def test_empty_source_hash_hold(self):
        e, _ = _check_eligibility(_entry(source_hash=""))
        assert e == HOLD_UNKNOWN

    def test_unknown_source_hash_hold(self):
        e, _ = _check_eligibility(_entry(source_hash="unknown"))
        assert e == HOLD_UNKNOWN

    def test_missing_provenance_hold(self):
        e, _ = _check_eligibility(_entry(path="UNKNOWN"))
        assert e == HOLD_UNKNOWN

    def test_dedup_unknown_hold(self):
        e, _ = _check_eligibility(_entry(dedup="DEDUP_UNKNOWN"))
        assert e == HOLD_UNKNOWN

    def test_kx108_missing_hold(self):
        entry = _entry()
        entry["kx108_decision"] = None
        e, reasons = _check_eligibility(entry)
        assert e == HOLD_UNKNOWN
        assert "kx108_decision_missing" in reasons

    def test_kx108_block_ineligible(self):
        e, _ = _check_eligibility(_entry(kx108="BLOCK"))
        assert e == INELIGIBLE

    def test_lifecycle_aborted_already_processed(self):
        e, _ = _check_eligibility(_entry(lifecycle="ABORTED"))
        assert e == ALREADY_PROCESSED

    def test_lifecycle_cleaned_already_processed(self):
        e, _ = _check_eligibility(_entry(lifecycle="CLEANED"))
        assert e == ALREADY_PROCESSED

    def test_lifecycle_committed_already_processed(self):
        e, _ = _check_eligibility(_entry(lifecycle="COMMITTED"))
        assert e == ALREADY_PROCESSED

    def test_lifecycle_ready_eligible(self):
        e, _ = _check_eligibility(_entry(lifecycle="READY_FOR_COMMIT_REVIEW"))
        assert e == ELIGIBLE

    def test_unknowns_critical_hold(self):
        e, reasons = _check_eligibility(_entry(unknowns=["kx108_decision_missing", "source_hash_missing"]))
        assert e == HOLD_UNKNOWN

    def test_unknowns_commit_sha_pending_not_blocking(self):
        e, _ = _check_eligibility(_entry(unknowns=["commit_sha_pending"]))
        assert e == ELIGIBLE


# ─── C. Dedup ────────────────────────────────────────────────────────────────

class TestDedupInSelector:
    def test_same_path_same_content_excluded(self):
        candidates = [build_candidate(_entry(dedup="SAME_PATH_SAME_CONTENT"))]
        deduped, excluded = _dedup_candidates(candidates)
        assert len(deduped) == 0
        assert len(excluded) == 1
        assert "DUPLICATE" in excluded[0]["exclusion_reason"]

    def test_same_path_new_content_kept(self):
        candidates = [build_candidate(_entry(dedup="SAME_PATH_NEW_CONTENT"))]
        deduped, excluded = _dedup_candidates(candidates)
        assert len(deduped) == 1
        assert len(excluded) == 0

    def test_moved_same_content_kept(self):
        candidates = [build_candidate(_entry(dedup="MOVED_SAME_CONTENT"))]
        deduped, excluded = _dedup_candidates(candidates)
        assert len(deduped) == 1

    def test_distinct_content_kept(self):
        candidates = [build_candidate(_entry(dedup="DISTINCT_CONTENT"))]
        deduped, _ = _dedup_candidates(candidates)
        assert len(deduped) == 1

    def test_dedup_unknown_excluded_by_eligibility(self):
        # DEDUP_UNKNOWN → HOLD_UNKNOWN (par eligibility) → pas dans selected
        c = build_candidate(_entry(dedup="DEDUP_UNKNOWN"))
        assert c["eligibility"] == HOLD_UNKNOWN

    def test_duplicate_key_excluded(self):
        c1 = build_candidate(_entry("eid01", "a.py", "hash1"))
        c2 = build_candidate(_entry("eid02", "a.py", "hash1"))
        deduped, excluded = _dedup_candidates([c1, c2])
        assert len(deduped) == 1
        assert len(excluded) == 1
        assert excluded[0]["exclusion_reason"] == "DUPLICATE_KEY"


# ─── D. Dependencies ─────────────────────────────────────────────────────────

class TestDependencies:
    def test_no_known_dependency(self):
        c = build_candidate(_entry("eid01"))
        assert c["dependency_status"] == NO_DEPENDENCY_KNOWN

    def test_confirmed_dependency_within_batch(self):
        c1 = build_candidate(_entry("eid01", path="a.py", prev=None))
        c2 = build_candidate(_entry("eid02", path="b.py", prev="eid01"))
        edges = detect_dependencies([c1, c2])
        assert any(e["type"] == DEPENDENCY_CONFIRMED for e in edges)
        assert any(e["from"] == "eid02" and e["to"] == "eid01" for e in edges)

    def test_probable_dependency_outside_batch(self):
        c = build_candidate(_entry("eid02", prev="eid_external"))
        edges = detect_dependencies([c])
        assert any(e["type"] == DEPENDENCY_PROBABLE for e in edges)
        assert "dependency_outside_batch" in c.get("unknowns", [])

    def test_no_dependency_no_prev(self):
        c = build_candidate(_entry("eid01"))
        edges = detect_dependencies([c])
        assert len(edges) == 0

    def test_cycle_detected(self):
        c1 = build_candidate(_entry("eid01", prev="eid02"))
        c2 = build_candidate(_entry("eid02", prev="eid01"))
        edges = detect_dependencies([c1, c2])
        cycles = detect_cycles([c1, c2], edges)
        assert len(cycles) > 0

    def test_dependency_outside_batch_marks_unknown(self):
        c = build_candidate(_entry("eid99", prev="eid_missing"))
        detect_dependencies([c])
        assert "dependency_outside_batch" in c.get("unknowns", [])

    def test_dependency_included_automatically(self, tmp_path):
        ledger = tmp_path / "ledger"
        e1 = _entry("eid01", path="a.py")
        e2 = _entry("eid02", path="b.py", prev="eid01")
        result = propose_batch(
            max_batch_size=5,
            additional_candidates=[e1, e2],
            ledger_dir=ledger,
            selector_dir=tmp_path / "sel",
        )
        sel_ids = [c["candidate_id"] for c in result["selected_entries"]]
        assert "eid01" in sel_ids
        assert "eid02" in sel_ids


# ─── E. Batch size ────────────────────────────────────────────────────────────

class TestBatchSize:
    def test_zero_candidates(self, tmp_path):
        result = propose_batch(
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] == 0
        assert result["status"] == BATCH_HOLD

    def test_one_candidate(self, tmp_path):
        e = _entry("e01")
        result = propose_batch(
            additional_candidates=[e],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] == 1

    def test_exactly_max(self, tmp_path):
        entries = [_entry(f"e{i:02d}", path=f"path/f{i}.py") for i in range(5)]
        result = propose_batch(
            additional_candidates=entries,
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] == 5

    def test_exceeds_max_truncated(self, tmp_path):
        entries = [_entry(f"e{i:02d}", path=f"path/f{i}.py") for i in range(8)]
        result = propose_batch(
            additional_candidates=entries,
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] == 5
        overflow_excl = [
            e for e in result["excluded_entries"]
            if e.get("exclusion_reason") == "EXCEEDS_MAX_BATCH_SIZE"
        ]
        assert len(overflow_excl) == 3

    def test_hard_max_enforcement(self, tmp_path):
        entries = [_entry(f"e{i:02d}", path=f"path/f{i}.py") for i in range(15)]
        result = propose_batch(
            additional_candidates=entries,
            max_batch_size=99,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] <= HARD_MAX_BATCH_SIZE

    def test_no_wildcard_unbounded(self, tmp_path):
        assert HARD_MAX_BATCH_SIZE == 10
        assert DEFAULT_MAX_BATCH_SIZE == 5


# ─── F. Selection déterministe ───────────────────────────────────────────────

class TestSelectionDeterminism:
    def test_same_input_same_output(self, tmp_path):
        entries = [
            _entry("e01", path="a.py"),
            _entry("e02", path="b.py"),
        ]
        r1 = propose_batch(
            additional_candidates=entries,
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        r2 = propose_batch(
            additional_candidates=entries,
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r1["batch_hash"] == r2["batch_hash"]
        assert r1["selected_count"] == r2["selected_count"]

    def test_exclusion_reason_recorded(self, tmp_path):
        entries = [
            _entry("prot01", path="proofs/some.lean"),
            _entry("e01", path="a.py"),
        ]
        result = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        excl_ids = [e["candidate_id"] for e in result["excluded_entries"]]
        assert "prot01" in excl_ids

    def test_hold_reason_recorded(self, tmp_path):
        entries = [
            _entry("hold01", source_hash=None),
        ]
        result = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["hold_count"] == 1
        hold_ids = [e["candidate_id"] for e in result["hold_entries"]]
        assert "hold01" in hold_ids

    def test_selection_reason_recorded(self, tmp_path):
        e = _entry("e01")
        result = propose_batch(
            additional_candidates=[e],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert "e01" in result["selection_reasons"]
        assert result["selection_reasons"]["e01"]


# ─── G. BatchProposal schema ─────────────────────────────────────────────────

class TestBatchProposalSchema:
    def test_required_fields(self, tmp_path):
        result = propose_batch(
            additional_candidates=[_entry("e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        for f in (
            "batch_id", "batch_schema_version", "created_at", "selector_version",
            "objective", "requested_max_size", "actual_size",
            "selected_entries", "hold_entries", "excluded_entries",
            "dependency_edges", "batch_hash", "status",
            "human_approved", "decision_authority", "metrics",
        ):
            assert f in result, f"Champ manquant : {f}"

    def test_batch_hash_deterministic(self, tmp_path):
        e = _entry("e01")
        h1 = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        h2 = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        assert h1 == h2

    def test_batch_hash_differs_on_selection(self, tmp_path):
        h1 = batch_hash_from_proposal(["e01"], ["h1"], [], "", 5)
        h2 = batch_hash_from_proposal(["e02"], ["h2"], [], "", 5)
        assert h1 != h2

    def test_batch_id_deterministic(self):
        b1 = batch_id_from_selection(["e01", "e02"], "obj", 5)
        b2 = batch_id_from_selection(["e02", "e01"], "obj", 5)
        assert b1 == b2  # trié donc identique

    def test_decision_authority_kx108_only(self, tmp_path):
        result = propose_batch(
            additional_candidates=[_entry("e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["decision_authority"] == "KX108_ONLY"

    def test_human_approved_false(self, tmp_path):
        result = propose_batch(
            additional_candidates=[_entry("e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["human_approved"] is False

    def test_selected_refs_match(self, tmp_path):
        entries = [_entry("e01"), _entry("e02", path="b.py")]
        result = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        sel_ids = {e["candidate_id"] for e in result["selected_entries"]}
        assert sel_ids.issubset(set(result["ledger_refs"]))

    def test_metrics_present_and_plausible(self, tmp_path):
        entries = [_entry("e01"), _entry("e02", path="b.py")]
        result = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        m = result["metrics"]
        assert m["candidate_count"] == 2
        assert m["selected_count"] <= m["candidate_count"]
        assert 0.0 <= m["batch_fill_ratio"] <= 2.0
        assert "selection_duration_ms" in m


# ─── H. Append-only / immutabilité ───────────────────────────────────────────

class TestAppendOnly:
    def test_old_proposal_not_overwritten(self, tmp_path):
        sd = tmp_path / "sel"
        entries = [_entry("e01")]
        r1 = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
            objective="first",
        )
        bid1 = r1["batch_id"]
        r2 = propose_batch(
            additional_candidates=[_entry("e02", path="b.py")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
            objective="second",
        )
        bid2 = r2["batch_id"]
        # Les deux batches coexistent
        assert bid1 != bid2
        p1 = _load_batch(bid1, sd)
        assert p1 is not None
        assert p1["objective"] == "first"

    def test_new_selection_creates_new_proposal(self, tmp_path):
        sd = tmp_path / "sel"
        r1 = propose_batch(
            additional_candidates=[_entry("e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        r2 = propose_batch(
            additional_candidates=[_entry("e02", path="b.py")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        assert r1["batch_id"] != r2["batch_id"]
        batches = _list_batches(sd)
        assert len(batches) == 2

    def test_batch_proposal_immutable_after_save(self, tmp_path):
        sd = tmp_path / "sel"
        e = _entry("e01")
        result = propose_batch(
            additional_candidates=[e],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        bid = result["batch_id"]
        loaded_before = _load_batch(bid, sd)
        assert loaded_before is not None
        original_hash = loaded_before["batch_hash"]
        # Simuler une deuxième proposition différente
        propose_batch(
            additional_candidates=[_entry("e02", path="b.py")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        # La première reste intacte
        loaded_after = _load_batch(bid, sd)
        assert loaded_after["batch_hash"] == original_hash


# ─── I. Source integrity ──────────────────────────────────────────────────────

class TestSourceIntegrity:
    def test_ledger_entries_unchanged(self, tmp_path):
        ledger = tmp_path / "ledger"
        ledger.mkdir()
        entry_line = json.dumps({
            "ledger_entry_id": "eid_src",
            "entry_schema_version": "V0",
            "target_path": "a.py",
            "source_hash": "abc123",
            "kx108_decision": "ACT",
            "lifecycle_status": "READY_FOR_COMMIT_REVIEW",
            "dedup_classification": "DISTINCT_CONTENT",
            "unknowns": [],
            "risk_flags": [],
        })
        ef = ledger / "entries.jsonl"
        ef.write_text(entry_line + "\n", encoding="utf-8")
        before = ef.read_text(encoding="utf-8")
        propose_batch(
            ledger_dir=ledger,
            selector_dir=tmp_path / "sel",
        )
        after = ef.read_text(encoding="utf-8")
        assert before == after

    def test_no_subprocess_in_selector(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "subprocess" not in src
        assert "git commit" not in src
        assert "git push" not in src

    def test_no_write_text_in_selector(self):
        import obsidia_batch_selector as _m, re
        src = Path(_m.__file__).read_text(encoding="utf-8")
        # La seule ecriture legale est .write_text() dans _save_batch
        # Elle doit apparaitre exactement une fois
        write_texts = re.findall(r'\.write_text\(', src)
        assert len(write_texts) == 1, (
            f"write_text attendu exactement 1 fois (dans _save_batch), "
            f"trouve: {write_texts}"
        )
        # Aucun subprocess, aucun git commit/push
        assert "subprocess" not in src
        assert "git commit" not in src
        assert "git push" not in src


# ─── J. CLI routing réel ──────────────────────────────────────────────────────

class TestCLIRouting:
    def test_batch_list_cli(self, capsys):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "obsidia_cli.py"), "batch", "list"],
            capture_output=True, text=True,
            cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH" in result.stdout or "EMPTY" in result.stdout

    def test_batch_propose_cli(self, capsys):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "obsidia_cli.py"),
             "batch", "propose", "--max", "2"],
            capture_output=True, text=True,
            cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "batch_id" in result.stdout or "status" in result.stdout

    def test_batch_status_cli_unknown(self, capsys):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "obsidia_cli.py"),
             "batch", "status", "nonexistent_bid"],
            capture_output=True, text=True,
            cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        out = result.stdout
        assert "BATCH_FAIL" in out or "inconnu" in out

    def test_batch_inspect_cli_unknown(self, capsys):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "obsidia_cli.py"),
             "batch", "inspect", "nonexistent_bid"],
            capture_output=True, text=True,
            cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        out = result.stdout
        assert "BATCH_FAIL" in out or "inconnu" in out

    def test_batch_candidates_cli(self, capsys):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "obsidia_cli.py"), "batch", "candidates"],
            capture_output=True, text=True,
            cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0

    def test_batch_status_after_propose(self, tmp_path, capsys):
        """Propose via code, puis status via CLI sur le ledger par défaut."""
        sd = tmp_path / "sel"
        result = propose_batch(
            additional_candidates=[_entry("cli-e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        bid = result["batch_id"]
        import subprocess, sys as _sys, os as _os
        env = dict(_os.environ)
        out = cmd_batch_status(bid, sd)
        assert out == 0

    def test_batch_inspect_after_propose(self, tmp_path, capsys):
        sd = tmp_path / "sel"
        result = propose_batch(
            additional_candidates=[_entry("cli-e02")],
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        bid = result["batch_id"]
        ret = cmd_batch_inspect(bid, sd)
        assert ret == 0
        out = capsys.readouterr().out
        assert "KX108_ONLY" in out
        assert "REVIEW_BATCH_PROPOSAL" in out


# ─── K. Autorité ─────────────────────────────────────────────────────────────

class TestAuthority:
    def test_decision_authority_constant(self):
        assert DECISION_AUTHORITY == "KX108_ONLY"

    def test_can_decide_false(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "CAN_DECIDE_KX108    = FALSE" in src

    def test_can_apply_false(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "CAN_APPLY           = FALSE" in src

    def test_can_commit_false(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "CAN_COMMIT          = FALSE" in src

    def test_can_push_false(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "CAN_PUSH            = FALSE" in src

    def test_can_merge_false(self):
        import obsidia_batch_selector as _m
        src = Path(_m.__file__).read_text(encoding="utf-8")
        assert "CAN_MERGE           = FALSE" in src

    def test_no_kx108_decision_fabricated(self, tmp_path):
        entry_with_hold = _entry("e01", kx108="HOLD")
        result = propose_batch(
            additional_candidates=[entry_with_hold],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        all_entries = result["selected_entries"] + result["excluded_entries"] + result["hold_entries"]
        for e in all_entries:
            assert e.get("kx108_decision") in ("ACT", "HOLD", "BLOCK", None), \
                "KX108 ne doit pas être fabriqué"
        assert result["selected_count"] == 0  # HOLD → non selected

    def test_human_approved_always_false(self, tmp_path):
        result = propose_batch(
            additional_candidates=[_entry("e01")],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["human_approved"] is False


# ─── Fail-closed §28 ─────────────────────────────────────────────────────────

class TestFailClosed:
    def test_ledger_unavailable_returns_empty(self, tmp_path):
        candidates = build_candidates_from_ledger(tmp_path / "does_not_exist")
        assert candidates == []

    def test_corrupt_jsonl_skipped_no_crash(self, tmp_path):
        ledger = tmp_path / "ledger"
        ledger.mkdir()
        (ledger / "entries.jsonl").write_text("NOT_JSON\nNOT_JSON\n", encoding="utf-8")
        candidates = build_candidates_from_ledger(ledger)
        assert candidates == []

    def test_hash_missing_hold_not_eligible(self, tmp_path):
        entries = [_entry("e01", source_hash=None)]
        result = propose_batch(
            additional_candidates=entries,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["selected_count"] == 0
        assert result["hold_count"] == 1

    def test_dependency_resolution_error_hold(self, tmp_path):
        # Entrée avec prev_entry_id pointant vers un ID inexistant → DEPENDENCY_PROBABLE → unknowns
        e = _entry("e01", prev="external_eid")
        candidates = [build_candidate(e)]
        detect_dependencies(candidates)
        assert "dependency_outside_batch" in candidates[0].get("unknowns", [])

    def test_cycle_produces_hold_not_selection(self, tmp_path):
        e1 = _entry("e01", prev="e02")
        e2 = _entry("e02", path="b.py", prev="e01")
        result = propose_batch(
            additional_candidates=[e1, e2],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        # Les candidats en cycle ne doivent pas être dans selected
        sel_ids = {e["candidate_id"] for e in result["selected_entries"]}
        assert "e01" not in sel_ids or "e02" not in sel_ids


# ─── E2E synthétique §29 ─────────────────────────────────────────────────────

class TestE2ESynthetic:
    """
    Jeu de candidats représentatif :
      A.py — eligible
      B.py — depend de A
      C.py — duplicate (SAME_PATH_SAME_CONTENT)
      D.py — source_hash inconnu
      E.py — protected
      F.py — eligible independant
      G.py — dependency outside batch
    """

    def _build_fixture(self) -> list[dict]:
        return [
            _entry("eid_A", path="periphery/A.py", source_hash="hash_A"),
            _entry("eid_B", path="periphery/B.py", source_hash="hash_B", prev="eid_A"),
            _entry("eid_C", path="periphery/A.py", source_hash="hash_A",
                   dedup="SAME_PATH_SAME_CONTENT"),
            _entry("eid_D", path="periphery/D.py", source_hash=None),
            _entry("eid_E", path="proofs/some.lean"),
            _entry("eid_F", path="periphery/F.py", source_hash="hash_F"),
            _entry("eid_G", path="periphery/G.py", source_hash="hash_G",
                   prev="eid_missing_external"),
        ]

    def test_e2e_propose_with_max5(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._build_fixture(),
            max_batch_size=5,
            objective="e2e-test",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        sel_ids = {e["candidate_id"] for e in result["selected_entries"]}
        excl_ids = {e["candidate_id"] for e in result["excluded_entries"]}
        hold_ids = {e["candidate_id"] for e in result["hold_entries"]}

        # A et F éligibles directs
        assert "eid_A" in sel_ids
        assert "eid_F" in sel_ids

        # B dépend de A (dans le batch) → DEPENDENCY_CONFIRMED → eligible
        assert "eid_B" in sel_ids

        # C : SAME_PATH_SAME_CONTENT → exclu (duplicate)
        assert "eid_C" in excl_ids

        # D : source_hash absent → HOLD
        assert "eid_D" in hold_ids

        # E : protected → exclu
        assert "eid_E" in excl_ids

    def test_e2e_explanation_complete(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._build_fixture(),
            max_batch_size=5,
            objective="e2e-explain",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        # Toute entrée est dans exactement une des 3 listes
        all_ids = (
            {e["candidate_id"] for e in result["selected_entries"]} |
            {e["candidate_id"] for e in result["excluded_entries"]} |
            {e["candidate_id"] for e in result["hold_entries"]}
        )
        fixture_ids = {"eid_A", "eid_B", "eid_C", "eid_D", "eid_E", "eid_F", "eid_G"}
        assert fixture_ids == all_ids

    def test_e2e_batch_list_after_propose(self, tmp_path, capsys):
        sd = tmp_path / "sel"
        propose_batch(
            additional_candidates=self._build_fixture(),
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        cmd_batch_list(sd)
        out = capsys.readouterr().out
        assert "BATCH" in out
        assert "KX108_ONLY" in out

    def test_e2e_batch_inspect_after_propose(self, tmp_path, capsys):
        sd = tmp_path / "sel"
        result = propose_batch(
            additional_candidates=self._build_fixture(),
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=sd,
        )
        bid = result["batch_id"]
        ret = cmd_batch_inspect(bid, sd)
        assert ret == 0
        out = capsys.readouterr().out
        assert "eid_A" in out or "SELECTED" in out
        assert "KX108_ONLY" in out

    def test_e2e_metrics_plausible(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._build_fixture(),
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        m = result["metrics"]
        assert m["candidate_count"] == 7
        assert m["selected_count"] <= m["candidate_count"]
        assert m["hold_count"] >= 1  # D au minimum
        assert m["excluded_count"] >= 2  # C + E au minimum


# ─── E2E ledger réel READ_ONLY §30 ───────────────────────────────────────────

class TestE2ERealLedger:
    """Sélection READ-ONLY depuis le Ledger réel.
    Ne crée aucun worktree, aucune PatchProposal Obsidure, aucun apply.
    """

    def test_e2e_real_ledger_propose(self, tmp_path):
        sd = tmp_path / "real_sel"
        result = propose_batch(
            objective="real-e2e-readonly",
            max_batch_size=5,
            selector_dir=sd,
        )
        # La proposition est produite sans crash
        assert "batch_id" in result
        assert result["decision_authority"] == "KX108_ONLY"
        assert result["human_approved"] is False
        assert result["metrics"]["candidate_count"] >= 0

    def test_e2e_real_ledger_list(self, tmp_path, capsys):
        sd = tmp_path / "real_sel"
        propose_batch(
            objective="real-e2e-list",
            max_batch_size=5,
            selector_dir=sd,
        )
        cmd_batch_list(sd)
        out = capsys.readouterr().out
        assert "BATCH" in out

    def test_e2e_real_ledger_no_worktree_created(self, tmp_path):
        sd = tmp_path / "real_sel"
        propose_batch(
            objective="real-e2e-no-wt",
            max_batch_size=5,
            selector_dir=sd,
        )
        # Vérifier qu'aucun worktree n'existe dans le répertoire de travail
        wt_dirs = list(tmp_path.glob("wt_*"))
        assert wt_dirs == [], f"Worktrees non attendus : {wt_dirs}"

    def test_e2e_real_ledger_entries_not_mutated(self, tmp_path):
        import os
        localappdata = os.environ.get("LOCALAPPDATA", "")
        ledger_path = Path(localappdata) / "Obsidia" / "branching_ledger" / "entries.jsonl"
        if not ledger_path.exists():
            pytest.skip("Ledger réel absent")
        content_before = ledger_path.read_text(encoding="utf-8")
        propose_batch(
            objective="real-e2e-immut",
            max_batch_size=5,
            selector_dir=tmp_path / "sel",
        )
        content_after = ledger_path.read_text(encoding="utf-8")
        assert content_before == content_after


# --- TestSelectorDiscoveredStage (PREBUILD_SOURCE_DISCOVERY_V0) ---------------

class TestSelectorDiscoveredStage:
    """Selector doit distinguer une source DISCOVERED (pre-build) d'une
    entree post-build cassee. proposal_id/kx108 absents ne doivent PAS
    a eux seuls declencher un HOLD pour une entree DISCOVERED."""

    def _discovered(self, **overrides) -> dict:
        params = dict(
            eid="disc01",
            path="periphery/discovered_a.py",
            source_hash="disc0000000hash1",
            kx108=None,
            lifecycle="DISCOVERED",
            dedup="DISTINCT_CONTENT",
            unknowns=[],
        )
        # overrides matching _entry()'s own kwargs (path, source_hash, kx108, ...)
        entry_kwargs = {k: v for k, v in overrides.items() if k in params or k in (
            "prev", "domain", "schema",
        )}
        params.update(entry_kwargs)
        entry = _entry(**params)
        # any remaining overrides target raw ledger-entry fields directly
        for k, v in overrides.items():
            if k not in entry_kwargs:
                entry[k] = v
        return entry

    def test_discovered_complete_source_is_eligible(self):
        e = self._discovered()
        status, reasons = _check_eligibility(e)
        assert status == ELIGIBLE, reasons

    def test_discovered_without_proposal_id_not_holding_for_that_alone(self):
        e = self._discovered(proposal_id=None)
        status, reasons = _check_eligibility(e)
        assert status == ELIGIBLE
        assert not any("proposal_id" in r for r in reasons)

    def test_discovered_without_kx108_not_holding_for_that_alone(self):
        e = self._discovered(kx108=None)
        status, reasons = _check_eligibility(e)
        assert status == ELIGIBLE
        assert not any("kx108_decision_missing" in r for r in reasons)

    def test_discovered_missing_hash_still_holds(self):
        e = self._discovered(source_hash=None)
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN
        assert "source_hash_missing" in reasons

    def test_discovered_protected_still_excluded(self):
        e = self._discovered(path="proofs/whatever.py")
        status, reasons = _check_eligibility(e)
        assert status == PROTECTED

    def test_discovered_dedup_unknown_still_holds(self):
        e = self._discovered(dedup="DEDUP_UNKNOWN")
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN
        assert "dedup_unknown" in reasons

    def test_discovered_missing_dependency_holds(self):
        # dependency_outside_batch est injecté dans unknowns par detect_dependencies
        e = self._discovered(unknowns=["dependency_outside_batch"])
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN

    def test_discovered_clear_dependencies_selectable_in_full_flow(self, tmp_path):
        candidates = [build_candidate(self._discovered())]
        result = select_batch(candidates, max_batch_size=5, objective="disc-flow")
        sel_ids = {c["candidate_id"] for c in result["selected"]}
        assert "disc01" in sel_ids

    def test_discovered_kx108_block_still_ineligible(self):
        e = self._discovered(kx108="BLOCK")
        status, reasons = _check_eligibility(e)
        assert status == INELIGIBLE
        assert "kx108_blocked" in reasons

    def test_discovered_kx108_hold_still_holds(self):
        e = self._discovered(kx108="HOLD")
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN
        assert "kx108_hold_status" in reasons

    def test_historical_postbuild_entry_missing_proposal_id_still_holds(self):
        """Non-regression : une entree POST-BUILD (pas DISCOVERED) avec
        proposal_id manquant dans ses unknowns doit toujours etre HOLD."""
        e = _entry(
            eid="post01",
            lifecycle="READY_FOR_COMMIT_REVIEW",
            kx108="ACT",
            unknowns=["proposal_id_missing"],
        )
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN
        assert "unknowns:['proposal_id_missing']" in reasons

    def test_historical_postbuild_entry_missing_kx108_still_holds(self):
        """Non-regression : une entree POST-BUILD sans kx108_decision doit
        toujours HOLD (le kx108 absent n'est acceptable qu'a DISCOVERED)."""
        e = _entry(
            eid="post02",
            lifecycle="READY_FOR_COMMIT_REVIEW",
            kx108=None,
        )
        status, reasons = _check_eligibility(e)
        assert status == HOLD_UNKNOWN
        assert "kx108_decision_missing" in reasons

    def test_discovered_no_authority_leakage(self):
        e = self._discovered()
        status, reasons = _check_eligibility(e)
        assert status == ELIGIBLE
        # ELIGIBLE for batch proposal never implies apply/commit authority
        c = build_candidate(e)
        assert c["eligibility"] == ELIGIBLE
        assert c.get("kx108_decision") is None
        assert c.get("proposal_id") is None
