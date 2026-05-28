# OBSIDIA F30.1B — WORKFLOW GOVERNANCE V5 DANGER CLASSIFICATION

Mode: DANGER_CLASSIFICATION_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `79f329c`
ZIP: `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5.zip`
Target: `src/obsidia_workflow_governance/repo_aware/obsidia_x108_repo_map.py`

## Summary

- Hits: 5
- False positives: 5
- Confirmed violations: 0
- Copy gate: `ALLOW_COPY_WITH_REVIEW_NOTE`

## Classified hits

- L78 `session.write_transaction` — `FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL`
  - confirmed_violation: False
  - reason: Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.
  - line: `"session.write_transaction",`
- L79 `execute_write` — `FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL`
  - confirmed_violation: False
  - reason: Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.
  - line: `"execute_write",`
- L85 `git commit` — `FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL`
  - confirmed_violation: False
  - reason: Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.
  - line: `"git commit",`
- L86 `git push` — `FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL`
  - confirmed_violation: False
  - reason: Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.
  - line: `"git push",`
- L87 `os.system(` — `FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL`
  - confirmed_violation: False
  - reason: Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.
  - line: `"os.system(",`

## Next

F30.2_COPY_V5_READONLY_MODULE

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
runtime_execute=false
emits_act=false
kernel_mutation=false
x108_mutation=false
```

## Status

F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_DONE
