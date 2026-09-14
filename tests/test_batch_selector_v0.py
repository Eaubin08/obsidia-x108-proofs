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
    DEPENDENCY_UNRESOLVED,
    DEPENDENCY_OUTSIDE_SCOPE,
    SCOPE_GLOBAL,
    SCOPE_EXPLICIT,
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
    build_entry_index_from_ledger,
    cmd_batch_candidates,
    cmd_batch_inspect,
    cmd_batch_list,
    cmd_batch_status,
    compute_metrics,
    compute_execution_order,
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
from obsidia_branching_ledger import link_dependency as _link_dependency  # noqa: E402
from obsidia_branching_ledger import register_source as _register_source  # noqa: E402


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
        # Detection COMPLETE (Tarjan SCC) : les DEUX membres du cycle,
        # pas seulement la cible d'une back-edge.
        assert set(cycles) == {"eid01", "eid02"}

    def test_cycle_three_node_all_held(self):
        a = build_candidate(_entry("cyc_a", prev="cyc_c"))
        b = build_candidate(_entry("cyc_b", path="b.py", prev="cyc_a"))
        c = build_candidate(_entry("cyc_c", path="c.py", prev="cyc_b"))
        edges = detect_dependencies([a, b, c])
        cycles = detect_cycles([a, b, c], edges)
        assert set(cycles) == {"cyc_a", "cyc_b", "cyc_c"}

    def test_self_loop_cyclic(self):
        a = build_candidate(_entry("self_a"))
        edges = [{"from": "self_a", "to": "self_a", "type": DEPENDENCY_CONFIRMED, "reason": "test"}]
        cycles = detect_cycles([a], edges)
        assert cycles == ["self_a"]

    def test_acyclic_chain_no_cycles(self):
        a = build_candidate(_entry("chain_a", prev="chain_b"))
        b = build_candidate(_entry("chain_b", path="b.py", prev="chain_c"))
        c = build_candidate(_entry("chain_c", path="c.py"))
        edges = detect_dependencies([a, b, c])
        cycles = detect_cycles([a, b, c], edges)
        assert cycles == []

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
        # HOLD COMPLET : aucun des deux membres du cycle ne doit rester
        # selectionne (Tarjan SCC — pas seulement un noeud).
        sel_ids = {e["candidate_id"] for e in result["selected_entries"]}
        assert "e01" not in sel_ids
        assert "e02" not in sel_ids
        hold_ids = {e["candidate_id"] for e in result["hold_entries"]}
        assert "e01" in hold_ids
        assert "e02" in hold_ids
        for e in result["hold_entries"]:
            if e["candidate_id"] in ("e01", "e02"):
                assert "DEPENDENCY_CYCLE" in e["hold_reason"]


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


# --- TestExplicitScope (IMPLEMENT_SCOPED_BATCH_AND_DEPENDENCY_REFS_V0) --------

