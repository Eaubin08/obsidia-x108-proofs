from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.main import app
from apps.obsidia_api.routes import supervised_missions as S
from tests.api.test_supervised_mission_authorization_handoff_api import _auth, _prepare
from tests.api.test_supervised_mission_prepare_ingress_api import _request, _world

client = TestClient(app)


TICKET_ID = "ticket-mission-r12-f6-c1-prepare"


def _executed(monkeypatch, tmp_path: Path):
    world = _world(tmp_path)
    prepared = _prepare(monkeypatch, world)
    executed = _auth(world, prepared).json()
    assert executed["status"] == S.AUTH_STATUS_ACCEPTED
    assert executed["execution_phase"] == "EXECUTED_OBSERVED"
    return world, prepared, executed


def _project(world: dict[str, object]) -> dict[str, object]:
    return {
        "repository_identity": "repo://r12-f6-c1-disposable",
        "local_root": str(world["main"]),
        "worktree": str(world["exec_wt"]),
        "branch": world["branch"],
        "base_sha": world["base_sha"],
    }


def _verification(world: dict[str, object], executed: dict[str, object], *, full_binder: bool = True) -> dict[str, object]:
    outcome = executed["execution_outcome"]
    replay = dict(outcome["r8_replay"])
    if full_binder:
        replay["replay_verdict"] = "VERIFIED"
        replay["binder_replay_status"] = "RECONSTRUCTED_MATCH"
    return {
        "verification_id": "ver-r12-f6-d2-" + TICKET_ID,
        "mission_id": executed["mission_id"],
        "ticket_id": TICKET_ID,
        "mandate_reference": "mandate-r12-f6-c1",
        "project": _project(world),
        "action_evidence_id": executed["action_evidence_id"],
        "execution_attempt_id": outcome["execution_attempt_id"],
        "prepared_proposal_id": outcome["prepared_proposal_id"],
        "prepared_patch_hash": outcome["prepared_patch_hash"],
        "authority_reference": outcome["authority_reference"],
        "r8_replay": replay,
        "realized_state_reconciliation": outcome["realized_state_reconciliation"],
        "reviewer_verdict": "PASS",
        "reviewer_independent": True,
        "reviewer_reference": "review-r12-f6-d2",
        "test_evidence": [
            {
                "test_id": "pytest-r12-f6-d2-disposable",
                "status": "PASS",
                "independently_checked": True,
                "real_input_tested": True,
                "evidence_ref": "test-ref-r12-f6-d2",
            }
        ],
        "acceptance_criteria_results": [{"criterion": "checkpoint saved", "status": "PASS", "evidence_ref": "accept-r12-f6-d2"}],
        "mission_acceptance_criteria_results": [{"criterion": "checkpoint saved", "status": "PASS", "evidence_ref": "mission-accept-r12-f6-d2"}],
        "observed_project": {
            "original_base_sha": world["base_sha"],
            "current_head": world["base_sha"],
            "authorized_state_evolution": False,
        },
        "unknowns": [],
        "contradictions": [],
    }


def _verify_payload(executed: dict[str, object], evidence: dict[str, object], **extra):
    payload = {
        "checkpoint_id": executed["checkpoint_id"],
        "ticket_id": TICKET_ID,
        "verification_evidence": evidence,
    }
    payload.update(extra)
    return payload


def test_execution_observed_projection_is_not_verified(monkeypatch, tmp_path):
    _world_data, _prepared, executed = _executed(monkeypatch, tmp_path)

    response = client.get(
        f"/api/supervised-missions/{executed['mission_id']}/verification-projection",
        params={"checkpoint_id": executed["checkpoint_id"], "ticket_id": TICKET_ID},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.VERIFICATION_STATUS_PROJECTED
    assert data["verification_projection"]["execution_observation"]["phase"] == "AWAITING_INDEPENDENT_VERIFICATION"
    assert data["verification_projection"]["execution_observation"]["executed_observed_is_verified"] is False
    assert data["verification_projection"]["closure_eligibility"] == "CLOSURE_BLOCKED"
    assert data["executor_invoked"] is False
    assert data["approval_created"] is False


def test_limited_binder_replay_blocks_closure(monkeypatch, tmp_path):
    world, _prepared, executed = _executed(monkeypatch, tmp_path)
    evidence = _verification(world, executed, full_binder=False)
    evidence["r8_replay"]["replay_verdict"] = "VERIFIED_WITH_LIMITS"
    evidence["r8_replay"]["binder_replay_status"] = "INLINE_STATUS_ONLY"

    response = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, evidence),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.VERIFICATION_STATUS_HELD
    assert data["reason"] == "BINDER_DECISION_RECONSTRUCTION_REQUIRED"
    assert data["closure_eligibility"] == "CLOSURE_BLOCKED"
    assert data["binder_independence"]["fully_independent"] is False
    assert data["executor_invoked"] is False
    assert data["memory_write"] is False


