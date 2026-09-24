"""Bounded, deterministic remote-output repair (no second model call).

Only mechanical, meaning-preserving transformations are allowed: trimming,
stripping a short preamble, extracting a single fenced code block or a
single JSON object/array, normalizing label casing, dropping a duplicated
terminal punctuation, or keeping only the first sentence/a numeric value
when the contract explicitly asked for exactly that.

Never invents content, never completes missing JSON fields, never guesses
a label, never truncates a complex answer arbitrarily, never calls a model.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

MAX_REPAIR_STEPS = 4

_PREAMBLE_RE = re.compile(
    r"^(?:here\s+is\s+the\s+answer:?|here'?s\s+the\s+answer:?|"
    r"sure,?\s+here\s+is:?|the\s+answer\s+is:?|answer:?)\s*", re.IGNORECASE)
_CODE_FENCE_RE = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)
_JSON_OBJ_RE = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


@dataclass
class RepairResult:
    original: str
    repaired: str
    repair_applied: bool = False
    repair_operations: list[str] = field(default_factory=list)
    repair_safe: bool = True


def repair_remote_output(
    raw_answer: str,
    *,
    code_only: bool = False,
    json_required: bool = False,
    allowed_labels: tuple[str, ...] | None = None,
    sentence_count: int | None = None,
    numeric_only: bool = False,
) -> RepairResult:
    text = raw_answer or ""
    ops: list[str] = []
    steps = 0

    stripped = text.strip()
    if stripped != text:
        ops.append("trim_whitespace")
        text = stripped
        steps += 1

    if steps < MAX_REPAIR_STEPS:
        m = _PREAMBLE_RE.match(text)
        if m:
            text = text[m.end():].strip()
            ops.append("strip_preamble")
            steps += 1

    if code_only and steps < MAX_REPAIR_STEPS:
        m = _CODE_FENCE_RE.search(text)
        if m:
            text = m.group(1).strip()
            ops.append("extract_code_fence")
            steps += 1

    if json_required and steps < MAX_REPAIR_STEPS:
        try:
            json.loads(text)
        except Exception:
            m = _JSON_OBJ_RE.search(text)
            if m:
                candidate = m.group(0)
                try:
                    json.loads(candidate)
                    text = candidate
                    ops.append("extract_json_object")
                    steps += 1
                except Exception:
                    pass  # not safely repairable: leave as-is, let validator reject

    if allowed_labels and steps < MAX_REPAIR_STEPS:
        low = text.strip().lower()
        for label in allowed_labels:
            if low.startswith(label):
                if not text.startswith(label):
                    text = label + text[len(label):]
                    ops.append("normalize_label_casing")
                    steps += 1
                break

    if sentence_count == 1 and steps < MAX_REPAIR_STEPS:
        sentences = _SENTENCE_SPLIT_RE.split(text.strip())
        if len(sentences) > 1:
            text = sentences[0].strip()
            ops.append("keep_first_sentence_only")
            steps += 1

    if numeric_only and steps < MAX_REPAIR_STEPS:
        m = re.search(r"-?\d+(?:\.\d+)?", text)
        if m and text.strip() != m.group(0):
            text = m.group(0)
            ops.append("extract_numeric_value")
            steps += 1

    return RepairResult(
        original=raw_answer or "",
        repaired=text,
        repair_applied=bool(ops),
        repair_operations=ops,
        repair_safe=True,
    )
