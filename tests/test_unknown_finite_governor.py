"""NF3c: an infinitive after an unknown finite governor is never an addressee request.

"Paul n'aime pas lancer P": "aimer" is not in the lexicon, so the
infinitive was a bare injunctive REQUESTED unit with a gate ("Paul aime
lancer P" even gave it the subject "paul aime"). Generically, without
adding the verb to the lexicon: a bare infinitive whose left context is
subject + unknown content word (+ ne / pas / ni) is governed by that
unrecognised word. It stays EMBEDDED with the existing named marker
infinitive_under_unrecognized_governor (closure open), takes no subject
from the unknown word, and has no gate. Known governors, prepositions and
real imperatives are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _view(text):
    f = parse_utterance(text)
    return f, {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text,n", [
    ("Paul aime lancer P.", 1),
    ("Paul n'aime pas lancer P.", 1),
    ("Paul n'aime ni lancer P ni exécuter Q.", 2),
    ("Paul adore exécuter le test.", 1),
    ("Je déteste lancer P.", 1),
    ("Le script frobnique lancer P.", 1),
    ("Tu préfères lancer P ?", 1),
])
def test_infinitive_under_unknown_governor_is_named_not_requested(text, n):
    f, gate = _view(text)
    assert len(f.units) == n
    for u in f.units:
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in REQUESTS and not gate[u.id]
        assert u.request_target == "NONE"
        assert u.subject is None or " " not in u.subject
        assert f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text,prag", [
    ("Lance P.", "REQUESTED"),
    ("Paul veut lancer P.", "ASSERTED"),
    ("Il faut lancer P.", "REQUESTED"),
    ("Pour lancer P, Paul attend.", "EMBEDDED"),
    ("Paul, lance P.", "REQUESTED"),
])
def test_known_governors_and_imperatives_unchanged(text, prag):
    f, _ = _view(text)
    (u,) = [x for x in f.units if x.lemma == "lancer"]
    assert u.pragmatic == prag
    assert not any(a.startswith("infinitive_under_unrecognized_governor") for a in f.ambiguities)
