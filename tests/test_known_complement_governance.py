"""B2c: a known verb without an embedding contract must not assert its "que" clause.

The governing predicate keeps its lexical meaning (CONFIRM stays CONFIRM); only
the complement relation is marked as unresolved governance, and the canonical
occurrence rule treats it as a fail-closed boundary.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.language_flow_projection import project_ordered_flows
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

UNRESOLVED_GOVERNANCE = "UNRESOLVED_GOVERNANCE"
GOVERNOR = "UNKNOWN_COMPLEMENT_GOVERNOR"
A = OccurrenceStatus.ASSERTED_OCCURRED
R = OccurrenceStatus.REPORTED
U = OccurrenceStatus.UNKNOWN
N = OccurrenceStatus.NEGATED
F = OccurrenceStatus.FUTURE
C = OccurrenceStatus.UNCERTAIN


def _analyse(text: str):
    frame = parse_utterance(text)
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    events = tuple(base) + tuple(observation.observation_events) + tuple(knowledge.knowledge_events)
    return frame, {event.predicate_ref: event for event in events}


def _run_statuses(text: str):
    frame, events = _analyse(text)
    return [events[unit.id].occurrence_status for unit in frame.units if unit.predicate == "EXECUTE"]


@pytest.mark.parametrize("text, predicate", [
    ("Paul confirme que Marie a lancé le test.", "CONFIRM"),
    ("Paul explique que Marie a lancé le test.", "EXPLAIN"),
    ("Paul vérifie que Marie a lancé le test.", "VERIFY"),
    ("Paul sait que Marie a lancé le test.", "KNOW"),
    ("Paul a confirmé que Marie a lancé le test.", "CONFIRM"),
    ("Paul explique à Marie que Jean a lancé le test.", "EXPLAIN"),
    ("Paul ne confirme pas que Marie a lancé le test.", "CONFIRM"),
    ("Vérifie que Marie a lancé le test.", "VERIFY"),
])
def test_known_non_embedding_governor_fails_closed(text, predicate):
    frame, events = _analyse(text)
    governor = next(unit for unit in frame.units if unit.predicate == predicate)
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")

    # The known predicate keeps its lexical identity.
    assert not [unit for unit in frame.units if unit.predicate == GOVERNOR]
    assert run.embedded_under == governor.id
    assert run.epistemic == UNRESOLVED_GOVERNANCE
    assert f"unresolved_complement_governance:{run.id}" in frame.ambiguities
    relation = next(r for r in frame.relations if r.source == governor.id and r.target == run.id)
    assert relation.kind == "EMBEDS" and relation.evidence == "que_unresolved_governance"
    assert events[run.id].occurrence_status is U
    # No report / belief / verification meaning is inferred.
    assert not {r.kind for r in frame.relations} & {"REPORTS", "BELIEVES"}
    assert not {flow.state for flow in project_ordered_flows(frame)} & {"VERIFIED", "SUPPORTED", "OBSERVED"}


def test_negated_known_governor_keeps_polarity_and_does_not_detach_complement():
    frame, _ = _analyse("Paul ne confirme pas que Marie a lancé le test.")
    confirm = next(unit for unit in frame.units if unit.predicate == "CONFIRM")

    assert confirm.polarity == "negative"
    assert confirm.restriction is None


@pytest.mark.parametrize("text, expected", [
    ("Paul confirme que Marie n'a pas lancé le test.", N),
    ("Paul explique que Marie lancera le test.", F),
    ("Paul vérifie que Marie pourrait lancer le test.", C),
    ("Paul confirme que Marie a dit que Jean a lancé le test.", R),
    ("Paul confirme que Marie croit que Jean a lancé le test.", U),
])
def test_stronger_or_nearer_signals_survive(text, expected):
    assert _run_statuses(text) == [expected]


def test_nested_content_under_known_non_embedding_governor_is_not_asserted():
    frame, events = _analyse("Paul confirme que Marie a appris que Jean a lancé le test.")
    learn = next(unit for unit in frame.units if unit.predicate == "LEARN")

    assert events[learn.id].occurrence_status is U
    assert _run_statuses("Paul confirme que Marie a appris que Jean a lancé le test.") == [U]


def test_coordination_under_known_non_embedding_governor_does_not_leak():
    assert A not in _run_statuses("Paul confirme que Marie a lancé A et que Jean a lancé B.")


@pytest.mark.parametrize("text", [
    "Paul confirme le rendez-vous.",
    "Paul explique le problème.",
    "Paul vérifie le test.",
    "Paul sait nager.",
])
def test_root_uses_without_complement_are_unchanged(text):
    frame = parse_utterance(text)

    assert all(unit.epistemic != UNRESOLVED_GOVERNANCE for unit in frame.units)
    assert not any(a.startswith("unresolved_complement_governance") for a in frame.ambiguities)


@pytest.mark.parametrize("text", [
    "Paul ne lance que les tests.",
    "Il ne lance pas que les tests.",
    "Marie lance plus de tests que Paul.",
    "Paul fait ce que Marie dit.",
    "Marie a lancé le test que Paul a préparé.",
])
def test_restrictions_comparatives_and_relatives_are_unchanged(text):
    frame = parse_utterance(text)

    assert all(unit.epistemic != UNRESOLVED_GOVERNANCE for unit in frame.units)


def test_known_embeddings_and_b2a_are_unchanged():
    assert _run_statuses("Paul affirme que Marie a lancé le test.") == [R]
    assert _run_statuses("Paul dit que Marie a lancé le test.") == [R]
    assert _run_statuses("Paul suppose que Marie a lancé le test.") == [U]
    assert _run_statuses("J'ai appris que Marie a lancé le test.") == [A]
    frame = parse_utterance("Paul nie que Marie a lancé le test.")
    assert [unit.predicate for unit in frame.units][0] == GOVERNOR


def test_known_non_embedding_governor_never_fabricates_request():
    for text in ("Paul confirme que tu as lancé le test.", "Vérifie que tu as lancé le test.",
                 "Paul explique que Marie supprime le fichier."):
        frame = parse_utterance(text)
        requested = governable_summary(frame)["requested_world_actions"]
        assert "EXECUTE" not in requested and "DELETE" not in requested


# Adversarial matrix.

_KNOWN_NON_EMBEDDING = ("confirme", "explique", "vérifie", "sait", "a confirmé", "a expliqué",
                        "ne confirme pas", "n'explique pas", "explique à Luc")
_KNOWN_EMBEDDING = (("dit", R), ("affirme", R), ("déclare", R), ("croit", U), ("suppose", U),
                    ("pense", U))
_UNKNOWN = ("nie", "prétend", "assure", "soutient", "estime")
_SUBJECTS = ("Paul", "Anne", "Il", "Elle", "Le chef")
_COMPLEMENTS = (
    ("a lancé le test {i}", None),
    ("n'a pas lancé le test {i}", N),
    ("lancera le test {i}", F),
    ("pourrait lancer le test {i}", C),
    ("a appris que Jean a lancé le test {i}", None),
    ("a dit que Jean a lancé le test {i}", R),
    ("croit que Jean a lancé le test {i}", U),
    ("a lancé le build {i} et que Jean a lancé le test {i}", None),
)
_ROOT = ("{s} confirme le rendez-vous {i}.", "{s} explique le problème {i}.", "{s} vérifie le test {i}.",
         "{o} a lancé le test {i}.")


def test_known_complement_governance_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "ASSERTED_UNDER_KNOWN_NONEMBEDDING", "KNOWN_EMBEDDING_REGRESSION",
        "UNKNOWN_GOVERNOR_REGRESSION", "ROOT_USE_REGRESSION", "FALSE_REPORTS", "FALSE_BELIEFS",
        "VERIFIED_CREATED", "REQUEST_FABRICATED", "STRONG_STATUS_LOST", "MARKED_COMPLEMENTS",
    ), 0)

    def analyse(text):
        frame, events = _analyse(text)
        metrics["CASES"] += 1
        runs = [unit for unit in frame.units if unit.predicate == "EXECUTE"]
        if {"VERIFIED", "SUPPORTED"} & {flow.state for flow in project_ordered_flows(frame)}:
            metrics["VERIFIED_CREATED"] += 1
        if governable_summary(frame)["requested_world_actions"]:
            metrics["REQUEST_FABRICATED"] += 1
        return frame, [events[unit.id].occurrence_status for unit in runs]

    for i in range(5):
        for s in _SUBJECTS:
            for complement, strong in _COMPLEMENTS:
                c = complement.format(i=i)
                for verb in _KNOWN_NON_EMBEDDING:
                    frame, statuses = analyse(f"{s} {verb} que Marie {c}.")
                    metrics["ASSERTED_UNDER_KNOWN_NONEMBEDDING"] += statuses.count(A)
                    metrics["MARKED_COMPLEMENTS"] += sum(
                        unit.epistemic == UNRESOLVED_GOVERNANCE for unit in frame.units)
                    governor_ids = {u.id for u in frame.units if u.predicate not in {"EXECUTE", "SAY", "BELIEVE", "LEARN"}}
                    if any(r.source in governor_ids and r.kind == "REPORTS" for r in frame.relations):
                        metrics["FALSE_REPORTS"] += 1
                    if any(r.source in governor_ids and r.kind == "BELIEVES" for r in frame.relations):
                        metrics["FALSE_BELIEFS"] += 1
                    if strong is not None and statuses[-1:] != [strong]:
                        metrics["STRONG_STATUS_LOST"] += 1
                for verb, content in _KNOWN_EMBEDDING:
                    frame, statuses = analyse(f"{s} {verb} que Marie {c}.")
                    if any(unit.epistemic == UNRESOLVED_GOVERNANCE for unit in frame.units):
                        metrics["KNOWN_EMBEDDING_REGRESSION"] += 1
                    if complement == "a lancé le test {i}" and statuses != [content]:
                        metrics["KNOWN_EMBEDDING_REGRESSION"] += 1
                    metrics["ASSERTED_UNDER_KNOWN_NONEMBEDDING"] += 0
                for verb in _UNKNOWN:
                    frame, statuses = analyse(f"{s} {verb} que Marie {c}.")
                    if not any(unit.predicate == GOVERNOR for unit in frame.units) or A in statuses:
                        metrics["UNKNOWN_GOVERNOR_REGRESSION"] += 1
            for template in _ROOT:
                frame, statuses = analyse(template.format(s=s, o="Marie", i=i))
                if any(unit.epistemic == UNRESOLVED_GOVERNANCE for unit in frame.units):
                    metrics["ROOT_USE_REGRESSION"] += 1
                if template.startswith("{o}") and statuses != [A]:
                    metrics["ROOT_USE_REGRESSION"] += 1

    assert metrics["CASES"] >= 2500
    assert metrics["MARKED_COMPLEMENTS"] > 0
    for key, value in metrics.items():
        if key not in {"CASES", "MARKED_COMPLEMENTS"}:
            assert value == 0, (key, metrics)
