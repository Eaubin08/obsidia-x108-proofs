"""
tests/integration_cognition/test_native_fidelity_red.py

RED contracts from the independent audit of aab6f749:
  - a statement labelled NATIVE_REALIZATION must lose nothing (voice, reflexive,
    adverbs, restriction, epistemic markers);
  - realize_semantic_relation must limit mood/aspect/tense combinations it cannot
    realize and bare subjects whose number is ambiguous.
"""
from __future__ import annotations

import pytest

from periphery.language.lexical_corpus import DB_PATH, is_known_lexical_item
from periphery.language.native_realization import realize_semantic_relation as realize

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="linguistic corpus not built")


@pytest.mark.parametrize("stmt", [
    "La vanne est vérifiée.",                          # passive / state
    "Les pompes sont arrêtées.",
    "Le réacteur s'arrête.",                           # reflexive
    "Le moteur s'est arrêté.",
    "Les opérateurs se parlent.",
    "L'opérateur ne vérifie pas toujours la vanne.",   # negation scope
    "L'opérateur ne vérifie que la vanne.",            # restriction
    "Le technicien vérifie sans doute la vanne.",      # epistemic marker
    "L'opérateur vérifie encore la vanne.",            # adverb
    "L'opérateur vérifie déjà la vanne.",
])
def test_fidelity_lossy_statements_are_not_native(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    _text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    assert provenance != "NATIVE_VERIFIED_ECHO"


@pytest.mark.parametrize("stmt", [
    "Les opérateurs ne vérifiaient pas la vanne principale.",
    "L'opérateur vérifiera la vanne.",
    "Le technicien a lancé le test.",
    "Elle est venue.",
])
def test_fidelity_native_output_covers_every_input_token(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    if provenance == "NATIVE_VERIFIED_ECHO":
        assert text.lower() == stmt.rstrip(".").lower()


@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("Il", "finir", "le travail", {"lang": "fr", "mood": "subjunctive"}),          # no "que"
    ("Il", "finir", "le travail", {"lang": "fr", "tense": "subjunctive"}),
    ("L'opérateur", "vérifier", "la vanne", {"lang": "fr", "mood": "conditional", "aspect": "perfect"}),
    ("L'opérateur", "vérifier", "la vanne", {"lang": "fr", "mood": "subjunctive", "tense": "past"}),
    ("L'opérateur", "vérifier", "la vanne", {"lang": "fr", "tense": "compound_past", "aspect": "progressive"}),
    ("You", "check", "the valve", {"lang": "en", "mood": "imperative", "tense": "past"}),
    ("You", "check", "the valve", {"lang": "en", "mood": "imperative", "aspect": "perfect"}),
    ("Tu", "vérifier", "la vanne", {"lang": "fr", "mood": "imperative", "tense": "future"}),
    ("Paris", "être", "belle", {"lang": "fr"}),                                     # "paris" = plural of pari
    ("Fils", "arriver", "", {"lang": "fr"}),                                        # sg/pl ambiguous
    ("Wales", "be", "small", {"lang": "en"}),
    ("Sheep", "eat", "grass", {"lang": "en"}),
])
def test_fidelity_unrealizable_combinations_are_limited(subject, verb, obj, kw):
    assert realize(subject=subject, verb_lemma=verb, obj=obj, **kw)["has_linguistic_limitations"] is True


def test_fidelity_subjunctive_after_que_is_realized():
    res = realize(subject="Qu'il", verb_lemma="finir", obj="le travail", lang="fr", mood="subjunctive")
    assert res["text"] == "Qu'il finisse le travail." and res["has_linguistic_limitations"] is False


@pytest.mark.parametrize("word", ["don't", "cannot", "won't", "isn't"])
def test_fidelity_english_contractions_are_known(word):
    assert is_known_lexical_item(word, lang="en") is True


def test_fidelity_answer_level_is_not_reconstruction_when_wording_is_auxiliary():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer

    ctx = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": "The operator checks the valve.",
            "evidence_only": True,
            "provider": "QWEN_LOCAL",
        },
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    res = build_true_brody_answer(user_message="What does the operator do?", language="en", brody_full_context=ctx)
    prov = res["formulation_provenance"]
    assert prov and all(p == "AUXILIARY_WORDING_PRESERVED" for p in prov)
    assert res["native_linguistic_level"] == "AUXILIARY_WORDING_PRESERVED"


def test_fidelity_noun_complement_outside_object_is_not_dropped():
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance("L'opérateur vérifie la température du circuit.", fr=True)
    assert provenance != "NATIVE_VERIFIED_ECHO" or "du circuit" in text


