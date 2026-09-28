"""Occurrence must be consistent across base, observation and knowledge events.

The nearest REPORT/BELIEF ancestor bounds an occurrence that would otherwise be
presented as asserted; stronger local signals are preserved.
"""
from __future__ import annotations

from dataclasses import replace

from app.semantic.lattice.event_extraction import (
    OccurrenceStatus,
    extract_event_candidates,
    resolve_epistemic_ancestor_occurrence,
)
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

A = OccurrenceStatus.ASSERTED_OCCURRED
R = OccurrenceStatus.REPORTED
U = OccurrenceStatus.UNKNOWN
N = OccurrenceStatus.NEGATED
F = OccurrenceStatus.FUTURE
C = OccurrenceStatus.UNCERTAIN

_REPORT = {"SAY"}
_BELIEF = {"BELIEVE"}


def _extract(text: str):
    frame = parse_utterance(text)
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    events = tuple(base) + tuple(observation.observation_events) + tuple(knowledge.knowledge_events)
    return frame, events, observation, knowledge


def _statuses(text: str) -> list[tuple[str, OccurrenceStatus]]:
    frame, events, _, _ = _extract(text)
    by_predicate = {event.predicate_ref: event for event in events}
    assert len(by_predicate) == len(events), "one EventRef per predicate"
    return [
        (unit.predicate, by_predicate[unit.id].occurrence_status)
        for unit in sorted(frame.units, key=lambda unit: unit.span[0])
        if unit.id in by_predicate
    ]


# A. O1: observation under belief.

def test_observation_under_belief_is_not_asserted():
    assert _statuses("Paul croit que Marie a vu Jean lancer le test.") == [
        ("BELIEVE", A), ("OBSERVE", U), ("EXECUTE", U),
    ]


# B. O2 + O3: learn under report, and content below it.

def test_learn_under_report_and_its_content_are_reported():
    assert _statuses("Paul dit que Marie a appris que Jean a lancé le test.") == [
        ("SAY", A), ("LEARN", R), ("EXECUTE", R),
    ]


# C. B1 compatibility: the nearest epistemic ancestor governs.

def test_nearest_epistemic_ancestor_governs_belief_around_report():
    assert _statuses("Paul croit que Marie a dit que Jean a lancé le test.") == [
        ("BELIEVE", A), ("SAY", U), ("EXECUTE", R),
    ]


def test_report_around_belief():
    assert _statuses("Paul dit que Marie croit que Jean a lancé le test.") == [
        ("SAY", A), ("BELIEVE", R), ("EXECUTE", U),
    ]


# D. Nested belief / nested report.

def test_nested_belief():
    assert _statuses("Paul croit que Marie pense que Jean a lancé le test.") == [
        ("BELIEVE", A), ("BELIEVE", U), ("EXECUTE", U),
    ]


def test_nested_report():
    assert _statuses("Paul dit que Marie dit que Jean a lancé le test.") == [
        ("SAY", A), ("SAY", R), ("EXECUTE", R),
    ]


# E. REPORT -> OBSERVE. The perception infinitive is locally UNKNOWN; the
# ancestry rule only bounds asserted occurrence, it never promotes UNKNOWN.

def test_report_around_observation():
    assert _statuses("Paul dit que Marie a vu Jean lancer le test.") == [
        ("SAY", A), ("OBSERVE", R), ("EXECUTE", U),
    ]


# F. BELIEF -> LEARN.

def test_belief_around_learn():
    assert _statuses("Paul croit que Marie a appris que Jean a lancé le test.") == [
        ("BELIEVE", A), ("LEARN", U), ("EXECUTE", U),
    ]


# G. O4: coordinated complements are siblings under SAY and do not leak.

def test_reported_coordination_does_not_leak_asserted_occurrence():
    frame, events, _, _ = _extract("Paul dit que Marie a lancé A et que Jean a lancé B.")
    runs = [unit for unit in frame.units if unit.predicate == "EXECUTE"]
    by_predicate = {event.predicate_ref: event for event in events}

    assert len(runs) == 2
    # "que P et que Q": sibling complements of the unique governor (doctrine Q2).
    assert runs[1].embedded_under == runs[0].embedded_under == frame.units[0].id
    assert [by_predicate[run.id].occurrence_status for run in runs] == [R, R]


