from __future__ import annotations

import importlib.util
import json
from dataclasses import fields, is_dataclass
import sys
from pathlib import Path
from collections.abc import Mapping

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidure_cli_supervised_r12 as cli

_R10_PATH = ROOT / "tests" / "test_r10_b3_obsidure_repair_outcome_feedback.py"
_spec = importlib.util.spec_from_file_location("_r10_b3_helpers", _R10_PATH)
_r10 = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_r10)


def _jsonable(value):
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _jsonable(to_dict())
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _context_file(tmp_path: Path, agent, prepared, *, mission_context=None) -> Path:
    path = tmp_path / "r10_outcome_context.json"
    path.write_text(
        json.dumps(
            {
                "repair_request": agent._last_repair_request.to_dict(),
                "repair_proposal": agent._last_repair_proposal.to_dict(),
                "repair_verdict": agent._last_repair_verdict.to_dict(),
                "prepared_repair": _jsonable(prepared),
                "mission_context": mission_context
                or {"status": "ACTIVE", "allowed_targets": [_r10.TARGET], "max_attempts": 3, "attempt_index": 1},
                "repair_budget": 5,
                "attempt_history": [{"attempt_id": "attempt-f8d"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _projection(action_id: str) -> dict:
    return {
        "status": "PROJECTED",
        "mission_id": "mission-f8d",
        "checkpoint": {"checkpoint_id": "chk-f8d"},
        "tickets": [
            {
                "ticket_id": "ticket-f8d",
                "phase": "AWAITING_INDEPENDENT_VERIFICATION",
                "status": "HELD",
                "action_evidence_id": action_id,
                "evidence_refs": [action_id],
            }
        ],
        "evidence": {"action_evidence_refs": [action_id]},
        "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
        "verification": {"ticket_levels": {"ticket-f8d": "VERIFIED_WITH_LIMITS"}},
    }


def _args(world, context_file: Path, action_id: str, **overrides):
    args = {
        "mission_id": "mission-f8d",
        "checkpoint_id": "chk-f8d",
        "ticket_id": "ticket-f8d",
        "action_evidence_id": action_id,
        "stores_base_dir": str(world["stores"]),
        "repair_context_file": str(context_file),
        "json": True,
    }
    args.update(overrides)
    return args


def test_outcome_ingests_real_r8_r10_evidence_without_claiming_closure(tmp_path, monkeypatch, capsys):
    world, agent, prepared = _r10._prepared_fixture(tmp_path, monkeypatch)
    execution = _r10._store_apply_patch_outcome(world, prepared)
    action_id = execution["action_evidence_id"]
    context_file = _context_file(tmp_path, agent, prepared)
    receipt_path = _r10._receipt_path(world, action_id)
    before_receipt = receipt_path.read_bytes()

    calls = []

    def fake_api(api, method, path, *, query=None, body=None):
        calls.append((method, path, query, body))
        return 200, _projection(action_id)

    monkeypatch.setattr(cli, "_api_json", fake_api)

    rc = cli.run_supervised("outcome", "http://obsidia.test", _args(world, context_file, action_id))

    assert rc == 0
    assert calls == [("GET", "/api/supervised-missions/mission-f8d/projection", {"checkpoint_id": "chk-f8d"}, None)]
    out = json.loads(capsys.readouterr().out)
    assert out["derived_outcome_classification"] == "EXECUTED_VERIFIED"
    assert out["recommendation"] == "STOP_SUCCESS"
    assert out["stop_success"] is True
    assert out["limited_verdict"] is True
    assert out["binder_limitations_preserved"] is True
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" in out["r10_outcome_feedback"]["r8_evidence_limits"]
    assert out["execution_observed_is_verified"] is False
    assert out["verified"] is False
    assert out["closed"] is False
    assert out["mission_done_verified"] is False
    assert out["executor_invoked"] is False
    assert out["memory_write"] is False
    assert receipt_path.read_bytes() == before_receipt


def test_outcome_rejects_projection_evidence_mismatch_before_r10_context(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_api(api, method, path, *, query=None, body=None):
        calls.append((method, path, query, body))
        return 200, _projection("aev-other")

    monkeypatch.setattr(cli, "_api_json", fake_api)

    rc = cli.run_supervised(
        "outcome",
        "http://obsidia.test",
        {
            "mission_id": "mission-f8d",
            "checkpoint_id": "chk-f8d",
            "ticket_id": "ticket-f8d",
            "action_evidence_id": "aev-requested",
            "stores_base_dir": str(tmp_path / "stores"),
            "repair_context_file": str(tmp_path / "missing.json"),
            "json": True,
        },
    )

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["reason"] == "ACTION_EVIDENCE_ID_PROJECTION_MISMATCH"
    assert out["executor_invoked"] is False
    assert calls == [("GET", "/api/supervised-missions/mission-f8d/projection", {"checkpoint_id": "chk-f8d"}, None)]


def test_outcome_real_disposable_pre_dispatch_receipt_stays_blocked(tmp_path, monkeypatch, capsys):
    world, agent, prepared = _r10._prepared_fixture(tmp_path, monkeypatch)
    execution = _r10._execute(world, prepared)
    action_id = execution["action_evidence_id"]
    context_file = _context_file(tmp_path, agent, prepared)
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: (200, _projection(action_id)))

    rc = cli.run_supervised("outcome", "http://obsidia.test", _args(world, context_file, action_id))

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["stop_success"] is False
    assert out["closed"] is False
    assert out["verified"] is False
    assert out["r10_outcome_feedback"]["r8_replay_verdict"] == "VERIFIED"
    assert out["recommendation"] in {"STOP_BLOCKED", "ESCALATE"}
    assert out["executor_invoked"] is False


def test_outcome_missing_receipt_is_escalated_not_success(tmp_path, monkeypatch, capsys):
    world, agent, prepared = _r10._prepared_fixture(tmp_path, monkeypatch)
    action_id = "aev-" + "0" * 32
    context_file = _context_file(tmp_path, agent, prepared)
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: (200, _projection(action_id)))

    rc = cli.run_supervised("outcome", "http://obsidia.test", _args(world, context_file, action_id))

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["derived_outcome_classification"] == "EVIDENCE_INCOMPLETE"
    assert out["recommendation"] == "ESCALATE"
    assert out["stop_success"] is False
    assert out["closed"] is False
    assert out["r10_outcome_feedback"]["reason"] == "ACTION_EVIDENCE_NOT_FOUND"


def test_outcome_requires_explicit_context_and_store_without_posting(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: pytest.fail("api must not be called"))

    rc = cli.run_supervised(
        "outcome",
        "http://obsidia.test",
        {
            "mission_id": "mission-f8d",
            "checkpoint_id": "chk-f8d",
            "ticket_id": "ticket-f8d",
            "json": True,
        },
    )

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["reason"] == "ACTION_EVIDENCE_ID_REQUIRED"
    assert out["physical_mutation"] is False
