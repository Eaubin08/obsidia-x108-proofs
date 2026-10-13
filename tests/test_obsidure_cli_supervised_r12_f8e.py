from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidure_cli_supervised_r12 as cli

_R10_PATH = ROOT / "tests" / "test_obsidure_cli_supervised_r12_f8d.py"
_spec = importlib.util.spec_from_file_location("_f8d_helpers", _R10_PATH)
_f8d = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_f8d)


def test_operator_inspect_displays_status_lineage_and_binder_limits(monkeypatch, capsys):
    projection = {
        "status": "PROJECTED",
        "mission_id": "mission-f8e",
        "checkpoint": {"checkpoint_id": "chk-f8e"},
        "project": {
            "repository_identity": "repo://f8e",
            "worktree": "C:/tmp/f8e",
            "branch": "f8e",
            "base_sha": "a" * 40,
        },
        "tickets": [
            {
                "ticket_id": "ticket-f8e",
                "phase": "PREPARED_AWAITING_APPROVAL",
                "status": "HELD",
                "hold_reason": "PREPARED_AWAITING_APPROVAL",
                "evidence_refs": ["b" * 64],
            }
        ],
        "hold": {"reason": "PREPARED_AWAITING_APPROVAL"},
        "binder_replay": {
            "status": "INLINE_STATUS_ONLY",
            "limitations": [
                "BINDER_INDEPENDENT_REPLAY_NOT_PROVEN",
                "BINDER_DECISION_RECONSTRUCTION_REQUIRED",
            ],
        },
        "verification": {"ticket_levels": {"ticket-f8e": "VERIFIED_WITH_LIMITS"}},
    }
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: (200, projection))

    rc = cli.run_supervised("inspect", "http://obsidia.test", {"checkpoint_id": "chk-f8e"})

    assert rc == 0
    out = capsys.readouterr().out
    assert "mission_id=mission-f8e" in out
    assert "ticket[ticket-f8e].phase=PREPARED_AWAITING_APPROVAL" in out
    assert "hold_reason=PREPARED_AWAITING_APPROVAL" in out
    assert "binder.status=INLINE_STATUS_ONLY" in out
    assert "BINDER_DECISION_RECONSTRUCTION_REQUIRED" in out
    assert "verification.ticket_levels" in out


def test_operator_authorize_displays_observed_execution_without_closure(monkeypatch, capsys):
    projection = _f8d._projection("aev-f8e")
    projection["mission_id"] = "mission-f8"
    projection["tickets"][0].update(
        {
            "phase": "PREPARED",
            "action_evidence_id": None,
            "evidence_refs": ["c" * 64],
        }
    )
    projection["project"] = {
        "repository_identity": "repo://f8e",
        "worktree": "C:/tmp/f8e",
        "branch": "f8e",
        "base_sha": "a" * 40,
    }
    calls = []

    def fake_api(api, method, path, *, query=None, body=None):
        calls.append((method, path, query, body))
        if method == "POST":
            return 200, {
                "status": "R12_F6_D1_EXECUTION_OUTCOME_ACCEPTED",
                "state": "EXECUTED_OBSERVED",
                "mission_id": "mission-f8",
                "checkpoint_id": "chk-after",
                "ticket_id": "ticket-f8d",
                "execution_phase": "EXECUTED_OBSERVED",
                "action_evidence_id": "aev-f8e",
                "executor_invoked": True,
            }
        return 200, projection

    monkeypatch.setattr(cli, "_api_json", fake_api)

    rc = cli.run_supervised(
        "authorize",
        "http://obsidia.test",
        {
            "mission_id": "mission-f8",
            "checkpoint_id": "chk-f8d",
            "ticket_id": "ticket-f8d",
            "execution_authority_hash": "d" * 64,
            "human_authorization_reference": "human-test-f8e",
            "confirm_human_authorization": True,
        },
    )

    assert rc == 0
    out = capsys.readouterr().out
    assert "state=EXECUTED_OBSERVED" in out
    assert "execution_phase=EXECUTED_OBSERVED" in out
    assert "action_evidence_id=aev-f8e" in out
    assert "http_success_is_closure=False" in out
    assert "verified=False" in out
    assert "closed=False" in out
    assert "mission_done_verified=False" in out
    assert calls[1][1] == "/api/supervised-missions/mission-f8/authorize-execution"


def test_operator_outcome_displays_r10_advisory_and_limited_evidence(tmp_path, monkeypatch, capsys):
    world, agent, prepared = _f8d._r10._prepared_fixture(tmp_path, monkeypatch)
    execution = _f8d._r10._store_apply_patch_outcome(world, prepared)
    action_id = execution["action_evidence_id"]
    context_file = _f8d._context_file(tmp_path, agent, prepared)
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: (200, _f8d._projection(action_id)))

    rc = cli.run_supervised(
        "outcome",
        "http://obsidia.test",
        _f8d._args(world, context_file, action_id, json=False),
    )

    assert rc == 0
    out = capsys.readouterr().out
    assert "r10.classification=EXECUTED_VERIFIED" in out
    assert "r10.recommendation=STOP_SUCCESS" in out
    assert "r10.limited_verdict=True" in out
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" in out
    assert "r10.r8_reconciliation_status=MATCH" in out
    assert "verified=False" in out
    assert "closed=False" in out
    assert "mission_done_verified=False" in out
