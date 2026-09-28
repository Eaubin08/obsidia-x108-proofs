"""A CONDITIONS B: the consequent B is conditional content, never an asserted fact.

The parser's typed CONDITIONS relation drives it: B's occurrence becomes
CONDITIONAL unless B carries a stronger local signal (NEGATED, FUTURE,
UNCERTAIN, REPORTED, HYPOTHETICAL), which is preserved. The protasis, the
relation graph and non-conditional clauses are unchanged; embedded-content
factivity is out of scope.
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary

A = chr(39)
C = "CONDITIONAL"


def _pair(text: str):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    conditions = [r for r in frame.relations if r.kind == "CONDITIONS"]
    assert len(conditions) == 1, text
    relation = conditions[0]
    status = lambda pid: index.event_for(pid).occurrence_status.value if index.event_for(pid) else None
    return frame, index, relation, status(relation.source), status(relation.target)


@pytest.mark.parametrize("text", [
    "Si Paul lance le test, Marie relance le build.",
    "Si Paul a lancé le test, Marie a relancé le build.",
    "Si Paul lance le test, alors Marie relance le build.",
    f"S{A}il lance le test, Marie relance le build.",
    "Si le chef lance le test, Marie relance le build.",
    "Si tu as lancé le test, alors Marie a relancé le build.",
])
def test_consequent_is_conditional_not_asserted(text):
    frame, _, _, protasis, consequent = _pair(text)

    assert protasis == C
    assert consequent == C
    assert "CAUSES" not in {r.kind for r in frame.relations}


@pytest.mark.parametrize("text, expected", [
    ("Si Paul lance le test, Marie ne relance pas le build.", "NEGATED"),
    ("Si Paul lance le test, Marie relancera le build.", "FUTURE"),
    ("Si Paul lance le test, Marie pourrait relancer le build.", "UNCERTAIN"),
])
def test_stronger_local_consequent_signal_is_preserved(text, expected):
    _, _, _, protasis, consequent = _pair(text)
    assert (protasis, consequent) == (C, expected)


@pytest.mark.parametrize("text, meta", [
    ("Si Paul lance le test, Marie dit que Jean relance le build.", "SAY"),
    ("Si Paul lance le test, Marie croit que Jean relance le build.", "BELIEVE"),
    ("Si Paul lance le test, Marie apprend que Jean relance le build.", "LEARN"),
    ("Si Paul a lancé le test, Marie a dit que Jean a relancé le build.", "SAY"),
])
def test_consequent_meta_event_is_conditional(text, meta):
    frame, _, relation, _, consequent = _pair(text)
    assert frame.unit(relation.target).predicate == meta
    assert consequent == C


def test_a_moins_que_main_clause_is_conditional():
    _, _, relation, protasis, consequent = _pair("Paul relance le build à moins que Marie lance le test.")
    assert relation.evidence == "à moins que"
    assert (protasis, consequent) == (C, C)


@pytest.mark.parametrize("text", [
    "Paul lance le test, Marie relance le build.",
    "Paul a lancé le test et Marie a relancé le build.",
    "Paul a relancé le build, alors Marie a relancé le job.",
    "Paul a relancé le build donc Marie a relancé le job.",
])
def test_non_conditional_clauses_are_unaffected(text):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    assert "CONDITIONS" not in {r.kind for r in frame.relations}
    assert all(c.occurrence_status.value != C for c in index.events())


def test_politeness_formula_remains_a_request():
    frame = parse_utterance(f"S{A}il te plaît, lance le test.")
    assert governable_summary(frame)["requested_world_actions"] == ["EXECUTE"]
    assert "CONDITIONS" not in {r.kind for r in frame.relations}


def test_conditional_consequent_adversarial_matrix():
    openers = ("Si Paul", "Si Nadia", "Si Omar", "Si le chef", "Si la directrice", "Si tu", f"S{A}il", f"S{A}ils",
               f"S{A}elles", "Si elle")
    protasis_verb = {"Si tu": "lances", f"S{A}ils": "lancent", f"S{A}elles": "lancent"}
    consequents = (
        ("Marie relance {x}.", C), ("Marie a relancé {x}.", C), ("Marie ne relance pas {x}.", "NEGATED"),
        ("Marie relancera {x}.", "FUTURE"), ("Marie pourrait relancer {x}.", "UNCERTAIN"),
        ("Marie dit que Tom relance {x}.", C), ("Marie croit que Tom relance {x}.", C),
        ("Marie apprend que Tom relance {x}.", C), ("Marie a dit que Tom a relancé {x}.", C),
    )
    metrics = dict.fromkeys((
        "CASES", "CONSEQUENT_ASSERTED_LEAK", "PROTASIS_REGRESSION", "FALSE_CAUSES", "NEGATION_LOST",
        "FUTURE_LOST", "UNCERTAINTY_LOST", "UNEXPECTED_CONSEQUENT", "NON_CONDITIONAL_DRIFT", "POLITENESS_REGRESSION",
        "CONDITIONAL_PROTASIS_COUNT", "CONDITIONAL_CONSEQUENT_COUNT", "CONDITIONS_EDGE_COUNT",
    ), 0)
    lost = {"NEGATED": "NEGATION_LOST", "FUTURE": "FUTURE_LOST", "UNCERTAIN": "UNCERTAINTY_LOST"}
    things = ("le test", "le build", "le job", "le script", "la suite", "le lot")
    for opener, (consequent, expected), x, alors, protasis_object in product(
            openers, consequents, things, ("", "alors "), ("le test", "le déploiement")):
        verb = protasis_verb.get(opener, "lance")
        text = f"{opener} {verb} {protasis_object}, {alors}{consequent.format(x=x)}"
        frame, _, _, protasis, got = _pair(text)
        metrics["CASES"] += 1
        metrics["CONDITIONS_EDGE_COUNT"] += 1
        metrics["CONDITIONAL_PROTASIS_COUNT"] += protasis == C
        metrics["PROTASIS_REGRESSION"] += protasis != C
        metrics["FALSE_CAUSES"] += "CAUSES" in {r.kind for r in frame.relations}
        metrics["CONSEQUENT_ASSERTED_LEAK"] += got == "ASSERTED_OCCURRED"
        metrics["CONDITIONAL_CONSEQUENT_COUNT"] += got == C
        if got != expected:
            metrics[lost.get(expected, "UNEXPECTED_CONSEQUENT")] += 1
    for text in ("Paul lance le test, Marie relance le build.", "Paul a lancé le test et Marie a relancé le build.",
                 "Paul a relancé le build, alors Marie a relancé le job.", "Paul a relancé le build donc Marie a relancé le job."):
        frame = parse_utterance(text)
        index = build_frame_event_index(frame)
        metrics["NON_CONDITIONAL_DRIFT"] += any(c.occurrence_status.value == C for c in index.events())
    for text in (f"S{A}il te plaît, lance le test.", f"Lance le test s{A}il vous plaît."):
        metrics["POLITENESS_REGRESSION"] += governable_summary(parse_utterance(text))["requested_world_actions"] != ["EXECUTE"]

    assert metrics["CASES"] >= 2000
    for key in ("CONDITIONAL_PROTASIS_COUNT", "CONDITIONAL_CONSEQUENT_COUNT", "CONDITIONS_EDGE_COUNT"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("CONSEQUENT_ASSERTED_LEAK", "PROTASIS_REGRESSION", "FALSE_CAUSES", "NEGATION_LOST", "FUTURE_LOST",
                "UNCERTAINTY_LOST", "UNEXPECTED_CONSEQUENT", "NON_CONDITIONAL_DRIFT", "POLITENESS_REGRESSION"):
        assert metrics[key] == 0, (key, metrics)
