"""A meta-event (SAY / BELIEVE / OBSERVE / LEARN) is only asserted as occurring
when its own tense presents it as occurring: conditional, near-future and
averted meta-events are not ASSERTED_OCCURRED. Content occurrence is unaffected.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

A = OccurrenceStatus.ASSERTED_OCCURRED
R = OccurrenceStatus.REPORTED
U = OccurrenceStatus.UNKNOWN
META = {"SAY", "BELIEVE", "OBSERVE", "LEARN"}


def _statuses(text: str):
    frame = parse_utterance(text)
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    events = {e.predicate_ref: e for e in tuple(base) + tuple(observation.observation_events)
              + tuple(knowledge.knowledge_events)}
    return [(u.predicate, u.tense_aspect, events[u.id].occurrence_status) for u in frame.units if u.id in events]


@pytest.mark.parametrize("text, content", [
    ("Paul croirait que Marie a lancé le test.", U),
    ("Paul dirait que Marie a lancé le test.", R),
    ("Paul affirmerait que Marie a lancé le test.", R),
    ("Paul supposerait que Marie a lancé le test.", U),
    ("Paul aurait dit que Marie a lancé le test.", R),
    ("Paul va dire que Marie a lancé le test.", R),
    ("Paul va croire que Marie a lancé le test.", U),
    ("Paul a failli dire que Marie a lancé le test.", R),
])
def test_non_occurring_meta_event_is_not_asserted(text, content):
    statuses = _statuses(text)
    meta = statuses[0]

    assert meta[0] in META
    assert meta[2] is U
    assert statuses[-1] == ("EXECUTE", statuses[-1][1], content)


@pytest.mark.parametrize("text", [
    "Paul verrait Marie lancer le test.",
    "Paul apprendrait que Marie a lancé le test.",
])
def test_conditional_observation_and_learning_events_are_not_asserted(text):
    assert _statuses(text)[0][2] is U


@pytest.mark.parametrize("text", [
    "Paul dit que Marie a lancé le test.",
    "Paul a dit que Marie a lancé le test.",
    "Paul vient de dire que Marie a lancé le test.",
    "Paul est en train de dire que Marie a lancé le test.",
    "Paul croyait que Marie avait lancé le test.",
    "Paul croit que Marie a lancé le test.",
    "Je vois Marie lancer le test.",
    "J'apprends que Marie a lancé le test.",
])
def test_occurring_meta_events_stay_asserted(text):
    assert _statuses(text)[0][2] is A


def test_stronger_meta_signals_unchanged():
    assert _statuses("Paul croira que Marie a lancé le test.")[0][2] is OccurrenceStatus.FUTURE
    assert _statuses("Paul pourrait dire que Marie a lancé le test.")[0][2] is OccurrenceStatus.UNCERTAIN
    assert _statuses("Paul ne dit pas que Marie a lancé le test.")[0][2] is OccurrenceStatus.NEGATED
