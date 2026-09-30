"""WH complement safety and H13 KNOW closure.

"Je sais quand Paul lance P" / "Dis-moi comment Paul lance P": the WH word
stayed inside its governor's clause, so "Paul lance P" became a second root
predicate asserted by the speaker, with no link to "savoir" / "dire", and
the frame was closed. A WH word right after a verb (or its hyphenated
pronoun) and followed by a finite clause opens a "wh" complement. H13 closes
the KNOW case as INTERROGATIVE_COMPLEMENT / QUESTION_CONTENT. Other governors
keep the NEW7 fail-closed marker unresolved_complement_governance. No WH form
asserts occurrence, truth or verification of the embedded event. Direct
questions ("Quand lances-tu P ?"), WH + infinitive ("Dis-moi comment lancer P")
and temporal "quand" are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

ASSERTIVE = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}


@pytest.mark.parametrize("text,gov,evidence,closed,claim", [
    ("Je sais quand Paul lance P.", "savoir", "interrogative_complement", True, "NO_ASSERTION"),
    ("Je sais pourquoi Paul lance P.", "savoir", "interrogative_complement", True, "NO_ASSERTION"),
    ("Dis-moi quand Paul lance P.", "dire", "wh_unresolved_governance", False, "UNRESOLVED"),
    ("Dis-moi comment Paul lance P.", "dire", "wh_unresolved_governance", False, "UNRESOLVED"),
    ("Je sais où Paul a lancé P.", "savoir", "interrogative_complement", True, "NO_ASSERTION"),
    ("Dis-moi quand Paul a lancé P.", "dire", "wh_unresolved_governance", False, "UNRESOLVED"),
])
def test_wh_complement_is_embedded_under_its_adjacent_governor(text, gov, evidence, closed, claim):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    (g,) = [u for u in f.units if u.lemma == gov]
    (c,) = [u for u in f.units if u.lemma == "lancer"]
    assert c.subject == "paul" and c.pragmatic == "EMBEDDED" and c.embedded_under == g.id
    assert ("EMBEDS", g.id, c.id, evidence) in \
        [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
    assert (f"unresolved_complement_governance:{c.id}" in f.ambiguities) is (not closed)
    assert events.get(c.id) == claim and events.get(c.id) not in ASSERTIVE and not gate[c.id]
    assert f.closure is closed and semantic_closure(f).closed is closed


def test_governor_request_is_unchanged():
    f = parse_utterance("Dis-moi quand Paul lance P.")
    (g,) = [u for u in f.units if u.lemma == "dire"]
    assert g.pragmatic == "REQUESTED"


@pytest.mark.parametrize("text", [
    "Quand lances-tu P ?", "Quand Paul lance-t-il P ?", "Dis-moi comment lancer P.",
    "Paul lance P quand Nadia exécute Q.", "Je sais que Paul lance P.",
])
def test_other_wh_and_complements_unchanged(text):
    f = parse_utterance(text)
    assert not any(r.evidence == "wh_unresolved_governance" for r in f.relations)
