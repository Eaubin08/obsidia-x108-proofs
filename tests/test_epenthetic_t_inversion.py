"""N12: the euphonic "-t-" of an inversion never breaks the modal chain.

"Ne faudra-t-il pas lancer P ?": the "t'" token between the verb and "il"
hid the inversion; "falloir" stayed alone and the infinitive fell back to an
injunctive REQUESTED (a false runtime request). The "-t-" is now only an
inversion marker (not a subject, not content); the chain is built and the
N7 contract applies unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", ["Faudra-t-il lancer P ?", "Faut-il lancer P ?", "Faudrait-il lancer P ?"])
def test_positive_question_matches_n7(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.lemma, u.modality, u.pragmatic) == ("lancer", "OBLIGATION", "INDIRECT_REQUEST")
    assert f"question_or_request:{u.id}" in f.ambiguities and _gate(f)[u.id]


@pytest.mark.parametrize("text", ["Ne faudra-t-il pas lancer P ?", "Ne faut-il pas lancer P ?",
                                  "Ne faudrait-il pas lancer P ?"])
def test_negative_question_matches_n7(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.polarity, u.pragmatic) == ("negative", "INDIRECT_REQUEST") and f.constraints == ()
    s = governable_summary(f)
    # H10 (requalified): the request reading of the negated question operator keeps the gate
    assert s["requested_world_actions"] == ["EXECUTE"] and s["confirmed_no_execute"] is False
    assert f"negated_speech_act_open:{u.id}" in f.ambiguities


def test_other_t_inversion_keeps_subject():
    f = parse_utterance("Va-t-il lancer P ?")
    assert f.units[0].subject == "il"
