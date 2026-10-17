"""
tests/integration_cognition/test_linguistic_minimum_red.py

RED contracts for the minimum linguistic repair demonstrated by the
independent audit of dbde01b5:
  A. subject/verb agreement is derived from the subject (FR/EN);
  B. French generic "past" is the passé composé, other tenses stay distinct;
  C. any uncertain or synthesized realization is declared as limited;
  D. synonym groups and translation glosses are never exposed as definitions,
     and no lexical entry is presented as a verified fact.
"""
from __future__ import annotations

import pytest

from periphery.language.lexical_corpus import DB_PATH, get_senses_and_synonyms
from periphery.language.native_realization import realize_semantic_relation as realize

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="linguistic corpus not built")


def _r(subject, verb, obj="", **kw):
    return realize(subject=subject, verb_lemma=verb, obj=obj, **kw)


# A. Agreement -----------------------------------------------------------------

@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("Nous", "être", "prêts", {"lang": "fr"}, "Nous sommes prêts."),
    ("Les opérateurs", "vérifier", "la vanne", {"lang": "fr"}, "Les opérateurs vérifient la vanne."),
    ("Je", "finir", "le rapport", {"lang": "fr"}, "Je finis le rapport."),
    ("Le capteur et la sonde", "mesurer", "la pression", {"lang": "fr"}, "Le capteur et la sonde mesurent la pression."),
    ("They", "be", "ready", {"lang": "en", "polarity": "negative"}, "They are not ready."),
    ("I", "be", "ready", {"lang": "en"}, "I am ready."),
    ("The pumps", "need", "maintenance", {"lang": "en"}, "The pumps need maintenance."),
    ("The operator", "check", "the valve", {"lang": "en"}, "The operator checks the valve."),
    ("The pumps", "be", "offline", {"lang": "en", "tense": "past"}, "The pumps were offline."),
])
def test_min_a_agreement_from_subject(subject, verb, obj, kw, expected):
    res = _r(subject, verb, obj, **kw)
    assert res["text"] == expected
    assert res["has_linguistic_limitations"] is False


def test_min_a_unattested_subject_head_is_limited_not_guessed():
    # "operators" is not attested in the corpus: number cannot be established.
    res = _r("The operators", "check", "the valve", lang="en")
    assert res["has_linguistic_limitations"] is True
    assert "AGREEMENT" in (res["limitation_reason"] or "")


def test_min_a_explicit_person_number_still_override():
    res = _r("Ils", "vérifier", "la vanne", lang="fr", person="3", number="sg")
    assert res["text"] == "Ils vérifie la vanne."


# B. Tenses --------------------------------------------------------------------

@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("Les opérateurs", "vérifier", "la vanne", {"lang": "fr", "tense": "past", "polarity": "negative"},
     "Les opérateurs n'ont pas vérifié la vanne."),
    ("Elle", "venir", "à la maison", {"lang": "fr", "tense": "past"}, "Elle est venue à la maison."),
    ("Ils", "partir", "", {"lang": "fr", "tense": "past"}, "Ils sont partis."),
    ("Le chat", "manger", "la souris", {"lang": "fr", "tense": "imperfect"}, "Le chat mangeait la souris."),
    ("Le chat", "manger", "la souris", {"lang": "fr", "tense": "simple_past"}, "Le chat mangea la souris."),
    ("Nous", "aller", "à Paris", {"lang": "fr", "tense": "future"}, "Nous irons à Paris."),
    ("The child", "go", "to school", {"lang": "en", "tense": "past"}, "The child went to school."),
    ("She", "write", "a letter", {"lang": "en", "tense": "past", "polarity": "negative"}, "She did not write a letter."),
])
def test_min_b_tenses_and_irregulars(subject, verb, obj, kw, expected):
    res = _r(subject, verb, obj, **kw)
    assert res["text"] == expected
    assert res["has_linguistic_limitations"] is False


# C. Explicit limitations ------------------------------------------------------

def test_min_c_etre_auxiliary_with_unknown_gender_is_limited():
    # "L'équipe" carries no gender in its determiner: participle agreement is uncertain.
    res = _r("L'équipe", "arriver", "", lang="fr", tense="past")
    assert res["has_linguistic_limitations"] is True
    assert "AGREEMENT" in (res["limitation_reason"] or "")


def test_min_c_unknown_verb_is_limited_fr_and_en():
    assert _r("Le système", "zorbifier", "la vanne", lang="fr")["has_linguistic_limitations"] is True
    assert _r("The system", "zorbify", "the valve", lang="en", tense="past")["has_linguistic_limitations"] is True


def test_min_c_unknown_verb_in_compound_and_progressive_is_limited():
    assert _r("Le système", "zorbifier", "", lang="fr", tense="past")["has_linguistic_limitations"] is True
    assert _r("The system", "zorbify", "", lang="en", aspect="progressive")["has_linguistic_limitations"] is True
    assert _r("The system", "zorbify", "", lang="en", aspect="perfect")["has_linguistic_limitations"] is True


def test_min_c_never_world_fact_and_kx108_only():
    res = _r("Nous", "être", "prêts", lang="fr")
    assert res["is_world_fact_established"] is False
    assert res["decision_authority"] == "KX108_ONLY"


# D. Definitions vs synonym groups vs glosses ----------------------------------

def test_min_d_sense_kinds_are_separated():
    senses = get_senses_and_synonyms("maison", lang="fr")
    kinds = {s.source_id: s.kind for s in senses}
    assert kinds["xmlittre_fr"] == "definition"
    assert kinds["thes_fr"] == "synonym_group"
    assert kinds["freedict_fra_eng"] == "translation_gloss"


def test_min_d_synonym_groups_and_glosses_carry_no_definition_text():
    for s in get_senses_and_synonyms("maison", lang="fr"):
        if s.kind != "definition":
            assert s.definition == "", f"{s.source_id} exposes a pseudo-definition: {s.definition!r}"
    glosses = [s for s in get_senses_and_synonyms("pomme", lang="fr") if s.kind == "translation_gloss"]
    assert glosses and glosses[0].gloss == "apple"


def test_min_d_no_lexical_entry_is_a_verified_fact():
    for lemma, lang in (("maison", "fr"), ("house", "en")):
        for s in get_senses_and_synonyms(lemma, lang=lang):
            d = s.to_dict()
            assert d["verified_fact"] is False
            assert d["kind"] in ("definition", "synonym_group", "translation_gloss")


# E. Questions keep a lowercase function-word subject and French elision --------

@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("Tu", "avoir", "raison", {"lang": "fr", "mood": "interrogative"}, "Est-ce que tu as raison ?"),
    ("Il", "venir", "", {"lang": "fr", "mood": "interrogative"}, "Est-ce qu'il vient ?"),
    ("Brody", "analyser", "le signal", {"lang": "fr", "mood": "interrogative"}, "Est-ce que Brody analyse le signal ?"),
    ("The child", "go", "to school", {"lang": "en", "mood": "interrogative"}, "Does the child go to school?"),
])
def test_min_e_questions(subject, verb, obj, kw, expected):
    assert _r(subject, verb, obj, **kw)["text"] == expected
