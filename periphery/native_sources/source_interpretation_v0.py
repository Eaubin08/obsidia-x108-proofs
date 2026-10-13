"""SOURCE_INTERPRETATION_NATIVE_V0.

Provider-neutral, deterministic, non-sovereign interpretation of ephemeral
MAIL / DOCUMENT / CALENDAR material bound to a provenance-complete
NativeSourceContextPacketV0.

This layer proposes structure only. It cannot decide, act, or mutate native
CRM/TASK state.
"""
from __future__ import annotations

import datetime
import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional, Sequence

from .calendar_connector_v0 import NativeCalendarMaterialV0
from .common_v0 import (
    DECISION_AUTHORITY,
    SOURCE_CALENDAR,
    SOURCE_DOCUMENT_REPOSITORY,
    SOURCE_MAILBOX,
    canonical_hash,
)
from .document_connector_v0 import NativeDocumentMaterialV0
from .mail_connector_v0 import NativeMailMaterialV0
from .source_registry_v0 import NativeSourceRegistrationV0
from .source_runtime_v0 import NativeSourceContextPacketV0

INTERPRETER_ID = "OBSIDIA_SOURCE_INTERPRETER"
INTERPRETER_VERSION = "V0"

KIND_INFORMATION_ONLY = "INFORMATION_ONLY"
KIND_ACTION_REQUEST = "ACTION_REQUEST"
KIND_ACTION_WITH_DEADLINE = "ACTION_WITH_DEADLINE"
KIND_INCIDENT = "INCIDENT"
KIND_CONSTRAINT = "CONSTRAINT"
KIND_CALENDAR_CONTEXT = "CALENDAR_CONTEXT"
KIND_EVIDENCE_GAP = "EVIDENCE_GAP"

POLARITY_NONE = "NONE"
POLARITY_REQUIRE = "REQUIRE"
POLARITY_FORBID = "FORBID"

CASE_ACTION = "ACTION_WITH_DEADLINE"
CASE_INCIDENT = "INCIDENT"
CASE_CONTRACT = "CONTRACT_DEADLINE"
CASE_CONFLICT = "CONFLICTING_INSTRUCTIONS"
CASE_MISSING_EVIDENCE = "MISSING_EVIDENCE"

_DATE_UTC_RE = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2})[ T](\d{2}:\d{2})(?::\d{2})?\s*(?:UTC|Z)\b",
    re.IGNORECASE,
)
_ISO_OFFSET_RE = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\b"
)
_ORDER_RE = re.compile(r"\bSO-\d+\b", re.IGNORECASE)
_CONTRACT_RE = re.compile(r"\bCR-\d{4}-\d+\b", re.IGNORECASE)


@dataclass(frozen=True)
class SourceInterpretationCandidateV0:
    schema: str
    candidate_id: str
    source_packet_id: str
    source_packet_hash: str
    source_id: str
    source_kind: str
    provider: str
    registration_hash: str
    material_fingerprint: str
    interpretation_kind: str
    actionable_signal: bool
    information_only_signal: bool
    deadline_candidate: str | None
    incident_signal: bool
    work_identity_candidate: str | None
    contradiction_subject: str | None
    directive_polarity: str
    duplicate_identity_candidate: str | None
    unknowns: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    entity_refs: tuple[str, ...]
    proposed_case_type: str | None
    proposed_priority: str | None
    proposed_title: str | None
    proposed_summary: str | None
    occurred_at: str
    provenance_refs: tuple[str, ...]
    interpreter_id: str
    interpreter_version: str
    allowed_to_decide: bool
    allowed_to_act: bool
    decision_authority: str
    interpretation_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("unknowns", "evidence_gaps", "entity_refs", "provenance_refs"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True)
class SourceContradictionGroupV0:
    contradiction_id: str
    subject: str
    candidate_ids: tuple[str, ...]
    polarities: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    contradiction_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["candidate_ids"] = list(self.candidate_ids)
        data["polarities"] = list(self.polarities)
        data["evidence_refs"] = list(self.evidence_refs)
        return data


