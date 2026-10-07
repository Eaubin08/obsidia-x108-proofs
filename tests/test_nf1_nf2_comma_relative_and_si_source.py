"""NF1 / NF2: comma relatives stay descriptive; a source after "si" keeps the protasis.

NF1: a comma-delimited "qui" relative ("Le script, qui lance Q, échoue.") is a relative of
its antecedent: never a definitive request, its object never absorbs the main predicate
("q échoue"), the unresolved main predicate is reported and the frame stays open.
NF2: a detached source right after "si" ("Si, selon Marie, P, Q.") qualifies the protasis:
"si" keeps governing it, the source is kept, the relative object never absorbs the
protasis predicate, the protasis stays named (conditional_protasis) and the frame open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _objects(f, lemma):
    return [[a.text for a in u.objects] for u in f.units if u.lemma == lemma]


def _kept(f):
    out = []
    for m in f.missing:
        a, b = map(int, m.split(":")[1].split("-"))
        out.append((f.raw[a:b], m.split(":", 2)[2]))
    return out


@pytest.mark.parametrize("text", ["Le script, qui lance Q, échoue.", "Paul, qui lance Q, échoue.",
                                  "Le script qui teste P, qui lance Q, échoue."])
def test_nf1_comma_qui_relative_is_descriptive(text):
    f = parse_utterance(text)
    assert governable_summary(f)["requested_world_actions"] == []
    assert not any(u.pragmatic == "REQUESTED" for u in f.units)
    assert _objects(f, "lancer") == [["q"]]
    assert any(s == "échoue" for s, _ in _kept(f)) and not f.closure


def test_nf1_comma_qui_relative_without_main_predicate():
    f = parse_utterance("Le script qui teste P, qui lance Q.")
    assert governable_summary(f)["requested_world_actions"] == []
    assert not any(u.pragmatic == "REQUESTED" for u in f.units)
    assert _objects(f, "lancer") == [["q"]] and _objects(f, "tester") == [["p"]]


@pytest.mark.parametrize("text,source", [("Si, selon Marie, le script qui teste P échoue, lance R.", "selon Marie"),
                                         ("Si, apparemment, le script qui teste P échoue, lance R.", "apparemment")])
def test_nf2_source_after_si_keeps_the_protasis(text, source):
    f = parse_utterance(text)
    kept = _kept(f)
    assert _objects(f, "tester") == [["p"]]
    assert ("échoue", "conditional_protasis") in kept
    assert any(s == source and "detached_source_of=" in why for s, why in kept)
    assert _objects(f, "lancer") == [["r"]] and not f.closure


def test_nf2_source_before_si_keeps_the_protasis():
    f = parse_utterance("Selon Marie, si le script qui teste P échoue, lance R.")
    kept = _kept(f)
    assert _objects(f, "tester") == [["p"]]
    assert ("échoue", "conditional_protasis") in kept
    assert any(s == "Selon Marie" for s, _ in kept) and not f.closure


@pytest.mark.parametrize("text", ["Lance Q.", "Le script que Paul lance et qui teste P échoue."])
def test_controls_unchanged(text):
    f = parse_utterance(text)
    if text == "Lance Q.":
        assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"] and f.closure
    else:
        assert governable_summary(f)["requested_world_actions"] == [] and not f.closure


def test_c3_comma_main_predicate_stays_ambiguous():
    f = parse_utterance("Le script qui teste P, lance Q.")
    assert "coordination_attachment_ambiguous:u2" in f.ambiguities and not f.closure
    assert not any(u.pragmatic == "REQUESTED" for u in f.units)


def test_nf1_comma_relative_closed_by_its_comma_keeps_coordinated_object():
    f = parse_utterance("Le script, qui lance Q et R, échoue.")
    assert _objects(f, "lancer") == [["q", "r"]] and governable_summary(f)["requested_world_actions"] == []
    assert any(s == "échoue" for s, _ in _kept(f)) and not f.closure


@pytest.mark.parametrize("text", ["Si, selon Marie, Paul lance P, lance R.", "Si, apparemment, Paul lance P, lance R."])
def test_nf3_source_after_si_keeps_condition_and_subjects(text):
    f = parse_utterance(text)
    p, r = f.units
    assert [(x.kind, x.source, x.target) for x in f.relations] == [("CONDITIONS", p.id, r.id)]
    assert p.pragmatic == "HYPOTHETICAL" and r.subject is None and not f.coordinations
    assert any(why.startswith(f"detached_source_of={p.id}") for _, why in _kept(f)) and not f.closure


def test_nf2_source_of_unresolved_protasis_is_kept():
    kept = _kept(parse_utterance("Si, selon Marie, le script échoue, lance R."))
    assert ("le script échoue", "conditional_protasis") in kept
    assert any(s == "selon Marie" and "detached_source_of=" in why for s, why in kept)


def test_nf4_sibling_comma_relative_in_protasis_keeps_the_protasis():
    f = parse_utterance("Si le script qui teste P, que Marie observe, échoue, lance R.")
    assert ("échoue", "conditional_protasis") in _kept(f)
    assert _objects(f, "tester") == [["p"]] and not f.closure
