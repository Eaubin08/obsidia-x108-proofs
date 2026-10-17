# Obsidia / Brody — Real FR/EN Linguistic Corpus Rebuild Guide

This guide documents the exact, reproducible pipeline to acquire, verify, and build the real French and English lexical SQLite corpus for Brody (`data/linguistic_corpus/lexicon.db`).

---

## 1. Design & Boundary Principles

- **Zero Heavy Binaries in Git**: The generated SQLite database (`lexicon.db`, ~555 MB) and the raw compressed archives (`_external_sources/lexicon/raw/`, ~125 MB) are strictly excluded from version control via `.gitignore`.
- **Graceful Clone Fallback**: In a fresh clone without `lexicon.db`, the runtime (`app/semantic/lattice/lexical_corpus.py` and `lexicon.py`) falls back cleanly to the built-in closed deterministic grammar without errors.
- **Pinned Provenance & Checksums**: Every external resource is pinned with exact SHA-256 hashes, upstream source URLs, and official open licenses in `data/linguistic_corpus/DOWNLOAD_MANIFEST.json`.

---

## 2. Pinned Datasets & Licenses

| Dataset | Version | Lang | License | Upstream Source | SHA-256 |
|---|---|:---:|---|---|---|
| **Morphalou 3.1** | 3.1 (06/2016) | FR | LGPL-LR | ATILF CNRS / ORTOLANG | `4fc815cbf17aecdf1b47f6bbc263489a460fd8d11ae17e6b522336c72bd0e333` |
| **UniMorph French** | Master | FR | CC-BY-SA 4.0 | UniMorph Consortium | `4760fc36435a9ffba9b4de6f0787d8eca5b15022e6b141e3b242b129f0d88dcb` |
| **UniMorph English** | Master | EN | CC-BY-SA 4.0 | UniMorph Consortium | `20a191cefdc7cad6fa74b00f49d6f658684f17b14541aae372e5a3d5a8c15c67` |
| **Open English WordNet** | 2025-edition | EN | CC-BY 4.0 | Global WordNet Association | `7d749f6e2c39e6970e4997839dcf6e42fd281f3c2fae0171d2192bae8cfa4b51` |
| **French Thesaurus** | 7.0 | FR | MPL 2.0 / LGPL 3.0 | Dicollecte / LibreOffice | `52efa736c37f98d7f0abfe5dd4345b6f712880ca0ca664c15a8168d9475a0b46` |
| **WordNet Exceptions** | 3.0 | EN | WordNet / BSD | Princeton University / NLTK | `cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59` |
| **XMLittré** | XMLittré | FR | CC-BY-SA 3.0 / PD | François Gannaz / Littre.org | `7d2f4205b70b49d0d6503cb0f9b70b16ee428350be8f8c3260ad1d5876274448` |
| **FreeDict French-English** | TEI Master | FR/EN | GPL v2+ | FreeDict Project | `de9eb6e5756d994bca9bdb2a91bfc2bb8d8822d3387f5a3b586acc8d42133114` |

---

## 3. Rebuild Commands

### Step 1: Download & Verify Raw Datasets

Requires network access (~125 MB total across 8 official endpoints). Uses Python standard library only (`urllib.request`, `hashlib`).

```powershell
python scripts/download_linguistic_corpora.py
```

*Optional arguments:*
- `--raw-dir <path>`: Custom directory for storing raw archives (default: `_external_sources/lexicon/raw`).
- `--force`: Force redownload even if archives already exist.

If raw archives already exist in `--raw-dir`, the script automatically skips re-downloading and validates SHA-256 integrity in place.

### Step 2: Ingest & Build SQLite Corpus

Ingests lemmas, inflection paradigms, definitions, synonyms, and translations into `data/linguistic_corpus/lexicon.db`.

```powershell
python scripts/build_linguistic_corpus.py
```

*Optional arguments:*
- `--raw-dir <path>`: Source directory containing raw archives (default: `_external_sources/lexicon/raw`).
- `--db-path <path>`: Destination path for SQLite database (default: `data/linguistic_corpus/lexicon.db`).
- `--manifest <path>`: Path to manifest (default: `data/linguistic_corpus/DOWNLOAD_MANIFEST.json`).

*Output metrics:*
- **Total Lemmas**: 843,969
- **Total Inflected Forms**: 2,002,724
- **Total Senses / Definitions**: 307,892
- **Database Size**: ~555 MB (SQLite indexed B-trees)
- **Ingestion Time**: ~3-5 minutes (depending on disk I/O)

### Step 3: Verify Integrity & Runtime Lookups

Run the comprehensive linguistic test suite:

```powershell
python -m pytest tests/integration_cognition/test_brody_real_lexicon_and_corpus_red.py -v
```

All 55 tests must pass, confirming bidirectional lookups, irregular conjugation coverage, elision, compound tenses, and sub-millisecond query latency (< 0.5 ms).
