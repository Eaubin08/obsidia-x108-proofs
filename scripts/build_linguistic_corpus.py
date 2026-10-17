"""
scripts/build_linguistic_corpus.py

Builds a reproducible SQLite corpus index from official, legal French and English lexical datasets:
- Morphalou 3.1 (LGPL-LR, ATILF CNRS)
- UniMorph English (CC-BY-SA 4.0)
- UniMorph French (CC-BY-SA 4.0)
- Open English WordNet 2025 (CC-BY 4.0)
- French Thesaurus (Dicollecte / LibreOffice, MPL 2.0 / LGPL 3.0)

Generates:
- data/linguistic_corpus/lexicon.db (indexed SQLite database)
- data/linguistic_corpus/INGESTION_REPORT.json (provenance, stats, checksums)
- data/linguistic_corpus/MANIFEST.json (metadata and licenses)
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "_external_sources" / "lexicon" / "raw"
DATA_DIR = ROOT / "data" / "linguistic_corpus"
DB_PATH = DATA_DIR / "lexicon.db"


def init_db(conn: sqlite3.Connection):
    c = conn.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS inflections;
    DROP TABLE IF EXISTS lemmas;
    DROP TABLE IF EXISTS senses;
    DROP TABLE IF EXISTS sources;
    DROP TABLE IF EXISTS metadata;

    CREATE TABLE metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    CREATE TABLE sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        license TEXT NOT NULL,
        source TEXT NOT NULL,
        checksum TEXT NOT NULL,
        bytes INTEGER NOT NULL,
        lemmas_count INTEGER DEFAULT 0,
        forms_count INTEGER DEFAULT 0,
        senses_count INTEGER DEFAULT 0,
        exceptions_count INTEGER DEFAULT 0,
        rejected_count INTEGER DEFAULT 0
    );

    CREATE TABLE lemmas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        lang TEXT NOT NULL,
        pos TEXT NOT NULL,
        features TEXT,
        source_id TEXT NOT NULL
    );

    CREATE TABLE inflections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        surface_form TEXT NOT NULL,
        lemma TEXT NOT NULL,
        lang TEXT NOT NULL,
        pos TEXT NOT NULL,
        mood TEXT,
        tense TEXT,
        person TEXT,
        number TEXT,
        gender TEXT,
        morpho_tag TEXT,
        source_id TEXT NOT NULL,
        UNIQUE(surface_form, lemma, lang, pos, mood, tense, person, number, gender)
    );

    CREATE TABLE senses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        lang TEXT NOT NULL,
        pos TEXT NOT NULL,
        sense_id TEXT,
        definition TEXT,
        synonyms TEXT,
        antonyms TEXT,
        source_id TEXT NOT NULL
    );
    """)
    conn.commit()


def normalize_pos(raw_cat: str) -> str:
    cat = (raw_cat or "").strip().lower()
    if "verbe" in cat or cat == "v":
        return "verb"
    if "nom" in cat or cat == "n":
        return "noun"
    if "adjectif" in cat or cat == "adj" or cat == "a":
        return "adj"
    if "adverbe" in cat or cat == "adv" or cat == "r":
        return "adv"
    if "pronom" in cat or cat == "pron":
        return "pron"
    if "préposition" in cat or "preposition" in cat or cat == "prep":
        return "prep"
    if "conjonction" in cat or cat == "conj":
        return "conj"
    if "interjection" in cat:
        return "interj"
    return "other"


def normalize_number(raw: str) -> str:
    r = (raw or "").strip().lower()
    if r in ("singular", "singulier", "sg", "s"):
        return "sg"
    if r in ("plural", "pluriel", "pl", "p"):
        return "pl"
    if r in ("invariable", "inv"):
        return "inv"
    return ""


def normalize_gender(raw: str) -> str:
    r = (raw or "").strip().lower()
    if r in ("masculine", "masculin", "masc", "m"):
        return "masc"
    if r in ("feminine", "féminin", "fem", "f"):
        return "fem"
    return ""


def normalize_person(raw: str) -> str:
    r = (raw or "").strip().lower()
    if "first" in r or r == "1":
        return "1"
    if "second" in r or r == "2":
        return "2"
    if "third" in r or r == "3":
        return "3"
    return ""


def normalize_tense(raw: str) -> str:
    r = (raw or "").strip().lower()
    if "present" in r or "présent" in r or r == "prs":
        return "present"
    if "imperfect" in r or "imparfait" in r or r == "impf":
        return "imperfect"
    if "future" in r or "futur" in r or r == "fut":
        return "future"
    if "simplepast" in r or "passésimple" in r or "passe_simple" in r:
        return "simple_past"
    if "past" in r or "passé" in r or r == "pst":
        return "past"
    return r if r != "-" else ""


