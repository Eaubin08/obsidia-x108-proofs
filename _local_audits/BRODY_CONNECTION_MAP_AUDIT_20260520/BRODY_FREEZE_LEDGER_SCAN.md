# Brody Freeze Ledger Scan
**Audit date**: 2026-05-20
**Scope**: docs/freeze/, _local_audits/EXTERNAL_BENCHMARKS/, memory/

---

## Confirmed Freeze Entries

### F01 — BFCL V1 Offline Path
- **freeze_id**: BFCL_BRODY_LOCAL_ADAPTER_V1_PASS_OFFLINE_PATH_FROZEN
- **path**: `_external_benchmarks/03_bfcl/brody_adapter/`
- **date**: prior session
- **result/status**: PASS
- **claims**: BFCL simple_python_0 load → parse → offline candidate → normalize → compare — all pass
- **proof level**: OFFLINE_PATH_ONLY
- **related module**: `brody_call_local.py` / `_bfcl_offline_parse()`
- **runtime_bound**: false
- **still valid**: true
- **notes**: This proves the harness chain, NOT Brody full runtime. Must not be cited as runtime proof.

---

### F02 — BFCL V2 Full Runtime (Blocked)
- **freeze_id**: BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON
- **path**: `_external_benchmarks/03_bfcl/brody_adapter_v2_full_runtime/`
- **date**: 2026-05-20
- **result/status**: BLOCKED_NO_CANDIDATE_FROM_FULL_RUNTIME
- **claims**: Three Foundations runtime callable, all snapshots present, boundary invariants hold; Brody does NOT produce structured `CANDIDATE_TOOL_CALL`
- **proof level**: API_LIVE_CHECK
- **related module**: `brody_true_voice_adapter.py`, `brody_call_full_runtime_v2.py`
- **runtime_bound**: true (runtime called, but no candidate output)
- **still valid**: true
- **notes**: Missing layer = `tool_call_candidate` readonly adapter. Next P1 priority.

---

### F03 — Three Foundations Runtime Stabilized
- **freeze_id**: BRODY_THREE_FOUNDATIONS_RUNTIME_STABILIZED_FREEZE_PASS
- **path**: `_local_audits/EXTERNAL_BENCHMARKS/BRODY_THREE_FOUNDATIONS_RUNTIME_STABILIZED/`
- **date**: 2026-05-20
- **result/status**: PASS
- **claims**: Foundation A (READY_LOCAL_SOURCES_WITH_GRAPHITI_LIVE_BLOCKED), Foundation B (READY), Foundation C (READY); /api/brody/chat live; 1224/1224 non-sigma tests pass; UTF8_CLEAN=true
- **proof level**: TESTED_RUNTIME
- **related module**: `brody_full_runtime_reconnect.py`, all three Foundation adapters
- **runtime_bound**: true
- **still valid**: true
- **notes**: Honest: GRAPHITI_LIVE_BLOCKED=true, NEO4J_PASSWORD_NOT_SET.

---

### F04 — UTF-8 Mojibake Audit
- **freeze_id**: BRODY_UTF8_MOJIBAKE_FIX_PASS
- **path**: `docs/freeze/BRODY_UTF8_MOJIBAKE_AUDIT.md`, `docs/freeze/BRODY_UTF8_MOJIBAKE_FIX_FREEZE_REPORT.md`
- **date**: 2026-05-20
- **result/status**: PASS — SOURCE_CAUSE=POWERSHELL_RENDERING_ONLY
- **claims**: No code-level mojibake; Windows pipe cp1252 rendering artifact only; 7 defensive tests pass
- **proof level**: TESTED_RUNTIME
- **related module**: `brody_text_encoding.py`, `tests/api/test_brody_utf8_no_mojibake.py`
- **runtime_bound**: true
- **still valid**: true
- **notes**: API bytes are clean. Zero code changes needed.

---

### F05 — Brody Real Memory→Response Chain Patch
- **freeze_id**: BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_READY_FOR_OPERATOR_RETEST
- **path**: `docs/freeze/BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_RETEST_AFTER_PATCH.md`
- **date**: 2026-05-20
- **result/status**: PASS — LOCAL_GRAPHITI_INDEX_FALLBACK active
- **claims**: 1261/1261 tests pass; query ladder working (primary_query → fallbacks); effective_query returns 8 hits; followup strict patterns applied
- **proof level**: TESTED_RUNTIME
- **related module**: `brody_memory_response_chain_adapter.py`, `brody_semantic_query_router.py`
- **runtime_bound**: true
- **still valid**: true
- **notes**: Neo4j offline → local 3267-record index used.

---

### F06 — Foundation A: Project Memory
- **freeze_id**: BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE
- **path**: `docs/freeze/BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.md`
- **proof level**: SMOKE_ONLY
- **runtime_bound**: true
- **still valid**: true — local sources ready, graphiti_live blocked

