from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api import main as api_main
from apps.obsidia_api.main import app
from apps.obsidia_api.routes import supervised_missions as S
from scripts import obsidure_supervised_mission_checkpoint_v1 as C
from scripts.obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state
from scripts.obsidure_supervised_mission_state_v1 import canonical_json, project_supervised_mission_state
from scripts.obsidure_supervised_mission_stepper_v1 import propose_supervised_mission_step

client = TestClient(app)

BASE_SHA = "a" * 40


def _ticket(ticket_id, *, deps=(), status="PENDING", evidence=(), hold_reason="", receipt_refs=()):
    return {
        "ticket_id": ticket_id,
        "objective": f"Prepare {ticket_id}",
        "dependency_ids": list(deps),
        "status": status,
        "authorized_paths": ["scripts/example.py"],
        "authorized_operations": ["MODIFY"],
        "acceptance_criteria": ["prepared only"],
        "evidence_refs": list(evidence),
        "receipt_refs": list(receipt_refs),
        "unknowns": ["unknown-preserved"],
        "hold_reason": hold_reason,
    }


def _mission(tickets, *, mandate_status="ACTIVE", remaining_actions=5):
    return {
        "mission_id": "mission-r12-f6b1",
        "human_mandate_reference": "mandate-r12-f6b1",
        "repository_identity": "repo://obsidia/f6b1",
        "local_root": "C:/work/repo",
        "worktree": "C:/work/repo",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": BASE_SHA,
        "original_goal": "Expose supervised mission state through readonly API.",
        "acceptance_criteria": ["readonly projection is stable"],
        "bounded_authorized_scope": {"authorized_paths": ["scripts/example.py"], "authorized_operations": ["MODIFY"]},
        "tickets": tickets,
        "global_budget": {"remaining_actions": remaining_actions, "remaining_tickets": 5},
        "timebox": {"expired": False},
        "evidence_refs": ["mandate-evidence"],
        "explicit_unknowns": ["semantic-unknown-preserved"],
        "mission_authority": "KX108_ONLY",
        "mandate_status": mandate_status,
        "source_ids": ["r12-f6b1-test"],
    }


def _hash(value):
    return C._sha256(value)


def _feedback(projection, step):
    proposal = step["step_proposal"]
    return {
        "feedback_id": "feedback-f6b1",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": _hash(proposal),
        "mission_id": proposal["mission_id"],
        "selected_ticket_id": proposal["selected_ticket_id"],
        "mandate_reference": proposal["mandate_reference"],
        "project": dict(proposal["project"]),
        "preparation_outcome": "R11_SELF_BUILD_PREPARED",
        "r9_candidate_reference": {
            "r9_proposal_id": "r9-proposal-f6b1",
            "r9_manifest_id": "r9-manifest-f6b1",
            "r9_validation_id": "r9-validation-f6b1",
            "r9_handoff_id": "r9-handoff-f6b1",
            "candidate_patch_hash": "b" * 64,
        },
        "evidence_references": list(proposal["evidence_references"]) + ["validation-f6b1"],
        "prepared_action_reference": {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "execution_authority_hash": "eah-f6b1",
            "v2_exec_id": "v2-exec-f6b1",
            "handoff_to_governed_prepare": True,
            "executor_invoked": False,
            "physical_mutation": False,
        },
        "expected_next_state": "PREPARED_AWAITING_VALIDATED_FEEDBACK",
        "canonical_state_json": projection["canonical_state_json"],
        "preparation_is_execution": False,
        "prepared_not_verified": True,
        "prepared_not_closed": True,
        "approval_created": False,
        "kx108_called": False,
        "binder_mutation": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "native_memory_write": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
    }


def _accepted_update(tickets=None, **mission_kwargs):
    mission = _mission(
        tickets
        or [
            _ticket("a"),
            _ticket("b", deps=["a"]),
            _ticket("c", deps=["b"]),
            _ticket("d"),
        ],
        **mission_kwargs,
    )
    projection = project_supervised_mission_state(mission)
    step = propose_supervised_mission_step(projection)
    return integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=_feedback(projection, step),
    )


def _save_checkpoint(tmp_path, update=None):
    store = tmp_path / "checkpoints"
    saved = C.save_supervised_mission_checkpoint(update or _accepted_update(), checkpoint_store_dir=store)
    assert saved["status"] == C.STATUS_SAVED
    S._DEFAULT_STORE = store
    return saved


def _republish_checkpoint(record, store):
    record = deepcopy(record)
    record["accepted_state_hash"] = C._sha256(record["accepted_state"])
    record["dependency_projection_hash"] = C._sha256(record["dependency_projection"])
    record["next_step_hash"] = C._sha256(record["next_step"])
    record["integrity_digest"] = C._record_hash(record)
    path = Path(store) / f"{record['checkpoint_id']}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return record


def test_valid_stored_mission_projection_is_readonly_and_stable(tmp_path):
    saved = _save_checkpoint(tmp_path)

    first = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection")
    second = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection")

    assert first.status_code == 200
    assert first.json() == second.json()
    data = first.json()
    assert data["schema_version"] == S.PROJECTION_SCHEMA_VERSION
    assert data["mission_id"] == "mission-r12-f6b1"
    assert data["readonly"] is True
    assert data["authority"] == "NONE"
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["executor_invoked"] is False
    assert data["memory_write"] is False


