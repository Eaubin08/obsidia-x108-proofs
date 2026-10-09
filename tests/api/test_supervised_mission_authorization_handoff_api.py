from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api import main as api_main
from apps.obsidia_api.main import app
from apps.obsidia_api.routes import supervised_missions as S
from tests.api.test_supervised_mission_prepare_ingress_api import (
    AFTER,
    BEFORE,
    TARGET,
    _install_paths,
    _request,
    _world,
)

client = TestClient(app)


def _prepare(monkeypatch, world: dict[str, object]) -> dict[str, object]:
    _install_paths(monkeypatch, world)
    response = client.post("/api/supervised-missions/prepare-only", json=_request(world))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.PREPARE_STATUS_ACCEPTED
    return data


def _prepared_eah(world: dict[str, object]) -> str:
    v2exec = Path(world["prepare_store"]) / "v2exec"
    records = sorted(v2exec.glob("v2x-*.json"))
    assert records
    return json.loads(records[0].read_text(encoding="utf-8"))["eah"]


def _auth_payload(world: dict[str, object], prepared: dict[str, object], **overrides: object) -> dict[str, object]:
    payload = {
        "checkpoint_id": prepared["checkpoint_id"],
        "ticket_id": "ticket-mission-r12-f6-c1-prepare",
        "execution_authority_hash": _prepared_eah(world),
        "human_authorization_reference": "human-auth:r12-f6-d1:disposable",
        "session_id": "r12-f6-d1-test",
    }
    payload.update(overrides)
    return payload


def _auth(world: dict[str, object], prepared: dict[str, object], **overrides: object):
    return client.post(
        f"/api/supervised-missions/{prepared['mission_id']}/authorize-execution",
        json=_auth_payload(world, prepared, **overrides),
    )


def _checkpoint_path(world: dict[str, object], checkpoint_id: str) -> Path:
    matches = list(Path(world["checkpoint_store"]).glob(f"{checkpoint_id}*.json"))
    assert matches
    return matches[0]


def _mutate_checkpoint(world: dict[str, object], checkpoint_id: str, mutate):
    path = _checkpoint_path(world, checkpoint_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, sort_keys=True, indent=2), encoding="utf-8", newline="\n")


def _record(world: dict[str, object], checkpoint_id: str) -> dict[str, object]:
    return json.loads(_checkpoint_path(world, checkpoint_id).read_text(encoding="utf-8"))


def _serve_record(monkeypatch, record: dict[str, object]) -> None:
    original = S.load_supervised_mission_checkpoint

    def fake_load(checkpoint_id, *, checkpoint_store_dir=None):
        if checkpoint_id == record["checkpoint_id"]:
            return record, None
        return original(checkpoint_id, checkpoint_store_dir=checkpoint_store_dir)

    monkeypatch.setattr(S, "load_supervised_mission_checkpoint", fake_load)


def test_valid_authorized_disposable_execution_projects_observed_outcome(monkeypatch, tmp_path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)

    response = _auth(world, prepared)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.AUTH_STATUS_ACCEPTED
    assert data["state"] in {"EXECUTED_OBSERVED", "EXECUTION_FAILED", "OUTCOME_UNCERTAIN"}
    assert data["execution_phase"] == "EXECUTED_OBSERVED"
    assert data["executor_invoked"] is True
    assert data["approval_created"] is False
    assert data["supervisor_approval_created"] is False
    assert data["memory_write"] is False
    assert data["action_evidence_id"].startswith("aev-")
    assert data["r10_repair_classification"]["automatic_retry"] is False
    assert data["checkpoint_projection_available"] is True
    assert data["checkpoint_projection"]["tickets"][0]["phase"] == "AWAITING_INDEPENDENT_VERIFICATION"
    assert (Path(world["exec_wt"]) / TARGET).read_text(encoding="utf-8") == AFTER


def test_missing_or_wrong_authorization_holds_before_executor(monkeypatch, tmp_path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)

    missing = _auth(world, prepared, human_authorization_reference="")
    assert missing.status_code == 200
    missing_data = missing.json()
    assert missing_data["status"] == S.AUTH_STATUS_HELD
    assert missing_data["reason"] == S.HOLD_AWAITING_VALID_AUTHORIZATION
    assert missing_data["executor_invoked"] is False

    wrong = _auth(world, prepared, execution_authority_hash="a" * 64)
    assert wrong.status_code == 200
    wrong_data = wrong.json()
    assert wrong_data["status"] == S.AUTH_STATUS_HELD
    assert wrong_data["reason"] in {S.HOLD_AWAITING_VALID_AUTHORIZATION, "PREPARED_DESCRIPTOR_NOT_FOUND"}
    assert wrong_data["executor_invoked"] is False
    assert (Path(world["exec_wt"]) / TARGET).read_text(encoding="utf-8") == BEFORE


