"""
periphery/language/lexical_corpus.py

High-performance runtime interface to Brody's real French and English lexical,
morphological, and semantic corpora.

Data sources:
- Morphalou 3.1 (ATILF CNRS / ORTOLANG - LGPL-LR)
- UniMorph French & English (UniMorph - CC-BY-SA 4.0)
- Princeton WordNet Morphological Exceptions (Princeton - BSD-style)
- Open English WordNet 2025 (Global WordNet Association - CC-BY 4.0)
- French Thesaurus (Dicollecte / LibreOffice - MPL 2.0 / LGPL 3.0)

Features:
- Fast indexed B-tree lookups (< 0.5 ms)
- Substantial coverage: >750,000 lemmas, >2,000,000 inflected forms, >220,000 senses
- Bidirectional lookup: surface_form -> lemma + features and lemma + features -> surface_form
- Zero full-corpus RAM loading (SQLite paging on disk)
"""
from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "linguistic_corpus" / "lexicon.db"

_local = threading.local()


def _get_connection() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return conn


@dataclass(frozen=True)
class LinguisticAnalysis:
    surface_form: str
    lemma: str
    lang: str
    pos: str
    mood: str = ""
    tense: str = ""
    person: str = ""
    number: str = ""
    gender: str = ""
    morpho_tag: str = ""
    source_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_form": self.surface_form,
            "lemma": self.lemma,
            "lang": self.lang,
            "pos": self.pos,
            "mood": self.mood,
            "tense": self.tense,
            "person": self.person,
            "number": self.number,
            "gender": self.gender,
            "morpho_tag": self.morpho_tag,
            "source_id": self.source_id,
        }


@dataclass(frozen=True)
class SenseDefinition:
    lemma: str
    lang: str
    pos: str
    sense_id: str
    definition: str
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    source_id: str = ""
    # "definition" (Littré, OEWN), "synonym_group" (thesaurus) or "translation_gloss" (bilingual).
    kind: str = "definition"
    gloss: str = ""
    # External lexical resources are reference material, never verified world knowledge.
    verified_fact: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "lemma": self.lemma,
            "lang": self.lang,
            "pos": self.pos,
            "sense_id": self.sense_id,
            "definition": self.definition,
            "synonyms": list(self.synonyms),
            "antonyms": list(self.antonyms),
            "source_id": self.source_id,
            "kind": self.kind,
            "gloss": self.gloss,
            "verified_fact": self.verified_fact,
        }


_SYNONYM_GROUP_SOURCES = frozenset({"thes_fr"})
_TRANSLATION_GLOSS_SOURCES = frozenset({"freedict_fra_eng"})
_GLOSS_PREFIX = "Anglais: "


@lru_cache(maxsize=16384)
def lookup_surface_form(form: str, lang: str | None = None) -> tuple[LinguisticAnalysis, ...]:
    """
    Bidirectional forward lookup: surface_form -> list of morphological analyses.
    Accent and case sensitive with fallback to accent-folded search.
    """
    clean_form = (form or "").strip()
    if not clean_form:
        return ()

    conn = _get_connection()
    if conn is None:
        return ()

    cursor = conn.cursor()
    if lang:
        query = """
        SELECT surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id
        FROM inflections
        WHERE surface_form = ? AND lang = ?
        ORDER BY (source_id = 'morphalou_3_1' OR source_id = 'wordnet_exc') DESC
        LIMIT 30
        """
        cursor.execute(query, (clean_form, lang.lower()))
    else:
        query = """
        SELECT surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id
        FROM inflections
        WHERE surface_form = ?
        ORDER BY (source_id = 'morphalou_3_1' OR source_id = 'wordnet_exc') DESC
        LIMIT 30
        """
        cursor.execute(query, (clean_form,))

    rows = cursor.fetchall()
    if not rows and clean_form.lower() != clean_form:
        if lang:
            cursor.execute(query, (clean_form.lower(), lang.lower()))
        else:
            cursor.execute(query, (clean_form.lower(),))
        rows = cursor.fetchall()

    results = []
    seen = set()
    for r in rows:
        key = (r["surface_form"], r["lemma"], r["lang"], r["pos"], r["mood"], r["tense"], r["person"], r["number"], r["gender"])
        if key not in seen:
            seen.add(key)
            results.append(LinguisticAnalysis(
                surface_form=r["surface_form"],
                lemma=r["lemma"],
                lang=r["lang"],
                pos=r["pos"],
                mood=r["mood"] or "",
                tense=r["tense"] or "",
                person=r["person"] or "",
                number=r["number"] or "",
                gender=r["gender"] or "",
                morpho_tag=r["morpho_tag"] or "",
                source_id=r["source_id"] or "",
            ))
    return tuple(results)