def test_full_replay_assesses_closure_eligibility_without_persisting(monkeypatch, tmp_path):
    world, _prepared, executed = _executed(monkeypatch, tmp_path)
    evidence = _verification(world, executed, full_binder=True)

    response = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, evidence),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.VERIFICATION_STATUS_ASSESSED
    assert data["closure_eligibility"] in {"TICKET_CLOSURE_ELIGIBLE", "MISSION_CLOSURE_ELIGIBLE"}
    assert data["verification_assessment"]["ticket_closed"] is True
    assert data["persisted"] is False
    assert data["checkpoint_id"] == executed["checkpoint_id"]
    assert data["executor_invoked"] is False
    assert data["approval_created"] is False

    projection = client.get(
        f"/api/supervised-missions/{executed['mission_id']}/verification-projection",
        params={"checkpoint_id": executed["checkpoint_id"], "ticket_id": TICKET_ID},
    ).json()
    assert projection["verification_projection"]["closure_eligibility"] == "CLOSURE_BLOCKED"


def test_missing_tampered_and_wrong_identity_evidence_fail_closed(monkeypatch, tmp_path):
    world, _prepared, executed = _executed(monkeypatch, tmp_path)
    missing = _verification(world, executed)
    del missing["r8_replay"]
    missing_result = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, missing),
    ).json()
    assert missing_result["status"] == S.VERIFICATION_STATUS_HELD
    assert missing_result["reason"] == "R8_REPLAY_REQUIRED"

    tampered = _verification(world, executed)
    tampered["action_evidence_id"] = "aev-tampered"
    tampered_result = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, tampered),
    ).json()
    assert tampered_result["status"] == S.VERIFICATION_STATUS_REJECTED
    assert tampered_result["reason"] == "VERIFICATION_BINDING_MISMATCH:ACTION_EVIDENCE_ID"

    wrong_ticket = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, _verification(world, executed), ticket_id="ticket-other"),
    ).json()
    assert wrong_ticket["status"] == S.VERIFICATION_STATUS_HELD
    assert wrong_ticket["reason"] == "VERIFICATION_TICKET_NOT_FOUND"


def test_reconciliation_mismatch_duplicate_and_no_authority(monkeypatch, tmp_path):
    world, _prepared, executed = _executed(monkeypatch, tmp_path)
    mismatch = _verification(world, executed)
    mismatch["realized_state_reconciliation"]["reconciliation_status"] = "MISMATCH"
    mismatch_result = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, mismatch),
    ).json()
    assert mismatch_result["status"] == S.VERIFICATION_STATUS_HELD
    assert mismatch_result["reason"] == "R8_RECONCILIATION_NOT_CONFIRMED:MISMATCH"

    evidence = _verification(world, executed)
    first = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, evidence),
    ).json()
    duplicate = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, evidence, prior_verification_evidence=evidence),
    ).json()
    assert first["closure_eligibility"] == duplicate["closure_eligibility"]
    for key in ("executor_invoked", "approval_created", "kx108_called", "binder_mutation", "memory_write", "native_memory_write"):
        assert duplicate[key] is False


def test_invalid_selector_and_api_key_policy_fail_closed(monkeypatch, tmp_path):
    world, _prepared, executed = _executed(monkeypatch, tmp_path)
    invalid = client.get(
        f"/api/supervised-missions/{executed['mission_id']}/verification-projection",
        params={"checkpoint_id": "../secret", "ticket_id": TICKET_ID},
    )
    assert invalid.status_code == 422

    from apps.obsidia_api import main as api_main

    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "secret")
    denied = client.post(
        f"/api/supervised-missions/{executed['mission_id']}/verify-ticket",
        json=_verify_payload(executed, _verification(world, executed)),
    )
    assert denied.status_code == 401
    assert denied.json()["error"] == "unauthorized"
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "")
