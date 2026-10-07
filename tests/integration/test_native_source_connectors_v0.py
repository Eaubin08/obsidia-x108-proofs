import json
from pathlib import Path

import pytest

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
from periphery.native_sources.mail_connector_v0 import (
    LocalMailFixtureProviderV0,
    MailNativeConnectorV0,
)
from periphery.native_sources.source_onboarding_v0 import (
    build_native_human_source_authorization_v0,
    build_native_observed_source_candidate_v0,
)
from periphery.native_sources.source_runtime_v0 import NativeSourceRuntimeV0

T0 = "2026-10-07T12:00:00+00:00"
T1 = "2026-10-07T12:05:00+00:00"


def activate(runtime, source_id, source_kind, provider, capabilities, identity):
    candidate = build_native_observed_source_candidate_v0(
        candidate_id=f"candidate:{source_id}",
        source_kind=source_kind,
        provider=provider,
        source_identity_sha256=identity,
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
    registration, _ = runtime.activate(
        candidate=candidate,
        authorization=auth,
        source_id=source_id,
        activated_at=T0,
    )
    return registration


def test_mail_connector_reads_local_fixture_into_source_runtime(tmp_path):
    mailbox = tmp_path / "mailbox"
    mailbox.mkdir()
    (mailbox / "001.json").write_text(
        json.dumps(
            {
                "id": "mail-001",
                "sender": "sender@example.invalid",
                "recipients": ["receiver@example.invalid"],
                "subject": "Action request",
                "body": "Raw body that must not be persisted.",
                "received_at": T1,
                "attachment_count": 0,
            }
        ),
        encoding="utf-8",
    )
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "1" * 64,
    )
    connector = MailNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalMailFixtureProviderV0(mailbox),
    )

    assert connector.list_item_ids() == ["mail-001"]
    material, observation, packet, receipt = connector.read("mail-001")
    assert material.subject == "Action request"
    assert material.body == "Raw body that must not be persisted."
    assert runtime.verify_packet(packet) == (True, None)
    assert verify_native_connector_read_receipt_v0(receipt) == (True, None)
    assert receipt.network_call_performed is False
    assert receipt.external_mutation_performed is False

    persisted = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "runtime").rglob("*.json")
    )
    assert "Raw body that must not be persisted." not in persisted
    assert "sender@example.invalid" not in persisted
    assert "receiver@example.invalid" not in persisted


def test_document_connector_reads_filesystem_without_persisting_content(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "contract.md").write_text(
        "Internal contract fixture body.",
        encoding="utf-8",
    )
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:docs",
        SOURCE_DOCUMENT_REPOSITORY,
        "LOCAL_DOCUMENT_REPOSITORY",
        ("SEARCH", "READ_DOCUMENT", "READ_FILE_METADATA"),
        "2" * 64,
    )
    connector = DocumentNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalDocumentRepositoryProviderV0(docs),
    )

    assert connector.list_item_ids() == ["contract.md"]
    material, observation, packet, receipt = connector.read(
        "contract.md",
        observed_at=T1,
    )
    assert material.content == "Internal contract fixture body."
    assert material.extension == ".md"
    assert runtime.verify_packet(packet) == (True, None)
    assert verify_native_connector_read_receipt_v0(receipt) == (True, None)

    persisted = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "runtime").rglob("*.json")
    )
    assert "Internal contract fixture body." not in persisted
    assert "contract.md" not in persisted


