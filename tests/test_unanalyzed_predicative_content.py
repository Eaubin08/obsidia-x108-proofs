"""M8-0b: unanalyzed predicative content is not non-existent content.

A clause whose verb the lexicon does not know ("Paul est parti", "elle appelle
Luc") used to vanish: no unit, no relation, no marker, and closure stayed True.
Such a clause now leaves an `unanalyzed_predicative_content` entry in
frame.missing (source span + structural link), which blocks closure. No
predicate, occurrence, factivity or truth is invented for it.
"""
from __future__ import annotations

import re
from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)
MARK = "unanalyzed_predicative_content"
# Known modal / aspectual heads of an unknown infinitive ("pourrait partir"):
# analyzed operators, not unknown content.
_KNOWN_CONTENT_OPERATORS = {"ABLE", "MUST", "WANT", "NEED", "GO"}


def _markers(frame):
    out = []
    for m in frame.missing:
        match = re.fullmatch(rf"{MARK}:(\d+)-(\d+):([^:]+)(?::governed_by=(u\d+))?(?::ops=(.*))?", m)
        assert match, m
        start, end, link, _governor, ops = match.groups()
        out.append((frame.raw[int(start):int(end)], link, set((ops or "").split(",")) - {""}))
    return out


def _unit(frame, predicate):
    return next(u for u in frame.units if u.predicate == predicate)


@pytest.mark.parametrize("text, span", [
    ("Paul est parti.", "Paul est parti"),
    ("Elle téléphone à Luc.", "Elle téléphone à Luc"),
])
def test_root_unanalyzed_content_is_marked(text, span):
    frame = parse_utterance(text)
    assert _markers(frame) == [(span, "root", set())]
    assert frame.closure is False


@pytest.mark.parametrize("verb, predicate", [
    ("a appris", "LEARN"), ("croit", "BELIEVE"), ("a vu", "OBSERVE"), ("dit", "SAY"),
])
def test_embedded_unanalyzed_content_keeps_its_governor(verb, predicate):
    frame = parse_utterance(f"Marie {verb} que Paul est parti.")
    governor = _unit(frame, predicate)

    assert [u.predicate for u in frame.units] == [predicate]
    assert _markers(frame) == [("Paul est parti", f"embedded_under={governor.id}", set())]
    assert frame.closure is False
    assert all(c.occurrence_status.value != "ASSERTED_OCCURRED" or c.predicate_ref == governor.id
               for c in build_frame_event_index(frame).events())


def test_conditional_branches_keep_their_losses_separately():
    frame = parse_utterance("Si Marie apprend que Paul est parti, elle appelle Luc.")
    learn = _unit(frame, "LEARN")

    assert learn.pragmatic == "HYPOTHETICAL"
    assert _markers(frame) == [
        ("Paul est parti", f"embedded_under={learn.id}", set()),
        ("elle appelle Luc", f"conditional_consequent_of={learn.id}", set()),
    ]
    assert frame.closure is False


def test_unknown_protasis_is_marked_and_consequent_kept():
    frame = parse_utterance("Si Paul part, Luc attend.")
    assert _markers(frame) == [("Paul part", "conditional_protasis", set())]
    assert [u.predicate for u in frame.units] == ["WAIT"]


@pytest.mark.parametrize("text, ops", [
    ("Marie dit que Paul n" + A + "est pas parti.", {"neg"}),
    ("Marie dit que Paul sera parti.", {"future"}),
    ("Marie dit que Paul va partir.", {"future"}),
    ("Marie dit que Paul pourrait partir.", {"modal", "conditional_mood"}),
    ("Paul doit partir.", {"modal"}),
])
def test_detectable_operators_are_recorded(text, ops):
    [(_, _, got)] = _markers(parse_utterance(text))
    assert got == ops


def test_modal_with_unknown_infinitive_keeps_modal_and_link():
    frame = parse_utterance("Marie a appris que Paul pourrait partir.")
    learn, able = _unit(frame, "LEARN"), _unit(frame, "ABLE")
    assert frame.missing == (f"{MARK}:19-39:embedded_under={learn.id}:governed_by={able.id}:ops=conditional_mood,modal",)
    assert frame.closure is False


def test_main_predicate_absorbed_after_relative_is_reported():
    frame = parse_utterance("Le script que Paul a lancé est cassé.")
    # R1-R5 (requalified, formerly "unattached"): named as the antecedent's main predicate
    assert [link for _, link, _ in _markers(frame)] == ["main_predicate_after_relative_of=u1"]
    assert [u.predicate for u in frame.units] == ["EXECUTE"]


def test_coordinated_unknown_clause_is_not_swallowed():
    frame = parse_utterance("Marie dit que Paul a lancé le test et elle appelle Luc.")
    say = _unit(frame, "SAY")
    assert _markers(frame) == [("elle appelle Luc", f"et_after={say.id}", set())]
    assert [u.predicate for u in frame.units] == ["SAY", "EXECUTE"]


@pytest.mark.parametrize("text", [
    "Paul a lancé le test.",
    "Marie a appris que Paul a lancé le test.",
    "Lance le test.",
    "Il est si content.",
    "Paul et Marie ont lancé le test.",
    "Merci beaucoup.",
    "Je suis là.",
])
def test_analyzed_or_non_predicative_text_is_not_marked(text):
    # no unanalysed predicative content; a coordinated subject's first conjunct is
    # reported under its own marker (NEW8, test_coordinated_subject_unrepresented)
    missing = parse_utterance(text).missing
    assert not [m for m in missing if m.startswith(MARK)]
    assert all(m.startswith("coordinated_subject_unrepresented:") for m in missing)


