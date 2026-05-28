from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .constants import (
    DECISION_AUTHORITY,
    FORBIDDEN_DECISION_TOKENS,
    FORBIDDEN_OUTPUT_FIELDS,
    READONLY_FLAGS,
)


class BoundaryViolation(ValueError):
    """Raised when an output attempts to cross the readonly/KX108 boundary."""


def assert_boundary_flags(payload: Dict[str, Any]) -> None:
    """Validate the mandatory readonly boundary flags recursively at top-level boundary blocks."""
    boundary = payload.get("boundary", {})
    if not isinstance(boundary, dict):
        raise BoundaryViolation("boundary must be a dict")

    if boundary.get("decision_authority") != DECISION_AUTHORITY:
        raise BoundaryViolation("decision_authority must be KX108_ONLY")

    for key, expected in READONLY_FLAGS.items():
        if boundary.get(key) != expected:
            raise BoundaryViolation(f"boundary.{key} must be {expected!r}")


def scan_forbidden_fields(payload: Any, path: str = "$") -> List[str]:
    hits: List[str] = []
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k in FORBIDDEN_OUTPUT_FIELDS:
                hits.append(f"{path}.{k}")
            hits.extend(scan_forbidden_fields(v, f"{path}.{k}"))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            hits.extend(scan_forbidden_fields(item, f"{path}[{i}]"))
    return hits


def scan_forbidden_decision_tokens(payload: Any) -> List[str]:
    """Scan string leaves for exact forbidden decision tokens.

    This intentionally uses token boundaries so words like 'interaction' are not
    treated as an ACT signal.
    """
    import re

    hits: List[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for item in x:
                walk(item)
        elif isinstance(x, str):
            for token in FORBIDDEN_DECISION_TOKENS:
                if re.search(rf"\b{re.escape(token)}\b", x):
                    hits.append(token)

    walk(payload)
    return sorted(set(hits))


def assert_no_forbidden_fields(payload: Any) -> None:
    hits = scan_forbidden_fields(payload)
    if hits:
        raise BoundaryViolation(f"forbidden fields present: {hits}")


def validate_readonly_output(payload: Dict[str, Any], allow_descriptive_tokens: bool = True) -> Dict[str, Any]:
    """Validate a generated object as readonly.

    By default, forbidden decision tokens are allowed in documentation fields
    because this package must document X108 boundaries. Runtime payloads should
    call this with allow_descriptive_tokens=False.
    """
    assert_boundary_flags(payload)
    assert_no_forbidden_fields(payload)
    if not allow_descriptive_tokens:
        hits = scan_forbidden_decision_tokens(payload)
        if hits:
            raise BoundaryViolation(f"forbidden decision tokens in runtime payload: {hits}")
    return {
        "boundary_check_ok": True,
        "decision_authority": DECISION_AUTHORITY,
        "forbidden_field_hits": [],
    }
