# CI Pipeline — X108 Periphery V1

**Workflow:** `.github/workflows/x108-periphery-ci.yml`
**Local runner:** `scripts/run_ci_local.ps1`

## Gates

| # | Gate | Command |
|---|------|---------|
| 1 | Python syntax | `python -m compileall periphery -q` |
| 2 | Protected files | `git diff --exit-code -- sigma/ ...` |
| 3 | Forbidden content | `python scripts/check_forbidden_content.py` |
| 4 | Full test suite | `python -m pytest tests/ -q --tb=short` |
| 5 | Generate manifest | `python scripts/generate_recursive_manifest.py` |
| 6 | Verify manifest | `python scripts/verify_recursive_manifest.py` |

## Status

**CI_PIPELINE_CREATED_PASS** — 6 gates, all automated.
