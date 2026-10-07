from __future__ import annotations

"""
R9-B3 canonical Obsidure proposal validation gate.

Validation checks frozen proposal, manifest, evidence, and obligation
consistency only. It grants no action authority.
"""

import dataclasses
import hashlib

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from obsidure_builder_proposal_v1 import (
    AUTHORITY_NONE,
    EXECUTION_ALLOWED,
    BuilderProposalError,
    ObsidureBuilderProposalV1,
    canonical_json,
)
from obsidure_proposal_manifest_v1 import (
    EVIDENCE_STATUS_DECLARED,
    EVIDENCE_STATUS_OBSERVED,
    EVIDENCE_STATUS_VERIFIED,
    EvidenceRecord,
    ObsidureProposalManifestV1,
    ProposalManifestError,
    verify_proposal_manifest,
)


SCHEMA_VERSION = "OBSIDURE_PROPOSAL_VALIDATION_RESULT_V1"
POLICY_SCHEMA_VERSION = "OBSIDURE_PROPOSAL_VALIDATION_POLICY_V1"
VALIDATION_ID_PREFIX = "obv-"
OBLIGATION_ID_PREFIX = "obo-"
VALIDATION_ID_BITS = 256
OBLIGATION_ID_BITS = 256
VALIDATION_POLICY_VERSION = "R9_B3_POLICY_V1"

VALIDATION_VERDICTS = frozenset((
    "VALID",
    "INVALID",
    "INCOMPLETE",
    "CONFLICTING",
    "HELD",
))

OBLIGATION_KINDS = frozenset((
    "UNIT_TEST",
    "INTEGRATION_TEST",
    "STATIC_CHECK",
    "BUILD_CHECK",
    "LEAN_PROOF",
    "DIFF_REVIEW",
    "REPLAY_CHECK",
    "CUSTOM_TYPED",
))

COMPATIBLE_EVIDENCE = {
    "UNIT_TEST": frozenset(("TEST_RESULT_EVIDENCE",)),
    "INTEGRATION_TEST": frozenset(("TEST_RESULT_EVIDENCE",)),
    "STATIC_CHECK": frozenset(("TEST_RESULT_EVIDENCE", "MANIFEST_EVIDENCE")),
    "BUILD_CHECK": frozenset(("TEST_RESULT_EVIDENCE", "MANIFEST_EVIDENCE")),
    "LEAN_PROOF": frozenset(("LEAN_EVIDENCE",)),
    "DIFF_REVIEW": frozenset(("PATCH_ARTIFACT_EVIDENCE", "MANIFEST_EVIDENCE")),
    "REPLAY_CHECK": frozenset(("MANIFEST_EVIDENCE",)),
    "CUSTOM_TYPED": frozenset(("MANIFEST_EVIDENCE",)),
}

MAX_TEXT = 4096
MAX_ITEMS = 64


