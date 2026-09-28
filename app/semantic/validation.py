"""SemanticCandidateValidator — runtime-side candidate gate.

One authority for deciding whether a locally produced candidate answer is
safe to close. Non-emptiness is never sufficient. Fixture-specific expected
answers stay in tests/graders; this validator only checks structural,
linguistic and derivational properties available at runtime.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


_FR_MARKERS = re.compile(
    r"[àâäéèêëîïôùûüçœ]|"
    r"\b(le|la|les|une|des|est|sont|dans|avec|pour|cette|ces)\b")


@dataclass
class ValidationResult:
    instruction_pass: bool = True
    semantic_pass: bool = True
    format_pass: bool = True
    english_pass: bool = True
    contradiction_free: bool = True
    unknowns_remaining: tuple[str, ...] = ()
    closure_safe: bool = True
    failure_reasons: list[str] = field(default_factory=list)


def validate_candidate(
    answer: str,
    *,
    sentence_count: int | None = None,
    allowed_labels: tuple[str, ...] | None = None,
    derivation_present: bool = True,
    unknowns: tuple[str, ...] = (),
    contradictions: tuple[str, ...] = (),
) -> ValidationResult:
    r = ValidationResult()

    if not answer or not answer.strip():
        r.format_pass = False
        r.failure_reasons.append("empty_candidate")

    if answer and _FR_MARKERS.search(answer):
        r.english_pass = False
        r.failure_reasons.append("non_english_markers")

    if sentence_count is not None and answer:
        n = len(re.findall(r"[.!?](?:\s|$)", answer.strip()))
        if n != sentence_count:
            r.instruction_pass = False
            r.failure_reasons.append(
                f"sentence_count_mismatch:{n}!={sentence_count}")

    if allowed_labels and answer:
        low = answer.strip().lower()
        if not any(low.startswith(l) for l in allowed_labels):
            r.instruction_pass = False
            r.failure_reasons.append("label_not_in_allowed_set")

    if not derivation_present:
        r.semantic_pass = False
        r.failure_reasons.append("no_derivation")

    if contradictions:
        r.contradiction_free = False
        r.failure_reasons.extend(f"contradiction:{c}" for c in contradictions)

    r.unknowns_remaining = tuple(unknowns)
    r.closure_safe = (r.instruction_pass and r.semantic_pass and r.format_pass
                      and r.english_pass and r.contradiction_free
                      and not unknowns)
    return r
