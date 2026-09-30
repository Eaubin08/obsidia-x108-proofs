"""R1 (NF4-ROOT): the absence of a subject is not a proof of imperative.

"Exécutent Q." / "Exécutes Q." / "Font Q." / "Fait Q.": _build_drafts made
every subject-less present an IMPERATIVE, so a finite form with no
imperative reading became an addressee request (gated for world actions).
When the lemma has an imperative paradigm in the lexicon and the observed
form is not one of its imperative forms, the form stays FINITE with an
unresolved subject: EMBEDDED with unresolved governance (no assertion, no
request, no gate), named subject_unresolved (closure open). Genuine
imperatives ("Exécute Q.", "Exécutez Q.", "Fais Q.") are unchanged, and a
lemma whose imperative morphology is absent from the lexicon ("Vois Q.")
keeps the conservative imperative reading.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.lexicon import has_imperative_paradigm
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure


def _view(text):
    f = parse_utterance(text)
    return f, {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", ["Exécutent Q.", "Exécutes Q.", "Font Q.", "Fait Q.", "Lancent P et exécutent Q."])
def test_finite_form_without_imperative_reading_is_not_a_request(text):
    f, gate = _view(text)
    for u in f.units:
        assert (u.verb_form, u.subject) == ("FINITE", None)
        assert u.pragmatic == "EMBEDDED" and u.request_target == "NONE" and not gate[u.id]
        assert f"subject_unresolved:{u.id}" in f.ambiguities
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text,gated", [
    ("Exécute Q.", True), ("Exécutez Q.", True), ("Fais Q.", False), ("Lance P.", True),
    ("Lançons P.", True), ("Vois Q.", False), ("Lance P et exécute Q.", True),
    ("Disons Q.", False), ("Faites Q.", False),
])
def test_genuine_or_undecidable_imperatives_unchanged(text, gated):
    f, gate = _view(text)
    u = f.units[-1]
    assert (u.verb_form, u.pragmatic) == ("IMPERATIVE", "REQUESTED")
    assert gate[u.id] is gated


def test_imperative_paradigm_is_read_from_the_lexicon():
    assert has_imperative_paradigm("exécuter") and has_imperative_paradigm("faire")
    assert not has_imperative_paradigm("voir")


@pytest.mark.parametrize("text", ["Paul lance P et exécute Q.", "Run the tests.", "Please run the tests.",
                                  "Lancera le test.", "Supposait que Paul lance P."])
def test_subject_sharing_and_english_unchanged(text):
    f, _ = _view(text)
    assert not any(a.startswith("subject_unresolved") for a in f.ambiguities)
