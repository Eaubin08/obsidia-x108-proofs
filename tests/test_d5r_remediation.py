"""D5-R local remediation: R2 (comma objects), R3 (mixed-person subject), R1 ("chacun" tense).

R2: comma-separated object NPs stay distinct argument mentions ("P, Q et R" ->
[p, q, r], AND; "P, Q ou R" -> OR); a comma tail that cannot be attached is never
dropped silently. "P et Q ou R" stays named (coordination_attachment_ambiguous).

R3: a coordinated subject whose members span more than one action_agent class
("Toi et moi", "Toi et Paul", "Paul et moi") keeps every member, gets the existing
UNKNOWN agent (no MIXED value) and leaves closure open. Homogeneous subjects keep
their class.

R1: a floating "chacun" between the auxiliary and the participle is transparent to
the tense chain: "ont chacun lancé" has the tense / occurrence of "ont lancé" (no
promotion beyond it) and keeps distributivity EXPLICIT.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _objects(f):
    return [c for c in f.coordinations if c.construction == "coordinated_object"]


def _subject(f):
    return [c for c in f.coordinations if c.construction == "coordinated_subject"]


def _no_false_force(f):
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False
    assert f.constraints == () and all(u.pragmatic not in {"REQUESTED", "FORBIDDEN"} for u in f.units)


# ── R2 ──
@pytest.mark.parametrize("text,kind,members", [
    ("Paul lance P, Q et R.", "AND", ("p", "q", "r")),
    ("Paul lance P, Q ou R.", "OR", ("p", "q", "r")),
    ("Paul lance le test, le build et R.", "AND", ("le test", "le build", "r")),
    ("Paul lance P et Q.", "AND", ("p", "q")),
    ("Paul lance P ou Q.", "OR", ("p", "q")),
    ("Paul lance P et Q et R.", "AND", ("p", "q", "r")),
    ("Paul lance P ou Q ou R.", "OR", ("p", "q", "r")),
])
def test_r2_comma_objects_stay_distinct(text, kind, members):
    f = parse_utterance(text)
    assert len(f.units) == 1 and len(build_frame_event_index(f).events()) == 1
    assert tuple(a.text for a in f.units[0].objects) == members
    (c,) = _objects(f)
    assert (c.kind, c.member_texts) == (kind, members)


def test_r2_mixed_and_or_stays_named():
    f = parse_utterance("Paul lance P et Q ou R.")
    assert not _objects(f) and "coordination_attachment_ambiguous:u1" in f.ambiguities and not f.closure


# ── R3 ──
@pytest.mark.parametrize("text,members", [
    ("Paul et moi lançons P.", ("paul", "moi")),
    ("Toi et moi lançons P.", ("toi", "moi")),
    ("Toi et Paul lancez P.", ("toi", "paul")),
])
def test_r3_mixed_person_subject_is_unknown_and_open(text, members):
    f = parse_utterance(text)
    (c,) = _subject(f)
    assert c.member_texts == members and len(f.units) == 1
    assert f.units[0].action_agent == "UNKNOWN" and not f.closure
    _no_false_force(f)


@pytest.mark.parametrize("text,agent", [
    ("Paul et Nadia lancent P.", "THIRD_PARTY"), ("Paul lance P.", "THIRD_PARTY"),
    ("Tu lances P.", "ADDRESSEE"), ("Je lance P.", "SPEAKER"),
])
def test_r3_homogeneous_agents_unchanged(text, agent):
    f = parse_utterance(text)
    assert f.units[0].action_agent == agent and f.closure


# ── R1 ──
def test_r1_chacun_is_transparent_to_the_tense_chain():
    base, each = parse_utterance("Paul et Nadia ont lancé P."), parse_utterance("Paul et Nadia ont chacun lancé P.")
    b, e = base.units[0], each.units[0]
    assert (e.tense_aspect, e.realized, e.verb_form) == (b.tense_aspect, b.realized, b.verb_form) == ("PAST", True, "PARTICIPLE")
    ev = lambda f: build_frame_event_index(f).events()[0].occurrence_claim
    assert ev(each) == ev(base)  # no promotion beyond the sentence without "chacun"
    assert _subject(each)[0].distributivity == "EXPLICIT" and _subject(base)[0].distributivity == "UNSPECIFIED"
    assert each.closure == base.closure


@pytest.mark.parametrize("text,tense", [("Paul et Nadia peuvent chacun lancer P.", "PRESENT"),
                                        ("Paul et Nadia vont chacun lancer P.", "NEAR_FUTURE")])
def test_r1_chacun_inside_modal_or_periphrastic_chain(text, tense):
    f = parse_utterance(text)
    assert len(f.units) == 1 and len(build_frame_event_index(f).events()) == 1
    assert f.units[0].tense_aspect == tense and f.units[0].subject == "paul et nadia"
    (c,) = _subject(f)
    assert c.distributivity == "EXPLICIT"
    _no_false_force(f)


# ── N1: future coordinated subject + post-verbal "chacun" ──
@pytest.mark.parametrize("text,tense,dist,objs", [
    ("Paul et Nadia lanceront P.", "FUTURE", "UNSPECIFIED", ("p",)),
    ("Paul et Nadia lanceront chacun P.", "FUTURE", "EXPLICIT", ("p",)),
    ("Paul et Nadia lancent chacun P.", "PRESENT", "EXPLICIT", ("p",)),
    ("Paul et Nadia ont chacun lancé P.", "PAST", "EXPLICIT", ("p",)),
    ("Paul et Nadia peuvent chacun lancer P.", "PRESENT", "EXPLICIT", ("p",)),
    ("Paul et Nadia lanceront chacun le test.", "FUTURE", "EXPLICIT", ("le test",)),
])
def test_n1_future_and_post_verbal_chacun(text, tense, dist, objs):
    f = parse_utterance(text)
    (u,) = f.units
    (c,) = _subject(f)
    assert (c.member_texts, c.distributivity) == (("paul", "nadia"), dist)
    assert (u.tense_aspect, u.action_agent, u.subject) == (tense, "THIRD_PARTY", "paul et nadia")
    assert tuple(a.text for a in u.objects) == objs and not any("chacun" in a.text for a in u.objects)
    assert len(build_frame_event_index(f).events()) == 1 and f.closure
    _no_false_force(f)


def test_n1_no_promotion_from_post_verbal_chacun():
    ev = lambda t: build_frame_event_index(parse_utterance(t)).events()[0].occurrence_claim
    assert ev("Paul et Nadia lanceront chacun P.") == ev("Paul et Nadia lanceront P.")
    assert ev("Paul et Nadia lancent chacun P.") == ev("Paul et Nadia lancent P.")


@pytest.mark.parametrize("text", ["Paul lance chacun des tests.", "Paul et Nadia lancent chacun des tests."])
def test_n1_partitive_chacun_is_an_object_not_subject_distributivity(text):
    f = parse_utterance(text)
    # N3: the partitive quantifier is one complete object argument (was truncated to "chacun")
    assert [a.text for a in f.units[0].objects] == ["chacun des tests"]
    assert all(c.distributivity != "EXPLICIT" for c in _subject(f))
