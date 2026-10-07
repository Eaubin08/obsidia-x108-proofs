"""INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0.

Deterministic, provider-neutral projection from non-sovereign source
interpretation candidates into native CRM/TASK intake plans.

This layer does not execute plans and grants no decision or action authority.
It only classifies intake disposition, binds provenance/correlation evidence,
and constructs NativeCaseTaskIntakePlanV0 proposals for downstream human +
KX108 governance.
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from periphery.native_ops.common_v0 import DECISION_AUTHORITY, canonical_hash
from periphery.native_ops.intake_bundle_v0 import (
    NativeCaseTaskIntakePlanV0,
    build_native_case_task_intake_plan_v0,
)
from periphery.native_sources.source_interpretation_v0 import (
    CASE_CONFLICT,
    KIND_CALENDAR_CONTEXT,
    KIND_CONSTRAINT,
    KIND_EVIDENCE_GAP,
    KIND_INFORMATION_ONLY,
    SourceInterpretationCandidateV0,
    SourceInterpretationCorrelationV0,
    verify_source_interpretation_candidate_v0,
)

POLICY_ID = "OBSIDIA_INTERPRETATION_TO_INTAKE_POLICY"
POLICY_VERSION = "V0"

DISPOSITION_ACTION_PLAN = "ACTION_PLAN"
DISPOSITION_INFORMATION_ONLY = "INFORMATION_ONLY"
DISPOSITION_CONSTRAINT_CONTEXT = "CONSTRAINT_CONTEXT"
DISPOSITION_CALENDAR_CONTEXT = "CALENDAR_CONTEXT"
DISPOSITION_DUPLICATE_SUPPRESSED = "DUPLICATE_SUPPRESSED"
DISPOSITION_CONTRADICTION_REVIEW = "CONTRADICTION_REVIEW"
DISPOSITION_CONTRADICTION_MEMBER_CONTEXT = "CONTRADICTION_MEMBER_CONTEXT"
DISPOSITION_EVIDENCE_GAP_REVIEW = "EVIDENCE_GAP_REVIEW"
DISPOSITION_EVIDENCE_GAP_CONTEXT = "EVIDENCE_GAP_CONTEXT"
DISPOSITION_ACTION_REVIEW_REQUIRED = "ACTION_REVIEW_REQUIRED"
DISPOSITION_CONTEXT_ONLY = "CONTEXT_ONLY"

DEADLINE_NONE = "NONE"
DEADLINE_CANDIDATE = "CANDIDATE"
DEADLINE_INTAKE_REVIEW_POLICY = "INTAKE_REVIEW_POLICY"

OWNER_UNASSIGNED = "UNASSIGNED"
OWNER_EXPLICIT_POLICY_INPUT = "EXPLICIT_POLICY_INPUT"


@dataclass(frozen=True)
class InterpretationToIntakeInstructionV0:
    schema: str
    instruction_id: str
    candidate_id: str
    disposition: str
    group_key: str | None
    plan: NativeCaseTaskIntakePlanV0 | None
    gate_unknowns: tuple[str, ...]
    gate_contradictions: tuple[str, ...]
    duplicate_of_candidate_id: str | None
    contradiction_id: str | None
    contradiction_subject: str | None
    deadline_origin: str
    owner_origin: str
    policy_evidence_refs: tuple[str, ...]
    policy_hash: str
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["plan"] = self.plan.to_dict() if self.plan is not None else None
        data["gate_unknowns"] = list(self.gate_unknowns)
        data["gate_contradictions"] = list(self.gate_contradictions)
        data["policy_evidence_refs"] = list(self.policy_evidence_refs)
        return data


@dataclass(frozen=True)
class InterpretationToIntakeBatchV0:
    schema: str
    correlation_hash: str
    instruction_count: int
    instructions: tuple[InterpretationToIntakeInstructionV0, ...]
    batch_hash: str
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "correlation_hash": self.correlation_hash,
            "instruction_count": self.instruction_count,
            "instructions": [item.to_dict() for item in self.instructions],
            "batch_hash": self.batch_hash,
            "allowed_to_decide": self.allowed_to_decide,
            "allowed_to_act": self.allowed_to_act,
            "decision_authority": self.decision_authority,
        }


def _review_policy_due_at(occurred_at: str) -> str:
    dt = datetime.datetime.fromisoformat(occurred_at)
    next_day = dt + datetime.timedelta(days=1)
    return next_day.replace(
        hour=17,
        minute=0,
        second=0,
        microsecond=0,
    ).isoformat()


def _ids(group: str) -> dict[str, str]:
    digest = canonical_hash({"interpreted_office_group": group})[:20]
    return {
        "case_id": f"office-case:{digest}",
        "task_id": f"office-task:{digest}",
        "interaction_id": f"office-interaction:{digest}",
        "followup_id": f"office-followup:{digest}",
    }


def _plan_from_candidate(
    candidate: SourceInterpretationCandidateV0,
    *,
    group: str,
    due_at: str,
    owner_ref: str | None,
    context_tags: Sequence[str],
    deadline_origin: str,
) -> NativeCaseTaskIntakePlanV0:
    if not candidate.proposed_case_type:
        raise ValueError("INTAKE_POLICY_CASE_TYPE_REQUIRED")
    if not candidate.proposed_title or not candidate.proposed_summary:
        raise ValueError("INTAKE_POLICY_TITLE_SUMMARY_REQUIRED")
    if not candidate.proposed_priority:
        raise ValueError("INTAKE_POLICY_PRIORITY_REQUIRED")
    ids = _ids(group)
    tags = {
        *context_tags,
        "SOURCE_INTERPRETATION_NATIVE_V0",
        "INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0",
        candidate.proposed_case_type,
    }
    if owner_ref is None:
        tags.add("OWNER_UNASSIGNED")
    if deadline_origin == DEADLINE_INTAKE_REVIEW_POLICY:
        tags.add("POLICY_DUE_REVIEW_NOT_SOURCE_FACT")
    elif deadline_origin == DEADLINE_CANDIDATE:
        tags.add("DEADLINE_FROM_INTERPRETATION_CANDIDATE")
    return build_native_case_task_intake_plan_v0(
        intake_id=f"interpreted-intake:{group}",
        case_id=ids["case_id"],
        task_id=ids["task_id"],
        interaction_id=ids["interaction_id"],
        followup_id=ids["followup_id"],
        case_type=candidate.proposed_case_type,
        title=candidate.proposed_title,
        summary=candidate.proposed_summary,
        owner_ref=owner_ref,
        priority=candidate.proposed_priority,
        occurred_at=candidate.occurred_at,
        due_at=due_at,
        source_refs=tuple(candidate.provenance_refs),
        evidence_refs=(
            f"interpretation:{candidate.interpretation_hash}",
            *tuple(
                ref
                for ref in candidate.provenance_refs
                if ref.startswith("source-observation:")
            ),
        ),
        tags=tuple(sorted(tags)),
    )


def _instruction(
    *,
    candidate: SourceInterpretationCandidateV0,
    disposition: str,
    group_key: str | None = None,
    plan: NativeCaseTaskIntakePlanV0 | None = None,
    gate_unknowns: Sequence[str] = (),
    gate_contradictions: Sequence[str] = (),
    duplicate_of_candidate_id: str | None = None,
    contradiction_id: str | None = None,
    contradiction_subject: str | None = None,
    deadline_origin: str = DEADLINE_NONE,
    owner_origin: str = OWNER_UNASSIGNED,
    policy_evidence_refs: Sequence[str] = (),
) -> InterpretationToIntakeInstructionV0:
    payload = {
        "schema": "OBSIDIA_INTERPRETATION_TO_INTAKE_INSTRUCTION_V0",
        "candidate_id": candidate.candidate_id,
        "candidate_hash": candidate.interpretation_hash,
        "disposition": disposition,
        "group_key": group_key,
        "plan_hash": plan.plan_hash if plan is not None else None,
        "gate_unknowns": sorted(set(gate_unknowns)),
        "gate_contradictions": sorted(set(gate_contradictions)),
        "duplicate_of_candidate_id": duplicate_of_candidate_id,
        "contradiction_id": contradiction_id,
        "contradiction_subject": contradiction_subject,
        "deadline_origin": deadline_origin,
        "owner_origin": owner_origin,
        "policy_evidence_refs": sorted(set(policy_evidence_refs)),
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    policy_hash = canonical_hash(payload)
    return InterpretationToIntakeInstructionV0(
        schema=payload["schema"],
        instruction_id=f"intake-policy-{policy_hash[:32]}",
        candidate_id=candidate.candidate_id,
        disposition=disposition,
        group_key=group_key,
        plan=plan,
        gate_unknowns=tuple(payload["gate_unknowns"]),
        gate_contradictions=tuple(payload["gate_contradictions"]),
        duplicate_of_candidate_id=duplicate_of_candidate_id,
        contradiction_id=contradiction_id,
        contradiction_subject=contradiction_subject,
        deadline_origin=deadline_origin,
        owner_origin=owner_origin,
        policy_evidence_refs=tuple(payload["policy_evidence_refs"]),
        policy_hash=policy_hash,
    )


def project_interpretations_to_native_intake_v0(
    candidates: Mapping[str, SourceInterpretationCandidateV0],
    correlation: SourceInterpretationCorrelationV0,
    *,
    owner_ref: str | None = None,
    context_tags: Sequence[str] = (),
) -> InterpretationToIntakeBatchV0:
    """Project interpretation candidates into non-sovereign intake instructions.

    Mapping keys are external caller identities (for example fixture item ids) and
    are deliberately excluded from policy semantics. Candidate ids/hashes and
    correlation objects are the canonical inputs.
    """
    for candidate in candidates.values():
        ok, reason = verify_source_interpretation_candidate_v0(candidate)
        if not ok:
            raise ValueError(reason)
    if correlation.allowed_to_decide or correlation.allowed_to_act:
        raise ValueError("INTAKE_POLICY_CORRELATION_AUTHORITY_INVALID")
    if correlation.decision_authority != DECISION_AUTHORITY:
        raise ValueError("INTAKE_POLICY_CORRELATION_DECISION_AUTHORITY_INVALID")

    candidate_by_id = {x.candidate_id: x for x in candidates.values()}
    if set(correlation.candidate_hashes) != {
        x.interpretation_hash for x in candidates.values()
    }:
        raise ValueError("INTAKE_POLICY_CORRELATION_CANDIDATE_SET_MISMATCH")

    duplicate_map = {
        duplicate_id: primary_id
        for duplicate_id, primary_id in correlation.duplicate_links
    }
    contradiction_by_candidate: dict[str, Any] = {}
    contradiction_primary: dict[str, str] = {}
    for group in correlation.contradiction_groups:
        members = [candidate_by_id[candidate_id] for candidate_id in group.candidate_ids]
        action_members = [x for x in members if x.actionable_signal]
        if not action_members:
            raise ValueError("INTAKE_POLICY_CONTRADICTION_WITHOUT_ACTIONABLE_MEMBER")
        seed = sorted(action_members, key=lambda x: (x.occurred_at, x.candidate_id))[0]
        contradiction_primary[group.contradiction_id] = seed.candidate_id
        for candidate_id in group.candidate_ids:
            contradiction_by_candidate[candidate_id] = group

    owner_origin = (
        OWNER_EXPLICIT_POLICY_INPUT if owner_ref is not None else OWNER_UNASSIGNED
    )
    instructions: list[InterpretationToIntakeInstructionV0] = []

    ordered = sorted(
        candidates.values(),
        key=lambda item: (item.occurred_at, item.candidate_id),
    )
    for candidate in ordered:
        if candidate.interpretation_kind == KIND_INFORMATION_ONLY:
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_INFORMATION_ONLY,
            ))
            continue

        if candidate.interpretation_kind == KIND_CONSTRAINT:
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_CONSTRAINT_CONTEXT,
                group_key=candidate.work_identity_candidate,
            ))
            continue

        if candidate.interpretation_kind == KIND_CALENDAR_CONTEXT:
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_CALENDAR_CONTEXT,
                group_key=candidate.work_identity_candidate,
            ))
            continue

        primary_id = duplicate_map.get(candidate.candidate_id)
        if primary_id is not None:
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_DUPLICATE_SUPPRESSED,
                group_key=candidate.duplicate_identity_candidate,
                duplicate_of_candidate_id=primary_id,
                policy_evidence_refs=(
                    f"correlation:{correlation.correlation_hash}",
                    f"interpretation:{candidate.interpretation_hash}",
                ),
            ))
            continue

        contradiction = contradiction_by_candidate.get(candidate.candidate_id)
        if contradiction is not None:
            primary_candidate_id = contradiction_primary[contradiction.contradiction_id]
            if candidate.candidate_id != primary_candidate_id:
                instructions.append(_instruction(
                    candidate=candidate,
                    disposition=DISPOSITION_CONTRADICTION_MEMBER_CONTEXT,
                    group_key=contradiction.subject,
                    contradiction_id=contradiction.contradiction_id,
                    contradiction_subject=contradiction.subject,
                    policy_evidence_refs=(
                        f"correlation:{correlation.correlation_hash}",
                        f"contradiction:{contradiction.contradiction_hash}",
                    ),
                ))
                continue

            members = [
                candidate_by_id[candidate_id]
                for candidate_id in contradiction.candidate_ids
            ]
            action_members = [x for x in members if x.actionable_signal]
            due = next(
                (
                    x.deadline_candidate
                    for x in action_members
                    if x.deadline_candidate is not None
                ),
                None,
            )
            deadline_origin = DEADLINE_CANDIDATE
            if due is None:
                due = _review_policy_due_at(candidate.occurred_at)
                deadline_origin = DEADLINE_INTAKE_REVIEW_POLICY
            ids = _ids(contradiction.subject)
            tags = {
                *context_tags,
                "SOURCE_INTERPRETATION_NATIVE_V0",
                "INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0",
                CASE_CONFLICT,
            }
            if owner_ref is None:
                tags.add("OWNER_UNASSIGNED")
            if deadline_origin == DEADLINE_INTAKE_REVIEW_POLICY:
                tags.add("POLICY_DUE_REVIEW_NOT_SOURCE_FACT")
            else:
                tags.add("DEADLINE_FROM_INTERPRETATION_CANDIDATE")
            plan = build_native_case_task_intake_plan_v0(
                intake_id=f"interpreted-intake:{contradiction.subject}",
                case_id=ids["case_id"],
                task_id=ids["task_id"],
                interaction_id=ids["interaction_id"],
                followup_id=ids["followup_id"],
                case_type=CASE_CONFLICT,
                title="Resolve conflicting source instructions",
                summary=(
                    "Contradictory source directives detected for "
                    f"{contradiction.subject}."
                ),
                owner_ref=owner_ref,
                priority="HIGH",
                occurred_at=candidate.occurred_at,
                due_at=due,
                source_refs=tuple(sorted({
                    ref for member in members for ref in member.provenance_refs
                })),
                evidence_refs=tuple(sorted({
                    *(f"interpretation:{member.interpretation_hash}" for member in members),
                    f"correlation:{correlation.correlation_hash}",
                    f"contradiction:{contradiction.contradiction_hash}",
                })),
                tags=tuple(sorted(tags)),
            )
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_CONTRADICTION_REVIEW,
                group_key=contradiction.subject,
                plan=plan,
                gate_contradictions=(
                    f"SOURCE_DIRECTIVE_REQUIRE:{contradiction.subject}",
                    f"SOURCE_DIRECTIVE_FORBID:{contradiction.subject}",
                ),
                contradiction_id=contradiction.contradiction_id,
                contradiction_subject=contradiction.subject,
                deadline_origin=deadline_origin,
                owner_origin=owner_origin,
                policy_evidence_refs=(
                    f"correlation:{correlation.correlation_hash}",
                    f"contradiction:{contradiction.contradiction_hash}",
                ),
            ))
            continue

        if candidate.interpretation_kind == KIND_EVIDENCE_GAP:
            if not candidate.unknowns:
                instructions.append(_instruction(
                    candidate=candidate,
                    disposition=DISPOSITION_EVIDENCE_GAP_CONTEXT,
                    group_key=candidate.work_identity_candidate,
                ))
                continue
            due = _review_policy_due_at(candidate.occurred_at)
            group = (
                candidate.work_identity_candidate
                or f"evidence-gap:{candidate.candidate_id}"
            )
            plan = _plan_from_candidate(
                candidate,
                group=group,
                due_at=due,
                owner_ref=owner_ref,
                context_tags=context_tags,
                deadline_origin=DEADLINE_INTAKE_REVIEW_POLICY,
            )
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_EVIDENCE_GAP_REVIEW,
                group_key=group,
                plan=plan,
                gate_unknowns=candidate.unknowns,
                deadline_origin=DEADLINE_INTAKE_REVIEW_POLICY,
                owner_origin=owner_origin,
                policy_evidence_refs=tuple(
                    f"evidence-gap:{gap}" for gap in candidate.evidence_gaps
                ),
            ))
            continue

        if candidate.actionable_signal:
            if not candidate.deadline_candidate:
                instructions.append(_instruction(
                    candidate=candidate,
                    disposition=DISPOSITION_ACTION_REVIEW_REQUIRED,
                    group_key=(
                        candidate.work_identity_candidate or candidate.candidate_id
                    ),
                ))
                continue
            group = candidate.work_identity_candidate or candidate.candidate_id
            plan = _plan_from_candidate(
                candidate,
                group=group,
                due_at=candidate.deadline_candidate,
                owner_ref=owner_ref,
                context_tags=context_tags,
                deadline_origin=DEADLINE_CANDIDATE,
            )
            instructions.append(_instruction(
                candidate=candidate,
                disposition=DISPOSITION_ACTION_PLAN,
                group_key=group,
                plan=plan,
                deadline_origin=DEADLINE_CANDIDATE,
                owner_origin=owner_origin,
            ))
            continue

        instructions.append(_instruction(
            candidate=candidate,
            disposition=DISPOSITION_CONTEXT_ONLY,
            group_key=candidate.work_identity_candidate,
        ))

    batch_payload = {
        "schema": "OBSIDIA_INTERPRETATION_TO_INTAKE_BATCH_V0",
        "correlation_hash": correlation.correlation_hash,
        "instruction_hashes": [item.policy_hash for item in instructions],
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return InterpretationToIntakeBatchV0(
        schema=batch_payload["schema"],
        correlation_hash=correlation.correlation_hash,
        instruction_count=len(instructions),
        instructions=tuple(instructions),
        batch_hash=canonical_hash(batch_payload),
    )
