"""NEW8 (fail-closed only): the first conjunct of a coordinated subject is never lost silently.

"Nadia et Luc exécutent Q": "et" splits the clause between the two noun
phrases, so "Nadia" became a verbless clause with no unit and no report,
the verb took "luc" as its whole subject, and the frame was closed. The
coordinated-subject schema (group subject, collective / distributive) is not
decided here. Instead the lost conjunct is preserved as a missing entry
coordinated_subject_unrepresented:<span>:subject_of=<unit>, and the unit
carries the named structural ambiguity coordinated_subject_unrepresented
(closure open). Still one event; nothing is duplicated or invented.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.semantic_closure import semantic_closure


def _lost(f):
    return [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":")[2])
            for m in f.missing if m.startswith("coordinated_subject_unrepresented:")]


@pytest.mark.parametrize("text,lost", [
    ("Nadia et Luc exécutent Q.", "Nadia"),
    ("Paul et Nadia ont lancé P.", "Paul"),
    ("Le test et le build ont lancé P.", "Le test"),
    ("Marie et Paul vont lancer P.", "Marie"),
    ("Si Nadia et Luc exécutent Q, arrête R.", "Nadia"),
    ("Paul et moi lançons P.", "Paul"),
])
def test_first_conjunct_is_named_never_dropped(text, lost):
    f = parse_utterance(text)
    found = _lost(f)
    assert [x for x, _ in found] == [lost], found
    uid = found[0][1].split("=")[1] if found[0][1].startswith("subject_of=") else None
    if uid is not None:
        assert f"coordinated_subject_unrepresented:{uid}" in f.ambiguities
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
