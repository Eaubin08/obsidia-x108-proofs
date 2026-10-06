"""D3 / D4: a compound coordinated member keeps its subject; contradictions are named.

"Paul a lancé P et a lancé / n'a pas lancé Q": the member has its own auxiliary; it lost
its subject (None, unnamed). It now shares the host's explicit subject when the written
auxiliary agrees (person read on the auxiliary form, no proximity fallback); otherwise the
subject stays unresolved and named. Members sharing a coordinated subject hold the whole
subject ("paul et nadia"), never its last member. With the subject recovered, "Paul a lancé
P et n'a pas lancé P" is named as an occurrence conflict (D4); no winner is chosen.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


def _subj(f):
    return [u.subject for u in f.units]


@pytest.mark.parametrize("text,subjects", [
    ("Paul a lancé P et a lancé Q.", ["paul", "paul"]),
    ("Paul a lancé P et n'a pas lancé Q.", ["paul", "paul"]),
    ("Tu as lancé P et as lancé Q.", ["tu", "tu"]),
    ("Paul et Nadia ont lancé P et ont lancé Q.", ["paul et nadia", "paul et nadia"]),
    ("Paul et Nadia lancent P et lancent Q.", ["paul et nadia", "paul et nadia"]),
])
def test_compound_member_shares_subject(text, subjects):
    f = parse_utterance(text)
    assert _subj(f) == subjects and f.closure


def test_non_agreeing_member_is_named_unresolved():
    f = parse_utterance("Paul a lancé P et ont lancé Q.")
    assert _subj(f) == ["paul", None] and "subject_unresolved:u2" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Paul a lancé P et n'a pas lancé P.", "Paul lance P et ne lance pas P.",
                                  "Paul a lancé P et Paul n'a pas lancé P."])
def test_occurrence_conflict_named(text):
    f = parse_utterance(text)
    assert "occurrence_conflict_open:u1:u2" in f.ambiguities and not f.closure
    assert [u.polarity for u in f.units] == ["positive", "negative"]
