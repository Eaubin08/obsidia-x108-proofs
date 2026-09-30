"""R2: a protasis with a coordinated subject stays a protasis; its subject never leaks.

"Si Nadia et Luc exécutent Q, arrête R": "si" + "Nadia" was not opened as
a protasis (a bare nominal subject needed a verb right after it), so "et
Luc exécutent Q" became a main clause asserted by the speaker (condition
lost), and the consequent "arrête R" then took "luc" as its subject: the
true request was lost (since 4ef2602b). "si" + bare noun phrase + "et" +
bare noun phrase / tonic pronoun + a plural-agreeing verb now opens the
protasis, and the existing conjunctive-protasis rule keeps "et Luc exécutent
Q" inside it: HYPOTHETICAL, CONDITIONS to the consequent, which never shares
the protasis subject. The group-subject schema is not decided: the first
conjunct keeps its NEW8 marker (closure open).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project

ASSERTIVE = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    return f, gate, events


@pytest.mark.parametrize("text,lemma,gated", [
    ("Si Nadia et Luc exécutent Q, arrête R.", "arrêter", False),
    ("Si Nadia et Luc exécutent Q, lance R.", "lancer", True),
    ("Si Nadia et Luc exécutent Q, arrêtez R.", "arrêter", False),
    ("Si Paul et Nadia ont lancé P, lance R.", "lancer", True),
    ("Si le test et le build ont lancé P, lance R.", "lancer", True),
])
def test_coordinated_subject_protasis_is_kept_and_the_consequent_request_too(text, lemma, gated):
    f, gate, events = _view(text)
    (p,) = [u for u in f.units if u.lemma not in {lemma} or u.span[0] < text.index(",")][:1]
    (c,) = [u for u in f.units if u.lemma == lemma and u.span[0] > text.index(",")]
    assert p.pragmatic == "HYPOTHETICAL" and events.get(p.id) not in ASSERTIVE
    assert ("CONDITIONS", p.id, c.id) in [(r.kind, r.source, r.target) for r in f.relations]
    assert (c.subject, c.verb_form, c.pragmatic) == (None, "IMPERATIVE", "REQUESTED")
    assert gate[c.id] is gated
    assert any(a.startswith("coordinated_subject_unrepresented:") for a in f.ambiguities)


@pytest.mark.parametrize("text,subject", [
    ("Si Paul exécute Q, arrête R.", None),
    ("Si Nadia exécute Q, Luc arrête R.", "luc"),
])
def test_simple_protases_unchanged(text, subject):
    f, _, _ = _view(text)
    c = f.units[-1]
    assert c.subject == subject
    assert any(r.kind == "CONDITIONS" for r in f.relations)
