from __future__ import annotations

"""
R9-B2 canonical Obsidure proposal manifest and provenance contract.

The manifest is a frozen proposal-evidence snapshot. It is not an execution
receipt and grants no authority.
"""

import dataclasses
import hashlib

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from obsidure_builder_proposal_v1 import (
    AUTHORITY_NONE,
    EXECUTION_ALLOWED,
    PATCH_FORMAT_REAL_UNIFIED_DIFF_V1,
    BuilderProposalError,
    ObsidureBuilderProposalV1,
    canonical_json,
)


SCHEMA_VERSION = "OBSIDURE_PROPOSAL_MANIFEST_V1"
MANIFEST_ID_PREFIX = "obm-"
EVIDENCE_ID_PREFIX = "obe-"
MANIFEST_ID_BITS = 256
EVIDENCE_ID_BITS = 256

EVIDENCE_STATUS_DECLARED = "DECLARED"
EVIDENCE_STATUS_OBSERVED = "OBSERVED"
EVIDENCE_STATUS_VERIFIED = "VERIFIED"
EVIDENCE_STATUS_NOT_PROVIDED = "NOT_PROVIDED"
EVIDENCE_STATUS_NOT_VERIFIED = "NOT_VERIFIED"
EVIDENCE_STATUS_MISSING = "MISSING"

EVIDENCE_STATUSES = frozenset((
    EVIDENCE_STATUS_DECLARED,
    EVIDENCE_STATUS_OBSERVED,
    EVIDENCE_STATUS_VERIFIED,
    EVIDENCE_STATUS_NOT_PROVIDED,
    EVIDENCE_STATUS_NOT_VERIFIED,
    EVIDENCE_STATUS_MISSING,
))

ARTIFACT_KINDS = frozenset((
    "CANDIDATE_PATCH",
    "CANDIDATE_SOURCE",
    "BUILD_MANIFEST",
    "TEST_PLAN",
    "TEST_RESULT",
    "LEAN_ARTIFACT",
    "PROVIDER_OUTPUT",
    "PROPOSAL_JSON",
    "RUNTIME_RECEIPT",
))

EVIDENCE_KINDS = frozenset((
    "PROVIDER_DECLARATION",
    "TEST_OBLIGATION",
    "TEST_RESULT_EVIDENCE",
    "PROOF_OBLIGATION",
    "LEAN_EVIDENCE",
    "PATCH_ARTIFACT_EVIDENCE",
    "MANIFEST_EVIDENCE",
    "RISK_NOTE",
))

MAX_TEXT = 4096
MAX_REF_TEXT = 512
MAX_ITEMS = 64
MAX_ARTIFACTS = 64
MAX_EVIDENCE = 64


class ProposalManifestError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_text(value: object, field_name: str, *, max_len: int = MAX_REF_TEXT) -> str:
    if not isinstance(value, str):
        raise ProposalManifestError(f"{field_name}_NOT_STRING")
    text = value.strip()
    if not text:
        raise ProposalManifestError(f"{field_name}_REQUIRED")
    if len(text) > max_len:
        raise ProposalManifestError(f"{field_name}_TOO_LONG")
    return text


def _sha256(value: object, field_name: str) -> str:
    text = _require_text(value, field_name)
    lowered = text.lower()
    if len(lowered) != 64 or any(c not in "0123456789abcdef" for c in lowered):
        raise ProposalManifestError(f"{field_name}_NOT_SHA256")
    return lowered


