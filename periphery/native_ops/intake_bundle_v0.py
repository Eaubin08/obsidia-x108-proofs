"""Generic native CRM/TASK intake bundle V0.

Creates one canonical operational work bundle:
- CRM CASE record
- CRM interaction
- native TASK
- CRM follow-up linked to the task

All four mutations are KX108 WORLD_ACTION_PRE gated before any canonical
mutation. A shadow semantic apply is executed first. This is a stack primitive,
not a métier-specific classifier.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import tempfile
from typing import Any, Mapping, Optional

from .common_v0 import (
    ABSENT_STATE_HASH,
    DECISION_AUTHORITY,
    NativeEntityStoreV0,
    canonical_hash,
)
from .crm_native_v0 import (
    DOMAIN_ID as CRM_DOMAIN,
    KIND_FOLLOWUP,
    KIND_INTERACTION,
    KIND_RECORD,
    apply_crm_mutation_v0,
    build_crm_mutation_v0,
    crm_timeline_v0,
)
from .tasks_native_v0 import (
    DOMAIN_ID as TASK_DOMAIN,
    ENTITY_KIND as TASK_KIND,
    apply_task_mutation_v0,
    build_task_mutation_v0,
)
from .world_action_bridge_v0 import (
    build_native_human_approval_v0,
    build_native_world_action_request_v0,
)

import sys
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)


@dataclass(frozen=True)
class NativeCaseTaskIntakePlanV0:
    schema: str
    intake_id: str
    case_id: str
    task_id: str
    interaction_id: str
    followup_id: str
    case_type: str
    title: str
    summary: str
    owner_ref: str | None
    priority: str
    occurred_at: str
    due_at: str
    source_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    tags: tuple[str, ...]
    plan_hash: str
    decision_authority: str = DECISION_AUTHORITY
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_refs"] = list(self.source_refs)
        data["evidence_refs"] = list(self.evidence_refs)
        data["tags"] = list(self.tags)
        return data


def _plan_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "intake_id", "case_id", "task_id", "interaction_id",
        "followup_id", "case_type", "title", "summary", "owner_ref",
        "priority", "occurred_at", "due_at", "source_refs",
        "evidence_refs", "tags", "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_case_task_intake_plan_v0(
    *,
    intake_id: str,
    case_id: str,
    task_id: str,
    interaction_id: str,
    followup_id: str,
    case_type: str,
    title: str,
    summary: str,
    owner_ref: str | None,
    priority: str,
    occurred_at: str,
    due_at: str,
    source_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    tags: tuple[str, ...] = (),
) -> NativeCaseTaskIntakePlanV0:
    if not all((intake_id, case_id, task_id, interaction_id, followup_id, case_type)):
        raise ValueError("NATIVE_INTAKE_IDENTIFIERS_REQUIRED")
    if not title.strip() or not summary.strip():
        raise ValueError("NATIVE_INTAKE_TITLE_SUMMARY_REQUIRED")
    if priority not in {"LOW", "NORMAL", "HIGH", "CRITICAL"}:
        raise ValueError("NATIVE_INTAKE_PRIORITY_INVALID")
    if not source_refs or not evidence_refs:
        raise ValueError("NATIVE_INTAKE_PROVENANCE_REQUIRED")
    payload = {
        "schema": "OBSIDIA_NATIVE_CASE_TASK_INTAKE_PLAN_V0",
        "intake_id": intake_id,
        "case_id": case_id,
        "task_id": task_id,
        "interaction_id": interaction_id,
        "followup_id": followup_id,
        "case_type": case_type,
        "title": title,
        "summary": summary,
        "owner_ref": owner_ref,
        "priority": priority,
        "occurred_at": occurred_at,
        "due_at": due_at,
        "source_refs": list(source_refs),
        "evidence_refs": list(evidence_refs),
        "tags": sorted(set(tags)),
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeCaseTaskIntakePlanV0(
        schema=payload["schema"],
        intake_id=intake_id,
        case_id=case_id,
        task_id=task_id,
        interaction_id=interaction_id,
        followup_id=followup_id,
        case_type=case_type,
        title=title,
        summary=summary,
        owner_ref=owner_ref,
        priority=priority,
        occurred_at=occurred_at,
        due_at=due_at,
        source_refs=tuple(source_refs),
        evidence_refs=tuple(evidence_refs),
        tags=tuple(payload["tags"]),
        plan_hash=canonical_hash(payload),
    )


def verify_native_case_task_intake_plan_v0(
    plan: NativeCaseTaskIntakePlanV0,
) -> tuple[bool, Optional[str]]:
    if plan.decision_authority != DECISION_AUTHORITY:
        return False, "NATIVE_INTAKE_AUTHORITY_INVALID"
    if plan.allowed_to_decide or plan.allowed_to_act:
        return False, "NATIVE_INTAKE_CANNOT_GRANT_AUTHORITY"
    if canonical_hash(_plan_payload(plan.to_dict())) != plan.plan_hash:
        return False, "NATIVE_INTAKE_PLAN_HASH_MISMATCH"
    return True, None


def _build_mutations(plan: NativeCaseTaskIntakePlanV0):
    record = build_crm_mutation_v0(
        mutation_id=f"{plan.intake_id}:record",
        entity_kind=KIND_RECORD,
        entity_id=plan.case_id,
        operation="CREATE_RECORD",
        payload={
            "occurred_at": plan.occurred_at,
            "record_type": "CASE",
            "display_label": plan.title,
            "lifecycle_status": "OPEN",
            "owner_ref": plan.owner_ref,
            "fields": {
                "case_type": plan.case_type,
                "summary": plan.summary,
                "intake_id": plan.intake_id,
            },
            "tags": list(plan.tags),
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=plan.source_refs,
        requested_by="OBSIDIA_NATIVE_INTAKE_V0",
    )
    task = build_task_mutation_v0(
        mutation_id=f"{plan.intake_id}:task",
        task_id=plan.task_id,
        operation="CREATE_TASK",
        payload={
            "occurred_at": plan.occurred_at,
            "title": plan.title,
            "description": plan.summary,
            "priority": plan.priority,
            "assignee_ref": plan.owner_ref,
            "due_at": plan.due_at,
            "dependency_ids": [],
            "tags": list(plan.tags),
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=plan.source_refs,
        requested_by="OBSIDIA_NATIVE_INTAKE_V0",
    )
    interaction = build_crm_mutation_v0(
        mutation_id=f"{plan.intake_id}:interaction",
        entity_kind=KIND_INTERACTION,
        entity_id=plan.interaction_id,
        operation="APPEND_INTERACTION",
        payload={
            "occurred_at": plan.occurred_at,
            "record_id": plan.case_id,
            "interaction_type": "SYSTEM_EVENT",
            "summary": plan.summary,
            "evidence_refs": list(plan.evidence_refs),
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=plan.source_refs,
        requested_by="OBSIDIA_NATIVE_INTAKE_V0",
    )
    followup = build_crm_mutation_v0(
        mutation_id=f"{plan.intake_id}:followup",
        entity_kind=KIND_FOLLOWUP,
        entity_id=plan.followup_id,
        operation="CREATE_FOLLOWUP",
        payload={
            "occurred_at": plan.occurred_at,
            "record_id": plan.case_id,
            "task_ref": plan.task_id,
            "due_at": plan.due_at,
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=plan.source_refs,
        requested_by="OBSIDIA_NATIVE_INTAKE_V0",
    )
    return (record, task, interaction, followup)


def _apply_one(
    *,
    store: NativeEntityStoreV0,
    mutation,
    request: Mapping[str, Any],
    decision_record_id: str,
    decision_store_dir: Path,
    context_store_dir: Path,
):
    if mutation.domain_id == TASK_DOMAIN:
        return apply_task_mutation_v0(
            store=store,
            mutation=mutation,
            request=request,
            decision_record_id=decision_record_id,
            decision_store_dir=decision_store_dir,
            context_store_dir=context_store_dir,
        )
    if mutation.domain_id == CRM_DOMAIN:
        return apply_crm_mutation_v0(
            store=store,
            mutation=mutation,
            request=request,
            decision_record_id=decision_record_id,
            decision_store_dir=decision_store_dir,
            context_store_dir=context_store_dir,
        )
    raise ValueError("NATIVE_INTAKE_DOMAIN_UNSUPPORTED")


def execute_native_case_task_intake_v0(
    *,
    plan: NativeCaseTaskIntakePlanV0,
    store: NativeEntityStoreV0,
    governance_root: Path,
    approved_by: str,
    approval_reference: str,
    gate_overrides: Optional[Mapping[str, Mapping[str, tuple[str, ...]]]] = None,
) -> dict[str, Any]:
    ok, reason = verify_native_case_task_intake_plan_v0(plan)
    if not ok:
        raise ValueError(reason)
    if not approved_by or approved_by == "MACHINE":
        raise ValueError("NATIVE_INTAKE_HUMAN_APPROVER_REQUIRED")
    if not approval_reference:
        raise ValueError("NATIVE_INTAKE_APPROVAL_REFERENCE_REQUIRED")

    mutations = _build_mutations(plan)
    for mutation in mutations:
        if store.state_hash(
            mutation.domain_id,
            mutation.entity_kind,
            mutation.entity_id,
        ) != ABSENT_STATE_HASH:
            return {
                "status": "NATIVE_INTAKE_DUPLICATE_OR_TARGET_EXISTS",
                "canonical_mutation_count": 0,
                "blocking_mutation_id": mutation.mutation_id,
                "decision_authority": DECISION_AUTHORITY,
            }

    gated = []
    for mutation in mutations:
        request = build_native_world_action_request_v0(mutation)
        approval = build_native_human_approval_v0(
            request,
            approval_id=f"approval:{mutation.mutation_id}",
            approved_by=approved_by,
            approval_reference=f"{approval_reference}:{mutation.mutation_id}",
        )
        step_root = governance_root / canonical_hash(
            {"mutation_id": mutation.mutation_id}
        )[:20]
        decision_dir = step_root / "decisions"
        context_dir = step_root / "contexts"
        override = dict((gate_overrides or {}).get(mutation.operation, {}))
        pre = run_world_action_pre_execution_v0(
            request=request,
            human_approval=approval,
            evidence_refs=list(plan.evidence_refs),
            unknowns=list(override.get("unknowns", ())),
            contradictions=list(override.get("contradictions", ())),
            risk_flags=list(override.get("risk_flags", ())),
            context_store_dir=context_dir,
            decision_store_dir=decision_dir,
        )
        if pre.x108_gate != "ALLOW":
            return {
                "status": "NATIVE_INTAKE_GATED_NO_MUTATION",
                "gate": pre.x108_gate,
                "blocking_mutation_id": mutation.mutation_id,
                "blocking_operation": mutation.operation,
                "canonical_mutation_count": 0,
                "decision_authority": DECISION_AUTHORITY,
            }
        gated.append((mutation, request, pre, decision_dir, context_dir))

    with tempfile.TemporaryDirectory(prefix="obsidia-native-intake-shadow-") as tmp:
        shadow = NativeEntityStoreV0(Path(tmp))
        for mutation, request, pre, decision_dir, context_dir in gated:
            _apply_one(
                store=shadow,
                mutation=mutation,
                request=request,
                decision_record_id=pre.decision_record_id,
                decision_store_dir=decision_dir,
                context_store_dir=context_dir,
            )

    receipts = []
    for mutation, request, pre, decision_dir, context_dir in gated:
        if store.state_hash(
            mutation.domain_id,
            mutation.entity_kind,
            mutation.entity_id,
        ) != ABSENT_STATE_HASH:
            raise ValueError("NATIVE_INTAKE_PRESTATE_CHANGED_BEFORE_COMMIT")
        receipt = _apply_one(
            store=store,
            mutation=mutation,
            request=request,
            decision_record_id=pre.decision_record_id,
            decision_store_dir=decision_dir,
            context_store_dir=context_dir,
        )
        receipts.append(receipt.to_dict())

    case_state = store.load_state(CRM_DOMAIN, KIND_RECORD, plan.case_id)
    task_state = store.load_state(TASK_DOMAIN, TASK_KIND, plan.task_id)
    followup_state = store.load_state(CRM_DOMAIN, KIND_FOLLOWUP, plan.followup_id)
    timeline = crm_timeline_v0(store, plan.case_id)

    return {
        "status": "NATIVE_INTAKE_COMMITTED",
        "intake_id": plan.intake_id,
        "plan_hash": plan.plan_hash,
        "case_id": plan.case_id,
        "task_id": plan.task_id,
        "followup_id": plan.followup_id,
        "canonical_mutation_count": len(receipts),
        "receipt_ids": [item["receipt_id"] for item in receipts],
        "case_state_hash": canonical_hash(case_state),
        "task_state_hash": canonical_hash(task_state),
        "followup_state_hash": canonical_hash(followup_state),
        "timeline_event_count": len(timeline),
        "decision_authority": DECISION_AUTHORITY,
        "external_action": False,
    }
