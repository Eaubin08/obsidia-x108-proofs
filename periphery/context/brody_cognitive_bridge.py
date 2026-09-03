"""
W3 — Brody cognitive enrichment bridge.

Composable: BrodyResponse -> ContextPacketV2 (additive, never overwrites).
Not a standalone pipeline. Does not call Brody provider/execution.
SIGNAL COGNITIF = CONTEXTE (W1 forensic verdict preserved).
"""
from __future__ import annotations

import dataclasses
import hashlib

from periphery.brody.brody_runtime_readonly import BrodyResponse
from periphery.context.context_packet_builder_v2 import ContextPacketV2

_PFX = "BRODY_COGNITIVE_BRIDGE"
_TYPE_ERR = f"{_PFX}:BRODY_RESPONSE_TYPE_REQUIRED"
_READONLY_ERR = f"{_PFX}:BRODY_READONLY_VIOLATED"
_EMITS_ACT_ERR = f"{_PFX}:BRODY_EMITS_ACT_VIOLATED"
_MEMORY_WRITE_ERR = f"{_PFX}:BRODY_MEMORY_WRITE_VIOLATED"
_QUERY_MISMATCH_ERR = f"{_PFX}:QUERY_MISMATCH"
_LANGUAGE_MISMATCH_ERR = f"{_PFX}:LANGUAGE_MISMATCH"
_FORBIDDEN_TOKENS = frozenset({
    "ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT",
    "AUTHORIZE", "APPROVE", "EXECUTE", "DEPLOY",
})


def _validate_brody_response(response: BrodyResponse) -> None:
    if not isinstance(response, BrodyResponse):
        raise TypeError(_TYPE_ERR)
    if not response.readonly:
        raise AssertionError(_READONLY_ERR)
    if response.emits_act:
        raise AssertionError(_EMITS_ACT_ERR)
    if response.memory_write:
        raise AssertionError(_MEMORY_WRITE_ERR)


def _sha16(ref: str) -> str:
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _forbidden_in(text: str) -> list[str]:
    found = []
    for word in text.split():
        w = word.strip(".,;:!?\"'").upper()
        if w in _FORBIDDEN_TOKENS:
            found.append(w)
    return found


def extract_brody_context_items(response: BrodyResponse) -> list[str]:
    _validate_brody_response(response)
    return [response.response_text]


def enrich_context_packet_v2_with_brody(
    context: ContextPacketV2,
    response: BrodyResponse,
) -> ContextPacketV2:
    """
    Additive enrichment: merges BrodyResponse into an existing ContextPacketV2.

    Preserved unchanged: dominant_trees, memory_status, risk_flags, unknowns,
    contradictions, query, language, and all governance invariants.
    Fail-closed on any governance violation or query/language mismatch.
    """
    _validate_brody_response(response)
    expected_query = context.query[:500]
    if response.query != expected_query:
        raise ValueError(
            f"{_QUERY_MISMATCH_ERR}: "
            f"response.query={response.query!r} vs context.query[:500]={expected_query!r}"
        )
    if response.language != context.language:
        raise ValueError(
            f"{_LANGUAGE_MISMATCH_ERR}: "
            f"response.language={response.language!r} vs context.language={context.language!r}"
        )
    new_context_items = list(context.context_items)
    if response.response_text not in new_context_items:
        new_context_items.append(response.response_text)
    existing_refs = set(context.source_refs)
    new_refs = [r for r in response.context_refs if r not in existing_refs]
    new_source_refs = list(context.source_refs) + new_refs
    new_source_hashes = list(context.source_hashes) + [_sha16(r) for r in new_refs]
    new_forbidden = list(set(context.forbidden_tokens_detected) | set(_forbidden_in(response.response_text)))
    return dataclasses.replace(
        context,
        context_items=new_context_items,
        source_refs=new_source_refs,
        source_hashes=new_source_hashes,
        forbidden_tokens_detected=new_forbidden,
    )


__all__ = [
    "extract_brody_context_items",
    "enrich_context_packet_v2_with_brody",
]
