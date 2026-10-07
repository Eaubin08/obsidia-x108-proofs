"""Two-key onboarding for SOURCE_RUNTIME_NATIVE_V0."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

from .common_v0 import (
    DECISION_AUTHORITY,
    SOURCE_KINDS,
    canonical_hash,
    require_time,
)
from .source_registry_v0 import (
    NativeSourceRegistrationV0,
    NativeSourceRegistryV0,
    build_native_source_registration_v0,
)

@dataclass(frozen=True)
class NativeObservedSourceCandidateV0:
    schema: str
    candidate_id: str
    source_kind: str
    provider: str
    source_identity_sha256: str
    observed_capabilities: tuple[str, ...]
    connector_reference: str
    observed_at: str
    raw_source_identity_persisted: bool
    raw_credentials_persisted: bool
    internal_source_claimed: bool
    allowed_to_decide: bool
    allowed_to_act: bool
    decision_authority: str
    candidate_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["observed_capabilities"] = list(self.observed_capabilities)
        return data


@dataclass(frozen=True)
class NativeHumanSourceAuthorizationV0:
    schema: str
    authorization_id: str
    candidate_id: str
    candidate_hash: str
    source_identity_sha256: str
    approved_capabilities: tuple[str, ...]
    authority_reference: str
    approved_by: str
    authorized_at: str
    internal_source: bool
    readonly_only: bool
    is_execution_authority: bool
    decision_authority: str
    authorization_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["approved_capabilities"] = list(self.approved_capabilities)
        return data


@dataclass(frozen=True)
class NativeSourceActivationReceiptV0:
    schema: str
    receipt_id: str
    candidate_hash: str
    authorization_hash: str
    registration_hash: str
    source_id: str
    source_kind: str
    provider: str
    active: bool
    readonly: bool
    external_mutation_allowed: bool
    activated_at: str
    decision_authority: str
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _candidate_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "candidate_id", "source_kind", "provider",
        "source_identity_sha256", "observed_capabilities",
        "connector_reference", "observed_at",
        "raw_source_identity_persisted", "raw_credentials_persisted",
        "internal_source_claimed", "allowed_to_decide", "allowed_to_act",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_observed_source_candidate_v0(
    *,
    candidate_id: str,
    source_kind: str,
    provider: str,
    source_identity_sha256: str,
    observed_capabilities: tuple[str, ...],
    connector_reference: str,
    observed_at: str,
) -> NativeObservedSourceCandidateV0:
    if source_kind not in SOURCE_KINDS:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_KIND_INVALID")
    if not candidate_id or not provider or not connector_reference:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_FIELDS_REQUIRED")
    if len(source_identity_sha256) != 64:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_IDENTITY_HASH_INVALID")
    if not observed_capabilities:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_CAPABILITIES_REQUIRED")
    require_time(observed_at)
    normalized = tuple(sorted(set(observed_capabilities)))
    payload = {
        "schema": "OBSIDIA_NATIVE_OBSERVED_SOURCE_CANDIDATE_V0",
        "candidate_id": candidate_id,
        "source_kind": source_kind,
        "provider": provider,
        "source_identity_sha256": source_identity_sha256,
        "observed_capabilities": list(normalized),
        "connector_reference": connector_reference,
        "observed_at": observed_at,
        "raw_source_identity_persisted": False,
        "raw_credentials_persisted": False,
        "internal_source_claimed": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeObservedSourceCandidateV0(
        schema=payload["schema"],
        candidate_id=candidate_id,
        source_kind=source_kind,
        provider=provider,
        source_identity_sha256=source_identity_sha256,
        observed_capabilities=normalized,
        connector_reference=connector_reference,
        observed_at=observed_at,
        raw_source_identity_persisted=False,
        raw_credentials_persisted=False,
        internal_source_claimed=False,
        allowed_to_decide=False,
        allowed_to_act=False,
        decision_authority=DECISION_AUTHORITY,
        candidate_hash=canonical_hash(payload),
    )


def verify_native_observed_source_candidate_v0(
    candidate: NativeObservedSourceCandidateV0 | Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if candidate is None:
        return False, "NATIVE_SOURCE_ONBOARDING_CANDIDATE_MISSING"
    data = (
        candidate.to_dict()
        if isinstance(candidate, NativeObservedSourceCandidateV0)
        else dict(candidate)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_OBSERVED_SOURCE_CANDIDATE_V0":
        return False, "NATIVE_SOURCE_ONBOARDING_CANDIDATE_SCHEMA_INVALID"
    if data.get("source_kind") not in SOURCE_KINDS:
        return False, "NATIVE_SOURCE_ONBOARDING_KIND_INVALID"
    if len(str(data.get("source_identity_sha256", ""))) != 64:
        return False, "NATIVE_SOURCE_ONBOARDING_IDENTITY_HASH_INVALID"
    if data.get("raw_source_identity_persisted") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_RAW_IDENTITY_FORBIDDEN"
    if data.get("raw_credentials_persisted") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_RAW_CREDENTIALS_FORBIDDEN"
    if data.get("internal_source_claimed") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_SELF_CLAIM_FORBIDDEN"
    if data.get("allowed_to_decide") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_DECISION_FORBIDDEN"
    if data.get("allowed_to_act") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_ACTION_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTHORITY_INVALID"
    try:
        require_time(str(data.get("observed_at")))
    except ValueError as exc:
        return False, str(exc)
    if canonical_hash(_candidate_payload(data)) != data.get("candidate_hash"):
        return False, "NATIVE_SOURCE_ONBOARDING_CANDIDATE_HASH_MISMATCH"
    return True, None


def _authorization_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "authorization_id", "candidate_id", "candidate_hash",
        "source_identity_sha256", "approved_capabilities",
        "authority_reference", "approved_by", "authorized_at",
        "internal_source", "readonly_only", "is_execution_authority",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_human_source_authorization_v0(
    *,
    candidate: NativeObservedSourceCandidateV0,
    authorization_id: str,
    approved_capabilities: tuple[str, ...],
    authority_reference: str,
    approved_by: str,
    authorized_at: str,
) -> NativeHumanSourceAuthorizationV0:
    ok, reason = verify_native_observed_source_candidate_v0(candidate)
    if not ok:
        raise ValueError(reason)
    if not authorization_id or not authority_reference:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_AUTH_FIELDS_REQUIRED")
    if approved_by == "MACHINE" or not approved_by:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_HUMAN_REQUIRED")
    require_time(authorized_at)
    approved = tuple(sorted(set(approved_capabilities)))
    if not approved:
        raise ValueError("NATIVE_SOURCE_ONBOARDING_APPROVED_CAPABILITIES_REQUIRED")
    if not set(approved).issubset(set(candidate.observed_capabilities)):
        raise ValueError("NATIVE_SOURCE_ONBOARDING_CAPABILITY_ESCALATION_FORBIDDEN")
    payload = {
        "schema": "OBSIDIA_NATIVE_HUMAN_SOURCE_AUTHORIZATION_V0",
        "authorization_id": authorization_id,
        "candidate_id": candidate.candidate_id,
        "candidate_hash": candidate.candidate_hash,
        "source_identity_sha256": candidate.source_identity_sha256,
        "approved_capabilities": list(approved),
        "authority_reference": authority_reference,
        "approved_by": approved_by,
        "authorized_at": authorized_at,
        "internal_source": True,
        "readonly_only": True,
        "is_execution_authority": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeHumanSourceAuthorizationV0(
        schema=payload["schema"],
        authorization_id=authorization_id,
        candidate_id=candidate.candidate_id,
        candidate_hash=candidate.candidate_hash,
        source_identity_sha256=candidate.source_identity_sha256,
        approved_capabilities=approved,
        authority_reference=authority_reference,
        approved_by=approved_by,
        authorized_at=authorized_at,
        internal_source=True,
        readonly_only=True,
        is_execution_authority=False,
        decision_authority=DECISION_AUTHORITY,
        authorization_hash=canonical_hash(payload),
    )


def verify_native_human_source_authorization_v0(
    authorization: NativeHumanSourceAuthorizationV0 | Mapping[str, Any] | None,
    *,
    candidate: NativeObservedSourceCandidateV0,
) -> tuple[bool, Optional[str]]:
    if authorization is None:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTHORIZATION_MISSING"
    data = (
        authorization.to_dict()
        if isinstance(authorization, NativeHumanSourceAuthorizationV0)
        else dict(authorization)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_HUMAN_SOURCE_AUTHORIZATION_V0":
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_SCHEMA_INVALID"
    if data.get("candidate_id") != candidate.candidate_id:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_CANDIDATE_ID_MISMATCH"
    if data.get("candidate_hash") != candidate.candidate_hash:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_CANDIDATE_HASH_MISMATCH"
    if data.get("source_identity_sha256") != candidate.source_identity_sha256:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_IDENTITY_MISMATCH"
    if not set(data.get("approved_capabilities") or ()).issubset(
        set(candidate.observed_capabilities)
    ):
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_CAPABILITY_ESCALATION"
    if data.get("internal_source") is not True:
        return False, "NATIVE_SOURCE_ONBOARDING_INTERNAL_SCOPE_REQUIRED"
    if data.get("readonly_only") is not True:
        return False, "NATIVE_SOURCE_ONBOARDING_READONLY_REQUIRED"
    if data.get("is_execution_authority") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_EXECUTION_AUTHORITY_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_ONBOARDING_AUTHORITY_INVALID"
    if not data.get("approved_by") or data.get("approved_by") == "MACHINE":
        return False, "NATIVE_SOURCE_ONBOARDING_HUMAN_REQUIRED"
    try:
        require_time(str(data.get("authorized_at")))
    except ValueError as exc:
        return False, str(exc)
    if canonical_hash(_authorization_payload(data)) != data.get("authorization_hash"):
        return False, "NATIVE_SOURCE_ONBOARDING_AUTH_HASH_MISMATCH"
    return True, None


def _receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "receipt_id", "candidate_hash", "authorization_hash",
        "registration_hash", "source_id", "source_kind", "provider",
        "active", "readonly", "external_mutation_allowed", "activated_at",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def activate_native_source_v0(
    *,
    candidate: NativeObservedSourceCandidateV0,
    authorization: NativeHumanSourceAuthorizationV0,
    registry: NativeSourceRegistryV0,
    source_id: str,
    activated_at: str,
) -> tuple[NativeSourceRegistrationV0, NativeSourceActivationReceiptV0]:
    ok, reason = verify_native_observed_source_candidate_v0(candidate)
    if not ok:
        raise ValueError(reason)
    ok, reason = verify_native_human_source_authorization_v0(
        authorization, candidate=candidate
    )
    if not ok:
        raise ValueError(reason)
    require_time(activated_at)
    registration = build_native_source_registration_v0(
        source_id=source_id,
        source_kind=candidate.source_kind,
        provider=candidate.provider,
        source_identity_sha256=candidate.source_identity_sha256,
        capabilities=authorization.approved_capabilities,
        authority_reference=f"native-onboarding:{authorization.authorization_hash}",
        approved_by=authorization.approved_by,
        registered_at=activated_at,
    )
    registry.register(registration)
    payload = {
        "schema": "OBSIDIA_NATIVE_SOURCE_ACTIVATION_RECEIPT_V0",
        "receipt_id": f"sourceactivation-{canonical_hash({
            'candidate': candidate.candidate_hash,
            'authorization': authorization.authorization_hash,
            'registration': registration.registration_hash,
        })[:32]}",
        "candidate_hash": candidate.candidate_hash,
        "authorization_hash": authorization.authorization_hash,
        "registration_hash": registration.registration_hash,
        "source_id": registration.source_id,
        "source_kind": registration.source_kind,
        "provider": registration.provider,
        "active": registry.is_active(registration.source_id),
        "readonly": registration.readonly,
        "external_mutation_allowed": registration.external_mutation_allowed,
        "activated_at": activated_at,
        "decision_authority": DECISION_AUTHORITY,
    }
    return registration, NativeSourceActivationReceiptV0(
        **payload,
        receipt_hash=canonical_hash(payload),
    )


def verify_native_source_activation_receipt_v0(
    receipt: NativeSourceActivationReceiptV0 | Mapping[str, Any],
    *,
    candidate: NativeObservedSourceCandidateV0,
    authorization: NativeHumanSourceAuthorizationV0,
    registration: NativeSourceRegistrationV0,
) -> tuple[bool, Optional[str]]:
    data = (
        receipt.to_dict()
        if isinstance(receipt, NativeSourceActivationReceiptV0)
        else dict(receipt)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_ACTIVATION_RECEIPT_V0":
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_SCHEMA_INVALID"
    if data.get("candidate_hash") != candidate.candidate_hash:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_CANDIDATE_MISMATCH"
    if data.get("authorization_hash") != authorization.authorization_hash:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_AUTHORIZATION_MISMATCH"
    if data.get("registration_hash") != registration.registration_hash:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_REGISTRATION_MISMATCH"
    if data.get("source_id") != registration.source_id:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_SOURCE_MISMATCH"
    if data.get("readonly") is not True:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_READONLY_INVALID"
    if data.get("external_mutation_allowed") is not False:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_MUTATION_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_AUTHORITY_INVALID"
    if canonical_hash(_receipt_payload(data)) != data.get("receipt_hash"):
        return False, "NATIVE_SOURCE_ONBOARDING_RECEIPT_HASH_MISMATCH"
    return True, None
