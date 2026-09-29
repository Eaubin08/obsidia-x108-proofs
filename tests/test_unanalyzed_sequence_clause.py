"""NO SILENT DROP: an unanalysed clause of a sequence is reported, never absorbed.

"Paul frobnique le test puis lance P", "Paul lança le test et Nadia exécute Q"
(unknown verb, French passé simple): the clause produced no unit, was either
silently skipped or absorbed as an object of its neighbour, and the frame was
declared closed. Within a sequence (after a clause connective or a comma, or
beside another verbal clause) a nominal subject + unknown word is now kept as
unanalysed predicative content (M8-0b "missing"), so the frame is not closed.
A standalone verbless utterance ("Merci Paul.", "Le test rouge."),
interjections and detached source markers are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,link", [
    ("Paul frobnique le test puis lance P.", "root"),
    ("Lance P puis Paul frobnique le test.", "puis_after=u1"),
    ("Paul lança le test et Nadia exécute Q.", "root"),
    ("Nadia exécute Q et Paul lança le test.", "et_after=u1"),
    ("Lance P, Paul frobnique le test.", "root"),
])
def test_unanalysed_clause_of_a_sequence_is_reported(text, link):
    f = parse_utterance(text)
    assert any(m.startswith("unanalyzed_predicative_content:") and m.split(":")[2] == link for m in f.missing)
    assert f.closure is False
    assert not any("frobnique" in a.text or "lança" in a.text for u in f.units for a in u.objects)


@pytest.mark.parametrize("text", [
    "Merci Paul.", "Le test rouge.", "Paul frobnique le test.",   # standalone: unchanged (M8-0b)
    "Merci Paul, lance P.", "Bonjour Marie, lance P.",           # interjection before a clause
    "Selon Marie, Paul a lancé P.",                               # detached source marker
    "Lance le test et le build.", "Lance P et Q.",               # NP coordination
    "Explique X108 et la gouvernance Obsidia.", "Lance le test et le build rouge.",
])
def test_no_new_missing_outside_sequences(text):
    assert parse_utterance(text).missing == ()


def test_detached_source_keeps_its_marker():
    f = parse_utterance("Selon Marie, Paul a lancé P.")
    assert f.units[0].epistemic == "HUMAN_SOURCE" and f.closure is True