class ProposalValidationError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_text(value: object, field_name: str, *, max_len: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise ProposalValidationError(f"{field_name}_NOT_STRING")
    text = value.strip()
    if not text:
        raise ProposalValidationError(f"{field_name}_REQUIRED")
    if len(text) > max_len:
        raise ProposalValidationError(f"{field_name}_TOO_LONG")
    return text


def _as_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[Any, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        raise ProposalValidationError(f"{field_name}_MUST_BE_SEQUENCE")
    try:
        result = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ProposalValidationError(f"{field_name}_MUST_BE_SEQUENCE") from exc
    if len(result) > max_items:
        raise ProposalValidationError(f"{field_name}_TOO_LONG")
    return result


def _string_tuple(values: object, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[str, ...]:
    return tuple(_require_text(item, f"{field_name}_ITEM") for item in _as_tuple(values, field_name, max_items=max_items))


def _freeze(value: Mapping[str, Any]) -> Mapping[str, Any]:
    canonical_json(value)
    return MappingProxyType(dict(value))


def _payload_hash(payload: Mapping[str, Any]) -> str:
    return _sha256_text(canonical_json(payload))


def _plain(payload: Mapping[str, Any]) -> dict[str, Any]:
    return dict(__import__("json").loads(canonical_json(payload)))


@dataclass(frozen=True)
class ValidationObligation:
    obligation_kind: str
    target: str
    scope: tuple[str, ...] = ()
    required: bool = True
    expected_evidence_kind: str = ""
    allow_observed: bool = False
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        kind = _require_text(self.obligation_kind, "obligation_kind").upper()
        if kind not in OBLIGATION_KINDS:
            raise ProposalValidationError("OBLIGATION_KIND_UNSUPPORTED")
        object.__setattr__(self, "obligation_kind", kind)
        object.__setattr__(self, "target", _require_text(self.target, "target"))
        object.__setattr__(self, "scope", _string_tuple(self.scope, "scope"))
        if not isinstance(self.required, bool):
            raise ProposalValidationError("REQUIRED_NOT_BOOL")
        expected = str(self.expected_evidence_kind or "").strip().upper()
        if not expected:
            kinds = sorted(COMPATIBLE_EVIDENCE[kind])
            expected = kinds[0]
        if expected not in COMPATIBLE_EVIDENCE[kind]:
            raise ProposalValidationError("EXPECTED_EVIDENCE_KIND_INCOMPATIBLE")
        object.__setattr__(self, "expected_evidence_kind", expected)
        if not isinstance(self.allow_observed, bool):
            raise ProposalValidationError("ALLOW_OBSERVED_NOT_BOOL")
        object.__setattr__(self, "parameters", _freeze(dict(self.parameters)))

    def identity_payload(self, proposal_id: str) -> dict[str, Any]:
        return {
            "proposal_id": proposal_id,
            "obligation_kind": self.obligation_kind,
            "target": self.target,
            "scope": list(self.scope),
            "required": self.required,
            "expected_evidence_kind": self.expected_evidence_kind,
            "allow_observed": self.allow_observed,
            "parameters": self.parameters,
        }

    def obligation_id(self, proposal_id: str) -> str:
        return OBLIGATION_ID_PREFIX + _payload_hash(self.identity_payload(proposal_id))

    def to_dict(self, proposal_id: str) -> dict[str, Any]:
        payload = self.identity_payload(proposal_id)
        payload["obligation_id"] = self.obligation_id(proposal_id)
        payload["obligation_id_bits"] = OBLIGATION_ID_BITS
        return _plain(payload)


@dataclass(frozen=True)
class ValidationPolicy:
    policy_version: str = VALIDATION_POLICY_VERSION
    obligations: tuple[ValidationObligation, ...] = ()
    require_patch_artifact: bool = True
    require_no_unknowns: bool = False
    require_risk_notes: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_version", _require_text(self.policy_version, "policy_version"))
        obligations = _as_tuple(self.obligations, "obligations")
        if not all(isinstance(item, ValidationObligation) for item in obligations):
            raise ProposalValidationError("OBLIGATION_NOT_TYPED")
        object.__setattr__(self, "obligations", tuple(obligations))
        for field_name in ("require_patch_artifact", "require_no_unknowns", "require_risk_notes"):
            if not isinstance(getattr(self, field_name), bool):
                raise ProposalValidationError(f"{field_name.upper()}_NOT_BOOL")

    def identity_payload(self, proposal_id: str) -> dict[str, Any]:
        return {
            "policy_schema_version": POLICY_SCHEMA_VERSION,
            "policy_version": self.policy_version,
            "obligations": [item.to_dict(proposal_id) for item in self.obligations],
            "require_patch_artifact": self.require_patch_artifact,
            "require_no_unknowns": self.require_no_unknowns,
            "require_risk_notes": self.require_risk_notes,
        }

    def policy_id(self, proposal_id: str) -> str:
        return "obvp-" + _payload_hash(self.identity_payload(proposal_id))


@dataclass(frozen=True)
class ProposalValidationResultV1:
    proposal_id: str
    manifest_id: str
    policy_id: str
    policy_version: str
    structural_status: str
    evidence_status: str
    obligation_status: str
    risk_status: str
    unknown_status: str
    satisfied_obligations: tuple[str, ...] = ()
    missing_obligations: tuple[str, ...] = ()
    failed_obligations: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    limits: tuple[str, ...] = ()
    validation_verdict: str = "INCOMPLETE"
    authority: str = AUTHORITY_NONE
    execution_allowed: bool = EXECUTION_ALLOWED

    def __post_init__(self) -> None:
        for field_name in (
            "proposal_id",
            "manifest_id",
            "policy_id",
            "policy_version",
            "structural_status",
            "evidence_status",
            "obligation_status",
            "risk_status",
            "unknown_status",
        ):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))
        verdict = _require_text(self.validation_verdict, "validation_verdict").upper()
        if verdict not in VALIDATION_VERDICTS:
            raise ProposalValidationError("VALIDATION_VERDICT_UNSUPPORTED")
        object.__setattr__(self, "validation_verdict", verdict)
        for field_name in ("satisfied_obligations", "missing_obligations", "failed_obligations", "evidence_refs", "conflicts", "limits"):
            object.__setattr__(self, field_name, _string_tuple(getattr(self, field_name), field_name))
        if self.authority != AUTHORITY_NONE:
            raise ProposalValidationError("VALIDATION_AUTHORITY_MUST_BE_NONE")
        if self.execution_allowed is not False:
            raise ProposalValidationError("VALIDATION_EXECUTION_ALLOWED_MUST_BE_FALSE")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "proposal_id": self.proposal_id,
            "manifest_id": self.manifest_id,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "structural_status": self.structural_status,
            "evidence_status": self.evidence_status,
            "obligation_status": self.obligation_status,
            "risk_status": self.risk_status,
            "unknown_status": self.unknown_status,
            "satisfied_obligations": list(self.satisfied_obligations),
            "missing_obligations": list(self.missing_obligations),
            "failed_obligations": list(self.failed_obligations),
            "evidence_refs": list(self.evidence_refs),
            "conflicts": list(self.conflicts),
            "limits": list(self.limits),
            "validation_verdict": self.validation_verdict,
            "authority": self.authority,
            "execution_allowed": self.execution_allowed,
            "validation_id_differs_from_action_evidence_id": True,
        }

    @property
    def validation_digest(self) -> str:
        return _payload_hash(self.identity_payload())

    @property
    def validation_id(self) -> str:
        return VALIDATION_ID_PREFIX + self.validation_digest

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["validation_digest"] = self.validation_digest
        payload["validation_id"] = self.validation_id
        payload["validation_id_bits"] = VALIDATION_ID_BITS
        return _plain(payload)


