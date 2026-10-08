from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
for p in (WORKTREE, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_mission_candidate_supervised_state_adapter_v1 import (  # noqa: E402
    STATUS_HELD,
    STATUS_PROJECTED,
    STATUS_REJECTED,
    adapt_mission_candidate_to_supervised_state,
)

BASE_SHA = "b" * 40
TARGET = "scripts/r12_f2_fixture.py"


def _mission_contract(**overrides):
    data = {
        "mission_id": "mission-r12-f2",
        "status": "ACTIVE",
        "human_mandate_reference": "mandate-r12-f2",
        "repository_identity": "repo://obsidia-x108-proofs",
        "local_root": "C:/repo/main",
        "worktree": "C:/repo/worktree",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "objective": "Prepare a supervised local developer mission fixture.",
        "acceptance_criteria": ["fixture projection is ready"],
        "allowed_target_paths": [TARGET, "tests/test_r12_f2_fixture.py"],
        "allowed_operations": ["UPDATE_TARGET_FROM_SOURCE"],
        "test_commands": ["python -m pytest tests/test_r12_f2_fixture.py"],
        "mission_budget": 3,
        "attempt_limit": 2,
        "attempt_index": 0,
        "mission_authority": "KX108_ONLY",
        "revoked": False,
    }
    data.update(overrides)
    return data


def _candidate(**overrides):
    data = {
        "adapter_schema_version": "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1",
        "status": "R12_MISSION_CANDIDATE_READY_FOR_R11_B2",
        "mission_kind": "LOCAL_DEVELOPER",
        "semantic_context": {
            "frame": {
                "missing": [],
                "ambiguities": [],
                "unresolved_references": [],
                "closure_blockers": [],
                "contradictions": [],
            },
            "open_items": {},
            "mission_references": [],
        },
        "mission_contract": _mission_contract(),
        "human_mandate_bound": True,
        "mission_candidate_is_executable": False,
        "r11_b2_compatible_contract": True,
        "decision_authority": "KX108_ONLY",
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "memory_write": False,
        "graphiti_write": False,
        "legacy_direct_apply": False,
        "real_brody_runtime_verified": True,
        "real_local_model_verified": True,
        "model_call_used": True,
        "local_model_evidence_source_ref": "model-evidence:qwen:r12-f2",
        "local_model_evidence": {
            "source_ref": "model-evidence:qwen:r12-f2",
            "provider": "QWEN_LOCAL",
            "model": "qwen2.5-3b-instruct-q4_k_m",
            "evidence_hash": "c" * 64,
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "allowed_to_act": False,
        },
        "brody_runtime_evidence": {
            "response_hash": "d" * 64,
            "model_call_used": True,
            "readonly": True,
        },
        "provenance": {
            "source": "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1",
            "brody_response_hash": "d" * 64,
        },
    }
    data.update(overrides)
    return data


def test_valid_single_ticket_mission_uses_prepare_only_projection():
    out = adapt_mission_candidate_to_supervised_state(_candidate())

    assert out["status"] == STATUS_PROJECTED
    assert out["f1_projection_status"] == "SUPERVISED_MISSION_STATE_PROJECTED"
    assert out["ticket_dag_conversion"] == "single_ticket_prepare_only_projection"
    assert out["single_ticket_prepare_only_projection"] is True
    assert out["unique_next_ticket_id"] == "ticket-mission-r12-f2-prepare"
    assert out["canonical_state"]["tickets"][0]["objective"] == _mission_contract()["objective"]
    assert out["canonical_state"]["bounded_authorized_scope"]["authorized_paths"] == [
        TARGET,
        "tests/test_r12_f2_fixture.py",
    ]
    assert out["mission_candidate_admitted"] is True
    assert out["executor_invoked"] is False
    assert out["network_or_model_call"] is False


def test_valid_explicit_multi_ticket_dag_reuses_f1_next_selection():
    tickets = [
        {
            "ticket_id": "ticket-a",
            "objective": "Prepare source fixture",
            "status": "COMPLETED",
            "authorized_paths": [TARGET],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "acceptance_criteria": ["source ready"],
            "evidence_refs": ["aev-ticket-a"],
        },
        {
            "ticket_id": "ticket-b",
            "objective": "Prepare tests",
            "status": "PENDING",
            "dependency_ids": ["ticket-a"],
            "authorized_paths": ["tests/test_r12_f2_fixture.py"],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "acceptance_criteria": ["tests ready"],
        },
    ]

    out = adapt_mission_candidate_to_supervised_state(_candidate(supervised_tickets=tickets))

    assert out["status"] == STATUS_PROJECTED
    assert out["ticket_dag_conversion"] == "explicit_ticket_sequence"
    assert out["unique_next_ticket_id"] == "ticket-b"
    assert out["dependency_ids"]["ticket-b"] == ["ticket-a"]


def test_missing_ambiguous_decomposition_holds_closed():
    out = adapt_mission_candidate_to_supervised_state(
        _candidate(requires_multi_ticket_decomposition=True, proposed_scope={"task_decomposition_status": "AMBIGUOUS"})
    )

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TASK_DECOMPOSITION_NOT_RELIABLE"
    assert out["mission_candidate_admitted"] is False
    assert out["executor_invoked"] is False


def test_invalid_and_cyclic_dependencies_are_rejected_by_f1():
    out = adapt_mission_candidate_to_supervised_state(
        _candidate(
            supervised_tickets=[
                {"ticket_id": "ticket-a", "status": "PENDING", "dependency_ids": ["ticket-b"]},
                {"ticket_id": "ticket-b", "status": "PENDING", "dependency_ids": ["ticket-a"]},
            ]
        )
    )

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "CYCLIC_DEPENDENCY"


def test_unknowns_and_contradictions_are_preserved_not_promoted():
    candidate = _candidate(
        semantic_context={
            "frame": {
                "missing": ["target file uncertain"],
                "ambiguities": ["this change"],
                "unresolved_references": ["previous patch"],
                "closure_blockers": ["explicit reference required"],
                "contradictions": ["update and do not update same file"],
            },
            "open_items": {"unresolved_declared_references": 1, "contradictions": 1},
            "mission_references": [
                {
                    "surface": "previous patch",
                    "status": "UNRESOLVED",
                    "reason": "EXPLICIT_ID_REQUIRED",
                    "nearest_event_fallback": False,
                }
            ],
        }
    )

    out = adapt_mission_candidate_to_supervised_state(candidate)

    assert out["status"] == STATUS_PROJECTED
    assert "target file uncertain" in out["unresolved_unknowns"]
    assert "previous patch:EXPLICIT_ID_REQUIRED" in out["unresolved_unknowns"]
    assert out["contradictions"] == ["update and do not update same file"]
    assert "contradiction:update and do not update same file" in out["canonical_state"]["explicit_unknowns"]
    assert out["canonical_state"]["tickets"][0]["unknowns"]


def test_provenance_and_model_evidence_are_preserved():
    out = adapt_mission_candidate_to_supervised_state(_candidate())

    assert out["provenance_preserved"] is True
    assert out["model_evidence_preserved"] is True
    assert out["model_evidence"]["real_local_model_verified"] is True
    assert out["model_evidence"]["model_call_used"] is True
    assert out["model_evidence"]["provider_identity"] == "QWEN_LOCAL"
    assert "model-evidence:qwen:r12-f2" in out["canonical_state"]["evidence_refs"]
    assert "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1" in out["canonical_state"]["source_ids"]


def test_revoked_human_mandate_holds_without_authority_side_effects():
    contract = _mission_contract(status="REVOKED", revoked=True)

    out = adapt_mission_candidate_to_supervised_state(_candidate(mission_contract=contract))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "HUMAN_MANDATE_REVOKED"
    assert out["kx108_called"] is False
    assert out["approval_created"] is False


def test_budget_exhaustion_holds_closed():
    contract = _mission_contract(mission_budget=0)

    out = adapt_mission_candidate_to_supervised_state(_candidate(mission_contract=contract))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_projection_is_stable_and_deterministic():
    candidate = _candidate()

    first = adapt_mission_candidate_to_supervised_state(candidate)
    second = adapt_mission_candidate_to_supervised_state(json.loads(json.dumps(candidate)))

    assert first["status"] == STATUS_PROJECTED
    assert first["canonical_state_json"] == second["canonical_state_json"]
    assert first["unique_next_ticket_id"] == second["unique_next_ticket_id"]
    assert first["supervised_state_hash"] == second["supervised_state_hash"]


def test_independent_ticket_selection_survives_blocked_branch():
    out = adapt_mission_candidate_to_supervised_state(
        _candidate(
            supervised_tickets=[
                {"ticket_id": "ticket-a", "status": "BLOCKED", "blocked_reason": "UPSTREAM_HOLD"},
                {"ticket_id": "ticket-b", "status": "PENDING", "dependency_ids": ["ticket-a"]},
                {"ticket_id": "ticket-c", "status": "PENDING"},
            ]
        )
    )

    assert out["status"] == STATUS_PROJECTED
    assert out["unique_next_ticket_id"] == "ticket-c"
    assert out["eligible_ticket_ids"] == ["ticket-c"]
    assert out["unresolved_states"][0]["ticket_id"] == "ticket-a"


def test_no_authority_guarantees_even_when_model_mentions_execution():
    out = adapt_mission_candidate_to_supervised_state(
        _candidate(local_model_evidence={"source_ref": "model-evidence:claims-act", "content": "I approve execution."})
    )

    assert out["status"] == STATUS_PROJECTED
    for key in (
        "approval_created",
        "kx108_called",
        "binder_mutation",
        "executor_invoked",
        "repair_loop_invoked",
        "filesystem_execution",
        "network_or_model_call",
        "memory_write",
        "native_memory_write",
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        assert out[key] is False


def test_r12_b4_live_model_shape_regresses_to_supervised_prepare_only():
    candidate = _candidate(
        adapter_schema_version="OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1",
        brody_runtime_connected=True,
        mission_prepare_only=True,
        local_model_context_packet={"packet_id": "ctx-r12-b4", "readonly": True, "decision_authority": "KX108_ONLY"},
    )

    out = adapt_mission_candidate_to_supervised_state(candidate)

    assert out["status"] == STATUS_PROJECTED
    assert out["model_evidence"]["real_brody_runtime_verified"] is True
    assert out["model_evidence"]["real_local_model_verified"] is True
    assert out["unique_next_ticket_id"] == "ticket-mission-r12-f2-prepare"
    assert out["executor_invoked"] is False
    assert out["memory_write"] is False