def test_wrong_ticket_revoked_mandate_dirty_worktree_and_budget_hold(monkeypatch, tmp_path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)

    wrong_ticket = _auth(world, prepared, ticket_id="ticket-other").json()
    assert wrong_ticket["status"] == S.AUTH_STATUS_REJECTED
    assert wrong_ticket["reason"] == "PREPARED_TICKET_NOT_FOUND"

    revoked_record = _record(world, str(prepared["checkpoint_id"]))
    revoked_record["accepted_state"].update({"mandate_revoked": True})
    _serve_record(monkeypatch, revoked_record)
    revoked = _auth(world, prepared).json()
    assert revoked["status"] == S.AUTH_STATUS_HELD
    assert revoked["execution_outcome"]["reason"] == "HUMAN_MANDATE_REVOKED"

    dirty_root = tmp_path / "dirty"
    dirty_root.mkdir()
    world2 = _world(dirty_root)
    prepared2 = _prepare(monkeypatch, world2)
    (Path(world2["exec_wt"]) / "dirty.txt").write_text("dirty", encoding="utf-8")
    dirty = _auth(world2, prepared2).json()
    assert dirty["status"] == S.AUTH_STATUS_HELD
    assert dirty["reason"] == "WORKTREE_DIRTY"

    budget_root = tmp_path / "budget"
    budget_root.mkdir()
    world3 = _world(budget_root)
    prepared3 = _prepare(monkeypatch, world3)
    budget_record = _record(world3, str(prepared3["checkpoint_id"]))
    budget_record["accepted_state"].setdefault("global_budget", {}).update({"remaining_actions": 0})
    _serve_record(monkeypatch, budget_record)
    exhausted = _auth(world3, prepared3).json()
    assert exhausted["status"] == S.AUTH_STATUS_HELD
    assert exhausted["execution_outcome"]["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_scope_dependency_duplicate_and_missing_receipt_fail_closed(monkeypatch, tmp_path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)

    scope_record = _record(world, str(prepared["checkpoint_id"]))
    scope_record["accepted_state"]["tickets"][0].update({"authorized_paths": ["scripts/other.py"]})
    _serve_record(monkeypatch, scope_record)
    scope = _auth(world, prepared).json()
    assert scope["status"] == S.AUTH_STATUS_HELD
    assert scope["reason"] == "TICKET_TARGET_SCOPE_EXCEEDED"

    blocked_root = tmp_path / "blocked"
    blocked_root.mkdir()
    world2 = _world(blocked_root)
    prepared2 = _prepare(monkeypatch, world2)
    blocked_record = _record(world2, str(prepared2["checkpoint_id"]))
    blocked_record["dependency_projection"].update(
        {"transitive_dependency_blocks": [{"ticket_id": "ticket-mission-r12-f6-c1-prepare", "reason": "BLOCKED_BY_HOLD(upstream)"}]}
    )
    _serve_record(monkeypatch, blocked_record)
    blocked = _auth(world2, prepared2).json()
    assert blocked["status"] == S.AUTH_STATUS_HELD
    assert blocked["execution_outcome"]["reason"] == "TICKET_BLOCKED_BY_DEPENDENCY"

    duplicate_root = tmp_path / "duplicate"
    duplicate_root.mkdir()
    world3 = _world(duplicate_root)
    prepared3 = _prepare(monkeypatch, world3)
    duplicate_record = _record(world3, str(prepared3["checkpoint_id"]))
    duplicate_record["accepted_state"]["tickets"][0].update({"action_evidence_id": "aev-existing"})
    _serve_record(monkeypatch, duplicate_record)
    duplicate = _auth(world3, prepared3).json()
    assert duplicate["status"] == S.AUTH_STATUS_HELD
    assert duplicate["reason"] == "DUPLICATE_EXECUTION_REQUIRES_RECONCILIATION"

    receipt_root = tmp_path / "receipt"
    receipt_root.mkdir()
    world4 = _world(receipt_root)
    prepared4 = _prepare(monkeypatch, world4)
    eah4 = _prepared_eah(world4)
    descriptor4 = json.loads(next((Path(world4["prepare_store"]) / "v2exec").glob("v2x-*.json")).read_text(encoding="utf-8"))
    record4 = _record(world4, str(prepared4["checkpoint_id"]))
    proposal4 = next(ref for ref in record4["accepted_state"]["tickets"][0]["evidence_refs"] if ref.startswith("step-"))

    def fake_execute(**_kwargs):
        return {
            "status": S.F5B_STATUS_HELD,
            "reason": "R8_RECEIPT_MISSING",
            "execution_phase": "OUTCOME_UNCERTAIN",
            "executor_invoked": True,
            "mission_id": prepared4["mission_id"],
            "selected_ticket_id": "ticket-mission-r12-f6-c1-prepare",
            "mandate_reference": "mandate-r12-f6-c1",
            "prepared_proposal_id": proposal4,
            "prepared_patch_hash": descriptor4["descriptor"]["patch_sha256"],
            "authority_reference": {"execution_authority_hash": eah4},
        }

    monkeypatch.setattr(S, "execute_supervised_governed_ticket", fake_execute)
    uncertain = _auth(world4, prepared4).json()
    assert uncertain["status"] == S.AUTH_STATUS_HELD
    assert uncertain["reason"] in {"ACTION_EVIDENCE_ID_REQUIRED", "R8_RECEIPT_MISSING"}
    assert uncertain["executor_invoked"] is True


def test_authorization_handoff_api_key_policy(monkeypatch, tmp_path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "secret")

    denied = _auth(world, prepared)

    assert denied.status_code == 401
    assert denied.json()["error"] == "unauthorized"
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "")