def _as_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[Any, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        raise ProposalManifestError(f"{field_name}_MUST_BE_SEQUENCE")
    try:
        result = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ProposalManifestError(f"{field_name}_MUST_BE_SEQUENCE") from exc
    if len(result) > max_items:
        raise ProposalManifestError(f"{field_name}_TOO_LONG")
    return result


def _string_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[str, ...]:
    out: list[str] = []
    for item in _as_tuple(values, field_name, max_items=max_items):
        out.append(_require_text(item, f"{field_name}_ITEM"))
    return tuple(out)


def _freeze(value: Mapping[str, Any]) -> Mapping[str, Any]:
    canonical_json(value)
    return MappingProxyType(dict(value))


def _payload_hash(payload: Mapping[str, Any]) -> str:
    return _sha256_text(canonical_json(payload))


@dataclass(frozen=True)
class ArtifactRef:
    artifact_kind: str
    logical_ref: str
    content_sha256: str
    size_bytes: int | None = None
    artifact_format: str = ""
    schema_ref: str = ""

    def __post_init__(self) -> None:
        kind = _require_text(self.artifact_kind, "artifact_kind").upper()
        if kind not in ARTIFACT_KINDS:
            raise ProposalManifestError("ARTIFACT_KIND_UNSUPPORTED")
        object.__setattr__(self, "artifact_kind", kind)
        object.__setattr__(self, "logical_ref", _require_text(self.logical_ref, "logical_ref"))
        object.__setattr__(self, "content_sha256", _sha256(self.content_sha256, "content_sha256"))
        if self.size_bytes is not None:
            if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
                raise ProposalManifestError("SIZE_BYTES_INVALID")
        object.__setattr__(self, "artifact_format", str(self.artifact_format or "").strip())
        object.__setattr__(self, "schema_ref", str(self.schema_ref or "").strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_kind": self.artifact_kind,
            "logical_ref": self.logical_ref,
            "content_sha256": self.content_sha256,
            "size_bytes": self.size_bytes,
            "artifact_format": self.artifact_format,
            "schema_ref": self.schema_ref,
        }


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_kind: str
    subject_ref: str
    producer_ref: str
    verification_status: str
    artifact_ref: ArtifactRef | None = None
    scope: tuple[str, ...] = ()
    result: str = ""
    provenance: Mapping[str, Any] = field(default_factory=dict)
    authority: str = AUTHORITY_NONE

    def __post_init__(self) -> None:
        kind = _require_text(self.evidence_kind, "evidence_kind").upper()
        if kind not in EVIDENCE_KINDS:
            raise ProposalManifestError("EVIDENCE_KIND_UNSUPPORTED")
        status = _require_text(self.verification_status, "verification_status").upper()
        if status not in EVIDENCE_STATUSES:
            raise ProposalManifestError("EVIDENCE_STATUS_UNSUPPORTED")
        object.__setattr__(self, "evidence_kind", kind)
        object.__setattr__(self, "verification_status", status)
        object.__setattr__(self, "subject_ref", _require_text(self.subject_ref, "subject_ref"))
        object.__setattr__(self, "producer_ref", _require_text(self.producer_ref, "producer_ref"))
        object.__setattr__(self, "scope", _string_tuple(self.scope, "scope"))
        object.__setattr__(self, "result", str(self.result or "").strip()[:MAX_TEXT])
        object.__setattr__(self, "provenance", _freeze(dict(self.provenance)))
        if self.authority != AUTHORITY_NONE:
            raise ProposalManifestError("EVIDENCE_AUTHORITY_MUST_BE_NONE")
        if status in (EVIDENCE_STATUS_OBSERVED, EVIDENCE_STATUS_VERIFIED) and self.artifact_ref is None:
            raise ProposalManifestError("BOUND_ARTIFACT_REQUIRED_FOR_EVIDENCE")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "evidence_kind": self.evidence_kind,
            "subject_ref": self.subject_ref,
            "artifact_ref": self.artifact_ref.to_dict() if self.artifact_ref else None,
            "producer_ref": self.producer_ref,
            "verification_status": self.verification_status,
            "scope": list(self.scope),
            "result": self.result,
            "provenance": self.provenance,
            "authority": self.authority,
        }

    @property
    def evidence_digest(self) -> str:
        return _payload_hash(self.identity_payload())

    @property
    def evidence_id(self) -> str:
        return EVIDENCE_ID_PREFIX + self.evidence_digest

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["evidence_digest"] = self.evidence_digest
        payload["evidence_id"] = self.evidence_id
        payload["evidence_id_bits"] = EVIDENCE_ID_BITS
        return _plain_payload(payload)