---

### F07 — Foundation B: Session Memory / Followup
- **freeze_id**: BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE
- **path**: `docs/freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.md`
- **proof level**: SMOKE_ONLY
- **runtime_bound**: true
- **still valid**: true — strict followup patterns now applied

---

### F08 — Foundation C: True Response Structure
- **freeze_id**: BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE
- **path**: `docs/freeze/BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.md`
- **proof level**: SMOKE_ONLY
- **runtime_bound**: true
- **still valid**: true — terminal_structural_dialogue bound

---

### F09 — SWE-Bench WSL Gold Smoke
- **freeze_id**: SWE_BENCH_WSL_GOLD_SMOKE_PASS
- **path**: `_local_audits/EXTERNAL_BENCHMARKS/freezes/SWE_BENCH_WSL_GOLD_SMOKE/`
- **proof level**: SMOKE_ONLY (install + run — WSL required)
- **runtime_bound**: false (Brody not involved)
- **still valid**: unknown — depends on WSL Docker state

---

### F10 — Terminal-Bench Local Oracle Smoke V7
- **freeze_id**: TERMINAL_BENCH_LOCAL_ORACLE_SMOKE_V7_PASS
- **path**: `_local_audits/EXTERNAL_BENCHMARKS/freezes/TERMINAL_BENCH_LOCAL_ORACLE_SMOKE_V7/`
- **proof level**: SMOKE_ONLY (oracle only, not Brody)
- **runtime_bound**: false
- **still valid**: unknown

---

### F11 — Graphiti V20 / Readonly Index
- **path**: `docs/freeze/BRODY_GRAPHITI_LIVE_READONLY_REPORT.md`
- **claims**: Local readonly index available; Neo4j live blocked by password
- **proof level**: ADAPTER_ONLY
- **runtime_bound**: true (local index 3267 records accessible)
- **still valid**: true — index loaded successfully at audit time

---

### F12 — Operator Loop / Command Gate
- **path**: `docs/freeze/BRODY_EXISTING_AUTOMATION_MODULES_AUDIT.md`, `BRODY_AUTOMATION_LAYER_BINDING_REPORT.md`
- **claims**: automation_snapshot present; operator_loop field present in snapshot
- **proof level**: ADAPTER_ONLY
- **runtime_bound**: partial (automation_snapshot in API, but operator_loop.status empty)
- **still valid**: true (structure bound; logic not yet active)

---

### F13 — Session Ledger + Presave Buffer
- **path**: `docs/freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.md`
- **claims**: Session ledger JSONL written locally; presave buffer staged
- **proof level**: SMOKE_ONLY
- **runtime_bound**: true
- **still valid**: true

---

### F14 — Memory Candidate Pipeline
- **path**: `docs/freeze/BRODY_AUTOMATION_SNAPSHOT_API_REPORT.md`
- **claims**: memory_candidate_pipeline field in automation_snapshot
- **proof level**: ADAPTER_ONLY
- **runtime_bound**: true (field present in API)
- **still valid**: true

---

### F15 — OS Trad / IR / Reverse
- **path**: `docs/freeze/BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md`
- **claims**: ir_candidate and translation_trace present in API response; OS Trad = language routing; IR = Intent Recognition; Reverse = no live reverse OS
- **proof level**: API_LIVE_CHECK
- **runtime_bound**: true (ir_candidate present in all 7 live test calls)
- **still valid**: true

---

## Summary Table

| ID | Freeze | Proof Level | Runtime Bound | Still Valid |
|----|--------|-------------|---------------|-------------|
| F01 | BFCL V1 offline | OFFLINE_PATH_ONLY | false | true |
| F02 | BFCL V2 blocked | API_LIVE_CHECK | partial | true |
| F03 | Three Foundations | TESTED_RUNTIME | true | true |
| F04 | UTF-8 Mojibake | TESTED_RUNTIME | true | true |
| F05 | Memory chain patch | TESTED_RUNTIME | true | true |
| F06 | Foundation A | SMOKE_ONLY | true | true |
| F07 | Foundation B | SMOKE_ONLY | true | true |
| F08 | Foundation C | SMOKE_ONLY | true | true |
| F09 | SWE-Bench WSL | SMOKE_ONLY | false | unknown |
| F10 | Terminal-Bench V7 | SMOKE_ONLY | false | unknown |
| F11 | Graphiti readonly | ADAPTER_ONLY | true | true |
| F12 | Operator loop | ADAPTER_ONLY | partial | true |
| F13 | Session ledger | SMOKE_ONLY | true | true |
| F14 | Memory candidate | ADAPTER_ONLY | true | true |
| F15 | OS Trad / IR | API_LIVE_CHECK | true | true |
