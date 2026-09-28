"""B2c: "V que [le X que P] V2" — complement structure lost with its subject NP.

The verbless complement opener ("que le test") is merged into its governor
clause and the following clause carries both the relative (P) and the
complement's own predicate (V2). None of them may become a relative of the
governor asserted by the speaker: they stay subordinated under the governor
with unknown governance (fail-closed), and the loss is reported.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

ASSERTED = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}


@pytest.mark.parametrize("text", [
    "Marie dit que le test que Paul a lancé a arrêté le build.",
    "Marie dit que le test que Paul a lancé a échoué.",
    "Marie croit que le script que Paul a lancé a planté.",
    "Marie a appris que le test que Paul a lancé a arrêté le build.",
    "Marie dit que le test qui a échoué a été lancé par Paul.",
])
def test_units_of_a_lost_complement_are_never_asserted_relatives_of_the_governor(text):
    f = parse_utterance(text)
    governor, content = f.units[0], f.units[1:]
    assert content
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    for u in content:
        assert (u.pragmatic, u.epistemic, u.embedded_under) == ("EMBEDDED", "UNRESOLVED_GOVERNANCE", governor.id)
        assert f"complement_structure_lost:{u.id}" in f.ambiguities
        assert [(r.kind, r.evidence) for r in f.relations if r.target == u.id] == [("EMBEDS", "que_governor_lost")]
        if u.id in events:
            assert events[u.id].occurrence_claim.value == "UNRESOLVED"


def test_lost_complement_under_hearsay_is_never_asserted():
    f = parse_utterance("Il paraît que le test que Paul a lancé a arrêté le build.")
    assert f.units
    for c in build_frame_event_index(f).events():
        assert c.occurrence_claim.value not in ASSERTED


@pytest.mark.parametrize("text,expected", [
    ("Marie dit que Nadia a arrêté le test que Paul a lancé.",
     [("EMBEDS", "u2", "u3", "rel"), ("REPORTS", "u1", "u2", "que")]),
    ("Paul a lancé le test que Nadia a préparé.", None),
    ("J'ai vu le test que Paul a lancé.", None),
])
def test_ordinary_relatives_are_unchanged(text, expected):
    f = parse_utterance(text)
    assert not any(a.startswith("complement_structure_lost") for a in f.ambiguities)
    if expected is not None:
        assert sorted((r.kind, r.source, r.target, r.evidence) for r in f.relations) == expected


def test_lost_complement_after_a_lost_governor_is_never_asserted():
    f = parse_utterance("Marie se rend compte que le script que Paul a lancé a arrêté le build.")
    assert f.units
    for u in f.units:
        assert (u.pragmatic, u.epistemic) == ("EMBEDDED", "UNRESOLVED_GOVERNANCE")
    for c in build_frame_event_index(f).events():
        assert c.occurrence_claim.value == "UNRESOLVED"
