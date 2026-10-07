"""Interpreted enterprise-office E2E.

Unlike enterprise_office_e2e_v0, this runner never reads the sandbox truth
manifest for routing. It uses SOURCE_INTERPRETATION_NATIVE_V0 outputs and
correlation results, then sends proposed native intake plans through the
existing human/KX108-governed intake path.

The truth manifest remains test oracle only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.intake_bundle_v0 import execute_native_case_task_intake_v0
from periphery.native_ops.interpretation_to_intake_policy_v0 import (
    DISPOSITION_ACTION_PLAN,
    DISPOSITION_ACTION_REVIEW_REQUIRED,
    DISPOSITION_CALENDAR_CONTEXT,
    DISPOSITION_CONSTRAINT_CONTEXT,
    DISPOSITION_CONTEXT_ONLY,
    DISPOSITION_CONTRADICTION_MEMBER_CONTEXT,
    DISPOSITION_CONTRADICTION_REVIEW,
    DISPOSITION_DUPLICATE_SUPPRESSED,
    DISPOSITION_EVIDENCE_GAP_CONTEXT,
    DISPOSITION_EVIDENCE_GAP_REVIEW,
    DISPOSITION_INFORMATION_ONLY,
    project_interpretations_to_native_intake_v0,
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
    policy_batch = project_interpretations_to_native_intake_v0(
        interpretations,
        correlation,
        context_tags=("ENTERPRISE_SANDBOX",),
    )

    candidate_by_id = {
        candidate.candidate_id: candidate
        for candidate in interpretations.values()
    }
    item_id_by_candidate = {
        candidate.candidate_id: item_id
        for item_id, candidate in interpretations.items()
    }

    results: dict[str, Any] = {}
    committed_by_candidate: dict[str, dict[str, Any]] = {}

    for instruction in policy_batch.instructions:
        candidate = candidate_by_id[instruction.candidate_id]
        item_id = item_id_by_candidate[instruction.candidate_id]

        if instruction.disposition == DISPOSITION_INFORMATION_ONLY:
            results[item_id] = {
                "status": "NO_WORK_INFORMATION_ONLY",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_CONSTRAINT_CONTEXT:
            results[item_id] = {
                "status": "CONTEXT_ONLY_SUPPORTING_CONSTRAINT",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_CALENDAR_CONTEXT:
            results[item_id] = {
                "status": (
                    "EXISTING_CALENDAR_CONTEXT_ONLY"
                    if instruction.group_key
                    else "ROUTINE_CALENDAR_CONTEXT_ONLY"
                ),
                "canonical_mutation_count": 0,
                "linked_group": instruction.group_key,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_DUPLICATE_SUPPRESSED:
            primary_result = committed_by_candidate.get(
                instruction.duplicate_of_candidate_id or ""
            )
            if primary_result is None:
                raise ValueError("INTAKE_POLICY_DUPLICATE_PRIMARY_NOT_COMMITTED")
            results[item_id] = {
                "status": "DUPLICATE_SUPPRESSED",
                "canonical_mutation_count": 0,
                "canonical_case_id": primary_result["case_id"],
                "duplicate_of_interpretation": instruction.duplicate_of_candidate_id,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_CONTRADICTION_MEMBER_CONTEXT:
            results[item_id] = {
                "status": "CONTRADICTION_MEMBER_CONTEXT",
                "canonical_mutation_count": 0,
                "contradiction_id": instruction.contradiction_id,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_EVIDENCE_GAP_CONTEXT:
            results[item_id] = {
                "status": "INTERPRETATION_UNKNOWN_NO_NATIVE_WORK",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_ACTION_REVIEW_REQUIRED:
            results[item_id] = {
                "status": "INTERPRETATION_ACTION_WITHOUT_DUE_REVIEW_REQUIRED",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition == DISPOSITION_CONTEXT_ONLY:
            results[item_id] = {
                "status": "INTERPRETATION_CONTEXT_ONLY",
                "canonical_mutation_count": 0,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        if instruction.disposition not in {
            DISPOSITION_ACTION_PLAN,
            DISPOSITION_EVIDENCE_GAP_REVIEW,
            DISPOSITION_CONTRADICTION_REVIEW,
        }:
            raise ValueError("INTAKE_POLICY_DISPOSITION_UNSUPPORTED")
        if instruction.plan is None:
            raise ValueError("INTAKE_POLICY_EXECUTABLE_PLAN_REQUIRED")

        gate_overrides: dict[str, dict[str, tuple[str, ...]]] = {}
        create_record_override: dict[str, tuple[str, ...]] = {}
        if instruction.gate_unknowns:
            create_record_override["unknowns"] = tuple(instruction.gate_unknowns)
        if instruction.gate_contradictions:
            create_record_override["contradictions"] = tuple(
                instruction.gate_contradictions
            )
        if create_record_override:
            gate_overrides["CREATE_RECORD"] = create_record_override

        result = execute_native_case_task_intake_v0(
            plan=instruction.plan,
            store=store,
            governance_root=governance_root / instruction.policy_hash[:20],
            approved_by="HUMAN:SANDBOX_OPERATOR",
            approval_reference=f"interpreted-e2e:{instruction.instruction_id}",
            gate_overrides=gate_overrides or None,
        )

        if instruction.disposition == DISPOSITION_CONTRADICTION_REVIEW:
            if not instruction.contradiction_subject:
                raise ValueError("INTAKE_POLICY_CONTRADICTION_SUBJECT_REQUIRED")
            results[instruction.contradiction_subject] = result
            results[item_id] = {
                "status": "CONTRADICTION_MEMBER_CONTEXT",
                "canonical_mutation_count": 0,
                "contradiction_id": instruction.contradiction_id,
                "interpretation_hash": candidate.interpretation_hash,
                "intake_policy_hash": instruction.policy_hash,
            }
            continue

        results[item_id] = result
        if (
            instruction.disposition == DISPOSITION_ACTION_PLAN
            and result["status"] == "NATIVE_INTAKE_COMMITTED"
        ):
            committed_by_candidate[candidate.candidate_id] = result

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
        "intake_policy_batch_hash": policy_batch.batch_hash,
        "intake_policy_instruction_count": policy_batch.instruction_count,
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