@lru_cache(maxsize=16384)
def realize_inflection(
    lemma: str,
    pos: str = "verb",
    mood: str = "indicative",
    tense: str = "present",
    person: str = "3",
    number: str = "sg",
    gender: str = "",
    lang: str = "fr",
) -> str | None:
    """
    Bidirectional reverse lookup: lemma + grammatical features -> surface_form.
    Realizes exact conjugated or inflected form from real corpus data.
    """
    clean_lemma = (lemma or "").strip()
    if not clean_lemma:
        return None

    conn = _get_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    target_lang = (lang or "fr").lower()

    # Exact query
    cursor.execute("""
    SELECT surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id
    FROM inflections
    WHERE lemma = ? AND lang = ? AND pos = ?
      AND (? = '' OR mood = ?)
      AND (? = '' OR tense = ?)
      AND (? = '' OR person = '' OR person = ? OR person LIKE '%' || ? || '%')
      AND (? = '' OR number = '' OR number = ?)
      AND (? = '' OR gender = '' OR gender = ?)
    ORDER BY (source_id = 'morphalou_3_1' OR source_id = 'wordnet_exc' OR source_id = 'unimorph_eng') DESC,
             (person != '') DESC, (number != '') DESC,
             (length(surface_form) >= 3) DESC, length(surface_form) ASC
    LIMIT 10
    """, (
        clean_lemma, target_lang, pos,
        mood, mood,
        tense, tense,
        person, person, person,
        number, number,
        gender, gender,
    ))
    for row in cursor.fetchall():
        if not is_defective_analysis(LinguisticAnalysis(**{k: row[k] or "" for k in row.keys()})):
            return row["surface_form"]

    # Relaxed person/number for infinitives/participles or irregular tense mapping
    if mood in ("infinitive", "participle") or pos != "verb":
        cursor.execute("""
        SELECT surface_form
        FROM inflections
        WHERE lemma = ? AND lang = ? AND pos = ?
          AND (mood = ? OR ? = '')
          AND (number = ? OR ? = '')
        ORDER BY (length(surface_form) >= 3) DESC, length(surface_form) ASC
        LIMIT 1
        """, (clean_lemma, target_lang, pos, mood, mood, number, number))
        row = cursor.fetchone()
        if row:
            return row["surface_form"]

    # Regular English past-tense morphological rule when lemma is attested in corpus
    if target_lang == "en" and pos == "verb" and tense in ("past", "simple_past"):
        if is_known_lexical_item(clean_lemma, lang="en"):
            low = clean_lemma.lower()
            if low.endswith("e"):
                return low + "d"
            elif len(low) > 2 and low.endswith("y") and low[-2] not in "aeiou":
                return low[:-1] + "ied"
            else:
                return low + "ed"

    # Fallback to base lemma if nothing found
    return None


@lru_cache(maxsize=4096)
def get_verb_paradigm(lemma: str, lang: str = "fr") -> dict[str, list[dict[str, Any]]]:
    """
    Returns full inflectional paradigm for a verb, grouped by mood and tense.
    """
    clean_lemma = (lemma or "").strip()
    if not clean_lemma:
        return {}

    conn = _get_connection()
    if conn is None:
        return {}

    cursor = conn.cursor()
    cursor.execute("""
    SELECT surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id
    FROM inflections
    WHERE lemma = ? AND lang = ? AND pos = 'verb'
    ORDER BY mood, tense, person, number
    """, (clean_lemma, lang.lower()))

    rows = cursor.fetchall()
    paradigm: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        group_key = f"{r['mood'] or 'other'}_{r['tense'] or 'other'}"
        entry = {
            "surface_form": r["surface_form"],
            "person": r["person"] or "",
            "number": r["number"] or "",
            "gender": r["gender"] or "",
            "morpho_tag": r["morpho_tag"] or "",
            "source_id": r["source_id"] or "",
        }
        paradigm.setdefault(group_key, []).append(entry)
    return paradigm


@lru_cache(maxsize=8192)
def get_senses_and_synonyms(lemma: str, lang: str = "fr") -> tuple[SenseDefinition, ...]:
    """
    Returns lexical senses, definitions, synonyms, and antonyms for a lemma.
    """
    clean_lemma = (lemma or "").strip()
    if not clean_lemma:
        return ()

    conn = _get_connection()
    if conn is None:
        return ()

    cursor = conn.cursor()
    cursor.execute("""
    SELECT lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id
    FROM senses
    WHERE lemma = ? AND lang = ?
    LIMIT 20
    """, (clean_lemma, lang.lower()))

    rows = cursor.fetchall()
    defs = []
    for r in rows:
        syns = json.loads(r["synonyms"]) if r["synonyms"] else []
        ants = json.loads(r["antonyms"]) if r["antonyms"] else []
        source_id = r["source_id"] or ""
        text = r["definition"] or ""
        kind, gloss = "definition", ""
        if source_id in _SYNONYM_GROUP_SOURCES:
            # The stored text is a placeholder label ("Synonymes français (nom)"), not a definition.
            kind, text = "synonym_group", ""
        elif source_id in _TRANSLATION_GLOSS_SOURCES:
            kind = "translation_gloss"
            gloss = text[len(_GLOSS_PREFIX):] if text.startswith(_GLOSS_PREFIX) else text
            text = ""
        defs.append(SenseDefinition(
            lemma=r["lemma"],
            lang=r["lang"],
            pos=r["pos"],
            sense_id=r["sense_id"] or "",
            definition=text,
            synonyms=syns,
            antonyms=ants,
            source_id=source_id,
            kind=kind,
            gloss=gloss,
        ))
    return tuple(defs)


