"""
W4 — Memory cognitive enrichment bridge.

Composable: MemoryCandidate -> ContextPacketV2 (additive, never overwrites).
Not a standalone pipeline. No Graphiti. No memory_status mapping. No unknowns/contradictions.
SIGNAL COGNITIF = CONTEXTE (W1 forensic verdict preserved).
"""
from __future__ import annotations

import dataclasses
import hashlib

from periphery.memory.memory_candidate import MemoryCandidate
from periphery.context.context_packet_builder_v2 import ContextPacketV2

_PFX = "MEMORY_COGNITIVE_BRIDGE"
_TYPE_ERR = f"{_PFX}:MEMORY_CANDIDATE_TYPE_REQUIRED"
_MEMORY_WRITE_ERR = f"{_PFX}:MEMORY_WRITE_ALLOWED_VIOLATED"
_AUTO_PROMOTION_ERR = f"{_PFX}:AUTO_PROMOTION_ALLOWED_VIOLATED"

_FORBIDDEN_TOKENS = frozenset({
    "ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT",
    "AUTHORIZE", "APPROVE", "EXECUTE", "DEPLOY",
})


def _validate_memory_candidate(candidate: MemoryCandidate) -> None:
    if not isinstance(candidate, MemoryCandidate):
        raise TypeError(_TYPE_ERR)
    if candidate.memory_write_allowed:
        raise AssertionError(_MEMORY_WRITE_ERR)
    if candidate.auto_promotion_allowed:
        raise AssertionError(_AUTO_PROMOTION_ERR)


def _sha16(ref: str) -> str:
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _forbidden_in(text: str) -> list[str]:
    found = []
    for word in text.split():
        w = word.strip(".,;:!?\"'").upper()
        if w in _FORBIDDEN_TOKENS:
            found.append(w)
    return found


def extract_memory_context_items(candidate: MemoryCandidate) -> list[str]:
    _validate_memory_candidate(candidate)
    return [candidate.content_summary]


def enrich_context_packet_v2_with_memory(
    context: ContextPacketV2,
    candidate: MemoryCandidate,
) -> ContextPacketV2:
    """
    Additive enrichment: merges MemoryCandidate into an existing ContextPacketV2.

    Preserved unchanged: dominant_trees, memory_status, unknowns, contradictions,
    query, language, and all governance invariants.
    source_hashes[i] = sha256(source_refs[i])[:16] — convention canonique (W3/builder).
    Fail-closed on memory_write_allowed=True or auto_promotion_allowed=True.
    """
    _validate_memory_candidate(candidate)
    new_context_items = list(context.context_items)
    if candidate.content_summary not in new_context_items:
        new_context_items.append(candidate.content_summary)
    existing_refs = set(context.source_refs)
    new_refs = [candidate.source_id] if candidate.source_id not in existing_refs else []
    new_source_refs = list(context.source_refs) + new_refs
    new_source_hashes = list(context.source_hashes) + [_sha16(r) for r in new_refs]
    new_risk_flags = list(dict.fromkeys(list(context.risk_flags) + list(candidate.risk_flags)))
    new_forbidden = list(set(context.forbidden_tokens_detected) | set(_forbidden_in(candidate.content_summary)))
    return dataclasses.replace(
        context,
        context_items=new_context_items,
        source_refs=new_source_refs,
        source_hashes=new_source_hashes,
        risk_flags=new_risk_flags,
        forbidden_tokens_detected=new_forbidden,
    )


__all__ = [
    "extract_memory_context_items",
    "enrich_context_packet_v2_with_memory",
]
