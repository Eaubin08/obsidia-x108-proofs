"""H12 option B: a past / pluperfect modal ("a voulu / a pu / a dû / avait voulu / il a fallu
P") does not prove the occurrence of P: canonically UNRESOLVED, never realized, never
requested. That uncertainty is the intended reading (modal_past_occurrence_open, kept named):
it no longer blocks closure by itself; any structural ambiguity still blocks.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _occ(f):
    return {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text,modality,tense,polarity", [
    ("Paul a voulu lancer P.", "DESIRE", "PAST", "positive"),
    ("Paul a pu lancer P.", "ABILITY_OR_PERMISSION", "PAST", "positive"),
    ("Paul a dû lancer P.", "OBLIGATION", "PAST", "positive"),
    ("Paul avait voulu lancer P.", "DESIRE", "PLUPERFECT", "positive"),
    ("Il a fallu lancer P.", "OBLIGATION", "PAST", "positive"),
    ("Paul n'a pas voulu lancer P.", "DESIRE", "PAST", "negative"),
])
def test_modal_past_content_is_unresolved_and_closes(text, modality, tense, polarity):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.modality, u.tense_aspect, u.polarity, u.pragmatic) == (modality, tense, polarity, "ASSERTED")
    assert u.realized is None and _occ(f) == {"u1": "UNRESOLVED"}
    assert f"modal_past_occurrence_open:{u.id}" in f.ambiguities
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and not f.constraints and not s["confirmed_no_execute"]
    assert f.closure and not f.closure_blockers


@pytest.mark.parametrize("text,modality", [("Paul a voulu lancer P et exécuter Q.", "DESIRE"),
                                           ("Paul a pu lancer P et exécuter Q.", "ABILITY_OR_PERMISSION")])
def test_coordinated_modal_past_is_shared_never_requested(text, modality):
    f = parse_utterance(text)
    assert [(u.pragmatic, u.modality, u.tense_aspect, u.subject) for u in f.units] == \
        [("ASSERTED", modality, "PAST", "paul")] * 2
    (c,) = f.coordinations
    assert c.construction == "shared_modality" and c.members == ("u1", "u2")
    assert _occ(f) == {"u1": "UNRESOLVED", "u2": "UNRESOLVED"}
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure


def test_negated_modal_past_coordination_keeps_h01_scope_open():
    f = parse_utterance("Paul n'a pas voulu lancer P et exécuter Q.")
    q = f.units[1]
    assert (q.polarity, q.pragmatic) == ("positive", "EMBEDDED")      # negation not distributed
    assert f"negated_scope_open:{q.id}" in f.ambiguities
    assert governable_summary(f)["requested_world_actions"] == [] and not f.constraints
    assert not f.closure and f.closure_blockers == ("ambiguity:negated_scope_open:u2",)


def test_structural_ambiguity_still_blocks():
    f = parse_utterance("Paul a voulu lancer P et Q ou R.")
    assert "modal_past_occurrence_open:u1" in f.ambiguities
    assert f.closure_blockers == ("ambiguity:coordination_attachment_ambiguous:u1",) and not f.closure


@pytest.mark.parametrize("text,claim,realized", [("Paul a lancé P.", "ASSERTED_REALIZED", True),
                                                 ("Paul a failli lancer P.", "ASSERTED_NOT_REALIZED", False)])
def test_non_modal_controls_unchanged(text, claim, realized):
    f = parse_utterance(text)
    assert f.units[0].realized is realized and _occ(f) == {"u1": claim} and f.closure
