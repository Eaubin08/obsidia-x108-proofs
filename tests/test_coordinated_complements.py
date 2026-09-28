"""Coordinated "que" complements: "V que P et que Q" (coordination doctrine Q2).

With a unique syntactic governor, P and Q are sibling complements of that
governor, linked by COORDINATES(P, Q). Q never becomes a relative of P.
When several governors stay compatible, Q is never resolved to one of them
nor promoted to an assertion.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import extract_report_event_relations
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.event_extraction import extract_event_candidates

A = chr(39)
P = "Paul a lancé le test"
Q = "Nadia a lancé le build"

GOVERNORS = [
    ("Marie dit", "SAY"),
    ("Marie n" + A + "a pas dit", "SAY"),
    ("Marie croit", "BELIEVE"),
    ("Marie a appris", "LEARN"),
    ("Marie sait", "KNOW"),
    ("Marie a vu", "OBSERVE"),
    ("Paul confirme", "CONFIRM"),
    ("Marie espère", None),
]


def _frame(text):
    f = parse_utterance(text)
    units = {u.id: u for u in f.units}
    p = next(u for u in f.units if u.subject == "paul" and u.id != f.units[0].id)
    q = next(u for u in f.units if u.subject == "nadia")
    return f, units, p, q


def _incoming(f, uid):
    return [(r.kind, r.source, r.evidence) for r in f.relations if r.target == uid and r.kind != "COORDINATES"]


@pytest.mark.parametrize("gov,pred", GOVERNORS)
def test_sibling_complements_share_the_unique_governor(gov, pred):
    f, units, p, q = _frame(f"{gov} que {P} et que {Q}.")
    g = f.units[0]
    assert p.embedded_under == g.id
    assert q.embedded_under == g.id
    assert [(k, s) for k, s, _ in _incoming(f, q.id)] == [(k, s) for k, s, _ in _incoming(f, p.id)]
    assert [e for _, _, e in _incoming(f, q.id)] == [e for _, _, e in _incoming(f, p.id)]
    assert (q.pragmatic, q.epistemic) == (p.pragmatic, p.epistemic)
    assert not any(r.source == p.id and r.target == q.id and r.kind == "EMBEDS" for r in f.relations)
    assert [(r.kind, r.evidence) for r in f.relations
            if {r.source, r.target} == {p.id, q.id}] == [("COORDINATES", "et que")]
    assert [(r.source, r.target) for r in f.relations if r.kind == "COORDINATES"] == [(p.id, q.id)]


@pytest.mark.parametrize("gov,pred", GOVERNORS)
def test_sibling_occurrence_mirrors_the_first_complement(gov, pred):
    f, units, p, q = _frame(f"{gov} que {P} et que {Q}.")
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    if p.id not in events:
        assert q.id not in events
        return
    ep, eq = events[p.id], events[q.id]
    assert eq.occurrence_claim == ep.occurrence_claim
    dp, dq = ep.occurrence_derivation, eq.occurrence_derivation
    assert dq.rule == dp.rule
    assert dq.provenance.get("edge") == dp.provenance.get("edge") != "relative"
    assert dq.provenance.get("governor") == dp.provenance.get("governor")
    assert dq.provenance.get("commitment") == dp.provenance.get("commitment")


def test_elided_second_complementizer_is_a_sibling():
    f = parse_utterance("Marie dit que Paul a lancé le test et qu" + A + "il a lancé le build.")
    say, p, q = f.units[0], f.units[1], f.units[2]
    assert p.embedded_under == q.embedded_under == say.id
    assert ("REPORTS", say.id, q.id) in {(r.kind, r.source, r.target) for r in f.relations}


def test_sibling_of_a_complement_with_lost_governor_shares_that_governance():
    f = parse_utterance(f"Marie se rend compte que {P} et que {Q}.")
    p, q = f.units[0], f.units[1]
    assert (q.embedded_under, q.pragmatic, q.epistemic) == (p.embedded_under, p.pragmatic, p.epistemic)
    assert q.epistemic == "UNRESOLVED_GOVERNANCE"
    assert [(r.kind, r.source, r.target, r.evidence) for r in f.relations] == [("COORDINATES", p.id, q.id, "et que")]
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims[p.id] == claims[q.id] == "UNRESOLVED"


def test_meta_layer_keeps_both_siblings_as_explicit_candidates():
    # meta_event_relations contract: several immediate targets stay AMBIGUOUS
    # (MULTIPLE_TARGETS_UNSUPPORTED), naming every candidate, never the first one.
    f = parse_utterance(f"Marie dit que {P} et que {Q}.")
    result = extract_report_event_relations(f, build_frame_event_index(f))
    assert result.relations == ()
    (target,) = result.targets
    assert target.resolution_status.value == "AMBIGUOUS" and target.target_event is None
    assert list(target.provenance["candidate_predicate_ids"]) == ["u2", "u3"]
    f = parse_utterance(f"Marie a appris que {P} et que {Q}.")
    result = extract_knowledge_event_targets(f, extract_event_candidates(f))
    assert result.relations == ()
    assert [list(t.provenance["candidate_predicate_ids"]) for t in result.targets] == [["u2", "u3"]]


def test_negated_governor_scopes_over_both_siblings():
    f = parse_utterance(f"Marie ne dit pas que {P} et que {Q}.")
    i = build_frame_event_index(f)
    claims = {c.predicate_ref: c for c in i.events()}
    assert claims["u2"].occurrence_derivation.rule == claims["u3"].occurrence_derivation.rule == "commitment:MENTIONED"


@pytest.mark.parametrize("text", [
    f"Marie dit que Jean croit que {P} et que {Q}.",
    f"Marie croit que Jean a appris que {P} et que {Q}.",
])
def test_multiple_compatible_governors_never_assert_q(text):
    f = parse_utterance(text)
    q = next(u for u in f.units if u.subject == "nadia")
    ev = {c.predicate_ref: c for c in build_frame_event_index(f).events()}[q.id]
    assert ev.occurrence_claim.value not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
    assert q.embedded_under is not None


@pytest.mark.parametrize("text,expected", [
    (f"{P} et {Q}.", [("COORDINATES", "u1", "u2", "et")]),
    ("Paul a lancé le test que Nadia a préparé.", None),
    ("Marie dit que le test que Paul a lancé a échoué.", None),
])
def test_controls_without_coordinated_complements_are_unchanged(text, expected):
    f = parse_utterance(text)
    assert not any(r.evidence == "et que" for r in f.relations)
    if expected is not None:
        assert sorted((r.kind, r.source, r.target, r.evidence) for r in f.relations) == expected
