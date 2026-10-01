"""D5-N3: quantified nominal objects are conserved as ONE complete argument.

"chacun des tests", "chacun de ces tests", "tous les tests", "toutes les tâches",
"un des tests", "une des options" were truncated ("chacun", "tous") or dropped
("un des tests") with a closed frame. The quantifier now owns its structurally
licensed nominal complement; a nominal remainder that still cannot be attached is
reported (unanalyzed content), never dropped. Quantification is not subject
distributivity and never multiplies events.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text,obj", [
    ("Paul lance chacun des tests.", "chacun des tests"),
    ("Paul lance chacun de ces tests.", "chacun de ces tests"),
    ("Paul lance tous les tests.", "tous les tests"),
    ("Paul lance toutes les tâches.", "toutes les tâches"),
    ("Paul lance un des tests.", "un des tests"),
    ("Paul lance une des options.", "une des options"),
])
def test_n3_quantified_object_is_one_complete_argument(text, obj):
    f = parse_utterance(text)
    (u,) = f.units
    assert [a.text for a in u.objects] == [obj]
    a = u.objects[0]
    assert f.raw[a.span[0]:a.span[1]].lower() == obj
    assert u.subject == "paul" and not f.coordinations
    assert len(build_frame_event_index(f).events()) == 1 and f.closure
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False and f.constraints == ()


@pytest.mark.parametrize("text,objs", [
    ("Paul lance certains tests.", ["certains tests"]),
    ("Paul lance le test.", ["le test"]),
    ("Paul lance P, Q et R.", ["p", "q", "r"]),
    ("Paul lance P ou Q.", ["p", "q"]),
    ("Paul et Nadia lancent chacun P.", ["p"]),
])
def test_n3_controls_unchanged(text, objs):
    assert [a.text for a in parse_utterance(text).units[0].objects] == objs


@pytest.mark.parametrize("text,rest", [("Paul lance le test de Marie.", "de Marie"),
                                       ("Ne lance aucun des tests.", "des tests")])  # "aucun": the negator
def test_n3_unconsumed_nominal_is_reported_never_dropped(text, rest):
    f = parse_utterance(text)
    found = [m for m in f.missing if m.endswith(":unattached_nominal_of=u1")]
    assert len(found) == 1 and not f.closure
    a, b = map(int, found[0].split(":")[1].split("-"))
    assert f.raw[a:b] == rest
