"""B2b: reportive evidential without a governor unit ("il paraît que P").

The parser marks P itself as HEARSAY (no unit governs it). HEARSAY content is
attributed, never asserted by the speaker: it must not become an asserted
occurrence without an independent basis. No governor unit is invented; the
evidential marker closes the perspective like a report (commitment ATTRIBUTED)
and is named in the derivation provenance.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)
ASSERTED = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}


def _claims(text):
    f = parse_utterance(text)
    return f, {c.predicate_ref: c for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text", [
    "Il paraît que Paul a lancé le test.",
    "Il paraît que Paul n" + A + "a pas lancé le test.",
    "Il paraît que Paul lancera le test.",
    "Il paraît que Paul va lancer le test.",
    "Il paraît que Paul pourrait lancer le test.",
    "Il paraît que Paul lancerait le test.",
    "Il paraît que Paul a failli lancer le test.",
    "Paraît que Paul a lancé le test.",
    "Il ne paraît pas que Paul a lancé le test.",
    "Est-ce qu" + A + "il paraît que Paul a lancé le test ?",
])
def test_hearsay_content_is_attributed_not_asserted(text):
    f, events = _claims(text)
    (u,) = [u for u in f.units if u.pragmatic == "REPORTED" and u.embedded_under is None]
    d = events[u.id].occurrence_derivation
    assert events[u.id].occurrence_claim.value == "NO_ASSERTION"
    assert d.rule == "commitment:ATTRIBUTED"
    assert d.provenance["evidential"] == "HEARSAY"
    assert d.provenance["edge"] == "root" and d.provenance["governor"] is None


@pytest.mark.parametrize("text", [
    "Il paraît que Marie dit que Paul a lancé le test.",
    "Il paraît que Marie croit que Paul a lancé le test.",
    "Il paraît que Marie a appris que Paul a lancé le test.",
    "Il paraît que Marie a vu Paul lancer le test.",
    "Il paraît que Marie voit Paul lancer le test.",
])
def test_content_nested_under_hearsay_names_the_evidential_origin(text):
    f, events = _claims(text)
    root = next(u for u in f.units if u.pragmatic == "REPORTED" and u.embedded_under is None)
    for u in f.units:
        assert events[u.id].occurrence_claim.value not in ASSERTED, (u.id, u.predicate)
        if u is not root:
            inherited = events[u.id].occurrence_derivation.provenance.get("inherited_from", {})
            assert inherited.get("attribution_boundary") == root.id


def test_conditional_under_hearsay_is_never_asserted():
    f, events = _claims("Il paraît que si Paul lance le test, Nadia a lancé le build.")
    assert all(c.occurrence_claim.value not in ASSERTED for c in events.values())


@pytest.mark.parametrize("text,expected", [
    ("Paul a lancé le test.", {"u1": "ASSERTED_REALIZED"}),
    ("Marie dit que Paul a lancé le test.", {"u1": "ASSERTED_REALIZED", "u2": "NO_ASSERTION"}),
    ("On dit que Paul a lancé le test.", {"u1": "ASSERTED_REALIZED", "u2": "NO_ASSERTION"}),
    ("Marie a vu Paul lancer le test.", {"u1": "ASSERTED_REALIZED", "u2": "ASSERTED_REALIZED"}),
    ("Je vois Marie lancer le test.", {"u1": "ASSERTED_REALIZED", "u2": "ASSERTED_REALIZED"}),
])
def test_report_and_direct_perception_controls_are_unchanged(text, expected):
    _, events = _claims(text)
    assert {k: v.occurrence_claim.value for k, v in events.items()} == expected
    assert all("evidential" not in v.occurrence_derivation.provenance for v in events.values())


def test_hearsay_is_a_referable_report_perspective_like_a_report():
    def binding(text):
        f = parse_utterance(text)
        (ref,) = resolve_explicit_event_references(f, build_frame_event_index(f).events()).references
        return ref.resolution_status.value, ref.provenance.get("reason")

    assert binding("Il paraît que Paul a lancé le test. Luc a vu ce lancement.") == \
        binding("Marie dit que Paul a lancé le test. Luc a vu ce lancement.")
    assert binding("Il paraît que Paul lancera le test. Luc a vu ce lancement.")[0] == "AMBIGUOUS"
