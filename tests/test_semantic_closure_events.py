"""Semantic Closure over the event layer (master block 26).

Stricter than frame.closure: explicit event references that are unresolved or
ambiguous, ambiguous / broken meta-event targets and event index conflicts
keep the request open, each named as a reason. A speech verb without a
propositional complement is not open. Nothing is resolved or authorised.
"""
from __future__ import annotations

import itertools

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.semantic_closure import semantic_closure


@pytest.mark.parametrize("text,prefix", [
    ("Marie dit que Paul a lancé P et que Nadia a exécuté Q.", "meta_target:AMBIGUOUS:MULTIPLE_TARGETS_UNSUPPORTED"),
    ("Paul a lancé le test et Nadia a lancé le build. Marie a vu ce lancement.",
     "event_reference:AMBIGUOUS:multiple_compatible_antecedents"),
    ("Marie a vu ce lancement.", "event_reference:UNRESOLVED:no_compatible_antecedent"),
    ("Lance le test mais ne lance pas le test.", "frame:contradiction:"),
    ("Prépare le test et le build puis ne le lance pas.", "frame:ambiguity:ambiguous_antecedent"),
])
def test_open_reasons_are_named(text, prefix):
    c = semantic_closure(parse_utterance(text))
    assert c.closed is False and any(r.startswith(prefix) for r in c.reasons)
    assert c.metadata["truth"] is None and c.metadata["resolution"] == "none"


@pytest.mark.parametrize("text", [
    "Paul a lancé P.", "Dis bonjour à maman.", "Paul a lancé le test. Marie a vu ce lancement.",
    "Marie dit que Paul a lancé P.", "Maman est là ?",
])
def test_resolved_requests_are_closed(text):
    c = semantic_closure(parse_utterance(text))
    assert c.closed is True and c.reasons == ()


def test_event_closure_is_never_weaker_than_frame_closure():
    subjects = ["Paul", "Marie dit que Paul", "Selon Marie, Paul", "Il paraît que Paul"]
    bodies = ["a lancé le test", "a lancé le test et Nadia a lancé le build. Marie a vu ce lancement",
              "lance le test puis Nadia l'arrête", "a lancé le test ou Nadia a exécuté le build",
              "dit que Nadia a lancé le test et que Luc a exécuté le build"]
    seen_open = seen_closed = 0
    for s, b in itertools.product(subjects, bodies):
        f = parse_utterance(f"{s} {b}.")
        c = semantic_closure(f)
        assert (not c.closed) == bool(c.reasons)
        if c.closed:
            assert f.closure
            seen_closed += 1
        else:
            seen_open += 1
        assert {f"frame:{b_}" for b_ in f.closure_blockers} <= set(c.reasons)
    assert seen_open and seen_closed