def test_document_provider_blocks_path_escape(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (tmp_path / "secret.txt").write_text("secret", encoding="utf-8")
    provider = LocalDocumentRepositoryProviderV0(docs)
    with pytest.raises(
        ValueError,
        match="DOCUMENT_NATIVE_PATH_ESCAPE_FORBIDDEN",
    ):
        provider.fetch("../secret.txt")


def test_calendar_connector_reads_fixture_without_external_effect(tmp_path):
    cal = tmp_path / "calendar"
    cal.mkdir()
    (cal / "event.json").write_text(
        json.dumps(
            {
                "id": "event-001",
                "title": "Operational deadline",
                "description": "Prepare dossier.",
                "start_time": "2026-10-08T10:00:00+00:00",
                "end_time": "2026-10-08T10:30:00+00:00",
                "timezone": "Europe/Paris",
                "attendee_count": 2,
                "location": "Fixture office",
            }
        ),
        encoding="utf-8",
    )
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:calendar",
        SOURCE_CALENDAR,
        "LOCAL_CALENDAR_FIXTURE",
        ("SEARCH", "READ_EVENT"),
        "3" * 64,
    )
    connector = CalendarNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalCalendarFixtureProviderV0(cal),
    )

    assert connector.list_item_ids() == ["event-001"]
    material, observation, packet, receipt = connector.read("event-001")
    assert material.title == "Operational deadline"
    assert runtime.verify_packet(packet) == (True, None)
    assert verify_native_connector_read_receipt_v0(receipt) == (True, None)
    assert receipt.network_call_performed is False
    assert receipt.external_mutation_performed is False

    persisted = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "runtime").rglob("*.json")
    )
    assert "Operational deadline" not in persisted
    assert "Prepare dossier." not in persisted
    assert "Fixture office" not in persisted


def test_wrong_source_kind_is_rejected(tmp_path):
    mailbox = tmp_path / "mailbox"
    mailbox.mkdir()
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:not-mail",
        SOURCE_DOCUMENT_REPOSITORY,
        "LOCAL_DOCUMENT_REPOSITORY",
        ("SEARCH", "READ_DOCUMENT"),
        "4" * 64,
    )
    connector = MailNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalMailFixtureProviderV0(mailbox),
    )
    with pytest.raises(ValueError, match="MAIL_NATIVE_SOURCE_KIND_MISMATCH"):
        connector.list_item_ids()


def test_missing_read_scope_is_rejected(tmp_path):
    cal = tmp_path / "calendar"
    cal.mkdir()
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:cal-no-read",
        SOURCE_CALENDAR,
        "LOCAL_CALENDAR_FIXTURE",
        ("SEARCH",),
        "5" * 64,
    )
    connector = CalendarNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalCalendarFixtureProviderV0(cal),
    )
    with pytest.raises(ValueError, match="CALENDAR_NATIVE_READ_SCOPE_REQUIRED"):
        connector.list_item_ids()


def test_revoked_source_blocks_connector_read(tmp_path):
    mailbox = tmp_path / "mailbox"
    mailbox.mkdir()
    (mailbox / "001.json").write_text(
        json.dumps(
            {
                "id": "mail-001",
                "sender": "a@example.invalid",
                "recipients": ["b@example.invalid"],
                "subject": "x",
                "body": "y",
                "received_at": T1,
                "attachment_count": 0,
            }
        ),
        encoding="utf-8",
    )
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:revoked-mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "6" * 64,
    )
    connector = MailNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalMailFixtureProviderV0(mailbox),
    )
    runtime.revoke(
        source_id=registration.source_id,
        revocation_id="revoke:mail",
        reason="Fixture",
        revoked_by="HUMAN:TEST_OPERATOR",
        revoked_at="2026-10-07T12:10:00+00:00",
    )
    with pytest.raises(ValueError, match="MAIL_NATIVE_SOURCE_INACTIVE"):
        connector.read("mail-001")


def test_connector_read_receipt_tamper_is_detected(tmp_path):
    mailbox = tmp_path / "mailbox"
    mailbox.mkdir()
    (mailbox / "001.json").write_text(
        json.dumps(
            {
                "id": "mail-001",
                "sender": "a@example.invalid",
                "recipients": [],
                "subject": "subject",
                "body": "body",
                "received_at": T1,
                "attachment_count": 0,
            }
        ),
        encoding="utf-8",
    )
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    registration = activate(
        runtime,
        "source:tamper-mail",
        SOURCE_MAILBOX,
        "LOCAL_MAIL_FIXTURE",
        ("SEARCH", "READ_MESSAGE"),
        "7" * 64,
    )
    connector = MailNativeConnectorV0(
        runtime=runtime,
        source_id=registration.source_id,
        provider=LocalMailFixtureProviderV0(mailbox),
    )
    _, _, _, receipt = connector.read("mail-001")
    data = receipt.to_dict()
    data["external_mutation_performed"] = True
    ok, reason = verify_native_connector_read_receipt_v0(data)
    assert ok is False
    assert reason == "NATIVE_CONNECTOR_EXTERNAL_MUTATION_FORBIDDEN"
