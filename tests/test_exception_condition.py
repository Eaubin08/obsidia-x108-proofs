"""N10: an exception condition ("sauf si", "excepté si", "à moins que") is never a plain "si".

"sauf si P" was not recognised: "sauf" was absorbed into the main object
("r sauf", even in the constraint NO_EXECUTE(r sauf)) and "si P" became an
ordinary protasis, CONDITIONS(P -> R): the exception read as its opposite.
"à moins que P" was already an ordinary CONDITIONS(P -> R), distinguished
by its evidence text only.

The final representation of an exception condition is held (H17:
EXCEPTION-CONDITION-RELATION). Safety only: the connector opens its clause
(no object corruption), no CONDITIONS is emitted for the family, the
exception and its possible host(s) are named (exception_condition_open,
closure blocker; a coordinated host group is listed, never one chosen by
proximity), and their occurrence stays unresolved (never promoted by the
missing relation). Ordinary "si" is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _claims(f):
    return {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text", ["Lance R sauf si Paul lance P.", "Lance R excepté si Paul lance P.",
                                  "Lance R à moins que Paul lance P.", "Lance R sauf s'il lance P.",
                                  "Lance R, sauf si Paul lance P."])
def test_exception_condition_is_named_not_a_condition(text):
    f = parse_utterance(text)
    r, p = f.units[0], f.units[1]
    assert [a.text for a in r.objects] == ["r"]                               # no "r sauf"
    assert p.pragmatic == "HYPOTHETICAL"
    assert not any(x.kind == "CONDITIONS" for x in f.relations)
    # H17 A (requalified, formerly named open, closure held): one structural host ->
    # EXCEPTS(exception -> host); the request keeps its gate; closure no longer held
    assert [(x.kind, x.source, x.target) for x in f.relations] == [("EXCEPTS", p.id, r.id)]
    assert not any(a.startswith("exception_condition_open") for a in f.ambiguities)
    assert r.pragmatic == "REQUESTED" and f.closure


def test_negated_host_constraint_targets_exactly_r():
    f = parse_utterance("Ne lance pas R sauf si Paul lance P.")
    assert f.constraints == ("NO_EXECUTE(r)",)
    assert governable_summary(f)["confirmed_no_execute"] is True
    assert not any(x.kind == "CONDITIONS" for x in f.relations)


@pytest.mark.parametrize("text", ["Paul a lancé R sauf si Nadia a lancé P.", "Paul a lancé R à moins que Nadia ait lancé P."])
def test_host_occurrence_is_never_promoted(text):
    f = parse_utterance(text)
    claims = _claims(f)
    assert claims[f.units[0].id] not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}


def test_coordinated_host_group_is_listed_not_chosen():
    f = parse_utterance("Lance R et exécute Q à moins que Paul lance P.")
    r, q, p = f.units
    assert f"exception_condition_open:{p.id}:host={r.id},{q.id}" in f.ambiguities
    assert not any(x.kind == "CONDITIONS" for x in f.relations)


def test_exception_with_unknown_verb_is_reported():
    f = parse_utterance("Lance R sauf si Paul valide P.")
    assert any(m.startswith("unanalyzed_predicative_content:") for m in f.missing) and not f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul lance P.", "Lance tout sauf P."])
def test_ordinary_si_and_prepositional_sauf_are_unchanged(text):
    f = parse_utterance(text)
    assert not any(a.startswith("exception_condition_open") for a in f.ambiguities)


def test_member_after_an_exception_is_never_attached_by_proximity():
    # the G5 contract holds for the exception family: ambiguous member = possible request only
    f = parse_utterance("Lance R sauf si Paul lance P et exécute Q.")
    q = f.units[-1]
    assert (q.pragmatic, q.role) == ("EMBEDDED", "REQUEST")
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    forced = parse_utterance("Lance R sauf si tu veux lancer P et exécute Q.")
    r, p, q2 = forced.units
    assert q2.pragmatic == "REQUESTED"
    assert f"exception_condition_open:{p.id}:host={r.id},{q2.id}" in forced.ambiguities
