"""N11: an unrecognised governor inside a subordinate is never silently dropped.

"Lance R à moins que Paul veuille lancer P": "veuille" is unknown to the
lexicon; in a root clause the unrecognised-governor contract names it, but
inside a subordinate the subordinate's own branch (HYPOTHETICAL) took
precedence: the governor vanished, P survived without it, nothing was named.

The infinitive keeps its subordinate pragmatics, and the governor is named
anyway (infinitive_under_unrecognized_governor) with its surface span kept
as unanalyzed predicative content (unrecognized_governor_of=<unit>). No
DESIRE is inferred, no occurrence or commitment invented; closure stays
open. Adding "veuille" to the lexicon is a separate, non-safety ticket.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,gov", [
    ("Lance R à moins que Paul veuille lancer P.", "veuille"),
    ("Lance R si Paul veuille lancer P.", "veuille"),
    ("Lance R avant que Paul frobnique lancer P.", "frobnique"),
    ("Lance R sauf si Paul veuille lancer P.", "veuille"),
])
def test_unrecognised_governor_in_a_subordinate_is_named(text, gov):
    f = parse_utterance(text)
    p = f.units[-1]
    assert p.lemma == "lancer" and p.modality is None                    # no DESIRE inferred
    assert f"infinitive_under_unrecognized_governor:{p.id}" in f.ambiguities
    entries = [m for m in f.missing if m.endswith(f":unrecognized_governor_of={p.id}")]
    assert len(entries) == 1
    start, end = map(int, entries[0].split(":")[1].split("-"))
    assert text[start:end] == gov
    assert not f.closure


def test_root_unrecognised_governor_contract_is_unchanged():
    f = parse_utterance("Paul aime lancer P.")
    assert f.ambiguities == ("infinitive_under_unrecognized_governor:u1",) and f.missing == ()


def test_known_modal_in_a_subordinate_is_unchanged():
    f = parse_utterance("Lance R avant que Paul puisse lancer P.")
    assert f.units[-1].modality == "ABILITY_OR_PERMISSION"
    assert not any(a.startswith("infinitive_under_unrecognized_governor") for a in f.ambiguities)
