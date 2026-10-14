"""Builder epistemic records V0 — non-sovereign organizational reasoning layer.

This module sits above the read-only Company Model. It records only Builder
epistemic state and never promotes a claim, inference, unknown, or
contradiction to canonical organizational truth, authority, or action.
"""
from __future__ import annotations

import datetime
import re
from dataclasses import asdict, dataclass
from typing import Iterable

from periphery.native_ops.common_v0 import canonical_hash

SCHEMA = "OBSIDIA_BUILDER_EPISTEMIC_RECORD_V0"
AUTHORITY = "KX108_ONLY"
KINDS = frozenset({"INFERRED", "UNKNOWN", "CONTRADICTION"})
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,200}$")


def _ident(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("BUILDER_EPISTEMIC_ID_INVALID")
    return value


def _text(value: str, error: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(error)
    return value


def _refs(
    values: Iterable[str],
    *,
    required: bool = False,
    minimum: int = 0,
) -> tuple[str, ...]:
    if isinstance(values, str):
        raise ValueError("BUILDER_EPISTEMIC_REF_SEQUENCE_REQUIRED")
    refs = tuple(values)
    if required and not refs:
        raise ValueError("BUILDER_EPISTEMIC_REFS_REQUIRED")
    if len(refs) < minimum:
        raise ValueError("BUILDER_EPISTEMIC_REFS_INSUFFICIENT")
    if len(refs) > 30 or len(set(refs)) != len(refs):
        raise ValueError("BUILDER_EPISTEMIC_REFS_DUPLICATE_OR_TOO_MANY")
    if any(not isinstance(v, str) or not _REF.fullmatch(v) for v in refs):
        raise ValueError("BUILDER_EPISTEMIC_REF_INVALID")
    return refs


def _at(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("BUILDER_EPISTEMIC_TIME_INVALID")
    try:
        parsed = datetime.datetime.fromisoformat(value)
        if parsed.utcoffset() is None:
            raise ValueError("BUILDER_EPISTEMIC_TIME_UNAWARE")
    except (TypeError, ValueError) as exc:
        raise ValueError("BUILDER_EPISTEMIC_TIME_INVALID") from exc
    return value


def _confidence(value: float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("BUILDER_EPISTEMIC_CONFIDENCE_INVALID")
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError("BUILDER_EPISTEMIC_CONFIDENCE_INVALID")
    return numeric


@dataclass(frozen=True)
class BuilderEpistemicRecordV0:
    schema: str
    organization_id: str
    record_id: str
    kind: str
    subject_refs: tuple[str, ...]
    statement: str
    provenance_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    confidence: float | None
    status: str
    created_at: str
    canonical_truth: bool
    decision_authority: str
    allowed_to_decide: bool
    allowed_to_act: bool
    record_hash: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["subject_refs"] = list(self.subject_refs)
        data["provenance_refs"] = list(self.provenance_refs)
        data["evidence_refs"] = list(self.evidence_refs)
        return data


def _payload(record: BuilderEpistemicRecordV0 | dict) -> dict:
    data = record.to_dict() if isinstance(record, BuilderEpistemicRecordV0) else dict(record)
    return {
        "schema": data["schema"],
        "organization_id": data["organization_id"],
        "record_id": data["record_id"],
        "kind": data["kind"],
        "subject_refs": list(data["subject_refs"]),
        "statement": data["statement"],
        "provenance_refs": list(data["provenance_refs"]),
        "evidence_refs": list(data["evidence_refs"]),
        "confidence": data["confidence"],
        "status": data["status"],
        "created_at": data["created_at"],
        "canonical_truth": data["canonical_truth"],
        "decision_authority": data["decision_authority"],
        "allowed_to_decide": data["allowed_to_decide"],
        "allowed_to_act": data["allowed_to_act"],
    }


def builder_epistemic_record_v0(
    *,
    organization_id: str,
    record_id: str,
    kind: str,
    subject_refs: Iterable[str],
    statement: str,
    provenance_refs: Iterable[str],
    evidence_refs: Iterable[str] = (),
    confidence: float | None = None,
    status: str,
    created_at: str,
) -> BuilderEpistemicRecordV0:
    org = _ident(organization_id)
    rid = _ident(record_id)
    if kind not in KINDS:
        raise ValueError("BUILDER_EPISTEMIC_KIND_INVALID")
    subjects = _refs(
        subject_refs,
        required=True,
        minimum=2 if kind == "CONTRADICTION" else 1,
    )
    provenance = _refs(provenance_refs, required=True)
    evidence = _refs(evidence_refs)
    data = {
        "schema": SCHEMA,
        "organization_id": org,
        "record_id": rid,
        "kind": kind,
        "subject_refs": list(subjects),
        "statement": _text(statement, "BUILDER_EPISTEMIC_STATEMENT_INVALID"),
        "provenance_refs": list(provenance),
        "evidence_refs": list(evidence),
        "confidence": _confidence(confidence),
        "status": _text(status, "BUILDER_EPISTEMIC_STATUS_INVALID"),
        "created_at": _at(created_at),
        "canonical_truth": False,
        "decision_authority": AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }
    return BuilderEpistemicRecordV0(
        schema=data["schema"],
        organization_id=org,
        record_id=rid,
        kind=kind,
        subject_refs=subjects,
        statement=data["statement"],
        provenance_refs=provenance,
        evidence_refs=evidence,
        confidence=data["confidence"],
        status=data["status"],
        created_at=data["created_at"],
        canonical_truth=False,
        decision_authority=AUTHORITY,
        allowed_to_decide=False,
        allowed_to_act=False,
        record_hash=canonical_hash(data),
    )


def verify_builder_epistemic_record_v0(
    record: BuilderEpistemicRecordV0 | dict,
) -> tuple[bool, str | None]:
    try:
        data = record.to_dict() if isinstance(record, BuilderEpistemicRecordV0) else dict(record)
        if set(data) != {
            "schema", "organization_id", "record_id", "kind", "subject_refs",
            "statement", "provenance_refs", "evidence_refs", "confidence",
            "status", "created_at", "canonical_truth", "decision_authority",
            "allowed_to_decide", "allowed_to_act", "record_hash",
        }:
            return False, "BUILDER_EPISTEMIC_FIELDS_INVALID"
        if data["schema"] != SCHEMA or data["kind"] not in KINDS:
            return False, "BUILDER_EPISTEMIC_SCHEMA_OR_KIND_INVALID"
        if (
            data["canonical_truth"] is not False
            or data["decision_authority"] != AUTHORITY
            or data["allowed_to_decide"] is not False
            or data["allowed_to_act"] is not False
        ):
            return False, "BUILDER_EPISTEMIC_AUTHORITY_OR_TRUTH_ESCALATION"
        _ident(data["organization_id"])
        _ident(data["record_id"])
        _text(data["statement"], "BUILDER_EPISTEMIC_STATEMENT_INVALID")
        _text(data["status"], "BUILDER_EPISTEMIC_STATUS_INVALID")
        _at(data["created_at"])
        _confidence(data["confidence"])
        _refs(
            data["subject_refs"],
            required=True,
            minimum=2 if data["kind"] == "CONTRADICTION" else 1,
        )
        _refs(data["provenance_refs"], required=True)
        _refs(data["evidence_refs"])
        if canonical_hash(_payload(data)) != data["record_hash"]:
            return False, "BUILDER_EPISTEMIC_HASH_MISMATCH"
        return True, None
    except (KeyError, TypeError, ValueError, AttributeError):
        return False, "BUILDER_EPISTEMIC_VERIFICATION_FAILED"
