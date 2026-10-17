"""
tests/integration_cognition/test_linguistic_closure_red.py

RED contracts for the 12 false-confidence outputs found by the independent
certification of 787a74fb, and for the adapter temporal mapping. Each case
must end either in a correct realization or in an explicit limitation.
"""
from __future__ import annotations

import pytest

from periphery.language.lexical_corpus import DB_PATH, is_known_lexical_item
from periphery.language.native_realization import realize_semantic_relation as realize

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="linguistic corpus not built")


def _r(subject, verb, obj="", **kw):
    return realize(subject=subject, verb_lemma=verb, obj=obj, **kw)


def _correct_or_limited(res, expected):
    assert res["text"] == expected or res["has_linguistic_limitations"] is True, res


# 1-4, 7. French subject elision and spacing ------------------------------------

@pytest.mark.parametrize("verb,obj,kw,expected", [
    ("aimer", "le café", {}, "J'aime le café."),
    ("avoir", "faim", {}, "J'ai faim."),
    ("avoir", "faim", {"tense": "past"}, "J'ai eu faim."),
    ("écouter", "la radio", {}, "J'écoute la radio."),
    ("écouter", "", {}, "J'écoute."),
])
def test_close_fr_subject_elision(verb, obj, kw, expected):
    res = _r("Je", verb, obj, lang="fr", **kw)
    assert res["text"] == expected
    assert res["has_linguistic_limitations"] is False


# 8. No space after an elided clitic ------------------------------------------

def test_close_fr_no_space_after_elided_clitic():
    res = _r("Il", "s'arrêter", "", lang="fr", tense="past", polarity="negative")
    assert res["text"] == "Il ne s'est pas arrêté."
    assert "' " not in res["text"]


# 6. Imperative ----------------------------------------------------------------

@pytest.mark.parametrize("subject,expected", [
    ("Tu", "Vérifie la vanne."),
    ("Vous", "Vérifiez la vanne."),
    ("Nous", "Vérifions la vanne."),
])
def test_close_fr_imperative_drops_subject(subject, expected):
    res = _r(subject, "vérifier", "la vanne", lang="fr", mood="imperative")
    assert res["text"] == expected
    assert res["has_linguistic_limitations"] is False


def test_close_fr_third_person_imperative_is_limited():
    assert _r("L'opérateur", "vérifier", "la vanne", lang="fr", mood="imperative")["has_linguistic_limitations"] is True


def test_close_en_imperative_drops_subject():
    res = _r("You", "check", "the valve", lang="en", mood="imperative")
    assert res["text"] == "Check the valve."


# 5, 10. Bare nominal subjects -------------------------------------------------

def test_close_fr_bare_plural_subject():
    _correct_or_limited(_r("Opérateurs", "vérifier", "la vanne", lang="fr"), "Opérateurs vérifient la vanne.")
    assert _r("Opérateurs", "vérifier", "la vanne", lang="fr")["text"] != "Opérateurs vérifie la vanne."


def test_close_en_bare_plural_subject():
    res = _r("Operators", "check", "the valve", lang="en")
    _correct_or_limited(res, "Operators check the valve.")
    assert res["text"] != "Operators checks the valve." or res["has_linguistic_limitations"] is True


def test_close_proper_noun_subject_stays_singular_and_confident():
    res = _r("Brody", "analyser", "le signal", lang="fr")
    assert res["text"] == "Brody analyse le signal." and res["has_linguistic_limitations"] is False


# 9, 12. English future and conditional ----------------------------------------

@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("The operator", "check", "the valve", {"tense": "future"}, "The operator will check the valve."),
    ("The operator", "check", "the valve", {"tense": "future", "polarity": "negative"},
     "The operator will not check the valve."),
    ("He", "go", "home", {"mood": "conditional"}, "He would go home."),
    ("The pumps", "be", "ready", {"tense": "future"}, "The pumps will be ready."),
])
def test_close_en_future_and_conditional(subject, verb, obj, kw, expected):
    res = _r(subject, verb, obj, lang="en", **kw)
    assert res["text"] == expected
    assert res["has_linguistic_limitations"] is False


# 11. English negative questions -----------------------------------------------

@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("The operator", "check", "the valve", {}, "Does the operator not check the valve?"),
    ("The pump", "be", "ready", {}, "Is the pump not ready?"),
    ("She", "write", "a letter", {"tense": "past"}, "Did she not write a letter?"),
])
def test_close_en_negative_questions(subject, verb, obj, kw, expected):
    res = _r(subject, verb, obj, lang="en", mood="interrogative", polarity="negative", **kw)
    assert res["text"] == expected


# Unsupported cells are limited, never silently degraded ------------------------

def test_close_unsupported_tense_is_limited():
    assert _r("L'opérateur", "vérifier", "la vanne", lang="fr", tense="pluperfect")["has_linguistic_limitations"] is True
    assert _r("The operator", "check", "the valve", lang="en", tense="pluperfect")["has_linguistic_limitations"] is True


# is_known_lexical_item noise ---------------------------------------------------

@pytest.mark.parametrize("word,lang,expected", [
    ("cheval", "en", False),
    ("ciel", "en", False),
    ("countable", "en", True),   # genuine adjective, must stay known
    ("house", "en", True),
    ("maison", "fr", True),
])
def test_close_is_known_filters_cross_language_noise(word, lang, expected):
    assert is_known_lexical_item(word, lang=lang) is expected


def test_close_defective_rows_are_never_attested_analyses():
    from periphery.language.lexical_corpus import is_defective_analysis, lookup_surface_form

    # "st" is a genuine noun (stère abbreviation) but not a form of "être".
    st = lookup_surface_form("st", lang="fr")
    assert any(a.lemma == "st" and not is_defective_analysis(a) for a in st)
    assert all(is_defective_analysis(a) for a in st if a.lemma == "être")
    has = [a for a in lookup_surface_form("has", lang="en") if a.tense == "past"]
    assert has and all(is_defective_analysis(a) for a in has)
    assert all(is_defective_analysis(a) for a in lookup_surface_form("countable", lang="en") if a.pos == "noun")


# Adapter temporal mapping ------------------------------------------------------

def test_close_adapter_maps_tense_without_collapsing_to_past():
    from apps.obsidia_api.brody_true_voice_adapter import _sens_tense_to_realization

    assert _sens_tense_to_realization("PRESENT", "FINITE", "vérifie", "vérifier")["tense"] == "present"
    assert _sens_tense_to_realization("FUTURE", "FINITE", "vérifiera", "vérifier")["tense"] == "future"
    assert _sens_tense_to_realization("CONDITIONAL", "FINITE", "vérifierait", "vérifier")["mood"] == "conditional"
    assert _sens_tense_to_realization("PAST", "PARTICIPLE", "vérifié", "vérifier")["tense"] == "compound_past"
    assert _sens_tense_to_realization("PAST", "FINITE", "vérifiait", "vérifier")["tense"] == "imperfect"
    assert _sens_tense_to_realization("PAST", "FINITE", "vérifia", "vérifier")["tense"] == "simple_past"
    for unsupported in ("PLUPERFECT", "NEAR_FUTURE", "RECENT_PAST", "AVERTED", "NONE"):
        assert _sens_tense_to_realization(unsupported, "FINITE", "x", "vérifier") is None
