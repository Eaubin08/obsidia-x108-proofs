"""Full-frame event identity: discover every event first, bind meta-event
targets second, on the SAME complete frame EventIndex.

OBSERVE -> LEARN and LEARN -> OBSERVE must resolve to the target EventRef that
exists in the full frame (they used to fall back to PROPOSITION_TARGET because
each extractor bound against a partial, family-local index). Event ids and
occurrence are unchanged; conflicts fail closed; foreign frames are rejected.
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

import pytest

from app.semantic.lattice import event_index as EI
from app.semantic.lattice import knowledge_event_extraction as KE
from app.semantic.lattice import observation_event_extraction as OE
from app.semantic.lattice import review_join as RJ
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_index import build_event_index, build_frame_event_index, target_index_violation
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)
OBSERVE_LEARN = f"J{A}ai vu que Marie a appris que Paul a lancé le test."
LEARN_OBSERVE = f"J{A}ai appris que Marie a vu Jean lancer le test."


def _frame(text):
    frame = parse_utterance(text)
    return frame, build_frame_event_index(frame), extract_event_candidates(frame)


def _unit(frame, predicate):
    return next(u for u in frame.units if u.predicate == predicate)


def test_observe_to_learn_binds_learn_event_on_full_index():
    frame, full, base = _frame(OBSERVE_LEARN)
    observe, learn = _unit(frame, "OBSERVE"), _unit(frame, "LEARN")
    learn_event = full.event_for(learn.id)
    result = OE.extract_observation_event_targets(frame, base)

    assert learn_event is not None
    target = next(t for t in result.targets if t.source_predicate == observe.id)
    assert (target.target_kind.value, target.target_predicate, target.target_event) == (
        "EVENT_TARGET", learn.id, learn_event.event_ref.event_id)
    assert target_index_violation(target, full) is None
    assert [(r.relation_kind.value, r.target_event) for r in result.relations] == [
        ("OBSERVES", learn_event.event_ref.event_id)]


def test_learn_to_observe_binds_observation_event_on_full_index():
    frame, full, base = _frame(LEARN_OBSERVE)
    learn, observe = _unit(frame, "LEARN"), _unit(frame, "OBSERVE")
    observation_event = full.event_for(observe.id)
    result = KE.extract_knowledge_event_targets(frame, base)

    target = next(t for t in result.targets if t.source_predicate == learn.id)
    assert (target.target_kind.value, target.target_event) == ("EVENT_TARGET", observation_event.event_ref.event_id)
    assert target.resolution_status.value == "RESOLVED_EXPLICIT"
    assert [r.relation_kind.value for r in result.relations] == ["LEARNS_ABOUT"]


def test_binding_is_independent_of_which_candidates_the_caller_supplies():
    for text in (OBSERVE_LEARN, LEARN_OBSERVE):
        frame, _, base = _frame(text)
        observations = OE.extract_observation_event_targets(frame, base)
        knowledge = KE.extract_knowledge_event_targets(frame, base)
        enriched = tuple(base) + tuple(observations.observation_events) + tuple(knowledge.knowledge_events)
        assert OE.extract_observation_event_targets(frame, enriched).to_dict() == observations.to_dict()
        assert KE.extract_knowledge_event_targets(frame, enriched).to_dict() == knowledge.to_dict()


def test_full_index_build_needs_no_binding(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("index build must use discovery only")

    for module in (OE, KE, EI):
        for name in ("extract_observation_event_targets", "extract_knowledge_event_targets"):
            if hasattr(module, name):
                monkeypatch.setattr(module, name, forbidden)
    frame = parse_utterance(OBSERVE_LEARN)
    index = build_frame_event_index(frame)
    assert {c.event_ref.event_kind.value for c in index.events()} == {"OBSERVATION", "KNOWLEDGE_ACQUISITION", "ACTION"}


def test_discovery_mints_the_same_ids_and_occurrence_as_wrappers():
    for text in (OBSERVE_LEARN, LEARN_OBSERVE, "Si Paul a vu que Marie a appris que Jean a lancé le test, Luc attend."):
        frame, full, base = _frame(text)
        discovered = (*OE.discover_observation_events(frame), *KE.discover_knowledge_events(frame, base))
        wrapped = (*OE.extract_observation_event_targets(frame, base).observation_events,
                   *KE.extract_knowledge_event_targets(frame, base).knowledge_events)
        assert [c.to_dict() for c in discovered] == [c.to_dict() for c in wrapped]
        for candidate in discovered:
            indexed = full.event_for(candidate.predicate_ref)
            assert indexed.event_ref.event_id == candidate.event_ref.event_id
            assert indexed.occurrence_status is candidate.occurrence_status


@pytest.mark.parametrize("text, outer, inner", [
    (f"J{A}ai vu Marie voir Jean lancer le test.", "OBSERVE", "OBSERVE"),
    (f"J{A}ai appris que Marie a appris que Jean a lancé le test.", "LEARN", "LEARN"),
    (f"J{A}ai vu que Marie a dit que Jean a lancé le test.", "OBSERVE", "SAY"),
    (f"J{A}ai vu que Marie croit que Jean a lancé le test.", "OBSERVE", "BELIEVE"),
    (f"J{A}ai appris que Marie a dit que Jean a lancé le test.", "LEARN", "SAY"),
    (f"J{A}ai appris que Marie croit que Jean a lancé le test.", "LEARN", "BELIEVE"),
    (f"J{A}ai vu Marie lancer le test.", "OBSERVE", "EXECUTE"),
    (f"J{A}ai appris que Marie a lancé le test.", "LEARN", "EXECUTE"),
])
def test_same_family_and_previously_correct_pairings_stay_event_targets(text, outer, inner):
    frame, full, base = _frame(text)
    src = next(u for u in frame.units if u.predicate == outer)
    tgt = next(u for u in frame.units if u.embedded_under == src.id and u.predicate == inner)
    result = (OE.extract_observation_event_targets if outer == "OBSERVE" else KE.extract_knowledge_event_targets)(frame, base)
    target = next(t for t in result.targets if t.source_predicate == src.id)

    assert (target.target_kind.value, target.target_event) == ("EVENT_TARGET", full.event_for(tgt.id).event_ref.event_id)


def test_conflicted_full_frame_target_fails_closed():
    frame, full, base = _frame(OBSERVE_LEARN)
    learn = full.event_for(_unit(frame, "LEARN").id)
    conflicted = tuple(base) + (replace(learn, occurrence_status=OccurrenceStatus.NEGATED),)
    result = OE.extract_observation_event_targets(frame, conflicted)

    assert result.relations == ()
    assert [(t.target_kind.value, t.resolution_status.value) for t in result.targets] == [("UNKNOWN_TARGET", "UNRESOLVED")]


def test_foreign_candidates_are_neither_used_nor_poisoning():
    frame, _, base = _frame(OBSERVE_LEARN)
    foreign = extract_event_candidates(parse_utterance(f"J{A}ai vu que Marie a appris que Paul a lancé le build."))
    assert OE.extract_observation_event_targets(frame, tuple(base) + tuple(foreign)).to_dict() == \
        OE.extract_observation_event_targets(frame, base).to_dict()


def test_review_join_gains_the_repaired_perspective():
    frame, full, _ = _frame(OBSERVE_LEARN)
    env = RJ.build_review_envelope(frame, full.event_for(_unit(frame, "OBSERVE").id).event_ref.event_id, full)

    assert [e["predicate"] for e in env.events] == ["OBSERVE", "LEARN", "EXECUTE"]
    assert sorted(r.relation_kind.value for r in env.relations) == ["LEARNS_ABOUT", "OBSERVES"]
    assert env.non_event_targets == ()


def test_full_frame_identity_adversarial_matrix():
    rel = {"OBSERVE": "{s} a vu que {o} {v}", "LEARN": "{s} a appris que {o} {v}", "SAY": "{s} dit que {o} {v}",
           "BELIEVE": "{s} croit que {o} {v}"}
    inner = {"OBSERVE": "a vu Tom relancer {x}", "LEARN": "a appris que Tom a relancé {x}",
             "SAY": "a dit que Tom a relancé {x}", "BELIEVE": "croit que Tom a relancé {x}"}
    mid = {"OBSERVE": "a vu que Luc {v}", "LEARN": "a appris que Luc {v}", "SAY": "a dit que Luc {v}",
           "BELIEVE": "croit que Luc {v}"}
    metrics = dict.fromkeys((
        "CASES", "FULL_EVENT_EXISTS_BUT_PROPOSITION", "MISSING_EVENT_RELATION", "DUPLICATE_EVENT_ID",
        "CONFLICT_FIRST_MATCH", "CROSS_FRAME_ACCEPTED", "PRODUCER_INPUT_DEPENDENCE", "WRONG_TARGET_EVENT",
        "OBSERVE_TO_LEARN_RESOLVED", "LEARN_TO_OBSERVE_RESOLVED", "CONFLICT_CASES", "FOREIGN_FRAME_CASES",
    ), 0)

    def check(text):
        frame, full, base = _frame(text)
        metrics["CASES"] += 1
        ids = [c.event_ref.event_id for c in full.events()]
        metrics["DUPLICATE_EVENT_ID"] += len(ids) != len(set(ids))
        o = OE.extract_observation_event_targets(frame, base)
        k = KE.extract_knowledge_event_targets(frame, base)
        enriched = tuple(base) + tuple(o.observation_events) + tuple(k.knowledge_events)
        if (OE.extract_observation_event_targets(frame, enriched).to_dict() != o.to_dict()
                or KE.extract_knowledge_event_targets(frame, enriched).to_dict() != k.to_dict()):
            metrics["PRODUCER_INPUT_DEPENDENCE"] += 1
        relations = {(r.source_event, r.target_event) for r in (*o.relations, *k.relations)}
        for t in (*o.targets, *k.targets):
            src = frame.unit(t.source_predicate)
            tgt_units = [u for u in frame.units if u.embedded_under == src.id]
            if not tgt_units:
                continue
            tgt = tgt_units[0]
            indexed = full.event_for(tgt.id)
            if indexed is None:
                continue
            if t.target_kind.value == "PROPOSITION_TARGET":
                metrics["FULL_EVENT_EXISTS_BUT_PROPOSITION"] += 1
            if t.target_kind.value == "EVENT_TARGET" and t.target_event != indexed.event_ref.event_id:
                metrics["WRONG_TARGET_EVENT"] += 1
            if (t.source_event, indexed.event_ref.event_id) not in relations:
                metrics["MISSING_EVENT_RELATION"] += 1
            elif src.predicate == "OBSERVE" and tgt.predicate == "LEARN":
                metrics["OBSERVE_TO_LEARN_RESOLVED"] += 1
            elif src.predicate == "LEARN" and tgt.predicate == "OBSERVE":
                metrics["LEARN_TO_OBSERVE_RESOLVED"] += 1
        return frame, full, base

    people = ("Nadia", "Omar", "Léa", "Hugo", "Anne")
    for (s, o_), x in product(product(people, repeat=2), ("le script", "la suite", "le job", "le lot", "le test", "le déploiement")):
        if s == o_:
            continue
        for outer, inn in product(rel, inner):
            check(rel[outer].format(s=s, o=o_, v=inner[inn].format(x=x)) + ".")
            check(rel[outer].format(s=s, o=o_, v=mid[inn].format(v=inner[outer].format(x=x))) + ".")
        check(f"Si {s} a vu que {o_} a appris que Tom a relancé {x}, Luc attend.")
        frame, full, base = check(f"J{A}ai vu que {o_} a appris que Tom a relancé {x}.")
        learn = next(c for c in full.events() if c.event_ref.event_kind.value == "KNOWLEDGE_ACQUISITION")
        bad = OE.extract_observation_event_targets(frame, tuple(base) + (replace(learn, occurrence_status=OccurrenceStatus.NEGATED),))
        metrics["CONFLICT_CASES"] += 1
        metrics["CONFLICT_FIRST_MATCH"] += bool(bad.relations)
        foreign = extract_event_candidates(parse_utterance(f"{s} dit que {o_} a relancé le build."))
        metrics["FOREIGN_FRAME_CASES"] += 1
        metrics["CROSS_FRAME_ACCEPTED"] += len(build_event_index(frame, foreign).by_predicate) > 0

    assert metrics["CASES"] >= 3500
    for key in ("OBSERVE_TO_LEARN_RESOLVED", "LEARN_TO_OBSERVE_RESOLVED", "CONFLICT_CASES", "FOREIGN_FRAME_CASES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("FULL_EVENT_EXISTS_BUT_PROPOSITION", "MISSING_EVENT_RELATION", "DUPLICATE_EVENT_ID",
                "CONFLICT_FIRST_MATCH", "CROSS_FRAME_ACCEPTED", "PRODUCER_INPUT_DEPENDENCE", "WRONG_TARGET_EVENT"):
        assert metrics[key] == 0, (key, metrics)
