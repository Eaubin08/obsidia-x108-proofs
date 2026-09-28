"""M1: OBSERVE and LEARN extraction use the shared immediate-target contract.

0 distinct immediate targets -> UNKNOWN, 1 -> resolved (unchanged output),
>1 -> AMBIGUOUS / MULTIPLE_TARGETS_UNSUPPORTED with no relation. Duplicate
edges to the same target are one target. No first-match, no embedded_under
fallback, identity through the EventIndex contract.
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

import pytest

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.meta_event_relations import MULTIPLE_TARGETS_UNSUPPORTED
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.primitives import LatticeRelation

EXTRACT = {"OBSERVE": extract_observation_event_targets, "LEARN": extract_knowledge_event_targets}
TEXT = {"OBSERVE": "J'ai vu Marie lancer le test.", "LEARN": "J'ai appris que Marie a lancé le test."}
RESOLVED = {"OBSERVE": ResolutionStatus.RESOLVED_STRUCTURAL, "LEARN": ResolutionStatus.RESOLVED_EXPLICIT}
RELATION = {"OBSERVE": "OBSERVES", "LEARN": "LEARNS_ABOUT"}


def _source_and_target(frame, family):
    source = next(u for u in frame.units if u.predicate == family)
    target = next(u for u in frame.units if u.embedded_under == source.id)
    return source, target


def _second_target(frame, family):
    """Add a second, distinct immediate structural target under the meta-event."""
    source, target = _source_and_target(frame, family)
    extra = replace(target, id="u9", span=(target.span[0] + 200, target.span[1] + 200))
    return replace(frame, units=frame.units + (extra,),
                   relations=frame.relations + (LatticeRelation("EMBEDS", source.id, "u9", evidence="forged"),))


def _run(frame, family, candidates=None):
    candidates = extract_event_candidates(frame) if candidates is None else candidates
    return EXTRACT[family](frame, candidates)


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_multiple_distinct_targets_are_ambiguous_and_unrelated(family):
    frame = _second_target(parse_utterance(TEXT[family]), family)
    result = _run(frame, family)

    assert len(result.targets) == 1
    target = result.targets[0]
    assert target.target_kind is TargetKind.UNKNOWN_TARGET
    assert target.resolution_status is ResolutionStatus.AMBIGUOUS
    assert target.provenance["reason"] == MULTIPLE_TARGETS_UNSUPPORTED
    assert sorted(target.provenance["candidate_predicate_ids"]) == sorted(
        [_source_and_target(frame, family)[1].id, "u9"])
    assert target.target_event is None and target.target_predicate is None
    assert result.relations == ()


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_single_target_output_is_unchanged(family):
    frame = parse_utterance(TEXT[family])
    result = _run(frame, family)
    source, target_unit = _source_and_target(frame, family)
    target_event = next(c for c in extract_event_candidates(frame) if c.predicate_ref == target_unit.id)

    assert [(t.target_kind, t.resolution_status, t.target_predicate, t.target_event) for t in result.targets] == [
        (TargetKind.EVENT_TARGET, RESOLVED[family], target_unit.id, target_event.event_ref.event_id)]
    assert result.targets[0].provenance["parser_relation"] == "EMBEDS"
    assert [(r.relation_kind.value, r.target_event) for r in result.relations] == [
        (RELATION[family], target_event.event_ref.event_id)]


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_duplicate_edges_to_same_target_are_one_target(family):
    frame = parse_utterance(TEXT[family])
    source, target = _source_and_target(frame, family)
    doubled = replace(frame, relations=frame.relations + (LatticeRelation("EMBEDS", source.id, target.id, evidence="dup"),))

    assert _run(doubled, family).to_dict() == _run(frame, family).to_dict()


@pytest.mark.parametrize("family, text, reason", [
    ("OBSERVE", "J'observe.", "no_structural_target"),
    ("LEARN", "J'ai appris.", "no_explicit_embedded_target"),
])
def test_zero_target_stays_unknown(family, text, reason):
    result = _run(parse_utterance(text), family)

    assert [(t.target_kind, t.resolution_status) for t in result.targets] == [
        (TargetKind.UNKNOWN_TARGET, ResolutionStatus.UNRESOLVED)]
    assert result.targets[0].provenance["reason"] == reason
    assert result.relations == ()


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_embedded_under_without_typed_relation_is_not_a_fallback_target(family):
    frame = parse_utterance(TEXT[family])
    source, target = _source_and_target(frame, family)
    untyped = replace(frame, relations=tuple(r for r in frame.relations if not (r.source == source.id and r.target == target.id)))
    result = _run(untyped, family)

    assert result.relations == ()
    assert all(t.target_event is None for t in result.targets)


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_conflicted_target_identity_fails_closed(family):
    frame = parse_utterance(TEXT[family])
    base = extract_event_candidates(frame)
    _, target = _source_and_target(frame, family)
    clash = tuple(replace(c, occurrence_status=OccurrenceStatus.NEGATED) for c in base if c.predicate_ref == target.id)
    result = _run(frame, family, tuple(base) + clash)

    assert result.relations == ()
    assert [(t.target_kind, t.resolution_status) for t in result.targets] == [
        (TargetKind.UNKNOWN_TARGET, ResolutionStatus.UNRESOLVED)]


@pytest.mark.parametrize("family", ["OBSERVE", "LEARN"])
def test_foreign_candidates_neither_used_nor_poisoning(family):
    frame = parse_utterance(TEXT[family])
    local = extract_event_candidates(frame)
    foreign = extract_event_candidates(parse_utterance(TEXT[family].replace("le test", "le build")))
    assert {c.predicate_ref for c in foreign} & {c.predicate_ref for c in local}

    assert _run(frame, family, tuple(local) + tuple(foreign)).to_dict() == _run(frame, family, local).to_dict()
    only_foreign = _run(frame, family, foreign)
    assert only_foreign.relations == ()
    assert [t.target_kind for t in only_foreign.targets] == [TargetKind.PROPOSITION_TARGET]


def test_unified_selection_adversarial_matrix():
    subjects, objects = ("J'ai", "Nadia a", "Le directeur a", "Luc a"), ("Marie", "Omar", "Léa", "Hugo")
    things = ("le test", "la suite", "le job", "le script")
    templates = {
        "OBSERVE": ("{s} vu {o} relancer {x}.", "Paul dit que {o} a vu Tom relancer {x}.",
                    "Paul croit que {o} a vu Tom relancer {x}."),
        "LEARN": ("{s} appris que {o} a relancé {x}.", "Paul dit que {o} a appris que Tom a relancé {x}.",
                  "Paul croit que {o} a appris que Tom a relancé {x}."),
    }
    metrics = dict.fromkeys(("CASES", "FIRST_MATCH", "FALSE_AMBIGUOUS", "WRONG_RESOLUTION",
                             "OCCURRENCE_CHANGED", "EVENT_ID_CHANGED", "RELATION_KIND_CHANGED"), 0)
    for family, (s, o, x) in product(("OBSERVE", "LEARN"), product(subjects, objects, things)):
        for template in templates[family]:
            frame = parse_utterance(template.format(s=s, o=o, x=x))
            source, target = _source_and_target(frame, family)
            base = extract_event_candidates(frame)
            target_event = next(c for c in base if c.predicate_ref == target.id)
            plain = _run(frame, family)
            meta = next(e for e in (plain.observation_events if family == "OBSERVE" else plain.knowledge_events)
                        if e.predicate_ref == source.id)
            doubled = replace(frame, relations=frame.relations + (LatticeRelation("EMBEDS", source.id, target.id),))
            forked = _second_target(frame, family)
            for variant, expect in ((frame, "one"), (doubled, "one"), (forked, "many")):
                result = _run(variant, family)
                metrics["CASES"] += 1
                mine = [t for t in result.targets if t.source_predicate == source.id]
                rels = [r for r in result.relations if r.source_event == meta.event_ref.event_id]
                if expect == "many":
                    if rels or any(t.target_event for t in mine):
                        metrics["FIRST_MATCH"] += 1
                    continue
                if any(t.resolution_status is ResolutionStatus.AMBIGUOUS for t in mine):
                    metrics["FALSE_AMBIGUOUS"] += 1
                if [r.target_event for r in rels] != [target_event.event_ref.event_id]:
                    metrics["WRONG_RESOLUTION"] += 1
                if [r.relation_kind.value for r in rels] != [RELATION[family]]:
                    metrics["RELATION_KIND_CHANGED"] += 1
                events = result.observation_events if family == "OBSERVE" else result.knowledge_events
                again = next(e for e in events if e.predicate_ref == source.id)
                if again.event_ref.event_id != meta.event_ref.event_id:
                    metrics["EVENT_ID_CHANGED"] += 1
                if again.occurrence_status is not meta.occurrence_status:
                    metrics["OCCURRENCE_CHANGED"] += 1

    assert metrics["CASES"] >= 1000
    for key, value in metrics.items():
        if key != "CASES":
            assert value == 0, (key, metrics)
