"""MannerRef: typed adverbial modifiers of one predication, only where the word fixes the kind.

RATE: "vite" / "rapidement" (FAST), "lentement" (SLOW); speed as "en peu de temps", which
does not fix duration vs latency (never a deadline nor a temporal anchor). EXECUTION_MODE:
"manuellement" (MANUAL). "automatiquement" (automated mechanism / systematically / by
reflex), "directement", "indirectement" have several readings: they stay reported
(unrepresented_modifier_of), frame open. A negated predication carrying a modifier has an
open negation scope ("ne lance pas vite P": P may well be launched): negated_scope_open,
never a confirmed no-execute nor a prohibition (D5-N6 precedent). Descriptive only: no
event, occurrence, request, permission or authority comes from a modifier.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _mods(f):
    return [(m.unit, m.kind, m.value, f.raw[m.span[0]:m.span[1]]) for m in f.manner_modifiers]


def _open(f):
    out = []
    for m in f.missing:
        if ":unrepresented_modifier_of=" in m:
            a, b = map(int, m.split(":")[1].split("-"))
            out.append((f.raw[a:b], m.rsplit("=", 1)[1]))
    return out


def _claims(f):
    return [(e.predicate_ref, e.occurrence_claim) for e in build_frame_event_index(f).events()]


def _same_commitment(f, ref):
    r = parse_utterance(ref)
    assert [(u.predicate, u.pragmatic, u.polarity, u.subject, tuple(a.text for a in u.objects)) for u in f.units] == \
        [(u.predicate, u.pragmatic, u.polarity, u.subject, tuple(a.text for a in u.objects)) for u in r.units]
    s, rs = governable_summary(f), governable_summary(r)
    assert s["requested_world_actions"] == rs["requested_world_actions"] and f.constraints == r.constraints
    assert _claims(f) == _claims(r)


@pytest.mark.parametrize("text,kind,value,cue", [
    ("Paul lance vite le test.", "RATE", "FAST", "vite"),
    ("Paul lance rapidement le test.", "RATE", "FAST", "rapidement"),
    ("Paul lance lentement le test.", "RATE", "SLOW", "lentement"),
    ("Paul lance manuellement le test.", "EXECUTION_MODE", "MANUAL", "manuellement"),
])
def test_typed_modifier_is_carried_commitment_unchanged(text, kind, value, cue):
    f = parse_utterance(text)
    assert _mods(f) == [("u1", kind, value, cue)] and not _open(f) and f.closure
    _same_commitment(f, "Paul lance le test.")


@pytest.mark.parametrize("text,objs,ref", [
    ("Paul lance P vite.", ("p",), "Paul lance P."),
    ("Lance vite P.", ("p",), "Lance P."),
    ("Lance P et Q vite.", ("p", "q"), "Lance P et Q."),
    ("Lance le test lentement.", ("le test",), "Lance le test."),
])
def test_rate_never_fused_into_nor_replacing_the_object(text, objs, ref):
    # formerly "rapidement / lentement / manuellement" were read as the object itself
    f = parse_utterance(text)
    assert tuple(a.text for a in f.units[0].objects) == objs and len(_mods(f)) == 1
    _same_commitment(f, ref)


def test_modifier_attached_to_its_own_predication():
    f = parse_utterance("Paul lance P vite et Nadia lance Q.")
    assert [(m[0], m[3]) for m in _mods(f)] == [("u1", "vite")] and len(f.units) == 2


@pytest.mark.parametrize("text,cue", [
    ("Paul lance automatiquement le test.", "automatiquement"),
    ("Paul lance directement le test.", "directement"),
    ("Paul lance indirectement le test.", "indirectement"),
])
def test_ambiguous_modifiers_stay_open(text, cue):
    f = parse_utterance(text)
    assert _mods(f) == [] and _open(f) == [(cue, "u1")] and not f.closure
    assert [a.text for a in f.units[0].objects] == ["le test"]


@pytest.mark.parametrize("text,ref", [("Paul ne lance pas vite le test.", "Paul ne lance pas le test."),
                                      ("Ne lance pas vite le test.", "Ne lance pas le test."),
                                      ("Ne lance pas automatiquement le test.", "Ne lance pas le test.")])
def test_negation_kept_but_its_scope_over_the_modifier_is_open(text, ref):
    f, r = parse_utterance(text), parse_utterance(ref)
    (u,) = f.units
    assert u.polarity == "negative" and f"negated_scope_open:{u.id}" in f.ambiguities and not f.closure
    assert u.negation_confirmed is False and f.constraints == ()
    assert governable_summary(f)["confirmed_no_execute"] is False
    assert governable_summary(f)["requested_world_actions"] == governable_summary(r)["requested_world_actions"]
    assert _claims(f) == _claims(r)  # the modifier adds no occurrence of its own


def test_question_keeps_modifier_and_asked_commitment():
    f = parse_utterance("Paul lance-t-il rapidement le test ?")
    (u,) = f.units
    assert u.pragmatic == "ASKED" and _mods(f) == [("u1", "RATE", "FAST", "rapidement")]
    f = parse_utterance("Paul lance-t-il automatiquement le test ?")
    assert f.units[0].pragmatic == "ASKED" and _open(f) == [("automatiquement", "u1")] and not f.closure


def test_relative_subject_ref_intact():
    f = parse_utterance("Le script qui lance manuellement le test.")
    (u,) = f.units
    assert (u.subject_ref.text, u.subject_ref.reference) == ("le script", "RESOLVED_INTRA") and u.subject is None
    assert _mods(f) == [(u.id, "EXECUTION_MODE", "MANUAL", "manuellement")]
    f = parse_utterance("Le script qui lance automatiquement le test.")
    assert f.units[0].subject_ref.text == "le script" and _open(f) == [("automatiquement", f.units[0].id)]


@pytest.mark.parametrize("text,pred,ref", [("Détaille vite le script.", "DETAIL", "Détaille le script."),
                                           ("Compare lentement le script et le document.", "COMPARE",
                                            "Compare le script et le document.")])
def test_detail_compare_keep_the_modifier(text, pred, ref):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.predicate == pred and len(_mods(f)) == 1 and _mods(f)[0][0] == u.id
    assert _claims(f) == []  # DETAIL / COMPARE stay non-eventive
    _same_commitment(f, ref)


def test_unknown_adverb_is_never_silently_lost():
    # no lexical guessing: an unlisted adverb is not typed; its span stays in the frame, open
    f = parse_utterance("Paul lance soigneusement le test.")
    kept = " ".join([a.text for u in f.units for a in u.objects] + list(f.missing))
    assert "soigneusement" in kept and not f.closure and f.manner_modifiers == ()


@pytest.mark.parametrize("text", ["Paul lance vite le test.", "Lance lentement le test.",
                                  "Paul lance manuellement le test."])
def test_modifier_adds_no_event_request_or_authority(text):
    f = parse_utterance(text)
    bare = parse_utterance(text.replace(f.manner_modifiers[0].cue + " ", ""))
    assert len(build_frame_event_index(f).events()) == len(build_frame_event_index(bare).events())
    s, sb = governable_summary(f), governable_summary(bare)
    assert s == sb
