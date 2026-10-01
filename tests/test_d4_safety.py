"""D4 safety: D4-F1 / D4-F2 (see test_d4_negation_scope_know_how for H01 / H15).

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


# ── D4-F1 ──
@pytest.mark.parametrize("text", ["Marie sait comment lancer P et exécuter Q.",
                                  "Marie sait comment lancer P, exécuter Q."])
def test_d4f1_member_after_wh_infinitive_keeps_governed_scope(text):
    f = parse_utterance(text)
    q = next(u for u in f.units if u.lemma == "exécuter")
    assert q.pragmatic == "EMBEDDED" and not _gate(f)[q.id]
    assert governable_summary(f)["requested_world_actions"] == []


@pytest.mark.parametrize("text", ["Lance P et exécute Q.", "Veuillez lancer P et exécuter Q."])
def test_d4f1_directive_controls_remain_requests(text):
    f = parse_utterance(text)
    assert all(u.pragmatic == "REQUESTED" and _gate(f)[u.id] for u in f.units)


# ── D4-F2 ──
@pytest.mark.parametrize("text", ["Paul ne lance pas P et ne lance pas Q.", "Paul ne lance pas P et n'exécute pas Q.",
                                  "Paul ne lance pas P et ne lance pas Q ?"])
def test_d4f2_negated_member_keeps_the_descriptive_subject(text):
    f = parse_utterance(text)
    q = f.units[-1]
    assert (q.subject, q.polarity) == ("paul", "negative") and q.pragmatic != "FORBIDDEN"
    assert f.constraints == ()
    s = governable_summary(f)
    assert s["confirmed_no_execute"] is False and s["requested_world_actions"] == []


@pytest.mark.parametrize("text", ["Ne lance pas P.", "Ne lance pas P et n'exécute pas Q."])
def test_d4f2_real_prohibitions_are_kept(text):
    f = parse_utterance(text)
    assert all(u.pragmatic == "FORBIDDEN" for u in f.units) and f.constraints