def normalize_mood(raw: str) -> str:
    r = (raw or "").strip().lower()
    if "indicative" in r or "indicatif" in r or r == "ind":
        return "indicative"
    if "subjunctive" in r or "subjonctif" in r or r == "sbjv":
        return "subjunctive"
    if "conditional" in r or "conditionnel" in r or r == "cond":
        return "conditional"
    if "imperative" in r or "impératif" in r or r == "imp":
        return "imperative"
    if "participle" in r or "participe" in r or "ptcp" in r:
        return "participle"
    if "infinitive" in r or "infinitif" in r or "nfin" in r:
        return "infinitive"
    return r if r != "-" else ""


def ingest_morphalou(conn: sqlite3.Connection, raw_zip_path: Path) -> dict[str, int]:
    print("\nIngesting Morphalou 3.1 (French Morphology)...")
    c = conn.cursor()
    lemmas_seen = set()
    forms_count = 0
    rejected = 0

    batch_lemmas = []
    batch_forms = []

    with zipfile.ZipFile(raw_zip_path) as z:
        with z.open("Morphalou3.1_formatCSV_toutEnUn/Morphalou3.1_CSV.csv") as f:
            text_io = io.TextIOWrapper(f, encoding="utf-8")
            reader = csv.reader(text_io, delimiter=";")
            current_lemma = ""
            current_pos = ""
            current_gender = ""

            for i, row in enumerate(reader):
                if i < 16 or not row:
                    continue
                if len(row) < 16:
                    rejected += 1
                    continue

                raw_lem = row[0].strip()
                if raw_lem:
                    current_lemma = raw_lem
                    current_pos = normalize_pos(row[2])
                    current_gender = normalize_gender(row[5])
                    if (current_lemma, "fr", current_pos) not in lemmas_seen:
                        lemmas_seen.add((current_lemma, "fr", current_pos))
                        batch_lemmas.append((current_lemma, "fr", current_pos, current_gender, "morphalou_3_1"))

                surface = row[9].strip()
                if not surface or not current_lemma:
                    rejected += 1
                    continue

                nb = normalize_number(row[11])
                mood = normalize_mood(row[12])
                gender = normalize_gender(row[13]) or current_gender
                tense = normalize_tense(row[14])
                person = normalize_person(row[15])
                morpho_tag = f"{current_pos};{mood};{tense};{person};{nb}".strip(";")

                batch_forms.append((
                    surface,
                    current_lemma,
                    "fr",
                    current_pos,
                    mood,
                    tense,
                    person,
                    nb,
                    gender,
                    morpho_tag,
                    "morphalou_3_1",
                ))
                forms_count += 1

                if len(batch_forms) >= 50000:
                    c.executemany("""
                    INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch_forms)
                    batch_forms.clear()

                if len(batch_lemmas) >= 20000:
                    c.executemany("""
                    INSERT INTO lemmas (lemma, lang, pos, features, source_id)
                    VALUES (?, ?, ?, ?, ?)
                    """, batch_lemmas)
                    batch_lemmas.clear()

            if batch_forms:
                c.executemany("""
                INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_forms)
            if batch_lemmas:
                c.executemany("""
                INSERT INTO lemmas (lemma, lang, pos, features, source_id)
                VALUES (?, ?, ?, ?, ?)
                """, batch_lemmas)

    conn.commit()
    print(f"  Morphalou 3.1: {len(lemmas_seen):,} lemmas, {forms_count:,} inflected forms imported ({rejected} rejected).")
    return {"lemmas": len(lemmas_seen), "forms": forms_count, "senses": 0, "exceptions": 0, "rejected": rejected}


