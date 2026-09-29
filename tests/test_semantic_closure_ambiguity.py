"""Semantic Closure (master block 26): OUTPUT_EXISTS != SEMANTIC_CLOSURE.

A frame whose meaning structure is still ambiguous (antecedent, attachment,
governor, lost structure, bare "ne") is not closed, and every reason is named
in closure_blockers ("ambiguity:<marker>"). Speech-act readings that the
parser already represents fail-closed (indirect request, desire or request,
question or request) do not block closure here (held doctrine). Truth values
and evidence needs never block closure.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.primitives import STRUCTURAL_AMBIGUITIES


@pytest.mark.parametrize("text,marker", [
    ("Marie dit que Paul a lancé P et Nadia a exécuté Q.", "coordination_attachment_ambiguous"),
    ("Paul fraxe que Nadia a lancé P.", "complement_under_unresolved_governor"),
    ("Prépare le test et le build puis ne le lance pas.", "ambiguous_antecedent"),
    ("Paul ne lance P.", "bare_ne"),
    ("Marie dit que Nadia a arrêté Q parce que Paul a lancé P.", "coordination_attachment_ambiguous"),
])
def test_structural_ambiguity_blocks_closure_and_is_named(text, marker):
    f = parse_utterance(text)
    assert f.closure is False
    assert any(b.startswith(f"ambiguity:{marker}:") for b in f.closure_blockers)


@pytest.mark.parametrize("text", [
    "Peux-tu lancer P ?",            # ability_permission_or_request (held)
    "Je voudrais lancer P.",         # desire_or_request (held)
    "Tu lances le script ?",         # question_or_request (held)
    "Paul a lancé P.",
    "Maman est là ?",                # evidence need only
])
def test_speech_act_readings_and_truth_values_do_not_block(text):
    f = parse_utterance(text)
    assert not any(b.startswith("ambiguity:") for b in f.closure_blockers)


def test_every_blocking_marker_kind_is_structural():
    assert not {"ability_permission_or_request", "desire_or_request", "question_or_request"} & STRUCTURAL_AMBIGUITIES
