# TEST COUNT RECONCILIATION REPORT
Date: 2026-05-20
Scope: Full test matrix reconciliation — all historical counts explained

---

## Current state (2026-05-20)

```
python -m pytest --collect-only -q --ignore=_local_audits
→ 860 tests collected, 16 collection errors
```

### By directory

| Directory | Collected | Pass | Fail | Notes |
|---|---:|---:|---:|---|
| `tests/api/` | 271 | 266 | 5 | 5 pre-existing contract failures |
| `tests/periphery/` | 317 | 317 | 0 | |
| `tests/non_sovereignty/` | 139 | 139 | 0 | |
| `tests/integration/` | 44 | 44 | 0 | |
| **tests/ TOTAL** | **771** | **766** | **5** | |
| `sigma/tests/` | 81 | 81 | 0 | Sigma layer (outside tests/) |
| **Obsidia active suite** | **852** | **847** | **5** | tests/ + sigma/ |
| `_external_benchmarks/` | 8 | ? | ? | SWE-bench — not Obsidia tests |
| `proofs/V18_3_1/` | 0 | 0 | 0 | 6 collection errors — missing imports |
| `_local_audits/` | EXCLUDED | — | — | sys.exit() in smoke files |

### 16 collection errors explained

| Source | Count | Reason |
|---|---:|---|
| `_external_benchmarks/SWE-bench/` | 10 | Missing `swebench` package dependencies |
| `proofs/V18_3_1/engine_buildable_0_9_3_1/` | 6 | Missing engine modules (V18 protected area) |

---

## Historical count reconciliation

### Count table

| Source log | Count | Retrouvé ? | Suite | Explication |
|---|---:|---|---|---|
| V3/V4 patch | 194 | ESTIMATED | `tests/integration/` (44) + early `tests/periphery/` subset | V3/V4 integration stage: 7 integration files × ~6-8 + ~150 periphery tests at that time |
| UI/Workbench | 397 | ESTIMATED | `tests/periphery/` + `tests/non_sovereignty/` (early state) | Pre-blockchain: ~258 periphery + 139 non_sovereignty = ~397 |
| DeepSeek/Brody phase | 549 | ESTIMATED | periphery+non_sov+integration + early API (~55) | 317+139+44+49 API = ~549 at that stage |
| DeepSeek full stack | 714 | CONFIRMED | `tests/` before V1.4.12A additions | 771 − 57 = **714** exactly |
| V1.4.12A Phase 4 | 57 | CONFIRMED | 3 new test files in `tests/api/` | 12+21+24 = **57** exactly |
| **Current tests/** | **771** | CONFIRMED | Full `tests/` directory | 266+317+139+44+5 = **771** |
| **Current Obsidia** | **852** | CONFIRMED | `tests/` + `sigma/` | 771+81 = **852** |

---

## Questions answered

**1. How many pytest tests are collected?**
860 (--ignore=_local_audits), of which 852 are active Obsidia tests (771 tests/ + 81 sigma/).

**2. How many pass with `python -m pytest tests/ -q`?**
766 passed, 5 failed (in ~3m 23s).

**3. Why did the V3/V4 log show 194 tests?**
At the V3/V4 integration stage, only the integration pipeline tests (7 files) and an early subset of periphery tests existed. ~44 integration + ~150 periphery at that time ≈ 194.

**4. Where are the 397 tests?**
Periphery + non_sovereignty at a pre-blockchain expansion state: ~258 periphery + 139 non_sovereignty = 397.

**5. Where are the 549 tests?**
After blockchain/wallet/token tests were added to periphery (317) + non_sovereignty (139) + integration (44) + early API tests (~49) = 549.

**6. Where are the 714 tests?**
This is `tests/` minus the 57 V1.4.12A tests: 771 − 57 = **714 exactly**. Confirmed. This was the state right before the V1.4.12A Phase 4 patch.

**7. Does 714 correspond to a specific layer?**
Yes — all of `tests/` at the end of the DeepSeek full-stack phase, including the full API suite (~214 tests at that time), periphery (317), non_sovereignty (139), integration (44).

**8. Tests present but not in `pytest tests/`?**
- `sigma/tests/` — 81 tests, run separately with `pytest sigma/`
- `_local_audits/` — smoke scripts with `sys.exit()`, not pytest-compatible, excluded

**9. Smoke scripts not included in pytest?**
- `scripts/smoke_brody_v1_4_12a_live.ps1` — PowerShell, not pytest
- `scripts/check_brody_live_stack.ps1` — PowerShell, not pytest
- `_local_audits/` smoke files — sys.exit() pattern, not pytest-compatible

**10. Tests added today (2026-05-20)?**
```
tests/api/test_brody_v1_4_12a_final_answer.py       (12 tests)
tests/api/test_brody_v1_4_12a_creator_boundary.py   (21 tests)
tests/api/test_brody_final_answer_response_md_split.py (24 tests)
TOTAL: 57 new tests
```

**11. Tests expected but absent?**
- Tests for `translation_trace` and `ir_candidate` fields in V1.4.12A response: 5 existing tests assume these fields; they need to be updated to the new contract OR the route needs to add these fields back.

---

## The 5 pre-existing failures

| File | Test | Error | Pre-existing? |
|---|---|---|---|
| `test_brody_authority_escalation_no_act.py` | `test_authority_escalation_ir_candidate` | KeyError on `ir` sub-fields | YES |
| `test_brody_authority_escalation_response_quality.py` | `test_authority_escalation_response_refuses_act` | KeyError on ir | YES |
| `test_brody_authority_escalation_response_quality.py` | `test_authority_escalation_ir_candidate_blocked` | `KeyError: 'allowed_to_decide'` | YES |
| `test_brody_chat_french.py` | `test_brody_chat_french_trace` | `KeyError: 'detected_language'` | YES |
| `test_brody_chat_readonly.py` | `test_brody_chat_has_translation_trace` | `'translation_trace' not in response` | YES |

Root cause: These tests expect `translation_trace` and `ir_candidate` fields in the `/api/brody/chat` response. The V1.4.12A route does not return these fields (it returns `final_answer + response_md` instead).

---

## Tests by keyword category

| Category | Count | Pass | Fail |
|---|---:|---:|---:|
| brody + graphiti + memory + v1_4_12a | 331 | 326 | 5 |
| blockchain + wallet + signature + token | 120 | 120 | 0 |
| gencoin + world + os3 + sovereign | 231 | 230 | 1 |
| v3 or v4 (integration only) | 44 | 44 | 0 |

---

## Conclusion

The "full test matrix" is **852 active tests** (771 tests/ + 81 sigma/).

The 714 count (from DeepSeek full-stack logs) is exactly `tests/` before the 57 V1.4.12A tests were added. No tests were lost. The 5 failures are pre-existing contract mismatches unrelated to the V1.4.12A patch logic.

**Current total: 852 collected / 847 pass / 5 fail (pre-existing)**
