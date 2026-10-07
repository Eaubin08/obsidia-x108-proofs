"""Common primitives for SOURCE_RUNTIME_NATIVE_V0."""
from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

DECISION_AUTHORITY = "KX108_ONLY"

SOURCE_MAILBOX = "MAILBOX"
SOURCE_DOCUMENT_REPOSITORY = "DOCUMENT_REPOSITORY"
SOURCE_CALENDAR = "CALENDAR"
SOURCE_FORM_INBOX = "FORM_INBOX"
SOURCE_API_READONLY = "API_READONLY"

SOURCE_KINDS = {
    SOURCE_MAILBOX,
    SOURCE_DOCUMENT_REPOSITORY,
    SOURCE_CALENDAR,
    SOURCE_FORM_INBOX,
    SOURCE_API_READONLY,
}

READONLY_CAPABILITIES = {
    "LIST",
    "SEARCH",
    "READ_MESSAGE",
    "READ_THREAD",
    "READ_ATTACHMENT",
    "READ_DOCUMENT",
    "READ_FILE_METADATA",
    "READ_EVENT",
    "READ_FORM_RESPONSE",
    "READ_API_RESOURCE",
}

WRITE_LIKE_FRAGMENTS = (
    "WRITE",
    "SEND",
    "CREATE",
    "UPDATE",
    "DELETE",
    "TRASH",
    "ARCHIVE",
    "MOVE",
    "REPLY",
    "FORWARD",
    "UPLOAD",
    "MUTATE",
    "EXECUTE",
)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_time(value: str) -> str:
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("NATIVE_SOURCE_TIME_MUST_BE_TIMEZONE_AWARE")
    return value


def validate_readonly_capabilities(
    capabilities: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    normalized = tuple(sorted(set(str(x) for x in capabilities)))
    if not normalized:
        raise ValueError("NATIVE_SOURCE_CAPABILITIES_REQUIRED")
    for capability in normalized:
        upper = capability.upper()
        if any(fragment in upper for fragment in WRITE_LIKE_FRAGMENTS):
            raise ValueError(
                f"NATIVE_SOURCE_WRITE_CAPABILITY_FORBIDDEN:{capability}"
            )
        if capability not in READONLY_CAPABILITIES:
            raise ValueError(
                f"NATIVE_SOURCE_CAPABILITY_UNSUPPORTED:{capability}"
            )
    return normalized
