"""B6 query-aware projection: query + working state -> bounded, recorded selection.

Pure and deterministic (no model, no network, no mutation). Every entry ends up either
included (with its exposure and reason) or omitted (with its reason): nothing disappears.
UNKNOWN_RELEVANCE != IRRELEVANT: an entry that cannot be matched is kept (SHORT); an
UNKNOWN / ERROR / OPEN entry is always exposed unless explicitly hidden.

Canonical order (R4): entries are considered in state_id order (insertion order never matters);
included / omitted are SET_LIKE_CANONICALIZED by state_id. Hard bounds (R3): a query longer
than MAX_QUERY_CHARS fails closed; at most MAX_STATE_ENTRIES are considered, the rest are
omitted with reason ENTRY_LIMIT (UNKNOWN / ERROR included: their omission is explicit).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from app.harness.state_explicit.contracts import (MAX_QUERY_CHARS, MAX_STATE_ENTRIES, ContextBoundError, StateEntry,
                                                  StateStatus, Visibility)

_WORD = re.compile(r"[^\W_]+", re.UNICODE)


class Relevance(str, Enum):
    RELEVANT = "RELEVANT"
    UNKNOWN_RELEVANCE = "UNKNOWN_RELEVANCE"
    IRRELEVANT = "IRRELEVANT"


def tokens(text: str) -> frozenset[str]:
    norm = unicodedata.normalize("NFC", str(text or "")).lower()
    return frozenset(w for w in _WORD.findall(norm) if len(w) >= 2)


@dataclass(frozen=True)
class Included:
    state_id: str
    relevance: Relevance
    exposure: Visibility
    reason: str


@dataclass(frozen=True)
class Omitted:
    state_id: str
    reason: str


@dataclass(frozen=True)
class ProjectedState:
    query: str
    query_tokens: tuple[str, ...]
    included: tuple[Included, ...]
    omitted: tuple[Omitted, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"query_tokens": list(self.query_tokens),
                "included": [{"state_id": i.state_id, "relevance": i.relevance.value,
                              "exposure": i.exposure.value, "reason": i.reason} for i in self.included],
                "omitted": [{"state_id": o.state_id, "reason": o.reason} for o in self.omitted]}


def _cap(level: Visibility, cap: Visibility) -> Visibility:
    order = [Visibility.HIDE, Visibility.SHORT, Visibility.LONG, Visibility.FULL]
    return min(level, cap, key=order.index)


def check_query(query: str) -> str:
    query = str(query or "")
    if len(query) > MAX_QUERY_CHARS:
        raise ContextBoundError(f"query exceeds {MAX_QUERY_CHARS} chars ({len(query)})")
    return query


def project_entries(query: str, entries: Iterable[StateEntry]) -> ProjectedState:
    query = check_query(query)
    q = tokens(query)
    included: list[Included] = []
    omitted: list[Omitted] = []
    ordered = sorted(entries, key=lambda e: e.state_id)
    omitted += [Omitted(e.state_id, "ENTRY_LIMIT") for e in ordered[MAX_STATE_ENTRIES:]]
    for e in ordered[:MAX_STATE_ENTRIES]:
        if e.visibility == Visibility.HIDE:
            omitted.append(Omitted(e.state_id, "visibility_hide"))
            continue
        if e.status != StateStatus.KNOWN:
            included.append(Included(e.state_id, Relevance.RELEVANT if q & set(e.tags) else
                                     Relevance.UNKNOWN_RELEVANCE, e.visibility,
                                     "unresolved_state_always_exposed"))
            continue
        keys = set(e.tags)
        if not keys:
            included.append(Included(e.state_id, Relevance.UNKNOWN_RELEVANCE,
                                     _cap(e.visibility, Visibility.SHORT), "no_relevance_keys"))
        elif q & keys:
            included.append(Included(e.state_id, Relevance.RELEVANT, e.visibility, "tag_match"))
        else:
            omitted.append(Omitted(e.state_id, "irrelevant_to_query"))
    return ProjectedState(query=query, query_tokens=tuple(sorted(q)),
                          included=tuple(sorted(included, key=lambda i: i.state_id)),
                          omitted=tuple(sorted(omitted, key=lambda o: (o.state_id, o.reason))))


def project(query: str, registry) -> ProjectedState:
    return project_entries(query, registry.list_entries())
