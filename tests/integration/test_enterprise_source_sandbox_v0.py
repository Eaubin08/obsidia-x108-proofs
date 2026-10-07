import json
from pathlib import Path

from periphery.native_sources.calendar_connector_v0 import (
    CalendarNativeConnectorV0,
    LocalCalendarFixtureProviderV0,
)
from periphery.native_sources.common_v0 import (
    SOURCE_CALENDAR,
    SOURCE_DOCUMENT_REPOSITORY,
    SOURCE_MAILBOX,
)
from periphery.native_sources.connector_common_v0 import (
    verify_native_connector_read_receipt_v0,
)
from periphery.native_sources.document_connector_v0 import (
    DocumentNativeConnectorV0,
    LocalDocumentRepositoryProviderV0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    SANDBOX_STATUS,
    load_enterprise_sandbox_truth_v0,
    materialize_enterprise_source_sandbox_v0,
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

T0 = "2026-10-01T00:00:00+00:00"


def activate(runtime, source_id, kind, provider, capabilities, identity):
    candidate = build_native_observed_source_candidate_v0(
        candidate_id=f"candidate:{source_id}",
        source_kind=kind,
        provider=provider,
        source_identity_sha256=identity,
        observed_capabilities=capabilities,
        connector_reference=f"sandbox:{source_id}",
        observed_at=T0,
    )
    auth = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"auth:{source_id}",
        approved_capabilities=capabilities,
        authority_reference=f"sandbox-auth:{source_id}",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        authorized_at=T0,
    )
    return runtime.activate(
        candidate=candidate,
        authorization=auth,
        source_id=source_id,
        activated_at=T0,
    )[0]


def test_enterprise_source_sandbox_materializes_full_office(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    truth = load_enterprise_sandbox_truth_v0(paths)

    assert truth["status"] == SANDBOX_STATUS
    assert truth["mail_count"] == 7
    assert truth["document_count"] == 3
    assert truth["calendar_event_count"] == 2
    assert truth["expected_global"]["unique_actionable_cases"] == 3
    assert truth["expected_global"]["information_only_items"] == 2
    assert truth["expected_global"]["hold_groups"] == 1
    assert truth["expected_global"]["block_groups"] == 1
    assert truth["expected_global"]["duplicate_groups"] == 1
    assert truth["expected_global"]["external_mutation"] is False
    assert truth["expected_global"]["decision_authority"] == "KX108_ONLY"


def test_enterprise_sandbox_all_sources_ingest_via_native_connectors(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")

    mail_reg = activate(
        runtime,
        "sandbox:mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "1" * 64,
    )
    doc_reg = activate(
        runtime,
        "sandbox:docs",
        SOURCE_DOCUMENT_REPOSITORY,
        "LOCAL_DOCUMENT_REPOSITORY",
        ("SEARCH", "READ_DOCUMENT", "READ_FILE_METADATA"),
        "2" * 64,
    )
    cal_reg = activate(
        runtime,
        "sandbox:calendar",
        SOURCE_CALENDAR,
        "LOCAL_CALENDAR_FIXTURE",
        ("SEARCH", "READ_EVENT"),
        "3" * 64,
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

    mail_ids = mail.list_item_ids()
    doc_ids = docs.list_item_ids()
    event_ids = calendar.list_item_ids()

    assert len(mail_ids) == 7
    assert len(doc_ids) == 3
    assert len(event_ids) == 2

    receipts = []
    for item_id in mail_ids:
        material, observation, packet, receipt = mail.read(item_id)
        assert runtime.verify_packet(packet) == (True, None)
        assert observation.source_id == mail_reg.source_id
        receipts.append(receipt)

    for item_id in doc_ids:
        material, observation, packet, receipt = docs.read(
            item_id,
            observed_at="2026-10-05T12:00:00+00:00",
        )
        assert runtime.verify_packet(packet) == (True, None)
        assert observation.source_id == doc_reg.source_id
        receipts.append(receipt)

    for item_id in event_ids:
        material, observation, packet, receipt = calendar.read(item_id)
        assert runtime.verify_packet(packet) == (True, None)
        assert observation.source_id == cal_reg.source_id
        receipts.append(receipt)

    assert len(receipts) == 12
    for receipt in receipts:
        assert verify_native_connector_read_receipt_v0(receipt) == (True, None)
        assert receipt.external_mutation_performed is False
        assert receipt.network_call_performed is False
        assert receipt.decision_authority == "KX108_ONLY"

    assert len(runtime.list_observations(mail_reg.source_id)) == 7
    assert len(runtime.list_observations(doc_reg.source_id)) == 3
    assert len(runtime.list_observations(cal_reg.source_id)) == 2


def test_enterprise_sandbox_persists_no_raw_business_material(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")

    mail_reg = activate(
        runtime,
        "sandbox:mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "4" * 64,
    )
    doc_reg = activate(
        runtime,
        "sandbox:docs",
        SOURCE_DOCUMENT_REPOSITORY,
        "LOCAL_DOCUMENT_REPOSITORY",
        ("SEARCH", "READ_DOCUMENT"),
        "5" * 64,
    )
    cal_reg = activate(
        runtime,
        "sandbox:calendar",
        SOURCE_CALENDAR,
        "LOCAL_CALENDAR_FIXTURE",
        ("SEARCH", "READ_EVENT"),
        "6" * 64,
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

    for item_id in mail.list_item_ids():
        mail.read(item_id)
    for item_id in docs.list_item_ids():
        docs.read(item_id, observed_at="2026-10-05T12:00:00+00:00")
    for item_id in calendar.list_item_ids():
        calendar.read(item_id)

    persisted = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "runtime").rglob("*.json")
    )

    forbidden_raw = [
        "Please submit the requested dossier",
        "Access control is unavailable",
        "Approve supplier order SO-77",
        "Do not approve supplier order SO-77",
        "Contract CR-2026-04",
        "Order SO-77 requires dual validation",
        "Dossier submission deadline",
        "Weekly coordination",
        "communication@example.invalid",
        "office@example.invalid",
    ]
    for value in forbidden_raw:
        assert value not in persisted


def test_enterprise_sandbox_truth_contains_conflict_duplicate_and_missing_evidence(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    truth = load_enterprise_sandbox_truth_v0(paths)
    mail_truth = truth["mail_truth"]

    assert mail_truth["mail-conflict-a"]["conflict_group"] == "supplier-order-so77"
    assert mail_truth["mail-conflict-b"]["conflict_group"] == "supplier-order-so77"
    assert mail_truth["mail-conflict-a"]["expected_gate"] == "BLOCK"
    assert mail_truth["mail-conflict-b"]["expected_gate"] == "BLOCK"

    assert mail_truth["mail-action-001-duplicate"]["duplicate_of"] == "mail-action-001"
    assert mail_truth["mail-action-001-duplicate"]["must_not_create_second_case"] is True

    assert mail_truth["mail-missing-evidence-001"]["expected_gate"] == "HOLD"


def test_sandbox_is_explicitly_not_real_observation(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    truth = load_enterprise_sandbox_truth_v0(paths)
    assert truth["status"] == "SIMULATED_NOT_OBSERVED"