# Third audit (1970d041): set-based coverage and punctuation --------------------

@pytest.mark.parametrize("stmt", [
    "Le technicien vérifie la vanne A.",
    "Le technicien vérifie la vanne a.",
    "Le technicien vérifie la vanne « A ».",
    "Le technicien vérifie la vanne ont.",
    "Le technicien a vérifié la vanne a.",
    "Le technicien vérifie -3 vannes.",
    "Le technicien vérifie 3,5 vannes.",
    "Le technicien vérifie la vanne + pompe.",
    "Le technicien vérifie la vanne : non.",
    "Le technicien vérifie la vanne (principale).",
    "Le technicien vérifie la vanne V-12.",
    "Le technicien vérifie la vanne n° 3.",
    "Le technicien vérifie la vanne #2.",
])
def test_fidelity_identifiers_and_symbols_are_never_lost(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    assert provenance != "NATIVE_VERIFIED_ECHO", text


@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("People", "arrive", "", {"lang": "en"}),
    ("The people", "arrive", "", {"lang": "en"}),
    ("Fish", "swim", "", {"lang": "en"}),
    ("Fish", "swim", "", {"lang": "en", "tense": "past", "aspect": "progressive"}),
    ("La plupart", "manger", "", {"lang": "fr"}),
    ("Le technicien", "vérifier", "la vanne", {"lang": "fr", "mood": "conditional", "aspect": "progressive"}),
    ("Elle", "se laver", "les mains", {"lang": "fr", "tense": "past"}),
])
def test_fidelity_third_audit_false_confidence_is_limited_or_correct(subject, verb, obj, kw):
    expected = {
        ("La plupart", "manger"): "La plupart mangent.",
        ("Elle", "se laver"): "Elle s'est lavé les mains.",
    }.get((subject, verb))
    res = realize(subject=subject, verb_lemma=verb, obj=obj, **kw)
    assert res["has_linguistic_limitations"] is True or (expected and res["text"] == expected), res["text"]


@pytest.mark.parametrize("word", ["when", "how", "where", "don’t", "I'll", "let's", "he's", "you've"])
def test_fidelity_more_english_closed_class_words_are_known(word):
    assert is_known_lexical_item(word, lang="en") is True


# Fourth audit (53b40359): case of identifiers, honest label, residual limits ----

@pytest.mark.parametrize("stmt", [
    "Le technicien vérifie la pompe B.",
    "Le technicien vérifie le réseau Alpha.",
    "Le technicien vérifie la vanne ALPHA.",
])
def test_fidelity_identifier_case_is_preserved_exactly(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    if provenance == "NATIVE_VERIFIED_ECHO":
        assert text == stmt.rstrip(".")


def test_fidelity_native_provenance_is_named_as_verified_echo():
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    _text, provenance = _reconstruct_with_provenance("L'opérateur vérifiera la vanne.", fr=True)
    assert provenance == "NATIVE_VERIFIED_ECHO"


@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("Le technicien", "vérifier", "la vanne", {"lang": "fr", "polarity": "question"}),
    ("Le technicien", "vérifier", "la vanne", {"lang": "fr", "polarity": "maybe"}),
    ("Le technicien", "vérifier", "la vanne", {"lang": "fr", "aspect": "foo"}),
    ("Personne", "vérifier", "la vanne", {"lang": "fr"}),
    ("Aucun technicien", "vérifier", "la vanne", {"lang": "fr", "polarity": "negative"}),
    ("Rien", "arriver", "", {"lang": "fr"}),
    ("Nobody", "check", "the valve", {"lang": "en", "polarity": "negative"}),
    ("Ils", "se parler", "", {"lang": "fr", "tense": "past"}),
    ("Le technicien", "monter", "la valise", {"lang": "fr", "tense": "past"}),
    ("Le technicien", "sortir", "la poubelle", {"lang": "fr", "tense": "past"}),
    ("The United States", "be", "large", {"lang": "en"}),
    ("Le technicien", "vérifier", "la vanne", {"lang": "fr", "number": "pl"}),
    ("I", "check", "the valve", {"lang": "en", "person": "3"}),
])
def test_fidelity_fourth_audit_cases_are_limited(subject, verb, obj, kw):
    assert realize(subject=subject, verb_lemma=verb, obj=obj, **kw)["has_linguistic_limitations"] is True


# Fifth audit (acb6396d): ungrammatical subjects never verified -------------------