@dataclass(frozen=True)
class ProposalProvenance:
    builder_ref: str
    provider_ref: str
    source_context_refs: tuple[str, ...] = ()
    input_artifact_refs: tuple[str, ...] = ()
    created_from: str = "UNSPECIFIED_SOURCE"

    def __post_init__(self) -> None:
        object.__setattr__(self, "builder_ref", _require_text(self.builder_ref, "builder_ref"))
        object.__setattr__(self, "provider_ref", _require_text(self.provider_ref, "provider_ref"))
        object.__setattr__(self, "source_context_refs", _string_tuple(self.source_context_refs, "source_context_refs"))
        object.__setattr__(self, "input_artifact_refs", _string_tuple(self.input_artifact_refs, "input_artifact_refs"))
        object.__setattr__(self, "created_from", _require_text(self.created_from, "created_from"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "builder_ref": self.builder_ref,
            "provider_ref": self.provider_ref,
            "source_context_refs": list(self.source_context_refs),
            "input_artifact_refs": list(self.input_artifact_refs),
            "created_from": self.created_from,
        }


@dataclass(frozen=True)
class ObsidureProposalManifestV1:
    proposal: ObsidureBuilderProposalV1
    candidate_artifacts: tuple[ArtifactRef, ...] = ()
    evidence_records: tuple[EvidenceRecord, ...] = ()
    verification_obligations: tuple[str, ...] = ()
    repo_identity_ref: str = "UNSPECIFIED_REPO"
    authority: str = AUTHORITY_NONE
    execution_allowed: bool = EXECUTION_ALLOWED

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, ObsidureBuilderProposalV1):
            raise ProposalManifestError("PROPOSAL_OBJECT_REQUIRED")
        artifacts = _as_tuple(self.candidate_artifacts, "candidate_artifacts", max_items=MAX_ARTIFACTS)
        if not all(isinstance(item, ArtifactRef) for item in artifacts):
            raise ProposalManifestError("CANDIDATE_ARTIFACT_NOT_REF")
        evidence = _as_tuple(self.evidence_records, "evidence_records", max_items=MAX_EVIDENCE)
        if not all(isinstance(item, EvidenceRecord) for item in evidence):
            raise ProposalManifestError("EVIDENCE_RECORD_NOT_TYPED")
        object.__setattr__(self, "candidate_artifacts", tuple(artifacts))
        object.__setattr__(self, "evidence_records", tuple(evidence))
        object.__setattr__(self, "verification_obligations", _string_tuple(self.verification_obligations, "verification_obligations"))
        object.__setattr__(self, "repo_identity_ref", _require_text(self.repo_identity_ref, "repo_identity_ref"))
        if self.authority != AUTHORITY_NONE:
            raise ProposalManifestError("MANIFEST_AUTHORITY_MUST_BE_NONE")
        if self.execution_allowed is not False:
            raise ProposalManifestError("MANIFEST_EXECUTION_ALLOWED_MUST_BE_FALSE")
        self._check_consistency()

    @property
    def provenance(self) -> ProposalProvenance:
        return ProposalProvenance(
            builder_ref=self.proposal.builder_ref,
            provider_ref=self.proposal.provider_ref,
            source_context_refs=self.proposal.source_context_refs,
            input_artifact_refs=self.proposal.input_artifact_refs,
            created_from=self.proposal.created_from,
        )

    def _check_consistency(self) -> None:
        proposal_payload = self.proposal.to_dict()
        proposal_id = proposal_payload["proposal_id"]
        files = set(proposal_payload["files_touched"])
        for artifact in self.candidate_artifacts:
            if artifact.artifact_kind == "CANDIDATE_PATCH":
                patch_ref = proposal_payload.get("candidate_patch_ref")
                if not patch_ref:
                    raise ProposalManifestError("PATCH_ARTIFACT_WITHOUT_PROPOSAL_PATCH")
                if artifact.content_sha256 != patch_ref.get("sha256"):
                    raise ProposalManifestError("PATCH_HASH_MISMATCH")
                if artifact.artifact_format != PATCH_FORMAT_REAL_UNIFIED_DIFF_V1:
                    raise ProposalManifestError("PATCH_FORMAT_MISMATCH")
        for evidence in self.evidence_records:
            if evidence.subject_ref != proposal_id:
                raise ProposalManifestError("EVIDENCE_SUBJECT_MISMATCH")
            if evidence.scope and not set(evidence.scope).issubset(files):
                raise ProposalManifestError("EVIDENCE_SCOPE_OUTSIDE_PROPOSAL")

    def identity_payload(self) -> dict[str, Any]:
        proposal_payload = self.proposal.to_dict()
        return {
            "schema_version": SCHEMA_VERSION,
            "proposal_id": proposal_payload["proposal_id"],
            "proposal_digest": proposal_payload["proposal_digest"],
            "base_repo_ref": proposal_payload["base_repo_ref"],
            "base_commit_sha": proposal_payload["base_commit_sha"],
            "repo_identity_ref": self.repo_identity_ref,
            "target_scope": proposal_payload["target_scope"],
            "files_touched": proposal_payload["files_touched"],
            "builder_ref": proposal_payload["builder_ref"],
            "provider_ref": proposal_payload["provider_ref"],
            "provenance": self.provenance.to_dict(),
            "candidate_artifacts": [a.to_dict() for a in self.candidate_artifacts],
            "evidence_records": [e.to_dict() for e in self.evidence_records],
            "verification_obligations": list(self.verification_obligations),
            "created_from": proposal_payload["created_from"],
            "authority": self.authority,
            "execution_allowed": self.execution_allowed,
            "proposal_identity_differs_from_action_evidence_id": True,
            "r8_action_evidence_id": None,
            "provider_declaration_can_verify_evidence": False,
        }

    @property
    def manifest_digest(self) -> str:
        return _payload_hash(self.identity_payload())

    @property
    def manifest_id(self) -> str:
        return MANIFEST_ID_PREFIX + self.manifest_digest

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["manifest_digest"] = self.manifest_digest
        payload["manifest_id"] = self.manifest_id
        payload["manifest_id_bits"] = MANIFEST_ID_BITS
        return _plain_payload(payload)


