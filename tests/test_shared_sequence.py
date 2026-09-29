"""Coordination P10: "puis" / "mais" coordinate shared structure like "et".

"Paul lance P puis exécute Q", "Paul doit lancer P puis exécuter Q", "Peux-tu
lancer P puis exécuter Q ?": the second member shares the host's subject,
modal, periphrasis, directive or auxiliary exactly as with "et" (same
CoordinationRef constructions), so it is never an injunctive / imperative
REQUESTED member with a gate. The sequence / contrast relation itself
(PRECEDES / CONTRASTS) is unchanged. Under a negated host ("ne ... pas P mais
Q") only the finite subject is shared: sharing a modal or auxiliary there
would decide the held negative scope.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


def _signature(u, gate, events):
    e = events.get(u.id)
    return (u.verb_form, u.polarity, u.modality, u.subject, u.tense_aspect, u.pragmatic, u.role,
            u.action_agent, u.request_target, gate[u.id], e.occurrence_claim.value if e else None)


@pytest.mark.parametrize("conn", ["puis", "mais", "et puis"])
@pytest.mark.parametrize("head,construction", [
    ("Paul lance P {c} exécute Q.", "shared_subject"),
    ("Paul doit lancer P {c} exécuter Q.", "shared_modality"),
    ("Paul va lancer P {c} exécuter Q.", "shared_periphrasis"),
    ("Peux-tu lancer P {c} exécuter Q ?", "shared_modality"),
    ("Veuillez lancer P {c} exécuter Q.", "shared_directive"),
    ("Paul a lancé P {c} exécuté Q.", "shared_auxiliary"),
])
def test_sequence_connectives_share_like_et(conn, head, construction):
    f, gate, events = _view(head.format(c=conn))
    ref_f, ref_gate, ref_events = _view(head.format(c="et"))
    (coord,) = f.coordinations
    assert coord.construction == construction and coord.members == ("u1", "u2")
    assert _signature(f.units[1], gate, events) == _signature(ref_f.units[1], ref_gate, ref_events)
    kinds = {r.kind for r in f.relations}
    assert ("PRECEDES" in kinds) if "puis" in conn else ("CONTRASTS" in kinds)
    ids = [e.event_ref.event_id for e in events.values()]
    assert len(ids) == len(set(ids)) and coord.id not in events


def test_negated_host_shares_only_the_finite_subject():
    f, gate, _ = _view("Paul ne lance pas P mais exécute Q.")
    assert f.coordinations[0].construction == "shared_subject"
    assert (f.units[1].subject, f.units[1].polarity, gate["u2"]) == ("paul", "positive", False)


@pytest.mark.parametrize("text", [
    "Paul ne doit pas lancer P mais exécuter Q.",
    "Paul n'a pas lancé P mais exécuté Q.",
    "Paul ne va pas lancer P mais exécuter Q.",
])
def test_negated_host_keeps_operator_scope_open(text):
    assert parse_utterance(text).coordinations == ()


def test_imperative_sequence_unchanged():
    f, gate, _ = _view("Lance P puis exécute Q.")
    assert f.coordinations == () and all(u.pragmatic == "REQUESTED" and gate[u.id] for u in f.units)
