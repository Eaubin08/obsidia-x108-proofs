"""
tests/integration_cognition/test_journal_isolation_red.py

RED contract: running the cognition test suite through Brody's public entry
point must never write into the operational session journals of the
workspace (_local_audits/brody_sessions). Session records produced during
tests must land in an isolated temporary directory.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OPERATIONAL_SESSIONS = ROOT / "_local_audits" / "brody_sessions"


def _snapshot(base: Path) -> dict[str, tuple[int, int]]:
    if not base.exists():
        return {}
    return {
        str(p.relative_to(base)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in base.rglob("*")
        if p.is_file()
    }


def test_journal_isolation_orchestrator_points_outside_workspace():
    from apps.obsidia_api import brody_automation_orchestrator as orch

    sessions = Path(orch._SESSIONS).resolve()
    assert sessions != OPERATIONAL_SESSIONS.resolve()
    assert OPERATIONAL_SESSIONS.resolve() not in sessions.parents


@pytest.mark.asyncio
async def test_journal_isolation_public_brody_chat_leaves_operational_journal_untouched():
    from apps.obsidia_api import brody_automation_orchestrator as orch
    from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat

    before = _snapshot(OPERATIONAL_SESSIONS)
    res = await brody_chat(
        BrodyChatRequest(message="Quel est l'état de la pompe principale ?", language="fr", allow_local_model=False)
    )
    after = _snapshot(OPERATIONAL_SESSIONS)

    assert res.get("decision_authority") == "KX108_ONLY"
    assert after == before, "public Brody call during tests wrote into operational session journals"
    # The call must still be journaled, but only inside the isolated directory.
    assert any(Path(orch._SESSIONS).rglob("SESSION_LEDGER.jsonl"))
