"""NEW8 (fail-closed only): the first conjunct of a coordinated subject is never lost silently.

"Nadia et Luc exécutent Q": "et" splits the clause between the two noun
phrases, so "Nadia" became a verbless clause with no unit and no report,
the verb took "luc" as its whole subject, and the frame was closed. The
coordinated-subject schema (group subject, collective / distributive) is not
decided here. Instead the lost conjunct is preserved as a missing entry
coordinated_subject_unrepresented:<span>:subject_of=<unit>, and the unit
carries the named structural ambiguity coordinated_subject_unrepresented
(closure open). Still one event; nothing is duplicated or invented.

H14 (D5, decided): the schema is now represented. Every conjunct is a member of
one argument CoordinationRef (construction coordinated_subject, member_kind
"argument", host = the one unit, AND / OR, distributivity UNSPECIFIED): no group
entity, no event per participant, closure no longer blocked. Only a speech-act
person conjunct ("Paul et moi") keeps the fail-closed marker (its agent reading
is not decided).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.semantic_closure import semantic_closure


def _lost(f):
    return [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":")[2])
            for m in f.missing if m.startswith("coordinated_subject_unrepresented:")]


@pytest.mark.parametrize("text,members", [
    ("Nadia et Luc exécutent Q.", ("nadia", "luc")),
    ("Paul et Nadia ont lancé P.", ("paul", "nadia")),
    ("Le test et le build ont lancé P.", ("test", "build")),
    ("Marie et Paul vont lancer P.", ("marie", "paul")),
    ("Si Nadia et Luc exécutent Q, arrête R.", ("nadia", "luc")),
])
def test_h14_every_conjunct_is_a_represented_member(text, members):
    f = parse_utterance(text)
    (c,) = [c for c in f.coordinations if c.construction == "coordinated_subject"]
    assert (c.kind, c.member_kind, c.role, c.member_texts, c.distributivity) ==         ("AND", "argument", "subject", members, "UNSPECIFIED")
    assert c.host in {u.id for u in f.units}
    assert [f.raw[a:b].lower() for a, b in c.member_spans][0].endswith(members[0])
    assert not _lost(f) and not any(a.startswith("coordinated_subject_unrepresented") for a in f.ambiguities)


def test_speech_act_person_conjunct_stays_fail_closed():
    f = parse_utterance("Paul et moi lançons P.")
    found = _lost(f)
    assert [x for x, _ in found] == ["Paul"], found
    assert "coordinated_subject_unrepresented:u1" in f.ambiguities
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text", ["Nadia et Luc exécutent Q.", "Paul et Nadia ont lancé P."])
def test_one_event_nothing_duplicated(text):
    f = parse_utterance(text)
    assert len(f.units) == 1 and len(build_frame_event_index(f).events()) == 1


@pytest.mark.parametrize("text", [
    "Lance le test et le build.", "Paul lance P et Nadia exécute Q.", "Ni Paul ni Nadia n'ont lancé P.",
    "Paul lance le test et le build.", "Nadia exécute Q.",
])
def test_other_coordinations_unchanged(text):
    f = parse_utterance(text)
    assert not _lost(f) and not any(a.startswith("coordinated_subject_unrepresented") for a in f.ambiguities)
