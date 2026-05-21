# Recursive Manifest Report — V5A

**Date:** 2026-05-19
**Manifest:** `MANIFEST_SHA256_RECURSIVE.json`
**Root hash:** `MANIFEST_SHA256_RECURSIVE_ROOT.txt`

## Statistics

| Metric | Value |
|--------|-------|
| Total files | 22,877 |
| Total bytes | ~91 MB |
| Root hash (SHA-256) | Generated |

## Exclusions

- `.git/`
- `.venv/`
- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `.graph-memory/`
- `_local_audits/`
- `.claude/`
- `*.zip` files
- `*.pyc` files
- `package-lock.json`

## Verification

`python scripts/verify_recursive_manifest.py` — compares every entry's SHA-256 against current filesystem.

## Status

**RECURSIVE_MANIFEST_PASS** — Complete manifest generated and verifiable.
