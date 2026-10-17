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
