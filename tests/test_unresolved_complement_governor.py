"""B2a: an unrecognized verb governing "que + clause" must not assert the clause.

The parser keeps the unknown governor as an unresolved unit and the complement
under it; no REPORT / BELIEF / denial meaning is inferred.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.lexicon import lookup
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

GOVERNOR = "UNKNOWN_COMPLEMENT_GOVERNOR"
GOVERNOR_CLASS = "unresolved_complement_governor"

A = OccurrenceStatus.ASSERTED_OCCURRED
R = OccurrenceStatus.REPORTED
U = OccurrenceStatus.UNKNOWN


def _events(frame):
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    events = tuple(base) + tuple(observation.observation_events) + tuple(knowledge.knowledge_events)
    return {event.predicate_ref: event for event in events}


def _runs(frame):
    return [unit for unit in frame.units if unit.predicate == "EXECUTE"]


def _run_statuses(text: str):
    frame = parse_utterance(text)
    events = _events(frame)
    return [events[unit.id].occurrence_status for unit in _runs(frame)]


def _governors(frame):
    return [unit for unit in frame.units if unit.predicate == GOVERNOR]


CANONICAL = (
    "Paul rapporte que Marie a lancé le test.",
    "Paul signale que Marie a lancé le test.",
    "Paul soutient que Marie a lancé le test.",
    "Paul prétend que Marie a lancé le test.",
    "Paul estime que Marie a lancé le test.",
    "Paul nie que Marie a lancé le test.",
)


@pytest.mark.parametrize("text", CANONICAL + (
    "Paul a rapporté que Marie a lancé le test.",
    "Paul a nié que Marie a lancé le test.",
    "Le chef nie que Marie a lancé le test.",
    "Il assure que Marie a lancé le test.",
))
def test_unknown_governor_complement_fails_closed(text):
    frame = parse_utterance(text)
    governors = _governors(frame)
    runs = _runs(frame)
    events = _events(frame)

    assert len(governors) == 1 and len(runs) == 1
    governor, run = governors[0], runs[0]
    assert governor.predicate_class == GOVERNOR_CLASS
    assert run.embedded_under == governor.id
    assert ("EMBEDS", governor.id, run.id) in {(r.kind, r.source, r.target) for r in frame.relations}
    assert events[run.id].occurrence_status is U
    # No meaning is inferred for the unknown verb.
    assert governor.id not in events
    assert not {r.kind for r in frame.relations} & {"REPORTS", "BELIEVES"}
    assert all(e.event_ref.event_kind not in {EventKind.REPORT, EventKind.BELIEF} for e in events.values())
    assert f"complement_under_unresolved_governor:{run.id}" in frame.ambiguities


def test_nier_que_does_not_invent_negation_either():
    frame = parse_utterance("Paul nie que Marie a lancé le test.")
    run = _runs(frame)[0]

    assert run.polarity == "positive"
    assert _events(frame)[run.id].occurrence_status is U


def test_negated_unknown_governor_keeps_its_own_polarity():
    frame = parse_utterance("Paul ne nie pas que Marie a lancé le test.")
    governor = _governors(frame)[0]

    assert governor.polarity == "negative"
    assert _events(frame)[_runs(frame)[0].id].occurrence_status is U


@pytest.mark.parametrize("text, expected", [
    ("Paul rapporte que Marie ne lancera pas le test.", OccurrenceStatus.NEGATED),
    ("Paul rapporte que Marie n'a pas lancé le test.", OccurrenceStatus.NEGATED),
    ("Paul soutient que Marie lancera le test.", OccurrenceStatus.FUTURE),
    ("Paul estime que Marie pourrait lancer le test.", OccurrenceStatus.UNCERTAIN),
])
def test_strong_local_signals_survive_unknown_governor(text, expected):
    assert _run_statuses(text) == [expected]


def test_nested_content_below_unknown_governor_is_not_asserted():
    frame = parse_utterance("Paul soutient que Marie a appris que Jean a lancé le test.")
    events = _events(frame)
    learn = next(unit for unit in frame.units if unit.predicate == "LEARN")

    assert events[learn.id].occurrence_status is U
    assert events[_runs(frame)[0].id].occurrence_status is U


def test_unknown_governor_under_known_embeddings():
    frame = parse_utterance("Paul dit que Marie nie que Jean a lancé le test.")
    governor = _governors(frame)[0]
    say = next(unit for unit in frame.units if unit.predicate == "SAY")

    assert governor.embedded_under == say.id
    assert governor.pragmatic == "REPORTED"
    assert _run_statuses("Paul dit que Marie nie que Jean a lancé le test.") == [U]
    assert _run_statuses("Paul croit que Marie nie que Jean a lancé le test.") == [U]


def test_coordination_under_unknown_governor_does_not_leak():
    frame = parse_utterance("Paul rapporte que Marie a lancé A et que Jean a lancé B.")
    events = _events(frame)

    assert len(_runs(frame)) == 2
    assert all(events[run.id].occurrence_status is not A for run in _runs(frame))


def test_known_governors_and_root_clauses_are_unchanged():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    assert not _governors(frame)
    assert {r.kind for r in frame.relations} == {"REPORTS"}
    assert _run_statuses("Paul dit que Marie a lancé le test.") == [R]

    frame = parse_utterance("Paul croit que Marie a lancé le test.")
    assert not _governors(frame)
    assert {r.kind for r in frame.relations} == {"BELIEVES"}
    assert _run_statuses("Paul croit que Marie a lancé le test.") == [U]

    assert _run_statuses("J'ai appris que Marie a lancé le test.") == [A]
    assert _run_statuses("J'ai vu Marie lancer le test.") == [U]
    assert _run_statuses("Marie a lancé le test.") == [A]


@pytest.mark.parametrize("text", [
    "Marie a lancé le test que Paul a préparé.",
    "Le test que Paul a lancé a échoué.",
    "C'est lui que Paul a vu.",
    "C'est Paul que Marie a vu.",
    "Paul ne lance que les tests.",
    "Paul ne mange que des pommes.",
    "Marie lance plus de tests que Paul.",
])
def test_relatives_restrictions_clefts_and_comparatives_get_no_governor(text):
    assert not _governors(parse_utterance(text))


def test_unknown_governor_never_fabricates_a_request():
    for text in ("Paul soutient que tu as lancé le test.", "Paul nie que tu lances le test.",
                 "Paul rapporte que Marie supprime le fichier."):
        summary = governable_summary(parse_utterance(text))
        assert summary["requested_world_actions"] == []


def test_no_raw_phrase_hack_in_parser():
    source = Path("app/semantic/lattice/french_grammar.py").read_text(encoding="utf-8")
    for surface in ("nie", "nié", "rapporte", "rapporté", "signale", "affirme", "prétend", "suppose"):
        assert f'"{surface}"' not in source and f"'{surface}'" not in source


# Adversarial matrix.

# Verbs still unknown after B2b (affirmer/déclarer/mentionner/supposer are now lexical).
_UNKNOWN_PRESENT = ("rapporte", "signale", "soutient", "prétend", "estime", "nie", "assure", "annonce", "soupçonne")
_UNKNOWN_PARTICIPLE = ("rapporté", "signalé", "soutenu", "prétendu", "estimé", "nié", "assuré", "annoncé", "soupçonné")
_SUBJECTS = ("Paul", "Anne", "Il", "Elle", "Le chef")

_GOVERNED = (
    ("plain", "{s} {v} que {o} a lancé le test {i}.", (U,)),
    ("negative", "{s} {v} que {o} n'a pas lancé le test {i}.", (OccurrenceStatus.NEGATED,)),
    ("future", "{s} {v} que {o} lancera le test {i}.", (OccurrenceStatus.FUTURE,)),
    ("modal", "{s} {v} que {o} pourrait lancer le test {i}.", (OccurrenceStatus.UNCERTAIN,)),
    ("nested", "{s} {v} que {o} a appris que Jean a lancé le test {i}.", (U,)),
    ("under_belief", "Paul croit que {o} {v} que Jean a lancé le test {i}.", (U,)),
    ("under_report", "Paul dit que {o} {v} que Jean a lancé le test {i}.", (U,)),
    ("coordination", "{s} {v} que {o} a lancé le build {i} et que Jean a lancé le test {i}.", None),
    ("participle", "{s} a {p} que {o} a lancé le test {i}.", (U,)),
)
_CONTROLS = (
    ("known_report", "{s} dit que {o} a lancé le test {i}.", (R,)),
    ("known_belief", "{s} croit que {o} a lancé le test {i}.", (U,)),
    ("root", "{o} a lancé le test {i}.", (A,)),
    ("relative", "{o} a lancé le test {i} que Paul a préparé.", (A,)),
)
_LOST = {
    OccurrenceStatus.NEGATED: "NEGATION_LOST",
    OccurrenceStatus.FUTURE: "FUTURE_LOST",
    OccurrenceStatus.UNCERTAIN: "UNCERTAINTY_LOST",
}
_CONTROL_METRIC = {
    "known_report": "KNOWN_REPORT_REGRESSIONS",
    "known_belief": "KNOWN_BELIEF_REGRESSIONS",
    "root": "ROOT_ASSERTION_REGRESSIONS",
    "relative": "ROOT_ASSERTION_REGRESSIONS",
}


def test_unresolved_governor_adversarial_matrix():
    for verb in _UNKNOWN_PRESENT + _UNKNOWN_PARTICIPLE:
        assert not lookup(verb)[0], verb

    metrics = dict.fromkeys((
        "CASES", "UNKNOWN_GOVERNOR_COMPLEMENTS", "ASSERTED_UNDER_UNKNOWN_GOVERNOR",
        "KNOWN_REPORT_REGRESSIONS", "KNOWN_BELIEF_REGRESSIONS", "ROOT_ASSERTION_REGRESSIONS",
        "NEGATION_LOST", "FUTURE_LOST", "UNCERTAINTY_LOST", "UNEXPECTED_STATUS",
        "REPORT_OR_BELIEF_INFERRED", "REQUEST_FABRICATED",
    ), 0)

    def check(text, kind, expected, governed):
        frame = parse_utterance(text)
        events = _events(frame)
        units_by_id = {unit.id: unit for unit in frame.units}
        metrics["CASES"] += 1
        statuses = tuple(events[run.id].occurrence_status for run in _runs(frame))
        if governed:
            for run in _runs(frame):
                parent_id, seen = run.embedded_under, set()
                while parent_id is not None and parent_id not in seen:
                    seen.add(parent_id)
                    if units_by_id[parent_id].predicate == GOVERNOR:
                        metrics["UNKNOWN_GOVERNOR_COMPLEMENTS"] += 1
                        break
                    parent_id = units_by_id[parent_id].embedded_under
            metrics["ASSERTED_UNDER_UNKNOWN_GOVERNOR"] += statuses.count(A)
            governor_ids = {g.id for g in _governors(frame)}
            if any(r.source in governor_ids and r.kind in {"REPORTS", "BELIEVES"} for r in frame.relations):
                metrics["REPORT_OR_BELIEF_INFERRED"] += 1
            if governable_summary(frame)["requested_world_actions"]:
                metrics["REQUEST_FABRICATED"] += 1
        elif _governors(frame):
            metrics[_CONTROL_METRIC[kind]] += 1
        if expected is not None and statuses != expected:
            metric = _CONTROL_METRIC.get(kind) or _LOST.get(expected[0], "UNEXPECTED_STATUS")
            metrics[metric] += 1

    for i in range(5):
        for subject in _SUBJECTS:
            for obj in ("Marie", "Claire"):
                for verb, participle in zip(_UNKNOWN_PRESENT, _UNKNOWN_PARTICIPLE):
                    for kind, template, expected in _GOVERNED:
                        check(template.format(s=subject, v=verb, p=participle, o=obj, i=i), kind, expected, True)
                for kind, template, expected in _CONTROLS:
                    check(template.format(s=subject, o=obj, i=i), kind, expected, False)

    assert metrics["CASES"] >= 2000
    assert metrics["UNKNOWN_GOVERNOR_COMPLEMENTS"] > 0
    for key, value in metrics.items():
        if key not in {"CASES", "UNKNOWN_GOVERNOR_COMPLEMENTS"}:
            assert value == 0, (key, metrics)
