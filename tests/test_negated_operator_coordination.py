"""G1: a bare infinitive coordinated under a negated operator is never a request.

"Paul ne peut pas lancer P et exécuter Q": ¬(P∧Q), ¬P∧¬Q or ¬P∧Q is held
doctrine (H01). Only the negated "vouloir" kept Q open; under a negated
"pouvoir", near-future "aller" or recent-past "venir de" the host was not
shared (its scope is open) and Q fell back to a subject-less injunctive
infinitive: an independent REQUESTED, gated, requested at runtime.

In every reading Q is content under that exact operator, never an addressee
request (CONTENT_UNDER_NEGATED_OPERATOR != ADDRESSEE_REQUEST): Q is kept,
embedded under the operator unit, no polarity is copied onto it, the open
scope is named (negated_scope_open) and blocks closure.

"Paul (ne) vient (pas) lancer P" (venir + infinitive of motion, no
construction for it) dropped "vient" and its subject and made P an injunction:
the infinitive takes the existing unrecognised-governor contract, and a bare
infinitive coordinated after such a governed infinitive takes it too, never
an injunction.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

_REQ = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


def _q(f):
    (q,) = [u for u in f.units if u.lemma == "exécuter"]
    return q


@pytest.mark.parametrize("text", [
    "Paul ne peut pas lancer P et exécuter Q.",
    "Paul ne pouvait pas lancer P et exécuter Q.",
    "Paul ne va pas lancer P et exécuter Q.",
    "Je ne peux pas lancer P, exécuter Q.",
    "Paul ne peut pas lancer P ou exécuter Q.",
    "Paul ne peut pas lancer P puis exécuter Q.",
    "Paul ne peut pas lancer P mais exécuter Q.",
    "Ne peux-tu pas lancer P et exécuter Q ?",
])
def test_member_under_negated_operator_is_open_content(text):
    f = parse_utterance(text)
    host = f.units[0]
    q = _q(f)
    assert host.polarity == "negative" and host.lemma == "lancer"
    assert [a.head for a in q.objects] == ["q"]                           # Q kept
    assert q.pragmatic == "EMBEDDED" and q.pragmatic not in _REQ and not _gate(f)[q.id]
    assert (q.polarity, q.negator) == ("positive", None)                   # no polarity copied
    assert q.embedded_under == host.id
    assert f"negated_scope_open:{q.id}" in f.ambiguities
    # H10 (requalified): the host under the negated operator keeps its request reading
    # ("launch P"), the open member Q is never requested
    assert governable_summary(f)["requested_action_surfaces"] == (
        [host.surface] if host.pragmatic == "INDIRECT_REQUEST" else [])
    assert not f.closure


@pytest.mark.parametrize("text", [
    "Paul vient lancer P et exécuter Q.",
    "Paul ne vient pas lancer P et exécuter Q.",
    "Je viens lancer P et exécuter Q.",
    "Paul aime lancer P et exécuter Q.",
    "Paul n'aime pas lancer P et exécuter Q.",
])
def test_infinitives_under_an_unrecognised_governor_are_never_requests(text):
    f = parse_utterance(text)
    gate = _gate(f)
    assert [u.lemma for u in f.units] == ["lancer", "exécuter"]
    for u in f.units:
        assert u.pragmatic == "EMBEDDED" and not gate[u.id] and u.subject is None
        assert f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
    assert governable_summary(f)["requested_world_actions"] == []
    assert not f.closure


@pytest.mark.parametrize("text", ["Paul vient lancer P et ne pas exécuter Q.", "Paul aime lancer P et ne pas exécuter Q.",
                                  "Paul lance P et ne pas exécuter Q."])
def test_locally_negated_member_under_unrecognised_governor_is_never_asserted(text):
    from app.semantic.lattice.event_index import build_frame_event_index
    f = parse_utterance(text)
    q = f.units[-1]
    assert (q.pragmatic, q.polarity) == ("EMBEDDED", "negative") and not f.constraints
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims[q.id] == "NO_ASSERTION"


@pytest.mark.parametrize("text,expected", [
    ("Lance P et exécute Q.", [("REQUESTED", True), ("REQUESTED", True)]),
    ("Ne lance pas P et exécute Q.", [("FORBIDDEN", False), ("REQUESTED", True)]),
    ("Veuillez lancer P et exécuter Q.", [("REQUESTED", True), ("REQUESTED", True)]),
    ("Viens lancer P.", [("REQUESTED", True)]),
    ("Tu viens lancer P ?", [("INDIRECT_REQUEST", True)]),  # H09 (requalified): question_or_request
    ("Paul peut lancer P et exécuter Q.", [("ASSERTED", False), ("ASSERTED", False)]),
    ("Paul va lancer P et exécuter Q.", [("ASSERTED", False), ("ASSERTED", False)]),
])
def test_real_directives_and_shared_positive_operators_are_unchanged(text, expected):
    f = parse_utterance(text)
    gate = _gate(f)
    assert [(u.pragmatic, gate[u.id]) for u in f.units] == expected
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_negated_desire_contract_is_unchanged():
    f = parse_utterance("Paul ne veut pas lancer P et exécuter Q.")
    q = _q(f)
    assert (q.pragmatic, q.embedded_under) == ("EMBEDDED", "u1")
    assert f.ambiguities == (f"negated_scope_open:{q.id}",)