# Unembedded meta-events and plain assertions are unchanged.

def test_unembedded_meta_events_and_plain_assertions_unchanged():
    assert _statuses("Marie a lancé le test.") == [("EXECUTE", A)]
    assert _statuses("Je vois Marie lancer le test.") == [("OBSERVE", A), ("EXECUTE", U)]
    assert _statuses("J'apprends que Marie a lancé le test.") == [("LEARN", A), ("EXECUTE", A)]


# Strong local signals win.

def test_strong_local_signals_are_preserved_under_ancestry():
    assert _statuses("Paul croit que Marie n'a pas lancé le test.")[-1] == ("EXECUTE", N)
    assert _statuses("Paul dit que Marie ne lancera pas le test.")[-1] == ("EXECUTE", N)
    assert _statuses("Paul dit que Marie lancera le test.")[-1] == ("EXECUTE", F)
    assert _statuses("Paul croit que Marie pourrait lancer le test.")[-1] == ("EXECUTE", C)

    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    units_by_id = {unit.id: unit for unit in frame.units}
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    for status in OccurrenceStatus:
        if status is not A:
            assert resolve_epistemic_ancestor_occurrence(run, units_by_id, status) is status


# Malformed ancestry fails closed.

def test_malformed_ancestry_fails_closed():
    frame = parse_utterance("Paul a lancé le test.")
    run = frame.units[0]
    missing_parent = replace(run, embedded_under="u_missing")
    self_cycle = replace(run, embedded_under=run.id)

    assert resolve_epistemic_ancestor_occurrence(missing_parent, {run.id: missing_parent}, A) is U
    assert resolve_epistemic_ancestor_occurrence(self_cycle, {run.id: self_cycle}, A) is U
    assert resolve_epistemic_ancestor_occurrence(run, {run.id: run}, A) is A


# Adversarial matrix.

_TEMPLATES = (
    ("plain", "{o} a lancé le test {i}.", (A,)),
    ("plain_report", "{s} dit que {o} a lancé le test {i}.", (A, R)),
    ("plain_belief", "{s} croit que {o} a lancé le test {i}.", (A, U)),
    ("report_action_negated", "{s} dit que {o} n'a pas lancé le test {i}.", (A, N)),
    ("belief_action_negated", "{s} croit que {o} n'a pas lancé le test {i}.", (A, N)),
    ("report_future", "{s} dit que {o} lancera le test {i}.", (A, F)),
    ("belief_future", "{s} croit que {o} lancera le test {i}.", (A, F)),
    ("belief_modal", "{s} croit que {o} pourrait lancer le test {i}.", (A, C)),
    ("report_learn", "{s} dit que {o} a appris que Jean a lancé le test {i}.", (A, R, R)),
    ("belief_learn", "{s} croit que {o} a appris que Jean a lancé le test {i}.", (A, U, U)),
    ("report_observe", "{s} dit que {o} a vu Jean lancer le test {i}.", (A, R, U)),
    ("belief_observe", "{s} croit que {o} a vu Jean lancer le test {i}.", (A, U, U)),
    ("belief_report", "{s} croit que {o} a dit que Jean a lancé le test {i}.", (A, U, R)),
    ("report_belief", "{s} dit que {o} croit que Jean a lancé le test {i}.", (A, R, U)),
    ("nested_belief", "{s} croit que {o} pense que Jean a lancé le test {i}.", (A, U, U)),
    ("nested_report", "{s} dit que {o} dit que Jean a lancé le test {i}.", (A, R, R)),
    ("report_coordination", "{s} dit que {o} a lancé le build {i} et que Jean a lancé le test {i}.", (A, R, R)),
    ("belief_coordination", "{s} croit que {o} a lancé le build {i} et que Jean a lancé le test {i}.", (A, U, U)),
)

_LOST_METRIC = {N: "NEGATION_LOST", F: "FUTURE_LOST", C: "UNCERTAINTY_LOST", R: "REPORTED_LOST"}


