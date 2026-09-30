"""A1b: a bare infinitive coordinated after a negated desire is never a request.

"Paul ne veut pas lancer P et exécuter Q": the negative scope (¬(P∧Q),
¬P∧¬Q or ¬P∧Q) is a held doctrine, so the desire is not shared; but in every
reading "exécuter Q" is the content of that desire, never an injunction to
the addressee. It was REQUESTED with a gate. Without choosing any polarity,
the infinitive (after "et", ",", "puis", "et puis", "ou" or "mais") now stays
EMBEDDED under the exact negated desire unit (EMBEDS, evidence
negated_scope_open) with the named structural ambiguity negated_scope_open,
which blocks semantic closure. Its own polarity, modality and subject stay
unset: nothing is copied from the host.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


@pytest.mark.parametrize("text,n_open", [
    ("Paul ne veut pas lancer P et exécuter Q.", 1),
    ("Je ne veux pas lancer P et exécuter Q.", 1),
    ("Paul ne veut pas lancer P, exécuter Q.", 1),
    ("Paul ne veut pas lancer P puis exécuter Q.", 1),
    ("Paul ne veut pas lancer P et puis exécuter Q.", 1),
    ("Paul ne veut pas lancer P ou exécuter Q.", 1),
    ("Paul ne veut plus lancer P et exécuter Q.", 1),
    ("Paul ne voudrait pas lancer P, exécuter Q.", 1),
    ("Paul ne veut pas lancer P, exécuter Q et arrêter R.", 2),
    ("Tu ne veux pas lancer P et exécuter Q ?", 1),
    # NF1: "mais" joins the same open scope (its contrast relation is kept)
    ("Paul ne veut pas lancer P mais exécuter Q.", 1),
    ("Je ne veux pas lancer P mais exécuter Q.", 1),
    ("Paul ne voudrait pas lancer P mais exécuter Q.", 1),
    ("Paul ne veut plus lancer P mais exécuter Q.", 1),
])
def test_infinitive_after_negated_desire_stays_open_never_requested(text, n_open):
    f, gate, events = _view(text)
    host = f.units[0]
    assert (host.modality, host.polarity) == ("DESIRE", "negative")
    opened = f.units[1:]
    assert len(opened) == n_open
    rels = [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
    for u in opened:
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in REQUESTS and not gate[u.id]
        assert u.request_target == "NONE" and u.embedded_under == host.id
        # no polarity, modality or subject chosen for the member
        assert (u.polarity, u.modality, u.subject) == ("positive", None, None)
        assert f"negated_scope_open:{u.id}" in f.ambiguities
        assert ("EMBEDS", host.id, u.id, "negated_scope_open") in rels
        if u.id in events:
            assert events[u.id].occurrence_claim.value not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
    assert f.closure is False and not semantic_closure(f).closed
    assert not any(c.construction == "shared_modality" for c in f.coordinations)


@pytest.mark.parametrize("text", [
    "Paul veut lancer P et exécuter Q.",                 # positive desire: shared (P3)
    "Paul ne veut pas lancer P et ne veut pas exécuter Q.",
    "Paul ne veut pas lancer P et Nadia exécute Q.",
    "Veuillez lancer P et exécuter Q.",
    "Lance R si Paul ne veut pas lancer P et exécuter Q.",  # protasis: unchanged
])  # negated pouvoir / aller (NEG-OPERATOR-ET): see test_negated_operator_coordination (G1)
def test_outside_the_ticket_nothing_is_marked(text):
    f = parse_utterance(text)
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_mais_keeps_its_contrast_relation():
    f, _, _ = _view("Paul ne veut pas lancer P mais exécuter Q.")
    assert ("CONTRASTS", f.units[0].id, f.units[1].id) in [(r.kind, r.source, r.target) for r in f.relations]


def test_true_request_after_negated_desire_is_kept():
    f, gate, _ = _view("Paul ne veut pas lancer P et lance Q.")
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)
    assert f.units[-1].pragmatic in REQUESTS or f.units[-1].subject is not None
