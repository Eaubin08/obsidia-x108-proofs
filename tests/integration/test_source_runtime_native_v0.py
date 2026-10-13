from pathlib import Path

import pytest

from periphery.native_sources.common_v0 import (
    SOURCE_API_READONLY,
    SOURCE_CALENDAR,
    SOURCE_DOCUMENT_REPOSITORY,
    SOURCE_FORM_INBOX,
    SOURCE_MAILBOX,
)
from periphery.native_sources.source_onboarding_v0 import (
    activate_native_source_v0,
    build_native_human_source_authorization_v0,
    build_native_observed_source_candidate_v0,
    verify_native_human_source_authorization_v0,
    verify_native_observed_source_candidate_v0,
    verify_native_source_activation_receipt_v0,
)
from periphery.native_sources.source_registry_v0 import (
    NativeSourceRegistryV0,
    build_native_source_registration_v0,
    build_native_source_revocation_v0,
    verify_native_source_observation_v0,
    verify_native_source_registration_v0,
    verify_native_source_revocation_v0,
)
from periphery.native_sources.source_runtime_v0 import NativeSourceRuntimeV0

T0 = "2026-10-07T12:00:00+00:00"
T1 = "2026-10-07T12:05:00+00:00"
T2 = "2026-10-07T12:10:00+00:00"


def candidate(
    source_kind=SOURCE_MAILBOX,
    capabilities=("SEARCH", "READ_MESSAGE"),
    identity="a" * 64,
):
    return build_native_observed_source_candidate_v0(
        candidate_id=f"candidate:{source_kind.lower()}",
        source_kind=source_kind,
        provider="FIXTURE_PROVIDER",
        source_identity_sha256=identity,
        observed_capabilities=capabilities,
        connector_reference=f"fixture:{source_kind}",
        observed_at=T0,
    )


def authorization(candidate, capabilities=None):
    return build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"auth:{candidate.candidate_id}",
        approved_capabilities=capabilities or candidate.observed_capabilities,
        authority_reference=f"human-review:{candidate.candidate_id}",
        approved_by="HUMAN:TEST_OPERATOR",
        authorized_at=T1,
    )


def test_candidate_is_non_sovereign_and_privacy_safe():
    value = candidate()
    assert verify_native_observed_source_candidate_v0(value) == (True, None)
    assert value.internal_source_claimed is False
    assert value.raw_source_identity_persisted is False
    assert value.raw_credentials_persisted is False
    assert value.allowed_to_decide is False
    assert value.allowed_to_act is False
    assert value.decision_authority == "KX108_ONLY"


def test_authorization_is_exact_and_can_only_reduce_capabilities():
    value = candidate(capabilities=("SEARCH", "READ_MESSAGE", "READ_ATTACHMENT"))
    auth = authorization(value, ("SEARCH", "READ_MESSAGE"))
    assert verify_native_human_source_authorization_v0(
        auth, candidate=value
    ) == (True, None)
    assert auth.approved_capabilities == ("READ_MESSAGE", "SEARCH")
    assert auth.is_execution_authority is False
    assert auth.readonly_only is True


def test_machine_authorization_is_rejected():
    value = candidate()
    with pytest.raises(ValueError, match="NATIVE_SOURCE_ONBOARDING_HUMAN_REQUIRED"):
        build_native_human_source_authorization_v0(
            candidate=value,
            authorization_id="auth:machine",
            approved_capabilities=("READ_MESSAGE",),
            authority_reference="fixture:machine",
            approved_by="MACHINE",
            authorized_at=T1,
        )


def test_capability_escalation_is_rejected():
    value = candidate(capabilities=("READ_MESSAGE",))
    with pytest.raises(
        ValueError,
        match="NATIVE_SOURCE_ONBOARDING_CAPABILITY_ESCALATION_FORBIDDEN",
    ):
        authorization(value, ("READ_MESSAGE", "SEARCH"))


def test_identity_drift_invalidates_authorization():
    value = candidate(identity="a" * 64)
    auth = authorization(value)
    changed = candidate(identity="b" * 64)
    ok, reason = verify_native_human_source_authorization_v0(
        auth, candidate=changed
    )
    assert ok is False
    assert reason == "NATIVE_SOURCE_ONBOARDING_AUTH_CANDIDATE_HASH_MISMATCH"


@pytest.mark.parametrize(
    "source_kind,capabilities",
    [
        (SOURCE_MAILBOX, ("SEARCH", "READ_MESSAGE", "READ_ATTACHMENT")),
        (
            SOURCE_DOCUMENT_REPOSITORY,
            ("SEARCH", "READ_DOCUMENT", "READ_FILE_METADATA"),
        ),
        (SOURCE_CALENDAR, ("SEARCH", "READ_EVENT")),
        (SOURCE_FORM_INBOX, ("LIST", "READ_FORM_RESPONSE")),
        (SOURCE_API_READONLY, ("LIST", "READ_API_RESOURCE")),
    ],
)
def test_all_source_kinds_activate_readonly(tmp_path, source_kind, capabilities):
    runtime = NativeSourceRuntimeV0(tmp_path / source_kind)
    value = candidate(source_kind, capabilities)
    auth = authorization(value)
    registration, receipt = runtime.activate(
        candidate=value,
        authorization=auth,
        source_id=f"source:{source_kind.lower()}",
        activated_at=T1,
    )
    assert verify_native_source_registration_v0(registration) == (True, None)
    assert verify_native_source_activation_receipt_v0(
        receipt,
        candidate=value,
        authorization=auth,
        registration=registration,
    ) == (True, None)
    assert registration.readonly is True
    assert registration.external_mutation_allowed is False
    assert registration.is_execution_authority is False
    assert runtime.registry.is_active(registration.source_id) is True


