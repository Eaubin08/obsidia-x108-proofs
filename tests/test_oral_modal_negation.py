"""N1: an oral negation of a modal chain head is never dropped.

"Tu peux pas lancer P ?", "Paul peut pas lancer P.": the oral negator (no
"ne") sits between the finite head and the lexical infinitive; it was only
searched after the infinitive, so the unit came out positive (a negative
surface silently turned positive: gated requests, shared positive scope).

The oral negation of the head is now detected (negation_confirmed stays
False: an oral negation never relaxes nor confirms anything at runtime). A
question whose operator is negated takes the G3 contract; a negated head
opens its coordination scope like a written one (G1); "Tu peux pas ne pas
lancer P ?" keeps its member negation and its open operator act.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text,modality", [
    ("Tu peux pas lancer P ?", "ABILITY_OR_PERMISSION"), ("Peux-tu pas lancer P ?", "ABILITY_OR_PERMISSION"),
    ("Tu dois pas lancer P ?", "OBLIGATION"), ("Tu veux pas lancer P ?", "DESIRE"), ("Tu sais pas lancer P ?", "KNOW_HOW"),
    ("Paul peut pas lancer P.", "ABILITY_OR_PERMISSION"), ("Paul doit jamais lancer P.", "OBLIGATION"),
])
def test_oral_head_negation_is_kept(text, modality):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.polarity, u.ne_omitted, u.negation_confirmed) == (modality, "negative", True, False)
    # H09 / H10 (requalified): a negated 2nd-person ability / obligation / desire question
    # keeps its request reading ("do P"): gate; a know-how question has none
    gated = modality != "KNOW_HOW" and text.endswith("?")
    assert _gate(f)[u.id] is gated
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and s["requested_world_actions"] == (["EXECUTE"] if gated else [])


@pytest.mark.parametrize("text", ["Tu peux pas lancer P ?", "Tu dois pas lancer P ?", "Tu peux pas ne pas lancer P ?"])
def test_oral_negated_question_operator_is_never_a_prohibition(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == "INDIRECT_REQUEST" and f.constraints == ()
    assert f"negated_speech_act_open:{u.id}" in f.ambiguities
    # H10 (requalified): the open act alone does not block closure; a negated content under
    # the negated operator ("ne pas lancer") stays open (option A)
    assert f.closure is ("ne pas" not in text)


@pytest.mark.parametrize("text", ["Paul peut pas lancer P et exécuter Q.", "Tu peux pas lancer P et exécuter Q ?"])
def test_oral_negated_operator_keeps_the_coordination_open(text):
    f = parse_utterance(text)
    q = f.units[1]
    assert (q.pragmatic, q.embedded_under, q.polarity) == ("EMBEDDED", "u1", "positive")
    assert f"negated_scope_open:{q.id}" in f.ambiguities and not _gate(f)[q.id]


def test_oral_declarative_prohibition_is_not_confirmed():
    f = parse_utterance("Tu dois pas exécuter le build.")
    assert f.units[0].pragmatic == "FORBIDDEN" and "NO_EXECUTE(build)" in f.constraints
    assert governable_summary(f)["confirmed_no_execute"] is False     # oral: never confirmed


@pytest.mark.parametrize("text", ["Tu peux lancer P ?", "Tu as pas à lancer P."])
def test_positive_and_pas_a_are_unchanged(text):
    f = parse_utterance(text)
    assert f.units[0].polarity == "positive"


@pytest.mark.parametrize("text", ["J'ai pas lancé P.", "Paul a pas lancé P.", "Paul a jamais lancé P."])
def test_oral_negation_after_an_auxiliary_is_never_a_realized_event(text):
    # same root: the oral negator after the auxiliary head was lost (ASSERTED_REALIZED)
    from app.semantic.lattice.event_index import build_frame_event_index
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.polarity, u.ne_omitted) == ("negative", True)
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims[u.id] != "ASSERTED_REALIZED"