@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("The operators", "check", "the valve", {"lang": "en", "number": "sg"}),
    ("Elle", "venir", "", {"lang": "fr", "tense": "past", "gender": "masc"}),
    ("Le opérateur", "vérifier", "la vanne", {"lang": "fr"}),
    ("Le opérateur", "arriver", "", {"lang": "fr", "tense": "past"}),
    ("Le arbre", "tomber", "", {"lang": "fr"}),
    ("Ce", "être", "vrai", {"lang": "fr"}),
    ("La homme", "tomber", "", {"lang": "fr"}),
    ("Les", "vérifier", "la vanne", {"lang": "fr"}),
    ("The", "check", "the valve", {"lang": "en"}),
    ("Who", "check", "the valve", {"lang": "en"}),
    ("L'opérateur", "vérifier", "aucune vanne", {"lang": "fr"}),
])
def test_fidelity_fifth_audit_cases_are_limited(subject, verb, obj, kw):
    assert realize(subject=subject, verb_lemma=verb, obj=obj, **kw)["has_linguistic_limitations"] is True


@pytest.mark.parametrize("subject,expected", [
    ("The pump B", "The pump B runs."),
    ("Pump B", "Pump B runs."),
])
def test_fidelity_trailing_identifier_does_not_hide_the_head_noun(subject, expected):
    res = realize(subject=subject, verb_lemma="run", obj="", lang="en")
    assert res["text"] == expected or res["has_linguistic_limitations"] is True


@pytest.mark.parametrize("stmt", ["Le opérateur vérifie la vanne.", "La opérateur vérifie la vanne.",
                                  "L'opérateur vérifie aucune vanne."])
def test_fidelity_ungrammatical_statement_is_never_a_verified_echo(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    assert _reconstruct_with_provenance(stmt, fr=True)[1] != "NATIVE_VERIFIED_ECHO"


# Closure audit (15239e1c): positive noun-phrase verification ---------------------

@pytest.mark.parametrize("stmt", [
    "Le homme vérifie la vanne.", "La heure passe.", "L'haie pousse.", "Les opérateur vérifient la vanne.",
    "Des opérateur vérifient la vanne.", "L'opérateur vérifie les vanne.", "L'opérateur vérifie la hélice.",
    "L'opérateur vérifie le homme.", "L'opérateur ne vérifie pas aucune vanne.", "Quel opérateur vérifie la vanne.",
    "Ce vanne fuit.", "Cette chat mange.", "Mon vanne fuit.",
])
def test_closure_ungrammatical_statements_are_never_verified_echoes(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    assert _reconstruct_with_provenance(stmt, fr=True)[1] != "NATIVE_VERIFIED_ECHO"


@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("Le homme", "tomber", "", {"lang": "fr"}), ("Le hôpital", "fermer", "", {"lang": "fr"}),
    ("L'héros", "arriver", "", {"lang": "fr"}), ("Les opérateur", "vérifier", "la vanne", {"lang": "fr"}),
    ("Ces chat", "manger", "", {"lang": "fr"}), ("Ce vanne", "fuir", "", {"lang": "fr"}),
    ("Cet chat", "manger", "", {"lang": "fr"}), ("Ma chat", "manger", "", {"lang": "fr"}),
    ("A operator", "check", "the valve", {"lang": "en"}), ("These operator", "check", "the valve", {"lang": "en"}),
    ("The operator", "check", "no valve", {"lang": "en", "polarity": "negative"}),
    ("L'opérateur", "vérifier", "aucune vanne", {"lang": "fr", "polarity": "negative"}),
    ("Quel opérateur", "vérifier", "la vanne", {"lang": "fr"}), ("Whose operator", "check", "the valve", {"lang": "en"}),
    ("L'opérateur", "vérifier", "la hélice", {"lang": "fr"}),
])
def test_closure_unverifiable_phrases_are_limited(subject, verb, obj, kw):
    assert realize(subject=subject, verb_lemma=verb, obj=obj, **kw)["has_linguistic_limitations"] is True


@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("Le chat", "manger", "la souris", {"lang": "fr"}, "Le chat mange la souris."),
    ("Le yaourt", "tomber", "", {"lang": "fr"}, "Le yaourt tombe."),
    ("Le chat", "manger", "le yaourt", {"lang": "fr"}, "Le chat mange le yaourt."),
    ("L'opérateur", "vérifier", "la vanne", {"lang": "fr"}, "L'opérateur vérifie la vanne."),
    ("Les opérateurs", "vérifier", "la vanne", {"lang": "fr"}, "Les opérateurs vérifient la vanne."),
    ("Cet arbre", "tomber", "", {"lang": "fr"}, "Cet arbre tombe."),
    ("Ma voiture", "rouler", "", {"lang": "fr"}, "Ma voiture roule."),
    ("The pumps", "need", "maintenance", {"lang": "en"}, "The pumps need maintenance."),
])
def test_closure_correct_simple_sentences_are_not_over_limited(subject, verb, obj, kw, expected):
    res = realize(subject=subject, verb_lemma=verb, obj=obj, **kw)
    assert res["text"] == expected and res["has_linguistic_limitations"] is False


