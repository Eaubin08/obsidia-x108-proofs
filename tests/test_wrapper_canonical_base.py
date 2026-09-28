"""Meta-event wrappers always bind on the canonical frame base.

extract_observation_event_targets / extract_knowledge_event_targets must not
depend on which candidates the caller supplies: the canonical base
(extract_event_candidates(frame)) always participates in the binding index,
caller candidates are only proposals (identical -> merged, incompatible ->
conflict, foreign -> rejected). Caller omission is not event non-existence.
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

import pytest

from app.semantic.lattice import knowledge_event_extraction as KE
from app.semantic.lattice import observation_event_extraction as OE
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_index import build_frame_event_index, target_index_violation
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.french_grammar import parse_utterance

OUTER = {"OBSERVE": "{s} a vu que {c}.", "LEARN": "{s} a appris que {c}."}
INNER = {
    "ACTION": "Paul a lancé {x}",
    "REPORT": "{s} a dit que Paul a lancé {x}",
    "BELIEF": "{s} croit que Paul a lancé {x}",
    "OBSERVE": "{s} a vu Paul lancer {x}",
    "LEARN": "{s} a appris que Paul a lancé {x}",
}
WRAPPER = {"OBSERVE": OE.extract_observation_event_targets, "LEARN": KE.extract_knowledge_event_targets}
FOREIGN = extract_event_candidates(parse_utterance("Omar a relancé le lot."))


def _case(outer, inner, s1="Marie", s2="Jean", x="le test"):
    frame = parse_utterance(OUTER[outer].format(s=s1, c=INNER[inner].format(s=s2, x=x)))
    return frame, extract_event_candidates(frame), build_frame_event_index(frame)


def _outer_target(result, frame):
    return next(t for t in result.targets if t.source_predicate == frame.units[0].id)


def _semantic(result):
    return result.to_dict()


def _partials(base, target_id):
    by_kind = lambda kind: tuple(c for c in base if c.event_ref.event_kind is kind)
    return {
        "empty": (),
        "only_action": by_kind(EventKind.ACTION),
        "only_report": by_kind(EventKind.REPORT),
        "only_belief": by_kind(EventKind.BELIEF),
        "only_unrelated": FOREIGN,
        "target_removed": tuple(c for c in base if c.predicate_ref != target_id),
    }


@pytest.mark.parametrize("outer", ["OBSERVE", "LEARN"])
def test_empty_caller_still_binds_canonical_action_event(outer):
    frame, _, full = _case(outer, "ACTION")
    target = _outer_target(WRAPPER[outer](frame, ()), frame)
    action = full.event_for(frame.units[1].id)

    assert action is not None and action.event_ref.event_kind is EventKind.ACTION
    assert (target.target_kind.value, target.target_event) == ("EVENT_TARGET", action.event_ref.event_id)
    assert target_index_violation(target, full) is None


@pytest.mark.parametrize("outer, inner", list(product(OUTER, INNER)))
def test_partial_caller_matches_canonical_base(outer, inner):
    frame, base, full = _case(outer, inner)
    reference = WRAPPER[outer](frame, base)
    target = _outer_target(reference, frame)

    assert (target.target_kind.value, target.target_event) == (
        "EVENT_TARGET", full.event_for(frame.units[1].id).event_ref.event_id)
    for name, cands in _partials(base, frame.units[1].id).items():
        assert _semantic(WRAPPER[outer](frame, cands)) == _semantic(reference), name


@pytest.mark.parametrize("outer", ["OBSERVE", "LEARN"])
def test_identical_duplicates_and_order_do_not_change_semantics(outer):
    frame, base, full = _case(outer, "REPORT")
    reference = _semantic(WRAPPER[outer](frame, base))
    for cands in (tuple(base) * 2, tuple(reversed(base)), full.events(), tuple(base) + tuple(full.events())):
        assert _semantic(WRAPPER[outer](frame, cands)) == reference


@pytest.mark.parametrize("outer", ["OBSERVE", "LEARN"])
@pytest.mark.parametrize("caller", ["empty", "base"])
@pytest.mark.parametrize("forgery", ["occurrence", "event_id", "kind"])
def test_same_frame_incompatible_proposal_fails_closed(outer, caller, forgery):
    frame, base, full = _case(outer, "ACTION")
    canonical = full.event_for(frame.units[1].id)
    forged = {
        "occurrence": replace(canonical, occurrence_status=OccurrenceStatus.NEGATED),
        "event_id": replace(canonical, event_ref=replace(canonical.event_ref, event_id="event:forged0000000000")),
        "kind": replace(canonical, event_ref=replace(canonical.event_ref, event_kind=EventKind.REPORT)),
    }[forgery]
    result = WRAPPER[outer](frame, (() if caller == "empty" else tuple(base)) + (forged,))
    target = _outer_target(result, frame)

    assert target.target_event is None and target.target_kind.value != "EVENT_TARGET"
    assert target.provenance.get("reason") == "target_event_conflict"
    assert not [r for r in result.relations if r.source_event == full.event_for(frame.units[0].id).event_ref.event_id]


@pytest.mark.parametrize("outer", ["OBSERVE", "LEARN"])
def test_foreign_proposal_cannot_override_local_identity(outer):
    frame, base, _ = _case(outer, "ACTION")
    reference = _semantic(WRAPPER[outer](frame, base))
    local = frame.units[1].id
    reframed = tuple(replace(c, event_ref=replace(c.event_ref, source_frame="frame:ffffffffffff")) for c in base)

    assert any(c.predicate_ref == local for c in reframed)
    for cands in (FOREIGN, tuple(base) + FOREIGN, reframed, tuple(base) + reframed):
        assert _semantic(WRAPPER[outer](frame, cands)) == reference


@pytest.mark.parametrize("outer", ["OBSERVE", "LEARN"])
def test_legitimate_proposition_stays_proposition(outer):
    frame = parse_utterance(OUTER[outer].format(s="Marie", c="Paul a arrêté le test"))
    full = build_frame_event_index(frame)
    assert frame.units[1].predicate == "STOP" and full.event_for(frame.units[1].id) is None
    for cands in ((), extract_event_candidates(frame)):
        target = _outer_target(WRAPPER[outer](frame, cands), frame)
        assert (target.target_kind.value, target.target_event) == ("PROPOSITION_TARGET", None)


def test_wrapper_canonical_base_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "EMPTY_CALLER_CASES", "PARTIAL_CALLER_CASES", "CONFLICT_CASES", "FOREIGN_CASES",
        "EVENT_TARGET_RESOLVED", "LEGITIMATE_PROPOSITION",
        "CALLER_COMPLETENESS_SEMANTIC_DIFF", "FULL_FRAME_TARGET_RESOLUTION_FAILURE", "CANONICAL_SILENT_WIN",
        "CALLER_SILENT_WIN", "CONFLICT_FIRST_MATCH", "FOREIGN_OVERRIDE", "IDENTICAL_CALLER_DUPLICATE_DIFF",
        "CANDIDATE_ORDER_DIFF", "LEGITIMATE_PROPOSITION_PROMOTED", "EVENT_ID_DIFF", "OCCURRENCE_DIFF",
        "TARGET_INDEX_VIOLATION",
    ), 0)
    people = ("Marie", "Jean", "Nadia", "Omar")
    for outer, inner, s1, s2, x in product(OUTER, (*INNER, "STOP"), people, people, ("le test", "le build", "le job")):
        if s1 == s2:
            continue
        text = OUTER[outer].format(s=s1, c=INNER.get(inner, "Paul a arrêté {x}").format(s=s2, x=x))
        frame = parse_utterance(text)
        base = extract_event_candidates(frame)
        full = build_frame_event_index(frame)
        wrapper = WRAPPER[outer]
        reference = wrapper(frame, base)
        ref_target = _outer_target(reference, frame)
        target_id = frame.units[1].id
        canonical = full.event_for(target_id)
        metrics["CASES"] += 1
        if target_index_violation(ref_target, full):
            metrics["TARGET_INDEX_VIOLATION"] += 1
        if canonical is None:
            metrics["LEGITIMATE_PROPOSITION"] += ref_target.target_kind.value == "PROPOSITION_TARGET"
            metrics["LEGITIMATE_PROPOSITION_PROMOTED"] += ref_target.target_kind.value == "EVENT_TARGET"
        elif ref_target.target_event == canonical.event_ref.event_id:
            metrics["EVENT_TARGET_RESOLVED"] += 1
        else:
            metrics["FULL_FRAME_TARGET_RESOLUTION_FAILURE"] += 1
        meta = reference.observation_events if outer == "OBSERVE" else reference.knowledge_events
        for event in meta:
            indexed = full.event_for(event.predicate_ref)
            metrics["EVENT_ID_DIFF"] += indexed is None or indexed.event_ref.event_id != event.event_ref.event_id
            metrics["OCCURRENCE_DIFF"] += indexed is None or indexed.occurrence_status != event.occurrence_status
        expected = _semantic(reference)
        variants = {
            "EMPTY": ((), "CALLER_COMPLETENESS_SEMANTIC_DIFF"),
            "DUP": (tuple(base) * 2, "IDENTICAL_CALLER_DUPLICATE_DIFF"),
            "ORDER": (tuple(reversed(base)), "CANDIDATE_ORDER_DIFF"),
            "FOREIGN": (tuple(base) + FOREIGN, "FOREIGN_OVERRIDE"),
            "FOREIGN_ONLY": (FOREIGN, "FOREIGN_OVERRIDE"),
            "MIXED": (tuple(reversed(full.events())) + FOREIGN + tuple(base[:1]), "CALLER_COMPLETENESS_SEMANTIC_DIFF"),
        }
        for name, cands in _partials(base, target_id).items():
            variants["PARTIAL_" + name] = (cands, "CALLER_COMPLETENESS_SEMANTIC_DIFF")
        for name, (cands, metric) in variants.items():
            metrics["CASES"] += 1
            metrics["EMPTY_CALLER_CASES"] += name == "EMPTY"
            metrics["PARTIAL_CALLER_CASES"] += name.startswith("PARTIAL_")
            metrics["FOREIGN_CASES"] += name.startswith("FOREIGN")
            if _semantic(wrapper(frame, cands)) != expected:
                metrics[metric] += 1
        if canonical is None:
            continue
        source_id = full.event_for(frame.units[0].id).event_ref.event_id
        for forged in (replace(canonical, occurrence_status=OccurrenceStatus.NEGATED),
                       replace(canonical, event_ref=replace(canonical.event_ref, event_id="event:forged0000000000"))):
            for prefix in ((), tuple(base)):
                metrics["CASES"] += 1
                metrics["CONFLICT_CASES"] += 1
                result = wrapper(frame, prefix + (forged,))
                target = _outer_target(result, frame)
                if target.target_event == canonical.event_ref.event_id:
                    metrics["CANONICAL_SILENT_WIN"] += 1
                elif target.target_event is not None:
                    metrics["CALLER_SILENT_WIN"] += 1
                if any(r.source_event == source_id for r in result.relations):
                    metrics["CONFLICT_FIRST_MATCH"] += 1

    assert metrics["CASES"] >= 4000, metrics
    for key in ("EMPTY_CALLER_CASES", "PARTIAL_CALLER_CASES", "CONFLICT_CASES", "FOREIGN_CASES",
                "EVENT_TARGET_RESOLVED", "LEGITIMATE_PROPOSITION"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("CALLER_COMPLETENESS_SEMANTIC_DIFF", "FULL_FRAME_TARGET_RESOLUTION_FAILURE", "CANONICAL_SILENT_WIN",
                "CALLER_SILENT_WIN", "CONFLICT_FIRST_MATCH", "FOREIGN_OVERRIDE", "IDENTICAL_CALLER_DUPLICATE_DIFF",
                "CANDIDATE_ORDER_DIFF", "LEGITIMATE_PROPOSITION_PROMOTED", "EVENT_ID_DIFF", "OCCURRENCE_DIFF",
                "TARGET_INDEX_VIOLATION"):
        assert metrics[key] == 0, (key, metrics)
