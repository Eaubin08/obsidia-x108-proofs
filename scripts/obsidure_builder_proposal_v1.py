from __future__ import annotations

"""
R9-B1 canonical Obsidure builder proposal contract.

This module represents proposal material only. It does not perform patch
application, test running, provider calls, authority routing, or file mutation.
"""

import dataclasses
import hashlib
import json
import math
import re

from collections.abc import Mapping as RuntimeMapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping


SCHEMA_VERSION = "OBSIDURE_BUILDER_PROPOSAL_V1"
PROPOSAL_ID_PREFIX = "obp-"
PROPOSAL_ID_BITS = 256
AUTHORITY_NONE = "NONE"
PATCH_FORMAT_REAL_UNIFIED_DIFF_V1 = "REAL_UNIFIED_DIFF_V1"

PROVIDER_OUTPUT = "PROPOSAL_MATERIAL"
PROVIDER_OUTPUT_AUTHORITY = AUTHORITY_NONE
OBSIDURE_AUTHORITY = AUTHORITY_NONE
EXECUTION_ALLOWED = False

PROPOSAL_KINDS = frozenset((
    "PATCH",
    "REPAIR",
    "BUILD",
    "TOOLING",
    "NATIVE_PLAN",
))

MAX_TEXT = 4096
MAX_REF_TEXT = 512
MAX_ITEMS = 64
MAX_FILES = 64
MAX_METADATA_KEYS = 64

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_FORBIDDEN_AUTHORITY_WORDS = frozenset((
    "ALLOW",
    "ACT",
    "EXECUTE",
    "WRITE",
    "COMMIT",
    "PUSH",
    "MERGE",
    "SELF_AUTHORIZE",
))


class BuilderProposalError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _reject_forbidden_authority(value: object, field_name: str) -> None:
    if isinstance(value, str) and value.strip().upper() in _FORBIDDEN_AUTHORITY_WORDS:
        raise BuilderProposalError(f"FORBIDDEN_AUTHORITY_VALUE:{field_name}")


def _validate_json_value(value: Any, path: str = "$", seen: set[int] | None = None) -> Any:
    if seen is None:
        seen = set()

    if isinstance(value, (RuntimeMapping, list, tuple)):
        ident = id(value)
        if ident in seen:
            raise BuilderProposalError(f"RECURSIVE_STRUCTURE:{path}")
        seen.add(ident)

    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        _reject_forbidden_authority(value, path)
        if len(value) > MAX_TEXT:
            raise BuilderProposalError(f"TEXT_TOO_LONG:{path}")
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise BuilderProposalError(f"NON_FINITE_NUMBER:{path}")
        return value
    if isinstance(value, bytes):
        raise BuilderProposalError(f"BYTES_FORBIDDEN:{path}")
    if isinstance(value, (set, frozenset)):
        raise BuilderProposalError(f"SET_FORBIDDEN:{path}")
    if isinstance(value, tuple):
        return tuple(_validate_json_value(v, f"{path}[]", seen) for v in value)
    if isinstance(value, list):
        if len(value) > MAX_ITEMS:
            raise BuilderProposalError(f"LIST_TOO_LONG:{path}")
        return tuple(_validate_json_value(v, f"{path}[]", seen) for v in value)
    if isinstance(value, RuntimeMapping):
        if len(value) > MAX_METADATA_KEYS:
            raise BuilderProposalError(f"OBJECT_TOO_WIDE:{path}")
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise BuilderProposalError(f"NON_STRING_KEY:{path}")
            if len(key) > MAX_REF_TEXT:
                raise BuilderProposalError(f"KEY_TOO_LONG:{path}")
            _reject_forbidden_authority(key, f"{path}.{key}")
            out[key] = _validate_json_value(item, f"{path}.{key}", seen)
        return _freeze_mapping(out)
    raise BuilderProposalError(f"UNSUPPORTED_JSON_TYPE:{path}:{type(value).__name__}")


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


def _json_plain(value: Any) -> Any:
    if isinstance(value, RuntimeMapping):
        return {key: _json_plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_plain(item) for item in value]
    if isinstance(value, list):
        return [_json_plain(item) for item in value]
    return value


