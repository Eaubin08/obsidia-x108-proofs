"""N5-R: a relative object never absorbs an unknown main predicate.

"Le script qui teste le build échoue": the NP parser took "le build échoue" as the relative
object (a false participant) and, in a protasis, the condition vanished and the frame
closed. An extended object NP that would consume all the remaining material of the clause
(leaving no main predicate where one is required) is not admissible: the object is bounded
to its safe nominal core (det + head) and the remainder stays explicit, unresolved main
content. Never "false known structure + unknown marker". A known main verb still bounds the
full NP ("le build rouge lance Q").
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _obj(f):
    return [a.text for a in next(u for u in f.units if u.lemma == "tester").objects]


def _kept(f):
    return [f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])] for m in f.missing]


@pytest.mark.parametrize("text", ["Le script qui teste le build échoue.",
                                  "Le script que Paul lance et qui teste le build échoue."])
def test_unknown_main_predicate_outside_object(text):
    f = parse_utterance(text)
    assert _obj(f) == ["le build"]
    assert "échoue" in _kept(f) and not f.closure


def test_protasis_condition_kept():
    f = parse_utterance("Si le script qui teste le build échoue, lance R.")
    assert _obj(f) == ["le build"]
    assert any(m.endswith(":conditional_protasis") for m in f.missing)
    assert "échoue" in _kept(f)
    lance = f.units[-1]
    assert lance.pragmatic == "REQUESTED" and governable_summary(f)["requested_world_actions"] == ["EXECUTE"]
    assert not f.closure


def test_extended_np_never_absorbs_the_main_predicate():
    f = parse_utterance("Le script qui teste le build rouge échoue.")
    assert all("échoue" not in a for a in _obj(f))
    assert any("échoue" in k for k in _kept(f)) and not f.closure


def test_known_main_verb_keeps_full_np():
    f = parse_utterance("Le script qui teste le build rouge lance Q.")
    assert _obj(f) == ["le build rouge"]
    assert next(u for u in f.units if u.lemma == "lancer").subject == "script"


@pytest.mark.parametrize("text", ["Si le script qui teste P, lance R.", "Si le script qui teste le build, lance R."])
def test_protasis_without_main_predicate_stays_open(text):
    # a following consequent never proves that the protasis has a main predicate
    f = parse_utterance(text)
    assert any(m.endswith(":main_predicate_unresolved") for m in f.missing) and not f.closure
    assert f.units[-1].pragmatic == "REQUESTED"
