from __future__ import annotations

import hashlib

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from obsidure_builder_proposal_v1 import (
    AUTHORITY_NONE,
    EXECUTION_ALLOWED,
    PATCH_FORMAT_REAL_UNIFIED_DIFF_V1,
    ObsidureBuilderProposalV1,
    canonical_json,
)
from obsidure_proposal_manifest_v1 import (
    ObsidureProposalManifestV1,
    verify_proposal_manifest,
)
from obsidure_proposal_validation_v1 import (
    POLICY_SCHEMA_VERSION as VALIDATION_POLICY_SCHEMA_VERSION,
    ProposalValidationResultV1,
)


SCHEMA_VERSION = "OBSIDURE_GOVERNANCE_HANDOFF_V1"
HANDOFF_POLICY_SCHEMA_VERSION = "OBSIDURE_GOVERNANCE_HANDOFF_POLICY_V1"
HANDOFF_POLICY_VERSION = "R9_B4_POLICY_V1"
HANDOFF_ID_PREFIX = "obh-"
HANDOFF_ID_BITS = 256
REQUESTED_ACTION_KIND = "APPLY_PATCH"

MAX_TEXT = 4096
MAX_ITEMS = 64


class GovernanceHandoffError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_text(value: object, field_name: str, *, max_len: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise GovernanceHandoffError(f"{field_name}_NOT_STRING")
    text = value.strip()
    if not text:
        raise GovernanceHandoffError(f"{field_name}_REQUIRED")
    if len(text) > max_len:
        raise GovernanceHandoffError(f"{field_name}_TOO_LONG")
    return text


def _as_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[Any, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        raise GovernanceHandoffError(f"{field_name}_MUST_BE_SEQUENCE")
    try:
        result = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise GovernanceHandoffError(f"{field_name}_MUST_BE_SEQUENCE") from exc
    if len(result) > max_items:
        raise GovernanceHandoffError(f"{field_name}_TOO_LONG")
    return result


def _string_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[str, ...]:
    return tuple(_require_text(item, f"{field_name}_ITEM") for item in _as_tuple(values, field_name, max_items=max_items))


def _plain(value: Mapping[str, Any]) -> dict[str, Any]:
    return dict(__import__("json").loads(canonical_json(value)))


def _payload_hash(payload: Mapping[str, Any]) -> str:
    return _sha256_text(canonical_json(payload))


def _freeze(value: Mapping[str, Any]) -> Mapping[str, Any]:
    canonical_json(value)
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class GovernanceHandoffPolicy:
    policy_version: str = HANDOFF_POLICY_VERSION
    requested_action_kind: str = REQUESTED_ACTION_KIND
    require_valid_validation: bool = True
    preserve_unknowns: bool = True
    preserve_risk: bool = True
    require_real_unified_diff: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_version", _require_text(self.policy_version, "policy_version"))
        kind = _require_text(self.requested_action_kind, "requested_action_kind").upper()
        if kind != REQUESTED_ACTION_KIND:
            raise GovernanceHandoffError("REQUESTED_ACTION_KIND_UNSUPPORTED")
        object.__setattr__(self, "requested_action_kind", kind)
        for field_name in (
            "require_valid_validation",
            "preserve_unknowns",
            "preserve_risk",
            "require_real_unified_diff",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise GovernanceHandoffError(f"{field_name.upper()}_NOT_BOOL")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "handoff_policy_schema_version": HANDOFF_POLICY_SCHEMA_VERSION,
            "policy_version": self.policy_version,
            "requested_action_kind": self.requested_action_kind,
            "require_valid_validation": self.require_valid_validation,
            "preserve_unknowns": self.preserve_unknowns,
            "preserve_risk": self.preserve_risk,
            "require_real_unified_diff": self.require_real_unified_diff,
            "grants_authority": False,
        }

    @property
    def policy_id(self) -> str:
        return "obhp-" + _payload_hash(self.identity_payload())

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["handoff_policy_id"] = self.policy_id
        return _plain(payload)


@dataclass(frozen=True)
class ObsidureGovernanceHandoffV1:
    proposal: ObsidureBuilderProposalV1
    manifest: ObsidureProposalManifestV1
    validation: ProposalValidationResultV1
    handoff_policy: GovernanceHandoffPolicy = field(default_factory=GovernanceHandoffPolicy)
    source_metadata: Mapping[str, Any] = field(default_factory=dict)
    authority: str = AUTHORITY_NONE
    execution_allowed: bool = EXECUTION_ALLOWED

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, ObsidureBuilderProposalV1):
            raise GovernanceHandoffError("PROPOSAL_OBJECT_REQUIRED")
        if not isinstance(self.manifest, ObsidureProposalManifestV1):
            raise GovernanceHandoffError("MANIFEST_OBJECT_REQUIRED")
        if not isinstance(self.validation, ProposalValidationResultV1):
            raise GovernanceHandoffError("VALIDATION_OBJECT_REQUIRED")
        if not isinstance(self.handoff_policy, GovernanceHandoffPolicy):
            raise GovernanceHandoffError("HANDOFF_POLICY_OBJECT_REQUIRED")
        if self.authority != AUTHORITY_NONE:
            raise GovernanceHandoffError("HANDOFF_AUTHORITY_MUST_BE_NONE")
        if self.execution_allowed is not False:
            raise GovernanceHandoffError("HANDOFF_EXECUTION_ALLOWED_MUST_BE_FALSE")
        object.__setattr__(self, "source_metadata", _freeze(dict(self.source_metadata)))
        self._check_bound_objects()

    def _check_bound_objects(self) -> None:
        proposal_payload = self.proposal.to_dict()
        manifest_payload = self.manifest.to_dict()
        validation_payload = self.validation.to_dict()
        manifest_ok, manifest_reason = verify_proposal_manifest(self.manifest, self.proposal)
        if not manifest_ok:
            raise GovernanceHandoffError("MANIFEST_PROPOSAL_BINDING_FAILED:" + str(manifest_reason))
        if self.handoff_policy.require_valid_validation and validation_payload["validation_verdict"] != "VALID":
            raise GovernanceHandoffError("VALIDATION_VERDICT_NOT_VALID")
        if validation_payload["proposal_id"] != proposal_payload["proposal_id"]:
            raise GovernanceHandoffError("VALIDATION_PROPOSAL_ID_MISMATCH")
        if validation_payload["manifest_id"] != manifest_payload["manifest_id"]:
            raise GovernanceHandoffError("VALIDATION_MANIFEST_ID_MISMATCH")
        patch_ref = proposal_payload.get("candidate_patch_ref")
        if patch_ref is None:
            raise GovernanceHandoffError("PATCH_REF_REQUIRED")
        if self.handoff_policy.require_real_unified_diff and patch_ref.get("patch_format") != PATCH_FORMAT_REAL_UNIFIED_DIFF_V1:
            raise GovernanceHandoffError("PATCH_FORMAT_UNSUPPORTED")
        if not self.handoff_policy.preserve_unknowns and proposal_payload.get("unknowns"):
            raise GovernanceHandoffError("UNKNOWN_PRESERVATION_DISABLED")
        if not self.handoff_policy.preserve_risk and proposal_payload.get("risk_notes"):
            raise GovernanceHandoffError("RISK_PRESERVATION_DISABLED")

    def identity_payload(self) -> dict[str, Any]:
        proposal_payload = self.proposal.to_dict()
        manifest_payload = self.manifest.to_dict()
        validation_payload = self.validation.to_dict()
        patch_ref = proposal_payload["candidate_patch_ref"]
        return {
            "schema_version": SCHEMA_VERSION,
            "handoff_policy": self.handoff_policy.to_dict(),
            "requested_action_kind": self.handoff_policy.requested_action_kind,
            "proposal_id": proposal_payload["proposal_id"],
            "proposal_digest": proposal_payload["proposal_digest"],
            "manifest_id": manifest_payload["manifest_id"],
            "manifest_digest": manifest_payload["manifest_digest"],
            "validation_id": validation_payload["validation_id"],
            "validation_digest": validation_payload["validation_digest"],
            "validation_policy_id": validation_payload["policy_id"],
            "validation_policy_version": validation_payload["policy_version"],
            "validation_policy_schema_version": VALIDATION_POLICY_SCHEMA_VERSION,
            "validation_verdict": validation_payload["validation_verdict"],
            "repo_identity_ref": manifest_payload["repo_identity_ref"],
            "base_repo_ref": proposal_payload["base_repo_ref"],
            "base_commit_sha": proposal_payload["base_commit_sha"],
            "target_scope": list(proposal_payload["target_scope"]),
            "files_touched": list(proposal_payload["files_touched"]),
            "candidate_patch_ref": patch_ref,
            "requested_effects": [{
                "effect_kind": "PATCH_FILE_SET",
                "patch_format": patch_ref["patch_format"],
                "patch_sha256": patch_ref["sha256"],
                "files": list(proposal_payload["files_touched"]),
            }],
            "evidence_refs": list(validation_payload["evidence_refs"]),
            "risk_notes": list(proposal_payload["risk_notes"]),
            "unknowns": list(proposal_payload["unknowns"]),
            "limits": list(validation_payload["limits"]),
            "conflicts": list(validation_payload["conflicts"]),
            "source_metadata": self.source_metadata,
            "source_metadata_is_authority": False,
            "authority": self.authority,
            "execution_allowed": self.execution_allowed,
            "runtime_called": False,
            "governed_action_prepared": False,
            "execution_hash_created": False,
            "action_evidence_id": None,
            "stale_if_base_or_patch_or_validation_changes": True,
        }

    @property
    def handoff_digest(self) -> str:
        return _payload_hash(self.identity_payload())

    @property
    def handoff_id(self) -> str:
        return HANDOFF_ID_PREFIX + self.handoff_digest

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["handoff_digest"] = self.handoff_digest
        payload["handoff_id"] = self.handoff_id
        payload["handoff_id_bits"] = HANDOFF_ID_BITS
        return _plain(payload)


def build_governance_handoff(
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    validation: ProposalValidationResultV1,
    *,
    handoff_policy: GovernanceHandoffPolicy | None = None,
    source_metadata: Mapping[str, Any] | None = None,
) -> ObsidureGovernanceHandoffV1:
    return ObsidureGovernanceHandoffV1(
        proposal=proposal,
        manifest=manifest,
        validation=validation,
        handoff_policy=handoff_policy or GovernanceHandoffPolicy(),
        source_metadata=dict(source_metadata or {}),
    )


def verify_governance_handoff(
    handoff: ObsidureGovernanceHandoffV1 | Mapping[str, Any],
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    validation: ProposalValidationResultV1,
) -> tuple[bool, str | None]:
    try:
        payload = handoff.to_dict() if isinstance(handoff, ObsidureGovernanceHandoffV1) else dict(handoff)
        expected = build_governance_handoff(
            proposal,
            manifest,
            validation,
            source_metadata=payload.get("source_metadata") or {},
        ).to_dict()
        for field_name in (
            "schema_version",
            "handoff_policy",
            "requested_action_kind",
            "proposal_id",
            "proposal_digest",
            "manifest_id",
            "manifest_digest",
            "validation_id",
            "validation_digest",
            "validation_policy_id",
            "validation_policy_version",
            "validation_policy_schema_version",
            "validation_verdict",
            "repo_identity_ref",
            "base_repo_ref",
            "base_commit_sha",
            "target_scope",
            "files_touched",
            "candidate_patch_ref",
            "requested_effects",
            "evidence_refs",
            "risk_notes",
            "unknowns",
            "limits",
            "conflicts",
            "source_metadata",
            "source_metadata_is_authority",
            "authority",
            "execution_allowed",
            "runtime_called",
            "governed_action_prepared",
            "execution_hash_created",
            "action_evidence_id",
            "stale_if_base_or_patch_or_validation_changes",
        ):
            if payload.get(field_name) != expected.get(field_name):
                return False, f"{field_name.upper()}_MISMATCH"
        body = dict(payload)
        digest = body.pop("handoff_digest", None)
        handoff_id = body.pop("handoff_id", None)
        body.pop("handoff_id_bits", None)
        recalculated = _payload_hash(body)
        if digest != recalculated:
            return False, "HANDOFF_DIGEST_MISMATCH"
        if handoff_id != HANDOFF_ID_PREFIX + recalculated:
            return False, "HANDOFF_ID_MISMATCH"
        if payload.get("authority") != AUTHORITY_NONE:
            return False, "HANDOFF_AUTHORITY_NOT_NONE"
        if payload.get("execution_allowed") is not False:
            return False, "HANDOFF_EXECUTION_ALLOWED_NOT_FALSE"
        if payload.get("runtime_called") is not False:
            return False, "RUNTIME_CALLED_NOT_FALSE"
        if payload.get("governed_action_prepared") is not False:
            return False, "GOVERNED_ACTION_PREPARED_NOT_FALSE"
        if payload.get("action_evidence_id") is not None:
            return False, "ACTION_EVIDENCE_ID_PRESENT"
        return True, None
    except Exception as exc:
        return False, str(exc)
