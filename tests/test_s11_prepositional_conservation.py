"""S11: unattached prepositional content is preserved and keeps the frame open.

Material introduced by a preposition after a unit's objects ("en utilisant ta mémoire",
"à partir du document X", "avec Python", "sur le serveur", "avec Q") was dropped and
the frame closed, including gated directives. It is now reported with its exact span
(unanalyzed_predicative_content:<span>:unattached_prepositional_of=<unit>); its role
(source, instrument, location...) is NOT decided here (ObliqueArgumentRef comes later).
Structures that already consume material (temporal cues, participant configuration,
quantified objects, infinitive units, protases) are untouched. No request, prohibition,
occurrence, memory or tool decision changes.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _preps(f):
    out = []
    for m in f.missing:
        if ":unattached_prepositional_of=" in m:
            a, b = map(int, m.split(":")[1].split("-"))
            out.append((f.raw[a:b], m.rsplit("=", 1)[1]))
    return out


def _gov(f):
    s = governable_summary(f)
    return (s["requested_world_actions"], s["confirmed_no_execute"], f.constraints,
            [(u.predicate, u.pragmatic, u.polarity, u.subject, tuple(a.text for a in u.objects)) for u in f.units],
            [e.occurrence_claim for e in build_frame_event_index(f).events()])


@pytest.mark.parametrize("text,ref,span", [
    ("Explique-moi Obsidia en utilisant ta mémoire.", "Explique-moi Obsidia.", "en utilisant ta mémoire"),
    ("Explique Obsidia à partir de ta mémoire.", "Explique Obsidia.", "à partir de ta mémoire"),
    ("Explique Obsidia avec ta mémoire.", "Explique Obsidia.", "avec ta mémoire"),
    ("Explique Obsidia avec Python.", "Explique Obsidia.", "avec Python"),
    ("Explique Obsidia à partir du document X.", "Explique Obsidia.", "à partir du document X"),
    ("Lance P sur le serveur.", "Lance P.", "sur le serveur"),
    ("Lance P avec Q.", "Lance P.", "avec Q"),
    ("Dis bonjour à maman.", "Dis bonjour.", "à maman"),  # recipient: closed -> open (S11)
])
def test_s11_prepositional_content_kept_frame_open(text, ref, span):
    f, r = parse_utterance(text), parse_utterance(ref)
    assert _preps(f) == [(span, "u1")] and not f.closure and r.closure
    assert _gov(f) == _gov(r)  # same units, force, objects, requests, constraints, occurrence


@pytest.mark.parametrize("text", [
    "Explique Obsidia.", "Lance P.", "Lance P immédiatement.", "Paul lance chacun des tests.",
    "Si Paul lance P, exécute Q.", "Lance P pour tester Q.", "Ils lancent P ensemble.", "Paul lance P tout seul.",
])
def test_s11_consumed_material_not_reported(text):
    f = parse_utterance(text)
    assert not _preps(f) and f.closure


def test_s11_nominal_internal_pp_stays_preserved_open():
    f = parse_utterance("Paul lance le test de Marie.")
    assert any(m.endswith(":unattached_nominal_of=u1") for m in f.missing) and not _preps(f) and not f.closure


def test_s11_auxiliary_a_is_not_the_preposition():
    # "a" is both the auxiliary and an unaccented "à": a verb never opens prepositional content
    f = parse_utterance("Le test que Paul a lancé a échoué.")
    assert not _preps(f)


@pytest.mark.parametrize("text,obj", [("Lance le test s'il te plaît.", "le test"), ("Lance P s'il vous plaît.", "p")])
def test_politeness_formula_never_enters_the_object(text, obj):
    f = parse_utterance(text)
    assert [a.text for a in f.units[0].objects] == [obj] and f.closure
    assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"]
