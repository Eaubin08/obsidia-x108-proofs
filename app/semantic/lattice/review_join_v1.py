"""ReviewJoin V1: join every projection of the review component, resolve nothing.

JOIN != RESOLVE. Around the caller-chosen center event, V1 keeps the V0
envelope unchanged (component, perspective relations, lossless epistemic
contributions, unresolved targets, index conflicts) and adds, per member event,
every reading the other projections give of it, each with its dimension, its
native status (the projection's own vocabulary, never re-labelled), its
perspective and its provenance:

  occurrence    -- the sourced OccurrenceClaim and its derivation rule
  epistemic     -- one reading per V0 epistemic contribution (flow or relation)
  temporal      -- linguistic tense and BEFORE order of the temporal projection
  causal        -- CAUSES / CONDITIONS / PREVENTS flows and their claim level
  coordination  -- CoordinationRef membership (kind, construction, co-members)
  operator      -- OperatorScopeRef over a coordination the event belongs to
  contradiction -- frame contradictions naming the event
  ambiguity     -- parser ambiguity markers naming the event
  reference     -- unresolved intra-utterance references of the event

Readings coexist: several perspectives on one event are never merged, ranked
or voted, contradictory readings are both kept, and no truth scalar, winner,
world verification, memory write or authority is produced. A unified status
vocabulary across dimensions is deliberately not defined here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from app.semantic.lattice.event_index import EventIndex, build_frame_event_index
from app.semantic.lattice.language_flow_projection import project_causal_flows, project_temporal_flows
from app.semantic.lattice.primitives import UtteranceFrame
from app.semantic.lattice.review_join import ReviewEnvelope, build_review_envelope

REVIEW_JOIN_V1_VERSION = "review_join_v1"
READING_DIMENSIONS = ("occurrence", "epistemic", "temporal", "causal", "coordination", "operator",
                      "contradiction", "ambiguity", "reference")


@dataclass(frozen=True)
class ReviewJoinV1:
    envelope: ReviewEnvelope
    readings: tuple[Mapping[str, Any], ...] = ()
    open_items: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "readings", tuple(MappingProxyType(dict(r)) for r in self.readings))
        for name in ("open_items", "provenance", "metadata"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))

    def readings_for(self, event_id: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(r for r in self.readings if r["event_id"] == event_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope": self.envelope.to_dict(),
            "readings": [dict(r) for r in self.readings],
            "open_items": dict(self.open_items),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


def build_review_join_v1(frame: UtteranceFrame, center_event: str,
                         event_index: EventIndex | None = None) -> ReviewJoinV1:
    index = event_index if event_index is not None else build_frame_event_index(frame)
    envelope = build_review_envelope(frame, center_event, index)
    members = {e["predicate_ref"]: e["event_id"] for e in envelope.events}
    readings: list[dict[str, Any]] = []

    def add(predicate: str, dimension: str, status: Any, perspective: Any, provenance: Mapping[str, Any]) -> None:
        readings.append({"event_id": members[predicate], "predicate_ref": predicate, "dimension": dimension,
                         "status": status, "perspective": perspective, "provenance": dict(provenance)})

    for e in envelope.events:
        derivation = e["occurrence_derivation"] or {}
        add(e["predicate_ref"], "occurrence", e["occurrence_claim"], "speaker_utterance",
            {"source": "occurrence_projection", "rule": derivation.get("derivation", {}).get("rule")})
    for c in envelope.epistemic_contributions:
        if c["predicate_ref"] not in members:
            continue
        status = c["state"] if c["origin"] == "epistemic_flow" else c["relation_kind"]
        add(c["predicate_ref"], "epistemic", status, c["source_event"] or "speaker_utterance",
            {"source": c["origin"], "source_predicate": c["source_predicate"]})
    for flow in project_temporal_flows(frame):
        if flow.relation_type == "UTTERANCE_TIME" and flow.source_object in members:
            add(flow.source_object, "temporal", flow.metadata.get("linguistic_tense_aspect"), "utterance_time",
                {"source": "temporal_projection", "relation_type": "UTTERANCE_TIME",
                 "temporal_attachment": flow.metadata.get("temporal_attachment")})
        elif flow.relation_type == "BEFORE":
            for end, role, other in ((flow.source_object, "before", flow.target_object),
                                     (flow.target_object, "after", flow.source_object)):
                if end in members:
                    add(end, "temporal", f"BEFORE:{role}", other,
                        {"source": "temporal_projection", "relation_type": "BEFORE",
                         "evidence": flow.provenance.get("relation_evidence")})
    for flow in project_causal_flows(frame):
        ends = ((m, "source") for m in frame.relation_members(flow.source_object))
        for end, role in (*ends, (flow.target_object, "target")):
            if end in members:
                add(end, "causal", f"{flow.relation_type}:{role}",
                    flow.target_object if role == "source" else flow.source_object,
                    {"source": "causal_projection", "claim_level": flow.metadata.get("claim_level"),
                     "validated_proof": flow.metadata.get("validated_proof"),
                     "coordination": flow.metadata.get("coordination_members")})
    for c in frame.coordinations:
        for m in c.members:
            if m in members:
                add(m, "coordination", f"{c.kind}:{c.construction}", c.id,
                    {"source": "parser", "co_members": [x for x in c.members if x != m]})
    for o in frame.operator_scopes:
        for m in frame.relation_members(o.scope):
            if m in members:
                add(m, "operator", f"{o.kind}:{o.speech_act}", o.id,
                    {"source": "parser", "scope": o.scope, "target": o.target, "operator_source": o.source})
    for text in frame.contradictions:
        pair = text.rsplit(":", 1)[-1].split("/")
        for m in pair:
            if m in members:
                add(m, "contradiction", text, [x for x in pair if x != m], {"source": "parser"})
    for marker in frame.ambiguities:
        for m in members:
            if marker.endswith(f":{m}") or f":{m}:" in marker:
                add(m, "ambiguity", marker, "parser", {"source": "parser"})
    for ref in frame.unresolved_references:
        m = ref.split(":", 1)[0]
        if m in members:
            add(m, "reference", f"UNRESOLVED:{ref.split(':', 1)[1]}", "parser", {"source": "parser"})

    order = {d: i for i, d in enumerate(READING_DIMENSIONS)}
    units = {u.id: i for i, u in enumerate(frame.units)}
    readings.sort(key=lambda r: (units[r["predicate_ref"]], order[r["dimension"]]))
    return ReviewJoinV1(
        envelope=envelope,
        readings=tuple(readings),
        open_items={
            "closure": frame.closure,
            "closure_blockers": list(frame.closure_blockers),
            "missing": list(frame.missing),
            "unresolved_targets": len(envelope.unresolved),
            "index_conflicts": len(envelope.conflicts),
        },
        provenance={
            "source": REVIEW_JOIN_V1_VERSION,
            "envelope": envelope.provenance["source"],
            "center_selected_by": "caller",
            "dimensions": list(READING_DIMENSIONS),
            "status_vocabulary": "native_per_dimension (no cross-dimension mapping)",
        },
        metadata={
            "truth": None,
            "winner": None,
            "conflict_resolution": "none",
            "consensus": "none",
            "fusion": "none",
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "EXECUTED_FLOW_CREATED": 0,
            "VERIFIED_FLOW_CREATED": 0,
            "KX108_CALLED": 0,
        },
    )
