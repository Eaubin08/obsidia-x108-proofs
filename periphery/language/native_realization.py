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
    """Number of a noun head from attested corpus analyses.

    "" when the head is not attested as a noun, "?" when it is attested as both
    singular and plural (fils, sheep), else "sg" / "pl".
    """
    numbers = {a.number for a in lookup_surface_form(head, lang=lang) if a.pos == "noun" and a.number in ("sg", "pl")}
    if len(numbers) > 1:
        return "?"
    return numbers.pop() if numbers else ""


_KNOWN_POLARITIES = frozenset({"affirmative", "positive", "negative", "negated"})
_KNOWN_ASPECTS = frozenset({"simple", "progressive", "continuous", "perfect"})
_NEGATIVE_QUANTIFIERS = frozenset({
    "personne", "aucun", "aucune", "rien", "nul", "nulle", "nobody", "no", "nothing", "none",
    "no one", "neither",
})
# French verbs conjugated with être intransitively but with avoir when they take an object.
_ETRE_OR_AVOIR_VERBS = frozenset({"monter", "descendre", "sortir", "rentrer", "passer", "retourner"})

_VOWEL_ONSET = "aeiouàâäéèêëîïôöùûü"
_WH_SUBJECTS = frozenset({
    "who", "what", "which", "whose", "qui", "que", "quoi", "lequel", "laquelle", "lesquels",
    "lesquelles", "quel", "quelle", "quels", "quelles",
})

# French determiners: category and the (gender, number) cell they encode ("" = any gender).
_FR_DETERMINERS: dict[str, tuple[str, str, str]] = {
    "le": ("def", "masc", "sg"), "la": ("def", "fem", "sg"), "l'": ("def", "", "sg"), "les": ("def", "", "pl"),
    "un": ("indef", "masc", "sg"), "une": ("indef", "fem", "sg"), "des": ("indef", "", "pl"),
    "du": ("partitive", "masc", "sg"), "au": ("contracted", "masc", "sg"), "aux": ("contracted", "", "pl"),
    "ce": ("dem", "masc", "sg"), "cet": ("dem", "masc", "sg"), "cette": ("dem", "fem", "sg"), "ces": ("dem", "", "pl"),
    "mon": ("poss1", "masc", "sg"), "ma": ("poss1", "fem", "sg"), "mes": ("poss1", "", "pl"),
    "ton": ("poss2", "masc", "sg"), "ta": ("poss2", "fem", "sg"), "tes": ("poss2", "", "pl"),
    "son": ("poss3", "masc", "sg"), "sa": ("poss3", "fem", "sg"), "ses": ("poss3", "", "pl"),
    "notre": ("poss4", "", "sg"), "nos": ("poss4", "", "pl"), "votre": ("poss5", "", "sg"),
    "vos": ("poss5", "", "pl"), "leur": ("poss6", "", "sg"), "leurs": ("poss6", "", "pl"),
}
_EN_DETERMINERS: dict[str, str] = {
    "the": "", "a": "sg", "an": "sg", "this": "sg", "that": "sg", "these": "pl", "those": "pl",
    "each": "sg", "every": "sg",
}
_ALL_DETERMINERS = frozenset(_FR_DETERMINERS) | frozenset(_EN_DETERMINERS)


def _expected_fr_determiner(category: str, gender: str, number: str, onset: str) -> str | None:
    """The determiner French requires for a noun of this gender/number/onset, or None."""
    vowel = onset in _VOWEL_ONSET
    if number == "pl":
        return {"def": "les", "indef": "des", "contracted": "aux", "dem": "ces", "poss1": "mes", "poss2": "tes",
                "poss3": "ses", "poss4": "nos", "poss5": "vos", "poss6": "leurs"}.get(category)
    if category in ("poss4", "poss5", "poss6"):
        return {"poss4": "notre", "poss5": "votre", "poss6": "leur"}[category]
    if category == "def":
        return "l'" if vowel else ("le" if gender == "masc" else "la")
    if category == "indef":
        return "un" if gender == "masc" else "une"
    if category in ("partitive", "contracted"):
        return None if vowel else ({"partitive": "du", "contracted": "au"}[category] if gender == "masc" else None)
    if category == "dem":
        return ("cet" if vowel else "ce") if gender == "masc" else "cette"
    if category.startswith("poss"):
        stem = {"poss1": "m", "poss2": "t", "poss3": "s"}[category]
        return stem + ("on" if gender == "masc" or vowel else "a")
    return None


