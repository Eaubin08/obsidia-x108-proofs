"""Final SENS safety remediation: F-EV, A, C1, C3.

F-EV: a source / evidential marker survives when the main predicate after a relative stays
unanalysed (reported as a detached source of that unresolved content).
A: a non-empty predication without any unit (copula: "Le script est prêt.") is reported,
never a zero representation; no action, no occurrence is invented.
C1: a comma-separated relative ("..., que Marie observe et qui teste P échoue") is a sibling
relative: the relative object never absorbs the unresolved main predicate.
C3: "Le script qui teste P, lance Q.": imperative or main predicate of the antecedent is not
decided: never a definitive REQUESTED; the ambiguity is named, possible request exposed,
frame open. A genuine imperative stays a request.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _kept(f):
    out = []
    for m in f.missing:
        a, b = map(int, m.split(":")[1].split("-"))
        out.append((f.raw[a:b], m.split(":", 2)[2]))
    return out


@pytest.mark.parametrize("text,source", [("Apparemment, le script qui teste P échoue.", "Apparemment"),
                                         ("Selon Marie, le script qui teste P échoue.", "Selon Marie"),
                                         ("Apparemment, le script qui teste lentement le build échoue.", "Apparemment")])
def test_fev_source_kept_with_unresolved_main(text, source):
    f = parse_utterance(text)
    kept = _kept(f)
    assert any(span == "échoue" for span, _ in kept)
    assert any(span == source and link.startswith("detached_source_of") for span, link in kept)
    assert not f.closure


def test_fev_relative_details_kept():
    f = parse_utterance("Apparemment, le script qui teste lentement le build échoue.")
    t = next(u for u in f.units if u.lemma == "tester")
    assert [a.text for a in t.objects] == ["le build"] and [(m.unit, m.value) for m in f.manner_modifiers] == [(t.id, "SLOW")]


@pytest.mark.parametrize("text", ["Le script est prêt.", "Le build est rouge."])
def test_a_copula_never_zero_representation(text):
    f = parse_utterance(text)
    assert _kept(f) == [(text[:-1], "root")]
    assert governable_summary(f)["requested_world_actions"] == [] and not f.units and not f.closure


def test_a_control_unknown_predicate_still_reported():
    assert _kept(parse_utterance("Cette clé permet l'accès.")) == [("Cette clé permet l'accès", "root")]


def test_c1_comma_sibling_relative_no_false_object():
    f = parse_utterance("Le script que Paul lance, que Marie observe et qui teste P échoue.")
    t = next(u for u in f.units if u.lemma == "tester")
    assert [a.text for a in t.objects] == ["p"]
    assert any(span == "échoue" for span, _ in _kept(f)) and not f.closure
    o = next(u for u in f.units if u.lemma == "observer")
    assert any(r.kind == "COORDINATES" and {r.source, r.target} == {o.id, t.id} for r in f.relations)


def test_c3_comma_relative_request_stays_ambiguous():
    f = parse_utterance("Le script qui teste P, lance Q.")
    lance = next(u for u in f.units if u.lemma == "lancer")
    assert lance.pragmatic != "REQUESTED"
    assert f"coordination_attachment_ambiguous:{lance.id}" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Lance Q.", "Le script qui teste P, lancez Q."])
def test_c3_genuine_imperative_kept(text):
    f = parse_utterance(text)
    assert any(u.pragmatic == "REQUESTED" and u.lemma == "lancer" for u in f.units)
