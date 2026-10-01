"""D5-N7 (provisional, fail-closed): manner material is never fused into an object nor dropped.

"Paul lance P tout seul / seul / vite / automatiquement" fused the modifier into the
object ("p tout seul"), "Lance vite P" lost P, "Paul lance tout seul" kept no trace.
_np_from now ends the object before a manner word, the object search skips a manner word
before the object, and, with no positive manner carrier yet, the manner span is reported
(unanalyzed_predicative_content:<span>:unrepresented_modifier_of=<unit>): the frame stays
OPEN. "maintenant" is deixis and untouched; "tout" objects (N6) and quantified objects
(N3) are unchanged. No request, prohibition, authority or event is added.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _mods(f):
    out = []
    for m in f.missing:
        if ":unrepresented_modifier_of=" in m:
            a, b = map(int, m.split(":")[1].split("-"))
            out.append((f.raw[a:b], m.rsplit("=", 1)[1]))
    return out


def _claims(text):
    return [e.occurrence_claim for e in build_frame_event_index(parse_utterance(text)).events()]


@pytest.mark.parametrize("text,objs,mod,ref", [
    ("Paul lance P tout seul.", ("p",), "tout seul", "Paul lance P."),
    ("Paul lance P seul.", ("p",), "seul", "Paul lance P."),
    ("Paul lance P vite.", ("p",), "vite", "Paul lance P."),
    ("Paul lance P automatiquement.", ("p",), "automatiquement", "Paul lance P."),
    ("Paul lance tout seul.", (), "tout seul", "Paul lance."),
    ("Lance vite P.", ("p",), "vite", "Lance P."),
    ("Lance P directement.", ("p",), "directement", "Lance P."),
    ("Lance P et Q vite.", ("p", "q"), "vite", "Lance P et Q."),
    ("Paul et Nadia lancent P ensemble.", ("p",), "ensemble", "Paul et Nadia lancent P."),
])
def test_n7_object_kept_modifier_reported_frame_open(text, objs, mod, ref):
    f, r = parse_utterance(text), parse_utterance(ref)
    (u,) = f.units
    assert tuple(a.text for a in u.objects) == objs
    assert _mods(f) == [(mod, u.id)] and not f.closure
    assert (u.pragmatic, u.polarity, u.subject) == (r.units[0].pragmatic, r.units[0].polarity, r.units[0].subject)
    s, rs = governable_summary(f), governable_summary(r)
    assert s["requested_world_actions"] == rs["requested_world_actions"] and f.constraints == r.constraints
    assert _claims(text) == _claims(ref)


def test_n7_modifier_attached_to_its_own_predication():
    f = parse_utterance("Paul lance P vite et Nadia lance Q.")
    assert _mods(f) == [("vite", "u1")] and len(f.units) == 2


@pytest.mark.parametrize("text,objs", [
    ("Lance P maintenant.", ("p",)), ("Paul lance tout.", ("tout",)), ("Paul lance tout le test.", ("tout le test",)),
    ("Paul lance chacun des tests.", ("chacun des tests",)), ("Paul lance le test.", ("le test",)),
])
def test_n7_controls_closed_without_marker(text, objs):
    f = parse_utterance(text)
    assert tuple(a.text for a in f.units[0].objects) == objs and not _mods(f) and f.closure


def test_n7_copular_n11_unchanged():
    f = parse_utterance("Paul est tout seul.")
    assert f.units == () and not f.closure and not _mods(f)