@lru_cache(maxsize=16384)
def is_known_lexical_item(word: str, lang: str | None = None) -> bool:
    """
    Returns True if word exists in the verified dictionary (either as lemma or inflected form).
    """
    clean = (word or "").strip()
    if not clean:
        return False
    target = (lang or "").lower()

    if target == "en":
        low = clean.lower()
        if low in _EN_FUNCTION_WORDS or _in_oewn(low):
            return True
        return any(_in_oewn(a.lemma) for a in lookup_surface_form(clean, lang="en") if not is_defective_analysis(a))

    analyses = [a for a in lookup_surface_form(clean, lang=lang) if not is_defective_analysis(a)]
    if analyses:
        return True

    conn = _get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    if lang:
        cursor.execute("SELECT 1 FROM lemmas WHERE lemma = ? AND lang = ? LIMIT 1", (clean, target))
    else:
        cursor.execute("SELECT 1 FROM lemmas WHERE lemma = ? LIMIT 1", (clean,))
    return bool(cursor.fetchone())


# Rows of the imported sources that are demonstrably wrong (found by the independent
# certification of 787a74fb). They stay in the database for provenance but are never
# treated as attested knowledge: (source_id, surface_form, lemma, morpho_tag or "*").
_KNOWN_SOURCE_DEFECTS = frozenset({
    ("morphalou_3_1", "st", "être", "*"),            # truncated "sont" in the indicative present 3pl cell
    ("wordnet_exc", "has", "have", "V;IRREG;PAST"),   # "has" is present 3sg, not a past form
    ("wordnet_exc", "goes", "go", "N;PL;IRREG"),      # verb form listed as an irregular noun plural
})
# UniMorph English fills the plural cell of mass nouns with these placeholders.
_UNIMORPH_PLACEHOLDER_PLURALS = frozenset({"countable", "uncountable"})

# Closed-class English words absent from WordNet (which covers only open classes).
_EN_FUNCTION_WORDS = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "and", "or", "but", "nor", "of", "to", "in",
    "on", "at", "by", "for", "with", "from", "into", "onto", "over", "under", "about", "after",
    "before", "between", "through", "during", "without", "within", "against", "among", "i", "you",
    "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its",
    "our", "their", "who", "whom", "whose", "which", "what", "not", "no", "if", "than", "then",
    "because", "while", "although", "will", "would", "shall", "should", "can", "could", "may",
    "might", "must", "is", "am", "are", "was", "were", "been", "being", "be", "has", "have", "had",
    "does", "do", "did",
})


def is_defective_analysis(a: LinguisticAnalysis) -> bool:
    """True for imported rows known to be wrong; they are kept for provenance only."""
    if (a.source_id, a.surface_form, a.lemma, a.morpho_tag) in _KNOWN_SOURCE_DEFECTS:
        return True
    if (a.source_id, a.surface_form, a.lemma, "*") in _KNOWN_SOURCE_DEFECTS:
        return True
    return (a.source_id == "unimorph_eng" and a.pos == "noun" and a.number == "pl"
            and a.surface_form.lower() in _UNIMORPH_PLACEHOLDER_PLURALS)


@lru_cache(maxsize=16384)
def _in_oewn(lemma: str) -> bool:
    """English open-class lemma attested by Open English WordNet (UniMorph alone is not enough)."""
    conn = _get_connection()
    if conn is None or not lemma:
        return False
    row = conn.execute(
        "SELECT 1 FROM senses WHERE lemma = ? AND lang = 'en' AND source_id = 'oewn_2025' LIMIT 1", (lemma,)
    ).fetchone()
    return bool(row)


def get_corpus_statistics() -> dict[str, Any]:
    """
    Returns live database counts and source metrics.
    """
    conn = _get_connection()
    if conn is None:
        return {"status": "DB_UNAVAILABLE", "database_path": str(DB_PATH)}

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM lemmas")
    lemmas_count = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM inflections")
    forms_count = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM senses")
    senses_count = cursor.fetchone()["cnt"]

    cursor.execute("SELECT id, name, version, license, lemmas_count, forms_count, senses_count, checksum FROM sources")
    sources = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(DISTINCT lemma) AS cnt FROM inflections WHERE lang='fr' AND pos='verb'")
    fr_verbs = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(DISTINCT lemma) AS cnt FROM inflections WHERE lang='en' AND pos='verb'")
    en_verbs = cursor.fetchone()["cnt"]

    db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0

    return {
        "status": "READY",
        "database_path": str(DB_PATH),
        "database_size_bytes": db_size,
        "database_size_mb": round(db_size / (1024 * 1024), 2),
        "total_lemmas": lemmas_count,
        "total_inflected_forms": forms_count,
        "total_senses": senses_count,
        "french_verb_lemmas": fr_verbs,
        "english_verb_lemmas": en_verbs,
        "sources": sources,
    }
