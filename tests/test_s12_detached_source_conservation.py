"""S12: a detached source ("Selon Paul,", "D'après les logs,") is never dropped nor read as an object.

The evidential was applied only to an asserted unit; over a request or a question it
vanished and the frame closed, and a clause-final source ("Lance P, selon Paul") was
merged into the clause and read as a second object. A clause-final source is now
consumed by the evidential (never object material); when no positive reading exists yet
(request, question) it is reported with its span
(unanalyzed_predicative_content:<span>:detached_source_of=<unit>) and the frame stays
open. Asserted units keep the existing SourceClass carrier (HUMAN_SOURCE, INFERRED...),
negated ones included. No request, prohibition, authority or occurrence changes.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _sources(f):
    out = []
    for m in f.missing:
        if ":detached_source_of=" in m:
            a, b = map(int, m.split(":")[1].split("-"))
            out.append((f.raw[a:b], m.rsplit("=", 1)[1]))
    return out


def _gov(f):
    s = governable_summary(f)
    return (s["requested_world_actions"], s["confirmed_no_execute"], f.constraints,
            [(u.predicate, u.pragmatic, u.polarity, tuple(a.text for a in u.objects)) for u in f.units],
            [e.occurrence_claim for e in build_frame_event_index(f).events()])


@pytest.mark.parametrize("text,ref,src", [
    ("Selon Paul, lance P.", "Lance P.", "Selon Paul"),
    ("Lance P, selon Paul.", "Lance P.", "selon Paul"),
    ("D'après les logs, lance P.", "Lance P.", "D'après les logs"),
    ("Selon Paul, explique Obsidia.", "Explique Obsidia.", "Selon Paul"),
    ("Selon Paul, est-ce que Marie lance P ?", "Est-ce que Marie lance P ?", "Selon Paul"),
])
def test_s12_source_over_non_assertive_unit_reported_open(text, ref, src):
    f, r = parse_utterance(text), parse_utterance(ref)
    assert _sources(f) == [(src, "u1")] and not f.closure
    assert _gov(f) == _gov(r)  # the source adds no force, request, constraint or occurrence


@pytest.mark.parametrize("text,epistemic", [
    ("Selon Paul, Marie lance P.", "HUMAN_SOURCE"), ("Marie lance P, selon Paul.", "HUMAN_SOURCE"),
    ("Selon Paul, Marie ne lance pas P.", "HUMAN_SOURCE"), ("Apparemment, Marie a lancé P.", "INFERRED"),
])
def test_s12_asserted_units_keep_the_existing_carrier(text, epistemic):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.epistemic == epistemic and [a.text for a in u.objects] == ["p"] and not _sources(f) and f.closure


def test_s12_epistemic_and_functional_sources_never_fused():
    f = parse_utterance("Selon Paul, explique Obsidia avec ta mémoire.")
    assert _sources(f) == [("Selon Paul", "u1")]
    assert any(m.endswith(":unattached_prepositional_of=u1") for m in f.missing)
    assert [a.text for a in f.units[0].objects] == ["obsidia"]