def test_dag_next_and_pending_authorization_are_visible(tmp_path):
    saved = _save_checkpoint(tmp_path)

    data = client.get(f"/api/supervised-missions/mission-r12-f6b1/projection", params={"checkpoint_id": saved["checkpoint_id"]}).json()

    assert data["ticket_dag"] == [
        {"ticket_id": "a", "dependency_ids": []},
        {"ticket_id": "b", "dependency_ids": ["a"]},
        {"ticket_id": "c", "dependency_ids": ["b"]},
        {"ticket_id": "d", "dependency_ids": []},
    ]
    assert data["unique_next_ticket_id"] == "d"
    assert data["pending_approvals"][0]["ticket_id"] == "a"
    assert data["tickets"][0]["phase"] == "PREPARED"


def test_transitive_hold_projection_preserves_root_causes(tmp_path):
    saved = _save_checkpoint(tmp_path)
    data = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection").json()

    reasons = canonical_json(data["hold"])
    assert "BLOCKED_BY_HOLD(a)" in reasons
    assert "BLOCKED_BY_DEPENDENCY(b <- a)" in reasons
    assert data["hold"]["transitive_blocks"]


def test_receipt_refs_binder_limits_and_completion_reference_are_visible(tmp_path):
    saved = _save_checkpoint(tmp_path)
    record = deepcopy(saved["checkpoint"])
    record["accepted_state"]["tickets"][0]["action_evidence_id"] = "aev-f6b1"
    record["accepted_state"]["tickets"][0]["receipt_refs"] = ["receipt-f6b1"]
    record["accepted_state"]["tickets"][0]["verification_level"] = "CLOSED"
    record["accepted_state"]["tickets"][0]["verified"] = True
    record["accepted_state"]["tickets"][0]["closed"] = True
    record["accepted_state"]["mission_completion_proof"] = {
        "schema_version": "OBSIDURE_SUPERVISED_MISSION_COMPLETION_PROOF_V1",
        "mission_id": "mission-r12-f6b1",
        "completion_proof_digest": "proof-digest-f6b1",
        "evidence_refs": ["receipt-f6b1"],
    }
    record["accepted_state"]["binder_replay_limitations"] = ["INLINE_STATUS_ONLY"]
    _republish_checkpoint(record, tmp_path / "checkpoints")

    data = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection").json()

    assert data["evidence"]["action_evidence_refs"] == ["aev-f6b1"]
    assert data["evidence"]["receipt_refs"] == ["receipt-f6b1"]
    assert data["verification"]["ticket_levels"]["a"] == "CLOSED"
    assert data["verification"]["mission_completion_proof_ref"]["completion_proof_digest"] == "proof-digest-f6b1"
    assert data["binder_replay"]["independent_replay_available"] is False
    assert "INLINE_STATUS_ONLY" in data["binder_replay"]["limitations"]


def test_missing_corrupt_or_mismatched_checkpoint_fails_closed(tmp_path):
    S._DEFAULT_STORE = tmp_path / "checkpoints"
    missing = client.get("/api/supervised-missions/checkpoints/smc-missing/projection")
    assert missing.status_code == 404
    assert missing.json()["detail"]["readonly"] is True

    saved = _save_checkpoint(tmp_path)
    path = Path(saved["checkpoint_path"])
    path.write_text('{"schema_version":', encoding="utf-8")
    corrupt = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection")
    assert corrupt.status_code == 409
    assert corrupt.json()["detail"]["reason"] == "CHECKPOINT_JSON_INVALID"

    other = _save_checkpoint(tmp_path, _accepted_update([_ticket("z")]))
    mismatch = client.get("/api/supervised-missions/mission-other/projection", params={"checkpoint_id": other["checkpoint_id"]})
    assert mismatch.status_code == 404
    assert mismatch.json()["detail"]["reason"] == "MISSION_CHECKPOINT_MISMATCH"


def test_revoked_mandate_and_invalid_selector_are_explicit(tmp_path):
    saved = _save_checkpoint(tmp_path, _accepted_update(mandate_status="ACTIVE"))
    record = deepcopy(saved["checkpoint"])
    record["accepted_state"]["mandate_status"] = "REVOKED"
    record["accepted_state"]["mandate_revoked"] = True
    _republish_checkpoint(record, tmp_path / "checkpoints")

    data = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection").json()
    assert data["mandate"]["status"] == "REVOKED"
    assert data["mandate"]["revoked"] is True

    invalid = client.get("/api/supervised-missions/checkpoints/../secret/projection")
    assert invalid.status_code in {404, 422}


def test_access_control_denial_uses_existing_api_key_policy(monkeypatch, tmp_path):
    _save_checkpoint(tmp_path)
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "secret")

    denied = client.get("/api/supervised-missions/checkpoints/smc-missing/projection")

    assert denied.status_code == 401
    assert denied.json()["error"] == "unauthorized"
    assert denied.json()["readonly"] is True


def test_status_distinctions_never_promote_authority(tmp_path):
    saved = _save_checkpoint(tmp_path)
    data = client.get(f"/api/supervised-missions/checkpoints/{saved['checkpoint_id']}/projection").json()

    assert data["status_distinctions"] == {
        "prepared_is_authorized": False,
        "executed_observed_is_verified": False,
        "verified_is_closed": False,
        "closed_is_mission_done_verified": False,
    }
    assert data["automatic_approval"] is False
    assert data["kx108_called"] is False
    assert data["binder_mutation"] is False
    assert data["filesystem_execution"] is False
