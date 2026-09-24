"""RemoteOutputValidator — a deliberately lighter validation profile for
Fireworks answers than the local CandidateValidator.

A general remote answer does not carry a local derivation, a unique-solution
proof or a semantic signature — requiring those would reject every genuine
remote answer. The remote validator only checks what is actually knowable
without local proof: non-emptiness, language, and any output constraint the
prompt explicitly stated (label set, sentence count, code-only, JSON).
"""
from __future__ import annotations

import json
import re

_FR_MARKERS = re.compile(
    r"[àâäéèêëîïôùûüçœ]|"
    r"\b(le|la|les|une|des|est|sont|dans|avec|pour|cette|ces)\b")


def validate_remote_output(
    text: str,
    *,
    allowed_labels: tuple[str, ...] | None = None,
    sentence_count: int | None = None,
    code_only: bool = False,
    json_required: bool = False,
) -> tuple[bool, list[str]]:
    """Return (remote_valid, failure_reasons). Deliberately lenient: does
    not require a derivation, a certificate or a unique-solution proof —
    those are local-only concepts."""
    reasons: list[str] = []
    text = text or ""

    if not text.strip():
        reasons.append("empty_remote_answer")
        return False, reasons
    if "[dry-run]" in text or text.startswith("[error]"):
        reasons.append("dry_run_or_transport_error")
        return False, reasons
    if _FR_MARKERS.search(text):
        reasons.append("non_english_markers")

    if allowed_labels:
        low = text.strip().lower()
        matched = [l for l in allowed_labels
                  if re.search(rf"\b{re.escape(l)}\b", low)]
        if not any(low.startswith(l) for l in allowed_labels):
            reasons.append("label_not_in_allowed_set")
        elif len(set(matched)) > 1 and "mixed" not in allowed_labels:
            # Two distinct allowed labels both present ("positive and
            # negative at once") is contradictory unless the prompt itself
            # explicitly permits a combined/mixed label.
            reasons.append("contradictory_labels")

    if sentence_count is not None:
        n = len(re.findall(r"[.!?](?:\s|$)", text.strip()))
        if n != sentence_count:
            reasons.append(f"sentence_count_mismatch:{n}!={sentence_count}")

    if code_only:
        stripped = text.strip()
        if not (stripped.startswith("def ") or stripped.startswith("class ")):
            reasons.append("code_only_violated")

    if json_required:
        try:
            json.loads(text.strip())
        except Exception:
            reasons.append("invalid_json")

    return (not reasons), reasons
