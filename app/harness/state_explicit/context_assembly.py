"""B6 context assembly: query -> projection -> visibility -> instructions -> capabilities -> packet.

The ContextPacket is explicit, immutable, serializable and replayable: its packet_id is a
digest of its own semantic content (same inputs -> same packet). No cognition, judging or
truth resolution happens here; the caller's registry is never modified.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from app.harness.state_explicit.capabilities import DisclosureLevel, disclose, load_capability_matrix
from app.harness.state_explicit.contracts import BOUNDARY, StateEntry, StateStatus, render_entry
from app.harness.state_explicit.instructions import DEFAULT_INSTRUCTIONS, Instruction, select_instructions
from app.harness.state_explicit.projection import project_entries

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
        return json.dumps(_plain({"schema": PACKET_SCHEMA, "packet_id": self.packet_id, "query": self.query,
                                  "projection": self.projection, "state": self.state,
                                  "instructions": self.instructions, "capabilities": self.capabilities,
                                  "provenance_refs": self.provenance_refs, "unknowns": self.unknowns,
                                  "omitted": self.omitted, "boundary": self.boundary}),
                          ensure_ascii=False, sort_keys=True)


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
    by_id = {e.state_id: e for e in entries}
    projection = project_entries(query, entries)
    state = [render_entry(by_id[i.state_id], i.exposure) for i in projection.included]
    exposed = [by_id[i.state_id] for i in projection.included]
    state_tags = frozenset(t for e in exposed for t in e.tags) | frozenset(
        e.status.value.lower() for e in exposed if e.status in (StateStatus.ERROR, StateStatus.UNKNOWN))
    chosen = select_instructions(frozenset(projection.query_tokens), state_tags, instructions)
    matrix = capability_matrix if capability_matrix is not None else load_capability_matrix()
    capabilities = disclose(matrix, capability_level)
    unknowns = [{"state_id": e.state_id, "status": e.status.value, "uncertainty": list(e.uncertainty)}
                for e in entries if e.status != StateStatus.KNOWN]
    provenance = sorted({p for e in exposed for p in (e.source_ref, *e.provenance)})
    body = {"query": projection.query, "projection": projection.to_dict(), "state": state,
            "instructions": [i.to_dict() for i in chosen], "capabilities": capabilities,
            "provenance_refs": provenance, "unknowns": unknowns,
            "omitted": projection.to_dict()["omitted"], "boundary": dict(BOUNDARY)}
    digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return ContextPacket(packet_id=f"b6ctx_{digest[:16]}", query=body["query"],
                         projection=_freeze(body["projection"]), state=_freeze(state),
                         instructions=_freeze(body["instructions"]), capabilities=_freeze(capabilities),
                         provenance_refs=tuple(provenance), unknowns=_freeze(unknowns),
                         omitted=_freeze(body["omitted"]), boundary=_freeze(body["boundary"]))