def _status_rank(status: str) -> int:
    return {EVIDENCE_STATUS_DECLARED: 0, EVIDENCE_STATUS_OBSERVED: 1, EVIDENCE_STATUS_VERIFIED: 2}.get(status, -1)


def _evidence_satisfies(
    evidence: EvidenceRecord,
    obligation: ValidationObligation,
    proposal: ObsidureBuilderProposalV1,
) -> tuple[bool, str | None]:
    proposal_payload = proposal.to_dict()
    if evidence.subject_ref != proposal_payload["proposal_id"]:
        return False, "EVIDENCE_SUBJECT_MISMATCH"
    if evidence.verification_status == EVIDENCE_STATUS_DECLARED:
        return False, "DECLARED_EVIDENCE_INSUFFICIENT"
    if evidence.evidence_kind != obligation.expected_evidence_kind:
        return False, "EVIDENCE_KIND_INCOMPATIBLE"
    if evidence.verification_status == EVIDENCE_STATUS_OBSERVED and not obligation.allow_observed:
        return False, "OBSERVED_EVIDENCE_NOT_ALLOWED"
    if obligation.scope and evidence.scope and not set(obligation.scope).issubset(set(evidence.scope)):
        return False, "EVIDENCE_SCOPE_MISMATCH"
    base = evidence.provenance.get("base_commit_sha") if isinstance(evidence.provenance, Mapping) else None
    if base and base != proposal_payload["base_commit_sha"]:
        return False, "EVIDENCE_BASE_COMMIT_MISMATCH"
    return True, None


def _dedupe_evidence(evidence: tuple[EvidenceRecord, ...]) -> tuple[EvidenceRecord, ...]:
    by_id: dict[str, EvidenceRecord] = {}
    for item in evidence:
        previous = by_id.get(item.evidence_id)
        if previous is not None:
            if previous.to_dict() != item.to_dict():
                raise ProposalValidationError("EVIDENCE_ID_CONFLICT")
            continue
        by_id[item.evidence_id] = item
    return tuple(by_id.values())