def _plain_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return dict(__import__("json").loads(canonical_json(payload)))


def build_proposal_manifest(
    proposal: ObsidureBuilderProposalV1,
    *,
    candidate_artifacts: tuple[ArtifactRef, ...] = (),
    evidence_records: tuple[EvidenceRecord, ...] = (),
    verification_obligations: tuple[str, ...] = (),
    repo_identity_ref: str = "UNSPECIFIED_REPO",
) -> ObsidureProposalManifestV1:
    return ObsidureProposalManifestV1(
        proposal=proposal,
        candidate_artifacts=candidate_artifacts,
        evidence_records=evidence_records,
        verification_obligations=verification_obligations,
        repo_identity_ref=repo_identity_ref,
    )


def verify_proposal_manifest(
    manifest: ObsidureProposalManifestV1 | Mapping[str, Any],
    proposal: ObsidureBuilderProposalV1,
) -> tuple[bool, str | None]:
    try:
        payload = manifest.to_dict() if isinstance(manifest, ObsidureProposalManifestV1) else dict(manifest)
        proposal_payload = proposal.to_dict()
        if payload.get("proposal_id") != proposal_payload["proposal_id"]:
            return False, "PROPOSAL_ID_MISMATCH"
        if payload.get("proposal_digest") != proposal_payload["proposal_digest"]:
            return False, "PROPOSAL_DIGEST_MISMATCH"
        if payload.get("base_commit_sha") != proposal_payload["base_commit_sha"]:
            return False, "BASE_COMMIT_MISMATCH"
        if tuple(payload.get("target_scope") or ()) != tuple(proposal_payload["target_scope"]):
            return False, "TARGET_SCOPE_MISMATCH"
        patch_ref = proposal_payload.get("candidate_patch_ref")
        for artifact in payload.get("candidate_artifacts") or ():
            if artifact.get("artifact_kind") == "CANDIDATE_PATCH":
                if not patch_ref or artifact.get("content_sha256") != patch_ref.get("sha256"):
                    return False, "PATCH_HASH_MISMATCH"
        for evidence in payload.get("evidence_records") or ():
            if evidence.get("subject_ref") != proposal_payload["proposal_id"]:
                return False, "EVIDENCE_SUBJECT_MISMATCH"
        body = dict(payload)
        digest = body.pop("manifest_digest", None)
        manifest_id = body.pop("manifest_id", None)
        body.pop("manifest_id_bits", None)
        expected = _payload_hash(body)
        if digest != expected:
            return False, "MANIFEST_DIGEST_MISMATCH"
        if manifest_id != MANIFEST_ID_PREFIX + expected:
            return False, "MANIFEST_ID_MISMATCH"
        if payload.get("authority") != AUTHORITY_NONE:
            return False, "MANIFEST_AUTHORITY_NOT_NONE"
        if payload.get("execution_allowed") is not False:
            return False, "MANIFEST_EXECUTION_ALLOWED_NOT_FALSE"
        return True, None
    except (BuilderProposalError, ProposalManifestError) as exc:
        return False, str(exc)