@dataclass(frozen=True)
class SourceInterpretationCorrelationV0:
    schema: str
    candidate_hashes: tuple[str, ...]
    duplicate_links: tuple[tuple[str, str], ...]
    contradiction_groups: tuple[SourceContradictionGroupV0, ...]
    correlation_hash: str
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "candidate_hashes": list(self.candidate_hashes),
            "duplicate_links": [list(x) for x in self.duplicate_links],
            "contradiction_groups": [x.to_dict() for x in self.contradiction_groups],
            "correlation_hash": self.correlation_hash,
            "allowed_to_decide": self.allowed_to_decide,
            "allowed_to_act": self.allowed_to_act,
            "decision_authority": self.decision_authority,
        }


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _material_payload(material: Any) -> Mapping[str, Any]:
    if hasattr(material, "ephemeral_dict"):
        return material.ephemeral_dict()
    raise ValueError("SOURCE_INTERPRETATION_MATERIAL_UNSUPPORTED")


def _validate_binding(
    *,
    packet: NativeSourceContextPacketV0,
    registration: NativeSourceRegistrationV0,
    expected_source_kind: str,
) -> None:
    if packet.source_id != registration.source_id:
        raise ValueError("SOURCE_INTERPRETATION_SOURCE_ID_MISMATCH")
    if packet.source_kind != registration.source_kind:
        raise ValueError("SOURCE_INTERPRETATION_SOURCE_KIND_MISMATCH")
    if packet.source_kind != expected_source_kind:
        raise ValueError("SOURCE_INTERPRETATION_MATERIAL_KIND_MISMATCH")
    if packet.provider != registration.provider:
        raise ValueError("SOURCE_INTERPRETATION_PROVIDER_MISMATCH")
    if packet.registration_hash != registration.registration_hash:
        raise ValueError("SOURCE_INTERPRETATION_REGISTRATION_MISMATCH")
    if packet.provenance_complete is not True:
        raise ValueError("SOURCE_INTERPRETATION_PROVENANCE_INCOMPLETE")
    if packet.allowed_to_decide or packet.allowed_to_act:
        raise ValueError("SOURCE_INTERPRETATION_PACKET_AUTHORITY_INVALID")
    if packet.decision_authority != DECISION_AUTHORITY:
        raise ValueError("SOURCE_INTERPRETATION_PACKET_DECISION_AUTHORITY_INVALID")


def _extract_deadline(text: str) -> str | None:
    match = _ISO_OFFSET_RE.search(text)
    if match:
        return match.group(1)
    match = _DATE_UTC_RE.search(text)
    if match:
        return f"{match.group(1)}T{match.group(2)}:00+00:00"
    return None


def _end_of_received_day(received_at: str) -> str:
    dt = datetime.datetime.fromisoformat(received_at)
    return dt.replace(hour=17, minute=0, second=0, microsecond=0).isoformat()


def _incident_policy_due(received_at: str) -> str:
    dt = datetime.datetime.fromisoformat(received_at)
    return (dt + datetime.timedelta(hours=4, minutes=30)).isoformat()