def _noun_cells(noun: str, lang: str) -> set[tuple[str, str]]:
    from periphery.language.lexical_corpus import is_defective_analysis

    return {
        (a.gender, a.number) for a in lookup_surface_form(noun, lang=lang)
        if a.pos == "noun" and a.surface_form == noun and a.number in ("sg", "pl", "inv")
        and not is_defective_analysis(a)
    }


def _adjective_agrees(adj: str, gender: str, number: str, lang: str) -> bool:
    from periphery.language.lexical_corpus import is_defective_analysis

    return any(
        a.pos == "adj" and a.surface_form == adj and not is_defective_analysis(a)
        and a.number in (number, "", "inv") and (lang != "fr" or a.gender in (gender, ""))
        for a in lookup_surface_form(adj, lang=lang)
    )


def _verify_fr_noun_phrase(words: list[str]) -> str | None:
    """Regenerate "det noun [adj]" from the attested noun and compare; None when verified."""
    first = words[0]
    if first.startswith("l'") and len(first) > 2:
        words = ["l'", first[2:]] + words[1:]
    det, rest = words[0], words[1:]
    if not rest:
        return "DETERMINER_ONLY"
    if len(rest) > 2:
        return "NOUN_PHRASE_TOO_COMPLEX"
    noun, adj = rest[0], (rest[1] if len(rest) == 2 else "")
    onset = noun[:1]
    if onset == "h":
        return "H_ONSET_UNDECIDABLE"  # h muet vs h aspiré is not recorded in the corpus
    cells = _noun_cells(noun, "fr")
    if not cells:
        return f"NOUN_NOT_ATTESTED:{noun}"
    category, _, det_number = _FR_DETERMINERS[det]
    for gender, number in cells:
        if number not in (det_number, "inv"):
            continue
        if _expected_fr_determiner(category, gender, det_number, onset) != det:
            continue
        if adj and not _adjective_agrees(adj, gender, det_number, "fr"):
            continue
        return None
    return f"DETERMINER_NOUN_MISMATCH:{det} {noun}{(' ' + adj) if adj else ''}"


def _verify_en_noun_phrase(words: list[str]) -> str | None:
    det, rest = words[0], words[1:]
    if not rest:
        return "DETERMINER_ONLY"
    if len(rest) > 2:
        return "NOUN_PHRASE_TOO_COMPLEX"
    noun = rest[-1]
    adj = rest[0] if len(rest) == 2 else ""
    if adj and not _adjective_agrees(adj, "", "", "en"):
        return f"ADJECTIVE_NOT_ATTESTED:{adj}"
    numbers = {n for _, n in _noun_cells(noun, "en")}
    if not numbers:
        return f"NOUN_NOT_ATTESTED:{noun}"
    wanted = _EN_DETERMINERS[det]
    if wanted and wanted not in numbers and "inv" not in numbers:
        return f"DETERMINER_NOUN_MISMATCH:{det} {noun}"
    if det in ("a", "an"):
        head = (adj or noun).lower()
        if head[:1] in "hu" or head.startswith(("eu", "one", "once")):
            return f"ARTICLE_ONSET_UNDECIDABLE:{head}"
        if (det == "an") != (head[:1] in "aeio"):
            return f"ARTICLE_ONSET_MISMATCH:{det} {head}"
    return None


