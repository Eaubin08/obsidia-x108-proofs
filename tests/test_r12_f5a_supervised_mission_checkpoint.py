from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from scripts.obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state
from scripts.obsidure_supervised_mission_checkpoint_v1 import (
    STATUS_HELD,
    STATUS_RESTORED,
    STATUS_SAVED,
    resume_supervised_mission_checkpoint,
    save_supervised_mission_checkpoint,
)
from scripts.obsidure_supervised_mission_state_v1 import canonical_json, project_supervised_mission_state
from scripts.obsidure_supervised_mission_stepper_v1 import propose_supervised_mission_step

BASE_SHA = "a" * 40


def _hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _ticket(ticket_id, *, deps=(), status="PENDING", evidence=(), hold_reason=""):
    return {
        "ticket_id": ticket_id,
        "objective": f"Prepare {ticket_id}",
        "dependency_ids": list(deps),
        "status": status,
        "authorized_paths": ["scripts/example.py"],
        "authorized_operations": ["MODIFY"],
        "acceptance_criteria": ["prepared only"],
        "evidence_refs": list(evidence),
        "unknowns": ["unknown-preserved"],
        "hold_reason": hold_reason,
    }


def _mission(tickets, *, remaining_actions=5):
    return {
        "mission_id": "mission-r12-f5a",
        "human_mandate_reference": "mandate-r12-f5a",
        "repository_identity": "repo://obsidia/f5a",
        "local_root": "C:/work/repo",
        "worktree": "C:/work/repo",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": BASE_SHA,
        "original_goal": "Checkpoint supervised mission state.",
        "acceptance_criteria": ["checkpoint restores same NEXT"],
        "bounded_authorized_scope": {"authorized_paths": ["scripts/example.py"], "authorized_operations": ["MODIFY"]},
        "tickets": tickets,
        "global_budget": {"remaining_actions": remaining_actions, "remaining_tickets": 5},
        "timebox": {"expired": False},
        "evidence_refs": ["mandate-evidence"],
        "explicit_unknowns": ["semantic-unknown-preserved"],
        "mission_authority": "KX108_ONLY",
        "mandate_status": "ACTIVE",
        "source_ids": ["r12-f5a-test"],
    }


