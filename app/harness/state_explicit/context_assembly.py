"""B6 context assembly: query -> projection -> visibility -> instructions -> capabilities -> packet.

The ContextPacket is explicit, immutable, serializable and replayable: its packet_id is a
digest of its own canonical strict JSON (same input set -> same packet, whatever the insertion
order). ORDERED_SEMANTICS: none at packet level. SET_LIKE_CANONICALIZED: state / included /
omitted / unknowns (state_id), instructions (instruction_id), provenance_refs and capability
categories (sorted). Hard bound: the canonical packet never exceeds MAX_PACKET_BYTES (overflow
reduced to SHORT, then omitted as PACKET_SIZE_LIMIT, all recorded; fail closed otherwise).
No cognition, judging or truth resolution happens here; the caller's registry is never modified.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from app.harness.state_explicit.capabilities import DisclosureLevel, disclose, load_capability_matrix
from app.harness.state_explicit.contracts import (BOUNDARY, MAX_PACKET_BYTES, ContextBoundError, StateEntry,
                                                  StateStatus, Visibility, canonical_json, render_entry)
from app.harness.state_explicit.instructions import (DEFAULT_INSTRUCTIONS, Instruction, activation_tags,
                                                     select_instructions)
from app.harness.state_explicit.projection import Included, Omitted, project_entries
from app.harness.state_explicit.registry import DuplicateStateError

PACKET_SCHEMA = "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1"


@dataclass(frozen=True)
class ContextPacket:
    packet_id: str
    query: str
    projection: Mapping[str, Any]
    state: tuple[Mapping[str, Any], ...]
    instructions: tuple[Mapping[str, Any], ...]
    capabilities: Mapping[str, Any]
    provenance_refs: tuple[str, ...]
    unknowns: tuple[Mapping[str, Any], ...]
    omitted: tuple[Mapping[str, Any], ...]
    boundary: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self.to_json())

    def to_json(self) -> str:
        return canonical_json(_plain({"schema": PACKET_SCHEMA, "packet_id": self.packet_id, "query": self.query,
                                  "projection": self.projection, "state": self.state,
                                  "instructions": self.instructions, "capabilities": self.capabilities,
                                  "provenance_refs": self.provenance_refs, "unknowns": self.unknowns,
                                  "omitted": self.omitted, "boundary": self.boundary}))


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def assemble_context(query: str, registry, *, instructions: tuple[Instruction, ...] = DEFAULT_INSTRUCTIONS,
                     capability_matrix: Mapping[str, Any] | None = None,
                     capability_level: DisclosureLevel = DisclosureLevel.CATEGORY,
                     memory_entries: Iterable[StateEntry] = ()) -> ContextPacket:
    entries = [*registry.list_entries(), *memory_entries]
    by_id: dict[str, StateEntry] = {}
    for e in entries:
        if e.state_id in by_id:
            raise DuplicateStateError(f"state_id supplied twice: {e.state_id}")   # never a silent overwrite
        by_id[e.state_id] = e
    projection = project_entries(query, entries)
    over = {o.state_id for o in projection.omitted if o.reason == "ENTRY_LIMIT"}
    considered = [by_id[k] for k in sorted(by_id) if k not in over]
    chosen = select_instructions(activation_tags(considered), instructions)
    matrix = capability_matrix if capability_matrix is not None else load_capability_matrix()
    capabilities = disclose(matrix, capability_level)
    unknowns = [{"state_id": e.state_id, "status": e.status.value, "uncertainty": list(e.uncertainty)}
                for e in considered if e.status != StateStatus.KNOWN]
    included = list(projection.included)
    omitted = list(projection.omitted)

    def body() -> dict[str, Any]:
        exposed = [by_id[i.state_id] for i in included]
        proj = {"query_tokens": list(projection.query_tokens),
                "included": [{"state_id": i.state_id, "relevance": i.relevance.value, "exposure": i.exposure.value,
                              "reason": i.reason} for i in included],
                "omitted": [{"state_id": o.state_id, "reason": o.reason}
                            for o in sorted(omitted, key=lambda o: (o.state_id, o.reason))]}
        return {"query": projection.query, "projection": proj,
                "state": [render_entry(by_id[i.state_id], i.exposure) for i in included],
                "instructions": [i.to_dict() for i in chosen], "capabilities": capabilities,
                "provenance_refs": sorted({p for e in exposed for p in (e.source_ref, *e.provenance)}),
                "unknowns": unknowns, "omitted": proj["omitted"], "boundary": dict(BOUNDARY)}

    # R3: the canonical packet must fit MAX_PACKET_BYTES; reduce only through the visibility /
    # omission mechanism (largest exposed state first, then by state_id), each step recorded
    while True:
        current = body()
        text = canonical_json({"schema": PACKET_SCHEMA, "packet_id": "b6ctx_" + "0" * 16, **current})
        if len(text.encode("utf-8")) <= MAX_PACKET_BYTES:
            break
        sizes = {i.state_id: len(canonical_json(s)) for i, s in zip(included, current["state"])}
        reducible = [i for i in included if i.exposure != Visibility.SHORT]
        if reducible:
            victim = max(reducible, key=lambda i: (sizes[i.state_id], i.state_id))
            included[included.index(victim)] = Included(victim.state_id, victim.relevance, Visibility.SHORT,
                                                        "PACKET_SIZE_LIMIT:reduced_to_SHORT")
        elif included:
            victim = max(included, key=lambda i: (sizes[i.state_id], i.state_id))
            included.remove(victim)
            omitted.append(Omitted(victim.state_id, "PACKET_SIZE_LIMIT"))
        else:
            raise ContextBoundError("mandatory packet metadata alone exceeds MAX_PACKET_BYTES")
    digest = hashlib.sha256(canonical_json(current).encode("utf-8")).hexdigest()
    return ContextPacket(packet_id=f"b6ctx_{digest[:16]}", query=current["query"],
                         projection=_freeze(current["projection"]), state=_freeze(current["state"]),
                         instructions=_freeze(current["instructions"]), capabilities=_freeze(capabilities),
                         provenance_refs=tuple(current["provenance_refs"]), unknowns=_freeze(unknowns),
                         omitted=_freeze(current["omitted"]), boundary=_freeze(current["boundary"]))
