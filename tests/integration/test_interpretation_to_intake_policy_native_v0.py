import inspect

from periphery.native_ops.interpretation_to_intake_policy_v0 import (
    DEADLINE_CANDIDATE,
    DEADLINE_INTAKE_REVIEW_POLICY,
    DISPOSITION_ACTION_PLAN,
    DISPOSITION_CALENDAR_CONTEXT,
    DISPOSITION_CONSTRAINT_CONTEXT,
    DISPOSITION_CONTRADICTION_MEMBER_CONTEXT,
    DISPOSITION_CONTRADICTION_REVIEW,
    DISPOSITION_DUPLICATE_SUPPRESSED,
    DISPOSITION_EVIDENCE_GAP_REVIEW,
    DISPOSITION_INFORMATION_ONLY,
    OWNER_UNASSIGNED,
    project_interpretations_to_native_intake_v0,
)
import periphery.native_ops.interpretation_to_intake_policy_v0 as policy_module
from periphery.native_sources.source_interpretation_v0 import (
    CASE_CONFLICT,
    correlate_source_interpretations_v0,
)
from tests.integration.test_source_interpretation_native_v0 import (
    build_interpretations,
)


def build_batch(tmp_path):
    items = build_interpretations(tmp_path)
    correlation = correlate_source_interpretations_v0(list(items.values()))
    batch = project_interpretations_to_native_intake_v0(
        items,
        correlation,
        context_tags=("ENTERPRISE_SANDBOX",),
    )
    by_candidate = {item.candidate_id: item for item in batch.instructions}
    return items, correlation, batch, by_candidate


def instruction_for(items, by_candidate, item_id):
    return by_candidate[items[item_id].candidate_id]


def test_policy_projects_all_twelve_interpretations_without_authority(tmp_path):
    items, correlation, batch, by_candidate = build_batch(tmp_path)

    assert len(items) == 12
    assert batch.instruction_count == 12
    assert len(batch.instructions) == 12
    assert batch.correlation_hash == correlation.correlation_hash
    assert batch.allowed_to_decide is False
    assert batch.allowed_to_act is False
    assert batch.decision_authority == "KX108_ONLY"

    for instruction in batch.instructions:
        assert instruction.allowed_to_decide is False
        assert instruction.allowed_to_act is False
        assert instruction.decision_authority == "KX108_ONLY"
        assert instruction.candidate_id in by_candidate


def test_policy_routes_information_context_duplicate_and_calendar(tmp_path):
    items, _, _, by_candidate = build_batch(tmp_path)

    assert instruction_for(
        items, by_candidate, "mail-info-001"
    ).disposition == DISPOSITION_INFORMATION_ONLY
    assert instruction_for(
        items, by_candidate, "policy-info.md"
    ).disposition == DISPOSITION_INFORMATION_ONLY
    assert instruction_for(
        items, by_candidate, "supplier-terms.md"
    ).disposition == DISPOSITION_CONSTRAINT_CONTEXT
    assert instruction_for(
        items, by_candidate, "event-deadline-001"
    ).disposition == DISPOSITION_CALENDAR_CONTEXT
    assert instruction_for(
        items, by_candidate, "event-routine-001"
    ).disposition == DISPOSITION_CALENDAR_CONTEXT

    duplicate = instruction_for(
        items, by_candidate, "mail-action-001-duplicate"
    )
    assert duplicate.disposition == DISPOSITION_DUPLICATE_SUPPRESSED
    assert duplicate.plan is None
    assert duplicate.duplicate_of_candidate_id == items["mail-action-001"].candidate_id


def test_policy_builds_three_normal_work_plans_without_inventing_owner(tmp_path):
    items, _, batch, by_candidate = build_batch(tmp_path)

    expected = {
        "mail-action-001": ("ACTION_WITH_DEADLINE", "HIGH"),
        "mail-incident-001": ("INCIDENT", "CRITICAL"),
        "contract-renewal.md": ("CONTRACT_DEADLINE", "HIGH"),
    }
    for item_id, (case_type, priority) in expected.items():
        instruction = instruction_for(items, by_candidate, item_id)
        assert instruction.disposition == DISPOSITION_ACTION_PLAN
        assert instruction.deadline_origin == DEADLINE_CANDIDATE
        assert instruction.owner_origin == OWNER_UNASSIGNED
        assert instruction.plan is not None
        assert instruction.plan.case_type == case_type
        assert instruction.plan.priority == priority
        assert instruction.plan.owner_ref is None
        assert "OWNER_UNASSIGNED" in instruction.plan.tags
        assert "DEADLINE_FROM_INTERPRETATION_CANDIDATE" in instruction.plan.tags

    normal_plans = [
        x for x in batch.instructions if x.disposition == DISPOSITION_ACTION_PLAN
    ]
    assert len(normal_plans) == 3


def test_evidence_gap_becomes_review_plan_with_explicit_policy_deadline(tmp_path):
    items, _, _, by_candidate = build_batch(tmp_path)
    instruction = instruction_for(
        items, by_candidate, "mail-missing-evidence-001"
    )

    assert instruction.disposition == DISPOSITION_EVIDENCE_GAP_REVIEW
    assert instruction.deadline_origin == DEADLINE_INTAKE_REVIEW_POLICY
    assert instruction.owner_origin == OWNER_UNASSIGNED
    assert instruction.plan is not None
    assert instruction.plan.owner_ref is None
    assert "POLICY_DUE_REVIEW_NOT_SOURCE_FACT" in instruction.plan.tags
    assert set(instruction.gate_unknowns) == {
        "REQUEST_AUTHORITY_UNKNOWN",
        "REQUEST_SCOPE_UNKNOWN",
    }


def test_contradiction_builds_one_review_plan_and_one_context_member(tmp_path):
    items, correlation, batch, by_candidate = build_batch(tmp_path)

    conflict_instructions = [
        instruction_for(items, by_candidate, item_id)
        for item_id in ("mail-conflict-a", "mail-conflict-b")
    ]
    assert {
        item.disposition for item in conflict_instructions
    } == {
        DISPOSITION_CONTRADICTION_REVIEW,
        DISPOSITION_CONTRADICTION_MEMBER_CONTEXT,
    }

    review = next(
        item for item in conflict_instructions
        if item.disposition == DISPOSITION_CONTRADICTION_REVIEW
    )
    assert review.plan is not None
    assert review.plan.case_type == CASE_CONFLICT
    assert review.plan.owner_ref is None
    assert review.contradiction_subject == "supplier-order:SO-77"
    assert set(review.gate_contradictions) == {
        "SOURCE_DIRECTIVE_REQUIRE:supplier-order:SO-77",
        "SOURCE_DIRECTIVE_FORBID:supplier-order:SO-77",
    }
    assert f"correlation:{correlation.correlation_hash}" in review.policy_evidence_refs

    review_plans = [
        x for x in batch.instructions
        if x.disposition == DISPOSITION_CONTRADICTION_REVIEW
    ]
    assert len(review_plans) == 1


def test_policy_is_deterministic_and_does_not_execute_native_intake(tmp_path):
    _, _, first, _ = build_batch(tmp_path / "first")
    _, _, second, _ = build_batch(tmp_path / "second")

    assert first.batch_hash == second.batch_hash
    assert [x.policy_hash for x in first.instructions] == [
        x.policy_hash for x in second.instructions
    ]

    source = inspect.getsource(policy_module)
    assert "execute_native_case_task_intake_v0" not in source
    assert "apply_crm_mutation_v0" not in source
    assert "apply_task_mutation_v0" not in source
    assert "allowed_to_decide: bool = False" in source
    assert "allowed_to_act: bool = False" in source
