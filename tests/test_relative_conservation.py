"""A syntactically present relative never disappears because it produced no semantic unit.

"Explique la mémoire qui te sert à parler", "Explique le document qui frobule P",
"Explique le document que Paul frobule", "Explique le document qui est utile" closed with
the relative silently dropped: a relative with no recognised verb was merged into its
clause and ignored by the conservation pass, and a unit-less relative clause (copula) was
skipped by the M8-0b report. Both now keep the exact relative content
(unanalyzed_predicative_content:...:unattached_relative_of=<unit> or embedded_under=<unit>),
frame open. Nothing is inferred (no antecedent, subject, predicate, PURPOSE or REPORTS);
fully represented relatives are untouched; an infinitive under an unknown governor in a
relative stays non-asserted (477fdbd7).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _reported(f):
    out = []
    for m in f.missing:
        if m.startswith("unanalyzed_predicative_content:") and (
                ":unattached_relative_of=" in m or ":embedded_under=" in m):
            a, b = map(int, m.split(":")[1].split("-"))
            out.append(f.raw[a:b])
    return out


@pytest.mark.parametrize("text,kept", [
    # "qui te sert à parler" is a SERVE_FOR relative now (test_serve_for): unit-less example
    ("Explique la mémoire qui te frobule.", "qui te frobule"),
    ("Explique le document qui frobule P.", "qui frobule P"),
    ("Explique le document que Paul frobule.", "que Paul frobule"),
    ("Explique le document qui est utile.", "est utile"),
])
def test_unit_less_relative_is_kept_and_open(text, kept):
    f = parse_utterance(text)
    assert _reported(f) == [kept] and not f.closure
    (u,) = f.units
    assert u.predicate == "EXPLAIN" and not f.relations
    assert governable_summary(f)["requested_world_actions"] == []


def test_unknown_governor_relative_infinitive_stays_non_asserted():
    # "servir à" is SERVE_FOR since its approved APPLY (test_serve_for): a really unknown governor here
    f = parse_utterance("Explique le script qui contribue à lancer P.")
    u = f.units[-1]
    assert u.pragmatic == "EMBEDDED" and f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims.get(u.id) not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}
    assert not _reported(f) and not f.closure  # governor material kept as unrecognized_governor_of


@pytest.mark.parametrize("text", ["Explique le script qui lance P.", "Lance le test que Paul a écrit.",
                                  "Paul ne lance que P."])
def test_represented_relatives_and_restriction_unchanged(text):
    f = parse_utterance(text)
    assert not _reported(f) and f.closure
