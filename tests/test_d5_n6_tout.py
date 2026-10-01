"""D5-N6: "tout" as an argument keeps its object role and never breaks the verb chain.

"tout" sat in _MANNER_ADVERBS (for "tout seul"), so the pronoun object of "lance tout"
was dropped, and it broke "a tout lancé" / "peut tout lancer" into a detached EXECUTE
whose subject was "tout" (losing PAST, modality, the indirect request of "Tu peux tout
lancer ?"). Now: "tout" right after the verb (not "tout seul") is the object; between an
auxiliary / modal and the lexical verb it is transparent to the chain and recorded as its
object. "ne ... pas tout" is NOT ALL, never NONE: the negated scope is open (H01
negated_scope_open), no unrestricted NO_EXECUTE and no confirmed no-execute.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _row(text):
    f = parse_utterance(text)
    s = governable_summary(f)
    return f, s, [(u.predicate, u.subject, u.pragmatic, u.polarity, u.modality, u.tense_aspect,
                   tuple(a.text for a in u.objects)) for u in f.units]


def _claims(text):
    return [e.occurrence_claim for e in build_frame_event_index(parse_utterance(text)).events()]


@pytest.mark.parametrize("text,ref", [
    ("Paul lance tout.", "Paul lance P."),
    ("Paul exécute tout.", "Paul exécute P."),
    ("Paul a tout lancé.", "Paul a lancé P."),
    ("Paul veut tout lancer.", "Paul veut lancer P."),
    ("Paul peut tout lancer.", "Paul peut lancer P."),
    ("Tu peux tout lancer ?", "Tu peux lancer P ?"),
    ("Paul ne doit pas tout lancer.", "Paul ne doit pas lancer P."),
])
def test_n6_tout_object_same_structure_as_explicit_object(text, ref):
    f, s, rows = _row(text)
    rf, rs, rrows = _row(ref)
    assert [r[:-1] for r in rows] == [r[:-1] for r in rrows]  # same units, subject, force, modality, tense
    assert [r[-1] for r in rows] == [("tout",)] * len(rows)
    assert s["requested_world_actions"] == rs["requested_world_actions"]
    assert s["confirmed_no_execute"] == rs["confirmed_no_execute"] and f.constraints == rf.constraints
    assert _claims(text) == _claims(ref)  # no promotion
    assert all(u.subject != "tout" and "tout" not in (u.subject or "") for u in f.units)


def test_n6_ne_pas_tout_is_not_all_never_none():
    f, s, rows = _row("Ne lance pas tout.")
    assert rows == [("EXECUTE", None, "FORBIDDEN", "negative", None, "NONE", ("tout",))]
    assert "negated_scope_open:u1" in f.ambiguities and not f.closure
    assert not any(c.endswith("(*)") or c.endswith("(tout)") for c in f.constraints)
    assert s["confirmed_no_execute"] is False and s["requested_world_actions"] == []


@pytest.mark.parametrize("text,objs", [
    ("Paul lance tout le test.", ("tout le test",)), ("Paul lance tous les tests.", ("tous les tests",)),
    ("Paul lance chacun des tests.", ("chacun des tests",)), ("Paul lance tout seul.", ()),
    ("Ne lance pas P.", ("p",)),
])
def test_n6_controls(text, objs):
    assert tuple(a.text for a in parse_utterance(text).units[0].objects) == objs


def test_n6_ne_lance_pas_p_unchanged():
    f, s, _ = _row("Ne lance pas P.")
    assert f.constraints == ("NO_EXECUTE(p)",) and s["confirmed_no_execute"] is True and f.closure


def test_n6_ne_pas_tous_les_x_is_not_all_either():
    f, s, _ = _row("Ne lance pas tous les tests.")
    assert "negated_scope_open:u1" in f.ambiguities and f.constraints == () and s["confirmed_no_execute"] is False


def test_n6_ne_rien_stays_none():
    f, s, _ = _row("Ne lance rien.")
    assert f.constraints == ("NO_EXECUTE(*)",) and s["confirmed_no_execute"] is True