def _nearest_epistemic_ancestor(unit, units_by_id) -> str | None:
    seen = {unit.id}
    parent_id = unit.embedded_under
    while parent_id is not None and parent_id not in seen and parent_id in units_by_id:
        parent = units_by_id[parent_id]
        if parent.predicate in _REPORT:
            return "REPORT"
        if parent.predicate in _BELIEF:
            return "BELIEF"
        seen.add(parent_id)
        parent_id = parent.embedded_under
    return None


def _structure(frame):
    return (
        tuple((relation.kind, relation.source, relation.target) for relation in frame.relations),
        tuple((unit.id, unit.embedded_under) for unit in frame.units),
    )


def test_occurrence_ancestry_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "ASSERTED_UNDER_REPORT", "ASSERTED_UNDER_BELIEF", "OBSERVATION_ASSERTED_UNDER_BELIEF",
        "LEARN_ASSERTED_UNDER_REPORT", "NESTED_REPORT_LEAK", "NESTED_BELIEF_LEAK", "NEGATION_LOST",
        "FUTURE_LOST", "UNCERTAINTY_LOST", "REPORTED_LOST", "B1_REGRESSION", "RELATION_STRUCTURE_CHANGED",
        "UNEXPECTED_STATUS",
    ), 0)

    for i in range(10):
        for subject in ("Paul", "Luc", "Anne", "Je"):
            for obj in ("Marie", "Claire", "Sophie"):
                for kind, template, expected in _TEMPLATES:
                    text = template.format(s=subject, o=obj, i=i)
                    if subject == "Je":
                        text = text.replace("Je croit", "Je crois").replace("Je dit", "Je dis")
                    frame = parse_utterance(text)
                    before = _structure(frame)
                    base = extract_event_candidates(frame)
                    observation = extract_observation_event_targets(frame, base)
                    knowledge = extract_knowledge_event_targets(frame, base)
                    events = tuple(base) + tuple(observation.observation_events) + tuple(knowledge.knowledge_events)
                    metrics["CASES"] += 1

                    units_by_id = {unit.id: unit for unit in frame.units}
                    by_predicate = {event.predicate_ref: event for event in events}
                    if _structure(frame) != before or len(by_predicate) != len(events):
                        metrics["RELATION_STRUCTURE_CHANGED"] += 1
                    for relation in tuple(observation.relations) + tuple(knowledge.relations):
                        source = next(e for e in events if e.event_ref.event_id == relation.source_event)
                        target = next(e for e in events if e.event_ref.event_id == relation.target_event)
                        if units_by_id[target.predicate_ref].embedded_under != source.predicate_ref:
                            metrics["RELATION_STRUCTURE_CHANGED"] += 1

                    for event in events:
                        unit = units_by_id[event.predicate_ref]
                        if event.occurrence_status is not A:
                            continue
                        ancestor = _nearest_epistemic_ancestor(unit, units_by_id)
                        if ancestor == "REPORT":
                            metrics["ASSERTED_UNDER_REPORT"] += 1
                            if unit.predicate == "LEARN":
                                metrics["LEARN_ASSERTED_UNDER_REPORT"] += 1
                            if kind == "nested_report":
                                metrics["NESTED_REPORT_LEAK"] += 1
                        elif ancestor == "BELIEF":
                            metrics["ASSERTED_UNDER_BELIEF"] += 1
                            if unit.predicate == "OBSERVE":
                                metrics["OBSERVATION_ASSERTED_UNDER_BELIEF"] += 1
                            if kind == "nested_belief":
                                metrics["NESTED_BELIEF_LEAK"] += 1

                    actual = tuple(
                        by_predicate[unit.id].occurrence_status
                        for unit in sorted(frame.units, key=lambda unit: unit.span[0])
                        if unit.id in by_predicate
                    )
                    if actual != expected:
                        if len(actual) != len(expected):
                            metrics["UNEXPECTED_STATUS"] += 1
                        for got, want in zip(actual, expected):
                            if got is not want:
                                if kind in {"plain_belief", "belief_report", "nested_belief"}:
                                    metrics["B1_REGRESSION"] += 1
                                metrics[_LOST_METRIC.get(want, "UNEXPECTED_STATUS")] += 1

    assert metrics["CASES"] >= 2000
    for key, value in metrics.items():
        if key != "CASES":
            assert value == 0, (key, metrics)
