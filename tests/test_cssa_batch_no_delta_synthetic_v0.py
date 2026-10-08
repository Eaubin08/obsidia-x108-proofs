"""CSSA regression: explicitly SYNTHETIC five-child no-delta batch.

This does not recreate, replace or attest historical batch 84a929c6f48a90c5.
Only isolated tmp_path state is used; no real approval, execution or kernel action.
"""
from __future__ import annotations

import hashlib

from test_batch_execution_v0 import (
    _synthetic_entry,
    _prepare_synthetic_batch,
    prepare_execution,
    verify_batch_integrity,
    executable_candidate_count,
    NOT_READY_NO_DELTA,
    NO_MEANINGFUL_DELTA,
    BATCH_EXECUTION_NOT_READY,
)


def _five_child_no_delta_fixture(tmp_path):
    entries = []
    ids = []
    for index in range(5):
        eid = f"cssa_no_delta_{index}"
        relative = f"synthetic_cssa/target_{index}.txt"
        data = f"CSSA_SYNTHETIC_READONLY_{index}\n".encode("utf-8")
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        entry = _synthetic_entry(
            eid, relative, hashlib.sha256(data).hexdigest()[:16],
        )
        # Intentional identical source and target path: no meaningful delta.
        entry["source_path"] = relative
        entries.append(entry)
        ids.append(eid)
    proposal, ledger_dir, selector_dir, execution_dir = _prepare_synthetic_batch(
        tmp_path, entries, ids, objective="CSSA_SYNTHETIC_NO_DELTA_ONLY",
    )
    assert proposal["batch_id"] != "84a929c6f48a90c5"
    return proposal, ledger_dir, selector_dir, execution_dir


def test_synthetic_five_child_integrity_and_refusal(tmp_path):
    proposal, ledger_dir, selector_dir, execution_dir = _five_child_no_delta_fixture(tmp_path)
    verified, error = verify_batch_integrity(proposal, ledger_dir)
    assert verified is True, error

    result = prepare_execution(
        proposal["batch_id"], ledger_dir, selector_dir, execution_dir,
        repo_root=tmp_path,
    )
    assert result["integrity_verified"] is True
    assert result["decision_authority"] == "KX108_ONLY"
    assert len(result["children"]) == 5
    assert executable_candidate_count(result) == 0
    assert result["aggregate_status"] == BATCH_EXECUTION_NOT_READY
    assert result["human_execution_approved"] is False
    for child in result["children"]:
        assert child["materiality_status"] == NO_MEANINGFUL_DELTA
        assert child["execution_status"] == NOT_READY_NO_DELTA
        assert child["session_id"] is None
        assert child["kx108_decision"] is None
        assert child["decision_authority"] == "KX108_ONLY"


def test_synthetic_prepare_preserves_all_five_targets(tmp_path):
    proposal, ledger_dir, selector_dir, execution_dir = _five_child_no_delta_fixture(tmp_path)
    before = {
        path.name: path.read_bytes()
        for path in (tmp_path / "synthetic_cssa").iterdir()
    }
    prepare_execution(
        proposal["batch_id"], ledger_dir, selector_dir, execution_dir,
        repo_root=tmp_path,
    )
    after = {
        path.name: path.read_bytes()
        for path in (tmp_path / "synthetic_cssa").iterdir()
    }
    assert after == before
