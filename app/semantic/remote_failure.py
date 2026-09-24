"""Canonical remote-call failure classification and retry eligibility.

One authority for deciding WHY a remote call did not produce a projectable
answer, and whether a single bounded retry is allowed. Never reduces every
failure to a generic "[error]" bucket.
"""
from __future__ import annotations

from enum import Enum


class RemoteFailureReason(str, Enum):
    REMOTE_VALID = "REMOTE_VALID"
    REMOTE_EMPTY_CONTENT = "REMOTE_EMPTY_CONTENT"
    REMOTE_NO_FINAL_CONTENT = "REMOTE_NO_FINAL_CONTENT"
    REMOTE_LENGTH_EXHAUSTED = "REMOTE_LENGTH_EXHAUSTED"
    REMOTE_PARSE_ERROR = "REMOTE_PARSE_ERROR"
    REMOTE_TRANSPORT_ERROR = "REMOTE_TRANSPORT_ERROR"
    REMOTE_TIMEOUT = "REMOTE_TIMEOUT"
    REMOTE_FORMAT_INVALID = "REMOTE_FORMAT_INVALID"
    REMOTE_SEMANTIC_INVALID = "REMOTE_SEMANTIC_INVALID"


# Only these two justify spending a second bounded call: the model was
# reachable and produced no usable visible content, or exhausted its
# budget before emitting one. Everything else (bad format that is not a
# parse failure, semantic mismatch, transport failure, timeout) is not
# retried — retrying a semantically wrong or malformed-but-parseable
# answer would not fix the actual defect.
RETRYABLE_REASONS = frozenset({
    RemoteFailureReason.REMOTE_NO_FINAL_CONTENT,
    RemoteFailureReason.REMOTE_LENGTH_EXHAUSTED,
})


def classify_remote_failure(fw_response: dict) -> RemoteFailureReason:
    """Classify a raw fireworks.chat() response dict into a canonical
    reason. Never inspects reasoning_content text itself, only booleans/
    counts already computed by the adapter."""
    if fw_response.get("dry_run"):
        return RemoteFailureReason.REMOTE_EMPTY_CONTENT
    err = fw_response.get("error")
    if err and str(err).startswith("HTTP"):
        return RemoteFailureReason.REMOTE_TRANSPORT_ERROR
    if err and "network" in str(err):
        return RemoteFailureReason.REMOTE_TRANSPORT_ERROR
    if err == "timeout":
        return RemoteFailureReason.REMOTE_TIMEOUT

    final_present = fw_response.get("final_content_present", False)
    truncated = fw_response.get("truncated", False)

    if not final_present:
        if truncated:
            return RemoteFailureReason.REMOTE_LENGTH_EXHAUSTED
        # The adapter (app.adapters.fireworks.chat) always renders a
        # "[error] no final answer content" placeholder text for this
        # case, so the placeholder text can never distinguish a genuine
        # parse failure from ordinary no-content — rely on the adapter's
        # own response_error classification instead.
        if err == "no_final_content" or err is None:
            return RemoteFailureReason.REMOTE_NO_FINAL_CONTENT
        return RemoteFailureReason.REMOTE_PARSE_ERROR
    if truncated:
        return RemoteFailureReason.REMOTE_LENGTH_EXHAUSTED
    return RemoteFailureReason.REMOTE_VALID


def is_retryable(reason: RemoteFailureReason) -> bool:
    return reason in RETRYABLE_REASONS
