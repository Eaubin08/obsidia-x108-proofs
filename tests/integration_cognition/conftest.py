"""Shared fixtures for the cognition integration suites."""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_brody_session_journals(tmp_path, monkeypatch):
    """Redirect Brody session journals to a per-test temporary directory.

    Public Brody calls journal every turn under _local_audits/brody_sessions;
    tests must never append to the operational ledgers of the workspace.
    """
    from apps.obsidia_api import brody_automation_orchestrator as orch

    monkeypatch.setattr(orch, "_SESSIONS", tmp_path / "_local_audits" / "brody_sessions")


@pytest.fixture(autouse=True)
def _isolated_memory_candidate_ledger(tmp_path, monkeypatch):
    """Redirect the memory candidate ledger (cwd-relative by default) to a temp file."""
    from periphery.memory import memory_candidate_ledger

    monkeypatch.setattr(memory_candidate_ledger, "_DEFAULT_LEDGER_PATH", tmp_path / "memory_candidate_ledger.jsonl")
