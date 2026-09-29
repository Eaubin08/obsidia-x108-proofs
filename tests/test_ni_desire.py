"""A1a: a negated desire under verbal "ni" never turns its infinitives into requests.

"Paul ne veut ni lancer P ni exécuter Q": "vouloir" was not admitted as a
shared ni modal (only obligation and ability-permission were), and "ni"
broke the modal+infinitive chain, so both infinitives became injunctive
REQUESTED units with a gate. The desire modal is now shared by the ni
members exactly like "ne doit ni" / "ne peut ni": each member is DESIRE,
negated by "ni", in one ni_negative_coordination (parity with the simple
"Paul ne veut pas V O"). Where that sharing is not established (conditional
"ne voudrait ni", second person "Ne veux-tu ni ... ?"), nothing is chosen:
every ni infinitive stays EMBEDDED under that exact "vouloir" unit with the
named structural ambiguity negated_scope_open, which blocks closure.
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


def _signature(u, gate, events):
    e = events.get(u.id)
    return (u.polarity, u.modality, u.subject, u.tense_aspect, u.pragmatic, u.role, u.action_agent,
            u.request_target, gate[u.id], e.occurrence_claim.value if e else None)


@pytest.mark.parametrize("text,lead,n", [
    ("Paul ne veut ni lancer P ni exécuter Q.", "Paul ne veut pas", 2),
    ("Je ne veux ni lancer P ni exécuter Q.", "Je ne veux pas", 2),
    ("Paul ne veut ni lancer P, ni exécuter Q.", "Paul ne veut pas", 2),
    ("Paul ne veut ni lancer P ni exécuter Q ni arrêter R.", "Paul ne veut pas", 3),
    ("Nous ne voulons ni lancer P ni exécuter Q.", "Nous ne voulons pas", 2),
    ("Paul ne voulait ni lancer P ni exécuter Q.", "Paul ne voulait pas", 2),
])
def test_ni_members_share_the_negated_desire(text, lead, n):
    f, gate, events = _view(text)
    (coord,) = f.coordinations
    assert (coord.construction, len(coord.members)) == ("ni_negative_coordination", n)
    assert coord.members == tuple(u.id for u in f.units)
    for u in f.units:
        assert (u.modality, u.polarity, u.negator) == ("DESIRE", "negative", "ni")
        assert u.pragmatic not in REQUESTS and not gate[u.id]
        obj = u.objects[0].text if u.objects else ""
        ref_f, ref_gate, ref_events = _view(f"{lead} {u.lemma} {obj}".rstrip() + ".")
        ref = _signature(ref_f.units[0], ref_gate, ref_events)
        assert _signature(u, gate, events)[:1] + _signature(u, gate, events)[2:] == ref[:1] + ref[2:]


def test_first_person_keeps_the_desire_request_ambiguity_per_member():
    f = parse_utterance("Je ne veux ni lancer P ni exécuter Q.")
    assert {f"desire_or_request:{u.id}" for u in f.units} <= set(f.ambiguities)


@pytest.mark.parametrize("text", [
    "Paul ne voudrait ni lancer P ni exécuter Q.",
    "Je ne voudrais ni lancer P ni exécuter Q.",
    "Ne veux-tu ni lancer P ni exécuter Q ?",
    "Tu ne veux ni lancer P ni exécuter Q.",
    "Paul ne voudrait ni lancer P, ni exécuter Q.",
])
def test_unshared_ni_desire_fails_closed_with_a_named_ambiguity(text):
    f, gate, events = _view(text)
    (gov,) = [u for u in f.units if u.lemma == "vouloir"]
    members = [u for u in f.units if u is not gov]
    assert len(members) >= 2
    for u in members:
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in REQUESTS and not gate[u.id]
        assert u.embedded_under == gov.id and u.request_target == "NONE"
        assert f"negated_scope_open:{u.id}" in f.ambiguities
        assert ("EMBEDS", gov.id, u.id, "negated_scope_open") in \
            [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
        if u.id in events:
            assert events[u.id].occurrence_claim.value not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
    assert f.closure is False and not semantic_closure(f).closed
    assert any(b.startswith("ambiguity:negated_scope_open:") for b in f.closure_blockers)


@pytest.mark.parametrize("text", [
    "Paul ne doit ni lancer P ni exécuter Q.",
    "Paul ne peut ni lancer P ni exécuter Q.",
    "Paul n'a ni lancé P ni arrêté Q.",
])
def test_existing_ni_modals_unchanged(text):
    f = parse_utterance(text)
    (coord,) = f.coordinations
    assert coord.construction == "ni_negative_coordination"
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


@pytest.mark.parametrize("text", [
    "Ne lance ni le test ni le build.",
    "Paul ne veut ni le test ni le build.",
])
def test_nominal_ni_unchanged(text):
    f = parse_utterance(text)
    assert f.coordinations == ()
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)
