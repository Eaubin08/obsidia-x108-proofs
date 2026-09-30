"""N8: "ne pas avoir à + INF" is never an addressee request.

"Tu n'as pas à lancer P": "avoir à" was not recognised, "à" fell to the
unknown-preposition fallback and the infinitive was exposed at runtime as a
requested world action.

Its deontic force is held (H16: absence of obligation vs no-right /
quasi-prohibition). Safety only: the infinitive stays content under that
negated "avoir à" (EMBEDDED, no request, never FORBIDDEN, never an asserted
NOT_REQUIRED, no constraint), deontic_scope_open is named and closure stays
open; a coordinated bare infinitive takes the same contract. The positive
"Tu as à lancer P" and "pas besoin de" are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary

_DEONTIC = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN", "NOT_REQUIRED"}


@pytest.mark.parametrize("text", [
    "Tu n'as pas à lancer P.", "Tu n'as pas à exécuter le build.", "Vous n'avez pas à exécuter le build.",
    "Paul n'a pas à lancer P.", "Tu as pas à exécuter le build ?", "Tu n'avais pas à exécuter le build.",
    "N'as-tu pas à exécuter le build ?", "Tu n'as pas à lancer P et exécuter le build.",
    "Tu n'as pas à lancer P et ne pas exécuter le build.",
])
def test_negated_have_to_content_is_never_a_request(text):
    f = parse_utterance(text)
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert f.units
    for u in f.units:
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in _DEONTIC
        assert f"deontic_scope_open:{u.id}" in f.ambiguities
        assert claims[u.id] == "NO_ASSERTION"
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False
    assert f.constraints == () and not f.closure


def test_positive_have_to_is_unchanged():
    f = parse_utterance("Tu as à lancer P.")
    assert not any(a.startswith("deontic_scope_open") for a in f.ambiguities)
    assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"]


def test_pas_besoin_de_is_unchanged():
    f = parse_utterance("Tu n'as pas besoin de lancer P.")
    assert f.units[0].pragmatic == "NOT_REQUIRED" and f.closure
