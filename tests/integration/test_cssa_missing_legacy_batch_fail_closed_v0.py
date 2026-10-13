"""Regression: absent historical batch remains fail-closed, never fabricates children.

This does NOT replace the legacy five-child conformance fixture.
"""
from pathlib import Path
from scripts.obsidia_batch_execution import prepare_execution

def test_missing_legacy_batch_returns_explicit_error_without_execution(tmp_path: Path):
    envelope=prepare_execution(
        "84a929c6f48a90c5",
        ledger_dir=tmp_path/"ledger",
        selector_dir=tmp_path/"selector",
        execution_dir=tmp_path/"execution",
        repo_root=tmp_path,
    )
    assert envelope["aggregate_status"]=="BATCH_ERROR"
    assert envelope["integrity_error"]=="BATCH_PROPOSAL_NOT_FOUND"
    assert envelope["children"]==[]
    assert envelope["human_execution_approved"] is False
