"""N7: an impersonal obligation question is never a definitive request or prohibition.

N2 covered second-person obligation questions only. "Faut-il lancer P ?"
stayed a definitive REQUESTED, and "Ne faut-il pas / Il ne faudrait pas /
Ne faudrait-il pas lancer P ?" became FORBIDDEN, so a question produced
NO_EXECUTE and confirmed_no_execute (QUESTION != PROHIBITION).

In a question, the impersonal obligation now takes the same contract as N2:
question_or_request (INDIRECT_REQUEST, non-definitive act); the conservative
gate of the positive question is kept through the narrowest path (only an
impersonal obligation in the question channel may target a possible
addressee; no other impersonal clause is retargeted). When the negation
frames the operator: negated_speech_act_open, never FORBIDDEN, no
constraint, closure open. Declarative "Il faut / Il ne faut pas lancer P."
are unchanged. The act itself stays H10.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", ["Faut-il lancer P ?", "Faudrait-il exécuter le build ?",
                                  "Est-ce qu'il faut exécuter le build ?"])
def test_positive_impersonal_obligation_question_is_question_or_request(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.polarity, u.pragmatic) == ("OBLIGATION", "positive", "INDIRECT_REQUEST")
    assert f"question_or_request:{u.id}" in f.ambiguities and f.constraints == ()
    assert _gate(f)[u.id]                                    # conservative gate kept


@pytest.mark.parametrize("text", ["Ne faut-il pas lancer P ?", "Il ne faudrait pas exécuter le build ?",
                                  "Ne faudrait-il pas exécuter le build ?", "Il faut pas exécuter le build ?",
                                  "Est-ce qu'il ne faut pas exécuter le build ?"])
def test_negated_impersonal_obligation_question_is_never_a_prohibition(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.polarity, u.pragmatic) == ("OBLIGATION", "negative", "INDIRECT_REQUEST")
    assert f.constraints == () and not _gate(f)[u.id]
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and s["requested_world_actions"] == []
    assert f"negated_speech_act_open:{u.id}" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text,prag,gate", [("Il faut lancer P.", "REQUESTED", True),
                                            ("Il ne faut pas exécuter le build.", "FORBIDDEN", False)])
def test_declarative_impersonal_obligation_is_unchanged(text, prag, gate):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.pragmatic, _gate(f)[u.id]) == (prag, gate)
    if prag == "FORBIDDEN":
        assert governable_summary(f)["confirmed_no_execute"] is True


def test_other_impersonal_clauses_are_not_retargeted():
    f = parse_utterance("On lance P ?")
    assert all(u.request_target != "ADDRESSEE_OR_POSSIBLE_ADDRESSEE" or u.pragmatic == "INDIRECT_REQUEST"
               for u in f.units)
