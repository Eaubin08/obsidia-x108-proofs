import inspect
from pathlib import Path

from periphery.native_sources.calendar_connector_v0 import (
    CalendarNativeConnectorV0,
    LocalCalendarFixtureProviderV0,
)
from periphery.native_sources.common_v0 import (
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
    materialize_enterprise_source_sandbox_v0,
)
from periphery.native_sources.mail_connector_v0 import (
    LocalMailFixtureProviderV0,
    MailNativeConnectorV0,
)
from periphery.native_sources.source_interpretation_v0 import (
    KIND_ACTION_WITH_DEADLINE,
    KIND_CALENDAR_CONTEXT,
    KIND_CONSTRAINT,
    KIND_EVIDENCE_GAP,
    KIND_INCIDENT,
    KIND_INFORMATION_ONLY,
    POLARITY_FORBID,
    POLARITY_REQUIRE,
    correlate_source_interpretations_v0,
    interpret_calendar_v0,
    interpret_document_v0,
    interpret_mail_v0,
    verify_source_interpretation_candidate_v0,
)
import periphery.native_sources.source_interpretation_v0 as interpretation_module
from periphery.native_sources.source_onboarding_v0 import (
    build_native_human_source_authorization_v0,
    build_native_observed_source_candidate_v0,
)
from periphery.native_sources.source_runtime_v0 import NativeSourceRuntimeV0

T0 = "2026-10-01T00:00:00+00:00"


def activate(runtime, source_id, source_kind, provider, capabilities, seed):
    candidate = build_native_observed_source_candidate_v0(
        candidate_id=f"candidate:{source_id}",
        source_kind=source_kind,
        provider=provider,
        source_identity_sha256=canonical_hash({"seed": seed}),
        observed_capabilities=capabilities,
        connector_reference=f"fixture:{source_id}",
        observed_at=T0,
    )
    auth = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"auth:{source_id}",
        approved_capabilities=capabilities,
        authority_reference=f"fixture-auth:{source_id}",
        approved_by="HUMAN:TEST_OPERATOR",
        authorized_at=T0,
    )
    return runtime.activate(
        candidate=candidate,
        authorization=auth,
        source_id=source_id,
        activated_at=T0,
    )[0]


