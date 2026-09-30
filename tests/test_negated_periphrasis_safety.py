"""N3a: an infinitive under a negated periphrasis is never an addressee request.

"Paul ne vient pas de lancer P (et exécuter Q)", "Paul n'est pas en train de
lancer P": the negator between the finite verb and "de" / "en train de" hid
the periphrasis; P fell to the unknown-preposition fallback (exposed as a
request at runtime) and Q to an injunctive REQUESTED.

Safety only (N3b, the analysis of the negated periphrasis itself, is not
done): its infinitive takes the existing unrecognised-governor contract
(EMBEDDED, no subject, named, never a request, occurrence NO_ASSERTION,
closure open), and a coordinated bare infinitive takes it too. Positive
periphrases are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text", [
    "Paul ne vient pas de lancer P.", "Paul ne vient pas de lancer P et exécuter Q.",
    "Paul n'est pas en train de lancer P.", "Paul n'est pas en train de lancer P et exécuter Q.",
    "Paul vient pas de lancer P et exécuter Q.", "Je ne viens pas de lancer P, exécuter Q.",
    "Paul ne venait pas de lancer P.", "Paul n'était pas en train de lancer P et exécuter Q.",
])
def test_negated_periphrasis_content_is_never_requested(text):
    f = parse_utterance(text)
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert f.units and f.units[0].lemma == "lancer"
    for u in f.units:
        assert u.pragmatic == "EMBEDDED" and u.subject is None
        assert f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
        assert claims[u.id] == "NO_ASSERTION"
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False
    assert not f.closure


@pytest.mark.parametrize("text,tense", [("Paul vient de lancer P et exécuter Q.", "RECENT_PAST"),
                                        ("Paul est en train de lancer P et exécuter Q.", "PROGRESSIVE")])
def test_positive_periphrases_are_unchanged(text, tense):
    f = parse_utterance(text)
    assert all(u.tense_aspect == tense and u.pragmatic == "ASSERTED" for u in f.units) and f.closure
