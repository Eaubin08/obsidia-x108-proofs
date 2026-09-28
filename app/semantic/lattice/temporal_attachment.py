"""Conservative temporal cue attachment for EventRef candidates.

The current parser exposes frame-global deixis and typed predicate relations.
This module uses only typed PRECEDES relations for ATTACHED relative order. All
frame-global deictic cues remain unresolved because there is no stable
clause-local cue evidence yet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.semantic.lattice.event_extraction import EventCandidate
from app.semantic.lattice.primitives import RelationKind, UtteranceFrame

_SOURCE = "semantic_temporal_attachment"


class AttachmentStatus(str, Enum):
    ATTACHED = "ATTACHED"
    AMBIGUOUS_ATTACHMENT = "AMBIGUOUS_ATTACHMENT"
    UNRESOLVED_TEMPORAL_CUE = "UNRESOLVED_TEMPORAL_CUE"


class ResolutionStatus(str, Enum):
    UNRESOLVED_RELATIVE = "UNRESOLVED_RELATIVE"
    RELATIVE_ORDER_ONLY = "RELATIVE_ORDER_ONLY"
    RESOLVED_EXTERNAL = "RESOLVED_EXTERNAL"


@dataclass(frozen=True)
class TemporalCueAttachment:
    cue: str
    attachment_status: AttachmentStatus | str
    event_ref: str | None = None
    predicate_ref: str | None = None
    clause_ref: str | None = None
    resolution_status: ResolutionStatus | str = ResolutionStatus.UNRESOLVED_RELATIVE
    relation_type: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        attachment = self.attachment_status if isinstance(self.attachment_status, AttachmentStatus) else AttachmentStatus(str(self.attachment_status))
        resolution = self.resolution_status if isinstance(self.resolution_status, ResolutionStatus) else ResolutionStatus(str(self.resolution_status))
        object.__setattr__(self, "attachment_status", attachment)
        object.__setattr__(self, "resolution_status", resolution)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "confidence", MappingProxyType(dict(self.confidence)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "cue": self.cue,
            "attachment_status": self.attachment_status.value,
            "event_ref": self.event_ref,
            "predicate_ref": self.predicate_ref,
            "clause_ref": self.clause_ref,
            "resolution_status": self.resolution_status.value,
            "relation_type": self.relation_type,
            "provenance": dict(self.provenance),
            "confidence": dict(self.confidence),
            "metadata": dict(self.metadata),
        }


def attach_temporal_cues(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> tuple[TemporalCueAttachment, ...]:
    """Attach only parser-typed relative order; preserve deixis unresolved."""

    by_predicate = {candidate.predicate_ref: candidate for candidate in candidates}
    attachments: list[TemporalCueAttachment] = []

    for relation in frame.relations:
        if relation.kind != RelationKind.PRECEDES.value:
            continue
        source = by_predicate.get(relation.source)
        target = by_predicate.get(relation.target)
        if source is None or target is None:
            continue
        attachments.append(TemporalCueAttachment(
            cue=relation.evidence or RelationKind.PRECEDES.value,
            attachment_status=AttachmentStatus.ATTACHED,
            event_ref=source.event_ref.event_id,
            predicate_ref=source.predicate_ref,
            clause_ref=None,
            resolution_status=ResolutionStatus.RELATIVE_ORDER_ONLY,
            relation_type="BEFORE",
            provenance={
                "source": _SOURCE,
                "source_relation_kind": relation.kind,
                "relation_evidence": relation.evidence,
                "source_predicate_ref": source.predicate_ref,
                "target_predicate_ref": target.predicate_ref,
            },
            confidence={"value": relation.confidence, "calibrated": False},
            metadata={
                "target_event_ref": target.event_ref.event_id,
                "source_relation_kind": relation.kind,
                "absolute_time": False,
                "causal_flow_invented": False,
            },
        ))

    for cue in dict.fromkeys(frame.deixis):
        attachments.append(TemporalCueAttachment(
            cue=cue,
            attachment_status=AttachmentStatus.UNRESOLVED_TEMPORAL_CUE,
            event_ref=None,
            predicate_ref=None,
            clause_ref=None,
            resolution_status=ResolutionStatus.UNRESOLVED_RELATIVE,
            relation_type=None,
            provenance={
                "source": _SOURCE,
                "evidence": "frame_global_deixis",
            },
            confidence={"value": None, "calibrated": False},
            metadata={
                "reason": "frame_global_deixis_without_clause_local_attachment",
                "nearest_predicate_fallback": False,
                "absolute_time": False,
            },
        ))

    return tuple(attachments)
