# Overlay-Only Manifest — V3/V4 Final Completion

**Date:** 2026-05-19  
**Zip target:** OBSIDIA_X108_FULL_STACK_FINAL_COMPLETION_OVERLAY_PATCH.zip  
**Includes:** New/modified files only — not full repo

---

## Included Paths

```
periphery/
tests/
connectors/brody_memory_readonly_flow.py
connectors/context_packet_flow.py
connectors/interface_ready_memory_flow.py
connectors/memory_feedback_candidate_flow.py
scripts/
docs/civilization/
docs/FINAL_COMPLETION_REPORT.md
docs/TEST_RESULTS_FINAL.md
docs/DO_NOT_TOUCH_REPORT_FINAL.md
docs/DEFERRED_PHASES_CLOSED_REPORT.md
docs/PY_COMPILE_REPORT_FINAL.md
docs/OVERLAY_ONLY_MANIFEST.md
```

## Excluded

- `.env`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`
- Old zips (`*.zip`)
- `_local_audits/` (runtime audit trails)
- `audit/` (runtime audit trails)
- Credentials, secrets, tokens, API keys, Neo4j credentials
- `Demo-obsidia-x108-proof/`
- `.claude/` (session state)

## Protected Files (never included)

- `sigma/guard.py`, `sigma/contracts.py`, `sigma/protocols.py`, `sigma/aggregation.py`
- `proofs/lean/`, `formal/tla/`, `merkle_seal.json`