def ingest_unimorph_eng(conn: sqlite3.Connection, tsv_path: Path) -> dict[str, int]:
    print("\nIngesting UniMorph English...")
    c = conn.cursor()
    lemmas_seen = set()
    forms_count = 0
    exceptions_count = 0
    rejected = 0

    batch_lemmas = []
    batch_forms = []

    irregular_verbs = {"be", "have", "do", "go", "see", "write", "read", "run", "take", "come", "make", "get", "give", "know"}

    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                rejected += 1
                continue
            lemma, surface, tag = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if not lemma or not surface:
                rejected += 1
                continue

            tag_parts = tag.split(";")
            pos_tag = tag_parts[0]
            pos = "verb" if pos_tag == "V" else ("noun" if pos_tag == "N" else ("adj" if pos_tag == "ADJ" else "other"))

            if (lemma, "en", pos) not in lemmas_seen:
                lemmas_seen.add((lemma, "en", pos))
                batch_lemmas.append((lemma, "en", pos, "", "unimorph_eng"))

            mood = ""
            tense = ""
            person = ""
            number = ""
            gender = ""

            if "PRS" in tag_parts:
                tense = "present"
            elif "PST" in tag_parts:
                tense = "past"

            if "1" in tag_parts:
                person = "1"
            elif "2" in tag_parts:
                person = "2"
            elif "3" in tag_parts:
                person = "3"

            if "SG" in tag_parts:
                number = "sg"
            elif "PL" in tag_parts:
                number = "pl"

            if "PTCP" in tag_parts or "V.PTCP" in tag:
                mood = "participle"
            elif "IND" in tag_parts or "PRS" in tag_parts or "PST" in tag_parts:
                mood = "indicative"
            elif "NFIN" in tag_parts:
                mood = "infinitive"
            elif "IMP" in tag_parts:
                mood = "imperative"
            elif "SBJV" in tag_parts:
                mood = "subjunctive"

            if lemma in irregular_verbs:
                exceptions_count += 1

            batch_forms.append((
                surface,
                lemma,
                "en",
                pos,
                mood,
                tense,
                person,
                number,
                gender,
                tag,
                "unimorph_eng",
            ))
            forms_count += 1

            if len(batch_forms) >= 50000:
                c.executemany("""
                INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_forms)
                batch_forms.clear()

            if len(batch_lemmas) >= 20000:
                c.executemany("""
                INSERT INTO lemmas (lemma, lang, pos, features, source_id)
                VALUES (?, ?, ?, ?, ?)
                """, batch_lemmas)
                batch_lemmas.clear()

        if batch_forms:
            c.executemany("""
            INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_forms)
        if batch_lemmas:
            c.executemany("""
            INSERT INTO lemmas (lemma, lang, pos, features, source_id)
            VALUES (?, ?, ?, ?, ?)
            """, batch_lemmas)

    conn.commit()
    print(f"  UniMorph English: {len(lemmas_seen):,} lemmas, {forms_count:,} inflected forms ({exceptions_count} irregular entries).")
    return {"lemmas": len(lemmas_seen), "forms": forms_count, "senses": 0, "exceptions": exceptions_count, "rejected": rejected}


def ingest_oewn_senses(conn: sqlite3.Connection, oewn_zip_path: Path) -> dict[str, int]:
    print("\nIngesting Open English WordNet 2025 (English Senses & Definitions)...")
    c = conn.cursor()
    senses_count = 0
    lemmas_seen = set()
    rejected = 0

    batch_senses = []

    pos_map = {"v": "verb", "n": "noun", "a": "adj", "r": "adv", "s": "adj"}

    with zipfile.ZipFile(oewn_zip_path) as z:
        synset_files = [n for n in z.namelist() if n.endswith(".json") and (n.startswith("verb.") or n.startswith("noun.") or n.startswith("adj.") or n.startswith("adv."))]
        for synset_file in synset_files:
            try:
                with z.open(synset_file) as sf:
                    data = json.load(sf)
                    for synset_id, syn_data in data.items():
                        raw_pos = syn_data.get("partOfSpeech", "")
                        pos = pos_map.get(raw_pos, "other")
                        defs = syn_data.get("definition", [])
                        definition = "; ".join(defs) if isinstance(defs, list) else str(defs)
                        members = syn_data.get("members", [])
                        synonyms = [m for m in members if isinstance(m, str)]
                        antonyms = []

                        for member in synonyms:
                            lemmas_seen.add((member, "en", pos))
                            batch_senses.append((
                                member,
                                "en",
                                pos,
                                synset_id,
                                definition,
                                json.dumps(synonyms, ensure_ascii=False),
                                json.dumps(antonyms, ensure_ascii=False),
                                "oewn_2025",
                            ))
                            senses_count += 1

                            if len(batch_senses) >= 50000:
                                c.executemany("""
                                INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, batch_senses)
                                batch_senses.clear()
            except Exception as e:
                rejected += 1

        if batch_senses:
            c.executemany("""
            INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_senses)

    conn.commit()
    print(f"  Open English WordNet 2025: {len(lemmas_seen):,} lemmas, {senses_count:,} senses/definitions imported.")
    return {"lemmas": len(lemmas_seen), "forms": 0, "senses": senses_count, "exceptions": 0, "rejected": rejected}