def _feedback(projection, step, *, suffix="1"):
    proposal = step["step_proposal"]
    return {
        "feedback_id": f"feedback-f5a-{suffix}",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": _hash(proposal),
        "mission_id": proposal["mission_id"],
        "selected_ticket_id": proposal["selected_ticket_id"],
        "mandate_reference": proposal["mandate_reference"],
        "project": dict(proposal["project"]),
        "preparation_outcome": "R11_SELF_BUILD_PREPARED",
        "r9_candidate_reference": {
            "r9_proposal_id": f"r9-proposal-{suffix}",
            "r9_manifest_id": f"r9-manifest-{suffix}",
            "r9_validation_id": f"r9-validation-{suffix}",
            "r9_handoff_id": f"r9-handoff-{suffix}",
            "candidate_patch_hash": "b" * 64,
        },
        "evidence_references": list(proposal["evidence_references"]) + [f"validation-{suffix}"],
        "prepared_action_reference": {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "execution_authority_hash": f"eah-f5a-{suffix}",
            "v2_exec_id": f"v2-exec-f5a-{suffix}",
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


def _accepted_update(tickets=None):
    mission = _mission(tickets or [_ticket("a"), _ticket("b", deps=["a"]), _ticket("c", deps=["b"]), _ticket("d")])
    projection = project_supervised_mission_state(mission)
    step = propose_supervised_mission_step(projection)
    return integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=_feedback(projection, step),
    )


def _save(update, tmp_path):
    return save_supervised_mission_checkpoint(update, checkpoint_store_dir=tmp_path / "checkpoints")


def test_save_and_restore_valid_multi_ticket_state(tmp_path):
    update = _accepted_update()
    saved = _save(update, tmp_path)
    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert saved["status"] == STATUS_SAVED
    assert restored["status"] == STATUS_RESTORED
    assert restored["unique_next_ticket_id"] == "d"
    assert restored["restored_state_hash"] == saved["checkpoint"]["accepted_state_hash"]
    assert restored["prepare_available"] is True


def test_restart_after_hold_preserves_pending_approval_and_independent_next(tmp_path):
    update = _accepted_update()
    saved = _save(update, tmp_path)
    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert restored["pending_approvals"][0]["ticket_id"] == "a"
    assert restored["dependency_projection"]["transitive_hold"] is True
    assert restored["unique_next_ticket_id"] == "d"


def test_duplicate_restore_is_idempotent(tmp_path):
    saved = _save(_accepted_update(), tmp_path)

    first = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")
    second = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")
    duplicate_save = _save(_accepted_update(), tmp_path)

    assert first["status"] == STATUS_RESTORED
    assert second["restored_state_hash"] == first["restored_state_hash"]
    assert duplicate_save["store_status"] == "IDEMPOTENT_EXISTING_IDENTICAL"


def test_budget_preserved_after_resume(tmp_path):
    update = _accepted_update([_ticket("a"), _ticket("d")])
    saved = _save(update, tmp_path)
    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert restored["budget"] == {"remaining_actions": 5, "remaining_tickets": 5}


def test_revoked_mandate_after_save_holds(tmp_path):
    saved = _save(_accepted_update(), tmp_path)

    restored = resume_supervised_mission_checkpoint(
        saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints", mandate_revoked=True
    )

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "HUMAN_MANDATE_REVOKED"


def test_stale_head_after_save_holds(tmp_path):
    saved = _save(_accepted_update(), tmp_path)

    restored = resume_supervised_mission_checkpoint(
        saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints", observed_project_head="c" * 40
    )

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "PROJECT_HEAD_STALE"


def test_expired_timebox_at_restore_holds(tmp_path):
    saved = _save(_accepted_update(), tmp_path)

    restored = resume_supervised_mission_checkpoint(
        saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints", timebox_expired=True
    )

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "MISSION_TIMEBOX_EXPIRED"


def test_tampered_checkpoint_is_rejected(tmp_path):
    saved = _save(_accepted_update(), tmp_path)
    path = Path(saved["checkpoint_path"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["accepted_state"]["mission_id"] = "mission-tampered"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "CHECKPOINT_DIGEST_MISMATCH"


def test_truncated_write_crash_simulation_is_held(tmp_path):
    saved = _save(_accepted_update(), tmp_path)
    Path(saved["checkpoint_path"]).write_text('{"schema_version":', encoding="utf-8")

    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "CHECKPOINT_JSON_INVALID"


def test_corrupted_or_unknown_evidence_reference_holds(tmp_path):
    saved = _save(_accepted_update(), tmp_path)

    restored = resume_supervised_mission_checkpoint(
        saved["checkpoint_id"],
        checkpoint_store_dir=tmp_path / "checkpoints",
        known_evidence_refs=["mandate-evidence"],
    )

    assert restored["status"] == STATUS_HELD
    assert restored["reason"] == "UNKNOWN_EVIDENCE_REFERENCE"


def test_deterministic_serialization(tmp_path):
    saved = _save(_accepted_update(), tmp_path)
    checkpoint = saved["checkpoint"]

    assert canonical_json(checkpoint) == canonical_json(json.loads(json.dumps(checkpoint)))
    assert checkpoint["integrity_digest"]


def test_no_authority_or_act_regression(tmp_path):
    saved = _save(_accepted_update(), tmp_path)
    restored = resume_supervised_mission_checkpoint(saved["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert saved["approval_created"] is False
    assert saved["kx108_called"] is False
    assert saved["binder_mutation"] is False
    assert saved["executor_invoked"] is False
    assert saved["native_memory_write"] is False
    assert restored["prepared_promoted_to_executed"] is False
    assert restored["prepared_promoted_to_verified"] is False
    assert restored["prepared_promoted_to_closed"] is False
    assert restored["push_performed"] is False
    assert restored["merge_performed"] is False