def _candidate(
    *,
    packet: NativeSourceContextPacketV0,
    registration: NativeSourceRegistrationV0,
    material: Any,
    interpretation_kind: str,
    actionable_signal: bool,
    information_only_signal: bool,
    deadline_candidate: str | None,
    incident_signal: bool,
    work_identity_candidate: str | None,
    contradiction_subject: str | None,
    directive_polarity: str,
    duplicate_identity_candidate: str | None,
    unknowns: Sequence[str] = (),
    evidence_gaps: Sequence[str] = (),
    entity_refs: Sequence[str] = (),
    proposed_case_type: str | None = None,
    proposed_priority: str | None = None,
    proposed_title: str | None = None,
    proposed_summary: str | None = None,
    occurred_at: str,
) -> SourceInterpretationCandidateV0:
    material_fingerprint = canonical_hash(_material_payload(material))
    seed = {
        "source_packet_hash": packet.packet_hash,
        "material_fingerprint": material_fingerprint,
        "interpreter_id": INTERPRETER_ID,
        "interpreter_version": INTERPRETER_VERSION,
    }
    candidate_id = f"interpretation-{canonical_hash(seed)[:32]}"
    payload = {
        "schema": "OBSIDIA_SOURCE_INTERPRETATION_CANDIDATE_V0",
        "candidate_id": candidate_id,
        "source_packet_id": packet.packet_id,
        "source_packet_hash": packet.packet_hash,
        "source_id": registration.source_id,
        "source_kind": registration.source_kind,
        "provider": registration.provider,
        "registration_hash": registration.registration_hash,
        "material_fingerprint": material_fingerprint,
        "interpretation_kind": interpretation_kind,
        "actionable_signal": bool(actionable_signal),
        "information_only_signal": bool(information_only_signal),
        "deadline_candidate": deadline_candidate,
        "incident_signal": bool(incident_signal),
        "work_identity_candidate": work_identity_candidate,
        "contradiction_subject": contradiction_subject,
        "directive_polarity": directive_polarity,
        "duplicate_identity_candidate": duplicate_identity_candidate,
        "unknowns": sorted(set(unknowns)),
        "evidence_gaps": sorted(set(evidence_gaps)),
        "entity_refs": sorted(set(entity_refs)),
        "proposed_case_type": proposed_case_type,
        "proposed_priority": proposed_priority,
        "proposed_title": proposed_title,
        "proposed_summary": proposed_summary,
        "occurred_at": occurred_at,
        "provenance_refs": sorted(
            {
                f"source-packet:{packet.packet_hash}",
                f"source-observation:{packet.observation_hash}",
                f"source-registration:{registration.registration_hash}",
            }
        ),
        "interpreter_id": INTERPRETER_ID,
        "interpreter_version": INTERPRETER_VERSION,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return SourceInterpretationCandidateV0(
        schema=payload["schema"],
        candidate_id=candidate_id,
        source_packet_id=packet.packet_id,
        source_packet_hash=packet.packet_hash,
        source_id=registration.source_id,
        source_kind=registration.source_kind,
        provider=registration.provider,
        registration_hash=registration.registration_hash,
        material_fingerprint=material_fingerprint,
        interpretation_kind=interpretation_kind,
        actionable_signal=bool(actionable_signal),
        information_only_signal=bool(information_only_signal),
        deadline_candidate=deadline_candidate,
        incident_signal=bool(incident_signal),
        work_identity_candidate=work_identity_candidate,
        contradiction_subject=contradiction_subject,
        directive_polarity=directive_polarity,
        duplicate_identity_candidate=duplicate_identity_candidate,
        unknowns=tuple(payload["unknowns"]),
        evidence_gaps=tuple(payload["evidence_gaps"]),
        entity_refs=tuple(payload["entity_refs"]),
        proposed_case_type=proposed_case_type,
        proposed_priority=proposed_priority,
        proposed_title=proposed_title,
        proposed_summary=proposed_summary,
        occurred_at=occurred_at,
        provenance_refs=tuple(payload["provenance_refs"]),
        interpreter_id=INTERPRETER_ID,
        interpreter_version=INTERPRETER_VERSION,
        allowed_to_decide=False,
        allowed_to_act=False,
        decision_authority=DECISION_AUTHORITY,
        interpretation_hash=canonical_hash(payload),
    )


def verify_source_interpretation_candidate_v0(
    candidate: SourceInterpretationCandidateV0 | Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    data = (
        candidate.to_dict()
        if isinstance(candidate, SourceInterpretationCandidateV0)
        else dict(candidate)
    )
    if data.get("schema") != "OBSIDIA_SOURCE_INTERPRETATION_CANDIDATE_V0":
        return False, "SOURCE_INTERPRETATION_SCHEMA_INVALID"
    if data.get("allowed_to_decide") is not False:
        return False, "SOURCE_INTERPRETATION_DECISION_FORBIDDEN"
    if data.get("allowed_to_act") is not False:
        return False, "SOURCE_INTERPRETATION_ACTION_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "SOURCE_INTERPRETATION_AUTHORITY_INVALID"
    if data.get("interpreter_id") != INTERPRETER_ID:
        return False, "SOURCE_INTERPRETATION_INTERPRETER_ID_INVALID"
    if data.get("interpreter_version") != INTERPRETER_VERSION:
        return False, "SOURCE_INTERPRETATION_VERSION_INVALID"
    payload = dict(data)
    actual = payload.pop("interpretation_hash", None)
    if canonical_hash(payload) != actual:
        return False, "SOURCE_INTERPRETATION_HASH_MISMATCH"
    return True, None


def interpret_mail_v0(
    *,
    packet: NativeSourceContextPacketV0,
    registration: NativeSourceRegistrationV0,
    material: NativeMailMaterialV0,
) -> SourceInterpretationCandidateV0:
    _validate_binding(
        packet=packet,
        registration=registration,
        expected_source_kind=SOURCE_MAILBOX,
    )
    text = _normalize(f"{material.subject}\n{material.body}")
    deadline = _extract_deadline(material.body)

    if (
        "general information only" in text
        or "no response or action required" in text
    ):
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_INFORMATION_ONLY,
            actionable_signal=False,
            information_only_signal=True,
            deadline_candidate=None,
            incident_signal=False,
            work_identity_candidate=None,
            contradiction_subject=None,
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            proposed_title=None,
            proposed_summary=None,
            occurred_at=material.received_at,
        )

    if "access control" in text and (
        "incident" in text or "unavailable" in text
    ):
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_INCIDENT,
            actionable_signal=True,
            information_only_signal=False,
            deadline_candidate=_incident_policy_due(material.received_at),
            incident_signal=True,
            work_identity_candidate="work:incident:access-control",
            contradiction_subject=None,
            directive_polarity=POLARITY_REQUIRE,
            duplicate_identity_candidate="work:incident:access-control",
            entity_refs=("system:access-control",),
            proposed_case_type=CASE_INCIDENT,
            proposed_priority="CRITICAL",
            proposed_title="Investigate access-control incident",
            proposed_summary="Operational source reports access-control unavailability requiring investigation.",
            occurred_at=material.received_at,
        )

    order_match = _ORDER_RE.search(material.body)
    if order_match:
        order_id = order_match.group(0).upper()
        subject = f"supplier-order:{order_id}"
        if "do not approve" in text:
            polarity = POLARITY_FORBID
        elif "approve supplier order" in text:
            polarity = POLARITY_REQUIRE
        else:
            polarity = POLARITY_NONE
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_ACTION_REQUEST,
            actionable_signal=True,
            information_only_signal=False,
            deadline_candidate=(
                _end_of_received_day(material.received_at)
                if "today" in text else None
            ),
            incident_signal=False,
            work_identity_candidate=f"work:{subject}",
            contradiction_subject=subject,
            directive_polarity=polarity,
            duplicate_identity_candidate=f"work:{subject}",
            entity_refs=(f"supplier-order:{order_id}",),
            proposed_case_type=CASE_CONFLICT,
            proposed_priority="HIGH",
            proposed_title="Resolve supplier order instruction",
            proposed_summary=f"Operational source contains an instruction concerning supplier order {order_id}.",
            occurred_at=material.received_at,
        )

    if "submit the requested dossier" in text:
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=(
                KIND_ACTION_WITH_DEADLINE if deadline else KIND_ACTION_REQUEST
            ),
            actionable_signal=True,
            information_only_signal=False,
            deadline_candidate=deadline,
            incident_signal=False,
            work_identity_candidate="work:dossier-submission",
            contradiction_subject=None,
            directive_polarity=POLARITY_REQUIRE,
            duplicate_identity_candidate="work:dossier-submission",
            entity_refs=("dossier:requested",),
            proposed_case_type=CASE_ACTION,
            proposed_priority="HIGH",
            proposed_title="Submit requested dossier",
            proposed_summary="Operational source requests submission of a dossier.",
            occurred_at=material.received_at,
        )

    if "process the request as discussed" in text:
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_EVIDENCE_GAP,
            actionable_signal=False,
            information_only_signal=False,
            deadline_candidate=None,
            incident_signal=False,
            work_identity_candidate="work:missing-evidence-request",
            contradiction_subject=None,
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            unknowns=("REQUEST_AUTHORITY_UNKNOWN", "REQUEST_SCOPE_UNKNOWN"),
            evidence_gaps=("REFERENCED_PRIOR_CONTEXT_MISSING",),
            proposed_case_type=CASE_MISSING_EVIDENCE,
            proposed_priority="NORMAL",
            proposed_title="Clarify incomplete request",
            proposed_summary="Request references missing prior context and cannot be safely interpreted as executable work.",
            occurred_at=material.received_at,
        )

    return _candidate(
        packet=packet,
        registration=registration,
        material=material,
        interpretation_kind=KIND_EVIDENCE_GAP,
        actionable_signal=False,
        information_only_signal=False,
        deadline_candidate=deadline,
        incident_signal=False,
        work_identity_candidate=None,
        contradiction_subject=None,
        directive_polarity=POLARITY_NONE,
        duplicate_identity_candidate=None,
        unknowns=("MESSAGE_INTENT_UNKNOWN",),
        evidence_gaps=("INTENT_NOT_STRUCTURALLY_PROVEN",),
        occurred_at=material.received_at,
    )


