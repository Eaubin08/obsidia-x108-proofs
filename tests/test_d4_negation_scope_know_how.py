"""D4: D4-F1 / D4-F2 safety, then H01 (COORD-NEG-SCOPE) and H15 (KNOW_HOW parity).

D4-F1: "Marie sait comment lancer P et exécuter Q": the bare infinitive
coordinated after a governed WH infinitive fell back to an injunctive
REQUESTED; it now keeps that governed (interrogative) scope.

D4-F2: "Paul ne lance pas P et ne lance pas Q": a leading "ne" blocked subject
sharing, so the second member read as a subject-less imperative prohibition
(NO_EXECUTE, confirmed_no_execute) of a descriptive sentence; the subject is
now shared across the member's own negator.

H01: negation is shared only by explicit structure. "ni ... ni" is
distributive (ni_negative_coordination, every member negated, savoir
included). "ne V pas" over an "et" coordination whose scope the syntax does
not fix (bare infinitives under a negated operator, coordinated objects
under one negation) is named negated_scope_open (canonical unresolved; the
object case is an approved closed -> open change). A finite conjunct with its
own (or no) negation fixes its own polarity.

H15: KNOW_HOW is a modality (not capability, permission or authority): the
positive "sait lancer P et exécuter Q" shares it like the other modals
(shared_modality); negatives reuse H01. No request, no gate, no promotion.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


# ── H01 ──
@pytest.mark.parametrize("text", ["Paul ne doit ni lancer P ni exécuter Q.", "Paul ne veut ni lancer P ni exécuter Q.",
                                  "Paul ne peut ni lancer P ni exécuter Q."])
def test_h01_ni_ni_predicates_are_distributive(text):
    f = parse_utterance(text)
    assert any(c.construction == "ni_negative_coordination" for c in f.coordinations)
    assert all(u.polarity == "negative" for u in f.units)
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_h01_ni_ni_objects_are_distributive():
    f = parse_utterance("Paul ne lance ni P ni Q.")
    (u,) = f.units
    assert (u.negator, [a.text for a in u.objects]) == ("ni", ["p", "q"])
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


@pytest.mark.parametrize("text", ["Paul ne doit pas lancer P et exécuter Q.", "Paul ne peut pas lancer P et exécuter Q."])
def test_h01_negated_modal_et_scope_is_named(text):
    f = parse_utterance(text)
    assert f"negated_scope_open:{f.units[-1].id}" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Paul ne lance pas P et Q.", "Paul ne lance pas P ou Q."])
def test_h01_coordinated_objects_under_one_negation_are_named(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert f"negated_scope_open:{u.id}" in f.ambiguities and not f.closure      # closed -> open (approved)


def test_h01_finite_conjunct_fixes_its_own_polarity():
    f = parse_utterance("Paul ne lance pas P et exécute Q.")
    p, q = f.units
    assert (p.polarity, q.polarity, q.subject) == ("negative", "positive", "paul")
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_h01_positive_shared_modal_is_unchanged():
    f = parse_utterance("Paul doit lancer P et exécuter Q.")
    assert any(c.construction == "shared_modality" for c in f.coordinations) and f.closure


# ── H15 ──
@pytest.mark.parametrize("text", ["Marie sait lancer P et exécuter Q.", "Marie sait lancer P, exécuter Q."])
def test_h15_positive_know_how_is_shared(text):
    f = parse_utterance(text)
    assert any(c.construction == "shared_modality" for c in f.coordinations)
    assert all(u.modality == "KNOW_HOW" and u.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} for u in f.units)
    assert not any(_gate(f).values()) and governable_summary(f)["requested_world_actions"] == []
    assert not any(a.startswith(("know_how_scope_open", "negated_scope_open")) for a in f.ambiguities)


def test_h15_negative_ni_is_distributive():
    f = parse_utterance("Marie ne sait ni lancer P ni exécuter Q.")
    assert any(c.construction == "ni_negative_coordination" for c in f.coordinations)
    members = [u for u in f.units if u.lemma in {"lancer", "exécuter"}]
    assert len(members) == 2 and all(u.polarity == "negative" for u in members)
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_h15_negative_et_scope_is_named():
    f = parse_utterance("Marie ne sait pas lancer P et exécuter Q.")
    assert f"negated_scope_open:{f.units[-1].id}" in f.ambiguities and not f.closure


def test_h15_know_how_is_never_a_request_or_gate():
    f = parse_utterance("Marie sait lancer P.")
    (u,) = f.units
    assert u.pragmatic == "ASSERTED" and not _gate(f)[u.id]
