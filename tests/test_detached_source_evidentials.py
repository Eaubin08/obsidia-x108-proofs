"""B2e: detached source / evidential adverbials never yield an asserted occurrence.

Human source ("Selon Marie, P"), evidence source ("Selon les logs, P"),
speaker opinion ("Selon moi, P") and inferential ("Apparemment, P") are
attributed: NO_ASSERTION, the evidential class named in the provenance.
Non-detached "selon" (source vs manner) and directives are unchanged; the
marker is never distributed to a coordinated clause.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)


def _events(text):
    f = parse_utterance(text)
    return f, {c.predicate_ref: c for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text,evidential", [
    ("Selon Marie, Paul a lancé le test.", "HUMAN_SOURCE"),
    ("D" + A + "après Marie, Paul a lancé le test.", "HUMAN_SOURCE"),
    ("Paul a lancé le test, selon Marie.", "HUMAN_SOURCE"),
    ("Selon Marie, Paul n" + A + "a pas lancé le test.", "HUMAN_SOURCE"),
    ("Selon les logs, Paul a lancé le test.", "EVIDENCE_SOURCE"),
    ("D" + A + "après les logs, Paul a lancé le test.", "EVIDENCE_SOURCE"),
    ("Selon moi, Paul a lancé le test.", "SPEAKER_BELIEF"),
    ("Apparemment, Paul a lancé le test.", "INFERRED"),
    ("Apparemment, Paul lancera le test.", "INFERRED"),
])
def test_detached_source_is_attributed(text, evidential):
    f, events = _events(text)
    (ev,) = events.values()
    assert ev.occurrence_claim.value == "NO_ASSERTION"
    assert ev.occurrence_derivation.provenance["evidential"] == evidential


def test_marker_is_not_distributed_to_a_coordinated_clause():
    f, events = _events("Selon Marie, Paul a lancé le test et Nadia a lancé le build.")
    assert events["u1"].occurrence_claim.value == "NO_ASSERTION"
    assert events["u2"].occurrence_claim.value == "UNRESOLVED"
    assert "coordination_attachment_ambiguous:u2" in f.ambiguities


@pytest.mark.parametrize("text,expected", [
    ("Lance le test selon la procédure.", {"u1": "NO_ASSERTION"}),
    ("Selon Marie, lance le test.", {"u1": "NO_ASSERTION"}),
    ("Paul a lancé le test selon Marie.", {"u1": "ASSERTED_REALIZED"}),
    ("Paul a lancé le test.", {"u1": "ASSERTED_REALIZED"}),
    ("Marie dit que Paul a lancé le test.", {"u1": "ASSERTED_REALIZED", "u2": "NO_ASSERTION"}),
    ("Il paraît que Paul a lancé le test.", {"u1": "NO_ASSERTION"}),
    ("Marie a vu Paul lancer le test.", {"u1": "ASSERTED_REALIZED", "u2": "ASSERTED_REALIZED"}),
])
def test_controls_are_unchanged(text, expected):
    f, events = _events(text)
    assert {k: v.occurrence_claim.value for k, v in events.items()} == expected
    assert all(u.pragmatic != "ASSERTED" or u.epistemic in {"ASSERTED", "COUNTERFACTUAL"} for u in f.units)


def test_directive_under_detached_source_keeps_its_pragmatics():
    f = parse_utterance("Selon Marie, lance le test.")
    assert (f.units[0].pragmatic, f.units[0].epistemic) == ("REQUESTED", "NOT_APPLICABLE")
