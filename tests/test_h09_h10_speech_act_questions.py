"""H09 / H10: speech-act closure of questions.

H09: a speech-act ambiguity (ability_permission_or_request, desire_or_request,
question_or_request) keeps both readings canonically and never blocks closure by itself;
a possible request keeps its gate (SPEECH_ACT != AUTHORITY). Structural ambiguity still
blocks. H10: a negated question operator ("Ne peux-tu pas lancer P ?", "Tu ne dois pas
lancer P ?") is never a prohibition: no FORBIDDEN, no NO_EXECUTE, no confirmed no-execute;
its act stays open (negated_speech_act_open, non-blocking) and its request reading (do P)
keeps the gate. A negated requested content ("et ne pas exécuter Q") stays a prohibition.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _amb(f, kind):
    return [a for a in f.ambiguities if a.startswith(kind + ":")]


@pytest.mark.parametrize("text,family", [
    ("Peux-tu lancer P ?", "ability_permission_or_request"),
    ("Veux-tu lancer P ?", "desire_or_request"),
    ("Tu veux lancer P ?", "desire_or_request"),
    ("Tu viens lancer P ?", "question_or_request"),
    ("Viens-tu lancer P ?", "question_or_request"),
    ("Dois-tu lancer P ?", "question_or_request"),
])
def test_speech_act_ambiguity_double_reading_gate_closure(text, family):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.predicate, u.pragmatic, u.subject, tuple(a.text for a in u.objects)) == \
        ("EXECUTE", "INDIRECT_REQUEST", "tu", ("p",))
    assert u.role == "AMBIGUOUS_REQUEST" and u.request_target == "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"
    assert _amb(f, family) == ["%s:u1" % family]
    s = governable_summary(f)
    assert s["requested_world_actions"] == ["EXECUTE"] and not s["confirmed_no_execute"]
    assert f.closure and not f.closure_blockers


@pytest.mark.parametrize("text", [
    "Ne peux-tu pas lancer P ?", "Tu ne peux pas lancer P ?",
    "Tu ne dois pas lancer P ?", "Ne dois-tu pas lancer P ?",
])
def test_negated_question_is_never_a_prohibition(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == "INDIRECT_REQUEST" and u.pragmatic != "FORBIDDEN"
    assert u.role == "AMBIGUOUS_REQUEST" and u.request_target == "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"
    assert tuple(a.text for a in u.objects) == ("p",)
    assert _amb(f, "negated_speech_act_open") == ["negated_speech_act_open:u1"]
    assert _amb(f, "ability_permission_or_request") + _amb(f, "question_or_request")
    s = governable_summary(f)
    assert not f.constraints and not s["confirmed_no_execute"] and not s["negated_execute_surfaces"]
    assert s["requested_world_actions"] == ["EXECUTE"]
    assert f.closure


@pytest.mark.parametrize("text", ["Tu ne dois pas lancer P.", "Ne lance pas P."])
def test_genuine_prohibition_kept(text):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units] == ["FORBIDDEN"]
    s = governable_summary(f)
    assert f.constraints == ("NO_EXECUTE(p)",) and s["confirmed_no_execute"]
    assert s["requested_world_actions"] == []


def test_negated_requested_member_stays_prohibition():
    f = parse_utterance("Peux-tu lancer P et ne pas exécuter Q ?")
    assert [(u.pragmatic, u.polarity, tuple(a.text for a in u.objects)) for u in f.units] == [
        ("INDIRECT_REQUEST", "positive", ("p",)), ("FORBIDDEN", "negative", ("q",))]
    s = governable_summary(f)
    assert f.constraints == ("NO_EXECUTE(q)",) and s["confirmed_no_execute"]
    assert s["requested_action_surfaces"] == ["lancer"] and not _amb(f, "negated_speech_act_open")


def test_question_without_request_reading_has_no_gate():
    f = parse_utterance("Paul lance-t-il le test ?")
    assert [u.pragmatic for u in f.units] == ["ASKED"]
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure


def test_structural_ambiguity_still_blocks():
    f = parse_utterance("Ne peux-tu ni lancer P ni exécuter Q ?")
    assert not f.closure
    assert any("negated_scope_open" in b for b in f.closure_blockers)
    assert not f.constraints and not governable_summary(f)["confirmed_no_execute"]


@pytest.mark.parametrize("text", [
    "Tu peux pas ne pas lancer P ?", "Ne peux-tu pas ne pas lancer P ?", "Tu ne dois pas ne pas lancer P ?",
])
def test_negated_operator_over_negated_content_stays_open(text):
    # H10 option A: the request reading would be "do not launch P" (not represented): no gate
    # (never a false request to launch P), never a prohibition, frame open
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == "INDIRECT_REQUEST" and u.request_target == "NONE"
    assert _amb(f, "negated_speech_act_open") == ["negated_speech_act_open:u1"]
    assert _amb(f, "negated_scope_open") == ["negated_scope_open:u1"]
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and not f.constraints and not s["confirmed_no_execute"]
    assert not f.closure


def test_requested_negated_content_is_a_prohibition():
    f = parse_utterance("Peux-tu ne pas lancer P ?")
    assert [u.pragmatic for u in f.units] == ["FORBIDDEN"] and f.constraints == ("NO_EXECUTE(p)",)
