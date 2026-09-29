"""Epistemic E1a: a detached source marker is never dropped from the epistemic projection.

"Selon Marie, P" / "D'après Marie, P" (HUMAN_SOURCE, B2e REPORT profile) project
P as REPORTED; "Selon moi, P" (SPEAKER_BELIEF, B2e BELIEF profile) as BELIEVED —
the same states as "Marie dit que P" / a belief complement. The occurrence
claim stays NO_ASSERTION; nothing becomes VERIFIED / OBSERVED / SUPPORTED.
Trace and inferential sources ("Selon les logs", "Apparemment") have no
settled label (held): they get no new state here.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows

_WORLD_STATES = {"VERIFIED", "OBSERVED", "SUPPORTED"}


def _states(text):
    f = parse_utterance(text)
    flows = project_epistemic_flows(f)
    claims = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    return f, {(x.source_object, x.state) for x in flows}, flows, claims


@pytest.mark.parametrize("text,state", [
    ("Selon Marie, Paul a lancé P.", "REPORTED"),
    ("D'après Marie, Paul a lancé P.", "REPORTED"),
    ("Paul a lancé P, selon Marie.", "REPORTED"),
    ("Selon moi, Paul a lancé P.", "BELIEVED"),
])
def test_source_marked_content_keeps_its_perspective(text, state):
    f, states, flows, claims = _states(text)
    head = next(u for u in f.units if u.epistemic in {"HUMAN_SOURCE", "SPEAKER_BELIEF"})
    assert (head.id, state) in states
    flow = next(x for x in flows if x.source_object == head.id)
    assert flow.metadata["source_epistemic"] == head.epistemic
    assert claims[head.id] == "NO_ASSERTION"
    assert not {s for _, s in states} & _WORLD_STATES


def test_parity_with_explicit_report_and_belief():
    _, s1, _, _ = _states("Selon Marie, Paul a lancé P.")
    _, s2, _, _ = _states("Marie dit que Paul a lancé P.")
    assert {s for _, s in s1} == {s for _, s in s2} == {"REPORTED"}


@pytest.mark.parametrize("text", [
    "Selon les logs, Paul a lancé P.",   # trace source: label held
    "Apparemment, Paul a lancé P.",      # inferential source: label held
    "Paul a lancé P.",                   # speaker assertion: no epistemic state
])
def test_unlabelled_sources_get_no_new_state(text):
    _, states, _, _ = _states(text)
    assert states == set()
