# Protected Files CI Gate V1

**Script:** `scripts/check_protected_files.py`

## Protected Paths

```
sigma/guard.py
sigma/contracts.py
sigma/protocols.py
sigma/aggregation.py
proofs/lean/
formal/tla/
merkle_seal.json
```

## Gate Logic

Runs `git diff --exit-code` on all protected paths. Any modification → exit(1).

## Status

**PROTECTED_FILES_CI_GATE_PASS**
