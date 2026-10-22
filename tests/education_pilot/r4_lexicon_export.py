"""Deterministic minimal lexicon export for the Oxygen R4 student (preregistration §7).

Rule-based selection only (never a word list):
  1. senses     WHERE source_id='thes_fr' AND lang='fr'     -> lemma, pos, sense_id, synonyms
  2. inflections WHERE source_id='morphalou_3_1' AND lang='fr' -> DISTINCT surface_form, lemma, pos
Excluded: XMLittre, UniMorph French, OEWN, FreeDict, UniMorph English, WordNet exceptions.
Variant M-CIBLE: entries of every taught target lemma removed, and every form that the export
lemmatises to a target removed from the other lemmas' synonym lists.

The source database is opened read-only (mode=ro&immutable=1) and never modified. The export is
PRIVATE research material: write it outside the repository.

Usage: python -B tests/education_pilot/r4_lexicon_export.py <output_dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "linguistic_corpus" / "lexicon.db"
DB_SHA256 = "0a58bdb4c9094f06aaa92f3c545a9c9ef411eeeb4daf52f06b54c191e2eca16a"
SOURCES = {
    "thes_fr": {"name": "French Thesaurus (Dicollecte / LibreOffice)", "version": "7.0",
                "license": "MPL 2.0 / LGPL 3.0 / GPL 3.0", "attribution": "Dicollecte (Olivier R.) / LibreOffice Dictionaries"},
    "morphalou_3_1": {"name": "Morphalou", "version": "3.1 (06/2016)", "license": "LGPL-LR",
                      "attribution": "ATILF CNRS / ORTOLANG"},
}
EXCLUDED = ["xmlittre_fr", "unimorph_fra", "oewn_2025", "freedict_fra_eng", "unimorph_eng", "wordnet_exc"]


def canonical_line(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def target_lemmas() -> list[str]:
    sys.path.insert(0, str(ROOT))
    from tests.education_pilot import _pilot_data as D
    return sorted({it[1] for it in D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS})


def read_rows(conn):
    thes = []
    for lemma, pos, sense_id, synonyms in conn.execute(
            "SELECT lemma, pos, sense_id, synonyms FROM senses WHERE source_id='thes_fr' AND lang='fr'"):
        thes.append({"lemma": lemma, "pos": pos, "sense_id": sense_id, "synonyms": sorted(set(json.loads(synonyms or "[]")))})
    thes.sort(key=lambda r: (r["lemma"], r["pos"], r["sense_id"]))
    morph = [{"surface_form": s, "lemma": l, "pos": p} for s, l, p in conn.execute(
        "SELECT DISTINCT surface_form, lemma, pos FROM inflections WHERE source_id='morphalou_3_1' AND lang='fr'")]
    morph.sort(key=lambda r: (r["surface_form"], r["lemma"], r["pos"]))
    return thes, morph


def mask_targets(thes, morph, targets):
    target_forms = {r["surface_form"] for r in morph if r["lemma"] in targets} | set(targets)
    masked = []
    for r in thes:
        if r["lemma"] in targets:
            continue
        masked.append({**r, "synonyms": [s for s in r["synonyms"] if s not in target_forms]})
    return masked, sorted(target_forms)


def write_jsonl(path: pathlib.Path, rows) -> str:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(canonical_line(r))
    return sha256_file(path)


def export(out: pathlib.Path) -> dict:
    if ROOT in out.resolve().parents or out.resolve() == ROOT:
        raise SystemExit("export must be written outside the repository")
    db_sha = sha256_file(DB)
    if db_sha != DB_SHA256:
        raise SystemExit(f"HOLD: lexicon.db fingerprint {db_sha} differs from the preregistered one")
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro&immutable=1", uri=True)
    thes, morph = read_rows(conn)
    conn.close()
    targets = target_lemmas()
    thes_masked, masked_forms = mask_targets(thes, morph, targets)
    out.mkdir(parents=True, exist_ok=True)
    lemma_count = {}
    for r in morph:
        lemma_count.setdefault(r["surface_form"], set()).add(r["lemma"])
    files = {
        "thes_fr.jsonl": write_jsonl(out / "thes_fr.jsonl", thes),
        "morphalou_fr.jsonl": write_jsonl(out / "morphalou_fr.jsonl", morph),
        "thes_fr_mcible.jsonl": write_jsonl(out / "thes_fr_mcible.jsonl", thes_masked),
    }
    manifest = {
        "schema": "OXYGEN_R4_LEXICON_EXPORT_V1",
        "status": "PRIVATE_RESEARCH_EXPORT_NOT_FOR_REDISTRIBUTION",
        "source_db": {"path": "data/linguistic_corpus/lexicon.db", "sha256": db_sha, "opened": "mode=ro&immutable=1"},
        "rules": ["senses WHERE source_id='thes_fr' AND lang='fr' -> lemma,pos,sense_id,synonyms(sorted,distinct)",
                  "inflections WHERE source_id='morphalou_3_1' AND lang='fr' -> DISTINCT surface_form,lemma,pos",
                  "rows sorted lexicographically; one canonical JSON object per line (sort_keys, compact, UTF-8, LF)",
                  "M-CIBLE: drop entries of taught target lemmas; drop their forms from other synonym lists"],
        "sources": SOURCES, "excluded_sources": EXCLUDED,
        "sense_id_note": "thes_fr sense_id values are sequential import numbers, local to this database version",
        "mcible_targets": targets, "mcible_masked_form_count": len(masked_forms),
        "counts": {"thes_fr": len(thes), "morphalou_fr": len(morph), "thes_fr_mcible": len(thes_masked),
                   "ambiguous_forms": sum(1 for v in lemma_count.values() if len(v) > 1)},
        "files": files,
        "tool_sha256": sha256_file(pathlib.Path(__file__)),
    }
    (out / "MANIFEST.json").write_text(canonical_line(manifest), encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    m = export(pathlib.Path(sys.argv[1]))
    print(json.dumps({"files": m["files"], "counts": m["counts"]}, ensure_ascii=False))