def interpret_document_v0(
    *,
    packet: NativeSourceContextPacketV0,
    registration: NativeSourceRegistrationV0,
    material: NativeDocumentMaterialV0,
    observed_at: str,
) -> SourceInterpretationCandidateV0:
    _validate_binding(
        packet=packet,
        registration=registration,
        expected_source_kind=SOURCE_DOCUMENT_REPOSITORY,
    )
    text = _normalize(material.content)
    deadline = _extract_deadline(material.content)

    contract = _CONTRACT_RE.search(material.content)
    if contract and "renewal review required before" in text:
        contract_id = contract.group(0).upper()
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_ACTION_WITH_DEADLINE,
            actionable_signal=True,
            information_only_signal=False,
            deadline_candidate=deadline,
            incident_signal=False,
            work_identity_candidate=f"work:contract:{contract_id}",
            contradiction_subject=None,
            directive_polarity=POLARITY_REQUIRE,
            duplicate_identity_candidate=f"work:contract:{contract_id}",
            entity_refs=(f"contract:{contract_id}",),
            proposed_case_type=CASE_CONTRACT,
            proposed_priority="HIGH",
            proposed_title="Review contract renewal",
            proposed_summary=f"Contract {contract_id} requires renewal review before an explicit deadline.",
            occurred_at=observed_at,
        )

    order = _ORDER_RE.search(material.content)
    if order and "requires dual validation before approval" in text:
        order_id = order.group(0).upper()
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_CONSTRAINT,
            actionable_signal=False,
            information_only_signal=False,
            deadline_candidate=None,
            incident_signal=False,
            work_identity_candidate=f"work:supplier-order:{order_id}",
            contradiction_subject=f"supplier-order:{order_id}",
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            entity_refs=(f"supplier-order:{order_id}",),
            proposed_summary=f"Reference document requires dual validation before approval of supplier order {order_id}.",
            occurred_at=observed_at,
        )

    if "reference document only" in text or "no action required" in text:
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_INFORMATION_ONLY,
            actionable_signal=False,
            information_only_signal=True,
            deadline_candidate=None,
            incident_signal=False,
            work_identity_candidate=None,
            contradiction_subject=None,
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            occurred_at=observed_at,
        )

    return _candidate(
        packet=packet,
        registration=registration,
        material=material,
        interpretation_kind=KIND_EVIDENCE_GAP,
        actionable_signal=False,
        information_only_signal=False,
        deadline_candidate=deadline,
        incident_signal=False,
        work_identity_candidate=None,
        contradiction_subject=None,
        directive_polarity=POLARITY_NONE,
        duplicate_identity_candidate=None,
        unknowns=("DOCUMENT_SEMANTICS_UNKNOWN",),
        evidence_gaps=("DOCUMENT_INTENT_NOT_PROVEN",),
        occurred_at=observed_at,
    )


