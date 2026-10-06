"""D5: "apparemment" is always the evidential of its own clause, never subject / object
material and never attached across a sentence boundary.

Formerly: "Apparemment Marie a lancé P." (no comma) fused the subject ("apparemment marie")
and asserted P realized; "Marie a apparemment lancé P." took "apparemment" as the subject;
"Marie lance apparemment P." read the object "apparemment p"; "Paul lance R. Apparemment, Q"
hedged the previous sentence and left Q unhedged. Now each clause carrying it is INFERRED
(occurrence not asserted), with its exact participants.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance


def _rows(f):
    occ = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    return [(u.subject, u.epistemic, tuple(a.text for a in u.objects), occ.get(u.id)) for u in f.units]


@pytest.mark.parametrize("text", ["Apparemment Marie a lancé P.", "Apparemment, Marie a lancé P.",
                                  "Marie a apparemment lancé P."])
def test_apparemment_hedges_its_clause(text):
    assert _rows(parse_utterance(text)) == [("marie", "INFERRED", ("p",), "NO_ASSERTION")]


def test_apparemment_after_verb_is_not_object():
    assert _rows(parse_utterance("Marie lance apparemment P.")) == [("marie", "INFERRED", ("p",), "NO_ASSERTION")]


@pytest.mark.parametrize("text", ["Paul lance R. Apparemment Marie a lancé P.",
                                  "Paul lance R. Apparemment, Marie a lancé P."])
def test_sentence_initial_source_marks_its_own_sentence(text):
    first, second = _rows(parse_utterance(text))
    assert first[:2] == ("paul", "ASSERTED") and second == ("marie", "INFERRED", ("p",), "NO_ASSERTION")


def test_selon_unchanged():
    assert _rows(parse_utterance("Selon Paul, Marie a lancé P."))[0][:2] == ("marie", "HUMAN_SOURCE")
