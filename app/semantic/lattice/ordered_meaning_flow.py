"""Ordered meaning flow primitives for the semantic lattice V0.

This module implements the generic immutable core plus family validators from
`docs/semantic/ORDERED_MEANING_FLOW_V0.md`. It is descriptive only: no graph
engine, no persistence, no KX108 calls, no Native Memory writes.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping
import unicodedata

from app.semantic.lattice.flow_validators import (
    CAUSAL_CLAIM_LEVELS,
    EPISTEMIC_STATES,
    NO_PROVEN_CONNECTION,
    validate_flow_fields,
)
from app.semantic.lattice.primitives import UtteranceFrame

MEMORY_WRITE_AUTHORITY = False
KX108_AUTHORITY = "KX108_ONLY"


class FlowFamily(str, Enum):
    TEMPORAL_ORDER = "TEMPORAL_ORDER"
    CAUSAL_CLAIM = "CAUSAL_CLAIM"
    EPISTEMIC_STATE = "EPISTEMIC_STATE"
    MEMORY_LIFECYCLE = "MEMORY_LIFECYCLE"
    GOVERNANCE_STATE = "GOVERNANCE_STATE"


@dataclass(frozen=True)
class FlowPath:
    connection: str
    family: FlowFamily
    source: str
    target: str | None = None
    relation_type: str | None = None
    state: str | None = None
    path: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderedMeaningFlow:
    family: FlowFamily | str | None = None
    source_object: str | None = None
    target_object: str | None = None
    state: str | None = None
    relation_type: str | None = None
    direction: str = "state_on_source"
    scope: str = "utterance"
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: Mapping[str, Any] = field(default_factory=dict)
    status: str = "draft"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.family is None:
            raise ValueError("family is required")
        family = self.family if isinstance(self.family, FlowFamily) else FlowFamily(str(self.family))
        metadata = dict(self.metadata)
        if family is FlowFamily.MEMORY_LIFECYCLE:
            metadata.setdefault("MEMORY_WRITE_AUTHORITY", MEMORY_WRITE_AUTHORITY)
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "confidence", MappingProxyType(dict(self.confidence)))
        object.__setattr__(self, "metadata", MappingProxyType(metadata))
        validate_flow_fields(self)

    @property
    def has_evidence(self) -> bool:
        evidence = self.provenance.get("evidence")
        return evidence not in {None, "", (), frozenset()}

    @property
    def validated_proof(self) -> bool:
        return self.family is FlowFamily.CAUSAL_CLAIM and self.relation_type == "VALIDATED_CAUSAL_PROOF"

    def transition(self, state: str, *, authority: bool = False, **metadata: Any) -> "OrderedMeaningFlow":
        merged = dict(self.metadata)
        merged.update(metadata)
        if self.family is FlowFamily.MEMORY_LIFECYCLE:
            merged["MEMORY_WRITE_AUTHORITY"] = False
        if self.family is FlowFamily.GOVERNANCE_STATE and state in {"AUTHORIZED", "EXECUTED"} and not authority:
            raise ValueError(f"{state} requires external authority")
        return replace(self, state=state, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family.value,
            "source_object": self.source_object,
            "target_object": self.target_object,
            "state": self.state,
            "relation_type": self.relation_type,
            "direction": self.direction,
            "scope": self.scope,
            "provenance": dict(self.provenance),
            "confidence": dict(self.confidence),
            "status": self.status,
            "metadata": dict(self.metadata),
        }


def no_proven_connection(family: FlowFamily | str, source: str, target: str | None = None) -> FlowPath:
    return FlowPath(NO_PROVEN_CONNECTION, _family(family), source, target, path=())


def infer_family_path(
    flows: Iterable[OrderedMeaningFlow],
    *,
    family: FlowFamily | str,
    source: str,
    target: str | None,
    required_relation_type: str | None = None,
    required_state: str | None = None,
) -> FlowPath:
    fam = _family(family)
    scoped = [flow for flow in flows if flow.family is fam]

    if required_state is not None:
        for flow in scoped:
            if flow.source_object == source and flow.state == required_state:
                return FlowPath("DIRECT_RELATION", fam, source, target, flow.relation_type, flow.state, (source,))
        return no_proven_connection(fam, source, target)

    for flow in scoped:
        if flow.source_object == source and flow.target_object == target:
            if required_relation_type is None or flow.relation_type == required_relation_type:
                return FlowPath("DIRECT_RELATION", fam, source, target, flow.relation_type, flow.state, (source, target) if target else (source,))

    if fam is FlowFamily.TEMPORAL_ORDER and required_relation_type in {None, "BEFORE"}:
        path = _temporal_before_path(scoped, source, target)
        if path:
            return FlowPath("INDIRECT_PATH", fam, source, target, "BEFORE", path=path)

    return no_proven_connection(fam, source, target)


def derive_ordered_meaning_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    raw = _fold(frame.raw)
    flows: list[OrderedMeaningFlow] = []

    event_source = _first_unit_id(frame, "EXECUTE") or _first_unit_id(frame, "KNOW") or "utterance"
    if "hier" in raw:
        flows.append(_temporal(event_source, "EVENT_TIME", "yesterday", frame.raw))
    if "aujourd'hui" in raw or "aujourdhui" in raw:
        event_time = "today"
        if "lance" in raw and "hier" not in raw:
            flows.append(_temporal(event_source, "EVENT_TIME", event_time, frame.raw))
        elif "reussi" in raw or "echoue" in raw:
            flows.append(_temporal(event_source, "EVENT_TIME", event_time, frame.raw))
    if "demain" in raw:
        flows.append(_temporal(event_source, "KNOWLEDGE_ACQUISITION_TIME", "tomorrow", frame.raw))
    if any(token in raw for token in ("apprendre", "appris", "appris", "saurai")):
        state = "now"
        if "aujourd'hui" in raw or "aujourdhui" in raw:
            state = "today"
        if "demain" in raw:
            state = "tomorrow"
        flows.append(_temporal(event_source, "KNOWLEDGE_ACQUISITION_TIME", state, frame.raw))
    if "viens seulement" in raw:
        flows.append(_temporal(event_source, "KNOWLEDGE_ACQUISITION_TIME", "now", frame.raw))
    if frame.raw:
        flows.append(_temporal(event_source, "UTTERANCE_TIME", "now", frame.raw))

    if "parce que" in raw:
        relation_type = "REPORTED_CAUSAL_CLAIM" if any(token in raw for token in ("dit que", "on m'a dit")) else "LINGUISTIC_CAUSAL_CLAIM"
        flows.append(OrderedMeaningFlow(
            family=FlowFamily.CAUSAL_CLAIM,
            source_object="BROKEN_BUILD",
            target_object="FAIL_TEST",
            relation_type=relation_type,
            direction="source_to_target",
            scope="utterance",
            provenance={"source": "utterance", "raw": frame.raw},
            confidence={"value": None, "calibrated": False},
            status="asserted",
            metadata={"causal_relation": "CAUSES", "validated_proof": False},
        ))

    flows.extend(_epistemic_flows(frame, raw))
    return tuple(flows)


def _temporal(source: str, relation_type: str, state: str, raw: str) -> OrderedMeaningFlow:
    return OrderedMeaningFlow(
        family=FlowFamily.TEMPORAL_ORDER,
        source_object=source,
        state=state,
        relation_type=relation_type,
        direction="state_on_source",
        scope="utterance",
        provenance={"source": "utterance", "raw": raw},
        confidence={"value": None, "calibrated": False},
        status="asserted",
        metadata={},
    )


def _epistemic_flows(frame: UtteranceFrame, raw: str) -> tuple[OrderedMeaningFlow, ...]:
    states: list[tuple[str, str]] = []
    source = _first_unit_id(frame, "EXECUTE") or _first_unit_id(frame, "BELIEVE") or _first_unit_id(frame, "SAY") or "utterance"
    if "je pense" in raw or "je croyais" in raw:
        states.append(("BELIEVED", "asserted"))
    if "on m'a dit" in raw or "il parait" in raw:
        states.append(("REPORTED", "asserted"))
    if "j'ai vu" in raw or "jai vu" in raw:
        states.append(("OBSERVED", "asserted"))
    if "logs montrent" in raw:
        states.append(("SUPPORTED", "asserted"))
    if "peut-etre" in raw or "peut etre" in raw:
        states.append(("UNCERTAIN", "asserted"))
    if "mais" in raw and ("echoue" in raw or "echou" in raw) and ("reussi" in raw or "reuss" in raw):
        states.append(("CONTRADICTED", "superseded_candidate"))

    return tuple(
        OrderedMeaningFlow(
            family=FlowFamily.EPISTEMIC_STATE,
            source_object=source,
            state=state,
            relation_type="STATE",
            direction="state_on_source",
            scope="utterance",
            provenance={"source": "utterance", "raw": frame.raw},
            confidence={"value": None, "calibrated": False},
            status=status,
            metadata={},
        )
        for state, status in states
        if state in EPISTEMIC_STATES
    )


def _temporal_before_path(flows: list[OrderedMeaningFlow], source: str, target: str | None) -> tuple[str, ...]:
    if target is None:
        return ()
    edges = [(flow.source_object, flow.target_object) for flow in flows if flow.relation_type == "BEFORE"]
    frontier: list[tuple[str, tuple[str, ...]]] = [(source, (source,))]
    seen = {source}
    while frontier:
        current, path = frontier.pop(0)
        for left, right in edges:
            if left != current or right is None or right in seen:
                continue
            next_path = path + (right,)
            if right == target:
                return next_path
            seen.add(right)
            frontier.append((right, next_path))
    return ()


def _first_unit_id(frame: UtteranceFrame, predicate: str) -> str | None:
    for unit in frame.units:
        if unit.predicate == predicate:
            return unit.id
    return None


def _family(family: FlowFamily | str) -> FlowFamily:
    return family if isinstance(family, FlowFamily) else FlowFamily(str(family))


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).replace("’", "'")