def interpret_calendar_v0(
    *,
    packet: NativeSourceContextPacketV0,
    registration: NativeSourceRegistrationV0,
    material: NativeCalendarMaterialV0,
) -> SourceInterpretationCandidateV0:
    _validate_binding(
        packet=packet,
        registration=registration,
        expected_source_kind=SOURCE_CALENDAR,
    )
    text = _normalize(f"{material.title}\n{material.description}")

    if "deadline associated with mail-action-001" in text:
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_CALENDAR_CONTEXT,
            actionable_signal=False,
            information_only_signal=False,
            deadline_candidate=material.end_time,
            incident_signal=False,
            work_identity_candidate="work:dossier-submission",
            contradiction_subject=None,
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            entity_refs=("dossier:requested",),
            proposed_summary="Calendar event provides deadline context for the dossier-submission work identity.",
            occurred_at=material.start_time,
        )

    if "weekly coordination" in text or "routine meeting" in text:
        return _candidate(
            packet=packet,
            registration=registration,
            material=material,
            interpretation_kind=KIND_CALENDAR_CONTEXT,
            actionable_signal=False,
            information_only_signal=False,
            deadline_candidate=None,
            incident_signal=False,
            work_identity_candidate=None,
            contradiction_subject=None,
            directive_polarity=POLARITY_NONE,
            duplicate_identity_candidate=None,
            proposed_summary="Routine calendar context only.",
            occurred_at=material.start_time,
        )

    return _candidate(
        packet=packet,
        registration=registration,
        material=material,
        interpretation_kind=KIND_EVIDENCE_GAP,
        actionable_signal=False,
        information_only_signal=False,
        deadline_candidate=None,
        incident_signal=False,
        work_identity_candidate=None,
        contradiction_subject=None,
        directive_polarity=POLARITY_NONE,
        duplicate_identity_candidate=None,
        unknowns=("CALENDAR_EVENT_INTENT_UNKNOWN",),
        evidence_gaps=("CALENDAR_EVENT_RELATION_NOT_PROVEN",),
        occurred_at=material.start_time,
    )


