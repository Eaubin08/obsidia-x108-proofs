"""R6-C1 strict semantic-role interpretation adapter.

Transforms bounded structured output proposed by Brody or a local model into the
canonical SemanticRoleProjectionV0. It does not call a model itself.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

from periphery.cognition.semantic_roles_v0 import (
    SemanticResolutionStatusV0,
    SemanticRoleBindingV0,
    SemanticRoleCandidateV0,
    SemanticRoleKindV0,
    SemanticRoleProjectionV0,
    build_semantic_role_projection_v0,
)

_SCHEMA = "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0"
_ALLOWED_TOP = {"schema", "roles", "producer", "producer_version"}
_ALLOWED_ROLE_FIELDS = {"status", "candidates", "rationale_refs"}
_ALLOWED_CANDIDATE_FIELDS = {"value", "surface", "evidence_refs"}
_AUTHORITY_FORBIDDEN = {
    "ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT", "EXECUTE",
    "AUTHORIZED", "AUTHORISED",
}


@dataclass(frozen=True)
class SemanticRoleInterpretationResultV0:
    status: str
    projection: SemanticRoleProjectionV0 | None
    producer: str
    producer_version: str
    errors: tuple[str, ...]
    readonly: bool = True
    non_sovereign: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    emits_verdict: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False


def semantic_role_prompt_v0(raw_utterance: str) -> str:
    return (
        "Return JSON only. No explanation, reasoning, markdown, or authority words.\\n"
        f"schema must be {_SCHEMA}.\\n"
        "roles must contain only FOCUS, SCOPE, OPERATION, QUALIFIER, "
        "SOURCE_OR_INSTRUMENT.\\n"
        "Each role: status is RESOLVED, AMBIGUOUS, or UNKNOWN.\\n"
        "RESOLVED => exactly one candidate. AMBIGUOUS => at least two candidates. "
        "UNKNOWN => empty candidates.\\n"
        "Each candidate contains value plus surface copied exactly from the user "
        "utterance; evidence_refs may be empty. Never invent spans.\\n"
        "Do not decide, authorize, execute, route, or choose tools.\\n"
        "User utterance:\\n" + raw_utterance
    )


def _json_object(value: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    text = str(value or "").strip()
    if not text:
        raise ValueError("EMPTY_INTERPRETATION_OUTPUT")
    if text.startswith("~~~") or "<thinking>" in text.lower() or "<scratchpad>" in text.lower():
        raise ValueError("NON_JSON_OR_REASONING_WRAPPER_FORBIDDEN")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("INVALID_JSON_INTERPRETATION_OUTPUT") from exc
    if not isinstance(parsed, Mapping):
        raise ValueError("INTERPRETATION_OUTPUT_MUST_BE_OBJECT")
    return parsed


def _surface_span(raw: str, surface: str) -> tuple[int, int]:
    if not surface:
        raise ValueError("CANDIDATE_SURFACE_REQUIRED")
    matches = list(re.finditer(re.escape(surface), raw, flags=re.IGNORECASE))
    if not matches:
        raise ValueError("CANDIDATE_SURFACE_NOT_IN_RAW")
    if len(matches) > 1:
        raise ValueError("CANDIDATE_SURFACE_NOT_UNIQUE")
    match = matches[0]
    return match.start(), match.end()


def _forbid_authority_words(payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False).upper()
    for token in _AUTHORITY_FORBIDDEN:
        if re.search(rf"(?<![A-Z0-9_]){re.escape(token)}(?![A-Z0-9_])", rendered):
            raise ValueError(f"AUTHORITY_WORD_FORBIDDEN:{token}")


def interpret_semantic_roles_v0(
    *,
    raw_utterance: str,
    structured_output: str | Mapping[str, Any],
    source_refs: tuple[str, ...] = (),
) -> SemanticRoleInterpretationResultV0:
    try:
        payload = _json_object(structured_output)
        extra = set(payload) - _ALLOWED_TOP
        if extra:
            raise ValueError("UNEXPECTED_TOP_LEVEL_FIELDS:" + ",".join(sorted(extra)))
        if payload.get("schema") != _SCHEMA:
            raise ValueError("SEMANTIC_ROLE_SCHEMA_MISMATCH")
        _forbid_authority_words(payload)

        producer = str(payload.get("producer") or "UNKNOWN_PRODUCER").strip()
        producer_version = str(payload.get("producer_version") or "UNKNOWN").strip()
        roles = payload.get("roles")
        if not isinstance(roles, Mapping):
            raise ValueError("ROLES_OBJECT_REQUIRED")

        known_roles = {item.value for item in SemanticRoleKindV0}
        unknown_role_keys = set(roles) - known_roles
        if unknown_role_keys:
            raise ValueError("UNKNOWN_ROLE_KEYS:" + ",".join(sorted(unknown_role_keys)))

        bindings: list[SemanticRoleBindingV0] = []
        for role_kind in SemanticRoleKindV0:
            item = roles.get(role_kind.value)
            if item is None:
                bindings.append(
                    SemanticRoleBindingV0(
                        role=role_kind,
                        status=SemanticResolutionStatusV0.UNKNOWN,
                    )
                )
                continue
            if not isinstance(item, Mapping):
                raise ValueError(f"ROLE_OBJECT_REQUIRED:{role_kind.value}")
            extra_fields = set(item) - _ALLOWED_ROLE_FIELDS
            if extra_fields:
                raise ValueError(
                    f"UNEXPECTED_ROLE_FIELDS:{role_kind.value}:"
                    + ",".join(sorted(extra_fields))
                )
            try:
                status = SemanticResolutionStatusV0(str(item.get("status") or ""))
            except ValueError as exc:
                raise ValueError(f"INVALID_ROLE_STATUS:{role_kind.value}") from exc

            raw_candidates = item.get("candidates") or []
            if not isinstance(raw_candidates, list):
                raise ValueError(f"ROLE_CANDIDATES_MUST_BE_LIST:{role_kind.value}")

            candidates: list[SemanticRoleCandidateV0] = []
            for raw_candidate in raw_candidates:
                if not isinstance(raw_candidate, Mapping):
                    raise ValueError(f"CANDIDATE_OBJECT_REQUIRED:{role_kind.value}")
                extra_candidate = set(raw_candidate) - _ALLOWED_CANDIDATE_FIELDS
                if extra_candidate:
                    raise ValueError(
                        f"UNEXPECTED_CANDIDATE_FIELDS:{role_kind.value}:"
                        + ",".join(sorted(extra_candidate))
                    )
                value = str(raw_candidate.get("value") or "").strip()
                surface = str(raw_candidate.get("surface") or "")
                span = _surface_span(raw_utterance, surface)
                evidence_refs = tuple(
                    str(x).strip()
                    for x in (raw_candidate.get("evidence_refs") or [])
                    if str(x).strip()
                )
                candidates.append(
                    SemanticRoleCandidateV0(
                        value=value,
                        source_span=span,
                        evidence_refs=(*evidence_refs, f"raw-surface:{surface}"),
                    )
                )

            rationale_refs = tuple(
                str(x).strip()
                for x in (item.get("rationale_refs") or [])
                if str(x).strip()
            )
            bindings.append(
                SemanticRoleBindingV0(
                    role=role_kind,
                    status=status,
                    candidates=tuple(candidates),
                    rationale_refs=rationale_refs,
                )
            )

        projection = build_semantic_role_projection_v0(
            raw_utterance=raw_utterance,
            bindings=bindings,
            source_refs=(
                *source_refs,
                f"semantic-role-producer:{producer}:{producer_version}",
            ),
        )
        return SemanticRoleInterpretationResultV0(
            status="SEMANTIC_ROLE_INTERPRETATION_ACCEPTED",
            projection=projection,
            producer=producer,
            producer_version=producer_version,
            errors=(),
        )
    except (TypeError, ValueError) as exc:
        return SemanticRoleInterpretationResultV0(
            status="SEMANTIC_ROLE_INTERPRETATION_REJECTED",
            projection=None,
            producer="UNVERIFIED",
            producer_version="UNVERIFIED",
            errors=(str(exc),),
        )
