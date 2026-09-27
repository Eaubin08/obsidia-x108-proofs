"""EventIndex V0: immutable, frame-local, predicate_ref -> at most one EventRef.

The index consumes existing extractor outputs (no new ids) and records
incompatible proposals as explicit conflicts instead of choosing one.
"""
from __future__ import annotations

import random
from dataclasses import replace

import pytest

from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_index import EventIndex, build_event_index, build_frame_event_index
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets


def _groups(frame):
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base).observation_events
    knowledge = extract_knowledge_event_targets(frame, base).knowledge_events
    return tuple(base), tuple(observation), tuple(knowledge)


def test_index_consumes_existing_extractor_outputs_without_new_ids():
    frame = parse_utterance("Paul dit qu'il a vu Marie lancer le test.")
    base, observation, knowledge = _groups(frame)
    index = build_event_index(frame, base, observation, knowledge)

    assert index.conflicts == ()
    assert set(index.by_predicate) == {c.predicate_ref for c in base + observation + knowledge}
    for candidate in base + observation + knowledge:
        assert index.event_for(candidate.predicate_ref) is candidate
        assert index.by_event_id(candidate.event_ref.event_id) is candidate


def test_build_frame_event_index_equals_explicit_build():
    frame = parse_utterance("J'ai appris que Paul a dit que Marie a lancé le test.")
    explicit = build_event_index(frame, *_groups(frame))
    implicit = build_frame_event_index(frame)

    assert {p: c.event_ref.event_id for p, c in explicit.by_predicate.items()} == \
        {p: c.event_ref.event_id for p, c in implicit.by_predicate.items()}
    kinds = {c.event_ref.event_kind for c in implicit.events()}
    assert {EventKind.KNOWLEDGE_ACQUISITION, EventKind.REPORT, EventKind.ACTION} <= kinds


def test_index_is_deterministic_and_order_independent():
    frame = parse_utterance("Paul croit que Marie a vu Jean lancer le test.")
    groups = _groups(frame)
    flat = [c for group in groups for c in group]
    reference = build_event_index(frame, *groups)
    for seed in range(5):
        shuffled = flat[:]
        random.Random(seed).shuffle(shuffled)
        other = build_event_index(frame, shuffled)
        assert {p: c.event_ref.event_id for p, c in other.by_predicate.items()} == \
            {p: c.event_ref.event_id for p, c in reference.by_predicate.items()}
        assert [c.predicate_ref for c in other.events()] == [c.predicate_ref for c in reference.events()]


def test_events_follow_frame_unit_order():
    frame = parse_utterance("Paul dit que Marie dit que Jean a lancé le test.")
    index = build_frame_event_index(frame)
    order = [unit.id for unit in frame.units]

    assert [c.predicate_ref for c in index.events()] == sorted(index.by_predicate, key=order.index)


def test_identical_duplicate_is_not_a_conflict():
    frame = parse_utterance("Paul a lancé le test.")
    base = extract_event_candidates(frame)
    index = build_event_index(frame, base, base)

    assert index.conflicts == ()
    assert len(index.by_predicate) == 1


@pytest.mark.parametrize("mutate, reason", [
    (lambda c: replace(c, event_ref=replace(c.event_ref, event_kind=EventKind.OBSERVATION)), "incompatible_event_refs"),
    (lambda c: replace(c, occurrence_status=OccurrenceStatus.NEGATED), "incompatible_event_refs"),
    (lambda c: replace(c, event_ref=replace(c.event_ref, event_id="event:other")), "incompatible_event_refs"),
])
def test_incompatible_proposals_are_explicit_conflicts_and_excluded(mutate, reason):
    frame = parse_utterance("Paul a lancé le test.")
    base = extract_event_candidates(frame)
    index = build_event_index(frame, base, tuple(mutate(c) for c in base))

    assert index.event_for(base[0].predicate_ref) is None
    assert [(c.predicate_ref, c.reason) for c in index.conflicts] == [(base[0].predicate_ref, reason)]
    assert len(index.conflicts[0].event_ids) >= 1


def test_foreign_frame_and_unknown_predicate_are_rejected():
    frame = parse_utterance("Paul a lancé le test.")
    foreign = extract_event_candidates(parse_utterance("Paul a lancé le build."))
    unscoped = tuple(replace(c, event_ref=replace(c.event_ref, source_frame=None)) for c in extract_event_candidates(frame))
    stray = tuple(replace(c, predicate_ref="u99", event_ref=replace(c.event_ref, predicate_ref="u99"))
                  for c in extract_event_candidates(frame))
    index = build_event_index(frame, foreign, unscoped, stray)

    assert index.by_predicate == {}
    assert sorted(c.reason for c in index.conflicts) == ["frame_mismatch", "frame_mismatch", "predicate_not_in_frame"]


def test_event_id_collision_across_predicates_is_a_conflict():
    frame = parse_utterance("Paul a lancé le build et Paul a lancé le test.")
    first, second = extract_event_candidates(frame)
    clash = replace(second, event_ref=replace(second.event_ref, event_id=first.event_ref.event_id))
    index = build_event_index(frame, (first, clash))

    assert index.by_predicate == {}
    assert {c.reason for c in index.conflicts} == {"event_id_collision"}


def test_index_is_immutable():
    index = build_frame_event_index(parse_utterance("Paul a lancé le test."))

    assert isinstance(index, EventIndex)
    with pytest.raises(TypeError):
        index.by_predicate["u9"] = None  # type: ignore[index]
    with pytest.raises(AttributeError):
        index.frame_ref = "frame:x"  # type: ignore[misc]


def test_corpus_frames_index_without_conflicts():
    texts = [
        "Paul dit que Marie a lancé le test.", "Paul croit que Marie a vu Jean lancer le test.",
        "J'ai appris que Paul a dit que Marie a lancé le test.", "Paul dit que Marie a appris que Jean a lancé le test.",
        "Paul confirme que Marie a lancé le test.", "Paul nie que Marie a lancé le test.",
        "Paul a lancé le build et Paul a lancé le test.", "Je vois Marie lancer le test.",
    ]
    for i in range(40):
        for text in texts:
            frame = parse_utterance(text.replace("le test", f"le test {i}"))
            index = build_frame_event_index(frame)
            groups = _groups(frame)
            assert index.conflicts == ()
            assert len(index.by_predicate) == sum(len(g) for g in groups)
