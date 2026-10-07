"""B3-G R1-R5: the relative / main-clause boundary.

The antecedent of a subject relative (a bare NP with no verb yet, possibly after "si", a
source marker, or coordinated) is followed by the relative's own chain, then by the main
predicate. The relative ends after its own chain (qui: verb + its object; que: subject +
verb); what follows is the antecedent's main predicate, whose subject is the antecedent
(never the relative's object), which inherits the antecedent's condition / source, and which
is reported when its verb is unknown (never an object, never dropped). Coordinated relatives
("que ... et qui ...") are sibling relatives. H11 option C applies to "que" relatives too.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _objs(f):
    return {u.lemma: [a.text for a in u.objects] for u in f.units}


def _req(f):
    return governable_summary(f)["requested_world_actions"]


# R1 ----------------------------------------------------------------------------------
@pytest.mark.parametrize("text,link", [("Le script que Paul lance et qui teste P échoue.", "COORDINATES"),
                                       ("Le script que Paul lance ou qui teste P échoue.", "ALTERNATIVE")])
def test_r1_coordinated_relatives(text, link):
    f = parse_utterance(text)
    t = next(u for u in f.units if u.lemma == "tester")
    assert t.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} and [a.text for a in t.objects] == ["p"]
    assert any(r.kind == link and r.target == t.id for r in f.relations)
    assert any("échoue" in f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])]
               for m in f.missing)
    assert _req(f) == [] and not f.closure


# R2 ----------------------------------------------------------------------------------
def test_r2_que_relative_homograph_under_imperative():
    f = parse_utterance("Lance le script que Paul a préparé et exécute Q.")
    e = next(u for u in f.units if u.lemma == "exécuter")
    assert e.pragmatic != "REQUESTED" and f"coordination_attachment_ambiguous:{e.id}" in f.ambiguities
    assert f.units[0].pragmatic == "REQUESTED" and not f.closure


# R3 ----------------------------------------------------------------------------------
@pytest.mark.parametrize("text", ["Si le script qui teste P échoue, lance R.",
                                  "Si le script qui teste P fonctionne, lance R.",
                                  "Si le script que Paul teste échoue, lance R."])
def test_r3_relative_in_protasis_keeps_condition_open(text):
    f = parse_utterance(text)
    lance = f.units[-1]
    assert lance.pragmatic == "REQUESTED" and _req(f) == ["EXECUTE"]
    assert all(a.split() == [a] or "échoue" not in a for objs in _objs(f).values() for a in objs)
    assert any("conditional_protasis" in m for m in f.missing) and not f.closure


def test_r3_known_main_predicate_conditions_consequent():
    f = parse_utterance("Si le script qui teste P lance Q, lance R.")
    assert ("CONDITIONS", "u2", "u3") in [(r.kind, r.source, r.target) for r in f.relations]
    assert f.unit("u2").subject == "script"


# R4 ----------------------------------------------------------------------------------
@pytest.mark.parametrize("text,kind", [("Paul et Nadia qui testent P lancent Q.", "AND"),
                                       ("Paul ou Nadia qui testent P lancent Q.", "OR")])
def test_r4_coordinated_antecedent_is_main_subject(text, kind):
    f = parse_utterance(text)
    main = next(u for u in f.units if [a.text for a in u.objects] == ["q"])
    assert main.subject != "p" and "paul" in main.subject and "nadia" in main.subject
    (c,) = [c for c in f.coordinations if c.construction == "coordinated_subject"]
    assert (c.kind, c.member_texts, c.host) == (kind, ("paul", "nadia"), main.id)


# R5 ----------------------------------------------------------------------------------
@pytest.mark.parametrize("text,epi", [("Apparemment le script qui teste P a lancé Q.", "INFERRED"),
                                      ("Selon Marie, le script qui teste P a lancé Q.", "HUMAN_SOURCE")])
def test_r5_source_scopes_main_predicate(text, epi):
    f = parse_utterance(text)
    main = next(u for u in f.units if [a.text for a in u.objects] == ["q"])
    assert main.subject == "script" and main.epistemic == epi
    occ = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    assert occ[main.id] != "ASSERTED_REALIZED"


# controls ----------------------------------------------------------------------------
def test_h11_homograph_control_unchanged():
    f = parse_utterance("Lance le script qui teste P et exécute Q.")
    assert f.units[0].pragmatic == "REQUESTED" and f.unit("u3").pragmatic == "EMBEDDED"
    assert "coordination_attachment_ambiguous:u3" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text,subject", [("Le script qui lance P lance Q.", "script"),
                                          ("Paul qui lance P lance Q.", "paul")])
def test_n6_control(text, subject):
    f = parse_utterance(text)
    assert f.unit("u2").subject == subject and f.closure
