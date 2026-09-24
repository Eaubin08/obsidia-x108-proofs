"""Generic output-constraint representation and parser (Phase 5).

OutputConstraints is derived from prompt text signals only — never from
task_id. It is shared by the strict grader V2 (benchmarks/practice_grader_v2)
and can inform local-solver candidate validation without leaking fixture-
specific expected answers into runtime code.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutputConstraints:
    required_language: str = "en"
    allowed_labels: tuple[str, ...] | None = None
    sentence_count: int | None = None
    bullet_count: int | None = None
    max_words_per_bullet: int | None = None
    required_entity_types: tuple[str, ...] = ()
    code_only: bool = False
    explanation_required: bool = False


_SENTENCE_COUNT_WORDS = {"one": 1, "1": 1, "two": 2, "2": 2, "three": 3, "3": 3}
_BULLET_COUNT_WORDS = {"one": 1, "1": 1, "two": 2, "2": 2, "three": 3, "3": 3,
                        "four": 4, "4": 4, "five": 5, "5": 5}

_SENTENCE_COUNT_RE = re.compile(
    r"\b(one|two|three|1|2|3)\s+sentences?\b", re.I)
_BULLET_COUNT_RE = re.compile(
    r"\b(one|two|three|four|five|1|2|3|4|5)\s+bullets?\b|"
    r"\bbullets?\s*:?\s*(one|two|three|four|five|1|2|3|4|5)\b|"
    r"\b(one|two|three|four|five|1|2|3|4|5)\s+bullet\s+points?\b", re.I)
_MAX_WORDS_PER_BULLET_RE = re.compile(
    r"\b(?:no\s+more\s+than|at\s+most|max(?:imum)?\s+of?)\s+(\d+|one|two|three|"
    r"four|five|six|seven|eight|nine|ten|fifteen|twenty)\s+words?\b", re.I)
_WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "fifteen": 15,
             "twenty": 20}
_LABEL_SET_RE = re.compile(
    r"\bas\s+([a-z]+(?:\s*,\s*[a-z]+)*\s*,?\s*(?:or|and)\s+[a-z]+)\b", re.I)
_ENTITY_TYPE_RE = re.compile(
    r"\b(PERSON|ORGANIZATION|LOCATION|DATE|people|organizations?|locations?|"
    r"dates?)\b", re.I)
_ENTITY_TYPE_MAP = {
    "person": "PERSON", "people": "PERSON",
    "organization": "ORGANIZATION", "organizations": "ORGANIZATION",
    "location": "LOCATION", "locations": "LOCATION",
    "date": "DATE", "dates": "DATE",
}
_CODE_ONLY_RE = re.compile(r"\bcode\s+only\b|\bonly\s+code\b", re.I)
_EXPLANATION_RE = re.compile(
    r"\bexplain\b|\bjustif(?:y|ication)\b|\bbriefly\s+explain\b|"
    r"\breasoning\b|\bwhy\b", re.I)


def _to_int(token: str, table: dict[str, int]) -> int | None:
    return table.get(token.lower())


def parse_output_constraints(prompt: str) -> OutputConstraints:
    """Derive OutputConstraints from prompt text signals only."""
    sentence_count = None
    m = _SENTENCE_COUNT_RE.search(prompt)
    if m:
        sentence_count = _to_int(m.group(1), _SENTENCE_COUNT_WORDS)

    bullet_count = None
    m = _BULLET_COUNT_RE.search(prompt)
    if m:
        token = next(g for g in m.groups() if g)
        bullet_count = _to_int(token, _BULLET_COUNT_WORDS)

    max_words_per_bullet = None
    m = _MAX_WORDS_PER_BULLET_RE.search(prompt)
    if m:
        token = m.group(1)
        max_words_per_bullet = int(token) if token.isdigit() else _WORD_NUM.get(token.lower())

    allowed_labels = None
    m = _LABEL_SET_RE.search(prompt)
    if m:
        parts = re.split(r",|\bor\b|\band\b", m.group(1), flags=re.I)
        known = {"positive", "negative", "neutral", "mixed"}
        labels = tuple(p.strip().lower() for p in parts if p.strip().lower() in known)
        allowed_labels = labels or None

    entity_types: tuple[str, ...] = ()
    if re.search(r"\bentit(?:y|ies)\b", prompt, re.I):
        found = []
        for raw in _ENTITY_TYPE_RE.findall(prompt):
            mapped = _ENTITY_TYPE_MAP.get(raw.lower())
            if mapped and mapped not in found:
                found.append(mapped)
        if not found:
            found = ["PERSON", "ORGANIZATION", "LOCATION"]
        entity_types = tuple(found)

    code_only = bool(_CODE_ONLY_RE.search(prompt))
    explanation_required = bool(_EXPLANATION_RE.search(prompt))

    return OutputConstraints(
        required_language="en",
        allowed_labels=allowed_labels,
        sentence_count=sentence_count,
        bullet_count=bullet_count,
        max_words_per_bullet=max_words_per_bullet,
        required_entity_types=entity_types,
        code_only=code_only,
        explanation_required=explanation_required,
    )
