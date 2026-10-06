"""N2: a question about an obligation is never a definitive request nor a prohibition.

A second-person obligation chain was always REQUESTED, even in a question:
"Dois-tu lancer P ?" became a definitive request, and "Tu ne dois pas
exécuter P ?" / "Ne dois-tu pas lancer P ?" became FORBIDDEN, so a question
produced NO_EXECUTE(p) and confirmed_no_execute (QUESTION != PROHIBITION,
SPEECH_ACT != AUTHORITY).

In a question, the second-person obligation takes the existing fail-closed
question_or_request channel (INDIRECT_REQUEST, conservative gate kept when
positive); when the negation frames the obligation operator it takes the G3
contract (negated_speech_act_open: no FORBIDDEN, no constraint, no gate,
closure open). The final act stays H10. Declarative obligations and
prohibitions are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", ["Dois-tu lancer P ?", "Tu dois lancer P ?", "Devez-vous exécuter le build ?",
                                  "Est-ce que tu dois lancer P ?"])
def test_positive_obligation_question_is_question_or_request(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.polarity, u.pragmatic) == ("OBLIGATION", "positive", "INDIRECT_REQUEST")
    assert f"question_or_request:{u.id}" in f.ambiguities
    assert _gate(f)[u.id]                                   # conservative request safety kept
    assert f.constraints == ()


@pytest.mark.parametrize("text", ["Tu ne dois pas lancer P ?", "Ne dois-tu pas lancer P ?",
                                  "Tu ne dois pas exécuter le build ?", "Ne devez-vous pas exécuter le build ?",
                                  "Est-ce que tu ne dois pas exécuter le build ?"])
def test_negated_obligation_question_is_never_a_prohibition(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.polarity) == ("OBLIGATION", "negative")
    assert u.pragmatic != "FORBIDDEN" and u.pragmatic == "INDIRECT_REQUEST"
    # H10 (requalified): the request reading of a negated question operator is "do P": gate
    # kept, never a prohibition; the speech-act ambiguity alone does not block closure
    assert f.constraints == () and _gate(f)[u.id]
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and s["requested_world_actions"] == ["EXECUTE"]
    assert f"negated_speech_act_open:{u.id}" in f.ambiguities and f.closure


@pytest.mark.parametrize("text", ["Tu ne dois pas exécuter le build.", "N'exécute pas le build.",
                                  "Tu dois ne pas exécuter le build ?"])
def test_prohibitions_are_unchanged(text):
    f = parse_utterance(text)
    assert f.units[0].pragmatic == "FORBIDDEN" and "NO_EXECUTE(build)" in f.constraints
    assert not any(a.startswith("negated_speech_act_open") for a in f.ambiguities)


@pytest.mark.parametrize("text,prag", [("Tu dois lancer P.", "REQUESTED"), ("Doit-il lancer P ?", "ASKED"),
                                       ("Paul doit lancer P.", "ASSERTED")])
def test_declarative_and_third_person_obligation_are_unchanged(text, prag):
    f = parse_utterance(text)
    assert f.units[0].pragmatic == prag
