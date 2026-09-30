"""G6: an exact same-frame positive / negative occurrence pair is never silently closed.

"Paul a lancé P et Paul n'a pas lancé P": both claims were kept, nothing was
named and closure was True, as if the frame were fully understood.

Contradiction resolution (temporal anchors, perspectives, versions, sources)
is held doctrine (H06). Safety only: when two root assertions of one frame
are the same clause word for word except for the negation (same subject,
same verb form, same object, no temporal or source adjunct), both claims are
kept as they are, neither is marked false, nothing is merged, and the pair is
named as a possible conflict (occurrence_conflict_open), which blocks closure.
It means "requires contradiction / temporal / perspective resolution", not
"contradiction proven". Pairs that differ in anything else, or whose
comparison would need reference, temporal or perspective doctrine, are left
untouched.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance


def _claims(f):
    return {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text", [
    "Paul a lancé P et Paul n'a pas lancé P.",
    "Paul n'a pas lancé P et Paul a lancé P.",
    "Paul a lancé P mais Paul n'a pas lancé P.",
    "Paul a lancé P. Paul n'a pas lancé P.",
    "Paul lance P et Paul ne lance pas P.",
    "Le test a lancé P et le test n'a pas lancé P.",
    "Paul a exécuté le test et Paul n'a pas exécuté le test.",
])
def test_exact_positive_negative_pair_is_named_and_blocks_closure(text):
    base = parse_utterance(text.replace(" n'a pas ", " a ").replace(" ne lance pas ", " lance "))
    f = parse_utterance(text)
    a, b = f.units
    assert {a.polarity, b.polarity} == {"positive", "negative"}
    assert (a.pragmatic, b.pragmatic) == ("ASSERTED", "ASSERTED")          # neither resolved nor falsified
    assert f"occurrence_conflict_open:{a.id}:{b.id}" in f.ambiguities
    events = build_frame_event_index(f).events()
    assert len({c.event_ref.event_id for c in events}) == 2                 # both kept, not merged
    assert _claims(f) == _claims(parse_utterance(text)) and len(_claims(f)) == 2
    assert f.contradictions == ()                                           # not a proven contradiction
    assert not f.closure
    assert base.closure and not any(x.startswith("occurrence_conflict_open") for x in base.ambiguities)


@pytest.mark.parametrize("text", [
    "Paul a lancé P et Nadia n'a pas lancé P.",               # other subject
    "Paul a lancé P et Paul n'a pas lancé Q.",                # other object
    "Paul a lancé P et Paul n'a pas exécuté P.",              # other predicate
    "Paul a lancé P et il n'a pas lancé P.",                  # needs reference resolution
    "Paul lançait P et Paul ne lance pas P.",                 # other tense
    "Paul a lancé P hier et Paul n'a pas lancé P aujourd'hui.",  # temporal anchors (H05)
    "Marie dit que Paul a lancé P et Paul n'a pas lancé P.",  # perspective (H03)
    "Paul a lancé P puis Paul n'a pas lancé P.",              # sequence (H05)
    "Paul a lancé P ou Paul n'a pas lancé P.",                # disjunction
    "Paul a lancé P et Paul n'a pas lancé P ?",               # question
])
def test_non_exact_pairs_are_left_untouched(text):
    f = parse_utterance(text)
    assert not any(x.startswith("occurrence_conflict_open") for x in f.ambiguities)


def test_single_negative_assertion_is_unchanged():
    f = parse_utterance("Paul n'a pas lancé P.")
    assert f.closure and not f.ambiguities
