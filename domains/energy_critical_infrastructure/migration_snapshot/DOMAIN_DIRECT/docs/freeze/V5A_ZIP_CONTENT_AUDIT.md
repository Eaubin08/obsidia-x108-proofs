# V5A Zip Content Audit

**Date:** 2026-05-19
**Zip:** `OBSIDIA_X108_V5A_SINGLE_REPO_STABILIZATION_OVERLAY_PATCH.zip`

## Statistics

| Metric | Value |
|--------|-------|
| Total files | 104 |
| Size | 987 KB |
| Compression | DEFLATE |

## Contents

### demos/ (10 files)
- Internal flow package with 8 dry-run flow scripts

### scripts/ (7 files)
- CI verification scripts + run_all_local_flows.ps1

### docs/ (48 files)
- 5 freeze reports
- 13 blockchain docs
- 20 memory/brody/graphiti/context/interface docs
- 8 module READMEs
- 3 CI docs

### tests/ (16 files)
- 3 integration tests (demo flows)
- 10 non-sovereignty tests
- 3 manifest tests

### .github/ (1 file)
- CI workflow

### Manifest (2 files)
- Recursive SHA-256 manifest + root hash

### DeepSeek Audit (5 files)
- V3/V4 audit reports from DeepSeek

## Excluded

- `.env`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`
- `apps/` (UI workbench)
- `Demo-obsidia-x108-proof/` (archive)
- Old zip files
- Protected kernel files (sigma/, proofs/lean/, formal/tla/, merkle_seal.json)

## Verdict

**PATCH_INTEGRITY_PASS** — Clean overlay. < 1 MB. No forbidden content.