def test_unanalyzed_content_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "SILENT_PREDICATIVE_CONTENT_LOSS", "UNANALYZED_CONTENT_CLOSED", "UNKNOWN_CONTENT_ROOT_PROMOTION",
        "UNKNOWN_CONTENT_ASSERTED_OCCURRED", "KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT", "SUPPORTED_CONTENT_DIFF",
        "UNANALYZED_CONTENT_MARKERS", "EMBEDDED_UNKNOWN_CASES", "CONDITIONAL_UNKNOWN_CASES",
    ), 0)
    unknown = {"past": "Paul est parti", "past2": "Paul a dormi", "neg": f"Paul n{A}est pas parti",
               "future": "Paul va partir", "modal": "Paul pourrait partir", "finite": "elle appelle Luc"}
    known = {"past": "Paul a lancé le test", "past2": "Paul a relancé le build", "neg": f"Paul n{A}a pas lancé le test",
             "future": "Paul va lancer le test", "modal": "Paul pourrait lancer le test", "finite": "elle lance le job"}
    governors = {"LEARN": "a appris que", "BELIEVE": "croit que", "SAY": "dit que", "OBSERVE": "a vu que",
                 "LEARN_NEG": f"n{A}a pas appris que", "SAY_FUT": "dira que"}
    subjects = ("Marie", "Nadia", "Le chef", "Omar", "Jean", "La directrice", "Hugo", "Anne")

    def shapes(content, subject, gov):
        yield "root", content[0].upper() + content[1:] + "."
        yield "embedded", f"{subject} {gov} {content}."
        yield "embedded2", f"{subject} dit que Jean {gov} {content}."
        yield "protasis_embedded", f"Si {subject} {gov.replace('a appris', 'apprend').replace('a vu', 'voit')} {content}, Luc attend."
        yield "consequent", f"Si {subject} lance le lot, {content}."
        yield "consequent_embedded", f"Si {subject} lance le lot, Luc {gov} {content}."

    known_units = {}
    for (kind, content), subject, (gname, gov) in product(known.items(), subjects, governors.items()):
        for shape, text in shapes(content, subject, gov):
            frame = parse_utterance(text)
            metrics["CASES"] += 1
            if frame.missing:
                metrics["SUPPORTED_CONTENT_DIFF"] += 1
            start = text.lower().index(content.lower())
            known_units[(kind, subject, gname, shape)] = [
                u.predicate for u in frame.units if not start <= u.span[0] < start + len(content)]

    for (kind, content), subject, (gname, gov) in product(unknown.items(), subjects, governors.items()):
        for shape, text in shapes(content, subject, gov):
            metrics["CASES"] += 1
            frame = parse_utterance(text)
            index = build_frame_event_index(frame)
            markers = _markers(frame)
            metrics["UNANALYZED_CONTENT_MARKERS"] += len(markers)
            metrics["EMBEDDED_UNKNOWN_CASES"] += shape.startswith(("embedded", "protasis"))
            metrics["CONDITIONAL_UNKNOWN_CASES"] += shape in {"protasis_embedded", "consequent", "consequent_embedded"}
            content_spans = [s for s, _, _ in markers]
            if not any(content.lower() in s.lower() for s in content_spans):
                metrics["SILENT_PREDICATIVE_CONTENT_LOSS"] += 1
            if frame.closure:
                metrics["UNANALYZED_CONTENT_CLOSED"] += 1
            start = text.lower().index(content.lower())
            inside = [u for u in frame.units if start <= u.span[0] < start + len(content)
                      and u.predicate not in _KNOWN_CONTENT_OPERATORS]
            if any(u.embedded_under is None and u.pragmatic == "ASSERTED" for u in inside):
                metrics["UNKNOWN_CONTENT_ROOT_PROMOTION"] += 1
            if any(index.event_for(u.id) and index.event_for(u.id).occurrence_status.value == "ASSERTED_OCCURRED"
                   for u in inside):
                metrics["UNKNOWN_CONTENT_ASSERTED_OCCURRED"] += 1
            link = next((l for s, l, _ in markers if content.lower() in s.lower()), "")
            expected_link = {"root": "root", "embedded": "embedded_under=", "embedded2": "embedded_under=",
                             "protasis_embedded": "embedded_under=", "consequent": "conditional_consequent_of=",
                             "consequent_embedded": "embedded_under="}[shape]
            if not link.startswith(expected_link):
                metrics["KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT"] += 1
            if shape == "protasis_embedded" and not any(u.pragmatic == "HYPOTHETICAL" for u in frame.units):
                metrics["KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT"] += 1
            if gname == "LEARN_NEG" and shape == "embedded" and _unit(frame, "LEARN").polarity != "negative":
                metrics["KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT"] += 1
            outside = [u.predicate for u in frame.units if not start <= u.span[0] < start + len(content)]
            if outside != known_units[(kind, subject, gname, shape)]:
                metrics["KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT"] += 1

    assert metrics["CASES"] >= 3000, metrics
    for key in ("UNANALYZED_CONTENT_MARKERS", "EMBEDDED_UNKNOWN_CASES", "CONDITIONAL_UNKNOWN_CASES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("SILENT_PREDICATIVE_CONTENT_LOSS", "UNANALYZED_CONTENT_CLOSED", "UNKNOWN_CONTENT_ROOT_PROMOTION",
                "UNKNOWN_CONTENT_ASSERTED_OCCURRED", "KNOWN_SCOPE_LOST_AROUND_UNKNOWN_CONTENT",
                "SUPPORTED_CONTENT_DIFF"):
        assert metrics[key] == 0, (key, metrics)