def build_interpretations(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")

    mail_reg = activate(
        runtime,
        "source:mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "mail",
    )
    doc_reg = activate(
        runtime,
        "source:docs",
        SOURCE_DOCUMENT_REPOSITORY,
        "LOCAL_DOCUMENT_REPOSITORY",
        ("SEARCH", "READ_DOCUMENT", "READ_FILE_METADATA"),
        "docs",
    )
    cal_reg = activate(
        runtime,
        "source:calendar",
        SOURCE_CALENDAR,
        "LOCAL_CALENDAR_FIXTURE",
        ("SEARCH", "READ_EVENT"),
        "calendar",
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

    out = {}
    for item_id in mail.list_item_ids():
        material, _, packet, _ = mail.read(item_id)
        out[item_id] = interpret_mail_v0(
            packet=packet,
            registration=mail_reg,
            material=material,
        )

    for item_id in docs.list_item_ids():
        material, _, packet, _ = docs.read(
            item_id,
            observed_at="2026-10-05T12:00:00+00:00",
        )
        out[item_id] = interpret_document_v0(
            packet=packet,
            registration=doc_reg,
            material=material,
            observed_at="2026-10-05T12:00:00+00:00",
        )

    for item_id in calendar.list_item_ids():
        material, _, packet, _ = calendar.read(item_id)
        out[item_id] = interpret_calendar_v0(
            packet=packet,
            registration=cal_reg,
            material=material,
        )
    return out


def test_interpreter_classifies_sandbox_without_truth_manifest_routing(tmp_path):
    items = build_interpretations(tmp_path)
    assert len(items) == 12

    assert items["mail-info-001"].interpretation_kind == KIND_INFORMATION_ONLY
    assert items["mail-info-001"].information_only_signal is True

    action = items["mail-action-001"]
    assert action.interpretation_kind == KIND_ACTION_WITH_DEADLINE
    assert action.actionable_signal is True
    assert action.deadline_candidate == "2026-10-10T17:00:00+00:00"
    assert action.work_identity_candidate == "work:dossier-submission"

    duplicate = items["mail-action-001-duplicate"]
    assert duplicate.work_identity_candidate == "work:dossier-submission"
    assert duplicate.actionable_signal is True

    incident = items["mail-incident-001"]
    assert incident.interpretation_kind == KIND_INCIDENT
    assert incident.incident_signal is True
    assert incident.proposed_priority == "CRITICAL"

    missing = items["mail-missing-evidence-001"]
    assert missing.interpretation_kind == KIND_EVIDENCE_GAP
    assert missing.actionable_signal is False
    assert set(missing.unknowns) == {
        "REQUEST_AUTHORITY_UNKNOWN",
        "REQUEST_SCOPE_UNKNOWN",
    }

    contract = items["contract-renewal.md"]
    assert contract.interpretation_kind == KIND_ACTION_WITH_DEADLINE
    assert contract.work_identity_candidate == "work:contract:CR-2026-04"
    assert contract.deadline_candidate == "2026-10-12T12:00:00+00:00"

    supplier = items["supplier-terms.md"]
    assert supplier.interpretation_kind == KIND_CONSTRAINT
    assert supplier.actionable_signal is False
    assert supplier.contradiction_subject == "supplier-order:SO-77"

    assert items["policy-info.md"].interpretation_kind == KIND_INFORMATION_ONLY
    assert items["event-deadline-001"].interpretation_kind == KIND_CALENDAR_CONTEXT
    assert (
        items["event-deadline-001"].work_identity_candidate
        == "work:dossier-submission"
    )
    assert items["event-routine-001"].interpretation_kind == KIND_CALENDAR_CONTEXT


def test_correlation_detects_duplicate_and_conflict_without_deciding(tmp_path):
    items = build_interpretations(tmp_path)
    correlation = correlate_source_interpretations_v0(list(items.values()))

    duplicate_id = items["mail-action-001-duplicate"].candidate_id
    primary_id = items["mail-action-001"].candidate_id
    assert (duplicate_id, primary_id) in correlation.duplicate_links

    assert len(correlation.contradiction_groups) == 1
    group = correlation.contradiction_groups[0]
    assert group.subject == "supplier-order:SO-77"
    assert set(group.polarities) == {POLARITY_REQUIRE, POLARITY_FORBID}
    assert items["mail-conflict-a"].candidate_id in group.candidate_ids
    assert items["mail-conflict-b"].candidate_id in group.candidate_ids

    assert correlation.allowed_to_decide is False
    assert correlation.allowed_to_act is False
    assert correlation.decision_authority == "KX108_ONLY"


def test_candidates_are_deterministic_and_hash_verified(tmp_path):
    first = build_interpretations(tmp_path / "a")
    second = build_interpretations(tmp_path / "b")

    assert set(first) == set(second)
    for item_id in first:
        assert first[item_id].interpretation_hash == second[item_id].interpretation_hash
        assert first[item_id].to_dict() == second[item_id].to_dict()
        assert verify_source_interpretation_candidate_v0(first[item_id]) == (
            True,
            None,
        )


def test_interpreter_is_non_sovereign_and_has_no_native_apply_dependency(tmp_path):
    items = build_interpretations(tmp_path)
    for candidate in items.values():
        assert candidate.allowed_to_decide is False
        assert candidate.allowed_to_act is False
        assert candidate.decision_authority == "KX108_ONLY"

    source = inspect.getsource(interpretation_module)
    assert "periphery.native_ops" not in source
    assert "execute_native_case_task_intake_v0" not in source
    assert "apply_crm_mutation_v0" not in source
    assert "apply_task_mutation_v0" not in source


def test_interpretation_candidate_does_not_store_raw_material(tmp_path):
    items = build_interpretations(tmp_path)
    serialized = "\n".join(str(x.to_dict()) for x in items.values())

    assert "General information only. No response or action required." not in serialized
    assert "Please submit the requested dossier" not in serialized
    assert "Approve supplier order SO-77 today." not in serialized
    assert "Internal contract fixture body." not in serialized

    for candidate in items.values():
        assert len(candidate.material_fingerprint) == 64
