"""Project safe language-lattice facts into OrderedMeaningFlow V0.

This module is a pure projection boundary. It reads an UtteranceFrame and emits
family-scoped OrderedMeaningFlow records without changing parser behavior,
calling authority layers, or creating memory lifecycle flows.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.semantic.lattice.flow_validators import EPISTEMIC_STATES
from app.semantic.lattice.ordered_meaning_flow import FlowFamily, OrderedMeaningFlow
from app.semantic.lattice.primitives import PredicateUnit, RelationKind, UtteranceFrame

_OBJECT_ID_SCOPE = "frame_local"
_SOURCE_KIND = "language_parser"

_TEMPORAL_RELATION_MAP = {
    RelationKind.PRECEDES.value: "BEFORE",
}

_CAUSAL_RELATION_MAP = {
    RelationKind.CAUSES.value: "CAUSES",
    RelationKind.CONDITIONS.value: "CONDITIONS",
    RelationKind.PREVENTS.value: "PREVENTS",
}

_EPISTEMIC_UNIT_MAP = {
    "BELIEF": "BELIEVED",
    "HEARSAY": "REPORTED",
    "REPORTED": "REPORTED",
    "UNKNOWN": "UNKNOWN",
    "POSSIBLE": "UNCERTAIN",
    "HYPOTHETICAL": "HYPOTHESIS",
    "COUNTERFACTUAL": "CONTRADICTED",
    # detached source markers (B2e profiles): "Selon Marie, P" is Marie's report,
    # "Selon moi, P" the speaker's belief; trace / inferential sources stay unlabelled (held)
    "HUMAN_SOURCE": "REPORTED",
    "SPEAKER_BELIEF": "BELIEVED",
}

_EPISTEMIC_PRAGMATIC_MAP = {
    "BELIEVED": "BELIEVED",
    "REPORTED": "REPORTED",
    "HYPOTHETICAL": "HYPOTHESIS",
}

_EPISTEMIC_RELATION_MAP = {
    RelationKind.BELIEVES.value: "BELIEVED",
    RelationKind.REPORTS.value: "REPORTED",
}

_GOVERNANCE_MENTION_ROLES = frozenset({
    "MENTION",
    "EXPLANATION_CONTENT",
    "TEMPORAL_CONTEXT",
    "PURPOSE",
    "PRECONDITION",
    "PERMISSION_QUERY",
    "REPORTED",
    "BELIEVED",
    "NEGATED",
    "THIRD_PARTY_ACTION",
})


def project_temporal_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    """Project structural temporal order only.

    Deictic words and tense/aspect remain provenance metadata. They are not
    converted into EVENT_TIME or absolute timestamps by this safe subset.
    """
    flows: list[OrderedMeaningFlow] = []
    for relation in frame.relations:
        relation_type = _TEMPORAL_RELATION_MAP.get(relation.kind)
        if relation_type is None:
            continue
        flows.append(_flow(
            family=FlowFamily.TEMPORAL_ORDER,
            source_object=relation.source,
            target_object=relation.target,
            relation_type=relation_type,
            direction="source_to_target",
            frame=frame,
            relation_evidence=relation.evidence,
            confidence_value=relation.confidence,
            metadata={"source_relation_kind": relation.kind},
        ))
    for unit in frame.units:
        if unit.tense_aspect != "NONE" or frame.deixis:
            flows.append(_flow(
                family=FlowFamily.TEMPORAL_ORDER,
                source_object=unit.id,
                state="utterance_scope",
                relation_type="UTTERANCE_TIME",
                direction="state_on_source",
                frame=frame,
                unit=unit,
                metadata={
                    "linguistic_tense_aspect": unit.tense_aspect,
                    "realized_assertion": unit.realized,
                    "deixis": tuple(frame.deixis),
                    "temporal_attachment": "unresolved",
                },
            ))
    return tuple(flows)


def project_causal_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    """Project typed language causal/conditional/prevention relations."""
    flows: list[OrderedMeaningFlow] = []
    for relation in frame.relations:
        relation_type = _CAUSAL_RELATION_MAP.get(relation.kind)
        if relation_type is None:
            continue
        claim_level = _claim_level(frame, relation)
        metadata = {
            "claim_level": claim_level,
            "source_relation_kind": relation.kind,
            "validated_proof": False,
        }
        coordination = frame.coordination(relation.source)
        if coordination is not None:
            # one flow for the whole coordinated antecedent; no member is sufficient alone
            metadata.update(coordination_kind=coordination.kind,
                            coordination_members=list(coordination.members),
                            coordination_construction=coordination.construction)
        flows.append(_flow(
            family=FlowFamily.CAUSAL_CLAIM,
            source_object=relation.source,
            target_object=relation.target,
            relation_type=relation_type,
            direction="source_to_target",
            frame=frame,
            relation_evidence=relation.evidence,
            confidence_value=relation.confidence,
            metadata=metadata,
        ))
    return tuple(flows)


def project_epistemic_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    """Project explicit epistemic states and embedding relations."""
    flows: list[OrderedMeaningFlow] = []
    seen: set[tuple[str, str, str | None]] = set()
    for unit in frame.units:
        state = _unit_epistemic_state(unit)
        if state is None:
            continue
        key = (unit.id, state, unit.embedded_under)
        if key in seen:
            continue
        seen.add(key)
        flows.append(_flow(
            family=FlowFamily.EPISTEMIC_STATE,
            source_object=unit.id,
            state=state,
            relation_type="STATE",
            direction="state_on_source",
            frame=frame,
            unit=unit,
            metadata={
                "embedded_under": unit.embedded_under,
                "source_epistemic": unit.epistemic,
                "source_pragmatic": unit.pragmatic,
            },
        ))
    for relation in frame.relations:
        state = _EPISTEMIC_RELATION_MAP.get(relation.kind)
        if state is None:
            continue
        key = (relation.target, state, relation.source)
        if key in seen:
            continue
        seen.add(key)
        flows.append(_flow(
            family=FlowFamily.EPISTEMIC_STATE,
            source_object=relation.target,
            state=state,
            relation_type="STATE",
            direction="state_on_source",
            frame=frame,
            relation_evidence=relation.evidence,
            confidence_value=relation.confidence,
            metadata={
                "embedded_under": relation.source,
                "source_relation_kind": relation.kind,
            },
        ))
    return tuple(flows)


def project_governance_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    """Project descriptive governance states from semantic request fields."""
    flows: list[OrderedMeaningFlow] = []
    for unit in frame.units:
        state = _governance_state(unit)
        if state is None:
            continue
        flows.append(_flow(
            family=FlowFamily.GOVERNANCE_STATE,
            source_object=unit.id,
            state=state,
            relation_type="STATE",
            direction="state_on_source",
            frame=frame,
            unit=unit,
            metadata={
                "source_role": unit.role,
                "source_pragmatic": unit.pragmatic,
                "request_target": unit.request_target,
                "action_agent": unit.action_agent,
                "ambiguities": _unit_ambiguities(frame, unit.id),
                "authority": None,
                "emits_act": False,
                "requires_gate": False,
            },
        ))
    return tuple(flows)


def project_ordered_flows(frame: UtteranceFrame) -> tuple[OrderedMeaningFlow, ...]:
    """Aggregate family projections without cross-family inference."""
    return (
        project_temporal_flows(frame)
        + project_causal_flows(frame)
        + project_epistemic_flows(frame)
        + project_governance_flows(frame)
    )


def _flow(
    *,
    family: FlowFamily,
    source_object: str,
    relation_type: str,
    frame: UtteranceFrame,
    target_object: str | None = None,
    state: str | None = None,
    direction: str = "state_on_source",
    unit: PredicateUnit | None = None,
    relation_evidence: str = "",
    confidence_value: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> OrderedMeaningFlow:
    raw_surface = None
    span = None
    parser = None
    if unit is not None:
        span = unit.span
        raw_surface = frame.raw[unit.span[0]:unit.span[1]]
        parser = unit.provenance
        if confidence_value is None:
            confidence_value = unit.confidence
    data: dict[str, Any] = {
        "source_kind": _SOURCE_KIND,
        "object_id_scope": _OBJECT_ID_SCOPE,
    }
    if metadata:
        data.update(metadata)
    provenance: dict[str, Any] = {
        "source": _SOURCE_KIND,
        "raw": frame.raw,
        "normalized": frame.normalized,
        "source_object": source_object,
        "parser": parser,
        "span": span,
        "raw_surface": raw_surface,
        "relation_evidence": relation_evidence,
        "evidence": None,
    }
    return OrderedMeaningFlow(
        family=family,
        source_object=source_object,
        target_object=target_object,
        state=state,
        relation_type=relation_type,
        direction=direction,
        scope="utterance",
        provenance=provenance,
        confidence={"value": confidence_value, "calibrated": False},
        status="asserted",
        metadata=data,
    )


def _claim_level(frame: UtteranceFrame, causal_relation: object) -> str:
    relation = causal_relation
    reported_targets = {
        rel.target
        for rel in frame.relations
        if rel.kind == RelationKind.REPORTS.value
    }
    endpoints = {*frame.relation_members(getattr(relation, "source")), getattr(relation, "target")}
    if endpoints & reported_targets:
        return "REPORTED_CAUSAL_CLAIM"
    return "LINGUISTIC_CAUSAL_CLAIM"


def _unit_epistemic_state(unit: PredicateUnit) -> str | None:
    candidates = (
        _EPISTEMIC_UNIT_MAP.get(unit.epistemic),
        _EPISTEMIC_PRAGMATIC_MAP.get(unit.pragmatic),
    )
    for state in candidates:
        if state in EPISTEMIC_STATES:
            return state
    return None


def _governance_state(unit: PredicateUnit) -> str | None:
    if unit.polarity != "positive" or unit.predicate_class != "world_action":
        return None
    if unit.role == "REQUEST" and unit.request_target == "ADDRESSEE":
        return "REQUESTED"
    if unit.role == "AMBIGUOUS_REQUEST":
        return "REQUESTED_CANDIDATE"
    if unit.role in _GOVERNANCE_MENTION_ROLES:
        return "MENTIONED"
    return None


def _unit_ambiguities(frame: UtteranceFrame, unit_id: str) -> tuple[str, ...]:
    suffix = f":{unit_id}"
    return tuple(item for item in frame.ambiguities if item.endswith(suffix))


def _families(flows: Iterable[OrderedMeaningFlow]) -> tuple[FlowFamily, ...]:
    return tuple(flow.family for flow in flows)