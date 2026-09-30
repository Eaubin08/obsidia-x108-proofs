"""D2 H07/H13 doctrine freeze.

H07 is naming consistency only: source, evidence, perspective and legacy labels
never become occurrence authority, world truth, verification or action.

H13 adds one complement form, INTERROGATIVE_COMPLEMENT, for governed question
content under KNOW. QUESTION_CONTENT is not answer knowledge by the system,
event occurrence, world truth or verification.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.complement_commitment import (
    ComplementCommitment,
    ConstructionType,
    PerspectiveKind,
    profile_for,
)
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.primitives import SourceClass, source_class
from app.semantic.lattice.projections import ProjectionAxis, project

ASSERTIVE = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}
FORBIDDEN_STATES = {"VERIFIED", "SUPPORTED", "OBSERVED"}


def _claims(frame):
    return {
        c.predicate_ref: (c.occurrence_claim.value, c.occurrence_derivation.rule, c.occurrence_derivation.provenance)
        for c in build_frame_event_index(frame).events()
    }


@pytest.mark.parametrize("text, expected", [
    ("Selon Marie, Paul a lancé P.", SourceClass.HUMAN),
    ("Selon les logs, Paul a lancé P.", SourceClass.EVIDENCE_TRACE),
    ("Apparemment, Paul a lancé P.", SourceClass.INFERENCE),
    ("Selon moi, Paul a lancé P.", SourceClass.SPEAKER),
])
def test_h07_source_class_is_not_truth_evidence_occurrence_or_authority(text, expected):
    frame = parse_utterance(text)
    (unit,) = frame.units
    claims = _claims(frame)

    assert source_class(unit) is expected
    assert project(frame, ProjectionAxis.EPISTEMIC)[unit.id]["source_class"] == expected.value
    assert claims[unit.id][0] != "ASSERTED_REALIZED"
    assert not {flow.state for flow in project_epistemic_flows(frame)} & FORBIDDEN_STATES
    assert not project(frame, ProjectionAxis.AUTHORITY)[unit.id]["requires_gate"]


def test_h13_interrogative_profile_reuses_commitment_model():
    profile = profile_for("KNOW", ConstructionType.INTERROGATIVE_COMPLEMENT)

    assert profile is not None
    assert profile.perspective_kind is PerspectiveKind.KNOWS
    assert profile.base_commitment is ComplementCommitment.QUESTIONED


@pytest.mark.parametrize("text", [
    "Marie sait qui a lancé P.",
    "Marie sait quand Paul a lancé P.",
    "Marie sait où Paul a lancé P.",
    "Marie sait pourquoi Paul a lancé P.",
    "Marie sait comment Paul a lancé P.",
])
def test_h13_know_wh_complement_is_question_content_not_occurrence(text):
    frame = parse_utterance(text)
    claims = _claims(frame)
    governor = next(unit for unit in frame.units if unit.lemma == "savoir")
    launched = next(unit for unit in frame.units if unit.lemma == "lancer")

    assert launched.pragmatic == "EMBEDDED"
    assert launched.epistemic == "NOT_APPLICABLE"
    assert launched.embedded_under == governor.id
    assert ("EMBEDS", governor.id, launched.id, "interrogative_complement") in {
        (rel.kind, rel.source, rel.target, rel.evidence) for rel in frame.relations
    }
    assert not any(a.startswith("unresolved_complement_governance") for a in frame.ambiguities)
    assert claims[launched.id][0] == "NO_ASSERTION"
    assert claims[launched.id][1] == "commitment:QUESTIONED"
    assert claims[launched.id][2]["commitment_rule"] == "KNOW/INTERROGATIVE_COMPLEMENT:base"
    assert not project(frame, ProjectionAxis.AUTHORITY)[launched.id]["requires_gate"]
    assert not {flow.state for flow in project_epistemic_flows(frame)} & FORBIDDEN_STATES
    assert frame.closure


@pytest.mark.parametrize("text", [
    "Marie ne sait pas qui a lancé P.",
    "Marie sait-elle qui a lancé P ?",
])
def test_h13_know_wh_complement_stays_safe_under_negation_and_question(text):
    frame = parse_utterance(text)
    claims = _claims(frame)
    launched = next(unit for unit in frame.units if unit.lemma == "lancer")

    assert launched.epistemic == "NOT_APPLICABLE"
    assert claims[launched.id][0] not in ASSERTIVE
    assert claims[launched.id][1] == "commitment:QUESTIONED"
    assert not {flow.state for flow in project_epistemic_flows(frame)} & FORBIDDEN_STATES
    assert frame.closure


@pytest.mark.parametrize("text", [
    "Marie sait que Paul a lancé P.",
    "Marie ne sait pas que Paul a lancé P.",
    "Marie sait-elle que Paul a lancé P ?",
])
def test_h04_declarative_know_controls_are_unchanged(text):
    frame = parse_utterance(text)
    complement = frame.units[-1]
    claims = _claims(frame)

    relations = {
        (rel.kind, rel.source, rel.target, rel.evidence) for rel in frame.relations
    }
    assert any(kind == "EMBEDS" and source == "u1" and target == complement.id and evidence.startswith("que")
               for kind, source, target, evidence in relations)
    assert claims[complement.id][0] in {"NO_ASSERTION", "UNRESOLVED"}
    assert claims[complement.id][0] != "ASSERTED_REALIZED"
    assert claims[complement.id][2]["commitment_rule"].startswith("KNOW/QUE_PROPOSITION")
