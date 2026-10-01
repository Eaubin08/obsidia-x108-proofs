"""D5-N4 (provisional fail-closed): floating "chacun" of a plural NON-coordinated subject.

"Ils lancent chacun P" read "chacun p" as the object and closed. The floating
quantifier is not object material: the object is re-read after it ("p"), and since
no positive carrier exists yet for the distributivity of a non-coordinated subject,
the quantifier is reported (unanalyzed_predicative_content:<span>:
subject_distributivity_of=<unit>) and the frame stays OPEN. Same inside the verb
chain ("Ils ont chacun lancé P"), which R1 made transparent. Coordinated subjects
keep their positive EXPLICIT CoordinationRef; a partitive "chacun des tests" stays
the quantified object (N3). No anaphora resolution, no event multiplication.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _marker(f):
    return [m for m in f.missing if ":subject_distributivity_of=" in m]


def _ev(text):
    return [e.occurrence_claim for e in build_frame_event_index(parse_utterance(text)).events()]


@pytest.mark.parametrize("text,subject,each,base", [
    ("Ils lancent chacun P.", "ils", "chacun", "Ils lancent P."),
    ("Elles lancent chacune P.", "elles", "chacune", "Elles lancent P."),
    ("Les agents lancent chacun P.", "agents", "chacun", "Les agents lancent P."),
    ("Les équipes lancent chacune P.", "équipes", "chacune", "Les équipes lancent P."),
    ("Ils ont chacun lancé P.", "ils", "chacun", "Ils ont lancé P."),
])
def test_n4_object_restored_and_distributivity_kept_open(text, subject, each, base):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.subject, [a.text for a in u.objects]) == (subject, ["p"])
    (m,) = _marker(f)
    a, b = map(int, m.split(":")[1].split("-"))
    assert f.raw[a:b] == each and m.endswith(f"={u.id}")
    assert not f.closure and not f.coordinations
    assert _ev(text) == _ev(base) and len(_ev(text)) == 1  # no promotion, no multiplication
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False and f.constraints == ()


@pytest.mark.parametrize("text", ["Paul et Nadia lancent chacun P.", "Paul et Nadia ont chacun lancé P.",
                                  "Paul et Nadia lanceront chacun P."])
def test_n4_coordinated_subject_keeps_positive_model(text):
    f = parse_utterance(text)
    (c,) = f.coordinations
    assert c.distributivity == "EXPLICIT" and not _marker(f) and f.closure
    assert [a.text for a in f.units[0].objects] == ["p"]


@pytest.mark.parametrize("text", ["Paul lance chacun des tests.", "Ils lancent chacun des tests.", "Ils lancent P."])
def test_n4_quantified_object_and_plain_plural_unchanged(text):
    f = parse_utterance(text)
    assert not _marker(f) and f.closure
