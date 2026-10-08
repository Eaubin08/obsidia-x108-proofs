"""R6-D1 Brody/SENS semantic focus V1.

Selective recovery of the historical Jarvis semantic-focus/query-roles work:
- source: Eaubin08/Jarvis-iron-obsidia- exp/semantic-focus-query-roles-v0
- source commit: 0b91179d5c4ad67ab5ecfda679d3d716e39bfe98

The historical V0 established PRESENCE_OF_CONCEPT != SEMANTIC_ROLE but treated
most MEMORY mentions as focus. V1 preserves that source idea while adding an
explicit instrument/source distinction and failing closed outside narrow,
grounded patterns.

No model call. No routing. No retrieval. No action. No authority.
"""
from __future__ import annotations

import re

from periphery.cognition.semantic_roles_v0 import (
    SemanticResolutionStatusV0,
    SemanticRoleBindingV0,
    SemanticRoleCandidateV0,
    SemanticRoleKindV0,
    SemanticRoleProjectionV0,
    build_semantic_role_projection_v0,
)


def _match(pattern: str, text: str) -> re.Match[str] | None:
    return re.search(pattern, text, flags=re.IGNORECASE | re.UNICODE)


def _candidate(
    value: str,
    match: re.Match[str],
    *,
    evidence: str,
) -> SemanticRoleCandidateV0:
    return SemanticRoleCandidateV0(
        value=value,
        source_span=(match.start(), match.end()),
        evidence_refs=(evidence,),
    )


def _unknown(role: SemanticRoleKindV0) -> SemanticRoleBindingV0:
    return SemanticRoleBindingV0(
        role=role,
        status=SemanticResolutionStatusV0.UNKNOWN,
    )


def _resolved(
    role: SemanticRoleKindV0,
    candidate: SemanticRoleCandidateV0,
    *,
    rationale: str,
) -> SemanticRoleBindingV0:
    return SemanticRoleBindingV0(
        role=role,
        status=SemanticResolutionStatusV0.RESOLVED,
        candidates=(candidate,),
        rationale_refs=(rationale,),
    )


