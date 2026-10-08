"""R6-A Semantic Role / Focus Contract V0.

A readonly, non-sovereign representation of functional semantic roles.
This module does not parse natural language, route capabilities, call models,
write memory, decide, or authorize execution.

Upstream cognition may propose role candidates; this contract preserves
resolution status, candidate ambiguity, raw-span provenance and evidence refs.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Iterable


class SemanticRoleKindV0(str, Enum):
    FOCUS = "FOCUS"
    SCOPE = "SCOPE"
    OPERATION = "OPERATION"
    QUALIFIER = "QUALIFIER"
    SOURCE_OR_INSTRUMENT = "SOURCE_OR_INSTRUMENT"


class SemanticResolutionStatusV0(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SemanticRoleCandidateV0:
    value: str
    source_span: tuple[int, int] | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("semantic role candidate value must be non-empty")
        if self.source_span is not None:
            start, end = self.source_span
            if start < 0 or end <= start:
                raise ValueError("source_span must satisfy 0 <= start < end")


@dataclass(frozen=True)
class SemanticRoleBindingV0:
    role: SemanticRoleKindV0
    status: SemanticResolutionStatusV0
    candidates: tuple[SemanticRoleCandidateV0, ...] = ()
    rationale_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        count = len(self.candidates)
        if self.status is SemanticResolutionStatusV0.RESOLVED and count != 1:
            raise ValueError("RESOLVED semantic role requires exactly one candidate")
        if self.status is SemanticResolutionStatusV0.AMBIGUOUS and count < 2:
            raise ValueError("AMBIGUOUS semantic role requires at least two candidates")
        if self.status is SemanticResolutionStatusV0.UNKNOWN and count != 0:
            raise ValueError("UNKNOWN semantic role must not invent candidates")

    @property
    def resolved_value(self) -> str | None:
        if self.status is SemanticResolutionStatusV0.RESOLVED:
            return self.candidates[0].value
        return None


@dataclass(frozen=True)
class SemanticRoleProjectionV0:
    projection_id: str
    utterance_sha256: str
    bindings: tuple[SemanticRoleBindingV0, ...]
    source_refs: tuple[str, ...] = ()
    readonly: bool = True
    non_sovereign: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    emits_verdict: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False

    def __post_init__(self) -> None:
        if not self.projection_id:
            raise ValueError("projection_id is required")
        if len(self.utterance_sha256) != 64:
            raise ValueError("utterance_sha256 must be a full SHA-256 hex digest")
        try:
            int(self.utterance_sha256, 16)
        except ValueError as exc:
            raise ValueError("utterance_sha256 must be hexadecimal") from exc

        roles = [binding.role for binding in self.bindings]
        if len(roles) != len(set(roles)):
            raise ValueError("each semantic role kind may appear at most once")

        if not self.readonly or not self.non_sovereign:
            raise ValueError("semantic role projection must remain readonly/non-sovereign")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("semantic role projection cannot change decision authority")
        if any(
            (
                self.allowed_to_decide,
                self.allowed_to_act,
                self.emits_act,
                self.emits_verdict,
                self.memory_write,
                self.kernel_mutation,
            )
        ):
            raise ValueError("semantic role projection cannot decide, act, write, or mutate kernel")

    def binding(self, role: SemanticRoleKindV0) -> SemanticRoleBindingV0 | None:
        return next((item for item in self.bindings if item.role is role), None)

    def resolved(self, role: SemanticRoleKindV0) -> str | None:
        item = self.binding(role)
        return item.resolved_value if item is not None else None

    def to_brody_context(self) -> dict:
        """Additive readonly context. No routing or authority semantics."""
        return {
            "contract": "SEMANTIC_ROLE_PROJECTION_V0",
            "projection_id": self.projection_id,
            "utterance_sha256": self.utterance_sha256,
            "roles": {
                binding.role.value: {
                    "status": binding.status.value,
                    "resolved_value": binding.resolved_value,
                    "candidates": [
                        {
                            "value": candidate.value,
                            "source_span": list(candidate.source_span)
                            if candidate.source_span is not None
                            else None,
                            "evidence_refs": list(candidate.evidence_refs),
                        }
                        for candidate in binding.candidates
                    ],
                    "rationale_refs": list(binding.rationale_refs),
                }
                for binding in self.bindings
            },
            "source_refs": list(self.source_refs),
            "readonly": True,
            "non_sovereign": True,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
            "memory_write": False,
            "kernel_mutation": False,
        }


def build_semantic_role_projection_v0(
    *,
    raw_utterance: str,
    bindings: Iterable[SemanticRoleBindingV0],
    source_refs: tuple[str, ...] = (),
) -> SemanticRoleProjectionV0:
    raw_bytes = raw_utterance.encode("utf-8")
    digest = hashlib.sha256(raw_bytes).hexdigest()
    material = tuple(bindings)

    # Validate spans against exact raw text bytes at the Python-string level.
    text_len = len(raw_utterance)
    for binding in material:
        for candidate in binding.candidates:
            if candidate.source_span is not None and candidate.source_span[1] > text_len:
                raise ValueError("semantic role source_span exceeds raw utterance length")

    identity_material = "|".join(
        [
            digest,
            *(
                f"{binding.role.value}:{binding.status.value}:"
                + ",".join(candidate.value for candidate in binding.candidates)
                for binding in material
            ),
        ]
    )
    projection_id = "srp-" + hashlib.sha256(identity_material.encode("utf-8")).hexdigest()[:32]

    return SemanticRoleProjectionV0(
        projection_id=projection_id,
        utterance_sha256=digest,
        bindings=material,
        source_refs=source_refs,
    )
