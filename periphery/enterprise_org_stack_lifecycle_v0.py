"""V0.1 C2: read-only organization/stack lifecycle over existing native contracts.

An in-memory evidence join, NOT a credential store, tenant-authentication service,
Binder permission, KX decision, data connector or execution router.
An operator's source approval is not proof of authority over the organization.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping

from periphery.company_model_v0 import verify_company_model_snapshot_v0
from periphery.native_ops.common_v0 import DECISION_AUTHORITY, canonical_hash
from periphery.native_sources.common_v0 import require_time
from periphery.native_sources.source_onboarding_v0 import (
    NativeHumanSourceAuthorizationV0,
    NativeObservedSourceCandidateV0,
    NativeSourceActivationReceiptV0,
    verify_native_human_source_authorization_v0,
    verify_native_observed_source_candidate_v0,
    verify_native_source_activation_receipt_v0,
)
from periphery.native_sources.source_registry_v0 import (
    NativeSourceRegistrationV0, NativeSourceRegistryV0,
    verify_native_source_registration_v0,
)
from periphery.universal_enterprise_stack_adapter_v0 import (
    EnterpriseSourceBindingV0, EnterpriseStackManifestV0,
    build_enterprise_source_binding_v0, verify_enterprise_stack_manifest_v0,
)

LINK_SCHEMA = "V01_ENTERPRISE_ORG_STACK_READONLY_LINK_V0"
REVOCATION_SCHEMA = "V01_ENTERPRISE_ORG_STACK_LINK_REVOCATION_V0"
LINK_STATUS = "LINKED_READONLY_NO_ORGANIZATION_AUTHORITY"
REFUSED_STATUS = "NOT_AVAILABLE"
_SLOT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_ID_PREFIX = "company-source-link:"


@dataclass(frozen=True)
class CompanyStackLinkV0:
    schema: str
    link_id: str
    organization_id: str
    company_snapshot_hash: str
    domain_id: str
    tool_instance_id: str
    integration_slot_id: str
    source_id: str
    source_registration_hash: str
    source_authorization_hash: str
    source_activation_receipt_hash: str
    provider_id: str
    stack_id: str
    manifest_hash: str
    source_capability_id: str
    source_binding_hash: str
    linked_at: str
    organization_authority_verified: bool
    has_runtime_permission: bool
    allows_provider_calls: bool
    allowed_to_decide: bool
    allowed_to_act: bool
    decision_authority: str
    link_hash: str


@dataclass(frozen=True)
class CompanyStackLinkRevocationV0:
    schema: str
    revocation_id: str
    link_id: str
    organization_id: str
    reason_ref: str
    revoked_by: str
    revoked_at: str
    is_execution_authority: bool
    decision_authority: str
    revocation_hash: str


def _link_payload(link: CompanyStackLinkV0) -> dict[str, Any]:
    value = asdict(link)
    value.pop("link_hash")
    return value


def _check_existing_proofs(
    *,
    company: Mapping[str, Any], domain_id: str, tool_instance_id: str,
    source_id: str, manifest: EnterpriseStackManifestV0,
    source_binding: EnterpriseSourceBindingV0,
    candidate: NativeObservedSourceCandidateV0,
    authorization: NativeHumanSourceAuthorizationV0,
    activation_receipt: NativeSourceActivationReceiptV0,
    registration: NativeSourceRegistrationV0,
    source_registry: NativeSourceRegistryV0,
) -> None:
    verified, reason = verify_company_model_snapshot_v0(dict(company))
    if not verified:
        raise ValueError(f"C2_COMPANY_MODEL_INVALID:{reason}")
    org = company["organization_id"]
    records = {n["record_id"]: n["kind"] for n in company["nodes"]}
    if (records.get(org) != "ORGANIZATION"
            or records.get(tool_instance_id) != "TOOL_INSTANCE"
            or records.get(source_id) != "SOURCE"
            or records.get(domain_id) != "DOMAIN_BINDING"):
        raise ValueError("C2_COMPANY_MODEL_REQUIRED_NODES_MISSING")
    relations = {
        (x["from_record_id"], x["to_record_id"], x["relation_kind"])
        for x in company["relations"]
    }
    if not {
        (org, tool_instance_id, "USES_TOOL"),
        (org, source_id, "HAS_SOURCE"),
        (org, domain_id, "BINDS_DOMAIN"),
    }.issubset(relations):
        raise ValueError("C2_COMPANY_MODEL_REQUIRED_RELATIONS_MISSING")
    ok, reason = verify_enterprise_stack_manifest_v0(manifest)
    if not ok:
        raise ValueError(f"C2_STACK_MANIFEST_INVALID:{reason}")
    if not isinstance(source_binding, EnterpriseSourceBindingV0):
        raise ValueError("C2_SOURCE_BINDING_TYPE_INVALID")
    if tool_instance_id != manifest.stack_id:
        raise ValueError("C2_TOOL_STACK_ID_MISMATCH")
    # Do not trust the fields or digest carried by the source binding alone.
    exact = build_enterprise_source_binding_v0(
        manifest=manifest, capability_id=source_binding.capability_id,
        source_identity_sha256=source_binding.source_identity_sha256,
        connector_reference=source_binding.connector_reference,
    )
    if exact != source_binding:
        raise ValueError("C2_SOURCE_BINDING_DRIFT_OR_FORGERY")
    if not isinstance(candidate, NativeObservedSourceCandidateV0):
        raise ValueError("C2_SOURCE_CANDIDATE_TYPE_INVALID")
    ok, reason = verify_native_observed_source_candidate_v0(candidate)
    if not ok:
        raise ValueError(f"C2_SOURCE_CANDIDATE_INVALID:{reason}")
    ok, reason = verify_native_human_source_authorization_v0(
        authorization, candidate=candidate
    )
    if not ok:
        raise ValueError(f"C2_SOURCE_AUTHORIZATION_INVALID:{reason}")
    ok, reason = verify_native_source_registration_v0(registration)
    if not ok:
        raise ValueError(f"C2_SOURCE_REGISTRATION_INVALID:{reason}")
    ok, reason = verify_native_source_activation_receipt_v0(
        activation_receipt, candidate=candidate, authorization=authorization,
        registration=registration,
    )
    if not ok or activation_receipt.active is not True:
        raise ValueError(f"C2_SOURCE_ACTIVATION_RECEIPT_INVALID:{reason}")
    if (registration.source_id != source_id
            or registration.provider != manifest.provider_id
            or registration.source_kind != source_binding.source_kind
            or registration.source_identity_sha256 != source_binding.source_identity_sha256
            or candidate.provider != manifest.provider_id
            or candidate.source_kind != source_binding.source_kind
            or candidate.source_identity_sha256 != source_binding.source_identity_sha256
            or candidate.connector_reference != source_binding.connector_reference
            or tuple(registration.capabilities) != tuple(source_binding.native_read_capabilities)
            or tuple(authorization.approved_capabilities) != tuple(registration.capabilities)
            or registration.authority_reference != f"native-onboarding:{authorization.authorization_hash}"
            or activation_receipt.registration_hash != registration.registration_hash):
        raise ValueError("C2_SOURCE_PROOF_BINDING_MISMATCH")
    # Live source revocation is checked every time, not only at registration.
    current = source_registry.load(source_id)
    if current is None or current.registration_hash != registration.registration_hash:
        raise ValueError("C2_NATIVE_SOURCE_NOT_CANONICAL")
    if not source_registry.is_active(source_id):
        raise ValueError("C2_NATIVE_SOURCE_REVOKED")


def build_company_stack_link_v0(
    *, company: Mapping[str, Any], domain_id: str, tool_instance_id: str,
    integration_slot_id: str, source_id: str, manifest: EnterpriseStackManifestV0,
    source_binding: EnterpriseSourceBindingV0,
    candidate: NativeObservedSourceCandidateV0,
    authorization: NativeHumanSourceAuthorizationV0,
    activation_receipt: NativeSourceActivationReceiptV0,
    registration: NativeSourceRegistrationV0,
    source_registry: NativeSourceRegistryV0,
    linked_at: str,
) -> CompanyStackLinkV0:
    if not isinstance(integration_slot_id, str) or not _SLOT_RE.fullmatch(integration_slot_id):
        raise ValueError("C2_INTEGRATION_SLOT_ID_INVALID")
    _check_existing_proofs(
        company=company, domain_id=domain_id,
        tool_instance_id=tool_instance_id, source_id=source_id,
        manifest=manifest, source_binding=source_binding, candidate=candidate,
        authorization=authorization, activation_receipt=activation_receipt,
        registration=registration, source_registry=source_registry,
    )
    require_time(linked_at)
    payload = {
        "schema": LINK_SCHEMA,
        "organization_id": company["organization_id"],
        "company_snapshot_hash": company["snapshot_hash"],
        "domain_id": domain_id,
        "tool_instance_id": tool_instance_id,
        "integration_slot_id": integration_slot_id,
        "source_id": source_id,
        "source_registration_hash": registration.registration_hash,
        "source_authorization_hash": authorization.authorization_hash,
        "source_activation_receipt_hash": activation_receipt.receipt_hash,
        "provider_id": manifest.provider_id,
        "stack_id": manifest.stack_id,
        "manifest_hash": manifest.manifest_hash,
        "source_capability_id": source_binding.capability_id,
        "source_binding_hash": source_binding.binding_hash,
        "linked_at": linked_at,
        "organization_authority_verified": False,
        "has_runtime_permission": False,
        "allows_provider_calls": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    payload["link_id"] = _ID_PREFIX + canonical_hash(payload)[:32]
    return CompanyStackLinkV0(**payload, link_hash=canonical_hash(payload))


def verify_company_stack_link_v0(
    link: CompanyStackLinkV0, *,
    company: Mapping[str, Any], manifest: EnterpriseStackManifestV0,
    source_binding: EnterpriseSourceBindingV0,
    candidate: NativeObservedSourceCandidateV0,
    authorization: NativeHumanSourceAuthorizationV0,
    activation_receipt: NativeSourceActivationReceiptV0,
    registration: NativeSourceRegistrationV0,
    source_registry: NativeSourceRegistryV0,
) -> tuple[bool, str | None]:
    if not isinstance(link, CompanyStackLinkV0) or link.schema != LINK_SCHEMA:
        return False, "C2_LINK_TYPE_OR_SCHEMA_INVALID"
    if not isinstance(link.integration_slot_id, str) or not _SLOT_RE.fullmatch(link.integration_slot_id):
        return False, "C2_INTEGRATION_SLOT_ID_INVALID"
    try:
        _check_existing_proofs(
            company=company, domain_id=link.domain_id,
            tool_instance_id=link.tool_instance_id, source_id=link.source_id,
            manifest=manifest, source_binding=source_binding,
            candidate=candidate, authorization=authorization,
            activation_receipt=activation_receipt, registration=registration,
            source_registry=source_registry,
        )
        require_time(link.linked_at)
        if (link.organization_id != company["organization_id"]
                or link.company_snapshot_hash != company["snapshot_hash"]
                or link.stack_id != manifest.stack_id
                or link.provider_id != manifest.provider_id
                or link.manifest_hash != manifest.manifest_hash
                or link.source_capability_id != source_binding.capability_id
                or link.source_binding_hash != source_binding.binding_hash
                or link.source_registration_hash != registration.registration_hash
                or link.source_authorization_hash != authorization.authorization_hash
                or link.source_activation_receipt_hash != activation_receipt.receipt_hash
                or link.decision_authority != DECISION_AUTHORITY
                or link.organization_authority_verified is not False
                or link.has_runtime_permission is not False
                or link.allows_provider_calls is not False
                or link.allowed_to_decide is not False
                or link.allowed_to_act is not False):
            return False, "C2_LINK_SCOPE_OR_AUTHORITY_MISMATCH"
        value = _link_payload(link)
        expected_id = value.pop("link_id")
        if expected_id != _ID_PREFIX + canonical_hash(value)[:32]:
            return False, "C2_LINK_ID_MISMATCH"
        value["link_id"] = expected_id
        if canonical_hash(value) != link.link_hash:
            return False, "C2_LINK_HASH_MISMATCH"
        return True, None
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return False, str(exc)


def build_company_stack_link_revocation_v0(
    link: CompanyStackLinkV0, *, revocation_id: str, reason_ref: str,
    revoked_by: str, revoked_at: str,
) -> CompanyStackLinkRevocationV0:
    if (not isinstance(link, CompanyStackLinkV0) or not revocation_id
            or not reason_ref or not revoked_by or revoked_by == "MACHINE"):
        raise ValueError("C2_REVOCATION_FIELDS_OR_HUMAN_REQUIRED")
    require_time(revoked_at)
    payload = {
        "schema": REVOCATION_SCHEMA,
        "revocation_id": revocation_id,
        "link_id": link.link_id,
        "organization_id": link.organization_id,
        "reason_ref": reason_ref,
        "revoked_by": revoked_by,
        "revoked_at": revoked_at,
        "is_execution_authority": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return CompanyStackLinkRevocationV0(
        **payload, revocation_hash=canonical_hash(payload)
    )


def verify_company_stack_link_revocation_v0(
    revocation: CompanyStackLinkRevocationV0, *,
    link: CompanyStackLinkV0,
) -> tuple[bool, str | None]:
    if not isinstance(revocation, CompanyStackLinkRevocationV0):
        return False, "C2_REVOCATION_TYPE_INVALID"
    data = asdict(revocation)
    digest = data.pop("revocation_hash")
    try:
        require_time(revocation.revoked_at)
    except ValueError:
        return False, "C2_REVOCATION_TIME_INVALID"
    if (revocation.schema != REVOCATION_SCHEMA or revocation.link_id != link.link_id
            or revocation.organization_id != link.organization_id
            or not revocation.revocation_id or not revocation.reason_ref
            or not revocation.revoked_by or revocation.revoked_by == "MACHINE"
            or revocation.decision_authority != DECISION_AUTHORITY
            or revocation.is_execution_authority is not False):
        return False, "C2_REVOCATION_SCOPE_OR_AUTHORITY_INVALID"
    if canonical_hash(data) != digest:
        return False, "C2_REVOCATION_HASH_MISMATCH"
    return True, None


class CompanyStackLifecycleV0:
    """Transient registry: visibility only, never an authorization gateway.

    Source ID permanently belongs to one explicitly linked organization within
    this in-memory instance. No automatic sharing or migration across tenants.
    A provider swap needs prior link revocation and new source onboarding.
    """
    def __init__(self) -> None:
        self._links: dict[str, CompanyStackLinkV0] = {}
        self._revocations: dict[str, CompanyStackLinkRevocationV0] = {}
        self._owners: dict[str, str] = {}
        self._slots: dict[tuple[str, str, str, str, str], str] = {}

    @staticmethod
    def _slot(link: CompanyStackLinkV0) -> tuple[str, str, str, str, str]:
        return (link.organization_id, link.tool_instance_id,
                link.domain_id, link.source_capability_id, link.integration_slot_id)

    def register(self, link: CompanyStackLinkV0, **proofs: Any) -> str:
        ok, reason = verify_company_stack_link_v0(link, **proofs)
        if not ok:
            raise ValueError(reason)
        old_owner = self._owners.get(link.source_id)
        if old_owner is not None and old_owner != link.organization_id:
            raise ValueError("C2_SOURCE_ALREADY_SCOPED_TO_OTHER_ORGANIZATION")
        previous = self._slots.get(self._slot(link))
        if previous is not None and previous != link.link_id:
            if previous not in self._revocations:
                raise ValueError("C2_ACTIVE_PROVIDER_BINDING_MUST_BE_REVOKED_FIRST")
        old = self._links.get(link.link_id)
        if old is not None and old != link:
            raise ValueError("C2_IMMUTABLE_LINK_CONFLICT")
        if link.link_id in self._revocations:
            raise ValueError("C2_REVOKED_LINK_CANNOT_REACTIVATE")
        self._links[link.link_id] = link
        self._owners[link.source_id] = link.organization_id
        self._slots[self._slot(link)] = link.link_id
        return link.link_id

    def revoke(self, revocation: CompanyStackLinkRevocationV0) -> str:
        link = self._links.get(revocation.link_id)
        if link is None:
            raise ValueError("C2_UNKNOWN_LINK")
        ok, reason = verify_company_stack_link_revocation_v0(
            revocation, link=link
        )
        if not ok:
            raise ValueError(reason)
        old = self._revocations.get(revocation.link_id)
        if old is not None and old != revocation:
            raise ValueError("C2_REVOCATION_IMMUTABLE_CONFLICT")
        self._revocations[revocation.link_id] = revocation
        return revocation.link_id

    def inspect(self, link_id: str, *, organization_id: str,
                **proofs: Any) -> dict[str, Any]:
        """Revalidates current registry/proofs; does NOT authorize reads."""
        link = self._links.get(link_id)
        if link is None or link.organization_id != organization_id:
            return {"status": REFUSED_STATUS, "reason": "C2_LINK_NOT_IN_ORGANIZATION"}
        if link_id in self._revocations:
            return {"status": REFUSED_STATUS, "reason": "C2_LINK_REVOKED"}
        if self._slots.get(self._slot(link)) != link_id:
            return {"status": REFUSED_STATUS, "reason": "C2_PROVIDER_SUPERSEDED"}
        ok, reason = verify_company_stack_link_v0(link, **proofs)
        if not ok:
            return {"status": REFUSED_STATUS, "reason": reason}
        return {
            "status": LINK_STATUS,
            "organization_id": link.organization_id,
            "link_id": link.link_id,
            "source_capability_id": link.source_capability_id,
            "source_registration_hash": link.source_registration_hash,
            "manifest_hash": link.manifest_hash,
            "organization_authority_verified": False,
            "runtime_permission_granted": False,
            "provider_call_allowed": False,
            "decision_authority": DECISION_AUTHORITY,
        }
