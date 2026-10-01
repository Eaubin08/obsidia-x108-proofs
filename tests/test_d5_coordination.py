"""D5: coordinated participants / objects / complements keep their structure.

D5-F1: "Paul et Nadia ont chacun lancé le test" took "chacun" as the subject
and lost Paul / Nadia with a closed frame. "chacun" is now the EXPLICIT
distributivity of the coordinated subject [paul, nadia]; still one predication,
one EventCandidate (no event splitting in V1).

D5-F2: "Paul lance P ou Q" had the same representation as "P et Q". Coordinated
objects of one unit now keep their connective (argument CoordinationRef
coordinated_object, AND / OR); one event, no branch chosen, a directive OR is
not an AND.

H02 (META-TARGET-CARDINALITY): "Marie dit que P et que Q" keeps one REPORTS
per member and adds an AND CoordinationRef (complement_conjunction) by parity
with "ou que" (OR, disjunction). The selector stays AMBIGUOUS
(MULTIPLE_TARGETS_UNSUPPORTED) and only exposes that group target.

H14: a coordinated subject is one argument CoordinationRef (coordinated_subject)
on ONE unit: no group entity, no event per participant, distributivity
UNSPECIFIED unless "chacun". Plural anaphora ("Ils") is not resolved here.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.meta_event_relations import MULTIPLE_TARGETS_UNSUPPORTED, select_immediate_meta_target


def _coord(f, construction):
    return [c for c in f.coordinations if c.construction == construction]


def _events(f):
    return len(build_frame_event_index(f).events())


def _safe(f, request=False):
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and f.constraints == ()
    assert all(u.pragmatic != "FORBIDDEN" for u in f.units)
    if not request:
        assert s["requested_world_actions"] == []


# ── D5-F1 ──
def test_d5f1_chacun_keeps_participants_and_is_explicit_distributivity():
    f = parse_utterance("Paul et Nadia ont chacun lancé le test.")
    (c,) = _coord(f, "coordinated_subject")
    assert (c.kind, c.member_texts, c.distributivity, c.host) == ("AND", ("paul", "nadia"), "EXPLICIT", "u1")
    assert len(f.units) == 1 and f.units[0].subject != "chacun" and _events(f) == 1
    _safe(f)


# ── D5-F2 ──
@pytest.mark.parametrize("text,kind", [("Paul lance P et Q.", "AND"), ("Paul lance P ou Q.", "OR"),
                                       ("Lance P et Q.", "AND"), ("Lance P ou Q.", "OR")])
def test_d5f2_object_coordination_keeps_its_kind(text, kind):
    f = parse_utterance(text)
    (c,) = _coord(f, "coordinated_object")
    assert (c.kind, c.member_texts, c.role, c.host) == (kind, ("p", "q"), "object", "u1")
    assert len(f.units) == 1 and _events(f) == 1


def test_d5f2_or_never_collapses_to_and():
    for a, b in (("Paul lance P et Q.", "Paul lance P ou Q."), ("Lance P et Q.", "Lance P ou Q.")):
        assert governable_summary(parse_utterance(a))["coordinations"] != governable_summary(parse_utterance(b))["coordinations"]


def test_d5f2_mixed_and_or_objects_stay_open():
    f = parse_utterance("Paul lance P et Q ou R.")
    assert not _coord(f, "coordinated_object") and "coordination_attachment_ambiguous:u1" in f.ambiguities


# ── H02 ──
@pytest.mark.parametrize("conn,kind,construction", [("et", "AND", "complement_conjunction"), ("ou", "OR", "disjunction")])
def test_h02_member_reports_and_group_target(conn, kind, construction):
    f = parse_utterance(f"Marie dit que Paul lance P {conn} que Nadia exécute Q.")
    assert {(r.kind, r.target) for r in f.relations if r.source == "u1"} == {("REPORTS", "u2"), ("REPORTS", "u3")}
    (c,) = _coord(f, construction)
    assert (c.kind, c.members) == (kind, ("u2", "u3"))
    t = select_immediate_meta_target(f, "u1", frozenset({"REPORTS"}), build_frame_event_index(f))
    p = dict(t.provenance)
    assert (p["resolution_status"], p["reason"]) == ("AMBIGUOUS", MULTIPLE_TARGETS_UNSUPPORTED)
    assert (p["coordination_target"], p["coordination_kind"]) == (c.id, kind)
    assert t.target_predicate is None and t.target_event is None  # no first / nearest / last pick


# ── H14 ──
@pytest.mark.parametrize("text", [
    "Paul et Nadia lancent P.", "Paul et Nadia ne lancent pas P.", "Paul et Nadia doivent lancer P.",
    "Paul et Nadia peuvent lancer P.", "Paul et Nadia veulent lancer P.", "Si Paul et Nadia lancent P, arrête Q.",
])
def test_h14_coordinated_subject_one_event_per_predication(text):
    f = parse_utterance(text)
    (c,) = _coord(f, "coordinated_subject")
    assert (c.kind, c.member_texts, c.distributivity) == ("AND", ("paul", "nadia"), "UNSPECIFIED")
    host = f.unit(c.host)
    assert host.subject == "paul et nadia" and host.pragmatic not in {"REQUESTED", "FORBIDDEN"}
    single = parse_utterance(text.replace("Paul et Nadia", "Paul").replace("lancent", "lance")
                             .replace("doivent", "doit").replace("peuvent", "peut").replace("veulent", "veut"))
    assert _events(f) == _events(single) and len(f.units) == len(single.units)  # no duplication
    if text.startswith("Si"):
        assert len(f.units) == 2 and [u.pragmatic for u in f.units].count("REQUESTED") == 1
    else:
        assert len(f.units) == 1
        _safe(f)


def test_h14_disjunctive_subject():
    f = parse_utterance("Paul ou Nadia lance P.")
    (c,) = _coord(f, "coordinated_subject")
    assert (c.kind, c.member_texts) == ("OR", ("paul", "nadia")) and _events(f) == 1


def test_h14_multiple_predications_control():
    f = parse_utterance("Paul lance P et Nadia lance Q.")
    assert len(f.units) == 2 and _events(f) == 2 and not _coord(f, "coordinated_subject")


def test_h14_plural_anaphora_not_resolved():
    f = parse_utterance("Paul et Nadia lancent P. Ils exécutent Q.")
    ils = f.units[-1]
    assert ils.subject == "ils"
    assert not any(r.kind == "REFERS_TO" and r.source == ils.id for r in f.relations)
