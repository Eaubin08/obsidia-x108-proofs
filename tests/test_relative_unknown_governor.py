"""An infinitive under an unrecognised governor inside a relative is never asserted.

"Explique le script qui sert à lancer P" read "le script lance P" (EXECUTE ASSERTED,
closed frame): the governor "sert" is not in the lexicon, and the relative branch
asserted every unit. Like a main clause ("Le script sert à lancer P"), the infinitive is
now the content of an unrecognised governor (EMBEDDED, infinitive_under_unrecognized_
governor, frame open), still attached to its antecedent clause (EMBEDS rel). The
functional relation ("sert à") itself is not represented yet (USED_FOR is held).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text,lemma", [("Explique le script qui sert à lancer P.", "lancer"),
                                        ("Lance le script qui permet de tester P.", "tester")])
def test_relative_infinitive_under_unknown_governor_is_not_asserted(text, lemma):
    f = parse_utterance(text)
    (u,) = [x for x in f.units if x.lemma == lemma]
    assert u.pragmatic == "EMBEDDED" and f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
    assert ("EMBEDS", "u1", u.id) in [(r.kind, r.source, r.target) for r in f.relations] and not f.closure
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims.get(u.id) not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}


def test_main_request_unchanged():
    assert governable_summary(parse_utterance("Lance le script qui permet de tester P."))["requested_world_actions"] \
        == ["EXECUTE"]


@pytest.mark.parametrize("text,modality", [("Explique le script qui lance P.", None),
                                           ("Explique le script qui veut lancer P.", "DESIRE")])
def test_known_relatives_unchanged(text, modality):
    f = parse_utterance(text)
    u = f.units[-1]
    assert (u.pragmatic, u.modality) == ("ASSERTED", modality) and f.closure
