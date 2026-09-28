"""B2d: a unit carrying the parser's unresolved-governance marker scopes over
its descendants. A relative inside content of unknown governance ("Marie se
rend compte que Nadia a arrêté le script que Paul a lancé") is never asserted;
its derivation names the unit that carries the marker.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

ASSERTED = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}


@pytest.mark.parametrize("text", [
    "Marie se rend compte que Nadia a arrêté le script que Paul a lancé.",
    "Marie se rend compte que Nadia a lancé le test que Paul a préparé.",
    "Marie dit que Paul a lancé le test et Nadia a arrêté le build que Luc a lancé.",
])
def test_descendants_of_unresolved_governance_are_never_asserted(text):
    f = parse_utterance(text)
    marked = {u.id for u in f.units if u.epistemic == "UNRESOLVED_GOVERNANCE" and u.embedded_under is None}
    assert marked
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    for u in f.units:
        if u.embedded_under in marked and u.id in events:
            d = events[u.id].occurrence_derivation
            assert events[u.id].occurrence_claim.value == "UNRESOLVED"
            assert d.provenance["inherited_from"]["unresolved_governance"] == u.embedded_under


def test_relatives_of_plain_roots_are_unchanged():
    f = parse_utterance("Nadia a arrêté le script que Paul a lancé.")
    events = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert "UNRESOLVED" not in events.values()
