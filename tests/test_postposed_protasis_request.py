"""G5-R + N5: request attachment and condition attachment are independent axes.

G5-R (regression of G5): after a postposed protasis, every member was made an
ambiguous non-request, even when its morphology leaves a single reading
("Lance R si tu veux lancer P et exécute Q": "exécute" cannot continue a
protasis whose subject is "tu"; only the main imperative remains), and the
possible main-clause request of ambiguous members vanished from runtime.

- morphology-forced main imperative: REQUESTED, gated, coordinated with R;
- ambiguous member: never REQUESTED, exposed as a possible request through the
  existing runtime path (EMBEDDED + role REQUEST + ADDRESSEE target).

N5: a postposed protasis never takes the next main head as its target, and
when the clause it follows is a coordinated member ("R et Q si P", "R puis Q
si P", "R ou Q si P", "R, Q si P") its scope over the coordination is not
decided (H11): no CONDITIONS target is chosen (neither Q by proximity nor
R∧Q), condition_scope_ambiguous is named, P stays HYPOTHETICAL, closure open.
With a forced main member after the protasis, R stays conditioned and only
the extension of the condition to that member is named.
REQUEST != CONDITION_TARGET.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


def _rels(f):
    return {(r.kind, r.source, r.target) for r in f.relations}


@pytest.mark.parametrize("text", [
    "Lance R si tu veux lancer P et exécute Q.",
    "Lance R si nous lançons P et exécute Q.",
    "Lancez R si Paul lance P et exécutez Q.",
])
def test_morphology_forced_main_imperative_is_a_request(text):
    f = parse_utterance(text)
    r, p, q = f.units
    assert (q.lemma, q.pragmatic, _gate(f)[q.id]) == ("exécuter", "REQUESTED", True)
    assert ("COORDINATES", r.id, q.id) in _rels(f)
    assert ("CONDITIONS", p.id, r.id) in _rels(f)                       # R conditioned in every reading
    assert not any(x.kind == "CONDITIONS" and x.target == q.id for x in f.relations)   # never Q by proximity
    assert f"condition_scope_ambiguous:{p.id}" in f.ambiguities          # extension to Q open
    assert not any(a.startswith("coordination_attachment_ambiguous") for a in f.ambiguities)
    assert p.pragmatic == "HYPOTHETICAL" and not f.closure


@pytest.mark.parametrize("text", [
    "Lance R si Paul lance P et exécute Q.",      # exécute: 3sg (protasis) or imperative (main)
    "Lance R si vous lancez P et exécutez Q.",    # exécutez: 2pl (protasis) or imperative (main)
])  # H11 option C: "si Paul veut lancer P et exécuter Q" (modal continuation) joins the protasis
def test_ambiguous_member_is_a_possible_request_not_requested(text):
    f = parse_utterance(text)
    q = f.units[-1]
    assert q.pragmatic == "EMBEDDED" and q.role == "REQUEST" and not _gate(f)[q.id]   # not semantic REQUESTED
    assert q.surface in governable_summary(f)["requested_action_surfaces"]            # possible request exposed
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text,link", [
    ("Lance R et exécute Q si Paul lance P.", "COORDINATES"),
    ("Lance R puis exécute Q si Paul lance P.", "PRECEDES"),
    ("Lance R ou exécute Q si Paul lance P.", "ALTERNATIVE"),
    ("Lance R, exécute Q si Paul lance P.", None),
])
def test_condition_scope_over_a_coordination_is_named_not_chosen(text, link):
    f = parse_utterance(text)
    r, q, p = f.units
    assert (r.pragmatic, q.pragmatic, p.pragmatic) == ("REQUESTED", "REQUESTED", "HYPOTHETICAL")
    assert _gate(f)[r.id] and _gate(f)[q.id]
    assert not any(x.kind == "CONDITIONS" for x in f.relations)          # neither Q nor R∧Q chosen
    assert f"condition_scope_ambiguous:{p.id}" in f.ambiguities and not f.closure
    if link:
        assert (link, r.id, q.id) in _rels(f)


@pytest.mark.parametrize("text", ["Lance R et Q si Paul lance P.", "Lance R si Paul lance P."])
def test_single_predicate_host_keeps_its_condition(text):
    f = parse_utterance(text)
    assert ("CONDITIONS", "u2", "u1") in _rels(f) and f.closure
    assert not any(a.startswith("condition_scope_ambiguous") for a in f.ambiguities)


def test_preposed_protasis_is_unchanged():
    f = parse_utterance("Si Paul lance P, lance R.")
    assert ("CONDITIONS", "u1", "u2") in _rels(f) and f.closure
