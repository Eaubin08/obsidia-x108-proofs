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
    assert provenance != "NATIVE_REALIZATION"


@pytest.mark.parametrize("stmt", [
    "Les opérateurs ne vérifiaient pas la vanne principale.",
    "L'opérateur vérifiera la vanne.",
    "Le technicien a lancé le test.",
    "Elle est venue.",
])
def test_fidelity_native_output_covers_every_input_token(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    if provenance == "NATIVE_REALIZATION":
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
    assert provenance != "NATIVE_REALIZATION" or "du circuit" in text


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
    assert provenance != "NATIVE_REALIZATION", text


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