@pytest.mark.parametrize(
    "forbidden",
    [
        "SEND",
        "CREATE_DRAFT",
        "WRITE",
        "UPDATE_EVENT",
        "DELETE",
        "TRASH",
        "REPLY",
        "FORWARD",
        "UPLOAD",
        "EXECUTE",
    ],
)
def test_write_like_capabilities_are_rejected(forbidden):
    with pytest.raises(ValueError, match="NATIVE_SOURCE_WRITE_CAPABILITY_FORBIDDEN"):
        build_native_source_registration_v0(
            source_id=f"forbidden:{forbidden.lower()}",
            source_kind=SOURCE_MAILBOX,
            provider="FIXTURE",
            source_identity_sha256="c" * 64,
            capabilities=("READ_MESSAGE", forbidden),
            authority_reference="fixture:forbidden",
            approved_by="HUMAN:TEST_OPERATOR",
            registered_at=T0,
        )


def test_registration_is_immutable(tmp_path):
    registry = NativeSourceRegistryV0(tmp_path / "registry")
    first = build_native_source_registration_v0(
        source_id="source:immutable",
        source_kind=SOURCE_MAILBOX,
        provider="FIXTURE",
        source_identity_sha256="d" * 64,
        capabilities=("READ_MESSAGE",),
        authority_reference="fixture:first",
        approved_by="HUMAN:TEST_OPERATOR",
        registered_at=T0,
    )
    registry.register(first)

    second = build_native_source_registration_v0(
        source_id="source:immutable",
        source_kind=SOURCE_MAILBOX,
        provider="FIXTURE",
        source_identity_sha256="e" * 64,
        capabilities=("READ_MESSAGE",),
        authority_reference="fixture:second",
        approved_by="HUMAN:TEST_OPERATOR",
        registered_at=T0,
    )
    with pytest.raises(
        ValueError,
        match="NATIVE_SOURCE_IMMUTABLE_REGISTRATION_CONFLICT",
    ):
        registry.register(second)


def test_observation_and_context_packet_are_replayable_and_non_sovereign(tmp_path):
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    value = candidate()
    auth = authorization(value)
    registration, _ = runtime.activate(
        candidate=value,
        authorization=auth,
        source_id="source:mailbox",
        activated_at=T1,
    )
    observation, packet = runtime.observe(
        source_id=registration.source_id,
        provider_item_id="raw-provider-id",
        content="raw fixture body",
        metadata={"subject": "fixture", "attachment_count": 0},
        observed_at=T2,
    )
    assert verify_native_source_observation_v0(
        observation,
        registration=registration,
    ) == (True, None)
    assert runtime.verify_packet(packet) == (True, None)
    assert observation.raw_provider_item_id_persisted is False
    assert observation.raw_content_persisted is False
    assert packet.allowed_to_decide is False
    assert packet.allowed_to_act is False
    assert packet.decision_authority == "KX108_ONLY"
    assert len(runtime.list_observations(registration.source_id)) == 1
    assert len(runtime.list_packets(registration.source_id)) == 1


def test_revocation_blocks_future_observation_and_invalidates_packet(tmp_path):
    runtime = NativeSourceRuntimeV0(tmp_path / "runtime")
    value = candidate()
    auth = authorization(value)
    registration, _ = runtime.activate(
        candidate=value,
        authorization=auth,
        source_id="source:revoked",
        activated_at=T1,
    )
    _, packet = runtime.observe(
        source_id=registration.source_id,
        provider_item_id="item-1",
        content="fixture",
        metadata={},
        observed_at=T2,
    )
    revocation = runtime.revoke(
        source_id=registration.source_id,
        revocation_id="revoke:source:revoked",
        reason="Fixture revocation",
        revoked_by="HUMAN:TEST_OPERATOR",
        revoked_at="2026-10-07T12:15:00+00:00",
    )
    assert verify_native_source_revocation_v0(
        revocation,
        registration=registration,
    ) == (True, None)
    assert runtime.registry.is_active(registration.source_id) is False
    with pytest.raises(ValueError, match="NATIVE_SOURCE_REVOKED_OR_INACTIVE"):
        runtime.observe(
            source_id=registration.source_id,
            provider_item_id="item-2",
            content="fixture 2",
            metadata={},
            observed_at="2026-10-07T12:20:00+00:00",
        )
    ok, reason = runtime.verify_packet(packet)
    assert ok is False
    assert reason == "NATIVE_SOURCE_PACKET_SOURCE_REVOKED"


def test_registration_tamper_is_detected():
    registration = build_native_source_registration_v0(
        source_id="source:tamper",
        source_kind=SOURCE_MAILBOX,
        provider="FIXTURE",
        source_identity_sha256="f" * 64,
        capabilities=("READ_MESSAGE",),
        authority_reference="fixture",
        approved_by="HUMAN:TEST_OPERATOR",
        registered_at=T0,
    )
    data = registration.to_dict()
    data["provider"] = "OTHER"
    ok, reason = verify_native_source_registration_v0(data)
    assert ok is False
    assert reason == "NATIVE_SOURCE_REGISTRATION_HASH_MISMATCH"


def test_candidate_tamper_is_detected():
    value = candidate()
    data = value.to_dict()
    data["provider"] = "OTHER"
    ok, reason = verify_native_observed_source_candidate_v0(data)
    assert ok is False
    assert reason == "NATIVE_SOURCE_ONBOARDING_CANDIDATE_HASH_MISMATCH"
