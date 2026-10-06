"""SERVE_FOR (approved option A): "X sert à Y" is a non-eventive functional predicate.

"servir à + INF" is SERVE_FOR(subject X) (class "other": no EventCandidate) with the
infinitive Y EMBEDDED under it (EMBEDS, evidence "servir_a", role PURPOSE). The
PredicateUnit carries the commitment: assertion, negation, question. Y never occurs, is
never requested nor authorized (SERVE_FOR != CAUSE / ENABLES / AUTHORIZES). In a relative,
Y is the content of the relative's own SERVE_FOR, never an asserted action. A dative clitic
("te sert à") has no role yet and is kept (frame open); other senses ("sert le repas",
"sert de preuve") are reported, never closed as a functional purpose.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _view(text):
    f = parse_utterance(text)
    serve = next(u for u in f.units if u.predicate == "SERVE_FOR")
    target = next(u for u in f.units if u.embedded_under == serve.id)
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    return f, serve, target, claims


@pytest.mark.parametrize("text,subject,pred,pragmatic,polarity", [
    ("La mémoire sert à parler.", "mémoire", "SPEAK", "ASSERTED", "positive"),
    ("Le script sert à lancer P.", "script", "EXECUTE", "ASSERTED", "positive"),
    ("Le document sert à expliquer P.", "document", "EXPLAIN", "ASSERTED", "positive"),
    ("La mémoire ne sert pas à parler.", "mémoire", "SPEAK", "ASSERTED", "negative"),
    ("Est-ce que la mémoire sert à parler ?", "mémoire", "SPEAK", "ASKED", "positive"),
])
def test_serve_for_main_clause(text, subject, pred, pragmatic, polarity):
    f, serve, y, claims = _view(text)
    assert (serve.subject, serve.pragmatic, serve.polarity, serve.predicate_class) == (subject, pragmatic, polarity, "other")
    assert (y.predicate, y.pragmatic, y.role, y.polarity) == (pred, "EMBEDDED", "PURPOSE", "positive")
    assert ("EMBEDS", serve.id, y.id, "servir_a") in [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
    assert serve.id not in claims  # non-eventive: no EventCandidate
    assert claims.get(y.id) not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False and f.constraints == ()
    assert not any(r.kind in {"CAUSES", "REPORTS", "CONDITIONS"} for r in f.relations) and f.closure


def test_negation_is_on_the_functional_claim_never_no_speak():
    f, serve, y, _ = _view("La mémoire ne sert pas à parler.")
    assert serve.polarity == "negative" and y.polarity == "positive" and f.constraints == ()


@pytest.mark.parametrize("text,closed", [("Détaille la mémoire qui sert à parler.", True),
                                         ("Détaille la mémoire qui te sert à parler.", False)])
def test_relative_serve_for(text, closed):
    f, serve, y, _ = _view(text)
    detail = f.units[0]
    assert (detail.predicate, [a.text for a in detail.objects]) == ("DETAIL", ["la mémoire"])
    assert ("EMBEDS", detail.id, serve.id, "rel") in [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
    assert (y.predicate, y.pragmatic, y.embedded_under, y.role) == ("SPEAK", "EMBEDDED", serve.id, "PURPOSE")
    assert f.closure is closed


@pytest.mark.parametrize("text", ["La mémoire te sert à parler.", "Détaille la mémoire qui te sert à parler."])
def test_te_is_kept_unresolved(text):
    f, serve, _, _ = _view(text)
    (m,) = [m for m in f.missing if m.endswith(f":unresolved_clitic_of={serve.id}")]
    a, b = map(int, m.split(":")[1].split("-"))
    assert f.raw[a:b] == "te" and not f.closure


@pytest.mark.parametrize("text", ["Paul sert le repas.", "Le document sert de preuve."])
def test_other_servir_senses_are_not_closed_as_purpose(text):
    f = parse_utterance(text)
    assert any(":serve_for_sense_unsupported_of=" in m for m in f.missing) and not f.closure
