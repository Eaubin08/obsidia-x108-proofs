"""Shared fixtures for the non-sovereignty suites."""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_memory_candidate_ledger(tmp_path, monkeypatch):
    """Tests must never append to the workspace memory candidate ledger."""
    from periphery.memory import memory_candidate_ledger

    monkeypatch.setattr(memory_candidate_ledger, "_DEFAULT_LEDGER_PATH", tmp_path / "memory_candidate_ledger.jsonl")
