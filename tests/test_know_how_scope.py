"""NF3a (fail-closed only): the content of savoir (KNOW_HOW) is never an addressee request.

"Paul ne sait ni lancer P ni exécuter Q" and "Paul sait lancer P et
exécuter Q": KNOW_HOW was neither admitted under verbal ni nor shared over a
coordination, so the infinitives became injunctive REQUESTED units with a
gate. The sharing parity of KNOW_HOW is not decided here. Instead:
- ni under savoir: every ni infinitive stays EMBEDDED under the exact
  savoir unit, named negated_scope_open (as the unshared desire, A1a);
- a bare infinitive coordinated after a savoir chain stays EMBEDDED under
  that exact host unit, named know_how_scope_open.
Both markers block closure; no modality, polarity or subject is copied, no
gate is kept.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _view(text):
    f = parse_utterance(text)
    return f, {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", [
    "Paul ne sait ni lancer P ni exécuter Q.",
    "Je ne sais ni lancer P ni exécuter Q.",
    "Paul ne sait ni lancer P, ni exécuter Q.",
])
def test_ni_under_savoir_is_open_never_requested(text):
    f, gate = _view(text)
    (gov,) = [u for u in f.units if u.lemma == "savoir"]
    members = [u for u in f.units if u is not gov]
    assert len(members) == 2
    for u in members:
        assert u.pragmatic == "EMBEDDED" and not gate[u.id] and u.embedded_under == gov.id
        assert f"negated_scope_open:{u.id}" in f.ambiguities
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text,n_open", [
    ("Paul sait lancer P et exécuter Q.", 1),
    ("Paul sait lancer P, exécuter Q.", 1),
    ("Paul sait lancer P ou exécuter Q.", 1),
    ("Paul ne sait pas lancer P et exécuter Q.", 1),
    ("Sais-tu lancer P et exécuter Q ?", 1),
    ("Paul sait lancer P, exécuter Q et arrêter R.", 2),
])
def test_infinitive_after_savoir_chain_is_open_never_requested(text, n_open):
    f, gate = _view(text)
    host = f.units[0]
    assert host.modality == "KNOW_HOW"
    opened = f.units[1:]
    assert len(opened) == n_open
    for u in opened:
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in REQUESTS and not gate[u.id]
        assert (u.modality, u.subject) == (None, None) and u.embedded_under == host.id
        assert f"know_how_scope_open:{u.id}" in f.ambiguities
    assert f.closure is False


@pytest.mark.parametrize("text", [
    "Paul sait lancer P.", "Paul ne sait pas lancer P.", "Je sais que Paul lance P.",
    "Paul sait lancer P et Nadia exécute Q.", "Paul veut lancer P et exécuter Q.",
])
def test_outside_the_ticket_nothing_is_marked(text):
    f = parse_utterance(text)
    assert not any(a.startswith("know_how_scope_open") for a in f.ambiguities)
