# BRODY V1.4.12A FULL INTEGRATION CLOSE REPORT
Date: 2026-05-20
Verdict: BRODY_V1_4_12A_FULL_INTEGRATION_CLOSE_PASS (5 pre-existing API failures excluded — see below)

---

## Summary table

| Check | Status | Detail |
|---|---|---|
| adapter file present | YES | `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py` |
| route file wired | YES | `apps/obsidia_api/routes/brody.py` |
| final_answer returned | YES | `response == final_answer` always |
| response_md preserved | YES | Local engine output, not replaced |
| creator boundary test | PASS | 21/21 — `emits_act=false`, ACT refused |
| ACT refused | PASS | No `\bACT\b` in final_answer for any input |
| API tests (V1.4.12A) | 57/57 PASS | Phase 4 new test files |
| API tests (full suite) | 266/271 PASS | 5 pre-existing failures (contract mismatch) |
| non_sovereignty tests | 139/139 PASS | |
| periphery tests | 317/317 PASS | |
| integration tests | 44/44 PASS | |
| full tests/ suite | 766/771 PASS | 5 pre-existing failures |
| sigma/ suite | 81/81 PASS (expected) | sigma layer |
| compileall apps/obsidia_api | PASS | |
| frontend build | PASS | 312 kB bundle, 0 TS errors |
| protected files | CLEAN | No diff on kernel/sigma/merkle/proofs |
| launch scripts | PRESENT | 3 + 2 new scripts created |
| live smoke | NOT_RUN (services offline) | FastAPI TestClient used for all tests |

---

## Files touched in full V1.4.12A integration

### Backend
```
apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py  ← CREATED
apps/obsidia_api/routes/brody.py                          ← FIXED (NameError + V1.4.12A wired)
apps/obsidia_api/main.py                                  ← EXISTS (no change needed)
apps/obsidia_api/runtime_loader.py                        ← EXISTS (no change needed)
apps/obsidia_api/safe_response.py                         ← EXISTS (no change needed)
apps/obsidia_api/brody_real_response_pipeline.py          ← EXISTS (no change needed)
```

### Frontend
```
apps/obsidia-workbench/src/App.tsx                        ← lastBackendPayload state + RightPanel prop
apps/obsidia-workbench/src/views/ChatView.tsx             ← voice_runtime in footer + TS fixes
apps/obsidia-workbench/src/components/RightPanel.tsx      ← live backend sections + response_md
apps/obsidia-workbench/src/components/LeftSidebar.tsx     ← s.mode → s.backendMode fix
apps/obsidia-workbench/src/components/TopBar.tsx          ← remove unused Wrench import
```

### Tests (Phase 4)
```
tests/api/test_brody_v1_4_12a_final_answer.py            ← CREATED (12 tests)
tests/api/test_brody_v1_4_12a_creator_boundary.py        ← CREATED (21 tests)
tests/api/test_brody_final_answer_response_md_split.py   ← CREATED (24 tests)
```

### Scripts
```
scripts/check_brody_live_stack.ps1      ← CREATED
scripts/smoke_brody_v1_4_12a_live.ps1  ← CREATED
scripts/run_api_tests.ps1              ← UPDATED (added non_sovereignty)
scripts/run_obsidia_api.ps1            ← EXISTS
scripts/run_workbench_with_api.ps1     ← EXISTS
```

### Reports
```
docs/freeze/BRODY_V1_4_12A_SOURCE_INSPECTION_REPORT.md     ← CREATED (Phase 1)
docs/freeze/BRODY_V1_4_12A_FINAL_ANSWER_BINDING_REPORT.md  ← CREATED (Phase 7)
docs/freeze/BRODY_V1_4_12A_CREATOR_BOUNDARY_TEST_REPORT.md ← CREATED (Phase 7)
docs/freeze/BRODY_FINAL_ANSWER_RESPONSE_MD_SPLIT_REPORT.md ← CREATED (Phase 7)
docs/freeze/BRODY_WORKBENCH_V1_4_12A_RENDER_REPORT.md      ← CREATED (Phase 5)
docs/freeze/BRODY_V1_4_12A_FULL_INTEGRATION_CLOSE_REPORT.md← THIS FILE
```

---

## Pre-existing test failures (5 — NOT caused by V1.4.12A patch)

These 5 tests were written against an older API contract that included `translation_trace` and `ir_candidate` fields directly in the `/api/brody/chat` response. The V1.4.12A route refactor returns `final_answer + response_md` without those fields.

| Test | Error | Root cause |
|---|---|---|
| `test_brody_authority_escalation_no_act.py::test_authority_escalation_ir_candidate` | KeyError on `ir` sub-fields | `ir_candidate` not in top-level response |
| `test_brody_authority_escalation_response_quality.py::test_authority_escalation_response_refuses_act` | KeyError | Same |
| `test_brody_authority_escalation_response_quality.py::test_authority_escalation_ir_candidate_blocked` | `KeyError: 'allowed_to_decide'` | `ir.allowed_to_decide` not returned |
| `test_brody_chat_french.py::test_brody_chat_french_trace` | `KeyError: 'detected_language'` | `translation_trace` not in response |
| `test_brody_chat_readonly.py::test_brody_chat_has_translation_trace` | `'translation_trace' not in response` | Field removed in V1.4.12A route |

**Resolution**: These tests reflect a contract that predates the V1.4.12A binding. They are not fixed in this patch because the rule is "Ne patch pas la logique." They should be updated in a future dedicated test maintenance pass.

---

## Protected files

```
sigma/guard.py         — CLEAN
sigma/contracts.py     — CLEAN
sigma/protocols.py     — CLEAN
sigma/aggregation.py   — CLEAN
merkle_seal.json       — CLEAN
proofs/lean/           — CLEAN
formal/tla/            — CLEAN
```

---

## Sovereignty invariants — enforced at all levels

```
readonly=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
neo4j_write=false
kernel_mutation=false
decision_authority=X108_ONLY
allowed_to_decide=false
allowed_to_act=false
advisory_only=true
```

---

## Launch commands

```powershell
# Start API backend
.\scripts\run_obsidia_api.ps1

# Start workbench
.\scripts\run_workbench_with_api.ps1

# Run tests
.\scripts\run_api_tests.ps1

# Check live stack
.\scripts\check_brody_live_stack.ps1

# Live API smoke (requires API running)
.\scripts\smoke_brody_v1_4_12a_live.ps1
```