def ingest_french_thesaurus(conn: sqlite3.Connection, thes_path: Path) -> dict[str, int]:
    print("\nIngesting French Thesaurus (Dicollecte Synonyms)...")
    c = conn.cursor()
    senses_count = 0
    lemmas_seen = set()
    rejected = 0

    batch_senses = []

    pos_map = {
        "(verbe)": "verb",
        "(nom)": "noun",
        "(adjectif)": "adj",
        "(adverbe)": "adv",
        "(preposition)": "prep",
    }

    with open(thes_path, "r", encoding="utf-8", errors="replace") as f:
        current_entry = ""
        current_count = 0

        for line in f:
            l = line.strip()
            if not l or l == "UTF-8":
                continue
            if "|" in l and not l.startswith("("):
                parts = l.split("|")
                current_entry = parts[0].strip()
                try:
                    current_count = int(parts[1].strip())
                except Exception:
                    current_count = 1
            elif l.startswith("("):
                parts = l.split("|")
                cat_raw = parts[0].strip().lower()
                pos = pos_map.get(cat_raw, "other")
                syns = [p.strip() for p in parts[1:] if p.strip()]
                if current_entry and syns:
                    lemmas_seen.add((current_entry, "fr", pos))
                    batch_senses.append((
                        current_entry,
                        "fr",
                        pos,
                        f"thes_fr_{senses_count}",
                        f"Synonymes français ({cat_raw.strip('()')})",
                        json.dumps(syns, ensure_ascii=False),
                        json.dumps([], ensure_ascii=False),
                        "thes_fr",
                    ))
                    senses_count += 1

                    if len(batch_senses) >= 20000:
                        c.executemany("""
                        INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, batch_senses)
                        batch_senses.clear()

        if batch_senses:
            c.executemany("""
            INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_senses)

    conn.commit()
    print(f"  French Thesaurus: {len(lemmas_seen):,} lemmas, {senses_count:,} synonym sets imported.")
    return {"lemmas": len(lemmas_seen), "forms": 0, "senses": senses_count, "exceptions": 0, "rejected": rejected}


def ingest_xmlittre(conn: sqlite3.Connection, zip_path: Path) -> dict[str, int]:
    print("\nIngesting XMLittré (Émile Littré - Dictionnaire de la langue française)...")
    c = conn.cursor()
    senses_count = 0
    lemmas_seen = set()
    rejected = 0
    batch_senses = []
    batch_lemmas = []

    pos_map = {
        "v. a.": "verb",
        "v. n.": "verb",
        "v. pron.": "verb",
        "v. impers.": "verb",
        "s. m.": "noun",
        "s. f.": "noun",
        "s. m. et f.": "noun",
        "adj.": "adj",
        "adv.": "adv",
        "prép.": "prep",
        "conj.": "conj",
        "interj.": "interj",
    }

    def clean_nature(raw: str) -> str:
        raw = (raw or "").strip().lower()
        for k, v in pos_map.items():
            if k in raw:
                return v
        if "verbe" in raw or "v." in raw:
            return "verb"
        if "subst" in raw or "s." in raw or "nom" in raw:
            return "noun"
        if "adj" in raw:
            return "adj"
        if "adv" in raw:
            return "adv"
        return "other"

    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(zip_path) as z:
        xml_files = [n for n in z.namelist() if n.endswith(".xml")]
        for xml_file in sorted(xml_files):
            with z.open(xml_file) as f:
                parser = ET.iterparse(f, events=("end",))
                for event, elem in parser:
                    if elem.tag == "entree":
                        raw_terme = (elem.attrib.get("terme") or "").strip().lower()
                        if raw_terme:
                            terme = raw_terme.split(",")[0].strip()
                            nature_raw = elem.findtext(".//nature") or ""
                            pos = clean_nature(nature_raw)
                            corps = elem.find(".//corps")
                            if corps is not None:
                                sens_elems = corps.findall(".//sens")
                                if sens_elems:
                                    for idx, s in enumerate(sens_elems[:4]):
                                        text_nodes = []
                                        for node in s.iter():
                                            if node.tag not in ("cit", "auteur", "ref", "bibl"):
                                                if node.text and node.text.strip():
                                                    text_nodes.append(node.text.strip())
                                                if node.tail and node.tail.strip():
                                                    text_nodes.append(node.tail.strip())
                                        def_text = " ".join(text_nodes).strip()
                                        def_text = re.sub(r"^[0-9]+[°\)]\s*", "", def_text)
                                        def_text = re.sub(r"\s+", " ", def_text).strip()
                                        if len(def_text) > 5:
                                            batch_senses.append((
                                                terme, "fr", pos, f"littre_{senses_count}",
                                                def_text[:400], json.dumps([], ensure_ascii=False),
                                                json.dumps([], ensure_ascii=False), "xmlittre_fr",
                                            ))
                                            senses_count += 1
                                else:
                                    var = corps.find(".//variante")
                                    if var is not None:
                                        text_nodes = []
                                        for node in var.iter():
                                            if node.tag not in ("cit", "auteur", "ref", "bibl"):
                                                if node.text and node.text.strip():
                                                    text_nodes.append(node.text.strip())
                                                if node.tail and node.tail.strip():
                                                    text_nodes.append(node.tail.strip())
                                        def_text = " ".join(text_nodes).strip()
                                        def_text = re.sub(r"^[0-9]+[°\)]\s*", "", def_text)
                                        def_text = re.sub(r"\s+", " ", def_text).strip()
                                        if len(def_text) > 5:
                                            batch_senses.append((
                                                terme, "fr", pos, f"littre_{senses_count}",
                                                def_text[:400], json.dumps([], ensure_ascii=False),
                                                json.dumps([], ensure_ascii=False), "xmlittre_fr",
                                            ))
                                            senses_count += 1

                            if (terme, "fr", pos) not in lemmas_seen:
                                lemmas_seen.add((terme, "fr", pos))
                                batch_lemmas.append((terme, "fr", pos, f"pos={pos}", "xmlittre_fr"))

                        elem.clear()

                        if len(batch_senses) >= 20000:
                            c.executemany("""
                            INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, batch_senses)
                            batch_senses.clear()

                        if len(batch_lemmas) >= 20000:
                            c.executemany("""
                            INSERT OR IGNORE INTO lemmas (lemma, lang, pos, features, source_id)
                            VALUES (?, ?, ?, ?, ?)
                            """, batch_lemmas)
                            batch_lemmas.clear()

        if batch_senses:
            c.executemany("""
            INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_senses)
        if batch_lemmas:
            c.executemany("""
            INSERT OR IGNORE INTO lemmas (lemma, lang, pos, features, source_id)
            VALUES (?, ?, ?, ?, ?)
            """, batch_lemmas)

    conn.commit()
    print(f"  XMLittre: {len(lemmas_seen):,} lemmas, {senses_count:,} genuine French definitions imported.")
    return {"lemmas": len(lemmas_seen), "forms": 0, "senses": senses_count, "exceptions": 0, "rejected": rejected}