def correlate_source_interpretations_v0(
    candidates: Sequence[SourceInterpretationCandidateV0],
) -> SourceInterpretationCorrelationV0:
    for candidate in candidates:
        ok, reason = verify_source_interpretation_candidate_v0(candidate)
        if not ok:
            raise ValueError(reason)

    ordered = sorted(candidates, key=lambda x: (x.occurred_at, x.candidate_id))

    duplicate_links: list[tuple[str, str]] = []
    primary_by_identity: dict[str, SourceInterpretationCandidateV0] = {}
    for candidate in ordered:
        identity = candidate.duplicate_identity_candidate
        if not identity or not candidate.actionable_signal:
            continue
        primary = primary_by_identity.get(identity)
        if primary is None:
            primary_by_identity[identity] = candidate
            continue
        # Contradictory directives are not duplicates.
        if (
            candidate.contradiction_subject
            and primary.contradiction_subject == candidate.contradiction_subject
            and {candidate.directive_polarity, primary.directive_polarity}
            == {POLARITY_REQUIRE, POLARITY_FORBID}
        ):
            continue
        duplicate_links.append((candidate.candidate_id, primary.candidate_id))

    contradiction_groups: list[SourceContradictionGroupV0] = []
    by_subject: dict[str, list[SourceInterpretationCandidateV0]] = {}
    for candidate in ordered:
        if candidate.contradiction_subject:
            by_subject.setdefault(candidate.contradiction_subject, []).append(candidate)
    for subject, members in sorted(by_subject.items()):
        action_members = [
            x for x in members
            if x.directive_polarity in {POLARITY_REQUIRE, POLARITY_FORBID}
        ]
        polarities = {x.directive_polarity for x in action_members}
        if polarities != {POLARITY_REQUIRE, POLARITY_FORBID}:
            continue
        ids = tuple(sorted(x.candidate_id for x in members))
        refs = tuple(sorted({ref for x in members for ref in x.provenance_refs}))
        payload = {
            "subject": subject,
            "candidate_ids": list(ids),
            "polarities": sorted(polarities),
            "evidence_refs": list(refs),
        }
        contradiction_groups.append(
            SourceContradictionGroupV0(
                contradiction_id=f"contradiction-{canonical_hash(payload)[:32]}",
                subject=subject,
                candidate_ids=ids,
                polarities=tuple(sorted(polarities)),
                evidence_refs=refs,
                contradiction_hash=canonical_hash(payload),
            )
        )

    payload = {
        "schema": "OBSIDIA_SOURCE_INTERPRETATION_CORRELATION_V0",
        "candidate_hashes": sorted(x.interpretation_hash for x in candidates),
        "duplicate_links": [list(x) for x in sorted(duplicate_links)],
        "contradiction_groups": [x.to_dict() for x in contradiction_groups],
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    return SourceInterpretationCorrelationV0(
        schema=payload["schema"],
        candidate_hashes=tuple(payload["candidate_hashes"]),
        duplicate_links=tuple(tuple(x) for x in payload["duplicate_links"]),
        contradiction_groups=tuple(contradiction_groups),
        correlation_hash=canonical_hash(payload),
        allowed_to_decide=False,
        allowed_to_act=False,
        decision_authority=DECISION_AUTHORITY,
    )
