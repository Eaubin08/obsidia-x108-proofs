"""G3: a negated question / ability operator is never a prohibition.

"Ne peux-tu pas lancer P ?", "Tu ne lances pas P ?": the negation bears on the
question (or on the ability operator it asks about), not on a requested
content. The chain turned every negative INDIRECT_REQUEST into FORBIDDEN, so a
question produced NO_EXECUTE(p) and confirmed_no_execute: a prohibition the
speaker never uttered (QUESTION != PROHIBITION, SPEECH_ACT != AUTHORITY).

Which act it is (question, indirect request, reproach, permission query) is
held doctrine (H10): the unit keeps its existing speech-act channel and its
content, is never FORBIDDEN, carries no constraint and no new gate, and the
open act is named (negated_speech_act_open) and blocks closure.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text,lemma,head", [
    ("Ne peux-tu pas lancer P ?", "lancer", "p"),
    ("Ne pouvez-vous pas exécuter le build ?", "exécuter", "build"),
    ("Ne pourrais-tu pas exécuter le build ?", "exécuter", "build"),
    ("Est-ce que tu ne peux pas lancer P ?", "lancer", "p"),
    ("Tu ne peux pas lancer P ?", "lancer", "p"),
    ("Tu n'exécutes pas le build ?", "exécuter", "build"),
    ("Tu ne pourrais pas exécuter le build.", "exécuter", "build"),
])
def test_negated_question_operator_is_never_a_prohibition(text, lemma, head):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.lemma, u.polarity, [a.head for a in u.objects]) == (lemma, "negative", [head])  # content kept
    assert u.pragmatic != "FORBIDDEN" and u.pragmatic == "INDIRECT_REQUEST"
    assert f.constraints == () and not _gate(f)[u.id]
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and s["negated_execute_surfaces"] == []
    assert s["requested_world_actions"] == []
    assert f"negated_speech_act_open:{u.id}" in f.ambiguities
    assert not f.closure


def test_genuine_prohibition_is_kept():
    f = parse_utterance("Ne lance pas P.")
    (u,) = f.units
    assert u.pragmatic == "FORBIDDEN" and len(f.constraints) == 1
    assert not any(a.startswith("negated_speech_act_open") for a in f.ambiguities)
    s = governable_summary(parse_utterance("N'exécute pas le build."))
    assert s["confirmed_no_execute"] is True


def test_negated_member_under_the_question_stays_a_prohibition():
    # "Peux-tu ne pas lancer P ?": the negation is on the requested content
    f = parse_utterance("Peux-tu ne pas exécuter le build ?")
    (u,) = f.units
    assert u.pragmatic == "FORBIDDEN" and f.constraints == ("NO_EXECUTE(build)",)
    assert not any(a.startswith("negated_speech_act_open") for a in f.ambiguities)


@pytest.mark.parametrize("text", ["Peux-tu lancer P et ne pas exécuter le build ?",
                                  "Est-ce que tu peux lancer P et ne pas exécuter le build ?"])
def test_negated_member_sharing_the_question_operator_stays_a_prohibition(text):
    f = parse_utterance(text)
    q = f.units[1]
    assert (q.lemma, q.pragmatic) == ("exécuter", "FORBIDDEN") and "NO_EXECUTE(build)" in f.constraints
    assert not any(a.startswith("negated_speech_act_open") for a in f.ambiguities)


def test_declarative_negated_ability_is_not_turned_into_a_question():
    f = parse_utterance("Tu ne peux pas lancer P.")
    (u,) = f.units
    assert (u.pragmatic, u.polarity) == ("ASSERTED", "negative")
    assert not any(a.startswith("negated_speech_act_open") for a in f.ambiguities)
    assert f.constraints == ()


def test_positive_ability_question_is_unchanged():
    f = parse_utterance("Peux-tu lancer P ?")
    (u,) = f.units
    assert (u.pragmatic, _gate(f)[u.id], f.closure) == ("INDIRECT_REQUEST", True, True)
    assert f.ambiguities == ("ability_permission_or_request:u1",)
