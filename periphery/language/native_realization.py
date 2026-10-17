"""
periphery/language/native_realization.py

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

from periphery.language.lexical_corpus import (
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


_FR_PRONOUNS: dict[str, tuple[str, str, str]] = {
    "je": ("1", "sg", ""), "j'": ("1", "sg", ""), "tu": ("2", "sg", ""),
    "il": ("3", "sg", "masc"), "elle": ("3", "sg", "fem"), "on": ("3", "sg", "masc"),
    "nous": ("1", "pl", ""), "vous": ("2", "pl", ""),
    "ils": ("3", "pl", "masc"), "elles": ("3", "pl", "fem"),
}
_FR_PLURAL_DETERMINERS = frozenset({
    "les", "des", "ces", "mes", "tes", "ses", "nos", "vos", "leurs", "plusieurs",
    "certains", "certaines", "quelques", "aux",
})
_FR_MASC_SG_DETERMINERS = frozenset({"le", "un", "ce", "cet", "mon", "ton", "son", "du", "au"})
_FR_FEM_SG_DETERMINERS = frozenset({"la", "une", "cette", "ma", "ta", "sa"})

_EN_PRONOUNS: dict[str, tuple[str, str]] = {
    "i": ("1", "sg"), "you": ("2", "pl"), "he": ("3", "sg"), "she": ("3", "sg"), "it": ("3", "sg"),
    "we": ("1", "pl"), "they": ("3", "pl"),
}
_EN_PLURAL_DETERMINERS = frozenset({"these", "those", "many", "several", "few", "both", "all"})
_EN_BE = {
    ("present", "1", "sg"): "am", ("present", "3", "sg"): "is",
    ("past", "1", "sg"): "was", ("past", "3", "sg"): "was",
}


def _head_noun_number(head: str, lang: str) -> str:
    """Number of a noun head from attested corpus analyses; "" when absent or ambiguous."""
    numbers = {a.number for a in lookup_surface_form(head, lang=lang) if a.pos == "noun" and a.number in ("sg", "pl")}
    return numbers.pop() if len(numbers) == 1 else ""


def _infer_subject_features(subject: str, is_fr: bool) -> tuple[str, str, str]:
    """Derive (person, number, gender) from the subject phrase.

    gender "" means unknown; number "" means the head noun is not attested, so
    agreement cannot be established from the corpus.
    """
    text = (subject or "").strip()
    low = text.lower()
    if not low:
        return "3", "sg", ""
    if re.search(r"\s(et|and)\s", low):
        return "3", "pl", ""
    tokens = re.findall(r"[\w'’-]+", low)
    first = tokens[0].replace("’", "'") if tokens else ""
    if first.startswith("l'"):
        return "3", "sg", ""
    if is_fr:
        if len(tokens) == 1 and first in _FR_PRONOUNS:
            return _FR_PRONOUNS[first]
        if first.startswith("j'"):
            return "1", "sg", ""
        if first in _FR_PLURAL_DETERMINERS:
            return "3", "pl", ""
        if first in _FR_MASC_SG_DETERMINERS:
            return "3", "sg", "masc"
        if first in _FR_FEM_SG_DETERMINERS:
            return "3", "sg", "fem"
        return "3", (_head_noun_number(tokens[-1], "fr") if len(tokens) > 1 else "sg"), ""
    if len(tokens) == 1 and first in _EN_PRONOUNS:
        return (*_EN_PRONOUNS[first], "")
    if first in _EN_PLURAL_DETERMINERS:
        return "3", "pl", ""
    if first in ("a", "an", "this", "that", "each", "every"):
        return "3", "sg", ""
    return "3", (_head_noun_number(tokens[-1], "en") if len(tokens) > 1 else "sg"), ""


def _is_attested(form: str | None, lemma: str, lang: str) -> bool:
    """True only when the corpus attests `form` as an inflection of `lemma`."""
    if not form:
        return False
    return any(a.lemma == lemma for a in lookup_surface_form(form, lang=lang))


def _french_past_participle(lemma: str, gender: str, number: str) -> str | None:
    """Attested past participle for the requested agreement (Morphalou stores sg/pl × masc/fem cells)."""
    for g, n in ((gender, number), (gender, ""), ("", number), ("", "")):
        form = realize_inflection(lemma, pos="verb", mood="participle", tense="past", gender=g, number=n, lang="fr")
        if form and _is_attested(form, lemma, "fr"):
            matches = [
                a for a in lookup_surface_form(form, lang="fr")
                if a.lemma == lemma and a.mood == "participle" and a.tense == "past"
            ]
            if any((not g or a.gender in (g, "")) and (not n or a.number in (n, "inv", "")) for a in matches):
                return form
    return None


def _inner_subject(subject: str, is_fr: bool) -> str:
    """Lowercase a sentence-initial pronoun or determiner when the subject moves inside a question."""
    tokens = subject.split(maxsplit=1)
    if not tokens:
        return subject
    first = tokens[0].lower().replace("’", "'")
    function_words = (
        set(_FR_PRONOUNS) | _FR_PLURAL_DETERMINERS | _FR_MASC_SG_DETERMINERS | _FR_FEM_SG_DETERMINERS
        if is_fr else set(_EN_PRONOUNS) - {"i"} | _EN_PLURAL_DETERMINERS | {"the", "a", "an", "this", "that", "each", "every"}
    )
    if first in function_words or first.startswith("l'"):
        return subject[0].lower() + subject[1:]
    return subject


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
    person: str | None = None,
    number: str | None = None,
    gender: str | None = None,
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
      person: "1", "2", "3" (derived from the subject when omitted)
      number: "sg", "pl" (derived from the subject when omitted)
      gender: "masc", "fem" (derived from the subject when omitted; unknown gender
              with a participle agreement is declared as a limitation)
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

    inf_person, inf_number, inf_gender = _infer_subject_features(clean_subj, is_fr)
    person = str(person) if person else inf_person
    number_known = bool(number or inf_number)
    number = (number or inf_number or "sg").lower()
    gender_known = bool(gender or inf_gender)
    gender = (gender or inf_gender or "masc").lower()

    # French generic "past" is the passé composé; imperfect / simple_past stay explicit.
    if is_fr and tense.lower() == "past" and aspect.lower() not in ("progressive", "continuous"):
        tense = "compound_past"

    is_compound = tense.lower() in ("compound_past", "passé_composé", "perfect") or aspect.lower() == "perfect"
    is_progressive = aspect.lower() in ("progressive", "continuous")
    is_neg = (polarity or "").lower() in ("negative", "negated")

    has_limitation = False
    limitation_reason = None
    realized_v = ""

    def _limit(reason: str) -> None:
        nonlocal has_limitation, limitation_reason
        has_limitation = True
        limitation_reason = limitation_reason or reason

    if not number_known:
        _limit(f"SUBJECT_AGREEMENT_UNCERTAIN:{clean_subj}")

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
            aux_form = realize_inflection(aux_lemma, pos="verb", mood="indicative", tense="present", person=person, number=number, lang="fr")
            if not _is_attested(aux_form, aux_lemma, "fr"):
                _limit(f"UNRESOLVED_AUXILIARY:{aux_lemma}:{person}:{number}")
                aux_form = aux_form or aux_lemma
            if aux_lemma == "être":
                pp_gender, pp_number = gender, number
                if not gender_known:
                    _limit(f"PARTICIPLE_AGREEMENT_UNCERTAIN:{clean_verb}:gender")
            else:
                pp_gender, pp_number = "masc", "sg"
            pp_form = _french_past_participle(clean_verb, pp_gender, pp_number)
            if not pp_form:
                _limit(f"UNKNOWN_PARTICIPLE:{clean_verb}")
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
            aux_be = realize_inflection("être", pos="verb", mood="indicative", tense=tense.lower(), person=person, number=number, lang="fr")
            if not _is_attested(aux_be, "être", "fr"):
                _limit(f"UNRESOLVED_AUXILIARY:être:{tense}:{person}:{number}")
                aux_be = aux_be or "être"
            if not is_known_lexical_item(clean_verb, lang="fr"):
                _limit(f"UNKNOWN_LEXICAL_ITEM:{clean_verb}")
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
                number=number,
                gender="",
                lang="fr",
            )
            if not _is_attested(simple_v, clean_verb, "fr"):
                simple_v = None
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
            inner = f"{_inner_subject(clean_subj, True)} {vp}".strip() if clean_subj else vp
            if clean_obj:
                inner = f"{inner} {clean_obj}"
            text = f"Est-ce {_apply_french_elision('que', inner)}{inner} ?"
        else:
            text = clause[0].upper() + clause[1:] + "."

    else:
        # English realization
        en_past = tense.lower() in ("past", "simple_past")
        en_tense = "past" if en_past else "present"
        verb_known = clean_verb.lower() == "be" or is_known_lexical_item(clean_verb, lang="en")
        if not verb_known:
            _limit(f"UNKNOWN_LEXICAL_ITEM:{clean_verb}")

        def _be_form() -> str:
            return _EN_BE.get((en_tense, person, number), "were" if en_past else "are")

        def _en_participle(p_tense: str) -> str:
            form = realize_inflection(clean_verb, pos="verb", mood="participle", tense=p_tense, lang="en")
            if not _is_attested(form, clean_verb, "en"):
                _limit(f"UNATTESTED_PARTICIPLE:{clean_verb}:{p_tense}")
                return form or clean_verb
            return form

        if is_compound:
            aux_have = "had" if en_past else ("has" if person == "3" and number == "sg" else "have")
            pp_form = _en_participle("past")
            if is_neg:
                vp = f"{aux_have} not {pp_form}"
            else:
                vp = f"{aux_have} {pp_form}"
            realized_v = vp

        elif is_progressive:
            aux_be = _be_form()
            prp_form = _en_participle("present")
            if is_neg:
                vp = f"{aux_be} not {prp_form}"
            else:
                vp = f"{aux_be} {prp_form}"
            realized_v = vp

        else:
            if clean_verb.lower() == "be":
                simple_v = _be_form()
            elif en_past:
                simple_v = realize_inflection(clean_verb, pos="verb", mood="indicative", tense="past", lang="en")
                if not _is_attested(simple_v, clean_verb, "en"):
                    if verb_known:
                        _limit(f"UNATTESTED_FORM:{clean_verb}:past")
                    simple_v = simple_v or clean_verb
            elif person == "3" and number == "sg":
                simple_v = realize_inflection(clean_verb, pos="verb", mood="indicative", tense="present", person="3", number="sg", lang="en")
                if not _is_attested(simple_v, clean_verb, "en"):
                    if verb_known:
                        _limit(f"UNATTESTED_FORM:{clean_verb}:present:3:sg")
                    simple_v = simple_v or clean_verb
            else:
                simple_v = clean_verb.lower()

            if is_neg:
                if clean_verb.lower() == "be":
                    vp = f"{simple_v} not"
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
                text = f"{aux_have.capitalize()} {_inner_subject(clean_subj, False)} {pp_form} {clean_obj}".strip() + "?"
            elif clean_verb.lower() == "be":
                be_form = _be_form()
                text = f"{be_form.capitalize()} {_inner_subject(clean_subj, False)} {clean_obj}".strip() + "?"
            else:
                aux_do = "did" if tense.lower() in ("past", "simple_past") else ("does" if person == "3" and number.lower() == "sg" else "do")
                infinitive = clean_verb.lower()
                clause = f"{aux_do.capitalize()} {_inner_subject(clean_subj, False)} {infinitive} {clean_obj}".strip()
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
