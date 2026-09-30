"""B1b: "quand" / "lorsque" keep their subordinate clause, its meaning held open.

"Paul lance P quand Nadia exécute Q" was one clause: "exécuter Q" was a
second root predicate (asserted by the speaker), and "Quand Nadia exécute Q,
lance P" even gave "lance" the subordinate's subject, losing the request.
"quand" (as a subordinator) and "lorsque" now open a subordinate clause
whose temporal meaning (order, simultaneity, habit, condition) is a held
doctrine: its predicate is EMBEDDED with unresolved governance (occurrence
UNRESOLVED), carries the named structural ambiguity
temporal_subordinate_open, which blocks closure, and no relation at all is
built (no PRECEDES, CONDITIONS, CAUSES, no host chosen). It never shares its
subject / modal / auxiliary with the main clause, nor receives them. An
interrogative "quand" ("Quand lances-tu P ?", "Dis-moi quand Paul lance P")
and "quand même" are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

ASSERTED = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE"}
TEMPORAL = {"PRECEDES", "CAUSES", "CONDITIONS", "SIMULTANEOUS"}


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    return f, gate, events


@pytest.mark.parametrize("text,host,sub,subject", [
    ("Paul lance P quand Nadia exécute Q.", "lancer", "exécuter", "nadia"),
    ("Paul lance P lorsque Nadia exécute Q.", "lancer", "exécuter", "nadia"),
    ("Quand Nadia exécute Q, Paul lance P.", "lancer", "exécuter", "nadia"),
    ("Lorsque Nadia exécute Q, Paul lance P.", "lancer", "exécuter", "nadia"),
    ("Paul a lancé P quand Nadia a exécuté Q.", "lancer", "exécuter", "nadia"),
    ("Paul lance P lorsqu'elle exécute Q.", "lancer", "exécuter", "elle"),
    ("Paul lancera P quand Nadia aura exécuté Q.", "lancer", "exécuter", "nadia"),
])
def test_subordinate_is_preserved_and_held_open(text, host, sub, subject):
    f, gate, events = _view(text)
    (s,) = [u for u in f.units if u.lemma == sub]
    (h,) = [u for u in f.units if u.lemma == host]
    assert s.subject == subject and s.pragmatic == "EMBEDDED"
    assert events.get(s.id) not in ASSERTED
    assert f"temporal_subordinate_open:{s.id}" in f.ambiguities
    assert not any(r.kind in TEMPORAL for r in f.relations)
    # H05 (D1): only the neutral TEMPORAL_ANCHOR(s -> host) is allowed (no order, condition or cause)
    assert [(r.kind, r.source, r.target) for r in f.relations if s.id in (r.source, r.target)] \
        == [("TEMPORAL_ANCHOR", s.id, h.id)]
    assert s.embedded_under is None
    assert h.subject == "paul" and not gate[s.id]
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text", [
    "Lance P quand Nadia exécute Q.",
    "Quand Nadia exécute Q, lance P.",
    "Lorsque Nadia a exécuté Q, lance P.",
])
def test_host_request_and_gate_are_kept(text):
    f, gate, _ = _view(text)
    (h,) = [u for u in f.units if u.lemma == "lancer"]
    assert (h.pragmatic, h.verb_form, h.subject, gate[h.id]) == ("REQUESTED", "IMPERATIVE", None, True)
    assert not any(c.construction == "shared_subject" for c in f.coordinations)


@pytest.mark.parametrize("text,content", [
    ("Paul lance P quand la stack est UP.", "la stack est UP"),
    ("Paul lance P quand le test frobnique.", "le test frobnique"),
    ("Lorsque le build frobnique, lance P.", "le build frobnique"),
])
def test_subordinate_without_unit_is_named_missing(text, content):
    f = parse_utterance(text)
    spans = [(m.split(":")[1], m.split(":")[2]) for m in f.missing if m.startswith("unanalyzed_predicative_content:")]
    assert any(f.raw[int(s.split("-")[0]):int(s.split("-")[1])] == content and link == "temporal_subordinate"
               for s, link in spans)
    assert f.closure is False


@pytest.mark.parametrize("text", [
    "Lance P lorsque Nadia et Luc exécutent Q.",
    "Paul lance P quand Nadia et Luc exécutent Q.",
])
def test_coordinated_subject_subordinate_is_never_asserted_nor_closed(text):
    f, gate, events = _view(text)
    (s,) = [u for u in f.units if u.lemma == "exécuter"]
    assert s.pragmatic == "EMBEDDED" and events.get(s.id) not in ASSERTED and not gate[s.id]
    assert f.closure is False and not semantic_closure(f).closed


def test_coordination_after_the_subordinate_is_not_attached_by_proximity():
    f, _, _ = _view("Paul lance P quand Nadia exécute Q et Luc arrête R.")
    (r,) = [u for u in f.units if u.lemma == "arrêter"]
    assert f"coordination_attachment_ambiguous:{r.id}" in f.ambiguities
    assert not any(x.kind in TEMPORAL for x in f.relations)


@pytest.mark.parametrize("text", [
    "Quand lances-tu P ?",
    "Quand Paul lance-t-il P ?",
    "Quand est-ce que Paul lance P ?",
    "Dis-moi quand Paul lance P.",
    "Je sais quand Paul lance P.",
    "Lance P quand même.",
    "Depuis quand Paul lance P ?",
])
def test_interrogative_and_idiomatic_quand_unchanged(text):
    f = parse_utterance(text)
    assert not any(a.startswith("temporal_subordinate_open") for a in f.ambiguities)
