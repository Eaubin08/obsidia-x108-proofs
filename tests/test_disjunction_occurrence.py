"""Coordination P6: an alternative is not an occurrence (ALTERNATIVE != OCCURRENCE).

"Paul a lancé P ou Nadia a exécuté Q": the speaker commits to the
disjunction, never to either branch. The branches form one structural
CoordinationRef (kind OR, construction "disjunction"); each branch claim is
UNRESOLVED (a claim is at stake, no branch can be determined), with
provenance "alternative". Local operators of a branch (negation, future,
modal) are not promoted into branch claims either. Units coordinated by
"et" with a branch share that fail-closed status: the precedence of "ou"
over "et" is not decided. Directives, questions, conditions and reports
keep their own claims; no event is fused.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


def _claims(text):
    f = parse_utterance(text)
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, events


@pytest.mark.parametrize("text", [
    "Paul a lancé P ou Nadia a exécuté Q.",
    "Paul a lancé P ou il a exécuté Q.",
    "Paul n'a pas lancé P ou Nadia a exécuté Q.",
    "Paul lancera P ou Nadia exécutera Q.",
    "Paul peut lancer P ou Nadia a exécuté Q.",
    "Paul a lancé P, ou Nadia a exécuté Q.",
])
def test_no_branch_of_a_disjunction_is_asserted(text):
    f, events = _claims(text)
    (coord,) = [c for c in f.coordinations if c.kind == "OR"]
    assert coord.construction == "disjunction" and len(coord.members) == 2
    for m in coord.members:
        d = events[m].occurrence_derivation
        assert events[m].occurrence_claim.value == "UNRESOLVED" and d.rule == "alternative"
        assert d.provenance["alternative"] == coord.id
    ids = [events[m].event_ref.event_id for m in coord.members]
    assert len(set(ids)) == 2 and coord.id not in events


def test_three_branches_form_one_disjunction():
    f, events = _claims("Paul a lancé P ou Nadia a exécuté Q ou Marie a vérifié R.")
    (coord,) = [c for c in f.coordinations if c.kind == "OR"]
    assert coord.members == ("u1", "u2", "u3")
    assert all(events[m].occurrence_claim.value == "UNRESOLVED" for m in coord.members)


@pytest.mark.parametrize("text", [
    "Paul a lancé P ou Nadia a lancé Q et exécuté R.",
    "Paul a lancé P et Nadia a lancé Q ou Marie a exécuté R.",
])
def test_undecided_precedence_with_et_fails_closed(text):
    f, events = _claims(text)
    assert all(e.occurrence_claim.value != "ASSERTED_REALIZED" for e in events.values())


def test_single_clause_controls_unchanged():
    f, events = _claims("Paul a lancé P et Nadia a exécuté Q.")
    assert not any(c.kind == "OR" for c in f.coordinations)
    assert [events[u.id].occurrence_claim.value for u in f.units] == ["ASSERTED_REALIZED"] * 2


@pytest.mark.parametrize("text,claim", [
    ("Lance P ou exécute Q.", "NO_ASSERTION"),                 # directive keeps its claim
    ("Paul a-t-il lancé P ou Nadia a-t-elle exécuté Q ?", "NO_ASSERTION"),  # question
])
def test_directive_and_question_claims_keep_precedence(text, claim):
    f, events = _claims(text)
    assert all(events[u.id].occurrence_claim.value == claim for u in f.units if u.id in events)


def test_directive_alternative_keeps_its_gates():
    f = parse_utterance("Lance P ou exécute Q.")
    auth = project(f, ProjectionAxis.AUTHORITY)
    assert all(auth[u.id]["requires_gate"] for u in f.units)