class TestExplicitScope:
    """Portee explicite de candidats : GLOBAL != EXPLICIT_ENTRY_IDS,
    aucune fuite de residu Ledger hors de la portee demandee."""

    def _pool(self):
        return [
            _entry(eid="scp_a", path="periphery/scp_a.py", source_hash="haaaaaaaaaaaaaaa"),
            _entry(eid="scp_b", path="periphery/scp_b.py", source_hash="hbbbbbbbbbbbbbbb"),
            _entry(eid="scp_c", path="periphery/scp_c.py", source_hash="hccccccccccccccc"),
            _entry(eid="scp_d", path="periphery/scp_d.py", source_hash="hddddddddddddddd"),
            _entry(eid="scp_e", path="periphery/scp_e.py", source_hash="heeeeeeeeeeeeeee"),
        ]

    def test_global_mode_unchanged_default(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["candidate_scope_mode"] == SCOPE_GLOBAL
        assert result["candidate_entry_ids"] is None
        assert result["candidate_scope_hash"] is None
        assert result["candidate_count"] == 5

    def test_explicit_scope_restricts_candidates_no_leakage(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "scp_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["candidate_scope_mode"] == SCOPE_EXPLICIT
        assert result["candidate_count"] == 2
        all_ids = (
            {c["candidate_id"] for c in result["selected_entries"]}
            | {c["candidate_id"] for c in result["hold_entries"]}
            | {c["candidate_id"] for c in result["excluded_entries"]}
        )
        assert all_ids <= {"scp_a", "scp_b"}
        assert "scp_c" not in all_ids
        assert "scp_d" not in all_ids
        assert "scp_e" not in all_ids

    def test_selected_subset_of_explicit_scope(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "scp_b", "scp_c"],
            max_batch_size=5,
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        selected_ids = {c["candidate_id"] for c in result["selected_entries"]}
        assert selected_ids <= {"scp_a", "scp_b", "scp_c"}

    def test_explicit_scope_unknown_id_fails_closed(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "does_not_exist"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["scope_error"] is not None
        assert "UNKNOWN_CANDIDATE_ENTRY_ID" in result["scope_error"]
        assert result["candidate_count"] == 0
        assert result["selected_count"] == 0
        assert result["status"] == BATCH_HOLD

    def test_explicit_scope_empty_list_fails_closed(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=[],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["scope_error"] == "EMPTY_EXPLICIT_SCOPE"
        assert result["candidate_count"] == 0
        assert result["status"] == BATCH_HOLD

    def test_explicit_scope_duplicate_ids_deterministic(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "scp_a", "scp_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["candidate_entry_ids"] == ["scp_a", "scp_b"]
        assert result["candidate_count"] == 2

    def test_explicit_scope_hash_order_independent(self, tmp_path):
        r1 = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "scp_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        r2 = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_b", "scp_a"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r1["candidate_scope_hash"] == r2["candidate_scope_hash"]
        assert r1["candidate_scope_hash"] is not None

    def test_scope_hash_differs_from_batch_hash(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a", "scp_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["candidate_scope_hash"] != result["batch_hash"]

    def test_explicit_scope_human_approved_and_authority(self, tmp_path):
        result = propose_batch(
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_a"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["human_approved"] is False
        assert result["decision_authority"] == DECISION_AUTHORITY

    def test_build_candidates_from_ledger_scoped_matches_propose(self, tmp_path):
        candidates = build_candidates_from_ledger(
            ledger_dir=tmp_path / "empty",
            additional_candidates=self._pool(),
            candidate_entry_ids=["scp_c"],
        )
        assert len(candidates) == 1
        assert candidates[0]["candidate_id"] == "scp_c"


# --- TestDependencyRefsScope (dependency_refs consumed by Selector) ----------

class TestDependencyRefsScope:
    """dependency_refs (champ Ledger + evenements DEPENDENCY_LINKED) sont
    desormais consommes par detect_dependencies, resolus contre l'univers
    complet du Ledger, distinguant confirmed / outside-scope / unresolved."""

    def _pair(self, a_refs=None, b_refs=None):
        a = _entry(eid="dep_a", path="periphery/dep_a.py", source_hash="da00000000000001")
        b = _entry(eid="dep_b", path="periphery/dep_b.py", source_hash="db00000000000002")
        if a_refs is not None:
            a["dependency_refs"] = a_refs
        if b_refs is not None:
            b["dependency_refs"] = b_refs
        return a, b

    def test_dependency_ref_confirmed_in_scope(self, tmp_path):
        a, b = self._pair(a_refs=["dep_b"])
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_a", "dep_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        edges = result["dependency_edges"]
        assert any(
            e["from"] == "dep_a" and e["to"] == "dep_b" and e["type"] == DEPENDENCY_CONFIRMED
            for e in edges
        )
        selected_ids = {c["candidate_id"] for c in result["selected_entries"]}
        assert "dep_a" in selected_ids
        assert "dep_b" in selected_ids

    def test_dependency_ref_resolves_via_target_path(self, tmp_path):
        a, b = self._pair(a_refs=["periphery/dep_b.py"])
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_a", "dep_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        edges = result["dependency_edges"]
        assert any(e["from"] == "dep_a" and e["to"] == "dep_b" for e in edges)

    def test_dependency_ref_outside_scope_holds(self, tmp_path):
        a, b = self._pair(a_refs=["dep_b"])
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_a"],  # dep_b existe mais hors portee
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        hold_ids = {c["candidate_id"] for c in result["hold_entries"]}
        assert "dep_a" in hold_ids
        held = next(c for c in result["hold_entries"] if c["candidate_id"] == "dep_a")
        assert DEPENDENCY_OUTSIDE_SCOPE in held["hold_reason"]

    def test_dependency_ref_unresolved_holds(self, tmp_path):
        a, b = self._pair(a_refs=["periphery/does_not_exist_anywhere.py"])
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_a", "dep_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        hold_ids = {c["candidate_id"] for c in result["hold_entries"]}
        assert "dep_a" in hold_ids
        held = next(c for c in result["hold_entries"] if c["candidate_id"] == "dep_a")
        assert DEPENDENCY_UNRESOLVED in held["hold_reason"]

    def test_no_dependency_refs_is_no_dependency_known(self, tmp_path):
        a, b = self._pair()
        candidates = build_candidates_from_ledger(
            ledger_dir=tmp_path / "empty",
            additional_candidates=[a, b],
        )
        c = next(c for c in candidates if c["candidate_id"] == "dep_a")
        assert c["dependency_status"] == NO_DEPENDENCY_KNOWN

    def test_dependency_ref_cycle_detected(self, tmp_path):
        a, b = self._pair(a_refs=["dep_b"], b_refs=["dep_a"])
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_a", "dep_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert len(result["cycle_nodes"]) > 0
        # detect_cycles (V0, inchangé) ne marque que le noeud cible de la
        # back-edge — au moins un des deux membres du cycle n'est pas
        # selectionne (meme convention que test_cycle_produces_hold_not_selection).
        selected_ids = {c["candidate_id"] for c in result["selected_entries"]}
        assert "dep_a" not in selected_ids or "dep_b" not in selected_ids

    def test_version_and_dependency_ref_no_duplicate_edge(self, tmp_path):
        a = _entry(eid="dep_v_a", path="periphery/dep_v_a.py", source_hash="dv0000000000001a")
        b = _entry(eid="dep_v_b", path="periphery/dep_v_b.py", source_hash="dv0000000000002b")
        a["prev_entry_id"] = "dep_v_b"
        a["dependency_refs"] = ["dep_v_b"]
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["dep_v_a", "dep_v_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        matching = [
            e for e in result["dependency_edges"]
            if e["from"] == "dep_v_a" and e["to"] == "dep_v_b"
        ]
        assert len(matching) == 1

    def test_dependency_linked_event_consumed(self, tmp_path):
        """Relation enregistree APRES coup via evenement append-only
        DEPENDENCY_LINKED (pas de reecriture des lignes d'entree)."""
        ld = tmp_path / "ledger"
        src = tmp_path / "evt_a.py"
        src.write_text("a\n", encoding="utf-8")
        dep = tmp_path / "evt_b.py"
        dep.write_text("b\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/evt_a.py", ledger_dir=ld)
        r_b = _register_source(str(dep), target_path="periphery/evt_b.py", ledger_dir=ld)
        link_result = _link_dependency(
            r_a["ledger_entry_id"], r_b["ledger_entry_id"],
            evidence_type="PYTHON_IMPORT", ledger_dir=ld,
        )
        assert link_result["status"] == "DEPENDENCY_LINKED"

        result = propose_batch(
            candidate_entry_ids=[r_a["ledger_entry_id"], r_b["ledger_entry_id"]],
            ledger_dir=ld,
            selector_dir=tmp_path / "sel",
        )
        edges = result["dependency_edges"]
        assert any(
            e["from"] == r_a["ledger_entry_id"] and e["to"] == r_b["ledger_entry_id"]
            and e["type"] == DEPENDENCY_CONFIRMED
            for e in edges
        )

    def test_link_dependency_fails_closed_unknown_source(self, tmp_path):
        ld = tmp_path / "ledger"
        dep = tmp_path / "only_b.py"
        dep.write_text("b\n", encoding="utf-8")
        r_b = _register_source(str(dep), target_path="periphery/only_b.py", ledger_dir=ld)
        result = _link_dependency("nonexistent_source", r_b["ledger_entry_id"], ledger_dir=ld)
        assert "error" in result

    def test_link_dependency_fails_closed_unknown_dependency(self, tmp_path):
        ld = tmp_path / "ledger"
        src = tmp_path / "only_a.py"
        src.write_text("a\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/only_a.py", ledger_dir=ld)
        result = _link_dependency(r_a["ledger_entry_id"], "nonexistent_dependency", ledger_dir=ld)
        assert "error" in result

    def test_link_dependency_does_not_rewrite_entries(self, tmp_path):
        ld = tmp_path / "ledger"
        src = tmp_path / "immut_a.py"
        src.write_text("a\n", encoding="utf-8")
        dep = tmp_path / "immut_b.py"
        dep.write_text("b\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/immut_a.py", ledger_dir=ld)
        r_b = _register_source(str(dep), target_path="periphery/immut_b.py", ledger_dir=ld)
        entries_before = (ld / "entries.jsonl").read_text(encoding="utf-8")
        _link_dependency(r_a["ledger_entry_id"], r_b["ledger_entry_id"], ledger_dir=ld)
        entries_after = (ld / "entries.jsonl").read_text(encoding="utf-8")
        assert entries_before == entries_after


# --- TestCLIExplicitScope (real CLI --entries, fail-closed) -------------------

class TestCLIExplicitScope:
    def test_cli_propose_entries_no_residue_leakage(self, tmp_path):
        import subprocess, uuid
        unique = uuid.uuid4().hex[:12]
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        src1 = tmp_path / "cli_scope_1.py"
        src1.write_text(f"x = 1  # {unique}\n", encoding="utf-8")
        src2 = tmp_path / "cli_scope_2.py"
        src2.write_text(f"x = 2  # {unique}\n", encoding="utf-8")

        r1 = subprocess.run(
            [sys.executable, cli, "ledger", "register-source", str(src1),
             "--target", f"periphery/cli_scope_1_{unique}.py", "--domain", "PERIPHERAL"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        r2 = subprocess.run(
            [sys.executable, cli, "ledger", "register-source", str(src2),
             "--target", f"periphery/cli_scope_2_{unique}.py", "--domain", "PERIPHERAL"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert r1.returncode == 0 and r2.returncode == 0
        d1 = json.loads(r1.stdout)
        d2 = json.loads(r2.stdout)
        id1 = d1.get("ledger_entry_id")
        id2 = d2.get("ledger_entry_id")
        assert id1 and id2

        propose = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--max", "5",
             "--objective", "cli-scope-test", "--entries", f"{id1},{id2}"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert propose.returncode == 0
        out = json.loads(propose.stdout)
        assert out["candidate_scope_mode"] == "EXPLICIT_ENTRY_IDS"
        assert set(out["candidate_entry_ids"]) == {id1, id2}
        assert out["metrics"]["candidate_count"] == 2

    def test_cli_propose_entries_unknown_id_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--entries", "totally_bogus_id_xyz"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert out["scope_error"] is not None
        assert out["selected_count"] == 0

    def test_cli_propose_unknown_flag_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--bogus", "x"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH_CLI_ERROR" in result.stdout

    def test_cli_propose_max_missing_value_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--max"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH_CLI_ERROR" in result.stdout

    def test_cli_propose_entries_empty_value_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--entries", ""],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH_CLI_ERROR" in result.stdout


# --- TestDependencyExecutionOrder (dependency-first, input-order independent) -

class TestDependencyExecutionOrder:
    def _dependent_pair(self):
        """A (dependant) apparait EN PREMIER dans additional_candidates,
        alors qu'il depend de B (qui apparait en second) — l'ordre naturel
        pre-tri est donc [A,B], l'ordre canonique attendu est [B,A]."""
        a = _entry(eid="ord_a", path="periphery/ord_a.py", source_hash="oa0000000000001a")
        b = _entry(eid="ord_b", path="periphery/ord_b.py", source_hash="ob0000000000002b")
        a["dependency_refs"] = ["ord_b"]
        return a, b

    def test_dependency_precedes_dependant_direct_call(self):
        a, b = self._dependent_pair()
        ca = build_candidate(a)
        cb = build_candidate(b)
        edges = detect_dependencies([ca, cb], entry_index={"ord_a": "ord_a", "ord_b": "ord_b"})
        order = compute_execution_order([ca, cb], edges)
        assert order.index("ord_b") < order.index("ord_a")

    def test_order_independent_of_input_order(self, tmp_path):
        a, b = self._dependent_pair()
        r1 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        r2 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_b", "ord_a"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r1["execution_order"] == ["ord_b", "ord_a"]
        assert r2["execution_order"] == ["ord_b", "ord_a"]
        assert r1["execution_order"] == r2["execution_order"]

    def test_independent_control_deterministic_position(self, tmp_path):
        a, b = self._dependent_pair()
        c = _entry(eid="ord_c", path="periphery/ord_c.py", source_hash="oc0000000000003c")
        result = propose_batch(
            additional_candidates=[a, b, c],
            candidate_entry_ids=["ord_a", "ord_b", "ord_c"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        order = result["execution_order"]
        assert order.index("ord_b") < order.index("ord_a")
        assert set(order) == {"ord_a", "ord_b", "ord_c"}

    def test_chain_a_depends_b_depends_c(self, tmp_path):
        a = _entry(eid="chn_a", path="periphery/chn_a.py", source_hash="ca0000000000001a")
        b = _entry(eid="chn_b", path="periphery/chn_b.py", source_hash="cb0000000000002b")
        c = _entry(eid="chn_c", path="periphery/chn_c.py", source_hash="cc0000000000003c")
        a["dependency_refs"] = ["chn_b"]
        b["dependency_refs"] = ["chn_c"]
        result = propose_batch(
            additional_candidates=[a, b, c],
            candidate_entry_ids=["chn_a", "chn_b", "chn_c"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        order = result["execution_order"]
        assert order == ["chn_c", "chn_b", "chn_a"]

    def test_repeated_same_graph_same_order(self, tmp_path):
        a, b = self._dependent_pair()
        r1 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        r2 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r1["execution_order"] == r2["execution_order"]

    def test_execution_order_equals_selected_ids(self, tmp_path):
        a, b = self._dependent_pair()
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        selected_ids = {c["candidate_id"] for c in result["selected_entries"]}
        assert set(result["execution_order"]) == selected_ids

    def test_real_gencoin_pilot_order(self, tmp_path):
        """Reproduit le graphe reel gencoin -> os3_ticket via dependency_refs."""
        a = _entry(eid="gc_gencoin", path="periphery/gencoin.py", source_hash="gc00000000000001")
        b = _entry(eid="gc_os3", path="periphery/os3_ticket.py", source_hash="gc00000000000002")
        a["dependency_refs"] = ["gc_os3"]
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["gc_gencoin", "gc_os3"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        order = result["execution_order"]
        assert order.index("gc_os3") < order.index("gc_gencoin")


# --- TestBatchHashBindsDependencySemantics -------------------------------------

class TestBatchHashBindsDependencySemantics:
    def test_same_graph_same_hash(self, tmp_path):
        a, b = TestDependencyExecutionOrder()._dependent_pair()
        r1 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            objective="hash-stable",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        r2 = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            objective="hash-stable",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r1["batch_hash"] == r2["batch_hash"]

    def test_dependency_changes_hash(self, tmp_path):
        a_no_dep = _entry(eid="hb_a", path="periphery/hb_a.py", source_hash="hb0000000000001a")
        b_ctrl = _entry(eid="hb_b", path="periphery/hb_b.py", source_hash="hb0000000000002b")
        r_without = propose_batch(
            additional_candidates=[a_no_dep, b_ctrl],
            candidate_entry_ids=["hb_a", "hb_b"],
            objective="hash-dep-cmp",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel1",
        )
        a_with_dep = dict(a_no_dep)
        a_with_dep["dependency_refs"] = ["hb_b"]
        r_with = propose_batch(
            additional_candidates=[a_with_dep, b_ctrl],
            candidate_entry_ids=["hb_a", "hb_b"],
            objective="hash-dep-cmp",
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel2",
        )
        assert r_without["batch_hash"] != r_with["batch_hash"]
        # meme contenu selectionne, meme scope -- seule la semantique de
        # dependance change
        assert set(c["candidate_id"] for c in r_without["selected_entries"]) == \
               set(c["candidate_id"] for c in r_with["selected_entries"])

    def test_scope_hash_and_batch_hash_are_distinct(self, tmp_path):
        a, b = TestDependencyExecutionOrder()._dependent_pair()
        result = propose_batch(
            additional_candidates=[a, b],
            candidate_entry_ids=["ord_a", "ord_b"],
            ledger_dir=tmp_path / "empty",
            selector_dir=tmp_path / "sel",
        )
        assert result["candidate_scope_hash"] != result["batch_hash"]


# --- TestLinkDependencyRelationTypeRestriction ---------------------------------

class TestLinkDependencyRelationTypeRestriction:
    def test_confirmed_accepted(self, tmp_path):
        ld = tmp_path / "ledger"
        src = tmp_path / "rt_a.py"; src.write_text("a\n", encoding="utf-8")
        dep = tmp_path / "rt_b.py"; dep.write_text("b\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/rt_a.py", ledger_dir=ld)
        r_b = _register_source(str(dep), target_path="periphery/rt_b.py", ledger_dir=ld)
        result = _link_dependency(
            r_a["ledger_entry_id"], r_b["ledger_entry_id"],
            relation_type="DEPENDENCY_CONFIRMED", ledger_dir=ld,
        )
        assert result["status"] == "DEPENDENCY_LINKED"

    def test_probable_rejected_fail_closed(self, tmp_path):
        ld = tmp_path / "ledger"
        src = tmp_path / "rt_c.py"; src.write_text("c\n", encoding="utf-8")
        dep = tmp_path / "rt_d.py"; dep.write_text("d\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/rt_c.py", ledger_dir=ld)
        r_b = _register_source(str(dep), target_path="periphery/rt_d.py", ledger_dir=ld)
        result = _link_dependency(
            r_a["ledger_entry_id"], r_b["ledger_entry_id"],
            relation_type="DEPENDENCY_PROBABLE", ledger_dir=ld,
        )
        assert "error" in result

    def test_unknown_relation_type_rejected(self, tmp_path):
        ld = tmp_path / "ledger"
        src = tmp_path / "rt_e.py"; src.write_text("e\n", encoding="utf-8")
        dep = tmp_path / "rt_f.py"; dep.write_text("f\n", encoding="utf-8")
        r_a = _register_source(str(src), target_path="periphery/rt_e.py", ledger_dir=ld)
        r_b = _register_source(str(dep), target_path="periphery/rt_f.py", ledger_dir=ld)
        result = _link_dependency(
            r_a["ledger_entry_id"], r_b["ledger_entry_id"],
            relation_type="DEPENDENCY_UNKNOWN", ledger_dir=ld,
        )
        assert "error" in result


# --- TestCLIQuotedObjectiveAndEntries -------------------------------------------

class TestCLIQuotedObjectiveAndEntries:
    def test_cli_quoted_objective_preserved(self, tmp_path):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--max", "1",
             "--objective", "First real batch pilot V0"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert out.get("scope_error") is None or out["scope_error"] is None
        # Verifie via inspect que l'objectif complet (avec espaces) a ete
        # preserve tel quel dans le BatchProposal sauvegarde.
        bid = out.get("batch_id")
        if bid:
            status = subprocess.run(
                [sys.executable, cli, "batch", "status", bid],
                capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
            )
            assert "First real batch pilot V0" in status.stdout

    def test_cli_objective_missing_value_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--objective"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH_CLI_ERROR" in result.stdout

    def test_cli_invalid_max_fails_closed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "propose", "--max", "notanumber"],
            capture_output=True, text=True, cwd=str(_SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0
        assert "BATCH_CLI_ERROR" in result.stdout
