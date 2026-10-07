"""E2E_AUTONOMOUS_OFFICE_V0 — deterministic sandbox office runner.

This module is SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER.

It uses the explicit truth manifest from ENTERPRISE_SOURCE_SANDBOX_V0 as the
semantic oracle. Its purpose is to prove orchestration across real stack
contracts, not to claim a production classifier.

Flow:
native source connectors
→ native source runtime packets
→ sandbox truth oracle
→ generic native intake bundle
→ WORLD_ACTION_PRE / GuardX108
→ canonical CRM/TASKS
→ receipts / replay
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import tempfile
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
    load_enterprise_sandbox_truth_v0,
)
from periphery.native_sources.mail_connector_v0 import (
    LocalMailFixtureProviderV0,
    MailNativeConnectorV0,
)
from periphery.native_sources.source_onboarding_v0 import (
    build_native_human_source_authorization_v0,
    build_native_observed_source_candidate_v0,
)
from periphery.native_sources.source_runtime_v0 import NativeSourceRuntimeV0

STATUS = "SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER"


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
            {"sandbox_source_identity": identity_seed}
        ),
        observed_capabilities=capabilities,
        connector_reference=f"sandbox:{source_id}",
        observed_at="2026-10-01T00:00:00+00:00",
    )
    auth = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"auth:{source_id}",
        approved_capabilities=capabilities,
        authority_reference=f"sandbox-auth:{source_id}",
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
    digest = canonical_hash({"office_case_group": group})[:20]
    return {
        "case_id": f"office-case:{digest}",
        "task_id": f"office-task:{digest}",
        "interaction_id": f"office-interaction:{digest}",
        "followup_id": f"office-followup:{digest}",
    }


def _plan(
    *,
    group: str,
    case_type: str,
    title: str,
    summary: str,
    priority: str,
    occurred_at: str,
    due_at: str,
    source_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
):
    ids = _ids(group)
    return build_native_case_task_intake_plan_v0(
        intake_id=f"office-intake:{group}",
        case_id=ids["case_id"],
        task_id=ids["task_id"],
        interaction_id=ids["interaction_id"],
        followup_id=ids["followup_id"],
        case_type=case_type,
        title=title,
        summary=summary,
        owner_ref="role:office_operator",
        priority=priority,
        occurred_at=occurred_at,
        due_at=due_at,
        source_refs=source_refs,
        evidence_refs=evidence_refs,
        tags=("ENTERPRISE_SANDBOX", case_type),
    )


def run_autonomous_office_e2e_v0(
    *,
    paths: EnterpriseSandboxPathsV0,
    runtime_root: Path,
    native_store_root: Path,
    governance_root: Path,
) -> dict[str, Any]:
    truth = load_enterprise_sandbox_truth_v0(paths)
    if truth.get("status") != "SIMULATED_NOT_OBSERVED":
        raise ValueError("OFFICE_E2E_REQUIRES_SIMULATED_TRUTH_MANIFEST")

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

    packets: dict[str, Any] = {}
    mail_materials: dict[str, Any] = {}
    for item_id in mail.list_item_ids():
        material, observation, packet, receipt = mail.read(item_id)
        packets[item_id] = packet
        mail_materials[item_id] = material

    doc_materials: dict[str, Any] = {}
    for item_id in docs.list_item_ids():
        material, observation, packet, receipt = docs.read(
            item_id,
            observed_at="2026-10-05T12:00:00+00:00",
        )
        packets[item_id] = packet
        doc_materials[item_id] = material

    event_materials: dict[str, Any] = {}
    for item_id in calendar.list_item_ids():
        material, observation, packet, receipt = calendar.read(item_id)
        packets[item_id] = packet
        event_materials[item_id] = material

    results: dict[str, Any] = {}
    committed_groups: set[str] = set()

    # Information-only mail.
    results["mail-info-001"] = {
        "status": "NO_WORK_INFORMATION_ONLY",
        "canonical_mutation_count": 0,
    }

    # Action + deadline.
    action_packet = packets["mail-action-001"]
    action_plan = _plan(
        group="dossier-submission",
        case_type="ACTION_WITH_DEADLINE",
        title="Submit requested dossier",
        summary="Synthetic action request with explicit deadline.",
        priority="HIGH",
        occurred_at=mail_materials["mail-action-001"].received_at,
        due_at="2026-10-10T17:00:00+00:00",
        source_refs=(f"source-packet:{action_packet.packet_hash}",),
        evidence_refs=(f"source-observation:{action_packet.observation_hash}",),
    )
    action_result = execute_native_case_task_intake_v0(
        plan=action_plan,
        store=store,
        governance_root=governance_root / "dossier-submission",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="sandbox:dossier-submission",
    )
    results["mail-action-001"] = action_result
    if action_result["status"] == "NATIVE_INTAKE_COMMITTED":
        committed_groups.add("dossier-submission")

    # Duplicate reminder maps to the same canonical group and is suppressed.
    duplicate_group = "dossier-submission"
    if duplicate_group in committed_groups:
        results["mail-action-001-duplicate"] = {
            "status": "DUPLICATE_SUPPRESSED",
            "canonical_mutation_count": 0,
            "canonical_case_id": action_result["case_id"],
        }
    else:
        raise ValueError("OFFICE_E2E_DUPLICATE_GROUP_WITHOUT_PRIMARY")

    # Incident.
    incident_packet = packets["mail-incident-001"]
    incident_plan = _plan(
        group="access-control-incident",
        case_type="INCIDENT",
        title="Investigate access-control incident",
        summary="Synthetic operational incident requires investigation.",
        priority="CRITICAL",
        occurred_at=mail_materials["mail-incident-001"].received_at,
        due_at="2026-10-03T12:00:00+00:00",
        source_refs=(f"source-packet:{incident_packet.packet_hash}",),
        evidence_refs=(f"source-observation:{incident_packet.observation_hash}",),
    )
    results["mail-incident-001"] = execute_native_case_task_intake_v0(
        plan=incident_plan,
        store=store,
        governance_root=governance_root / "access-control-incident",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="sandbox:access-control-incident",
    )
    if results["mail-incident-001"]["status"] == "NATIVE_INTAKE_COMMITTED":
        committed_groups.add("access-control-incident")

    # Contract deadline from document.
    contract_packet = packets["contract-renewal.md"]
    contract_plan = _plan(
        group="contract-renewal",
        case_type="CONTRACT_DEADLINE",
        title="Review contract renewal",
        summary="Synthetic contract requires renewal review before deadline.",
        priority="HIGH",
        occurred_at="2026-10-05T12:00:00+00:00",
        due_at="2026-10-12T12:00:00+00:00",
        source_refs=(f"source-packet:{contract_packet.packet_hash}",),
        evidence_refs=(f"source-observation:{contract_packet.observation_hash}",),
    )
    results["contract-renewal.md"] = execute_native_case_task_intake_v0(
        plan=contract_plan,
        store=store,
        governance_root=governance_root / "contract-renewal",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="sandbox:contract-renewal",
    )
    if results["contract-renewal.md"]["status"] == "NATIVE_INTAKE_COMMITTED":
        committed_groups.add("contract-renewal")

    results["policy-info.md"] = {
        "status": "NO_WORK_INFORMATION_ONLY",
        "canonical_mutation_count": 0,
    }
    results["supplier-terms.md"] = {
        "status": "CONTEXT_ONLY_SUPPORTING_CONSTRAINT",
        "canonical_mutation_count": 0,
    }
    results["event-deadline-001"] = {
        "status": "EXISTING_CALENDAR_CONTEXT_ONLY",
        "canonical_mutation_count": 0,
        "linked_group": "dossier-submission",
    }
    results["event-routine-001"] = {
        "status": "ROUTINE_CALENDAR_CONTEXT_ONLY",
        "canonical_mutation_count": 0,
    }

    # Contradictory instructions must BLOCK before canonical mutation.
    conflict_packet_a = packets["mail-conflict-a"]
    conflict_packet_b = packets["mail-conflict-b"]
    conflict_plan = _plan(
        group="supplier-order-so77",
        case_type="CONFLICTING_INSTRUCTIONS",
        title="Resolve supplier order conflict",
        summary="Synthetic contradictory instructions for supplier order SO-77.",
        priority="HIGH",
        occurred_at=mail_materials["mail-conflict-a"].received_at,
        due_at="2026-10-03T17:00:00+00:00",
        source_refs=(
            f"source-packet:{conflict_packet_a.packet_hash}",
            f"source-packet:{conflict_packet_b.packet_hash}",
        ),
        evidence_refs=(
            f"source-observation:{conflict_packet_a.observation_hash}",
            f"source-observation:{conflict_packet_b.observation_hash}",
        ),
    )
    conflict_result = execute_native_case_task_intake_v0(
        plan=conflict_plan,
        store=store,
        governance_root=governance_root / "supplier-order-so77",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="sandbox:supplier-order-so77",
        gate_overrides={
            "CREATE_RECORD": {
                "contradictions": (
                    "APPROVE_ORDER_REQUIRED",
                    "APPROVE_ORDER_FORBIDDEN",
                )
            }
        },
    )
    results["supplier-order-so77"] = conflict_result

    # Missing evidence must HOLD.
    missing_packet = packets["mail-missing-evidence-001"]
    missing_plan = _plan(
        group="missing-evidence-request",
        case_type="MISSING_EVIDENCE",
        title="Clarify incomplete request",
        summary="Synthetic request lacks enough evidence to authorize work.",
        priority="NORMAL",
        occurred_at=mail_materials["mail-missing-evidence-001"].received_at,
        due_at="2026-10-06T17:00:00+00:00",
        source_refs=(f"source-packet:{missing_packet.packet_hash}",),
        evidence_refs=(f"source-observation:{missing_packet.observation_hash}",),
    )
    missing_result = execute_native_case_task_intake_v0(
        plan=missing_plan,
        store=store,
        governance_root=governance_root / "missing-evidence-request",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="sandbox:missing-evidence-request",
        gate_overrides={
            "CREATE_RECORD": {
                "unknowns": (
                    "REQUEST_SCOPE_UNKNOWN",
                    "REQUEST_AUTHORITY_UNKNOWN",
                )
            }
        },
    )
    results["mail-missing-evidence-001"] = missing_result

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
        "schema": "OBSIDIA_AUTONOMOUS_OFFICE_E2E_RESULT_V0",
        "status": STATUS,
        "sandbox_truth_status": truth["status"],
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
            1 for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "DUPLICATE_SUPPRESSED"
        ),
        "hold_count": sum(
            1 for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NATIVE_INTAKE_GATED_NO_MUTATION"
            and value.get("gate") == "HOLD"
        ),
        "block_count": sum(
            1 for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NATIVE_INTAKE_GATED_NO_MUTATION"
            and value.get("gate") == "BLOCK"
        ),
        "information_only_count": sum(
            1 for value in results.values()
            if isinstance(value, dict)
            and value.get("status") == "NO_WORK_INFORMATION_ONLY"
        ),
        "external_action": False,
        "network_call_performed": False,
        "decision_authority": DECISION_AUTHORITY,
        "results": results,
    }
    summary["result_hash"] = canonical_hash(summary)
    return summary
