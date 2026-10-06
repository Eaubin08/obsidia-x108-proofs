"""Certification (block 26): Semantic Closure.

OUTPUT_EXISTS != SEMANTIC_CLOSURE != AUTHORITY. Closure succeeds when the only open points
are canonical, explicitly preserved uncertainties (speech act, modal-past occurrence, H16
deontic double reading) or fully represented structure (unique-host EXCEPTS, resolved
PURPOSE); it fails on true structural incompleteness (attachment, mixed grouping, unknown
governor, unresolved subject, condition / exception / temporal scope, H01 negated scope,
unrepresented content, occurrence or directive contradiction). Frame-level and event-level
closure agree; neither authorises anything.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.primitives import BOUNDARY, STRUCTURAL_AMBIGUITIES
from app.semantic.lattice.semantic_closure import semantic_closure

_CLOSES = [
    "Paul lance P.", "Paul a pu lancer P.", "Paul a voulu lancer P.", "Peux-tu lancer P ?",
    "Ne peux-tu pas lancer P ?", "Tu n'as pas à lancer P.", "Paul lance R sauf si Marie lance P.",
    "Paul lance P pour tester Q.",
]
_OPEN = [
    ("Lance R si Paul lance P et exécute Q.", "coordination_attachment_ambiguous"),
    ("Si Paul lance P et Marie lance Q ou Luc lance S, lance X.", "condition_scope_ambiguous"),
    ("Paul permet à Marie de lancer P.", "infinitive_under_unrecognized_governor"),
    ("Paul lance P et exécutent Q.", "subject_unresolved"),
    ("Lance R si tu lances P et exécute Q.", "condition_scope_ambiguous"),
    ("Lance R et exécute Q sauf si Marie lance P.", "exception_condition_open"),
    ("Lance R et exécute Q avant que Paul lance P.", "temporal_scope_ambiguous"),
    ("Ne lance pas P et Q.", "negated_scope_open"),
    ("Cette clé permet l'accès.", "unanalyzed_predicative_content"),
    ("Paul a lancé P et n'a pas lancé P.", "occurrence_conflict_open"),
    ("Lance P et ne lance pas P.", "requested_and_forbidden"),
]


@pytest.mark.parametrize("text", _CLOSES)
def test_closes_when_only_canonical_uncertainty_remains(text):
    f = parse_utterance(text)
    sc = semantic_closure(f)
    assert f.closure and sc.closed and not sc.reasons


@pytest.mark.parametrize("text,reason", _OPEN)
def test_stays_open_on_structural_incompleteness(text, reason):
    f = parse_utterance(text)
    sc = semantic_closure(f)
    assert not f.closure and not sc.closed and any(reason in r for r in sc.reasons)


def test_h01_negated_scope_stays_structural():
    assert "negated_scope_open" in STRUCTURAL_AMBIGUITIES


def test_canonical_families_are_not_structural():
    for fam in ("ability_permission_or_request", "desire_or_request", "question_or_request",
                "negated_speech_act_open", "modal_past_occurrence_open", "deontic_scope_open"):
        assert fam not in STRUCTURAL_AMBIGUITIES


@pytest.mark.parametrize("text", _CLOSES + [t for t, _ in _OPEN])
def test_closure_never_authorises(text):
    f = parse_utterance(text)
    sc = semantic_closure(f)
    assert (sc.metadata["MEMORY_WRITE"], sc.metadata["KX108_CALLED"], sc.metadata["truth"]) == (0, 0, None)
    b = governable_summary(f)["boundary"]
    assert b == BOUNDARY and b["decision_authority"] == "KX108_ONLY"
    assert (b["emits_act"], b["memory_write"], b["kernel_mutation"]) == (False, False, False)