def evidence_from_provider_declaration(
    *,
    proposal: ObsidureBuilderProposalV1,
    producer_ref: str,
    claims: Mapping[str, Any],
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_kind="PROVIDER_DECLARATION",
        subject_ref=proposal.proposal_id,
        producer_ref=producer_ref,
        verification_status=EVIDENCE_STATUS_DECLARED,
        provenance={"declared_claims": dict(claims)},
    )


def evidence_from_test_result_artifact(
    *,
    proposal: ObsidureBuilderProposalV1,
    artifact_ref: ArtifactRef,
    producer_ref: str,
    scope: tuple[str, ...] = (),
    result: str = "RESULT_BOUND",
    verified: bool = False,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=proposal.proposal_id,
        artifact_ref=artifact_ref,
        producer_ref=producer_ref,
        verification_status=EVIDENCE_STATUS_VERIFIED if verified else EVIDENCE_STATUS_OBSERVED,
        scope=scope,
        result=result,
    )


def from_candidate_manifest(
    candidate_manifest: Mapping[str, Any],
    proposal: ObsidureBuilderProposalV1,
    *,
    repo_identity_ref: str = "UNSPECIFIED_REPO",
) -> ObsidureProposalManifestV1:
    patch_ref = proposal.candidate_patch_ref
    if patch_ref is None:
        raise ProposalManifestError("PROPOSAL_PATCH_REF_REQUIRED")
    patch_artifact = ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref=str(candidate_manifest.get("candidate_patch") or patch_ref.artifact_ref),
        content_sha256=str(candidate_manifest.get("candidate_patch_sha256") or ""),
        artifact_format=str(candidate_manifest.get("candidate_patch_mode") or PATCH_FORMAT_REAL_UNIFIED_DIFF_V1),
        schema_ref=PATCH_FORMAT_REAL_UNIFIED_DIFF_V1,
    )
    manifest_artifact = ArtifactRef(
        artifact_kind="BUILD_MANIFEST",
        logical_ref=str(candidate_manifest.get("manifest") or "candidate_manifest.json"),
        content_sha256=str(candidate_manifest.get("manifest_sha256") or proposal.proposal_digest),
        artifact_format="JSON",
        schema_ref="OBSIDURE_CANDIDATE_MANIFEST",
    )
    declared = evidence_from_provider_declaration(
        proposal=proposal,
        producer_ref=str(candidate_manifest.get("producer") or proposal.provider_ref),
        claims={
            "producer_authority": candidate_manifest.get("producer_authority"),
            "decision_authority": candidate_manifest.get("decision_authority"),
            "auto_apply": candidate_manifest.get("auto_apply"),
            "auto_commit": candidate_manifest.get("auto_commit"),
            "auto_push": candidate_manifest.get("auto_push"),
            "auto_merge": candidate_manifest.get("auto_merge"),
            "world_action": candidate_manifest.get("world_action"),
        },
    )
    return build_proposal_manifest(
        proposal,
        candidate_artifacts=(patch_artifact, manifest_artifact),
        evidence_records=(declared,),
        verification_obligations=tuple(proposal.tests_proposed + proposal.proof_obligations),
        repo_identity_ref=repo_identity_ref,
    )


PARALLEL_OBSIDURE_RECEIPTS_CLASSIFICATION = {
    "candidate_manifest": "KEEP_AS_PROPOSAL_EVIDENCE",
    "proposal_receipt_md": "KEEP_AS_PROPOSAL_EVIDENCE",
    "bounded_apply_receipt": "ADAPT",
    "provider_runtime_receipt": "ADAPT",
    "r8_action_receipt": "SUPERSEDE_AS_CANONICAL_EXECUTION_PROOF",
}
