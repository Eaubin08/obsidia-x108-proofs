"""H14 canonical coordinated subject: one PredicateUnit, one EventCandidate, one nominal
CoordinationRef (construction coordinated_subject, host = the unit, role subject) whose
members stay addressable. AND != OR; distributivity UNSPECIFIED unless "chacun" marks it
(ParticipantConfigurationRef DISTRIBUTIVE), still one event. Mixed persons ("Paul et moi")
keep the structure, action_agent UNKNOWN (no MIXED value exists) and stay open.
Every comma member is kept ("Paul, Nadia et Luc": formerly subject "luc", two lost).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _subject(f):
    (c,) = [c for c in f.coordinations if c.construction == "coordinated_subject"]
    return c


def _events(f):
    return [e.predicate_ref for e in build_frame_event_index(f).events()]


@pytest.mark.parametrize("text,kind,members,links", [
    ("Paul et Nadia lancent P.", "AND", ("paul", "nadia"), ("et",)),
    ("Paul ou Nadia lance P.", "OR", ("paul", "nadia"), ("ou",)),
    ("Paul et Nadia ont lancé P.", "AND", ("paul", "nadia"), ("et",)),
    ("Paul, Nadia et Luc lancent P.", "AND", ("paul", "nadia", "luc"), (",", "et")),
    ("Paul, Nadia ou Luc lance P.", "OR", ("paul", "nadia", "luc"), (",", "ou")),
])
def test_coordinated_subject_is_one_unit_one_event_all_members(text, kind, members, links):
    f = parse_utterance(text)
    (u,) = f.units
    c = _subject(f)
    assert (c.kind, c.host, c.role, c.member_kind, c.member_texts, c.evidence) == \
        (kind, u.id, "subject", "argument", members, links)
    assert c.members == tuple(f"{u.id}.s{n}" for n in range(1, len(members) + 1))
    assert all(f.raw[a:b].lower().endswith(m) for (a, b), m in zip(c.member_spans, members))
    assert c.distributivity == "UNSPECIFIED" and not f.participant_configurations
    assert _events(f) == [u.id] and u.action_agent == "THIRD_PARTY"
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure


def test_explicit_distributivity_keeps_one_event():
    f = parse_utterance("Paul et Nadia ont chacun lancé P.")
    (u,) = f.units
    c = _subject(f)
    (p,) = f.participant_configurations
    assert (p.kind, p.cue, p.group, p.unit) == ("DISTRIBUTIVE", "chacun", c.id, u.id)
    assert c.member_texts == ("paul", "nadia") and [a.text for a in u.objects] == ["p"]
    assert _events(f) == [u.id] and f.closure


def test_or_subject_selects_no_member():
    f = parse_utterance("Paul ou Nadia lance P.")
    (u,) = f.units
    assert _subject(f).kind == "OR" and u.subject not in {"paul", "nadia"}
    assert {e.occurrence_claim.value for e in build_frame_event_index(f).events()} == {"UNRESOLVED"}


@pytest.mark.parametrize("text,members", [("Paul et moi lançons P.", ("paul", "moi")),
                                          ("Paul et toi lancez P.", ("paul", "toi")),
                                          ("Toi et moi lançons P.", ("toi", "moi")),
                                          ("Paul, Nadia et moi lançons P.", ("paul", "nadia", "moi"))])
def test_mixed_person_keeps_structure_agent_unknown_open(text, members):
    f = parse_utterance(text)
    (u,) = f.units
    assert _subject(f).member_texts == members and u.action_agent == "UNKNOWN"
    assert f"coordinated_subject_unrepresented:{u.id}" in f.ambiguities and not f.closure
    assert _events(f) == [u.id] and governable_summary(f)["requested_world_actions"] == []


def test_subject_and_object_coordination_do_not_fuse():
    f = parse_utterance("Paul et Nadia lancent P ou Q.")
    kinds = sorted((c.construction, c.kind, c.member_texts) for c in f.coordinations)
    assert kinds == [("coordinated_object", "OR", ("p", "q")), ("coordinated_subject", "AND", ("paul", "nadia"))]
    assert _events(f) == ["u1"]
