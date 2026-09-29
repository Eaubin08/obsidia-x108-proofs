"""NO SILENT DROP: a clause with a demonstrative subject and an unknown verb is reported.

"Ça parle de KX108 et Paul lance P": "ça" / "cela" / "ceci" were neither
subject pronouns nor content words, so the clause "ça parle de KX108"
produced no unit, no missing entry, and the frame was declared closed (or
the clause was absorbed into its neighbour and "ça" read as its object).
A demonstrative subject followed by an unknown word is now handled exactly
like a subject pronoun ("il parle de KX108"): the clause is kept as
unanalysed predicative content (M8-0b "missing"), which blocks closure. No
unit, occurrence, gate or truth is created for it.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

MISSING = "unanalyzed_predicative_content:"


@pytest.mark.parametrize("text,content", [
    ("Ça parle de KX108 et Paul lance P.", "Ça parle de KX108"),
    ("Cela concerne le build et Paul lance P.", "Cela concerne le build"),
    ("Ça marche et Paul lance P.", "Ça marche"),
    ("Ceci frobnique le test puis lance P.", "Ceci frobnique le test"),
    ("Paul lance P et ça parle de KX108.", "ça parle de KX108"),
    ("Lance P, cela concerne le build.", "cela concerne le build"),
    ("Ça parle de KX108.", "Ça parle de KX108"),
    ("Ça ne marche pas et Paul lance P.", "Ça ne marche pas"),
])
def test_demonstrative_clause_is_named_missing(text, content):
    f = parse_utterance(text)
    spans = [tuple(int(x) for x in m.split(":")[1].split("-")) for m in f.missing if m.startswith(MISSING)]
    assert any(f.raw[a:b].rstrip(" .") == content for a, b in spans)
    assert f.closure is False and not semantic_closure(f).closed
    # nothing of the clause is absorbed by a neighbour, nor resolved as a reference
    assert not any(w in a.text for u in f.units for a in u.objects for w in ("parle", "concerne", "marche", "ça", "cela"))
    assert not any("ça" in r or "cela" in r for r in f.unresolved_references)


def test_no_unit_gate_or_occurrence_is_created_for_it():
    f = parse_utterance("Ça parle de KX108 et Paul lance P.")
    ref = parse_utterance("Paul lance P.")
    assert [(u.lemma, u.pragmatic, u.subject) for u in f.units] == [(u.lemma, u.pragmatic, u.subject) for u in ref.units]
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    assert not any(gate.values())
    assert len(build_frame_event_index(f).events()) == len(build_frame_event_index(ref).events())


@pytest.mark.parametrize("text", [
    "Ça va.", "Ça, c'est bon.", "J'ai vu ça.", "Merci pour ça.", "Ça aussi.", "Pas ça.", "Et ça ?",
    "Ça va et Paul lance P.", "C'est bon et Paul lance P.", "Fais ça et lance P.", "Lance ça.",
])
def test_no_new_missing_for_known_or_verbless_demonstratives(text):
    f = parse_utterance(text)
    assert not any(m.startswith(MISSING) for m in f.missing)
