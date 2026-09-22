"""
tests/test_batch_execution_v0.py
=================================
Suite BATCH_EXECUTION_ENVELOPE_V0.

Couvre :
  A. Gates matérialité / opération (unitaires, purs)
  B. Intégrité BatchProposal (fidélité au Ledger courant)
  C. prepare_execution (NOT_READY, PLANNED, protégé, agrégat)
  D. run_execution : dépendance ACT/HOLD/BLOCK/transitive/mixte (synthétique)
  E. CLI réel (prepare/status/inspect/list)
  F. Batch réel 84a929c6f48a90c5 : preuve READ-ONLY que le pont refuse
     un batch techniquement valide mais sans delta réel
  G. Autorité / non-mutation / append-only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidia_batch_execution import (  # noqa: E402
    SCHEMA_VERSION,
    DECISION_AUTHORITY,
    MEANINGFUL_DELTA,
    NO_MEANINGFUL_DELTA,
    MATERIALITY_UNKNOWN,
    PLANNED,
    NOT_READY_NO_DELTA,
    NOT_READY_UNDEFINED_OPERATION,
    DEPENDENCY_BLOCKED,
    REFUSED_PROTECTED_TARGET,
    EXECUTED_ACT,
    EXECUTED_HOLD,
    EXECUTED_BLOCK,
    EXECUTED_ERROR,
    BATCH_EXECUTION_NOT_READY,
    BATCH_PLANNED,
    BATCH_COMPLETE,
    BATCH_PARTIAL,
    BATCH_HOLD,
    assess_materiality,
    assess_operation,
    verify_batch_integrity,
    prepare_execution,
    run_execution,
    executable_candidate_count,
    real_session_executor_via_compute_plan,
    load_approval_artifact,
    verify_approval_artifact,
    store_approval_artifact,
    compute_approval_record_hash,
    compute_execution_authority_hash,
    _validate_approval,
    _approval_path,
    cmd_execution_status,
    cmd_execution_inspect,
    cmd_execution_list,
    _compute_aggregate_status,
    _load_execution,
    _save_execution,
    APPROVED_FOR_BOUNDED_EXECUTION,
    EXECUTION_APPROVAL_INVALID,
    SOURCE_INTEGRITY_MISMATCH,
    TARGET_PRECONDITION_MISMATCH,
)
from obsidia_batch_selector import propose_batch  # noqa: E402


# ─── Fixtures helpers ─────────────────────────────────────────────────────────

def _synthetic_entry(
    eid: str,
    target_path: str,
    source_hash: str,
    dependency_refs: list | None = None,
    operation_type: str | None = "COPY",
) -> dict:
    return {
        "ledger_entry_id": eid,
        "entry_schema_version": "V0",
        "target_path": target_path,
        "source_path": f"_synthetic_source/{eid}.py",
        "source_hash": source_hash,
        "source_type": "REAL_SOURCE",
        "target_domain": "PERIPHERAL",
        "session_id": None,
        "prev_entry_id": None,
        "dedup_classification": "DISTINCT_CONTENT",
        "lifecycle_status": "DISCOVERED",
        "kx108_decision": None,
        "proposal_id": None,
        "proposal_hash": None,
        "risk_flags": [],
        "unknowns": [],
        "dependency_refs": dependency_refs or [],
        "provenance_refs": (
            {"operation_type": operation_type, "operation_reason": "synthetic test"}
            if operation_type else {}
        ),
    }


def _materialize_source(tmp_path, eid: str, content: bytes = b"synthetic\n") -> str:
    """
    Ecrit un VRAI fichier source physique (necessaire pour toute
    entree qui doit traverser run_execution — la re-verification
    d'integrite au runtime lit reellement ce fichier). Retourne le hash
    reel du contenu ecrit ; ne fabrique jamais un hash.
    """
    import hashlib
    src_dir = tmp_path / "_synthetic_source"
    src_dir.mkdir(parents=True, exist_ok=True)
    src_file = src_dir / f"{eid}.py"
    src_file.write_bytes(content)
    return hashlib.sha256(content).hexdigest()[:16]


# ─── Helper de TEST UNIQUEMENT — frontiere d'autorite externe simulee ────────
#
# obsidia_batch_execution.py ne fabrique JAMAIS approved_by="HUMAN" depuis
# une enveloppe : ce helper simule la frontiere externe (hors module) qui
# construit un record complet, calcule son hash, puis le stocke via
# store_approval_artifact (persistance stricte, append-only). Rien ici ne
# represente une capacite de production.

def _build_synthetic_approval_record(envelope: dict, overrides: dict | None = None, approval_id: str | None = None) -> dict:
    import uuid
    record = {
        "approval_id": approval_id or uuid.uuid4().hex[:16],
        "approval_schema_version": SCHEMA_VERSION,
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": envelope["batch_id"],
        "batch_hash": envelope["batch_hash"],
        "candidate_scope_hash": envelope["candidate_scope_hash"],
        "execution_authority_hash": envelope.get("execution_authority_hash"),
        "approved_by": "HUMAN",
        "approval_status": APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": DECISION_AUTHORITY,
    }
    if overrides:
        record.update(overrides)
    record["approval_record_hash"] = compute_approval_record_hash(record)
    return record


def _create_synthetic_approval(envelope: dict, execution_dir, overrides: dict | None = None) -> str:
    """Construit + stocke un artefact d'approbation synthetique VALIDE. Retourne son approval_id."""
    record = _build_synthetic_approval_record(envelope, overrides)
    result = store_approval_artifact(record, execution_dir)
    assert result["status"] == "STORED"
    return record["approval_id"]


def _prepare_synthetic_batch(tmp_path, entries: list[dict], candidate_entry_ids: list[str], objective="synthetic"):
    """
    Ecrit reellement les entrees synthetiques sur disque (ledger_dir), pour
    que verify_batch_integrity (qui lit uniquement le disque, exactement
    comme pour un vrai BatchProposal) les voie. Cree un target_path FICTIF
    (n'existe pas sur disque -> MEANINGFUL_DELTA 'target_does_not_exist_yet')
    pour que le gate de materialite laisse passer ces candidats
    synthetiques, sans jamais toucher au vrai repo. repo_root=tmp_path pour
    prepare_execution garde la resolution de target_path isolee.
    """
    from obsidia_branching_ledger import _append_entry

    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "sel"
    execution_dir = tmp_path / "exec"
    for e in entries:
        _append_entry(e, ledger_dir)
    proposal = propose_batch(
        candidate_entry_ids=candidate_entry_ids,
        objective=objective,
        max_batch_size=10,
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
    )
    return proposal, ledger_dir, selector_dir, execution_dir


# ─── A. Gates matérialité / opération ─────────────────────────────────────────

class TestMaterialityGate:
    def test_same_source_target_path_no_delta(self, tmp_path):
        status, detail = assess_materiality("periphery/x.py", "periphery/x.py", "hash1", tmp_path)
        assert status == NO_MEANINGFUL_DELTA
        assert detail["reason"] == "source_equals_target_path"

    def test_target_missing_target_path_field_unknown(self, tmp_path):
        status, detail = assess_materiality("periphery/x.py", None, "hash1", tmp_path)
        assert status == MATERIALITY_UNKNOWN

    def test_target_does_not_exist_yet_is_meaningful(self, tmp_path):
        status, detail = assess_materiality("periphery/x.py", "new/does_not_exist.py", "hash1", tmp_path)
        assert status == MEANINGFUL_DELTA
        assert detail["reason"] == "target_does_not_exist_yet"

    def test_target_exists_same_content_no_delta(self, tmp_path):
        import hashlib
        target = tmp_path / "existing.py"
        target.write_bytes(b"same\n")
        h = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        status, detail = assess_materiality("elsewhere/x.py", "existing.py", h, tmp_path)
        assert status == NO_MEANINGFUL_DELTA
        assert detail["reason"] == "target_content_equals_source"

    def test_target_exists_different_content_is_meaningful(self, tmp_path):
        target = tmp_path / "existing2.py"
        target.write_text("different\n", encoding="utf-8")
        status, detail = assess_materiality("elsewhere/x.py", "existing2.py", "totally_different_hash", tmp_path)
        assert status == MEANINGFUL_DELTA
        assert detail["reason"] == "target_content_differs"

    def test_never_fabricates_hash(self, tmp_path):
        # Le hash retourne (target_pre_hash) doit toujours provenir d'une
        # lecture reelle, jamais invente.
        import hashlib
        target = tmp_path / "real.py"
        target.write_bytes(b"abc\n")
        real_hash = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        status, detail = assess_materiality("x.py", "real.py", "unrelated", tmp_path)
        assert detail["target_pre_hash"] == real_hash


class TestOperationGate:
    def test_no_provenance_undefined(self):
        op, reason = assess_operation(None)
        assert op is None

    def test_no_operation_type_undefined(self):
        op, reason = assess_operation({"origin": "manual"})
        assert op is None

    def test_explicit_operation_type_defined(self):
        op, reason = assess_operation({"operation_type": "COPY", "operation_reason": "port from x"})
        assert op == "COPY"
        assert reason == "port from x"

    def test_never_infers_from_filename(self):
        # meme sans provenance_refs, jamais d'inference implicite
        op, reason = assess_operation({})
        assert op is None


# ─── B. Intégrité BatchProposal ────────────────────────────────────────────────

class TestBatchIntegrity:
    def test_global_mode_not_verifiable(self, tmp_path):
        proposal = propose_batch(
            additional_candidates=[_synthetic_entry("g1", "periphery/g1.py", "h1")],
            ledger_dir=tmp_path / "ledger",
            selector_dir=tmp_path / "sel",
        )
        ok, err = verify_batch_integrity(proposal, tmp_path / "ledger")
        assert ok is False
        assert err == "GLOBAL_MODE_NOT_VERIFIABLE_FOR_EXECUTION"

    def test_explicit_scope_verified_ok(self, tmp_path):
        entries = [_synthetic_entry("v1", "periphery/v1.py", "h1")]
        proposal, ld, sd, _ = _prepare_synthetic_batch(tmp_path, entries, ["v1"])
        ok, err = verify_batch_integrity(proposal, ld)
        assert ok is True
        assert err is None

    def test_source_hash_drift_detected(self, tmp_path):
        entries = [_synthetic_entry("d1", "periphery/d1.py", "h1")]
        proposal, ld, sd, _ = _prepare_synthetic_batch(tmp_path, entries, ["d1"])
        # simuler une derive : reecrire l'entree ledger avec un hash different
        entries_path = ld / "entries.jsonl"
        lines = entries_path.read_text(encoding="utf-8").splitlines()
        rewritten = []
        for line in lines:
            e = json.loads(line)
            if e.get("ledger_entry_id") == "d1":
                e["source_hash"] = "DRIFTED_HASH"
            rewritten.append(json.dumps(e))
        entries_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
        ok, err = verify_batch_integrity(proposal, ld)
        assert ok is False
        assert "SOURCE_HASH_DRIFT" in err

    def test_candidate_removed_from_ledger_detected(self, tmp_path):
        entries = [_synthetic_entry("r1", "periphery/r1.py", "h1")]
        proposal, ld, sd, _ = _prepare_synthetic_batch(tmp_path, entries, ["r1"])
        (ld / "entries.jsonl").write_text("", encoding="utf-8")
        ok, err = verify_batch_integrity(proposal, ld)
        assert ok is False
        assert "CANDIDATE_NO_LONGER_IN_LEDGER" in err


# ─── C. prepare_execution ──────────────────────────────────────────────────────

class TestPrepareExecution:
    def test_meaningful_delta_becomes_planned(self, tmp_path):
        entries = [_synthetic_entry("p1", "periphery/p1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["p1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert env["integrity_verified"] is True
        child = env["children"][0]
        assert child["materiality_status"] == MEANINGFUL_DELTA
        assert child["execution_status"] == PLANNED
        assert env["aggregate_status"] == BATCH_PLANNED

    def test_no_operation_defined_holds(self, tmp_path):
        entries = [_synthetic_entry("u1", "periphery/u1.py", "h1", operation_type=None)]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["u1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        child = env["children"][0]
        assert child["execution_status"] == NOT_READY_UNDEFINED_OPERATION
        assert env["aggregate_status"] == BATCH_EXECUTION_NOT_READY

    def test_source_equals_target_not_ready(self, tmp_path):
        entries = [_synthetic_entry("s1", "periphery/s1.py", "h1")]
        entries[0]["source_path"] = "periphery/s1.py"  # deja egal par construction
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["s1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        child = env["children"][0]
        assert child["materiality_status"] == NO_MEANINGFUL_DELTA
        assert child["execution_status"] == NOT_READY_NO_DELTA

    def test_batch_not_found_error(self, tmp_path):
        env = prepare_execution("does_not_exist_batch", tmp_path / "ledger", tmp_path / "sel", tmp_path / "exec")
        assert env["aggregate_status"] == "BATCH_ERROR"
        assert env["integrity_error"] == "BATCH_PROPOSAL_NOT_FOUND"

    def test_never_creates_session_or_kx108(self, tmp_path):
        entries = [_synthetic_entry("n1", "periphery/n1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["n1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        for c in env["children"]:
            assert c["session_id"] is None
            assert c["kx108_decision"] is None
        assert env["human_execution_approved"] is False

    def test_decision_authority_kx108_only(self, tmp_path):
        entries = [_synthetic_entry("a1", "periphery/a1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["a1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert env["decision_authority"] == DECISION_AUTHORITY == "KX108_ONLY"
        for c in env["children"]:
            assert c["decision_authority"] == "KX108_ONLY"


# ─── D. run_execution — scénarios synthétiques de propagation ───────────────

class TestRunExecutionScenarios:
    def _bcd(self, tmp_path):
        """B (prerequis), A (depend de B), C (independant)."""
        b = _synthetic_entry("dep_B", "periphery/synB.py", _materialize_source(tmp_path, "dep_B", b"B\n"))
        a = _synthetic_entry(
            "dep_A", "periphery/synA.py", _materialize_source(tmp_path, "dep_A", b"A\n"),
            dependency_refs=["dep_B"],
        )
        c = _synthetic_entry("dep_C", "periphery/synC.py", _materialize_source(tmp_path, "dep_C", b"C\n"))
        proposal, ld, sd, ed = _prepare_synthetic_batch(
            tmp_path, [b, a, c], ["dep_B", "dep_A", "dep_C"], objective="dep-scenario",
        )
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        return env, ed

    def test_all_act(self, tmp_path):
        env, ed = self._bcd(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            return {"kx108_decision": "ACT", "session_id": f"sess-{child['candidate_entry_id']}"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["dep_B"]["execution_status"] == EXECUTED_ACT
        assert by_id["dep_A"]["execution_status"] == EXECUTED_ACT
        assert by_id["dep_C"]["execution_status"] == EXECUTED_ACT
        assert result["aggregate_status"] == BATCH_COMPLETE

    def test_dependency_block(self, tmp_path):
        env, ed = self._bcd(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "dep_B":
                return {"kx108_decision": "BLOCK"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["dep_B"]["execution_status"] == EXECUTED_BLOCK
        assert by_id["dep_A"]["execution_status"] == DEPENDENCY_BLOCKED
        assert by_id["dep_A"]["kx108_decision"] is None  # jamais fabrique
        assert by_id["dep_C"]["execution_status"] == EXECUTED_ACT
        assert result["aggregate_status"] == BATCH_PARTIAL

    def test_dependency_hold(self, tmp_path):
        env, ed = self._bcd(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "dep_B":
                return {"kx108_decision": "HOLD"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["dep_B"]["execution_status"] == EXECUTED_HOLD
        assert by_id["dep_A"]["execution_status"] == DEPENDENCY_BLOCKED
        assert by_id["dep_A"]["kx108_decision"] is None
        assert by_id["dep_C"]["execution_status"] == EXECUTED_ACT

    def test_transitive_dependency_block(self, tmp_path):
        """A depend de B, B depend de C. C = BLOCK -> B et A DEPENDENCY_BLOCKED."""
        c = _synthetic_entry("trn_C", "periphery/trnC.py", _materialize_source(tmp_path, "trn_C", b"C\n"))
        b = _synthetic_entry(
            "trn_B", "periphery/trnB.py", _materialize_source(tmp_path, "trn_B", b"B\n"),
            dependency_refs=["trn_C"],
        )
        a = _synthetic_entry(
            "trn_A", "periphery/trnA.py", _materialize_source(tmp_path, "trn_A", b"A\n"),
            dependency_refs=["trn_B"],
        )
        proposal, ld, sd, ed = _prepare_synthetic_batch(
            tmp_path, [a, b, c], ["trn_A", "trn_B", "trn_C"], objective="transitive",
        )
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "trn_C":
                return {"kx108_decision": "BLOCK"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["trn_C"]["execution_status"] == EXECUTED_BLOCK
        assert by_id["trn_B"]["execution_status"] == DEPENDENCY_BLOCKED
        assert by_id["trn_A"]["execution_status"] == DEPENDENCY_BLOCKED
        # Seul C a un resultat KX108 reel issu de l'execution
        assert by_id["trn_C"]["kx108_decision"] == "BLOCK"
        assert by_id["trn_B"]["kx108_decision"] is None
        assert by_id["trn_A"]["kx108_decision"] is None

    def test_mixed_outcomes_partial(self, tmp_path):
        a = _synthetic_entry("mix_A", "periphery/mixA.py", _materialize_source(tmp_path, "mix_A", b"A\n"))
        b = _synthetic_entry("mix_B", "periphery/mixB.py", _materialize_source(tmp_path, "mix_B", b"B\n"))
        c = _synthetic_entry("mix_C", "periphery/mixC.py", _materialize_source(tmp_path, "mix_C", b"C\n"))
        proposal, ld, sd, ed = _prepare_synthetic_batch(
            tmp_path, [a, b, c], ["mix_A", "mix_B", "mix_C"], objective="mixed",
        )
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "mix_A":
                return {"kx108_decision": "ACT"}
            if child["candidate_entry_id"] == "mix_B":
                return {"kx108_decision": "HOLD"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert result["aggregate_status"] == BATCH_PARTIAL

    def test_independent_branch_continues_after_dependency_block(self, tmp_path):
        env, ed = self._bcd(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "dep_B":
                return {"kx108_decision": "BLOCK"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["dep_C"]["execution_status"] == EXECUTED_ACT
        assert by_id["dep_C"]["kx108_decision"] == "ACT"

    def test_no_op_no_child_session_ever(self, tmp_path):
        entries = [_synthetic_entry("noop1", "periphery/noop1.py", "h1")]
        entries[0]["target_path"] = entries[0]["source_path"]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["noop1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert executable_candidate_count(env) == 0
        approval_id = _create_synthetic_approval(env, ed)

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []  # jamais invoque : rien n'etait PLANNED
        assert result["aggregate_status"] == BATCH_EXECUTION_NOT_READY

    def test_undefined_operation_no_child_session_ever(self, tmp_path):
        entries = [_synthetic_entry("undef1", "periphery/undef1.py", "h1", operation_type=None)]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["undef1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []

    def test_run_execution_unknown_id(self, tmp_path):
        result = run_execution(
            "nonexistent", {"status": APPROVED_FOR_BOUNDED_EXECUTION},
            lambda c: {"kx108_decision": "ACT"}, tmp_path / "exec",
        )
        assert "error" in result

    def test_executor_error_result_marks_executed_error(self, tmp_path):
        entries = [_synthetic_entry("err1", "periphery/err1.py", _materialize_source(tmp_path, "err1", b"E\n"))]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["err1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            return {"kx108_decision": "UNEXPECTED_VALUE"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert result["children"][0]["execution_status"] == EXECUTED_ERROR


# --- TestHumanApprovalGate (HARDEN_AND_CLOSE_BATCH_EXECUTION_ENVELOPE_V0) -----

class TestHumanApprovalGate:
    def _planned_envelope(self, tmp_path):
        entries = [_synthetic_entry("appr1", "periphery/appr1.py", _materialize_source(tmp_path, "appr1", b"X\n"))]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["appr1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        return env, ed

    def test_missing_approval_zero_executor_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], None, executor, ed, tmp_path)
        assert called == []
        assert EXECUTION_APPROVAL_INVALID in result["execution_approval_status"]
        assert "APPROVAL_MISSING" in result["execution_approval_status"]

    def test_wrong_execution_id_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"batch_execution_id": "tampered_execution_id"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_WRONG_EXECUTION_ID" in result["execution_approval_status"]

    def test_wrong_batch_hash_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"batch_hash": "tampered_hash"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_WRONG_BATCH_HASH" in result["execution_approval_status"]

    def test_wrong_scope_hash_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"candidate_scope_hash": "tampered_scope_hash"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_WRONG_SCOPE_HASH" in result["execution_approval_status"]

    def test_wrong_status_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"approval_status": "SOMETHING_ELSE"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_STATUS_INVALID" in result["execution_approval_status"]

    def test_not_human_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"approved_by": "AGENT"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert EXECUTION_APPROVAL_INVALID in result["execution_approval_status"]
        assert "APPROVAL_APPROVED_BY_NOT_RECOGNIZED" in result["execution_approval_status"]

    def test_wrong_decision_authority_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed, {"decision_authority": "SOMETHING_ELSE"})
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_WRONG_DECISION_AUTHORITY" in result["execution_approval_status"]

    def test_unknown_approval_id_zero_calls(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], "totally_unknown_approval_id", executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_MISSING" in result["execution_approval_status"]

    def test_approval_belongs_to_another_execution_zero_calls(self, tmp_path):
        env_a, ed = self._planned_envelope(tmp_path)
        entries_b = [_synthetic_entry("appr2", "periphery/appr2.py", _materialize_source(tmp_path, "appr2", b"Y\n"))]
        proposal_b, ld_b, sd_b, ed_b = _prepare_synthetic_batch(tmp_path, entries_b, ["appr2"], objective="second")
        env_b = prepare_execution(proposal_b["batch_id"], ld_b, sd_b, ed, repo_root=tmp_path)

        approval_id_for_b = _create_synthetic_approval(env_b, ed)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        # tente d'utiliser l'approbation de B pour executer A
        result = run_execution(env_a["batch_execution_id"], approval_id_for_b, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_WRONG_EXECUTION_ID" in result["execution_approval_status"]

    def test_fabricated_in_memory_dict_is_not_authority(self, tmp_path):
        """Un dict fabrique par l'appelant, meme avec tous les champs
        corrects, n'est JAMAIS accepte par run_execution — seul un
        approval_id charge depuis le magasin canonique compte."""
        env, ed = self._planned_envelope(tmp_path)
        fake = _build_synthetic_approval_record(env)  # jamais stocke
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        # run_execution n'accepte qu'un ID (str) ; passer un ID jamais
        # stocke prouve qu'aucun contenu en memoire ne peut faire autorite.
        result = run_execution(env["batch_execution_id"], fake["approval_id"], executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_MISSING" in result["execution_approval_status"]

    def test_tampered_stored_field_without_hash_update_zero_calls(self, tmp_path):
        """Un champ stocke est altere manuellement SANS mettre a jour le
        hash -> verify_approval_artifact doit le detecter."""
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)
        p = _approval_path(approval_id, ed)
        record = json.loads(p.read_text(encoding="utf-8"))
        record["approved_by"] = "AGENT"  # altere sans recalculer le hash
        p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_RECORD_HASH_MISMATCH" in result["execution_approval_status"]

    def test_human_execution_approved_bool_is_not_authority(self, tmp_path):
        """La sortie stale human_execution_approved=True dans l'enveloppe
        ne doit JAMAIS autoriser une execution sans artefact valide."""
        env, ed = self._planned_envelope(tmp_path)
        env["human_execution_approved"] = True
        _save_execution(env, ed)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], None, executor, ed, tmp_path)
        assert called == []

    def test_manually_set_execution_approval_status_is_not_authority(self, tmp_path):
        """Ecrire execution_approval_status='EXECUTION_APPROVAL_VALID'
        directement dans l'enveloppe stockee ne doit rien autoriser :
        run_execution revalide toujours depuis zero a chaque appel."""
        env, ed = self._planned_envelope(tmp_path)
        env["execution_approval_status"] = "EXECUTION_APPROVAL_VALID"
        env["execution_approval_id"] = "fake_id"
        _save_execution(env, ed)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], None, executor, ed, tmp_path)
        assert called == []
        assert EXECUTION_APPROVAL_INVALID in result["execution_approval_status"]

    def test_valid_approval_permits_execution(self, tmp_path):
        env, ed = self._planned_envelope(tmp_path)
        approval_id = _create_synthetic_approval(env, ed)
        stored = load_approval_artifact(approval_id, ed)
        ok, reason = _validate_approval(stored, env)
        assert ok is True
        assert reason is None
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called != []
        assert result["execution_approval_status"] == "EXECUTION_APPROVAL_VALID"
        assert result["children"][0]["execution_status"] == EXECUTED_ACT

    def test_approval_cannot_override_no_meaningful_delta(self, tmp_path):
        entries = [_synthetic_entry("noopa1", "periphery/noopa1.py", "h1")]
        entries[0]["target_path"] = entries[0]["source_path"]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["noopa1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert result["aggregate_status"] == BATCH_EXECUTION_NOT_READY

    def test_approval_cannot_override_dependency_block(self, tmp_path):
        b = _synthetic_entry("ov_B", "periphery/ovB.py", _materialize_source(tmp_path, "ov_B", b"B\n"))
        a = _synthetic_entry(
            "ov_A", "periphery/ovA.py", _materialize_source(tmp_path, "ov_A", b"A\n"),
            dependency_refs=["ov_B"],
        )
        proposal, ld, sd, ed = _prepare_synthetic_batch(
            tmp_path, [b, a], ["ov_B", "ov_A"], objective="override-dep",
        )
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        def executor(child):
            if child["candidate_entry_id"] == "ov_B":
                return {"kx108_decision": "BLOCK"}
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        by_id = {c["candidate_entry_id"]: c for c in result["children"]}
        assert by_id["ov_A"]["execution_status"] == DEPENDENCY_BLOCKED
        assert by_id["ov_A"]["kx108_decision"] is None


# --- TestSourceAndTargetRuntimeIntegrity ---------------------------------------

class TestSourceAndTargetRuntimeIntegrity:
    def test_source_drift_after_prepare_zero_calls(self, tmp_path):
        """La source enregistree au prepare est mutee AVANT le run -> le
        hash relu ne correspond plus -> aucun appel executor pour cet
        enfant."""
        real_src = tmp_path / "_synthetic_source" / "drift1.py"
        real_src.parent.mkdir(parents=True, exist_ok=True)
        real_src.write_bytes(b"v1\n")
        import hashlib
        h1 = hashlib.sha256(real_src.read_bytes()).hexdigest()[:16]

        e = _synthetic_entry("drift1", "periphery/drift1.py", h1)
        e["source_path"] = "_synthetic_source/drift1.py"
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, [e], ["drift1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        approval_id = _create_synthetic_approval(env, ed)

        # Mutation APRES prepare, AVANT run
        real_src.write_bytes(b"v2_mutated\n")

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert result["children"][0]["execution_status"] == SOURCE_INTEGRITY_MISMATCH

    def test_target_drift_after_prepare_zero_calls(self, tmp_path):
        """La cible existait au prepare (target_pre_hash != None) puis
        change de contenu avant le run -> TARGET_PRECONDITION_MISMATCH."""
        real_src = tmp_path / "_synthetic_source" / "tdrift1.py"
        real_src.parent.mkdir(parents=True, exist_ok=True)
        real_src.write_bytes(b"source_content\n")
        target = tmp_path / "target_pre_exists.py"
        target.write_bytes(b"target_v1\n")
        import hashlib
        source_hash = hashlib.sha256(real_src.read_bytes()).hexdigest()[:16]

        e = _synthetic_entry("tdrift1", "target_pre_exists.py", source_hash)
        e["source_path"] = "_synthetic_source/tdrift1.py"
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, [e], ["tdrift1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        # verifie que le gate de materialite a bien vu un delta (contenu different)
        assert env["children"][0]["execution_status"] == PLANNED
        approval_id = _create_synthetic_approval(env, ed)

        # La cible change APRES prepare, AVANT run
        target.write_bytes(b"target_v2_mutated\n")

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert result["children"][0]["execution_status"] == TARGET_PRECONDITION_MISMATCH

    def test_target_unexpectedly_appears_zero_calls(self, tmp_path):
        """La cible n'existait PAS au prepare (target_pre_hash=None) puis
        apparait avant le run -> TARGET_PRECONDITION_MISMATCH (fail-closed,
        pas d'hypothese que ce soit acceptable)."""
        e = _synthetic_entry(
            "appear1", "new/appears_later.py", _materialize_source(tmp_path, "appear1", b"X\n"),
        )
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, [e], ["appear1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert env["children"][0]["target_pre_hash"] is None
        approval_id = _create_synthetic_approval(env, ed)

        # La cible apparait APRES prepare, AVANT run
        target = tmp_path / "new" / "appears_later.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"unexpected\n")

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert result["children"][0]["execution_status"] == TARGET_PRECONDITION_MISMATCH

    def test_protected_target_at_run_zero_calls(self, tmp_path):
        """Defense en profondeur : meme si (hypothetiquement) un enfant
        PLANNED portait une cible protegee, le run refuse avant tout appel
        executor."""
        e = _synthetic_entry("protrun1", "new/protrun_target.py", "h1")
        e["source_path"] = "_synthetic_source/protrun1.py"
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, [e], ["protrun1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert env["children"][0]["execution_status"] == PLANNED
        # Simuler une cible qui devient protegee entre prepare et run
        env["children"][0]["target_path"] = "proofs/injected.json"
        from obsidia_batch_execution import _save_execution
        _save_execution(env, ed)
        approval_id = _create_synthetic_approval(env, ed)

        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], approval_id, executor, ed, tmp_path)
        assert called == []
        assert result["children"][0]["execution_status"] == REFUSED_PROTECTED_TARGET


# ─── E. CLI réel ────────────────────────────────────────────────────────────────

class TestCLIBatchExecution:
    def test_cli_execution_prepare_real_batch(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "execution", "prepare", "84a929c6f48a90c5"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert out["aggregate_status"] == "BATCH_EXECUTION_NOT_READY"
        assert out["executable_candidate_count"] == 0
        assert out["children_count"] == 5
        assert out["integrity_verified"] is True
        assert out["human_execution_approved"] is False

    def test_cli_execution_status_and_inspect(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        prep = subprocess.run(
            [sys.executable, cli, "batch", "execution", "prepare", "84a929c6f48a90c5"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        beid = json.loads(prep.stdout)["batch_execution_id"]
        status = subprocess.run(
            [sys.executable, cli, "batch", "execution", "status", beid],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert "BATCH_EXECUTION_NOT_READY" in status.stdout
        inspect = subprocess.run(
            [sys.executable, cli, "batch", "execution", "inspect", beid],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert "os3_ticket.py" in inspect.stdout
        assert "NOT_READY_NO_DELTA" in inspect.stdout

    def test_cli_execution_list(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "execution", "list"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0

    def test_cli_execution_unknown_id(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "execution", "status", "totally_bogus"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert "BATCH_EXECUTION_FAIL" in result.stdout

    def test_cli_no_run_subcommand_exposed(self):
        import subprocess
        cli = str(_SCRIPTS_DIR / "obsidia_cli.py")
        result = subprocess.run(
            [sys.executable, cli, "batch", "execution", "run", "whatever"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert "BATCH_EXECUTION_UNKNOWN_SUBCMD" in result.stdout


# ─── F. Batch réel 84a929c6f48a90c5 — preuve READ-ONLY ───────────────────────

class TestRealPilotBatchRefusal:
    """Le pont doit refuser un batch techniquement valide (5/5 selectionnes,
    integrite verifiee) mais sans delta reel — sans jamais creer de
    session, sans jamais fabriquer une decision KX108."""

    def test_real_batch_not_ready(self):
        env = prepare_execution("84a929c6f48a90c5")
        assert env["integrity_verified"] is True
        assert len(env["children"]) == 5
        assert executable_candidate_count(env) == 0
        assert env["aggregate_status"] == BATCH_EXECUTION_NOT_READY
        for c in env["children"]:
            assert c["execution_status"] == NOT_READY_NO_DELTA
            assert c["materiality_status"] == NO_MEANINGFUL_DELTA
            assert c["session_id"] is None
            assert c["kx108_decision"] is None

    def test_real_bridge_plans_explicit_scope_exactly(self):
        """Depuis IMPLEMENT_EXPLICIT_CHILD_SESSION_SCOPE_V0, le pont reel
        planifie desormais correctement une portee explicite a un seul
        target — mais ne cree JAMAIS de session/ecriture/KX108 reel."""
        env = prepare_execution("84a929c6f48a90c5")
        child = env["children"][0]
        result = real_session_executor_via_compute_plan(child)
        assert result["kx108_decision"] is None
        assert result["session_id"] is None
        assert result.get("plan_verified") is True
        assert result.get("scope_mode") == "EXPLICIT_CHILD_TARGET"
        assert result.get("approved_scope") == [child["target_path"]]
        assert result.get("next_step") == "cmd_execute_required_manually_outside_this_mandate"

    def test_real_batch_sources_unchanged_after_review(self):
        import hashlib
        expected = {
            "periphery/os3_ticket.py": "c17eaa70c982c8ea",
            "periphery/gencoin.py": "01697ea2cfce3244",
            "periphery/gencoin_debt_model.py": "e6817f5ae9651c78",
            "periphery/gencoin_distribution.py": "b380b7005be96bad",
            "periphery/energy_thermo.py": "2940c6c1adbacaf8",
        }
        for rel, expected_hash in expected.items():
            content = (_REPO_ROOT / rel).read_bytes()
            actual = hashlib.sha256(content).hexdigest()[:16]
            assert actual == expected_hash, f"{rel} hash drifted"

    def test_real_bridge_all_five_children_plan_exactly_one_target_each(self):
        """Chaque enfant du batch reel obtient une portee exacte a un seul
        element correspondant a son propre target — jamais un melange."""
        env = prepare_execution("84a929c6f48a90c5")
        for child in env["children"]:
            result = real_session_executor_via_compute_plan(child)
            assert result.get("plan_verified") is True
            assert result.get("approved_scope") == [child["target_path"]]

    def test_real_bridge_never_writes_anything(self):
        """compute_plan est pur -- aucune ecriture, meme via le pont reel."""
        env = prepare_execution("84a929c6f48a90c5")
        child = env["children"][0]
        before = (_REPO_ROOT / child["target_path"]).read_bytes()
        real_session_executor_via_compute_plan(child)
        after = (_REPO_ROOT / child["target_path"]).read_bytes()
        assert before == after

    def test_real_bridge_never_creates_real_session_or_kx108(self):
        env = prepare_execution("84a929c6f48a90c5")
        for child in env["children"]:
            result = real_session_executor_via_compute_plan(child)
            assert result["session_id"] is None
            assert result["kx108_decision"] is None


# ─── G. Autorité / non-mutation / append-only ─────────────────────────────────

class TestAuthorityAndImmutability:
    def test_human_execution_approved_always_false(self, tmp_path):
        entries = [_synthetic_entry("auth1", "periphery/auth1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["auth1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        assert env["human_execution_approved"] is False

    def test_prepare_does_not_mutate_source_batch_proposal(self, tmp_path):
        entries = [_synthetic_entry("immut1", "periphery/immut1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["immut1"])
        from obsidia_batch_selector import _load_batch
        before = json.dumps(_load_batch(proposal["batch_id"], sd), sort_keys=True)
        prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        after = json.dumps(_load_batch(proposal["batch_id"], sd), sort_keys=True)
        assert before == after

    def test_prepare_never_touches_ledger_entries(self, tmp_path):
        entries = [_synthetic_entry("ro1", "periphery/ro1.py", "h1")]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["ro1"])
        before = (ld / "entries.jsonl").read_text(encoding="utf-8")
        prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        after = (ld / "entries.jsonl").read_text(encoding="utf-8")
        assert before == after

    def test_aggregate_never_equals_kx108_value(self, tmp_path):
        # L'agregat ne doit jamais etre confondu avec une valeur KX108
        # (ACT/HOLD/BLOCK) — projections distinctes.
        for status in (BATCH_EXECUTION_NOT_READY, BATCH_PLANNED, BATCH_COMPLETE, BATCH_PARTIAL, BATCH_HOLD):
            assert status not in ("ACT", "HOLD", "BLOCK")

    def test_protected_target_refused_defense_in_depth(self, tmp_path):
        entries = [_synthetic_entry("prot1", "proofs/whatever.json", "h1")]
        entries[0]["source_path"] = "elsewhere/whatever.json"
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["prot1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        # Le Selector exclut deja les cibles protegees (PROTECTED),
        # donc ce candidat ne doit meme pas apparaitre selectionne.
        assert len(env["children"]) == 0
        assert env["aggregate_status"] == BATCH_EXECUTION_NOT_READY


# --- TestApprovalArtifactStorage (append-only, no-overwrite, integrite) ------

class TestApprovalArtifactStorage:
    def _envelope(self, tmp_path):
        entries = [_synthetic_entry("stor1", "periphery/stor1.py", _materialize_source(tmp_path, "stor1", b"S\n"))]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["stor1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        return env, ed

    def test_store_creates_exactly_once(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        r1 = store_approval_artifact(record, ed)
        assert r1["status"] == "STORED"

    def test_store_exact_duplicate_idempotent(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        store_approval_artifact(record, ed)
        r2 = store_approval_artifact(record, ed)
        assert r2["status"] == "IDEMPOTENT_ALREADY_EXISTS"

    def test_store_same_id_different_content_refused(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id="fixed_id")
        store_approval_artifact(record, ed)
        different = _build_synthetic_approval_record(
            env, overrides={"batch_hash": "different_hash"}, approval_id="fixed_id",
        )
        result = store_approval_artifact(different, ed)
        assert result["status"] == "APPROVAL_IMMUTABILITY_VIOLATION"

    def test_overwrite_attempt_leaves_bytes_unchanged(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id="fixed_id2")
        store_approval_artifact(record, ed)
        p = _approval_path("fixed_id2", ed)
        before = p.read_bytes()

        different = _build_synthetic_approval_record(
            env, overrides={"approved_by": "AGENT"}, approval_id="fixed_id2",
        )
        store_approval_artifact(different, ed)  # doit etre refuse
        after = p.read_bytes()
        assert before == after

    def test_verify_valid_record(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        ok, reason = verify_approval_artifact(record)
        assert ok is True
        assert reason is None

    def test_verify_none_record(self):
        ok, reason = verify_approval_artifact(None)
        assert ok is False
        assert reason == "APPROVAL_MISSING"

    def test_verify_hash_mismatch_detected(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        record["approval_record_hash"] = "corrupted_hash_value"
        ok, reason = verify_approval_artifact(record)
        assert ok is False
        assert reason == "APPROVAL_RECORD_HASH_MISMATCH"

    def test_verify_missing_field_detected(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        del record["approved_by"]
        ok, reason = verify_approval_artifact(record)
        assert ok is False
        assert "APPROVAL_FIELD_MISSING" in reason

    def test_load_unknown_returns_none(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        assert load_approval_artifact("does_not_exist", ed) is None

    def test_compute_hash_changes_with_any_bound_field(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        r1 = _build_synthetic_approval_record(env)
        r2 = _build_synthetic_approval_record(env, overrides={"approved_by": "NOT_HUMAN"})
        assert compute_approval_record_hash(r1) != compute_approval_record_hash(r2)


# --- TestApprovalIdSafety (HARDEN_APPROVAL_ARTIFACT_STORAGE_ATOMICITY_V0) -----

class TestApprovalIdSafety:
    """approval_id est un IDENTIFIANT, jamais un chemin. Validation
    lexicale + confinement structurel, testes cote store ET load."""

    def _envelope(self, tmp_path):
        entries = [_synthetic_entry("idsafe1", "periphery/idsafe1.py", _materialize_source(tmp_path, "idsafe1", b"I\n"))]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["idsafe1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        return env, ed

    _MALFORMED_IDS = [
        "../escape",
        "../../escape",
        "..\\escape",
        "foo/bar",
        "foo\\bar",
        "",
        ".",
        "..",
    ]

    @pytest.mark.parametrize("bad_id", _MALFORMED_IDS)
    def test_store_rejects_malformed_id(self, tmp_path, bad_id):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id=bad_id) if bad_id else None
        if record is None:
            # id vide : construire quand meme un record avec cet id explicite
            record = _build_synthetic_approval_record(env)
            record["approval_id"] = bad_id
            record["approval_record_hash"] = compute_approval_record_hash(record)
        result = store_approval_artifact(record, ed)
        assert result["status"] == "INVALID_APPROVAL_ID"
        # Rien ecrit hors du magasin canonique (ni meme dedans, pour un ID invalide)
        approvals_dir = ed / "approvals"
        if approvals_dir.exists():
            for p in approvals_dir.rglob("*"):
                assert p.is_dir() or p.name == "approval.json"

    @pytest.mark.parametrize("bad_id", _MALFORMED_IDS)
    def test_load_rejects_malformed_id(self, tmp_path, bad_id):
        env, ed = self._envelope(tmp_path)
        assert load_approval_artifact(bad_id, ed) is None

    def test_store_rejects_absolute_path_id(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env)
        record["approval_id"] = str(tmp_path / "escaped")
        record["approval_record_hash"] = compute_approval_record_hash(record)
        result = store_approval_artifact(record, ed)
        assert result["status"] == "INVALID_APPROVAL_ID"

    def test_no_file_created_outside_approvals_dir(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id="../escape_attempt")
        record["approval_record_hash"] = compute_approval_record_hash(record)
        store_approval_artifact(record, ed)
        escape_target = ed / "escape_attempt"
        assert not escape_target.exists()

    def test_valid_id_still_works(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id="valid_id-123")
        result = store_approval_artifact(record, ed)
        assert result["status"] == "STORED"
        assert load_approval_artifact("valid_id-123", ed) is not None

    def test_run_execution_with_malformed_approval_id_zero_calls(self, tmp_path):
        env, ed = self._envelope(tmp_path)
        called = []

        def executor(child):
            called.append(child)
            return {"kx108_decision": "ACT"}

        result = run_execution(env["batch_execution_id"], "../escape", executor, ed, tmp_path)
        assert called == []
        assert "APPROVAL_MISSING" in result["execution_approval_status"]


# --- TestApprovalConcurrency ----------------------------------------------------

class TestApprovalConcurrency:
    def _envelope(self, tmp_path):
        entries = [_synthetic_entry("conc1", "periphery/conc1.py", _materialize_source(tmp_path, "conc1", b"C\n"))]
        proposal, ld, sd, ed = _prepare_synthetic_batch(tmp_path, entries, ["conc1"])
        env = prepare_execution(proposal["batch_id"], ld, sd, ed, repo_root=tmp_path)
        return env, ed

    def test_concurrent_different_content_no_double_store(self, tmp_path):
        import threading
        env, ed = self._envelope(tmp_path)
        record_a = _build_synthetic_approval_record(env, overrides={"approved_by": "HUMAN"}, approval_id="race_id")
        record_b = _build_synthetic_approval_record(env, overrides={"approved_by": "AGENT"}, approval_id="race_id")

        results = []
        barrier = threading.Barrier(2)

        def worker(record):
            barrier.wait()
            results.append(store_approval_artifact(record, ed))

        t1 = threading.Thread(target=worker, args=(record_a,))
        t2 = threading.Thread(target=worker, args=(record_b,))
        t1.start(); t2.start()
        t1.join(); t2.join()

        statuses = sorted(r["status"] for r in results)
        assert statuses == ["APPROVAL_IMMUTABILITY_VIOLATION", "STORED"]

        # Exactement UNE version de contenu sur disque, correspondant a
        # celui qui a reellement gagne la creation exclusive.
        stored = load_approval_artifact("race_id", ed)
        assert stored is not None
        assert stored["approved_by"] in ("HUMAN", "AGENT")
        winner = record_a if stored["approved_by"] == "HUMAN" else record_b
        assert stored == winner

    def test_concurrent_identical_content_idempotent(self, tmp_path):
        import threading
        env, ed = self._envelope(tmp_path)
        record = _build_synthetic_approval_record(env, approval_id="race_id_same")

        results = []
        barrier = threading.Barrier(2)

        def worker():
            barrier.wait()
            results.append(store_approval_artifact(record, ed))

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start(); t2.start()
        t1.join(); t2.join()

        statuses = sorted(r["status"] for r in results)
        assert statuses == ["IDEMPOTENT_ALREADY_EXISTS", "STORED"]

        stored = load_approval_artifact("race_id_same", ed)
        assert stored == record