_FR_NUMERALS = frozenset({
    "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "vingt",
    "cent", "mille", "plusieurs", "quelques", "certains", "certaines", "différents", "divers",
})
_FR_SG_QUANTIFIERS = frozenset({"chaque"})
_EN_QUANTIFIERS = {
    "two": "pl", "three": "pl", "four": "pl", "five": "pl", "six": "pl", "ten": "pl", "many": "pl",
    "several": "pl", "few": "pl", "both": "pl", "some": "", "all": "", "no": "", "one": "sg", "much": "sg",
}
_FR_PREPOSITIONS = frozenset({"à", "de", "en", "dans", "sur", "sous", "avec", "pour", "par", "vers", "chez", "sans", "contre", "entre"})
_EN_PREPOSITIONS = frozenset({"to", "at", "in", "on", "for", "with", "from", "into", "by", "about", "under", "over"})
_FR_PERSONAL_PRONOUNS = frozenset({"je", "j'", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"})
_EN_PERSONAL_PRONOUNS = frozenset({"i", "you", "he", "she", "it", "we", "they"})
# Bare nouns are not grammatical French objects except in fixed verb + noun phrases.
_FR_BARE_NOUN_IDIOMS = {
    "avoir": frozenset({"faim", "soif", "raison", "tort", "peur", "froid", "chaud", "sommeil", "besoin", "envie", "mal", "lieu", "honte"}),
    "faire": frozenset({"attention", "partie", "face", "confiance"}),
    "prendre": frozenset({"part", "place", "soin", "fin"}),
}


def _is_attested_adjective(word: str, lang: str) -> bool:
    from periphery.language.lexical_corpus import is_defective_analysis

    return any(a.pos == "adj" and a.surface_form == word and not is_defective_analysis(a)
               for a in lookup_surface_form(word, lang=lang))


def _is_common_noun(word: str, lang: str) -> bool:
    return bool(_noun_cells(word.lower(), lang))


def _verify_quantified_fr(words: list[str]) -> str | None:
    """Numeral/quantifier + noun: number agreement only (these words carry no gender)."""
    q, rest = words[0], words[1:]
    if q in ("tous", "toutes"):
        if len(rest) < 2 or rest[0] not in ("les", "ces", "mes", "tes", "ses", "nos", "vos", "leurs"):
            return f"QUANTIFIER_STRUCTURE:{' '.join(words)}"
        problem = _verify_fr_noun_phrase(rest)
        if problem:
            return problem
        genders = {g for g, _ in _noun_cells(rest[1], "fr")}
        if genders and ("masc" if q == "tous" else "fem") not in genders:
            return f"QUANTIFIER_GENDER_MISMATCH:{q} {rest[1]}"
        return None
    if not rest or len(rest) > 1:
        return f"QUANTIFIER_STRUCTURE:{' '.join(words)}"
    numbers = {n for _, n in _noun_cells(rest[0], "fr")}
    wanted = "sg" if q in _FR_SG_QUANTIFIERS else "pl"
    if not numbers:
        return f"NOUN_NOT_ATTESTED:{rest[0]}"
    if wanted not in numbers and "inv" not in numbers:
        return f"QUANTIFIER_NUMBER_MISMATCH:{q} {rest[0]}"
    if q in ("certains", "certaines"):
        genders = {g for g, _ in _noun_cells(rest[0], "fr")}
        if genders and ("masc" if q == "certains" else "fem") not in genders:
            return f"QUANTIFIER_GENDER_MISMATCH:{q} {rest[0]}"
    return None


def _verify_member(original: list[str], is_fr: bool, role: str, verb_lemma: str) -> str | None:
    """Closed-world check of one noun-phrase member; None only for a verified category."""
    words = [w.lower() for w in original]
    first = words[0]
    if first in _WH_SUBJECTS:
        return f"INTERROGATIVE_PHRASE:{' '.join(original)}"
    if any(ch.isdigit() for ch in "".join(words)):
        return f"NUMERIC_PHRASE_UNVERIFIED:{' '.join(original)}"
    if is_fr:
        if role == "subject" and len(words) == 1 and first in _FR_PERSONAL_PRONOUNS:
            return None
        if first.startswith(("qu'", "que")) and role == "subject":
            rest = words[1:] if first == "que" else [first[3:]] + words[1:]
            if len(rest) == 1 and rest[0] in _FR_PERSONAL_PRONOUNS:
                return None
            return _verify_member(rest, is_fr, role, verb_lemma) if rest else "QUE_ONLY"
        det = "l'" if first.startswith("l'") else first
        if det in ("de", "d'") or first.startswith("d'"):
            return f"BARE_DE_PHRASE:{' '.join(original)}"
        if det in _FR_DETERMINERS:
            if role == "subject" and det in ("du", "au", "aux"):
                return f"PREPOSITIONAL_SUBJECT:{' '.join(original)}"
            return _verify_fr_noun_phrase(words)
        if first in _FR_NUMERALS or first in _FR_SG_QUANTIFIERS or first in ("tous", "toutes"):
            return _verify_quantified_fr(words)
        if role == "object" and first in _FR_PREPOSITIONS:
            inner = original[1:]
            if inner and inner[0].lower() in ("la", "l'") or (inner and inner[0].lower().startswith("l'")):
                return _verify_member(inner, is_fr, "object", "")
            if inner and inner[0][:1].isupper():
                return _verify_member(inner, is_fr, "object", "")
            return f"PREPOSITIONAL_PHRASE_UNVERIFIED:{' '.join(original)}"
        if role == "object" and all(w[:1].isupper() for w in original):
            return None  # proper name inside the sentence
        if len(words) == 1 and role == "object":
            if _is_attested_adjective(first, "fr"):
                return None
            if first in _FR_BARE_NOUN_IDIOMS.get(verb_lemma, frozenset()):
                return None
            return f"BARE_NOUN_OBJECT:{first}"
    else:
        if role == "subject" and len(words) == 1 and first in _EN_PERSONAL_PRONOUNS:
            return None
        if first in _EN_DETERMINERS:
            return _verify_en_noun_phrase(words)
        if first in _EN_QUANTIFIERS:
            rest = words[1:]
            if len(rest) != 1:
                return f"QUANTIFIER_STRUCTURE:{' '.join(original)}"
            numbers = {n for _, n in _noun_cells(rest[0], "en")}
            wanted = _EN_QUANTIFIERS[first]
            if not numbers:
                return f"NOUN_NOT_ATTESTED:{rest[0]}"
            if wanted and wanted not in numbers and "inv" not in numbers:
                return f"QUANTIFIER_NUMBER_MISMATCH:{first} {rest[0]}"
            return None
        if role == "object" and first in _EN_PREPOSITIONS:
            inner = original[1:]
            return _verify_member(inner, is_fr, "object", "") if inner else "PREPOSITION_ONLY"
        if len(words) == 1:
            if _is_attested_adjective(first, "en") or _is_common_noun(first, "en"):
                return None  # English bare nouns (mass/plural) and predicative adjectives
    # Proper names: every word capitalized. Inside the sentence (objects, prepositional
    # complements) capitalization is meaningful; sentence-initially it is ambiguous, so the
    # first word must not also be a common noun ("Opérateur vérifie" vs "Brody analyse").
    if all(w[:1].isupper() for w in original):
        if role == "object" or not _is_common_noun(original[0], "fr" if is_fr else "en"):
            return None
    if is_fr and role == "subject" and len(words) == 1:
        return f"BARE_NOUN_SUBJECT:{original[0]}"
    if not is_fr and role == "subject":
        return None if all(_is_common_noun(w, "en") for w in words[-1:]) and len(words) == 1 else f"UNVERIFIED_PHRASE:{' '.join(original)}"
    return f"UNVERIFIED_PHRASE:{' '.join(original)}"


def _phrase_form_problem(phrase: str, is_fr: bool, role: str = "subject", verb_lemma: str = "") -> str | None:
    """Why a noun phrase copied verbatim into the sentence cannot be vouched for, or None.

    Closed world: a phrase is accepted only when every coordinated member belongs to a
    verified category (personal pronoun, determiner/numeral/quantifier + attested noun with
    regenerated agreement, proper name, attested adjective, preposition + verified phrase,
    English bare attested noun, fixed French verb + bare noun idiom). Anything else is
    reported, so the realizer declares a limitation instead of vouching for it.
    """
    text = phrase.replace("’", "'").strip()
    if not text:
        return None
    for member in re.split(r"\s+(?:et|ou|and|or)\s+", text):
        original = member.split()
        while len(original) > 1 and len(original[-1]) <= 2 and original[-1].isupper():
            original = original[:-1]  # trailing identifier ("pompe B")
        if not original:
            return "EMPTY_MEMBER"
        problem = _verify_member(original, is_fr, role, verb_lemma)
        if problem:
            return problem
    return None


# English nouns whose number is not marked (or is plural without -s): agreement cannot be
# read from the form, so the number proposed for them is only tentative.
_EN_NUMBER_AMBIGUOUS_NOUNS = frozenset({
    "people", "police", "fish", "deer", "sheep", "cattle", "staff", "crew", "team", "data",
    "series", "species", "aircraft", "offspring", "salmon", "trout", "moose", "swine",
})


def _bare_or_head_number(text: str, tokens: list[str], lang: str) -> str:
    """Number of a determinerless or determined nominal subject.

    A trailing "?" marks a tentative number: the form to realize is known but agreement
    is not established (ambiguous noun, or a capitalized word that may be a proper noun).
    "" means no number can be proposed at all.
    """
    if lang == "en" and tokens[-1] in _EN_NUMBER_AMBIGUOUS_NOUNS:
        return "sg?"
    attested = _head_noun_number(tokens[-1], lang)
    if attested == "?":
        return "sg?"
    if len(tokens) > 1:
        head_original = text.split()[-1]
        if head_original[:1].isupper() and head_original.lower().endswith(("s", "x")):
            # "The United States", "Les Pays-Bas": a proper name of plural form.
            return f"{attested or 'sg'}?"
        return attested
    if text[:1].isupper():
        # A capitalized bare word may be a proper noun ("Paris", "Wales") whatever the
        # corpus says about its lowercase homograph.
        if attested == "sg" or (not attested and not tokens[0].endswith(("s", "x"))):
            return "sg"
        return f"{attested or 'sg'}?"
    return attested


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
    original = text.split()
    while len(tokens) > 1 and len(original) == len(tokens) and len(original[-1]) <= 2 and original[-1].isupper():
        # "The pump B", "Pompe A": an identifier, not the head noun.
        tokens, original = tokens[:-1], original[:-1]
        text = " ".join(original)
    first = tokens[0].replace("’", "'") if tokens else ""
    if first.startswith("l'"):
        return "3", "sg", ""
    if is_fr and low.startswith(("la plupart", "beaucoup", "la majorité des", "nombre de")):
        return "3", "pl", ""
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
        return "3", _bare_or_head_number(text, tokens, "fr"), ""
    if len(tokens) == 1 and first in _EN_PRONOUNS:
        return (*_EN_PRONOUNS[first], "")
    if first in _EN_PLURAL_DETERMINERS:
        return "3", "pl", ""
    if first in ("a", "an", "this", "that", "each", "every"):
        return "3", "sg", ""
    return "3", _bare_or_head_number(text, tokens, "en"), ""


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


def _join(*parts: str) -> str:
    """Join tokens with single spaces, never after an elided clitic (l', n', s', j', qu')."""
    out = ""
    for part in parts:
        part = (part or "").strip()
        if not part:
            continue
        if not out:
            out = part
        elif out.endswith(("'", "’")):
            out += part
        else:
            out += " " + part
    return out


def _elide_subject_je(subject: str, following: str) -> tuple[str, bool]:
    """French "je" elides before a vowel; before "h" the onset may be aspirated (uncertain)."""
    if subject.lower() != "je" or not following:
        return subject, False
    onset = following[0].lower()
    if onset in "aeiouyàâäéèêëîïôöùûü":
        return subject[0] + "'", False
    if onset == "h":
        return subject[0] + "'", True
    return subject, False


_FR_SIMPLE_TENSES = {
    ("indicative", "present"), ("indicative", "imperfect"), ("indicative", "simple_past"),
    ("indicative", "future"), ("conditional", "present"), ("subjunctive", "present"),
    ("subjunctive", "imperfect"), ("imperative", "present"),
}
_FR_IMPERATIVE_PERSONS = {("2", "sg"), ("1", "pl"), ("2", "pl")}
_EN_TENSES = {"present", "past", "simple_past", "future"}


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
      obj: Complement or object, kept verbatim (e.g. "la vanne", "to school", "300 K")
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

    Any cell that cannot be established from attested forms or from the given
    structure is realized best-effort and declared in has_linguistic_limitations.
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
            "decision_authority": "KX108_ONLY",
            "is_world_fact_established": False,
        }

    actual_mood = (mood or "indicative").lower()
    is_question = actual_mood in ("interrogative", "question")
    if is_question:
        actual_mood = "indicative"
    is_imperative = actual_mood == "imperative"

    refl = is_pronominal or clean_verb.lower().startswith("se ") or clean_verb.lower().startswith("s'")
    if clean_verb.lower().startswith("se "):
        clean_verb = clean_verb[3:].strip()
    elif clean_verb.lower().startswith("s'"):
        clean_verb = clean_verb[2:].strip()

    inf_person, inf_number, inf_gender = _infer_subject_features(clean_subj, is_fr)
    person_given, number_given, gender_given = person, number, gender
    person = str(person) if person else inf_person
    number_known = bool(number) or bool(inf_number and not inf_number.endswith("?"))
    number = (number or inf_number.rstrip("?") or "sg").lower()
    gender_known = bool(gender or inf_gender)
    gender = (gender or inf_gender or "masc").lower()

    tense = (tense or "present").lower()
    aspect = (aspect or "simple").lower()
    # French generic "past" is the passé composé; imperfect / simple_past stay explicit.
    if is_fr and tense == "past" and aspect not in ("progressive", "continuous"):
        tense = "compound_past"

    is_compound = tense in ("compound_past", "passé_composé", "perfect") or aspect == "perfect"
    is_progressive = aspect in ("progressive", "continuous")
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
    if (polarity or "affirmative").lower() not in _KNOWN_POLARITIES:
        _limit(f"UNSUPPORTED_POLARITY:{polarity}")
    if aspect not in _KNOWN_ASPECTS:
        _limit(f"UNSUPPORTED_ASPECT:{aspect}")
    subj_first = clean_subj.lower().split()[0] if clean_subj else ""
    if subj_first in _NEGATIVE_QUANTIFIERS or clean_subj.lower() in _NEGATIVE_QUANTIFIERS:
        # "Personne ne ...", "Aucun X ne ...", "Nobody checks": negation comes from the subject.
        _limit(f"UNSUPPORTED_STRUCTURE:negative_quantifier_subject:{clean_subj}")
    if clean_subj and (person_given or number_given):
        # An imposed person/number is only trusted when the subject itself confirms it.
        tentative_confirmed = (inf_number.endswith("?") and number_given
                               and number_given.lower() == inf_number.rstrip("?"))
        if ((not inf_number or (inf_number.endswith("?") and not tentative_confirmed))
                or (person_given and str(person_given) != inf_person)
                or (number_given and number_given.lower() != inf_number.rstrip("?"))):
            _limit(f"AGREEMENT_OVERRIDE_CONFLICT:{clean_subj}:{person}:{number}")
    if clean_subj and gender_given and inf_gender and gender_given.lower() != inf_gender:
        _limit(f"GENDER_OVERRIDE_CONFLICT:{clean_subj}:{gender_given}")
    if clean_subj.lower().split()[0] in _ALL_DETERMINERS | _WH_SUBJECTS if clean_subj else False:
        if len(clean_subj.split()) == 1:
            _limit(f"UNVERIFIED_SUBJECT_PHRASE:FUNCTION_WORD_ONLY:{clean_subj}")
    for label, phrase in (("subject", clean_subj), ("object", clean_obj)):
        verb_key = clean_verb.lower().removeprefix("se ").removeprefix("s'")
        problem = _phrase_form_problem(phrase, is_fr, label, verb_key)
        if problem:
            _limit(f"UNVERIFIED_{label.upper()}_PHRASE:{problem}")
    obj_first = clean_obj.lower().split()[0] if clean_obj else ""
    if obj_first in _NEGATIVE_QUANTIFIERS:
        # "vérifie aucune vanne": a negative quantifier needs "ne" (FR) or carries the negation (EN).
        _limit(f"UNSUPPORTED_STRUCTURE:negative_quantifier_object:{obj_first}")
    if is_imperative and is_question:
        _limit("UNSUPPORTED_STRUCTURE:imperative_question")
    if is_imperative and (tense != "present" or aspect != "simple"):
        _limit(f"UNSUPPORTED_STRUCTURE:imperative_{tense}_{aspect}")
    if is_compound and is_progressive:
        _limit("UNSUPPORTED_STRUCTURE:compound_progressive")
    if is_compound and actual_mood not in ("indicative", "imperative"):
        _limit(f"UNSUPPORTED_STRUCTURE:{actual_mood}_compound")
    is_subjunctive = actual_mood == "subjunctive" or tense == "subjunctive"
    if is_fr and is_subjunctive and not clean_subj.lower().replace("’", "'").startswith(("que ", "qu'")):
        _limit("UNSUPPORTED_STRUCTURE:subjunctive_without_que")

    if is_fr:
        refl_pron_map = {
            ("1", "sg"): "me", ("2", "sg"): "te", ("3", "sg"): "se",
            ("1", "pl"): "nous", ("2", "pl"): "vous", ("3", "pl"): "se",
        }
        refl_pron = refl_pron_map.get((person, number), "se") if refl else ""

        def _clitics_and_negation(verb_form: str, tail: str = "") -> str:
            """[ne] [reflexive] verb [pas] [tail], with elision on each clitic."""
            refl_part = _apply_french_elision(refl_pron, verb_form).strip() if refl else ""
            first = refl_part or verb_form
            neg_part = _apply_french_elision("ne", first).strip() if is_neg else ""
            return _join(neg_part, refl_part, verb_form, "pas" if is_neg else "", tail)

        if is_imperative:
            if (person, number) not in _FR_IMPERATIVE_PERSONS:
                _limit(f"UNSUPPORTED_IMPERATIVE_PERSON:{person}:{number}")
            if refl or is_compound or is_progressive:
                _limit("UNSUPPORTED_STRUCTURE:imperative_clitic_or_compound")
            imp = realize_inflection(clean_verb, pos="verb", mood="imperative", tense="present",
                                     person=person, number=number, gender="", lang="fr")
            if not _is_attested(imp, clean_verb, "fr"):
                _limit(f"UNSUPPORTED_CONJUGATION_CELL:{clean_verb}:imperative:{person}:{number}")
                imp = imp or clean_verb
            vp = _join(_apply_french_elision("ne", imp).strip() if is_neg else "", imp, "pas" if is_neg else "")
            realized_v = vp
            clause = _join(vp, clean_obj)
            text = clause[0].upper() + clause[1:] + "."
        else:
            if is_compound:
                if tense not in ("compound_past", "passé_composé", "perfect", "present"):
                    _limit(f"UNSUPPORTED_TENSE:{tense}:{aspect}")
                aux_lemma = "être" if (refl or clean_verb.lower() in _ETRE_VERBS) else "avoir"
                aux_form = realize_inflection(aux_lemma, pos="verb", mood="indicative", tense="present",
                                              person=person, number=number, lang="fr")
                if not _is_attested(aux_form, aux_lemma, "fr"):
                    _limit(f"UNRESOLVED_AUXILIARY:{aux_lemma}:{person}:{number}")
                    aux_form = aux_form or aux_lemma
                if aux_lemma == "être":
                    pp_gender, pp_number = gender, number
                    if not gender_known:
                        _limit(f"PARTICIPLE_AGREEMENT_UNCERTAIN:{clean_verb}:gender")
                    if refl:
                        # Reflexive vs. reciprocal-indirect ("ils se sont parlé") and a following
                        # direct object ("elle s'est lavé les mains") change the agreement;
                        # the structure does not say which applies.
                        _limit(f"PARTICIPLE_AGREEMENT_UNCERTAIN:{clean_verb}:pronominal")
                    if clean_verb.lower() in _ETRE_OR_AVOIR_VERBS and clean_obj:
                        # "Il a monté la valise" vs "il est monté": transitive use takes avoir.
                        _limit(f"AUXILIARY_UNCERTAIN:{clean_verb}:with_object")
                else:
                    pp_gender, pp_number = "masc", "sg"
                pp_form = _french_past_participle(clean_verb, pp_gender, pp_number)
                if not pp_form:
                    _limit(f"UNKNOWN_PARTICIPLE:{clean_verb}")
                    pp_form = clean_verb
                vp = _clitics_and_negation(aux_form, pp_form)

            elif is_progressive:
                if tense not in ("present", "imperfect", "future"):
                    _limit(f"UNSUPPORTED_TENSE:{tense}:{aspect}")
                if actual_mood != "indicative":
                    _limit(f"UNSUPPORTED_STRUCTURE:{actual_mood}_progressive")
                aux_be = realize_inflection("être", pos="verb", mood="indicative", tense=tense,
                                            person=person, number=number, lang="fr")
                if not _is_attested(aux_be, "être", "fr"):
                    _limit(f"UNRESOLVED_AUXILIARY:être:{tense}:{person}:{number}")
                    aux_be = aux_be or "être"
                if not is_known_lexical_item(clean_verb, lang="fr"):
                    _limit(f"UNKNOWN_LEXICAL_ITEM:{clean_verb}")
                if refl:
                    _limit("UNSUPPORTED_STRUCTURE:pronominal_progressive")
                de_elided = _apply_french_elision("de", clean_verb).strip()
                vp = _join(_apply_french_elision("ne", aux_be).strip() if is_neg else "", aux_be,
                           "pas" if is_neg else "", "en train", de_elided, clean_verb)

            else:
                cell_mood, cell_tense = actual_mood, tense
                if tense == "subjunctive":
                    cell_mood, cell_tense = "subjunctive", "present"
                if (cell_mood, cell_tense) not in _FR_SIMPLE_TENSES:
                    _limit(f"UNSUPPORTED_TENSE:{cell_mood}:{cell_tense}")
                simple_v = realize_inflection(clean_verb, pos="verb", mood=cell_mood, tense=cell_tense,
                                              person=person, number=number, gender="", lang="fr")
                if not _is_attested(simple_v, clean_verb, "fr"):
                    simple_v = None
                if not simple_v:
                    if not is_known_lexical_item(clean_verb, lang="fr"):
                        _limit(f"UNKNOWN_LEXICAL_ITEM:{clean_verb}")
                    else:
                        _limit(f"UNSUPPORTED_CONJUGATION_CELL:{clean_verb}:{cell_mood}:{cell_tense}:{person}:{number}")
                    simple_v = clean_verb
                vp = _clitics_and_negation(simple_v)
            realized_v = vp

            subj, h_uncertain = _elide_subject_je(clean_subj, vp)
            if h_uncertain:
                _limit("ELISION_UNCERTAIN:h_onset")
            if is_question:
                inner = _join(_inner_subject(subj, True) if subj else "", vp, clean_obj)
                text = _join(_join("Est-ce", _apply_french_elision("que", inner).strip()), inner) + " ?"
            else:
                clause = _join(subj, vp, clean_obj)
                text = clause[0].upper() + clause[1:] + "."

    else:
        en_past = tense in ("past", "simple_past")
        en_future = tense == "future"
        modal = "would" if actual_mood == "conditional" else ("will" if en_future else "")
        if tense not in _EN_TENSES and not is_compound:
            _limit(f"UNSUPPORTED_TENSE:{tense}")
        if actual_mood == "subjunctive":
            _limit("UNSUPPORTED_MOOD:subjunctive")
        if modal and (is_compound or is_progressive):
            _limit(f"UNSUPPORTED_STRUCTURE:{modal}_{aspect}")
        if refl:
            _limit("UNSUPPORTED_STRUCTURE:pronominal_en")
        en_tense = "past" if en_past else "present"
        is_be = clean_verb.lower() == "be"
        verb_known = is_be or is_known_lexical_item(clean_verb, lang="en")
        if not verb_known:
            _limit(f"UNKNOWN_LEXICAL_ITEM:{clean_verb}")
        base = clean_verb.lower()

        def _be_form() -> str:
            return _EN_BE.get((en_tense, person, number), "were" if en_past else "are")

        def _en_participle(p_tense: str) -> str:
            form = realize_inflection(clean_verb, pos="verb", mood="participle", tense=p_tense, lang="en")
            if not _is_attested(form, clean_verb, "en"):
                _limit(f"UNATTESTED_PARTICIPLE:{clean_verb}:{p_tense}")
                return form or clean_verb
            return form

        def _finite(form_tense: str) -> str:
            if is_be:
                return _be_form()
            if form_tense == "past":
                form = realize_inflection(clean_verb, pos="verb", mood="indicative", tense="past", lang="en")
                cell = "past"
            elif person == "3" and number == "sg":
                form = realize_inflection(clean_verb, pos="verb", mood="indicative", tense="present",
                                          person="3", number="sg", lang="en")
                cell = "present:3:sg"
            else:
                return base
            if not _is_attested(form, clean_verb, "en"):
                if verb_known:
                    _limit(f"UNATTESTED_FORM:{clean_verb}:{cell}")
                return form or base
            return form

        not_ = "not" if is_neg else ""

        if is_imperative:
            if clean_subj and clean_subj.lower() != "you":
                _limit(f"UNSUPPORTED_IMPERATIVE_SUBJECT:{clean_subj}")
            vp = _join("do" if is_neg else "", not_, base)
            realized_v = vp
            clause = _join(vp, clean_obj)
            text = clause[0].upper() + clause[1:] + "."
        else:
            if modal:
                aux, main = modal, base
            elif is_compound:
                aux = "had" if en_past else ("has" if person == "3" and number == "sg" else "have")
                main = _en_participle("past")
            elif is_progressive:
                aux, main = _be_form(), _en_participle("present")
            elif is_be:
                aux, main = _be_form(), ""
            elif is_neg or is_question:
                aux = "did" if en_past else ("does" if person == "3" and number == "sg" else "do")
                main = base
            else:
                aux, main = "", _finite(en_tense)

            vp = _join(aux, not_, main)
            realized_v = vp
            if is_question:
                text = _join(aux.capitalize(), _inner_subject(clean_subj, False), not_, main, clean_obj) + "?"
            else:
                clause = _join(clean_subj, vp, clean_obj)
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