def build_brody_semantic_focus_projection_v1(
    raw_utterance: str,
) -> SemanticRoleProjectionV0 | None:
    """Build a narrow deterministic Brody/SENS semantic-role projection.

    Returns None when the supported role relation cannot be established without
    guessing. This is an upstream cognition signal, never a capability route.
    """
    raw = str(raw_utterance or "")
    if not raw.strip():
        return None

    memory = _match(r"\b(?:mémoire|memoire|memory)\b", raw)
    obsidia = _match(r"\b(?:obsidia|obsidian|obsidio)\b", raw)
    explain = _match(
        r"\b(?:explique|expliquer|expliquez|explain|describe|décris|decris)\b",
        raw,
    )
    detail = _match(
        r"\b(?:détaille|detaille|détailler|detailler|détails|details|"
        r"développe|developpe|developper)\b",
        raw,
    )
    knowledge = _match(
        r"\b(?:sais|savoir|connais|connait|connaît|know|contient|contenu|"
        r"retrouve|rappelle)\b",
        raw,
    )

    # "using memory" is a functional relation, not merely concept presence.
    instrument_memory = _match(
        r"(?:\ben\s+utilisant\s+(?:ta|la|ma|sa|notre|votre|leur)?\s*"
        r"|\bavec\s+(?:ta|la|ma|sa|notre|votre|leur)?\s*"
        r"|\bvia\s+(?:ta|la|ma|sa|notre|votre|leur)?\s*"
        r"|\bà\s+partir\s+de\s+(?:ta|la|ma|sa|notre|votre|leur)?\s*)"
        r"(?:mémoire|memoire|memory)\b",
        raw,
    )

    bindings: dict[SemanticRoleKindV0, SemanticRoleBindingV0] = {
        role: _unknown(role) for role in SemanticRoleKindV0
    }
    rationale = "brody-sens-v1:presence-not-role"

    # Case A: memory explicitly used as an instrument/source.
    if instrument_memory is not None:
        # Resolve the exact MEMORY token inside the larger instrument phrase.
        memory_inside = _match(r"\b(?:mémoire|memoire|memory)\b", instrument_memory.group(0))
        if memory_inside is None:
            return None
        mem_start = instrument_memory.start() + memory_inside.start()
        mem_end = instrument_memory.start() + memory_inside.end()
        source_candidate = SemanticRoleCandidateV0(
            value="MEMORY",
            source_span=(mem_start, mem_end),
            evidence_refs=("brody-sens-v1:explicit-instrument-construction",),
        )
        bindings[SemanticRoleKindV0.SOURCE_OR_INSTRUMENT] = _resolved(
            SemanticRoleKindV0.SOURCE_OR_INSTRUMENT,
            source_candidate,
            rationale="explicit linguistic instrument relation",
        )

        if obsidia is not None:
            bindings[SemanticRoleKindV0.FOCUS] = _resolved(
                SemanticRoleKindV0.FOCUS,
                _candidate(
                    "OBSIDIA",
                    obsidia,
                    evidence="brody-sens-v1:instrument-contrast-focus",
                ),
                rationale="object precedes explicit memory instrument relation",
            )
        else:
            # Instrument alone does not establish what the request is about.
            bindings[SemanticRoleKindV0.FOCUS] = _unknown(
                SemanticRoleKindV0.FOCUS
            )

    # Case B: memory itself is being interrogated, optionally about Obsidia.
    elif memory is not None and (knowledge is not None or explain is not None):
        bindings[SemanticRoleKindV0.FOCUS] = _resolved(
            SemanticRoleKindV0.FOCUS,
            _candidate(
                "MEMORY",
                memory,
                evidence="brody-sens-v1:memory-object",
            ),
            rationale="memory is the object being interrogated",
        )
        if obsidia is not None:
            bindings[SemanticRoleKindV0.SCOPE] = _resolved(
                SemanticRoleKindV0.SCOPE,
                _candidate(
                    "OBSIDIA",
                    obsidia,
                    evidence="brody-sens-v1:memory-scope",
                ),
                rationale="Obsidia constrains the memory object",
            )

    # Case C: direct Obsidia request with no memory relation.
    elif obsidia is not None:
        bindings[SemanticRoleKindV0.FOCUS] = _resolved(
            SemanticRoleKindV0.FOCUS,
            _candidate(
                "OBSIDIA",
                obsidia,
                evidence="brody-sens-v1:direct-project-focus",
            ),
            rationale="direct project/entity request",
        )

    else:
        return None

    if explain is not None:
        bindings[SemanticRoleKindV0.OPERATION] = _resolved(
            SemanticRoleKindV0.OPERATION,
            _candidate(
                "EXPLAIN",
                explain,
                evidence="brody-sens-v1:explicit-operation",
            ),
            rationale="explicit explanation operation",
        )
    elif knowledge is not None:
        bindings[SemanticRoleKindV0.OPERATION] = _resolved(
            SemanticRoleKindV0.OPERATION,
            _candidate(
                "RETRIEVE_KNOWLEDGE",
                knowledge,
                evidence="brody-sens-v1:knowledge-operation",
            ),
            rationale="explicit knowledge interrogation",
        )

    if detail is not None:
        bindings[SemanticRoleKindV0.QUALIFIER] = _resolved(
            SemanticRoleKindV0.QUALIFIER,
            _candidate(
                "DETAILED",
                detail,
                evidence="brody-sens-v1:explicit-qualifier",
            ),
            rationale="explicit detail qualifier",
        )

    return build_semantic_role_projection_v0(
        raw_utterance=raw,
        bindings=tuple(bindings[role] for role in SemanticRoleKindV0),
        source_refs=(
            "brody-sens:semantic-focus-v1",
            "historical-source:Jarvis-iron-obsidia-:0b91179d",
            rationale,
        ),
    )
