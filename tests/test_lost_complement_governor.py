"""M8-0: a complement governor the parser cannot classify must not vanish.

"Marie a découvert que X", "Marie se souvient que X", "Marie se doute que X",
"Marie s'imagine que X", "Marie parle du fait que X": the governor used to be
dropped (irregular participle, intervening clitic, "du fait" head) and X was
promoted to a root ASSERTED / ASSERTED_OCCURRED clause. The governor is now
kept as UNKNOWN_COMPLEMENT_GOVERNOR (existing B2a route), X stays embedded,
and no factivity is decided. A "que" complement whose governor still cannot be
built is subordinated (UNRESOLVED_GOVERNANCE), never promoted to a root.
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import UNRESOLVED_GOVERNOR, parse_utterance
from app.semantic.lattice.ir_projection import governable_summary

A = chr(39)
X = "Paul a lancé le test"
ASSERTED = "ASSERTED_OCCURRED"

# family -> (present, past, future, negated present, conditional-protasis present)
FAMILIES = {
    "DISCOVER": ("découvre", "a découvert", "découvrira", "ne découvre pas", "découvre"),
    "REMEMBER": ("se souvient", f"s{A}est souvenue", "se souviendra", "ne se souvient pas", "se souvient"),
    "DOUBT": ("se doute", f"s{A}est doutée", "se doutera", "ne se doute pas", "se doute"),
    "IMAGINE": (f"s{A}imagine", f"s{A}est imaginé", f"s{A}imaginera", f"ne s{A}imagine pas", f"s{A}imagine"),
    "TALK_ABOUT_FACT": ("parle du fait", "a parlé du fait", "parlera du fait", "ne parle pas du fait", "parle du fait"),
}


def _analyse(text):
    frame = parse_utterance(text)
    return frame, build_frame_event_index(frame)


def _complement(frame):
    return next(u for u in frame.units if u.predicate == "EXECUTE")


def _assert_preserved(text):
    frame, index = _analyse(text)
    x = _complement(frame)
    governors = [u for u in frame.units if u.predicate == UNRESOLVED_GOVERNOR]

    assert len(governors) == 1, (text, [u.predicate for u in frame.units])
    governor = governors[0]
    assert x.embedded_under == governor.id, text
    assert ("EMBEDS", governor.id, x.id) in {(r.kind, r.source, r.target) for r in frame.relations}, text
    assert x.pragmatic == "EMBEDDED", text
    assert index.event_for(x.id).occurrence_status.value != ASSERTED, text
    assert f"complement_under_unresolved_governor:{x.id}" in frame.ambiguities, text
    return frame, index, governor, x


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("form", ["present", "past", "future"])
def test_lost_governor_is_preserved_and_complement_embedded(family, form):
    verb = FAMILIES[family][("present", "past", "future").index(form)]
    _, _, governor, _ = _assert_preserved(f"Marie {verb} que {X}.")
    if form == "past":
        assert governor.tense_aspect in {"PAST", "PLUPERFECT"}
    if form == "future":
        assert governor.tense_aspect == "FUTURE" or governor.surface.endswith(("ra", "era"))


@pytest.mark.parametrize("family", FAMILIES)
def test_negation_stays_on_the_governor(family):
    _, _, governor, x = _assert_preserved(f"Marie {FAMILIES[family][3]} que {X}.")
    assert governor.polarity == "negative"
    assert x.polarity == "positive"


@pytest.mark.parametrize("family", FAMILIES)
def test_conditional_scope_stays_visible(family):
    frame, index, governor, x = _assert_preserved(f"Si Marie {FAMILIES[family][4]} que {X}, Luc attend.")
    assert governor.pragmatic == "HYPOTHETICAL"
    assert "CONDITIONS" in {r.kind for r in frame.relations if r.source == governor.id}
    assert index.event_for(x.id).occurrence_status.value != ASSERTED


@pytest.mark.parametrize("text", [
    f"Je me souviens que {X}.",
    f"Il se doute que {X}.",
    f"Elle s{A}imagine que {X}.",
    f"Paul te promet que Marie a lancé le test.",
    f"Le chef se souvient que {X}.",
    f"Marie a parlé du fait que {X}.",
])
def test_pronominal_and_clitic_variants(text):
    _assert_preserved(text)


@pytest.mark.parametrize("text", [
    f"Marie se rend compte que {X}.",
    f"Si Marie se rend compte que {X}, Luc attend.",
    f"Marie parle de ce que Paul a lancé.",
])
def test_unbuildable_governor_never_promotes_complement_to_root(text):
    frame, index = _analyse(text)
    x = _complement(frame)
    assert x.pragmatic != "ASSERTED" or x.embedded_under is not None, text
    assert index.event_for(x.id).occurrence_status.value != ASSERTED, text
    assert any(a.endswith(f":{x.id}") for a in frame.ambiguities), text


def test_lexical_fact_is_not_world_fact():
    frame, index, _, x = _assert_preserved(f"Marie parle du fait que {X}.")
    assert index.event_for(x.id).occurrence_status.value != ASSERTED
    # the noun "fait" is not a predicate and asserts nothing
    assert all(u.predicate != "DO" for u in frame.units)


@pytest.mark.parametrize("text, predicates", [
    ("Paul a découvert le bug.", None),
    ("Marie se souvient du test.", None),
    ("Marie parle du test.", None),
    ("Le mur que Paul a peint est bleu.", None),
    ("Le fait que Paul a lancé le test inquiète Marie.", None),
])
def test_non_complement_uses_are_unchanged(text, predicates):
    frame = parse_utterance(text)
    assert all(u.predicate != UNRESOLVED_GOVERNOR for u in frame.units), text
    assert not any(a.startswith("complement_governor_lost") for a in frame.ambiguities), text


@pytest.mark.parametrize("text, expected", [
    (f"Marie sait que {X}.", "UNKNOWN"),
    (f"Marie a appris que {X}.", ASSERTED),
    (f"Marie a vu que {X}.", ASSERTED),
    (f"Marie dit que {X}.", "REPORTED"),
    (f"Marie croit que {X}.", "UNKNOWN"),
    (f"Marie a compris que {X}.", "UNKNOWN"),
])
def test_supported_families_are_unchanged(text, expected):
    frame, index = _analyse(text)
    assert index.event_for(_complement(frame).id).occurrence_status.value == expected


def test_lost_governor_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "LOST_GOVERNOR_COMPLEMENT_PROMOTION", "UNSUPPORTED_GOVERNOR_ASSERTED_COMPLEMENT", "NEGATION_LOST",
        "CONDITION_LOST", "FUTURE_LOST", "FIRST_MATCH", "CRASH", "SUPPORTED_DRIFT",
        "UNRESOLVED_GOVERNOR_CASES", "PRESERVED_EMBEDDED_COMPLEMENTS", "SUPPORTED_GOVERNOR_CASES",
    ), 0)
    subjects = ("Marie", "Le chef", "Elle", "Nadia", "Omar", "La directrice", "Il", "Jean")
    complements = (X, "Paul lance le build", "Paul ne lance pas le build", "Paul lancera le job",
                   "Luc dit que Paul a lancé le test", "Paul a relancé le script", "Paul n'a pas lancé le lot")
    placements = ("{c}.", "Si {c}, Luc attend.", "Si Omar lance le lot, {c}.")
    supported = {"sait": "UNKNOWN", "a appris": None, "dit": "REPORTED", "croit": "UNKNOWN"}
    forms = [(fam, i, v) for fam, vs in FAMILIES.items() for i, v in enumerate(vs[:4])]
    for (fam, i, verb), subject, comp, place in product(forms, subjects, complements, placements):
        subj = subject.lower() if place.startswith("Si") and subject in {"Elle", "Il"} else subject
        text = place.format(c=f"{subj} {verb} que {comp}")
        text = text[0].upper() + text[1:]
        metrics["CASES"] += 1
        try:
            frame, index = _analyse(text)
        except Exception:
            metrics["CRASH"] += 1
            continue
        governors = [u for u in frame.units if u.predicate == UNRESOLVED_GOVERNOR]
        if len(governors) != 1:
            metrics["LOST_GOVERNOR_COMPLEMENT_PROMOTION"] += 1
            continue
        governor = governors[0]
        metrics["UNRESOLVED_GOVERNOR_CASES"] += 1
        inner = [u for u in frame.units if u.span[0] > governor.span[1] and u.predicate != "WAIT"]
        head = min(inner, key=lambda u: u.span[0])
        if head.embedded_under != governor.id:
            metrics["LOST_GOVERNOR_COMPLEMENT_PROMOTION"] += 1
            continue
        metrics["PRESERVED_EMBEDDED_COMPLEMENTS"] += 1
        for u in inner:
            event = index.event_for(u.id)
            if event is not None and event.occurrence_status.value == ASSERTED:
                metrics["UNSUPPORTED_GOVERNOR_ASSERTED_COMPLEMENT"] += 1
        if i == 3 and governor.polarity != "negative":
            metrics["NEGATION_LOST"] += 1
        if place.startswith("Si {c}") and "CONDITIONS" not in {r.kind for r in frame.relations if r.source == governor.id}:
            metrics["CONDITION_LOST"] += 1
        if comp.startswith("Paul n") and head.polarity != "negative":
            metrics["NEGATION_LOST"] += 1
        if "lancera" in comp and index.event_for(head.id).occurrence_status.value != "FUTURE":
            metrics["FUTURE_LOST"] += 1
        if len([r for r in frame.relations if r.kind == "EMBEDS" and r.source == governor.id]) != 1:
            metrics["FIRST_MATCH"] += 1
    for verb, expected, subject, place in product(supported, ("UNKNOWN",), subjects, placements[:1]):
        frame, index = _analyse(place.format(c=f"{subject} {verb} que {X}"))
        metrics["CASES"] += 1
        metrics["SUPPORTED_GOVERNOR_CASES"] += 1
        want = {"sait": "UNKNOWN", "a appris": ASSERTED, "dit": "REPORTED", "croit": "UNKNOWN"}[verb]
        if index.event_for(_complement(frame).id).occurrence_status.value != want:
            metrics["SUPPORTED_DRIFT"] += 1

    assert metrics["CASES"] >= 3000, metrics
    for key in ("UNRESOLVED_GOVERNOR_CASES", "PRESERVED_EMBEDDED_COMPLEMENTS", "SUPPORTED_GOVERNOR_CASES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("LOST_GOVERNOR_COMPLEMENT_PROMOTION", "UNSUPPORTED_GOVERNOR_ASSERTED_COMPLEMENT", "NEGATION_LOST",
                "CONDITION_LOST", "FUTURE_LOST", "FIRST_MATCH", "CRASH", "SUPPORTED_DRIFT"):
        assert metrics[key] == 0, (key, metrics)
