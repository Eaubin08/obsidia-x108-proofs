"""Iteration 6: conjunctive conditional antecedent "(P AND Q) -> R".

"Si P et Q, R", "Si P et que Q, R" and "Si P et si Q, R" converge on one
structural CoordinationRef(kind=AND, members=(P, Q)) with COORDINATES(P, Q)
and a single CONDITIONS(coordination -> R). Neither member is individually
sufficient (no CONDITIONS(P, R) / CONDITIONS(Q, R)); the coordination object
is structural only: no event, no occurrence claim, never an anaphora target.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.language_flow_projection import project_causal_flows

A = chr(39)
P = "Paul lance le test"
Q = "Nadia lance le build"
R = "Luc lance le lot"
ASSERTED = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
FORMS = [f"Si {P} et {Q}, {R}.", f"Si {P} et que {Q}, {R}.", f"Si {P} et si {Q}, {R}.",
         f"Si {P} et qu" + A + f"il lance le build, {R}."]


def _by_subject(f, subject):
    return next(u for u in f.units if u.subject == subject)


@pytest.mark.parametrize("text", FORMS)
def test_conjunctive_protasis_is_one_structural_antecedent(text):
    f = parse_utterance(text)
    p, r = _by_subject(f, "paul"), _by_subject(f, "luc")
    q = next(u for u in f.units if u.subject in {"nadia", "il"})
    (coord,) = f.coordinations
    assert (coord.kind, coord.members, coord.construction) == ("AND", (p.id, q.id), "conditional_protasis")
    rels = {(x.kind, x.source, x.target) for x in f.relations}
    assert ("CONDITIONS", coord.id, r.id) in rels
    assert ("COORDINATES", p.id, q.id) in rels
    assert not any(x.kind == "CONDITIONS" and x.source in {p.id, q.id} for x in f.relations)
    assert not any(x.kind == "CONDITIONS" and x.target == q.id for x in f.relations)
    assert (p.pragmatic, q.pragmatic) == ("HYPOTHETICAL", "HYPOTHETICAL")
    assert q.embedded_under is None


@pytest.mark.parametrize("text", FORMS)
def test_members_are_conditional_sources_and_the_object_has_no_occurrence(text):
    f = parse_utterance(text)
    (coord,) = f.coordinations
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    assert coord.id not in events
    for member in coord.members:
        assert events[member].occurrence_claim.value == "CONTINGENT"
        assert events[member].occurrence_derivation.rule == "conditional:source"
        assert events[member].occurrence_derivation.provenance["conditional_group"] == coord.id
    r = _by_subject(f, "luc")
    assert (events[r.id].occurrence_claim.value, events[r.id].occurrence_derivation.rule) == \
        ("CONTINGENT", "conditional:target")


@pytest.mark.parametrize("text", FORMS)
def test_one_grouped_conditional_flow(text):
    f = parse_utterance(text)
    (coord,) = f.coordinations
    flows = [x for x in project_causal_flows(f) if x.relation_type == "CONDITIONS"]
    assert len(flows) == 1
    (flow,) = flows
    assert (flow.source_object, flow.target_object) == (coord.id, _by_subject(f, "luc").id)
    assert flow.metadata["coordination_kind"] == "AND"
    assert list(flow.metadata["coordination_members"]) == list(coord.members)


def test_three_member_antecedent():
    f = parse_utterance(f"Si {P} et {Q} et Marie lance le script, {R}.")
    (coord,) = f.coordinations
    assert len(coord.members) == 3
    assert [(x.source, x.target) for x in f.relations if x.kind == "COORDINATES"] == \
        list(zip(coord.members, coord.members[1:]))
    assert [(x.source, x.target) for x in f.relations if x.kind == "CONDITIONS"] == \
        [(coord.id, _by_subject(f, "luc").id)]


@pytest.mark.parametrize("q", [
    "Nadia ne lance pas le build",
    "Nadia lancera le build",
    "Nadia pourrait lancer le build",
    "Nadia dit que Marie a lancé le build",
    "Nadia a appris que Marie a lancé le build",
    "Nadia croit que Marie a lancé le build",
])
def test_member_variants_are_never_asserted(q):
    f = parse_utterance(f"Si {P} et {q}, {R}.")
    (coord,) = f.coordinations
    for c in build_frame_event_index(f).events():
        assert c.occurrence_claim.value not in ASSERTED, (c.predicate_ref, c.occurrence_claim)


def test_coordination_is_never_an_anaphora_target():
    f = parse_utterance(f"Si {P} et {Q}, {R}. Marie a vu ce lancement.")
    (coord,) = f.coordinations
    refs = resolve_explicit_event_references(f, build_frame_event_index(f).events()).references
    assert all(ref.target_event != coord.id and ref.resolution_status.value != "RESOLVED_STRUCTURAL" for ref in refs)


def test_ir_exposes_the_structural_object():
    f = parse_utterance(f"Si {P} et {Q}, {R}.")
    ir = governable_summary(f)
    (coord,) = f.coordinations
    assert ir["coordinations"] == [[coord.id, "AND", list(coord.members), "conditional_protasis"]]


@pytest.mark.parametrize("text,conditions", [
    (f"Si {P}, {R}.", [("u1", "u2")]),
    (f"Si {P}, {Q} et {R}.", [("u1", "u2")]),
    (f"{R} si {P} et {Q}.", None),
    (f"{P} et {Q}.", []),
])
def test_out_of_scope_forms_have_no_coordination_object(text, conditions):
    f = parse_utterance(text)
    assert f.coordinations == ()
    if conditions is not None:
        assert [(x.source, x.target) for x in f.relations if x.kind == "CONDITIONS"] == conditions
