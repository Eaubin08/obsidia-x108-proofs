"""NF3a safety + H15 doctrine (D4): the content of savoir (KNOW_HOW) is never an addressee request.

NF3a made the infinitives under savoir fail-closed (open, never injunctive)
while KNOW_HOW sharing parity was held. H15 (D4, approved) decides it:
KNOW_HOW is a modality (not a capability, permission or authority), shared
over a coordination like devoir / pouvoir / vouloir (shared_modality);
"ne sait ni ... ni ..." is the explicit distributive negation
(ni_negative_coordination, every member negated, H01); "ne sait pas P et Q"
keeps its scope open (negated_scope_open, H01). In every case no member is
REQUESTED / FORBIDDEN and no gate is kept.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _view(text):
    f = parse_utterance(text)
    return f, {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", [
    "Paul ne sait ni lancer P ni exécuter Q.",
    "Je ne sais ni lancer P ni exécuter Q.",
    "Paul ne sait ni lancer P, ni exécuter Q.",
])
def test_ni_under_savoir_is_distributive_never_requested(text):
    f, gate = _view(text)
    members = [u for u in f.units if u.lemma in {"lancer", "exécuter"}]
    assert len(members) == 2
    assert any(c.construction == "ni_negative_coordination" for c in f.coordinations)
    for u in members:
        assert u.polarity == "negative" and u.pragmatic not in REQUESTS and not gate[u.id]
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


@pytest.mark.parametrize("text,n", [
    ("Paul sait lancer P et exécuter Q.", 2),
    ("Paul sait lancer P, exécuter Q.", 2),
    ("Paul sait lancer P ou exécuter Q.", 2),
    ("Sais-tu lancer P et exécuter Q ?", 2),
    ("Paul sait lancer P, exécuter Q et arrêter R.", 3),
])
def test_positive_know_how_is_shared_never_requested(text, n):
    f, gate = _view(text)
    assert len(f.units) == n and any(c.construction == "shared_modality" for c in f.coordinations)
    for u in f.units:
        assert u.modality == "KNOW_HOW" and u.pragmatic not in REQUESTS and not gate[u.id]
    assert not any(a.startswith(("know_how_scope_open", "negated_scope_open")) for a in f.ambiguities)


def test_negated_know_how_over_et_stays_open():
    f, gate = _view("Paul ne sait pas lancer P et exécuter Q.")
    q = f.units[1]
    assert q.pragmatic == "EMBEDDED" and not gate[q.id] and q.embedded_under == f.units[0].id
    assert f"negated_scope_open:{q.id}" in f.ambiguities and f.closure is False


@pytest.mark.parametrize("text", [
    "Paul sait lancer P.", "Paul ne sait pas lancer P.", "Je sais que Paul lance P.",
    "Paul sait lancer P et Nadia exécute Q.", "Paul veut lancer P et exécuter Q.",
])
def test_outside_the_ticket_nothing_is_marked(text):
    f = parse_utterance(text)
    assert not any(a.startswith("know_how_scope_open") for a in f.ambiguities)