# Closure audit 2 (571d9007): closed-world phrase verification -------------------

@pytest.mark.parametrize("stmt", [
    "L'opérateur vérifie au chat.", "L'opérateur vérifie deux vanne.", "Opérateur vérifie la vanne.",
    "L'opérateur vérifie vanne.", "L'opérateur vérifie pierre.",
])
def test_closure2_ungrammatical_statements_are_never_verified_echoes(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    assert _reconstruct_with_provenance(stmt, fr=True)[1] != "NATIVE_VERIFIED_ECHO"


@pytest.mark.parametrize("subject,verb,obj,kw", [
    ("De le vanne", "tomber", "", {"lang": "fr"}), ("De la eau", "tomber", "", {"lang": "fr"}),
    ("Au chat", "tomber", "", {"lang": "fr"}), ("Aux chats", "tomber", "", {"lang": "fr"}),
    ("Deux chat", "tomber", "", {"lang": "fr"}), ("Chaque chats", "tomber", "", {"lang": "fr"}),
    ("Tous les vannes", "tomber", "", {"lang": "fr"}), ("Plusieurs chat", "tomber", "", {"lang": "fr"}),
    ("Chat", "tomber", "", {"lang": "fr"}), ("Opérateur", "tomber", "", {"lang": "fr"}),
    ("L'opérateur", "vérifier", "de la eau", {"lang": "fr"}), ("L'opérateur", "vérifier", "de le pain", {"lang": "fr"}),
    ("L'opérateur", "vérifier", "deux vanne", {"lang": "fr"}), ("L'opérateur", "vérifier", "pierre", {"lang": "fr"}),
    ("Two valve", "fail", "", {"lang": "en"}), ("Many valve", "fail", "", {"lang": "en"}),
])
def test_closure2_unverified_phrases_are_limited(subject, verb, obj, kw):
    assert realize(subject=subject, verb_lemma=verb, obj=obj, **kw)["has_linguistic_limitations"] is True


@pytest.mark.parametrize("subject,verb,obj,kw,expected", [
    ("Deux chats", "tomber", "", {"lang": "fr"}, "Deux chats tombent."),
    ("Tous les chats", "tomber", "", {"lang": "fr"}, "Tous les chats tombent."),
    ("Chaque chat", "tomber", "", {"lang": "fr"}, "Chaque chat tombe."),
    ("L'opérateur", "vérifier", "deux vannes", {"lang": "fr"}, "L'opérateur vérifie deux vannes."),
    ("Je", "s'occuper", "du dossier", {"lang": "fr"}, "Je m'occupe du dossier."),
    ("Two valves", "fail", "", {"lang": "en"}, "Two valves fail."),
    ("Brody", "analyser", "le signal", {"lang": "fr"}, "Brody analyse le signal."),
])
def test_closure2_verified_phrases_stay_confident(subject, verb, obj, kw, expected):
    res = realize(subject=subject, verb_lemma=verb, obj=obj, **kw)
    assert res["text"] == expected and res["has_linguistic_limitations"] is False


# Closure audit 3 (e9ae36a4): narrow echo policy on the public path ---------------

@pytest.mark.parametrize("stmt", [
    "L'opérateur vérifie rouge.", "L'opérateur vérifie grand.", "L'opérateur vérifie ouvertes.",
    "L'opérateur vérifie Chat.", "Il pleut la vanne.", "L'opérateur vérifie Le Chat.",
    "L'opérateur vérifie la Vanne.", "L'OPÉRATEUR VÉRIFIE LA VANNE.", "L'opérateur Vérifie la vanne.",
])
def test_closure3_echo_requires_verified_noun_phrases_and_plain_case(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    assert _reconstruct_with_provenance(stmt, fr=True)[1] != "NATIVE_VERIFIED_ECHO"


@pytest.mark.parametrize("stmt", [
    "Les opérateurs ne vérifiaient pas la vanne principale.", "L'opérateur vérifiera les vannes.",
    "Le technicien a lancé le test.",
])
def test_closure3_verified_echoes_still_pass(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    assert _reconstruct_with_provenance(stmt, fr=True)[1] == "NATIVE_VERIFIED_ECHO"
