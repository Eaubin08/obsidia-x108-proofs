"""Conditional "si": the protasis must never surface as an asserted fact.

Missed forms (proper-noun / bare nominal subject, elided s'il/s'ils/s'elle/
s'elles) follow the route already used by "Si le chef ..." / "Si tu ...":
protasis head HYPOTHETICAL, occurrence CONDITIONAL, CONDITIONS relation, and
no CAUSES from "si ..., alors ...". Adverbial "si" (si content, si bien fait)
is not a protasis.
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)  # apostrophe


def _analyse(text: str):
    frame = parse_utterance(text)
    return frame, build_frame_event_index(frame)


def _protasis_units(frame):
    comma = frame.raw.index(",")
    return [u for u in frame.units if u.span[0] < comma]


def _head(frame):
    return _protasis_units(frame)[0]


def _assert_conditional(text: str):
    frame, index = _analyse(text)
    head = _head(frame)
    kinds = {(r.kind, r.source) for r in frame.relations}

    assert head.pragmatic == "HYPOTHETICAL" and head.role in {"HYPOTHETICAL", "NEGATED"}, text
    assert ("CONDITIONS", head.id) in kinds, text
    assert "CAUSES" not in {r.kind for r in frame.relations}, text
    for unit in _protasis_units(frame):
        event = index.event_for(unit.id)
        assert event is None or event.occurrence_status.value != "ASSERTED_OCCURRED", (text, unit.id)
    return frame, index


@pytest.mark.parametrize("text", [
    "Si Paul lance le test, Marie attend.",
    "Si Paul a relancé le build, Marie attend.",
    "Si Nadia relance le build, Omar attend.",
    "Si Paul ne lance pas le test, Marie attend.",
    "Si Jean Dupont lance le test, Marie attend.",
])
def test_proper_noun_subject_opens_protasis(text):
    frame, index = _assert_conditional(text)
    head = _head(frame)
    if index.event_for(head.id) is not None and head.polarity == "positive":
        assert index.event_for(head.id).occurrence_status.value == "CONDITIONAL"


@pytest.mark.parametrize("text", [
    f"S{A}il lance le test, Marie attend.",
    f"S{A}il a lancé le test, Marie attend.",
    f"S{A}ils lancent le test, Marie attend.",
    f"S{A}elle lance le test, Marie attend.",
    f"S{A}elles lancent le test, Marie attend.",
])
def test_elided_si_opens_protasis(text):
    _assert_conditional(text)


@pytest.mark.parametrize("text", [
    "Si Paul lance le test, alors Marie attend.",
    "Si Paul a relancé le build, alors Marie relance le job.",
    f"S{A}il a relancé le build, alors Marie relance le job.",
])
def test_si_alors_is_condition_not_cause(text):
    _assert_conditional(text)


@pytest.mark.parametrize("text, meta", [
    ("Si Marie dit que Paul lance le test, Jean attend.", "SAY"),
    ("Si Marie croit que Paul lance le test, Jean attend.", "BELIEVE"),
    ("Si Marie apprend que Paul lance le test, Jean attend.", "LEARN"),
    ("Si Marie a dit que Paul a relancé le build, Jean attend.", "SAY"),
])
def test_nested_meta_event_inside_protasis_is_not_asserted(text, meta):
    frame, index = _assert_conditional(text)
    head = _head(frame)
    assert head.predicate == meta
    assert index.event_for(head.id).occurrence_status.value == "CONDITIONAL"


@pytest.mark.parametrize("text", [
    "Si le chef lance le test, Marie attend.",
    "Si tu lances le test, Marie attend.",
    "Si le chef a relancé le build, alors Marie attend.",
])
def test_existing_good_controls(text):
    _assert_conditional(text)


@pytest.mark.parametrize("text", [
    "Il est si content.",
    f"C{A}est si bien fait.",
    "Paul est si rapide que Marie attend.",
    f"Paul s{A}arrête.",
    f"Il s{A}est arrêté.",
])
def test_adverbial_si_and_reflexive_s_are_not_protasis(text):
    frame = parse_utterance(text)
    assert "CONDITIONS" not in {r.kind for r in frame.relations}
    assert all(u.pragmatic != "HYPOTHETICAL" for u in frame.units)


def test_explicit_causal_connectives_still_cause():
    for text in ("Paul a relancé le build donc Marie a relancé le job.",
                 "Paul a relancé le build, alors Marie a relancé le job."):
        assert "CAUSES" in {r.kind for r in parse_utterance(text).relations}, text


def test_conditional_si_adversarial_matrix():
    subjects = ("Paul", "Marie", "Nadia", "Omar", "Jean", "le chef", "la directrice", "tu", "il", "elle", "ils", "elles")
    elided = {"il": f"S{A}il", "ils": f"S{A}ils", "elle": f"S{A}elle", "elles": f"S{A}elles"}
    conj = {"tu": ("lances", "as relancé", "relanceras", "ne lances pas", "peux lancer"),
            "ils": ("lancent", "ont relancé", "relanceront", "ne lancent pas", "peuvent lancer"),
            "elles": ("lancent", "ont relancé", "relanceront", "ne lancent pas", "peuvent lancer")}
    default = ("lance", "a relancé", "relancera", "ne lance pas", "peut lancer")
    say = {"tu": "dis", "ils": "disent", "elles": "disent"}
    believe = {"tu": "crois", "ils": "croient", "elles": "croient"}
    metrics = dict.fromkeys(("CASES", "SI_ASSERTED_LEAK", "SI_CAUSAL_PROMOTION", "SI_ELISION_MISSED",
                             "SI_PROPER_NOUN_MISSED", "GOOD_CONTROL_REGRESSION", "NON_CONDITIONAL_DRIFT",
                             "CONDITIONAL_RECOGNIZED", "CONDITIONS_RELATIONS"), 0)

    def check(text, family):
        frame, index = _analyse(text)
        metrics["CASES"] += 1
        conditions = [r for r in frame.relations if r.kind == "CONDITIONS"]
        metrics["CONDITIONS_RELATIONS"] += len(conditions)
        if not conditions:
            metrics[{"elided": "SI_ELISION_MISSED", "proper": "SI_PROPER_NOUN_MISSED"}.get(family, "GOOD_CONTROL_REGRESSION")] += 1
        if "CAUSES" in {r.kind for r in frame.relations}:
            metrics["SI_CAUSAL_PROMOTION"] += 1
        for unit in _protasis_units(frame):
            event = index.event_for(unit.id)
            if event is not None and event.occurrence_status.value == "ASSERTED_OCCURRED":
                metrics["SI_ASSERTED_LEAK"] += 1
            if event is not None and event.occurrence_status.value == "CONDITIONAL":
                metrics["CONDITIONAL_RECOGNIZED"] += 1

    for subject, x, consequence in product(subjects, ("le test", "le build", "le job", "le script", "la suite", "le lot", "le déploiement"),
                                           ("Marie attend.", "alors Marie attend.", "Omar attend.")):
        family = "elided" if subject in elided else ("proper" if subject[0].isupper() else "control")
        opener = "Si " + subject if subject not in elided else None
        for verb in conj.get(subject, default):
            if opener:
                check(f"{opener} {verb} {x}, {consequence}", family if family != "elided" else "control")
            if subject in elided:
                check(f"{elided[subject]} {verb} {x}, {consequence}", "elided")
                check(f"Si {subject} {verb} {x}, {consequence}", "control")
        s_verb, b_verb = say.get(subject, "dit"), believe.get(subject, "croit")
        for nested in (f"{s_verb} que Tom a relancé {x}", f"{b_verb} que Tom relance {x}"):
            if subject in elided:
                check(f"{elided[subject]} {nested}, {consequence}", "elided")
            else:
                check(f"Si {subject} {nested}, {consequence}", family)

    for text in ("Il est si content.", f"C{A}est si bien fait.", "Paul est si rapide que Marie attend.",
                 f"Paul s{A}arrête.", "Paul a relancé le build, alors Marie attend."):
        frame = parse_utterance(text)
        if "CONDITIONS" in {r.kind for r in frame.relations} or any(u.pragmatic == "HYPOTHETICAL" for u in frame.units):
            metrics["NON_CONDITIONAL_DRIFT"] += 1

    assert metrics["CASES"] >= 2000
    assert metrics["CONDITIONAL_RECOGNIZED"] > 0 and metrics["CONDITIONS_RELATIONS"] > 0
    for key in ("SI_ASSERTED_LEAK", "SI_CAUSAL_PROMOTION", "SI_ELISION_MISSED", "SI_PROPER_NOUN_MISSED",
                "GOOD_CONTROL_REGRESSION", "NON_CONDITIONAL_DRIFT"):
        assert metrics[key] == 0, (key, metrics)


@pytest.mark.parametrize("text", [
    f"Lance le test s{A}il te plaît.",
    f"S{A}il vous plaît, lance le test.",
    f"Lance le test, s{A}il te plaît.",
])
def test_politeness_formula_keeps_request(text):
    from app.semantic.lattice.ir_projection import governable_summary

    frame = parse_utterance(text)
    assert governable_summary(frame)["requested_world_actions"] == ["EXECUTE"]
    assert "CONDITIONS" not in {r.kind for r in frame.relations}
