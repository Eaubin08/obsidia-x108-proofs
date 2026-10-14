"""Builder Epistemics V0 contract tests."""
from __future__ import annotations

import copy
import json
from dataclasses import FrozenInstanceError

import pytest

from periphery.builder_epistemics_v0 import (
    AUTHORITY,
    SCHEMA,
    builder_epistemic_record_v0,
    verify_builder_epistemic_record_v0,
)

T0 = "2026-10-14T18:00:00+02:00"


def record(kind="INFERRED", subjects=("company-a:process-a",), **overrides):
    values = dict(
        organization_id="company-a",
        record_id="epistemic-001",
        kind=kind,
        subject_refs=subjects,
        statement="A bounded Builder statement.",
        provenance_refs=("fixture:builder-audit",),
        evidence_refs=("evidence:001",),
        confidence=0.7 if kind == "INFERRED" else None,
        status="OPEN",
        created_at=T0,
    )
    values.update(overrides)
    return builder_epistemic_record_v0(**values)


def test_inferred_is_not_observed_claim_or_canonical_truth():
    item = record()
    assert item.schema == SCHEMA
    assert item.kind == "INFERRED"
    assert item.kind != "OBSERVED_CLAIM"
    assert item.canonical_truth is False
    assert item.allowed_to_decide is False
    assert item.allowed_to_act is False
    assert item.decision_authority == AUTHORITY == "KX108_ONLY"


def test_unknown_survives_json_roundtrip_without_fabricated_resolution():
    item = record(
        kind="UNKNOWN",
        statement="Deadline source is not known.",
        evidence_refs=(),
        confidence=None,
    )
    data = json.loads(json.dumps(item.to_dict()))
    assert data["kind"] == "UNKNOWN"
    assert data["statement"] == "Deadline source is not known."
    assert verify_builder_epistemic_record_v0(data) == (True, None)


def test_contradiction_requires_and_preserves_two_subject_refs():
    item = record(
        kind="CONTRADICTION",
        subjects=("company-a:deadline-email", "company-a:deadline-contract"),
        statement="Two supplied deadline claims conflict.",
        confidence=None,
    )
    assert item.subject_refs == (
        "company-a:deadline-email",
        "company-a:deadline-contract",
    )
    with pytest.raises(ValueError, match="REFS_INSUFFICIENT"):
        record(
            kind="CONTRADICTION",
            subjects=("company-a:deadline-email",),
            confidence=None,
        )


def test_provenance_and_evidence_are_preserved():
    item = record(
        provenance_refs=("source:a", "source:b"),
        evidence_refs=("evidence:a", "evidence:b"),
    )
    assert item.provenance_refs == ("source:a", "source:b")
    assert item.evidence_refs == ("evidence:a", "evidence:b")


def test_authority_or_truth_escalation_is_rejected():
    item = record().to_dict()
    for field, value in (
        ("canonical_truth", True),
        ("allowed_to_decide", True),
        ("allowed_to_act", True),
        ("decision_authority", "BUILDER"),
    ):
        tampered = copy.deepcopy(item)
        tampered[field] = value
        assert verify_builder_epistemic_record_v0(tampered)[0] is False


def test_hash_tampering_is_rejected_and_record_is_frozen():
    item = record()
    tampered = item.to_dict()
    tampered["statement"] = "Altered."
    assert verify_builder_epistemic_record_v0(tampered) == (
        False,
        "BUILDER_EPISTEMIC_HASH_MISMATCH",
    )
    with pytest.raises(FrozenInstanceError):
        item.allowed_to_act = True


def test_identifier_time_confidence_and_reference_validation_fail_closed():
    with pytest.raises(ValueError, match="ID_INVALID"):
        record(organization_id="company a")
    with pytest.raises(ValueError, match="TIME_INVALID"):
        record(created_at="2026-10-14T18:00:00")
    with pytest.raises(ValueError, match="CONFIDENCE_INVALID"):
        record(confidence=1.5)
    with pytest.raises(ValueError, match="REF_SEQUENCE_REQUIRED"):
        record(subject_refs="company-a:process-a")


def test_representation_is_deterministic():
    a = record()
    b = record()
    assert a == b
    assert a.record_hash == b.record_hash


def test_builder_epistemics_has_no_domainstate_or_company_model_mutation_surface():
    import periphery.builder_epistemics_v0 as module

    public = set(dir(module))
    assert "DomainState" not in public
    assert "company_model_snapshot_v0" not in public
    assert "company_node_v0" not in public
    assert "company_relation_v0" not in public