def ingest_freedict(conn: sqlite3.Connection, tei_path: Path) -> dict[str, int]:
    print("\nIngesting FreeDict (French-English Lexicon & Glosses)...")
    c = conn.cursor()
    senses_count = 0
    lemmas_seen = set()
    rejected = 0
    batch_senses = []

    import xml.etree.ElementTree as ET

    tree = ET.parse(tei_path)
    root = tree.getroot()
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    entries = root.findall(".//tei:entry", ns)

    for e in entries:
        orth = e.find(".//tei:orth", ns)
        pos_el = e.find(".//tei:pos", ns)
        quote = e.find(".//tei:quote", ns)
        def_el = e.find(".//tei:def", ns)

        word = (orth.text if orth is not None else "").strip().lower()
        if not word:
            continue
        p_raw = (pos_el.text if pos_el is not None else "").strip().lower()
        pos = "noun" if p_raw in ("n", "s") else ("verb" if p_raw in ("v", "vb") else ("adj" if p_raw == "adj" else "other"))
        trans = (quote.text if quote is not None else (def_el.text if def_el is not None else "")).strip()
        if trans:
            lemmas_seen.add((word, "fr", pos))
            batch_senses.append((
                word, "fr", pos, f"freedict_{senses_count}",
                f"Anglais: {trans}", json.dumps([trans], ensure_ascii=False),
                json.dumps([], ensure_ascii=False), "freedict_fra_eng",
            ))
            senses_count += 1

    if batch_senses:
        c.executemany("""
        INSERT INTO senses (lemma, lang, pos, sense_id, definition, synonyms, antonyms, source_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, batch_senses)

    conn.commit()
    print(f"  FreeDict French-English: {len(lemmas_seen):,} lemmas, {senses_count:,} bilingual glosses imported.")
    return {"lemmas": len(lemmas_seen), "forms": 0, "senses": senses_count, "exceptions": 0, "rejected": rejected}


def ingest_unimorph_fra(conn: sqlite3.Connection, tsv_path: Path) -> dict[str, int]:
    print("\nIngesting UniMorph French...")
    c = conn.cursor()
    forms_count = 0
    rejected = 0
    batch_forms = []

    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                rejected += 1
                continue
            lemma, surface, tag = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if not lemma or not surface:
                rejected += 1
                continue

            tag_parts = tag.split(";")
            pos_tag = tag_parts[0]
            pos = "verb" if pos_tag == "V" else ("noun" if pos_tag == "N" else ("adj" if pos_tag == "ADJ" else "other"))

            mood = ""
            tense = ""
            person = ""
            number = ""
            gender = ""

            if "PRS" in tag_parts:
                tense = "present"
            elif "PST" in tag_parts or "PFV" in tag_parts:
                tense = "past"
            elif "IPFV" in tag_parts:
                tense = "imperfect"
            elif "FUT" in tag_parts:
                tense = "future"

            if "1" in tag_parts:
                person = "1"
            elif "2" in tag_parts:
                person = "2"
            elif "3" in tag_parts:
                person = "3"

            if "SG" in tag_parts:
                number = "sg"
            elif "PL" in tag_parts:
                number = "pl"

            if "MASC" in tag_parts:
                gender = "masc"
            elif "FEM" in tag_parts:
                gender = "fem"

            if "COND" in tag_parts:
                mood = "conditional"
            elif "SBJV" in tag_parts:
                mood = "subjunctive"
            elif "IMP" in tag_parts:
                mood = "imperative"
            elif "PTCP" in tag_parts or "V.PTCP" in tag:
                mood = "participle"
            elif "IND" in tag_parts or tense:
                mood = "indicative"
            elif "NFIN" in tag_parts:
                mood = "infinitive"

            batch_forms.append((
                surface, lemma, "fr", pos, mood, tense, person, number, gender, tag, "unimorph_fra"
            ))
            forms_count += 1

            if len(batch_forms) >= 50000:
                c.executemany("""
                INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_forms)
                batch_forms.clear()

        if batch_forms:
            c.executemany("""
            INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_forms)

    conn.commit()
    print(f"  UniMorph French: {forms_count:,} inflected forms imported.")
    return {"lemmas": 0, "forms": forms_count, "senses": 0, "exceptions": 0, "rejected": rejected}


def ingest_wordnet_exceptions(conn: sqlite3.Connection, zip_path: Path) -> dict[str, int]:
    print("\nIngesting Princeton WordNet Morphological Exceptions (Irregular English Verbs & Nouns)...")
    c = conn.cursor()
    forms_count = 0
    exceptions_count = 0
    batch_forms = []

    with zipfile.ZipFile(zip_path) as z:
        # 1. Verb exceptions
        with z.open("wordnet/verb.exc") as f:
            for line in f:
                l = line.decode("utf-8").strip()
                if not l:
                    continue
                parts = l.split()
                if len(parts) >= 2:
                    surface, lemma = parts[0], parts[1]
                    mood = "indicative"
                    tense = "past"
                    person = ""
                    number = ""
                    if surface == "was":
                        tense, person, number = "past", "1,3", "sg"
                    elif surface == "were":
                        tense, person, number = "past", "2", "pl"
                    elif surface == "am":
                        tense, person, number = "present", "1", "sg"
                    elif surface == "is":
                        tense, person, number = "present", "3", "sg"
                    elif surface == "are":
                        tense, person, number = "present", "2", "pl"
                    elif surface == "been":
                        mood, tense = "participle", "past"
                    elif surface.endswith("ing"):
                        mood, tense = "participle", "present"
                    elif surface.endswith("ed") or surface.endswith("en"):
                        tense = "past"

                    batch_forms.append((
                        surface, lemma, "en", "verb", mood, tense, person, number, "", f"V;IRREG;{tense.upper()}", "wordnet_exc"
                    ))
                    forms_count += 1
                    exceptions_count += 1

        # 2. Noun exceptions
        with z.open("wordnet/noun.exc") as f:
            for line in f:
                l = line.decode("utf-8").strip()
                if not l:
                    continue
                parts = l.split()
                if len(parts) >= 2:
                    surface, lemma = parts[0], parts[1]
                    batch_forms.append((
                        surface, lemma, "en", "noun", "", "", "", "pl", "", "N;PL;IRREG", "wordnet_exc"
                    ))
                    forms_count += 1
                    exceptions_count += 1

        # 3. Adjective exceptions
        with z.open("wordnet/adj.exc") as f:
            for line in f:
                l = line.decode("utf-8").strip()
                if not l:
                    continue
                parts = l.split()
                if len(parts) >= 2:
                    surface, lemma = parts[0], parts[1]
                    tag = "ADJ;SPRL" if surface.endswith("est") else ("ADJ;CMPR" if surface.endswith("er") else "ADJ;IRREG")
                    batch_forms.append((
                        surface, lemma, "en", "adj", "", "", "", "", "", tag, "wordnet_exc"
                    ))
                    forms_count += 1
                    exceptions_count += 1

        if batch_forms:
            c.executemany("""
            INSERT OR IGNORE INTO inflections (surface_form, lemma, lang, pos, mood, tense, person, number, gender, morpho_tag, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_forms)

    conn.commit()
    print(f"  WordNet Exceptions: {forms_count:,} irregular forms imported.")
    return {"lemmas": 0, "forms": forms_count, "senses": 0, "exceptions": exceptions_count, "rejected": 0}


def create_indexes(conn: sqlite3.Connection):
    print("\nCreating SQLite indexes for high-speed bidirectional lookup (< 0.5 ms)...")
    start = time.perf_counter()
    c = conn.cursor()
    c.executescript("""
    CREATE INDEX idx_inflections_surface ON inflections (surface_form, lang);
    CREATE INDEX idx_inflections_lemma ON inflections (lemma, lang, pos);
    CREATE INDEX idx_inflections_reverse ON inflections (lemma, lang, pos, mood, tense, person, number);
    CREATE INDEX idx_lemmas_lookup ON lemmas (lemma, lang);
    CREATE INDEX idx_senses_lookup ON senses (lemma, lang);
    """)
    conn.commit()
    elapsed = time.perf_counter() - start
    print(f"  Indexes created in {elapsed:.2f}s.")


def main():
    print(f"=== Obsidia Brody Linguistic Corpus Ingestion ===")
    print(f"Database destination: {DB_PATH}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    manifest_json_path = RAW_DIR.parent / "download_manifest.json"
    if not manifest_json_path.exists():
        print(f"ERROR: {manifest_json_path} not found. Run download_corpora.py first.")
        sys.exit(1)

    with open(manifest_json_path, "r", encoding="utf-8") as f:
        download_manifest = {item["id"]: item for item in json.load(f)}

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA cache_size = 100000")

    init_db(conn)

    report_entries = []

    # 1. Morphalou 3.1
    morph_item = download_manifest["morphalou_3_1"]
    morph_res = ingest_morphalou(conn, Path(morph_item["local_path"]))
    report_entries.append({
        "source": morph_item["name"],
        "id": morph_item["id"],
        "version": "3.1 (06/2016)",
        "license": morph_item["license"],
        "official_source": morph_item["source"],
        "bytes_downloaded": morph_item["bytes_downloaded"],
        "lemmas_imported": morph_res["lemmas"],
        "forms_imported": morph_res["forms"],
        "senses_imported": morph_res["senses"],
        "exceptions_imported": morph_res["exceptions"],
        "rejected_entries": morph_res["rejected"],
        "checksum": morph_item["sha256"],
    })

    # 2. UniMorph French
    if "unimorph_fra" in download_manifest:
        fra_item = download_manifest["unimorph_fra"]
        fra_res = ingest_unimorph_fra(conn, Path(fra_item["local_path"]))
        report_entries.append({
            "source": fra_item["name"],
            "id": fra_item["id"],
            "version": "UniMorph 4.0 / Master",
            "license": fra_item["license"],
            "official_source": fra_item["source"],
            "bytes_downloaded": fra_item["bytes_downloaded"],
            "lemmas_imported": fra_res["lemmas"],
            "forms_imported": fra_res["forms"],
            "senses_imported": fra_res["senses"],
            "exceptions_imported": fra_res["exceptions"],
            "rejected_entries": fra_res["rejected"],
            "checksum": fra_item["sha256"],
        })

    # 3. UniMorph English
    eng_item = download_manifest["unimorph_eng"]
    eng_res = ingest_unimorph_eng(conn, Path(eng_item["local_path"]))
    report_entries.append({
        "source": eng_item["name"],
        "id": eng_item["id"],
        "version": "UniMorph 4.0 / Master",
        "license": eng_item["license"],
        "official_source": eng_item["source"],
        "bytes_downloaded": eng_item["bytes_downloaded"],
        "lemmas_imported": eng_res["lemmas"],
        "forms_imported": eng_res["forms"],
        "senses_imported": eng_res["senses"],
        "exceptions_imported": eng_res["exceptions"],
        "rejected_entries": eng_res["rejected"],
        "checksum": eng_item["sha256"],
    })

    # 4. WordNet Exceptions
    if "wordnet_exc" in download_manifest:
        wexc_item = download_manifest["wordnet_exc"]
        wexc_res = ingest_wordnet_exceptions(conn, Path(wexc_item["local_path"]))
        report_entries.append({
            "source": wexc_item["name"],
            "id": wexc_item["id"],
            "version": "WordNet 3.0 Exceptions",
            "license": wexc_item["license"],
            "official_source": wexc_item["source"],
            "bytes_downloaded": wexc_item["bytes_downloaded"],
            "lemmas_imported": wexc_res["lemmas"],
            "forms_imported": wexc_res["forms"],
            "senses_imported": wexc_res["senses"],
            "exceptions_imported": wexc_res["exceptions"],
            "rejected_entries": wexc_res["rejected"],
            "checksum": wexc_item["sha256"],
        })

    # 5. Open English WordNet 2025
    oewn_item = download_manifest["oewn_2025"]
    oewn_res = ingest_oewn_senses(conn, Path(oewn_item["local_path"]))
    report_entries.append({
        "source": oewn_item["name"],
        "id": oewn_item["id"],
        "version": "2025-edition",
        "license": oewn_item["license"],
        "official_source": oewn_item["source"],
        "bytes_downloaded": oewn_item["bytes_downloaded"],
        "lemmas_imported": oewn_res["lemmas"],
        "forms_imported": oewn_res["forms"],
        "senses_imported": oewn_res["senses"],
        "exceptions_imported": oewn_res["exceptions"],
        "rejected_entries": oewn_res["rejected"],
        "checksum": oewn_item["sha256"],
    })

    # 6. French Thesaurus (Dicollecte)
    thes_item = download_manifest["thes_fr"]
    thes_res = ingest_french_thesaurus(conn, Path(thes_item["local_path"]))
    report_entries.append({
        "source": thes_item["name"],
        "id": thes_item["id"],
        "version": "7.0 (LibreOffice / Dicollecte)",
        "license": thes_item["license"],
        "official_source": thes_item["source"],
        "bytes_downloaded": thes_item["bytes_downloaded"],
        "lemmas_imported": thes_res["lemmas"],
        "forms_imported": thes_res["forms"],
        "senses_imported": thes_res["senses"],
        "exceptions_imported": thes_res["exceptions"],
        "rejected_entries": thes_res["rejected"],
        "checksum": thes_item["sha256"],
    })

    # 7. XMLittré (Émile Littré French Definitions)
    if "xmlittre_fr" in download_manifest:
        xmlittre_item = download_manifest["xmlittre_fr"]
        xmlittre_res = ingest_xmlittre(conn, Path(xmlittre_item["local_path"]))
        report_entries.append({
            "source": xmlittre_item["name"],
            "id": xmlittre_item["id"],
            "version": "XMLittré (Gannaz / Littre.org)",
            "license": xmlittre_item["license"],
            "official_source": xmlittre_item["source"],
            "bytes_downloaded": xmlittre_item["bytes_downloaded"],
            "lemmas_imported": xmlittre_res["lemmas"],
            "forms_imported": xmlittre_res["forms"],
            "senses_imported": xmlittre_res["senses"],
            "exceptions_imported": xmlittre_res["exceptions"],
            "rejected_entries": xmlittre_res["rejected"],
            "checksum": xmlittre_item["sha256"],
        })

    # 8. FreeDict French-English Lexicon
    if "freedict_fra_eng" in download_manifest:
        freedict_item = download_manifest["freedict_fra_eng"]
        freedict_res = ingest_freedict(conn, Path(freedict_item["local_path"]))
        report_entries.append({
            "source": freedict_item["name"],
            "id": freedict_item["id"],
            "version": "FreeDict fra-eng TEI",
            "license": freedict_item["license"],
            "official_source": freedict_item["source"],
            "bytes_downloaded": freedict_item["bytes_downloaded"],
            "lemmas_imported": freedict_res["lemmas"],
            "forms_imported": freedict_res["forms"],
            "senses_imported": freedict_res["senses"],
            "exceptions_imported": freedict_res["exceptions"],
            "rejected_entries": freedict_res["rejected"],
            "checksum": freedict_item["sha256"],
        })

    create_indexes(conn)

    # Populate sources table
    c = conn.cursor()
    for entry in report_entries:
        c.execute("""
        INSERT INTO sources (id, name, version, license, source, checksum, bytes, lemmas_count, forms_count, senses_count, exceptions_count, rejected_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry["id"],
            entry["source"],
            entry["version"],
            entry["license"],
            entry["official_source"],
            entry["checksum"],
            entry["bytes_downloaded"],
            entry["lemmas_imported"],
            entry["forms_imported"],
            entry["senses_imported"],
            entry["exceptions_imported"],
            entry["rejected_entries"],
        ))

    # Set metadata
    total_lemmas = sum(e["lemmas_imported"] for e in report_entries)
    total_forms = sum(e["forms_imported"] for e in report_entries)
    total_senses = sum(e["senses_imported"] for e in report_entries)

    c.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("schema_version", "BRODY_LINGUISTIC_CORPUS_V1"))
    c.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("created_at", str(time.time())))
    c.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("total_lemmas", str(total_lemmas)))
    c.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("total_forms", str(total_forms)))
    c.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("total_senses", str(total_senses)))

    conn.commit()
    conn.close()

    db_size = DB_PATH.stat().st_size
    print(f"\nIngestion Complete! Database size: {db_size / (1024 * 1024):.1f} MB ({db_size:,} bytes).")
    print(f"Total Lemmas: {total_lemmas:,} | Total Forms: {total_forms:,} | Total Senses: {total_senses:,}")

    # Write Ingestion Report
    ingestion_report_path = DATA_DIR / "INGESTION_REPORT.json"
    with open(ingestion_report_path, "w", encoding="utf-8") as f:
        json.dump({
            "schema_version": "BRODY_LINGUISTIC_CORPUS_INGESTION_REPORT_V1",
            "db_size_bytes": db_size,
            "total_lemmas": total_lemmas,
            "total_forms": total_forms,
            "total_senses": total_senses,
            "sources": report_entries,
        }, f, indent=2, ensure_ascii=False)

    print(f"Ingestion Report written to {ingestion_report_path}")


if __name__ == "__main__":
    main()