def _as_tuple(values: Any, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[Any, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        raise BuilderProposalError(f"{field_name}_MUST_BE_SEQUENCE")
    try:
        result = tuple(values)
    except TypeError as exc:
        raise BuilderProposalError(f"{field_name}_MUST_BE_SEQUENCE") from exc
    if len(result) > max_items:
        raise BuilderProposalError(f"{field_name}_TOO_LONG")
    return result


def _bounded_strings(values: Any, field_name: str, *, max_items: int = MAX_ITEMS) -> tuple[str, ...]:
    out: list[str] = []
    for item in _as_tuple(values, field_name, max_items=max_items):
        if not isinstance(item, str):
            raise BuilderProposalError(f"{field_name}_ITEM_NOT_STRING")
        value = item.strip()
        _reject_forbidden_authority(value, field_name)
        if not value:
            raise BuilderProposalError(f"{field_name}_ITEM_EMPTY")
        if len(value) > MAX_REF_TEXT:
            raise BuilderProposalError(f"{field_name}_ITEM_TOO_LONG")
        out.append(value)
    return tuple(out)


def _canonical_path(raw: str, field_name: str) -> str:
    if not isinstance(raw, str):
        raise BuilderProposalError(f"{field_name}_NOT_STRING")
    value = raw.strip().replace("\\", "/")
    if not value:
        raise BuilderProposalError(f"{field_name}_EMPTY")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise BuilderProposalError(f"{field_name}_ABSOLUTE")
    path = PurePosixPath(value)
    if any(part in ("", ".", "..") for part in path.parts):
        raise BuilderProposalError(f"{field_name}_TRAVERSAL")
    return "/".join(path.parts)


def _paths(values: Any, field_name: str) -> tuple[str, ...]:
    paths = tuple(_canonical_path(str(v), field_name) for v in _as_tuple(values, field_name, max_items=MAX_FILES))
    if len(set(paths)) != len(paths):
        raise BuilderProposalError(f"{field_name}_DUPLICATE")
    return tuple(sorted(paths))


def _sha256(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise BuilderProposalError(f"{field_name}_NOT_STRING")
    normalized = value.strip().lower()
    if not _SHA256_RE.fullmatch(normalized):
        raise BuilderProposalError(f"{field_name}_NOT_SHA256")
    return normalized


def _base_commit_sha(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise BuilderProposalError(f"{field_name}_NOT_STRING")
    normalized = value.strip().lower()
    if not (_SHA256_RE.fullmatch(normalized) or _GIT_SHA_RE.fullmatch(normalized)):
        raise BuilderProposalError(f"{field_name}_NOT_GIT_SHA_OR_SHA256")
    return normalized


def canonical_json(value: Mapping[str, Any]) -> str:
    normalized = _validate_json_value(value)
    try:
        return json.dumps(_json_plain(normalized), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise BuilderProposalError("CANONICAL_JSON_FAILED") from exc


def _canonical_payload(data: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_json(data))


def _proposal_digest(payload: Mapping[str, Any]) -> str:
    return _sha256_text(canonical_json(payload))


@dataclass(frozen=True)
class BuilderPatchRef:
    artifact_ref: str
    sha256: str
    patch_format: str = PATCH_FORMAT_REAL_UNIFIED_DIFF_V1

    def __post_init__(self) -> None:
        if not isinstance(self.artifact_ref, str) or not self.artifact_ref.strip():
            raise BuilderProposalError("PATCH_ARTIFACT_REF_REQUIRED")
        if len(self.artifact_ref) > MAX_REF_TEXT:
            raise BuilderProposalError("PATCH_ARTIFACT_REF_TOO_LONG")
        object.__setattr__(self, "artifact_ref", self.artifact_ref.strip())
        object.__setattr__(self, "sha256", _sha256(self.sha256, "candidate_patch_hash"))
        if self.patch_format != PATCH_FORMAT_REAL_UNIFIED_DIFF_V1:
            raise BuilderProposalError("PATCH_FORMAT_UNSUPPORTED")

    def to_payload(self) -> dict[str, str]:
        return {
            "artifact_ref": self.artifact_ref,
            "patch_format": self.patch_format,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class ObsidureBuilderProposalV1:
    objective: str
    proposal_kind: str
    base_commit_sha: str
    target_scope: tuple[str, ...]
    files_touched: tuple[str, ...]
    candidate_patch_ref: BuilderPatchRef | None = None
    source_context_refs: tuple[str, ...] = ()
    input_artifact_refs: tuple[str, ...] = ()
    tests_proposed: tuple[str, ...] = ()
    proof_obligations: tuple[str, ...] = ()
    risk_notes: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    provider_ref: str = "UNSPECIFIED_PROVIDER"
    builder_ref: str = "OBSIDURE"
    created_from: str = "UNSPECIFIED_SOURCE"
    declared_evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    authority: str = AUTHORITY_NONE
    execution_allowed: bool = EXECUTION_ALLOWED

    def __post_init__(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise BuilderProposalError("OBJECTIVE_REQUIRED")
        if len(self.objective) > MAX_TEXT:
            raise BuilderProposalError("OBJECTIVE_TOO_LONG")
        kind = str(self.proposal_kind).strip().upper()
        if kind not in PROPOSAL_KINDS:
            raise BuilderProposalError("PROPOSAL_KIND_UNSUPPORTED")
        object.__setattr__(self, "proposal_kind", kind)
        object.__setattr__(self, "base_commit_sha", _base_commit_sha(self.base_commit_sha, "base_commit_sha"))
        object.__setattr__(self, "target_scope", _paths(self.target_scope, "target_scope"))
        if not self.target_scope:
            raise BuilderProposalError("TARGET_SCOPE_REQUIRED")
        object.__setattr__(self, "files_touched", _paths(self.files_touched, "files_touched"))
        if not self.files_touched:
            raise BuilderProposalError("FILES_TOUCHED_REQUIRED")
        if not set(self.files_touched).issubset(set(self.target_scope)):
            raise BuilderProposalError("FILES_OUTSIDE_TARGET_SCOPE")
        object.__setattr__(self, "source_context_refs", _bounded_strings(self.source_context_refs, "source_context_refs"))
        object.__setattr__(self, "input_artifact_refs", _bounded_strings(self.input_artifact_refs, "input_artifact_refs"))
        object.__setattr__(self, "tests_proposed", _bounded_strings(self.tests_proposed, "tests_proposed"))
        object.__setattr__(self, "proof_obligations", _bounded_strings(self.proof_obligations, "proof_obligations"))
        object.__setattr__(self, "risk_notes", _bounded_strings(self.risk_notes, "risk_notes"))
        object.__setattr__(self, "unknowns", _bounded_strings(self.unknowns, "unknowns"))
        for field_name in ("provider_ref", "builder_ref", "created_from"):
            value = str(getattr(self, field_name) or "").strip()
            if not value:
                raise BuilderProposalError(f"{field_name.upper()}_REQUIRED")
            if len(value) > MAX_REF_TEXT:
                raise BuilderProposalError(f"{field_name.upper()}_TOO_LONG")
            _reject_forbidden_authority(value, field_name)
            object.__setattr__(self, field_name, value)
        object.__setattr__(self, "declared_evidence", _freeze_mapping(_validate_json_value(dict(self.declared_evidence), "declared_evidence")))
        object.__setattr__(self, "metadata", _freeze_mapping(_validate_json_value(dict(self.metadata), "metadata")))
        if self.authority != AUTHORITY_NONE:
            raise BuilderProposalError("AUTHORITY_MUST_BE_NONE")
        if self.execution_allowed is not False:
            raise BuilderProposalError("EXECUTION_ALLOWED_MUST_BE_FALSE")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "objective": self.objective.strip(),
            "proposal_kind": self.proposal_kind,
            "source_context_refs": list(self.source_context_refs),
            "input_artifact_refs": list(self.input_artifact_refs),
            "base_repo_ref": self.base_repo_ref,
            "base_commit_sha": self.base_commit_sha,
            "target_scope": list(self.target_scope),
            "candidate_patch_ref": self.candidate_patch_ref.to_payload() if self.candidate_patch_ref else None,
            "files_touched": list(self.files_touched),
            "tests_proposed": list(self.tests_proposed),
            "proof_obligations": list(self.proof_obligations),
            "risk_notes": list(self.risk_notes),
            "unknowns": list(self.unknowns),
            "provider_ref": self.provider_ref,
            "builder_ref": self.builder_ref,
            "created_from": self.created_from,
            "declared_evidence": self.declared_evidence,
            "metadata": self.metadata,
            "authority": self.authority,
            "execution_allowed": self.execution_allowed,
            "provider_output": PROVIDER_OUTPUT,
            "provider_output_authority": PROVIDER_OUTPUT_AUTHORITY,
            "tests_are_obligations_not_authority": True,
            "proof_claims_are_non_authoritative": True,
        }

    @property
    def base_repo_ref(self) -> str:
        return "GIT_COMMIT"

    @property
    def proposal_digest(self) -> str:
        return _proposal_digest(self.identity_payload())

    @property
    def proposal_id(self) -> str:
        return PROPOSAL_ID_PREFIX + self.proposal_digest

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.identity_payload())
        payload["proposal_digest"] = self.proposal_digest
        payload["proposal_id"] = self.proposal_id
        payload["proposal_id_bits"] = PROPOSAL_ID_BITS
        return _canonical_payload(payload)


def build_builder_proposal(**kwargs: Any) -> ObsidureBuilderProposalV1:
    return ObsidureBuilderProposalV1(**kwargs)


def verify_builder_proposal(proposal: ObsidureBuilderProposalV1 | Mapping[str, Any]) -> tuple[bool, str | None]:
    try:
        payload = proposal.to_dict() if isinstance(proposal, ObsidureBuilderProposalV1) else dict(proposal)
        digest = payload.get("proposal_digest")
        proposal_id = payload.get("proposal_id")
        body = dict(payload)
        body.pop("proposal_digest", None)
        body.pop("proposal_id", None)
        body.pop("proposal_id_bits", None)
        expected = _proposal_digest(body)
        if digest != expected:
            return False, "PROPOSAL_DIGEST_MISMATCH"
        if proposal_id != PROPOSAL_ID_PREFIX + expected:
            return False, "PROPOSAL_ID_MISMATCH"
        if payload.get("authority") != AUTHORITY_NONE:
            return False, "AUTHORITY_NOT_NONE"
        if payload.get("execution_allowed") is not False:
            return False, "EXECUTION_ALLOWED_NOT_FALSE"
        return True, None
    except BuilderProposalError as exc:
        return False, str(exc)


def from_candidate_manifest(manifest: Mapping[str, Any], *, objective: str | None = None) -> ObsidureBuilderProposalV1:
    patch_hash = manifest.get("candidate_patch_sha256")
    files = manifest.get("candidate_files") or ()
    base = manifest.get("base_sha") or manifest.get("base_commit_sha")
    patch_ref = manifest.get("candidate_patch") or "candidate.patch"
    return ObsidureBuilderProposalV1(
        objective=objective or str(manifest.get("objective") or manifest.get("proposal_id") or manifest.get("route") or "Obsidure candidate proposal"),
        proposal_kind="TOOLING" if str(manifest.get("route") or "").startswith("TOOLING") else "PATCH",
        base_commit_sha=str(base or ""),
        target_scope=tuple(files),
        files_touched=tuple(files),
        candidate_patch_ref=BuilderPatchRef(str(patch_ref), str(patch_hash or ""), str(manifest.get("candidate_patch_mode") or PATCH_FORMAT_REAL_UNIFIED_DIFF_V1)),
        input_artifact_refs=tuple(str(v) for v in (manifest.get("proposal_json"), manifest.get("candidate_patch")) if v),
        risk_notes=tuple(str(v) for v in (manifest.get("surface"), manifest.get("route")) if v),
        provider_ref=str(manifest.get("producer") or "OBSIDURE_CANDIDATE_EXPORT"),
        builder_ref=str(manifest.get("producer") or "OBSIDURE"),
        created_from="candidate_manifest",
        declared_evidence={
            "producer_authority": manifest.get("producer_authority"),
            "decision_authority": manifest.get("decision_authority"),
            "auto_apply": manifest.get("auto_apply"),
            "auto_commit": manifest.get("auto_commit"),
            "auto_push": manifest.get("auto_push"),
            "auto_merge": manifest.get("auto_merge"),
            "world_action": manifest.get("world_action"),
        },
    )


def from_patch_proposal(proposal: Any, *, base_commit_sha: str, candidate_patch_ref: BuilderPatchRef | None = None) -> ObsidureBuilderProposalV1:
    data = dataclasses.asdict(proposal) if dataclasses.is_dataclass(proposal) else dict(proposal)
    patches = data.get("patches") or ()
    files = tuple(str(p.get("path")) for p in patches if isinstance(p, Mapping) and p.get("path"))
    return ObsidureBuilderProposalV1(
        objective=str(data.get("objective") or "Obsidure patch proposal"),
        proposal_kind="PATCH",
        base_commit_sha=base_commit_sha,
        target_scope=files,
        files_touched=files,
        candidate_patch_ref=candidate_patch_ref,
        input_artifact_refs=tuple(str(v) for v in (data.get("proposal_id"), data.get("receipt_id")) if v),
        risk_notes=tuple(str(v) for v in (data.get("kernel_path_blocked"),) if v not in (None, False, "")),
        provider_ref="AGENT_OBSIDURE_PATCH_PROPOSAL",
        builder_ref="AGENT_OBSIDURE",
        created_from="PatchProposal",
        declared_evidence={"legacy_human_approved": data.get("human_approved")},
    )


def from_repair_proposal(proposal: Any, *, base_commit_sha: str) -> ObsidureBuilderProposalV1:
    data = dataclasses.asdict(proposal) if dataclasses.is_dataclass(proposal) else dict(proposal)
    candidates = data.get("candidate_files") or ()
    files = tuple(str(c.get("path")) for c in candidates if isinstance(c, Mapping) and c.get("path"))
    return ObsidureBuilderProposalV1(
        objective=str(data.get("rationale") or data.get("request_id") or "Obsidure repair proposal"),
        proposal_kind="REPAIR",
        base_commit_sha=base_commit_sha,
        target_scope=files,
        files_touched=files,
        tests_proposed=tuple(str(t) for t in (data.get("tests_to_run") or ())),
        input_artifact_refs=tuple(str(v) for v in (data.get("request_id"), data.get("proposal_id")) if v),
        provider_ref=str(data.get("engine") or "REPAIR_PROVIDER"),
        builder_ref="OBSIDURE_REPAIR_CONTRACT",
        created_from="RepairProposal",
        declared_evidence={"confidence": data.get("confidence"), "boundary": data.get("boundary")},
    )


def from_native_plan(plan: Any, *, base_commit_sha: str) -> ObsidureBuilderProposalV1:
    data = dataclasses.asdict(plan) if dataclasses.is_dataclass(plan) else dict(plan)
    steps = data.get("steps") or ()
    files = tuple(str(s.get("target_path")) for s in steps if isinstance(s, Mapping) and s.get("target_path") and not str(s.get("target_path")).startswith("<"))
    return ObsidureBuilderProposalV1(
        objective=str(data.get("objective") or "Obsidure native plan"),
        proposal_kind="NATIVE_PLAN",
        base_commit_sha=base_commit_sha,
        target_scope=files,
        files_touched=files,
        tests_proposed=tuple(str(v) for v in (data.get("acceptance_criteria") or ())),
        unknowns=tuple(str(v) for v in (data.get("missing_capabilities") or ())),
        input_artifact_refs=tuple(str(v) for v in (data.get("request_id"), data.get("spec_id"), data.get("plan_id")) if v),
        provider_ref="OBSIDURE_NATIVE_PLAN",
        builder_ref="OBSIDURE_NATIVE_PLAN",
        created_from="NativePlan",
        declared_evidence={
            "decision_authority": data.get("decision_authority"),
            "emits_act": data.get("emits_act"),
            "canonical_write": data.get("canonical_write"),
            "world_action": data.get("world_action"),
        },
    )
