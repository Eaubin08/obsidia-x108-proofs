"""Interpreted enterprise-office E2E.

Unlike enterprise_office_e2e_v0, this runner never reads the sandbox truth
manifest for routing. It uses SOURCE_INTERPRETATION_NATIVE_V0 outputs and
correlation results, then sends proposed native intake plans through the
existing human/KX108-governed intake path.

The truth manifest remains test oracle only.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.intake_bundle_v0 import (
    build_native_case_task_intake_plan_v0,
    execute_native_case_task_intake_v0,
)
from periphery.native_sources.calendar_connector_v0 import (
    CalendarNativeConnectorV0,
    LocalCalendarFixtureProviderV0,
)
from periphery.native_sources.common_v0 import (
    DECISION_AUTHORITY,
    SOURCE_CALENDAR,
    SOURCE_DOCUMENT_REPOSITORY,
    SOURCE_MAILBOX,
    canonical_hash,
)
from periphery.native_sources.document_connector_v0 import (
    DocumentNativeConnectorV0,
    LocalDocumentRepositoryProviderV0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    EnterpriseSandboxPathsV0,
)
from periphery.native_sources.mail_connector_v0 import (
    LocalMailFixtureProviderV0,
    MailNativeConnectorV0,
)
from periphery.native_sources.source_interpretation_v0 import (
    CASE_CONFLICT,
    CASE_MISSING_EVIDENCE,
    KIND_CALENDAR_CONTEXT,
    KIND_CONSTRAINT,
    KIND_EVIDENCE_GAP,
    KIND_INFORMATION_ONLY,
    SourceInterpretationCandidateV0,
    correlate_source_interpretations_v0,
    interpret_calendar_v0,
    interpret_document_v0,
    interpret_mail_v0,
)
from periphery.native_sources.source_onboarding_v0 import (
    build_native_human_source_authorization_v0,
    build_native_observed_source_candidate_v0,
)
from periphery.native_sources.source_runtime_v0 import NativeSourceRuntimeV0

STATUS = "SOURCE_INTERPRETATION_NATIVE_V0_E2E"


def _activate_source(
    *,
    runtime: NativeSourceRuntimeV0,
    source_id: str,
    source_kind: str,
    provider: str,
    capabilities: tuple[str, ...],
    identity_seed: str,
):
    candidate = build_native_observed_source_candidate_v0(
        candidate_id=f"candidate:{source_id}",
        source_kind=source_kind,
        provider=provider,
        source_identity_sha256=canonical_hash(
            {"interpreted_e2e_source_identity": identity_seed}
        ),
        observed_capabilities=capabilities,
        connector_reference=f"interpreted-e2e:{source_id}",
        observed_at="2026-10-01T00:00:00+00:00",
    )
    auth = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"auth:{source_id}",
        approved_capabilities=capabilities,
        authority_reference=f"interpreted-e2e-auth:{source_id}",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        authorized_at="2026-10-01T00:00:00+00:00",
    )
    return runtime.activate(
        candidate=candidate,
        authorization=auth,
        source_id=source_id,
        activated_at="2026-10-01T00:00:00+00:00",
    )[0]


def _ids(group: str) -> dict[str, str]:
    digest = canonical_hash({"interpreted_office_group": group})[:20]
    return {
        "case_id": f"office-case:{digest}",
        "task_id": f"office-task:{digest}",
        "interaction_id": f"office-interaction:{digest}",
        "followup_id": f"office-followup:{digest}",
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


def _build_plan_from_candidate(
    candidate: SourceInterpretationCandidateV0,
    *,
    group: str,
    due_at: str,
    policy_due: bool = False,
):
    if not candidate.proposed_case_type:
        raise ValueError("INTERPRETED_E2E_CASE_TYPE_REQUIRED")
    if not candidate.proposed_title or not candidate.proposed_summary:
        raise ValueError("INTERPRETED_E2E_TITLE_SUMMARY_REQUIRED")
    if not candidate.proposed_priority:
        raise ValueError("INTERPRETED_E2E_PRIORITY_REQUIRED")
    ids = _ids(group)
    tags = [
        "ENTERPRISE_SANDBOX",
        "SOURCE_INTERPRETATION_NATIVE_V0",
        candidate.proposed_case_type,
    ]
    if policy_due:
        tags.append("POLICY_DUE_REVIEW_NOT_SOURCE_FACT")
    return build_native_case_task_intake_plan_v0(
        intake_id=f"interpreted-intake:{group}",
        case_id=ids["case_id"],
        task_id=ids["task_id"],
        interaction_id=ids["interaction_id"],
        followup_id=ids["followup_id"],
        case_type=candidate.proposed_case_type,
        title=candidate.proposed_title,
        summary=candidate.proposed_summary,
        owner_ref="role:office_operator",
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
        tags=tuple(tags),
    )


def run_interpreted_autonomous_office_e2e_v0(
    *,
    paths: EnterpriseSandboxPathsV0,
    runtime_root: Path,
    native_store_root: Path,
    governance_root: Path,
) -> dict[str, Any]:
    runtime = NativeSourceRuntimeV0(runtime_root)
    store = NativeEntityStoreV0(native_store_root)

    mail_reg = _activate_source(
        runtime=runtime,
        source_id="sandbox:mail",
        source_kind=SOURCE_MAILBOX,
        provider="LOCAL_MAIL_FIXTURE",
        capabilities=("SEARCH", "READ_MESSAGE"),
        identity_seed="mail",
    )
    doc_reg = _activate_source(
        runtime=runtime,
        source_id="sandbox:docs",
        source_kind=SOURCE_DOCUMENT_REPOSITORY,
        provider="LOCAL_DOCUMENT_REPOSITORY",
        capabilities=("SEARCH", "READ_DOCUMENT", "READ_FILE_METADATA"),
        identity_seed="docs",
    )
    cal_reg = _activate_source(
        runtime=runtime,
        source_id="sandbox:calendar",
        source_kind=SOURCE_CALENDAR,
        provider="LOCAL_CALENDAR_FIXTURE",
        capabilities=("SEARCH", "READ_EVENT"),
        identity_seed="calendar",
    )

    mail = MailNativeConnectorV0(
        runtime=runtime,
        source_id=mail_reg.source_id,
        provider=LocalMailFixtureProviderV0(paths.mailbox),
    )
    docs = DocumentNativeConnectorV0(
        runtime=runtime,
        source_id=doc_reg.source_id,
        provider=LocalDocumentRepositoryProviderV0(paths.documents),
    )
    calendar = CalendarNativeConnectorV0(
        runtime=runtime,
        source_id=cal_reg.source_id,
        provider=LocalCalendarFixtureProviderV0(paths.calendar),
    )

    interpretations: dict[str, SourceInterpretationCandidateV0] = {}

    for item_id in mail.list_item_ids():
        material, _, packet, _ = mail.read(item_id)
        interpretations[item_id] = interpret_mail_v0(
            packet=packet,
            registration=mail_reg,
            material=material,
        )

    for item_id in docs.list_item_ids():
        material, _, packet, _ = docs.read(
            item_id,
            observed_at="2026-10-05T12:00:00+00:00",
        )
        interpretations[item_id] = interpret_document_v0(
            packet=packet,
            registration=doc_reg,
            material=material,
            observed_at="2026-10-05T12:00:00+00:00",
        )

    for item_id in calendar.list_item_ids():
        material, _, packet, _ = calendar.read(item_id)
        interpretations[item_id] = interpret_calendar_v0(
            packet=packet,
            registration=cal_reg,
            material=material,
        )

    correlation = correlate_source_interpretations_v0(
        list(interpretations.values())
    )
    duplicate_map = {
        duplicate_id: primary_id
        for duplicate_id, primary_id in correlation.duplicate_links
    }
    candidate_by_id = {
        candidate.candidate_id: candidate
        for candidate in interpretations.values()
    }

    contradiction_by_candidate: dict[str, Any] = {}
    for group in correlation.contradiction_groups:
        for candidate_id in group.candidate_ids:
            contradiction_by_candidate[candidate_id] = group

    results: dict[str, Any] = {}
    committed_by_candidate: dict[str, dict[str, Any]] = {}
    handled_contradictions: set[str] = set()

    for item_id, candidate in sorted(
        interpretations.items(),
        key=lambda item: (item[1].occurred_at, item[0]),
    ):
        if candidate.interpretation_kind == KIND_INFORMATION_ONLY:
            results[item_id] = {
                "status": "NO_WORK_INFORMATION_ONLY",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
            }
            continue

        if candidate.interpretation_kind == KIND_CONSTRAINT:
            results[item_id] = {
                "status": "CONTEXT_ONLY_SUPPORTING_CONSTRAINT",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
            }
            continue

        if candidate.interpretation_kind == KIND_CALENDAR_CONTEXT:
            results[item_id] = {
                "status": (
                    "EXISTING_CALENDAR_CONTEXT_ONLY"
                    if candidate.work_identity_candidate
                    else "ROUTINE_CALENDAR_CONTEXT_ONLY"
                ),
                "canonical_mutation_count": 0,
                "linked_group": candidate.work_identity_candidate,
                "interpretation_hash": candidate.interpretation_hash,
            }
            continue

        primary_id = duplicate_map.get(candidate.candidate_id)
        if primary_id is not None:
            primary_result = committed_by_candidate.get(primary_id)
            if primary_result is None:
                raise ValueError("INTERPRETED_E2E_DUPLICATE_PRIMARY_NOT_COMMITTED")
            results[item_id] = {
                "status": "DUPLICATE_SUPPRESSED",
                "canonical_mutation_count": 0,
                "canonical_case_id": primary_result["case_id"],
                "duplicate_of_interpretation": primary_id,
                "interpretation_hash": candidate.interpretation_hash,
            }
            continue

        contradiction = contradiction_by_candidate.get(candidate.candidate_id)
        if contradiction is not None:
            if contradiction.contradiction_id in handled_contradictions:
                results[item_id] = {
                    "status": "CONTRADICTION_MEMBER_CONTEXT",
                    "canonical_mutation_count": 0,
                    "contradiction_id": contradiction.contradiction_id,
                    "interpretation_hash": candidate.interpretation_hash,
                }
                continue
            handled_contradictions.add(contradiction.contradiction_id)

            members = [
                candidate_by_id[candidate_id]
                for candidate_id in contradiction.candidate_ids
            ]
            action_members = [x for x in members if x.actionable_signal]
            seed = sorted(
                action_members,
                key=lambda x: (x.occurred_at, x.candidate_id),
            )[0]
            due = next(
                (
                    x.deadline_candidate
                    for x in action_members
                    if x.deadline_candidate is not None
                ),
                _review_policy_due_at(seed.occurred_at),
            )
            conflict_candidate = SourceInterpretationCandidateV0(
                **{
                    **seed.__dict__,
                    "proposed_case_type": CASE_CONFLICT,
                    "proposed_priority": "HIGH",
                    "proposed_title": "Resolve conflicting source instructions",
                    "proposed_summary": (
                        f"Contradictory source directives detected for "
                        f"{contradiction.subject}."
                    ),
                }
            )
            # The derived group view is not re-hashed as a new interpretation.
            # The intake evidence binds all original interpretation hashes.
            ids = _ids(contradiction.subject)
            plan = build_native_case_task_intake_plan_v0(
                intake_id=f"interpreted-intake:{contradiction.subject}",
                case_id=ids["case_id"],
                task_id=ids["task_id"],
                interaction_id=ids["interaction_id"],
                followup_id=ids["followup_id"],
                case_type=CASE_CONFLICT,
                title="Resolve conflicting source instructions",
                summary=(
                    f"Contradictory source directives detected for "
                    f"{contradiction.subject}."
                ),
                owner_ref="role:office_operator",
                priority="HIGH",
                occurred_at=seed.occurred_at,
                due_at=due,
                source_refs=tuple(
                    sorted(
                        {
                            ref
                            for member in members
                            for ref in member.provenance_refs
                        }
                    )
                ),
                evidence_refs=tuple(
                    sorted(
                        {
                            *(
                                f"interpretation:{member.interpretation_hash}"
                                for member in members
                            ),
                            f"correlation:{correlation.correlation_hash}",
                            f"contradiction:{contradiction.contradiction_hash}",
                        }
                    )
                ),
                tags=(
                    "ENTERPRISE_SANDBOX",
                    "SOURCE_INTERPRETATION_NATIVE_V0",
                    CASE_CONFLICT,
                ),
            )
            result = execute_native_case_task_intake_v0(
                plan=plan,
                store=store,
                governance_root=governance_root / canonical_hash(
                    {"contradiction": contradiction.subject}
                )[:20],
                approved_by="HUMAN:SANDBOX_OPERATOR",
                approval_reference=(
                    f"interpreted-e2e:{contradiction.contradiction_id}"
                ),
                gate_overrides={
                    "CREATE_RECORD": {
                        "contradictions": (
                            f"SOURCE_DIRECTIVE_REQUIRE:{contradiction.subject}",
                            f"SOURCE_DIRECTIVE_FORBID:{contradiction.subject}",
                        )
                    }
                },
            )
            results[contradiction.subject] = result
            results[item_id] = {
                "status": "CONTRADICTION_MEMBER_CONTEXT",
                "canonical_mutation_count": 0,
                "contradiction_id": contradiction.contradiction_id,
                "interpretation_hash": candidate.interpretation_hash,
            }
            continue

        if candidate.interpretation_kind == KIND_EVIDENCE_GAP:
            if not candidate.unknowns:
                results[item_id] = {
                    "status": "INTERPRETATION_UNKNOWN_NO_NATIVE_WORK",
                    "canonical_mutation_count": 0,
                    "interpretation_hash": candidate.interpretation_hash,
                }
                continue
            due = _review_policy_due_at(candidate.occurred_at)
            plan = _build_plan_from_candidate(
                candidate,
                group=candidate.work_identity_candidate
                or f"evidence-gap:{candidate.candidate_id}",
                due_at=due,
                policy_due=True,
            )
            result = execute_native_case_task_intake_v0(
                plan=plan,
                store=store,
                governance_root=governance_root / canonical_hash(
                    {"evidence_gap": candidate.candidate_id}
                )[:20],
                approved_by="HUMAN:SANDBOX_OPERATOR",
                approval_reference=f"interpreted-e2e:{candidate.candidate_id}",
                gate_overrides={
                    "CREATE_RECORD": {
                        "unknowns": tuple(candidate.unknowns),
                    }
                },
            )
            results[item_id] = result
            continue

        if candidate.actionable_signal:
            if not candidate.deadline_candidate:
                results[item_id] = {
                    "status": "INTERPRETATION_ACTION_WITHOUT_DUE_REVIEW_REQUIRED",
                    "canonical_mutation_count": 0,
                    "interpretation_hash": candidate.interpretation_hash,
                }
                continue
            group = candidate.work_identity_candidate or candidate.candidate_id
            plan = _build_plan_from_candidate(
                candidate,
                group=group,
                due_at=candidate.deadline_candidate,
            )
            result = execute_native_case_task_intake_v0(
                plan=plan,
                store=store,
                governance_root=governance_root / canonical_hash(
                    {"work_identity": group}
                )[:20],
                approved_by="HUMAN:SANDBOX_OPERATOR",
                approval_reference=f"interpreted-e2e:{candidate.candidate_id}",
            )
            results[item_id] = result
            if result["status"] == "NATIVE_INTAKE_COMMITTED":
                committed_by_candidate[candidate.candidate_id] = result
            continue

        results[item_id] = {
            "status": "INTERPRETATION_CONTEXT_ONLY",
            "canonical_mutation_count": 0,
            "interpretation_hash": candidate.interpretation_hash,
        }

    committed = [
        value
        for value in results.values()
        if isinstance(value, dict)
        and value.get("status") == "NATIVE_INTAKE_COMMITTED"
    ]
    total_mutations = sum(
        int(value.get("canonical_mutation_count", 0))
        for value in results.values()
        if isinstance(value, dict)
    )
    summary = {
        "schema": "OBSIDIA_INTERPRETED_AUTONOMOUS_OFFICE_E2E_RESULT_V0",
        "status": STATUS,
        "truth_manifest_used_for_routing": False,
        "interpreter_id": "OBSIDIA_SOURCE_INTERPRETER",
        "interpreter_version": "V0",
        "interpretation_candidate_count": len(interpretations),
        "correlation_hash": correlation.correlation_hash,
        "source_observation_count": (
            len(runtime.list_observations(mail_reg.source_id))
            + len(runtime.list_observations(doc_reg.source_id))
            + len(runtime.list_observations(cal_reg.source_id))
        ),
        "source_packet_count": (
            len(runtime.list_packets(mail_reg.source_id))
            + len(runtime.list_packets(doc_reg.source_id))
            + len(runtime.list_packets(cal_reg.source_id))
        ),
        "committed_case_count": len(committed),
        "canonical_mutation_count": total_mutations,
        "duplicate_suppressed_count": sum(
            1
            for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "DUPLICATE_SUPPRESSED"
        ),
        "hold_count": sum(
            1
            for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NATIVE_INTAKE_GATED_NO_MUTATION"
            and value.get("gate") == "HOLD"
        ),
        "block_count": sum(
            1
            for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NATIVE_INTAKE_GATED_NO_MUTATION"
            and value.get("gate") == "BLOCK"
        ),
        "information_only_count": sum(
            1
            for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NO_WORK_INFORMATION_ONLY"
        ),
        "external_action": False,
        "network_call_performed": False,
        "decision_authority": DECISION_AUTHORITY,
        "results": results,
        "interpretation_hashes": {
            item_id: candidate.interpretation_hash
            for item_id, candidate in sorted(interpretations.items())
        },
    }
    summary["result_hash"] = canonical_hash(summary)
    return summary
