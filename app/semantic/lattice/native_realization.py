"""
app/semantic/lattice/native_realization.py

Brody Native Realization Layer.
Transforms structured semantic relations (subject, predicate, object, polarity, modality, tense, aspect)
into grammatical, conjugated, natural sentences in Brody's voice using real lexical and
morphological corpora.

Constraints:
- Consults real grammatical lookups (lexical_corpus.py) without asking Qwen.
- Never promotes dictionary entries to established world facts.
- Respects agreement, number, person, tense, aspect, and mood.
- Correctly realizes irregular verbs (être, avoir, aller, faire, prendre, venir, pouvoir, devoir, vouloir, tenir, be, have, do, go, write, see, read, run, take).
- Handles compound tenses (passé composé, perfect aspect) and auxiliary selection (avoir/être).
- Handles pronominal and reflexive verbs with elision (se souvenir, s'arrêter).
- Preserves negation ("ne ... pas", "n'...") and modality (conditional mood, interrogatives).
- Flags unsupported grammatical structures with explicit linguistic limitations.
"""
from __future__ import annotations

import re
from typing import Any

from app.semantic.lattice.lexical_corpus import (
    lookup_surface_form,
    realize_inflection,
    is_known_lexical_item,
)

_VOWELS = frozenset("aeiouyàâäéèêëîïôöùûühAEIOUYÀÂÄÉÈÊËÎÏÔÖÙÛÜH")

_ETRE_VERBS = frozenset({
    "aller", "venir", "revenir", "devenir", "partir", "arriver",
    "entrer", "sortir", "monter", "descendre", "naître", "mourir",
    "rester", "tomber", "retourner",
})


def _apply_french_elision(prefix: str, following_word: str) -> str:
    """Applies French phonetic elision (le -> l', de -> d', ne -> n', que -> qu', se -> s')."""
    if not following_word:
        return prefix
    first_char = following_word[0]
    is_vowel_onset = first_char in _VOWELS

    p_low = prefix.lower().strip()
    if is_vowel_onset:
        if p_low in ("le", "la"):
            return "l'"
        if p_low == "de":
            return "d'"
        if p_low == "ne":
            return "n'"
        if p_low == "que":
            return "qu'"
        if p_low == "ce":
            return "c'"
        if p_low == "se":
            return "s'"
        if p_low == "me":
            return "m'"
        if p_low == "te":
            return "t'"
    return prefix + " "