def validate_obsidure_proposal(
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    *,
    validation_policy: ValidationPolicy,
) -> ProposalValidationResultV1:
    proposal_payload = proposal.to_dict()
    manifest_payload = manifest.to_dict()
    policy_id = validation_policy.policy_id(proposal_payload["proposal_id"])
    structural_ok, structural_reason = verify_proposal_manifest(manifest, proposal)
    if not structural_ok:
        return ProposalValidationResultV1(
            proposal_id=proposal_payload["proposal_id"],
            manifest_id=str(manifest_payload.get("manifest_id", "manifest-unverified")),
            policy_id=policy_id,
            policy_version=validation_policy.policy_version,
            structural_status="CONFLICTING" if "MISMATCH" in str(structural_reason) else "INVALID",
            evidence_status="NOT_EVALUATED",
            obligation_status="NOT_EVALUATED",
            risk_status="NOT_EVALUATED",
            unknown_status="NOT_EVALUATED",
            conflicts=(str(structural_reason),),
            validation_verdict="CONFLICTING" if "MISMATCH" in str(structural_reason) else "INVALID",
        )

    conflicts: list[str] = []
    limits: list[str] = []
    evidence = _dedupe_evidence(tuple(manifest.evidence_records))
    evidence_refs = tuple(sorted(item.evidence_id for item in evidence))
    evidence_status = "NO_EVIDENCE" if not evidence else "EVIDENCE_PRESENT"

    if validation_policy.require_patch_artifact and proposal.candidate_patch_ref is not None:
        patch_hash = proposal.candidate_patch_ref.sha256
        if not any(a.artifact_kind == "CANDIDATE_PATCH" and a.content_sha256 == patch_hash for a in manifest.candidate_artifacts):
            conflicts.append("PATCH_ARTIFACT_REQUIRED")

    satisfied: list[str] = []
    missing: list[str] = []
    failed: list[str] = []
    seen_results: dict[str, str] = {}
    for obligation in validation_policy.obligations:
        obligation_id = obligation.obligation_id(proposal_payload["proposal_id"])
        matches: list[EvidenceRecord] = []
        rejection_reasons: list[str] = []
        for record in evidence:
            ok, reason = _evidence_satisfies(record, obligation, proposal)
            if ok:
                matches.append(record)
            elif reason:
                rejection_reasons.append(reason)
        if matches:
            result_values = {m.result for m in matches if m.result}
            if len(result_values) > 1 and {"PASS", "FAIL"}.issubset(result_values):
                conflicts.append("CONFLICTING_EVIDENCE:" + obligation_id)
                failed.append(obligation_id)
                continue
            strongest = max(matches, key=lambda item: _status_rank(item.verification_status))
            seen_results[obligation_id] = strongest.evidence_id
            satisfied.append(obligation_id)
        elif obligation.required:
            missing.append(obligation_id)
            if rejection_reasons:
                limits.append(obligation_id + ":" + sorted(set(rejection_reasons))[0])
        else:
            limits.append("OPTIONAL_OBLIGATION_UNSATISFIED:" + obligation_id)

    risk_status = "RISK_NOT_REQUIRED"
    if validation_policy.require_risk_notes:
        risk_status = "RISK_PRESENT" if proposal.risk_notes else "RISK_MISSING"
        if not proposal.risk_notes:
            missing.append("RISK_NOTES_REQUIRED")

    unknown_status = "UNKNOWN_ACCEPTED"
    if validation_policy.require_no_unknowns and proposal.unknowns:
        unknown_status = "UNKNOWN_HELD"
        limits.extend("UNKNOWN:" + item for item in proposal.unknowns)
    elif proposal.unknowns:
        unknown_status = "UNKNOWN_RECORDED"

    if conflicts:
        verdict = "CONFLICTING"
    elif missing:
        verdict = "INCOMPLETE"
    elif validation_policy.require_no_unknowns and proposal.unknowns:
        verdict = "HELD"
    else:
        verdict = "VALID"

    return ProposalValidationResultV1(
        proposal_id=proposal_payload["proposal_id"],
        manifest_id=manifest_payload["manifest_id"],
        policy_id=policy_id,
        policy_version=validation_policy.policy_version,
        structural_status="STRUCTURAL_VALID",
        evidence_status=evidence_status,
        obligation_status="OBLIGATIONS_SATISFIED" if not missing and not conflicts else "OBLIGATIONS_OPEN",
        risk_status=risk_status,
        unknown_status=unknown_status,
        satisfied_obligations=tuple(sorted(satisfied)),
        missing_obligations=tuple(sorted(missing)),
        failed_obligations=tuple(sorted(failed)),
        evidence_refs=evidence_refs,
        conflicts=tuple(sorted(conflicts)),
        limits=tuple(sorted(set(limits))),
        validation_verdict=verdict,
    )


def default_policy_for_proposal(proposal: ObsidureBuilderProposalV1) -> ValidationPolicy:
    obligations: list[ValidationObligation] = []
    for test in proposal.tests_proposed:
        obligations.append(
            ValidationObligation(
                obligation_kind="UNIT_TEST",
                target=test,
                scope=proposal.files_touched,
                required=True,
                expected_evidence_kind="TEST_RESULT_EVIDENCE",
            )
        )
    for proof in proposal.proof_obligations:
        kind = "LEAN_PROOF" if "lean" in proof.lower() else "STATIC_CHECK"
        expected = "LEAN_EVIDENCE" if kind == "LEAN_PROOF" else "TEST_RESULT_EVIDENCE"
        obligations.append(
            ValidationObligation(
                obligation_kind=kind,
                target=proof,
                scope=proposal.files_touched,
                required=True,
                expected_evidence_kind=expected,
            )
        )
    return ValidationPolicy(obligations=tuple(obligations))
