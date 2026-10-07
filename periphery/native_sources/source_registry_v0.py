"""Provider-neutral READONLY source registry V0."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from .common_v0 import (
    DECISION_AUTHORITY,
    SOURCE_KINDS,
    canonical_hash,
    filesystem_component_v0,
    require_time,
    validate_readonly_capabilities,
)

_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,180}$")


@dataclass(frozen=True)
class NativeSourceRegistrationV0:
    schema: str
    source_id: str
    source_kind: str
    provider: str
    source_identity_sha256: str
    capabilities: tuple[str, ...]
    authority_reference: str
    approved_by: str
    registered_at: str
    active: bool
    readonly: bool
    external_mutation_allowed: bool
    is_execution_authority: bool
    decision_authority: str
    registration_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = list(self.capabilities)
        return data


@dataclass(frozen=True)
class NativeSourceRevocationV0:
    schema: str
    revocation_id: str
    source_id: str
    registration_hash: str
    reason: str
    revoked_by: str
    revoked_at: str
    is_execution_authority: bool
    decision_authority: str
    revocation_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NativeSourceObservationV0:
    schema: str
    observation_id: str
    source_id: str
    source_kind: str
    provider: str
    registration_hash: str
    provider_item_id_sha256: str
    content_sha256: str
    metadata_sha256: str
    observed_at: str
    raw_provider_item_id_persisted: bool
    raw_content_persisted: bool
    raw_source_identity_persisted: bool
    allowed_to_decide: bool
    allowed_to_act: bool
    decision_authority: str
    observation_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _registration_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "source_id", "source_kind", "provider",
        "source_identity_sha256", "capabilities", "authority_reference",
        "approved_by", "registered_at", "active", "readonly",
        "external_mutation_allowed", "is_execution_authority",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_source_registration_v0(
    *,
    source_id: str,
    source_kind: str,
    provider: str,
    source_identity_sha256: str,
    capabilities: tuple[str, ...],
    authority_reference: str,
    approved_by: str,
    registered_at: str,
) -> NativeSourceRegistrationV0:
    if not _ID_RE.match(source_id):
        raise ValueError("NATIVE_SOURCE_ID_INVALID")
    if source_kind not in SOURCE_KINDS:
        raise ValueError("NATIVE_SOURCE_KIND_INVALID")
    if not provider or not authority_reference:
        raise ValueError("NATIVE_SOURCE_PROVIDER_AUTHORITY_REQUIRED")
    if approved_by == "MACHINE" or not approved_by:
        raise ValueError("NATIVE_SOURCE_HUMAN_APPROVER_REQUIRED")
    if len(source_identity_sha256) != 64:
        raise ValueError("NATIVE_SOURCE_IDENTITY_HASH_INVALID")
    require_time(registered_at)
    normalized = validate_readonly_capabilities(capabilities)

    payload = {
        "schema": "OBSIDIA_NATIVE_SOURCE_REGISTRATION_V0",
        "source_id": source_id,
        "source_kind": source_kind,
        "provider": provider,
        "source_identity_sha256": source_identity_sha256,
        "capabilities": list(normalized),
        "authority_reference": authority_reference,
        "approved_by": approved_by,
        "registered_at": registered_at,
        "active": True,
        "readonly": True,
        "external_mutation_allowed": False,
        "is_execution_authority": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeSourceRegistrationV0(
        schema=payload["schema"],
        source_id=source_id,
        source_kind=source_kind,
        provider=provider,
        source_identity_sha256=source_identity_sha256,
        capabilities=normalized,
        authority_reference=authority_reference,
        approved_by=approved_by,
        registered_at=registered_at,
        active=True,
        readonly=True,
        external_mutation_allowed=False,
        is_execution_authority=False,
        decision_authority=DECISION_AUTHORITY,
        registration_hash=canonical_hash(payload),
    )


def verify_native_source_registration_v0(
    registration: NativeSourceRegistrationV0 | Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if registration is None:
        return False, "NATIVE_SOURCE_REGISTRATION_MISSING"
    data = (
        registration.to_dict()
        if isinstance(registration, NativeSourceRegistrationV0)
        else dict(registration)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_REGISTRATION_V0":
        return False, "NATIVE_SOURCE_REGISTRATION_SCHEMA_INVALID"
    if data.get("source_kind") not in SOURCE_KINDS:
        return False, "NATIVE_SOURCE_KIND_INVALID"
    if not _ID_RE.match(str(data.get("source_id", ""))):
        return False, "NATIVE_SOURCE_ID_INVALID"
    if len(str(data.get("source_identity_sha256", ""))) != 64:
        return False, "NATIVE_SOURCE_IDENTITY_HASH_INVALID"
    if data.get("active") is not True:
        return False, "NATIVE_SOURCE_REGISTRATION_INACTIVE"
    if data.get("readonly") is not True:
        return False, "NATIVE_SOURCE_READONLY_REQUIRED"
    if data.get("external_mutation_allowed") is not False:
        return False, "NATIVE_SOURCE_EXTERNAL_MUTATION_FORBIDDEN"
    if data.get("is_execution_authority") is not False:
        return False, "NATIVE_SOURCE_EXECUTION_AUTHORITY_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_DECISION_AUTHORITY_INVALID"
    try:
        validate_readonly_capabilities(tuple(data.get("capabilities") or ()))
        require_time(str(data.get("registered_at")))
    except ValueError as exc:
        return False, str(exc)
    if canonical_hash(_registration_payload(data)) != data.get("registration_hash"):
        return False, "NATIVE_SOURCE_REGISTRATION_HASH_MISMATCH"
    return True, None


def _revocation_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "revocation_id", "source_id", "registration_hash",
        "reason", "revoked_by", "revoked_at", "is_execution_authority",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_source_revocation_v0(
    *,
    registration: NativeSourceRegistrationV0,
    revocation_id: str,
    reason: str,
    revoked_by: str,
    revoked_at: str,
) -> NativeSourceRevocationV0:
    ok, verify_reason = verify_native_source_registration_v0(registration)
    if not ok:
        raise ValueError(verify_reason)
    if not _ID_RE.match(revocation_id):
        raise ValueError("NATIVE_SOURCE_REVOCATION_ID_INVALID")
    if not reason.strip():
        raise ValueError("NATIVE_SOURCE_REVOCATION_REASON_REQUIRED")
    if revoked_by == "MACHINE" or not revoked_by:
        raise ValueError("NATIVE_SOURCE_REVOCATION_HUMAN_REQUIRED")
    require_time(revoked_at)

    payload = {
        "schema": "OBSIDIA_NATIVE_SOURCE_REVOCATION_V0",
        "revocation_id": revocation_id,
        "source_id": registration.source_id,
        "registration_hash": registration.registration_hash,
        "reason": reason,
        "revoked_by": revoked_by,
        "revoked_at": revoked_at,
        "is_execution_authority": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeSourceRevocationV0(
        **payload,
        revocation_hash=canonical_hash(payload),
    )


def verify_native_source_revocation_v0(
    revocation: NativeSourceRevocationV0 | Mapping[str, Any] | None,
    *,
    registration: NativeSourceRegistrationV0,
) -> tuple[bool, Optional[str]]:
    if revocation is None:
        return False, "NATIVE_SOURCE_REVOCATION_MISSING"
    data = (
        revocation.to_dict()
        if isinstance(revocation, NativeSourceRevocationV0)
        else dict(revocation)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_REVOCATION_V0":
        return False, "NATIVE_SOURCE_REVOCATION_SCHEMA_INVALID"
    if data.get("source_id") != registration.source_id:
        return False, "NATIVE_SOURCE_REVOCATION_SOURCE_MISMATCH"
    if data.get("registration_hash") != registration.registration_hash:
        return False, "NATIVE_SOURCE_REVOCATION_REGISTRATION_MISMATCH"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_REVOCATION_AUTHORITY_INVALID"
    if data.get("is_execution_authority") is not False:
        return False, "NATIVE_SOURCE_REVOCATION_EXECUTION_AUTHORITY_FORBIDDEN"
    if canonical_hash(_revocation_payload(data)) != data.get("revocation_hash"):
        return False, "NATIVE_SOURCE_REVOCATION_HASH_MISMATCH"
    return True, None


class NativeSourceRegistryV0:
    def __init__(self, root: Path):
        self.root = root

    def _registration_path(self, source_id: str) -> Path:
        if not _ID_RE.match(source_id):
            raise ValueError("NATIVE_SOURCE_ID_INVALID")
        return (
            self.root
            / "registrations"
            / f"{filesystem_component_v0(source_id)}.json"
        )

    def _revocation_dir(self, source_id: str) -> Path:
        if not _ID_RE.match(source_id):
            raise ValueError("NATIVE_SOURCE_ID_INVALID")
        return (
            self.root
            / "revocations"
            / filesystem_component_v0(source_id)
        )

    def register(
        self,
        registration: NativeSourceRegistrationV0,
    ) -> NativeSourceRegistrationV0:
        ok, reason = verify_native_source_registration_v0(registration)
        if not ok:
            raise ValueError(reason)
        path = self._registration_path(registration.source_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing != registration.to_dict():
                raise ValueError("NATIVE_SOURCE_IMMUTABLE_REGISTRATION_CONFLICT")
            return registration
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(
            json.dumps(registration.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp, path)
        return registration

    def load(self, source_id: str) -> Optional[NativeSourceRegistrationV0]:
        path = self._registration_path(source_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        registration = NativeSourceRegistrationV0(
            **{**data, "capabilities": tuple(data["capabilities"])}
        )
        ok, reason = verify_native_source_registration_v0(registration)
        if not ok:
            raise ValueError(f"NATIVE_SOURCE_REGISTRATION_CORRUPT:{reason}")
        return registration

    def revocations(self, source_id: str) -> list[NativeSourceRevocationV0]:
        registration = self.load(source_id)
        if registration is None:
            return []
        directory = self._revocation_dir(source_id)
        if not directory.exists():
            return []
        out: list[NativeSourceRevocationV0] = []
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            revocation = NativeSourceRevocationV0(**data)
            ok, reason = verify_native_source_revocation_v0(
                revocation,
                registration=registration,
            )
            if not ok:
                raise ValueError(f"NATIVE_SOURCE_REVOCATION_CORRUPT:{reason}")
            out.append(revocation)
        return out

    def is_active(self, source_id: str) -> bool:
        return self.load(source_id) is not None and not self.revocations(source_id)

    def revoke(
        self,
        revocation: NativeSourceRevocationV0,
    ) -> NativeSourceRevocationV0:
        registration = self.load(revocation.source_id)
        if registration is None:
            raise ValueError("NATIVE_SOURCE_NOT_FOUND")
        ok, reason = verify_native_source_revocation_v0(
            revocation,
            registration=registration,
        )
        if not ok:
            raise ValueError(reason)
        directory = self._revocation_dir(revocation.source_id)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{revocation.revocation_id}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing != revocation.to_dict():
                raise ValueError("NATIVE_SOURCE_REVOCATION_IMMUTABILITY_CONFLICT")
            return revocation
        path.write_text(
            json.dumps(revocation.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return revocation


def _observation_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "observation_id", "source_id", "source_kind",
        "provider", "registration_hash", "provider_item_id_sha256",
        "content_sha256", "metadata_sha256", "observed_at",
        "raw_provider_item_id_persisted", "raw_content_persisted",
        "raw_source_identity_persisted", "allowed_to_decide",
        "allowed_to_act", "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_source_observation_v0(
    *,
    registration: NativeSourceRegistrationV0,
    registry: NativeSourceRegistryV0,
    provider_item_id: str,
    content: str,
    metadata: Mapping[str, Any],
    observed_at: str,
) -> NativeSourceObservationV0:
    if not registry.is_active(registration.source_id):
        raise ValueError("NATIVE_SOURCE_REVOKED_OR_INACTIVE")
    loaded = registry.load(registration.source_id)
    if loaded is None or loaded.registration_hash != registration.registration_hash:
        raise ValueError("NATIVE_SOURCE_REGISTRATION_NOT_CANONICAL")
    if not provider_item_id:
        raise ValueError("NATIVE_SOURCE_PROVIDER_ITEM_ID_REQUIRED")
    require_time(observed_at)

    provider_item_hash = canonical_hash({"provider_item_id": provider_item_id})
    content_hash = canonical_hash({"content": content})
    metadata_hash = canonical_hash(dict(metadata))
    seed = {
        "source": registration.registration_hash,
        "provider_item": provider_item_hash,
    }
    payload = {
        "schema": "OBSIDIA_NATIVE_SOURCE_OBSERVATION_V0",
        "observation_id": f"sourceobs-{canonical_hash(seed)[:32]}",
        "source_id": registration.source_id,
        "source_kind": registration.source_kind,
        "provider": registration.provider,
        "registration_hash": registration.registration_hash,
        "provider_item_id_sha256": provider_item_hash,
        "content_sha256": content_hash,
        "metadata_sha256": metadata_hash,
        "observed_at": observed_at,
        "raw_provider_item_id_persisted": False,
        "raw_content_persisted": False,
        "raw_source_identity_persisted": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeSourceObservationV0(
        **payload,
        observation_hash=canonical_hash(payload),
    )


def verify_native_source_observation_v0(
    observation: NativeSourceObservationV0 | Mapping[str, Any],
    *,
    registration: NativeSourceRegistrationV0,
) -> tuple[bool, Optional[str]]:
    data = (
        observation.to_dict()
        if isinstance(observation, NativeSourceObservationV0)
        else dict(observation)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_OBSERVATION_V0":
        return False, "NATIVE_SOURCE_OBSERVATION_SCHEMA_INVALID"
    if data.get("source_id") != registration.source_id:
        return False, "NATIVE_SOURCE_OBSERVATION_SOURCE_MISMATCH"
    if data.get("source_kind") != registration.source_kind:
        return False, "NATIVE_SOURCE_OBSERVATION_KIND_MISMATCH"
    if data.get("provider") != registration.provider:
        return False, "NATIVE_SOURCE_OBSERVATION_PROVIDER_MISMATCH"
    if data.get("registration_hash") != registration.registration_hash:
        return False, "NATIVE_SOURCE_OBSERVATION_REGISTRATION_MISMATCH"
    if data.get("allowed_to_decide") is not False:
        return False, "NATIVE_SOURCE_OBSERVATION_DECISION_FORBIDDEN"
    if data.get("allowed_to_act") is not False:
        return False, "NATIVE_SOURCE_OBSERVATION_ACTION_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_SOURCE_OBSERVATION_AUTHORITY_INVALID"
    if any(
        (
            data.get("raw_provider_item_id_persisted"),
            data.get("raw_content_persisted"),
            data.get("raw_source_identity_persisted"),
        )
    ):
        return False, "NATIVE_SOURCE_OBSERVATION_PRIVACY_BOUNDARY_VIOLATED"
    if canonical_hash(_observation_payload(data)) != data.get("observation_hash"):
        return False, "NATIVE_SOURCE_OBSERVATION_HASH_MISMATCH"
    return True, None