def realize_semantic_relation(
    subject: str,
    verb_lemma: str,
    obj: str = "",
    *,
    mood: str = "indicative",
    tense: str = "present",
    aspect: str = "simple",
    is_pronominal: bool = False,
    polarity: str = "affirmative",
    person: str = "3",
    number: str = "sg",
    gender: str = "masc",
    lang: str = "fr",
) -> dict[str, Any]:
    """
    Realizes a structured semantic proposition into a grammatical sentence.

    Parameters:
      subject: Grammatical subject (e.g. "L'opérateur", "The operator")
      verb_lemma: Canonical verb lemma (e.g. "vérifier", "prendre", "check", "run")
      obj: Complement or object (e.g. "la vanne", "the valve", "300 K")
      mood: "indicative", "conditional", "subjunctive", "imperative", "interrogative"
      tense: "present", "past", "future", "imperfect", "simple_past", "compound_past", "passé_composé"
      aspect: "simple", "progressive", "continuous", "perfect"
      is_pronominal: Whether the verb is used pronominally/reflexively (e.g. se souvenir, s'arrêter)
      polarity: "affirmative" or "negative"
      person: "1", "2", "3"
      number: "sg", "pl"
      gender: "masc", "fem"
      lang: "fr" or "en"

    Returns:
      Dict with realized text, metadata, and limitation flags.
    """
    clean_subj = (subject or "").strip()
    clean_verb = (verb_lemma or "").strip()
    clean_obj = (obj or "").strip()
    is_fr = (lang or "fr").lower().startswith("fr")

    if not clean_verb:
        return {
            "text": "",
            "realized_verb": "",
            "verb_lemma": "",
            "has_linguistic_limitations": True,
            "limitation_reason": "EMPTY_VERB_LEMMA",
        }

    # Interrogative mood maps to indicative verb with interrogative sentence structure
    actual_mood = mood.lower()
    is_question = False
    if actual_mood in ("interrogative", "question"):
        actual_mood = "indicative"
        is_question = True

    # Check if verb is pronominal
    refl = is_pronominal or clean_verb.lower().startswith("se ") or clean_verb.lower().startswith("s'")
    if clean_verb.lower().startswith("se "):
        clean_verb = clean_verb[3:].strip()
    elif clean_verb.lower().startswith("s'"):
        clean_verb = clean_verb[2:].strip()

    is_compound = tense.lower() in ("compound_past", "passé_composé", "perfect") or aspect.lower() == "perfect"
    is_progressive = aspect.lower() in ("progressive", "continuous")
    is_neg = (polarity or "").lower() in ("negative", "negated")

    has_limitation = False
    limitation_reason = None
    realized_v = ""

    if is_fr:
        # Reflexive pronoun resolution
        refl_pron_map = {
            ("1", "sg"): "me", ("2", "sg"): "te", ("3", "sg"): "se",
            ("1", "pl"): "nous", ("2", "pl"): "vous", ("3", "pl"): "se",
        }
        refl_pron = refl_pron_map.get((str(person), number.lower()), "se") if refl else ""

        if is_compound:
            # Compound tense (passé composé)
            aux_lemma = "être" if (refl or clean_verb.lower() in _ETRE_VERBS) else "avoir"
            aux_form = realize_inflection(aux_lemma, pos="verb", mood="indicative", tense="present", person=person, number=number.lower(), lang="fr") or "a"
            pp_gender = gender.lower() if aux_lemma == "être" else ""
            pp_number = number.lower() if aux_lemma == "être" else "sg"
            pp_form = realize_inflection(clean_verb, pos="verb", mood="participle", tense="past", gender=pp_gender, number=pp_number, lang="fr")
            if not pp_form:
                has_limitation = True
                limitation_reason = f"UNKNOWN_PARTICIPLE:{clean_verb}"
                pp_form = clean_verb

            if refl:
                refl_elided = _apply_french_elision(refl_pron, aux_form)
                if is_neg:
                    ne_elided = _apply_french_elision("ne", refl_elided)
                    vp = f"{ne_elided}{refl_elided.strip()} {aux_form} pas {pp_form}"
                else:
                    vp = f"{refl_elided}{aux_form} {pp_form}"
            else:
                if is_neg:
                    ne_elided = _apply_french_elision("ne", aux_form)
                    vp = f"{ne_elided}{aux_form} pas {pp_form}"
                else:
                    vp = f"{aux_form} {pp_form}"
            realized_v = vp

        elif is_progressive:
            # Progressive aspect: être en train de + INF
            aux_be = realize_inflection("être", pos="verb", mood="indicative", tense=tense.lower(), person=person, number=number.lower(), lang="fr") or "est"
            de_elided = _apply_french_elision("de", clean_verb)
            if is_neg:
                ne_elided = _apply_french_elision("ne", aux_be)
                vp = f"{ne_elided}{aux_be} pas en train {de_elided}{clean_verb}"
            else:
                vp = f"{aux_be} en train {de_elided}{clean_verb}"
            realized_v = vp

        else:
            # Simple tenses
            simple_v = realize_inflection(
                clean_verb,
                pos="verb",
                mood=actual_mood,
                tense=tense.lower(),
                person=person,
                number=number.lower(),
                gender=gender.lower(),
                lang="fr",
            )
            if not simple_v:
                if not is_known_lexical_item(clean_verb, lang="fr"):
                    has_limitation = True
                    limitation_reason = f"UNKNOWN_LEXICAL_ITEM:{clean_verb}"
                    simple_v = clean_verb
                else:
                    has_limitation = True
                    limitation_reason = f"UNSUPPORTED_CONJUGATION_CELL:{clean_verb}:{actual_mood}:{tense}:{person}:{number}"
                    simple_v = clean_verb

            if refl:
                refl_elided = _apply_french_elision(refl_pron, simple_v)
                if is_neg:
                    ne_elided = _apply_french_elision("ne", refl_elided)
                    vp = f"{ne_elided}{refl_elided.strip()} {simple_v} pas"
                else:
                    vp = f"{refl_elided}{simple_v}"
            else:
                if is_neg:
                    ne_elided = _apply_french_elision("ne", simple_v)
                    vp = f"{ne_elided}{simple_v} pas"
                else:
                    vp = simple_v
            realized_v = vp

        if clean_subj:
            clause = f"{clean_subj} {vp}".strip()
        else:
            clause = vp

        if clean_obj:
            clause = f"{clause} {clean_obj}".strip()

        if is_question:
            text = f"Est-ce que {clause} ?"
            text = text[0].upper() + text[1:]
        else:
            text = clause[0].upper() + clause[1:] + "."

    else:
        # English realization
        if is_compound:
            aux_have = "had" if tense.lower() in ("past", "simple_past") else ("has" if person == "3" and number.lower() == "sg" else "have")
            pp_form = realize_inflection(clean_verb, pos="verb", mood="participle", tense="past", lang="en") or clean_verb
            if is_neg:
                vp = f"{aux_have} not {pp_form}"
            else:
                vp = f"{aux_have} {pp_form}"
            realized_v = vp

        elif is_progressive:
            past = tense.lower() in ("past", "simple_past")
            if past:
                aux_be = "was" if (person in ("1", "3") and number.lower() == "sg") else "were"
            else:
                aux_be = "am" if (person == "1" and number.lower() == "sg") else ("is" if (person == "3" and number.lower() == "sg") else "are")
            prp_form = realize_inflection(clean_verb, pos="verb", mood="participle", tense="present", lang="en") or f"{clean_verb}ing"
            if is_neg:
                vp = f"{aux_be} not {prp_form}"
            else:
                vp = f"{aux_be} {prp_form}"
            realized_v = vp

        else:
            simple_v = realize_inflection(
                clean_verb,
                pos="verb",
                mood=actual_mood,
                tense=tense.lower(),
                person=person,
                number=number.lower(),
                gender=gender.lower(),
                lang="en",
            )
            if not simple_v:
                if not is_known_lexical_item(clean_verb, lang="en"):
                    has_limitation = True
                    limitation_reason = f"UNKNOWN_LEXICAL_ITEM:{clean_verb}"
                    simple_v = clean_verb
                else:
                    has_limitation = True
                    limitation_reason = f"UNSUPPORTED_CONJUGATION_CELL:{clean_verb}:{actual_mood}:{tense}:{person}:{number}"
                    simple_v = clean_verb

            if is_neg:
                if clean_verb.lower() == "be":
                    neg_be = simple_v or "is"
                    vp = f"{neg_be} not"
                else:
                    aux_do = "did" if tense.lower() in ("past", "simple_past") else ("does" if person == "3" and number.lower() == "sg" else "do")
                    vp = f"{aux_do} not {clean_verb.lower()}"
            else:
                vp = simple_v
            realized_v = vp

        if is_question:
            if is_compound:
                aux_have = "had" if tense.lower() in ("past", "simple_past") else ("has" if person == "3" and number.lower() == "sg" else "have")
                pp_form = realize_inflection(clean_verb, pos="verb", mood="participle", tense="past", lang="en") or clean_verb
                text = f"{aux_have.capitalize()} {clean_subj} {pp_form} {clean_obj}?".strip()
            elif clean_verb.lower() == "be":
                be_form = realize_inflection("be", pos="verb", tense=tense.lower(), person=person, number=number.lower(), lang="en") or "is"
                text = f"{be_form.capitalize()} {clean_subj} {clean_obj}?".strip()
            else:
                aux_do = "did" if tense.lower() in ("past", "simple_past") else ("does" if person == "3" and number.lower() == "sg" else "do")
                infinitive = clean_verb.lower()
                clause = f"{aux_do.capitalize()} {clean_subj} {infinitive} {clean_obj}".strip()
                text = f"{clause}?"
        else:
            clause = f"{clean_subj} {vp} {clean_obj}".strip()
            text = clause[0].upper() + clause[1:] + "."

    return {
        "text": text,
        "realized_verb": realized_v,
        "verb_lemma": clean_verb,
        "subject": clean_subj,
        "object": clean_obj,
        "mood": mood,
        "tense": tense,
        "aspect": aspect,
        "is_pronominal": refl,
        "person": person,
        "number": number,
        "polarity": polarity,
        "lang": "fr" if is_fr else "en",
        "has_linguistic_limitations": has_limitation,
        "limitation_reason": limitation_reason,
        "decision_authority": "KX108_ONLY",
        "is_world_fact_established": False,
    }
