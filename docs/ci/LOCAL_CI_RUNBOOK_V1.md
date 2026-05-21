# Local CI Runbook V1

**Script:** `scripts/run_ci_local.ps1`

## Usage

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_ci_local.ps1
```

## Gates (in order)

1. Python compile check
2. Protected files diff check
3. Forbidden content scan
4. Full test suite (pytest)
5. Recursive manifest generation
6. Manifest verification

## Expected Output

All 6 gates print PASS (green) if clean. Any FAILURE (red) exits.

## Status

**LOCAL_CI_SCRIPT_PASS**
