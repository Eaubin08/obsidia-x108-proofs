"""NF4: a coordinated finite predicate shares the host subject only on morphological agreement.

4ef2602b let a form without an imperative reading ("exécutent", "exécutes",
"font") take the host subject without any person check: "Paul lance P et
exécutent Q" attributed "exécuter Q" to Paul (automatic subject fusion, the
real subject lost, frame closed). Agreement is now required for every
form. When a form without an imperative reading does not agree, it is
neither shared nor turned into an imperative: the predicate is kept with an
unresolved subject, EMBEDDED with unresolved governance (occurrence
UNRESOLVED, no assertion, no request, no gate) and the named structural
ambiguity subject_unresolved (closure open). Agreeing forms still share; a
disagreeing imperative form ("Paul ... et exécutez Q") stays an imperative.
A subject-less present outside coordination (NF4-ROOT) is not touched here.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}
ASSERTIVE = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    return f, gate, events


@pytest.mark.parametrize("text", [
    "Paul lance P et exécutent Q.",
    "Paul lance P et exécutes Q.",
    "Paul lance P et font Q.",
    "Nous lançons P et exécutent Q.",
    "Paul lance P, exécutent Q.",
    "Paul lance P puis exécutent Q.",
    "Paul lance P et exécutent Q ?",
    "Tu lances P et exécutent Q.",
])
def test_disagreeing_non_imperative_form_keeps_an_unresolved_subject(text):
    f, gate, events = _view(text)
    u = f.units[-1]
    assert u.subject is None and u.verb_form == "FINITE"
    assert u.pragmatic == "EMBEDDED" and u.pragmatic not in REQUESTS and not gate[u.id]
    assert u.request_target == "NONE" and u.action_agent != "ADDRESSEE"
    assert events.get(u.id) not in ASSERTIVE
    assert f"subject_unresolved:{u.id}" in f.ambiguities
    assert not any(c.construction == "shared_subject" and u.id in c.members for c in f.coordinations)
    assert f.closure is False and not semantic_closure(f).closed


def test_chain_continuation_stays_unresolved():
    f, gate, _ = _view("Paul lance P, exécutent Q et arrêtent R.")
    for u in f.units[1:]:
        assert u.subject is None and f"subject_unresolved:{u.id}" in f.ambiguities and not gate[u.id]


@pytest.mark.parametrize("text,subject", [
    ("Paul lance P et exécute Q.", "paul"),
    ("Tu lances P et exécutes Q.", "tu"),
    ("Les tests lancent P et exécutent Q.", "tests"),
    ("Nous lançons P et faisons Q.", "nous"),
    ("Paul lance P et fait Q.", "paul"),
])
def test_agreeing_forms_still_share(text, subject):
    f, _, _ = _view(text)
    assert f.units[-1].subject == subject
    assert any(c.construction == "shared_subject" for c in f.coordinations)


@pytest.mark.parametrize("text", ["Paul lance P et exécutez Q.", "Lance P et exécute Q."])
def test_imperative_forms_unchanged(text):
    f, gate, _ = _view(text)
    u = f.units[-1]
    assert (u.verb_form, u.pragmatic) == ("IMPERATIVE", "REQUESTED")
