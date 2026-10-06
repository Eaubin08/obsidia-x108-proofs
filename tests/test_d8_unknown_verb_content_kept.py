"""D8 option C (local conservation only): "permettre / autoriser" stay lexically ambiguous
(no ENABLES relation, no permission -> authority mapping, open), and an utterance whose
only verb is unknown is never a zero representation.

"Cette clé permet l'accès." produced no unit and no reported content. An utterance with no
unit at all whose unknown verb introduces a determiner argument is now reported as
unanalyzed predicative content (frame open). A verbless NP ("Le test rouge.") is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.primitives import RelationKind


@pytest.mark.parametrize("text,span", [("Cette clé permet l'accès.", "Cette clé permet l'accès"),
                                       ("Paul permet l'accès.", "Paul permet l'accès"),
                                       ("Le script ouvre la porte.", "Le script ouvre la porte")])
def test_unknown_verb_utterance_is_reported(text, span):
    f = parse_utterance(text)
    kept = [f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])] for m in f.missing]
    assert kept == [span] and not f.closure and not f.relations
    assert governable_summary(f)["requested_world_actions"] == []


@pytest.mark.parametrize("text", ["Le test rouge.", "Merci Paul."])
def test_verbless_np_unchanged(text):
    assert parse_utterance(text).missing == ()


def test_permettre_stays_ambiguous_no_enable():
    assert not hasattr(RelationKind, "ENABLES")
    f = parse_utterance("Paul permet à Marie de lancer P.")
    assert "infinitive_under_unrecognized_governor:u1" in f.ambiguities and not f.closure
    assert not f.relations
