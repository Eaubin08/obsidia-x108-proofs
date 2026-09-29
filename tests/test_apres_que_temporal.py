"""TEMP-SUBORDINATE (après que): a temporal subordinate, never a relative, never asserted.

"Paul lance P après que Nadia a exécuté Q" was parsed as a relative of P
(EMBEDS "rel"): Q became ASSERTED_REALIZED and the temporal order was lost;
"Après que Q, P" lost its governor (UNRESOLVED). Q is now the temporal anchor
of its host (PRECEDES(Q -> host), evidence "après que"), EMBEDDED /
TEMPORAL_CONTEXT, with no realization claim (presupposed by the construction,
not asserted), exactly the finite counterpart of "après avoir V". Temporal
order is not causality (no CAUSES), the host is unchanged, and a subordinate
host never shares its subject / modal / auxiliary with the main clause.
"quand" and "pendant que" stay held.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


def _view(text):
    f = parse_utterance(text)
    claims = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    return f, claims, gate


@pytest.mark.parametrize("text,sub,host", [
    ("Paul lance P après que Nadia a exécuté Q.", "u2", "u1"),
    ("Après que Nadia a exécuté Q, Paul lance P.", "u1", "u2"),
    ("Paul lance P après qu'il a exécuté Q.", "u2", "u1"),
    ("Paul a lancé P après que Nadia n'a pas exécuté Q.", "u2", "u1"),
])
def test_apres_que_is_a_temporal_anchor_not_a_relative(text, sub, host):
    f, claims, _ = _view(text)
    rel = {(r.kind, r.source, r.target, r.evidence) for r in f.relations}
    assert ("PRECEDES", sub, host, "après que") in rel
    assert not any(r.kind in {"EMBEDS", "CAUSES"} for r in f.relations)
    u = next(x for x in f.units if x.id == sub)
    assert u.pragmatic == "EMBEDDED" and u.embedded_under is None
    assert claims[sub] == "NO_ASSERTION"


def test_parity_with_apres_avoir():
    f1, c1, _ = _view("Paul lance P après que Nadia a exécuté Q.")
    f2, c2, _ = _view("Paul lance P après avoir exécuté Q.")
    assert (f1.units[1].pragmatic, f1.units[1].role, c1["u2"]) == (f2.units[1].pragmatic, f2.units[1].role, c2["u2"])
    assert c1["u1"] == c2["u1"]


def test_main_imperative_after_subordinate_keeps_its_request():
    f, _, gate = _view("Après que Nadia a exécuté Q, lance P.")
    main = f.units[1]
    assert (main.subject, main.pragmatic, gate[main.id]) == (None, "REQUESTED", True)
    assert not any(c.construction == "shared_subject" for c in f.coordinations)


def test_dapres_source_unchanged():
    f, claims, _ = _view("D'après Marie, Paul a lancé P.")
    assert f.units[0].epistemic == "HUMAN_SOURCE" and claims["u1"] == "NO_ASSERTION"
