"""H11 option C: "R si P et Q" attaches Q only where morphology licenses a host.

- a bare infinitive (infinitive morphology only, no subject) continuing the modal chain of
  a postposed protasis stays in the protasis, by parity with the preposed form: it joins
  the conjunctive protasis whose coordination conditions R; never a request;
- a form that is only a main-clause imperative ("exécutez", "lance" after a verbless
  protasis) belongs to the main clause: its request and gate are kept;
- otherwise (3sg / imperative homography "exécute", infinitive after a finite protasis,
  "ou", "puis", "de sorte que", "jusqu'à ce que"): coordination_attachment_ambiguous, frame
  open, the possible request kept fail-closed; never the nearest host.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _rels(f):
    return [(r.kind, r.source, r.target) for r in f.relations]


def _prag(f):
    return [(u.lemma, u.pragmatic) for u in f.units]


def _req(f):
    return governable_summary(f)["requested_action_surfaces"]


@pytest.mark.parametrize("text,modality", [
    ("Lance R si Paul veut lancer P et exécuter Q.", "veut"),
    ("Lance R si Paul doit lancer P et exécuter Q.", "doit"),
])
def test_postposed_modal_continuation_stays_in_protasis(text, modality):
    f = parse_utterance(text)
    assert _prag(f) == [("lancer", "REQUESTED"), ("lancer", "HYPOTHETICAL"), ("exécuter", "HYPOTHETICAL")]
    (c,) = f.coordinations
    assert c.kind == "AND" and c.members == ("u2", "u3")
    assert ("COORDINATES", "u2", "u3") in _rels(f) and ("CONDITIONS", c.id, "u1") in _rels(f)
    assert _req(f) == ["lance"]                          # Q is never a request
    assert not any(a.startswith("coordination_attachment_ambiguous") for a in f.ambiguities)
    assert f.closure


def test_postposed_matches_preposed_protasis():
    post = parse_utterance("Lance R si Paul veut lancer P et exécuter Q.")
    pre = parse_utterance("Si Paul veut lancer P et exécuter Q, lance R.")
    sig = lambda f: sorted((u.lemma, u.pragmatic, tuple(a.text for a in u.objects)) for u in f.units)
    assert sig(post) == sig(pre) and _req(post) == _req(pre) and post.closure == pre.closure


@pytest.mark.parametrize("text", [
    "Lance R si Paul lance P et exécute Q.",          # 3sg present / imperative homography
    "Lance R si Paul veut lancer P et exécute Q.",
    "Lance R si Paul lance P et exécuter Q.",         # infinitive after a finite protasis
    "Lance R si Paul lance P ou exécute Q.",
    "Lance R si Paul peut lancer P ou exécuter Q.",   # disjunctive protasis not represented
    "Lance R si Paul lance P, puis exécute Q.",
    "Lance R de sorte que Paul lance P et exécute Q.",
    "Lance R jusqu'à ce que Paul lance P et exécute Q.",
])
def test_ambiguous_morphology_stays_open_with_possible_request(text):
    f = parse_utterance(text)
    q = f.units[-1]
    assert q.lemma == "exécuter" and [a.text for a in q.objects] == ["q"]
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    assert q.pragmatic == "EMBEDDED" and q.pragmatic != "REQUESTED"
    assert not any(r[0] == "CONDITIONS" and q.id in r[1:] for r in _rels(f))   # no proximity
    assert not any(r[0] == "COORDINATES" and q.id in r[1:] for r in _rels(f))
    assert q.surface in _req(f)                       # possible request kept fail-closed
    assert not f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul lance P et exécutez Q.",
                                  "Lance R si Paul veut lancer P et exécutez Q."])
def test_imperative_only_form_is_main_clause_request(text):
    f = parse_utterance(text)
    q = f.units[-1]
    assert q.pragmatic == "REQUESTED" and ("COORDINATES", "u1", q.id) in _rels(f)
    assert _req(f) == ["lance", "exécutez"]
    assert "condition_scope_ambiguous:u2" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul lance P.", "Si Paul lance P, lance R."])
def test_plain_condition_unchanged(text):
    f = parse_utterance(text)
    assert [r[0] for r in _rels(f)] == ["CONDITIONS"] and _req(f) == ["lance"] and f.closure


def test_negated_member_keeps_possible_prohibition():
    # "et ne pas exécuter Q": one reading is a main-clause prohibition: not joined to the
    # protasis, kept in doubt (never relaxes execution), attachment open
    f = parse_utterance("Lance R si Paul veut lancer P et ne pas exécuter Q.")
    q = f.units[-1]
    assert q.pragmatic == "FORBIDDEN" and f.constraints == ("NO_EXECUTE(q)",)
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities and not f.closure
