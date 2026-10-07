"""Local strict canonical JSON and full SHA-256 identities (spec §3, §5).

Reproduces the B6 canonical form (sorted keys, compact separators, UTF-8 text, finite numbers, string
keys, no coercion) byte for byte, without importing B6 from production.
"""
from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from typing import Any, Iterable

from app.knowledge.b8.contracts import ClaimClass, MalformedSlot


def _check_json(value: Any, path: str, active: set[int]) -> None:
    if value is None or isinstance(value, (bool, str, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite float at {path}")
        return
    if isinstance(value, (list, tuple, dict)):
        if id(value) in active:
            raise ValueError(f"recursive container at {path}")
        active.add(id(value))
        try:
            if isinstance(value, dict):
                for k, v in value.items():
                    if not isinstance(k, str):
                        raise ValueError(f"non-string mapping key at {path}")
                    _check_json(v, f"{path}.{k}", active)
            else:
                for i, v in enumerate(value):
                    _check_json(v, f"{path}[{i}]", active)
        finally:
            active.discard(id(value))
        return
    raise ValueError(f"non-JSON value of type {type(value).__name__} at {path}")


def canonical_json(value: Any) -> str:
    """Strict JSON (finite numbers, string keys, no cycles, no coercion), sorted keys."""
    _check_json(value, "$", set())
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def full_identity(prefix: str, value: Any) -> str:
    """prefix + full 64-hex SHA-256 over canonical JSON (no truncation)."""
    return prefix + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedSlot("slot component must be a non-empty, non-whitespace string")
    return unicodedata.normalize("NFC", value)


def _ref_set(refs: Iterable[Any]) -> list[str]:
    if isinstance(refs, (str, bytes)):
        raise MalformedSlot("slot ref collection must not be a bare string")
    return sorted({_text(r) for r in refs})


def knowledge_slot_id(claim_class: Any, domain_id: Any, subject_refs: Iterable[Any],
                      context_refs: Iterable[Any], predicate_ref: Any) -> str:
    """b8slot_ + SHA-256(canonical_json([claim_class, domain_id, subject_set, context_set, predicate_ref]))."""
    try:
        cls = ClaimClass(claim_class.value if isinstance(claim_class, ClaimClass) else claim_class).value
    except ValueError:
        raise MalformedSlot("unknown claim_class") from None
    subjects = _ref_set(subject_refs)
    if not subjects:
        raise MalformedSlot("subject_refs must not be empty")
    payload = [cls, _text(domain_id), subjects, _ref_set(context_refs), _text(predicate_ref)]
    return full_identity("b8slot_", payload)
