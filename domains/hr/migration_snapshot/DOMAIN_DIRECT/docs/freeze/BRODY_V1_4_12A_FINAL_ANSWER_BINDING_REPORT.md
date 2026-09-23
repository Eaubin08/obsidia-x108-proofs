# BRODY V1.4.12A FINAL ANSWER BINDING REPORT
Date: 2026-05-20
Verdict: BRODY_V1_4_12A_FINAL_ANSWER_BINDING_REPORT_PASS

---

## Architecture bound

```
POST /api/brody/chat
  → run_brody_real_response_pipeline()       → response_md (local engine audit)
  → run_brody_v1_4_12a_final_answer()        → final_answer (natural chat)
  → safe_backend_response()                  → JSON with both fields
```

## Files

| File | Role | Status |
|---|---|---|
| `apps/obsidia_api/routes/brody.py` | Route — wires both layers | ACTIVE |
| `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py` | V1.4.12A natural response layer | ACTIVE |
| `apps/obsidia_api/brody_real_response_pipeline.py` | Local engine → response_md | ACTIVE |
| `apps/obsidia_api/safe_response.py` | Token stripping + sovereignty seal | ACTIVE |
| `apps/obsidia_api/runtime_loader.py` | Runtime component discovery | ACTIVE |
| `apps/obsidia_api/main.py` | FastAPI app, port 8000 | ACTIVE |

## Response contract (per /api/brody/chat)

| Field | Value | Source |
|---|---|---|
| `response` | = `final_answer` | V1.4.12A adapter |
| `final_answer` | Natural French/EN chat response | V1.4.12A adapter |
| `response_md` | Structured audit document | Local response engine |
| `voice_runtime` | `BRODY_OBSIDIEN_V1_4_12A` | Hardcoded |
| `source` | `REAL_BRODY_RUNTIME_NO_GRAPHITI` etc. | Runtime |
| `graphiti_status` | Explicit (LIVE or OFFLINE/BLOCKED) | Pipeline |
| `neo4j_status` | Explicit | Pipeline |
| `readonly` | `true` | Sovereignty seal |
| `emits_act` | `false` | Sovereignty seal |
| `emits_verdict` | `false` | Sovereignty seal |
| `memory_write` | `false` | Sovereignty seal |
| `kernel_mutation` | `false` | Sovereignty seal |
| `decision_authority` | `X108_ONLY` | Sovereignty seal |
| `allowed_to_decide` | `false` | Sovereignty seal |
| `advisory_only` | `true` | Sovereignty seal |

## V1.4.12A adapter key behaviours

- Detects intent: greeting, creator_claim, action_request, memory_query, x108_query, governance, proof_query, gencoin_query, worldcall, general_query
- `_QUERY_OVERRIDES` list prevents false-positive critical pressure on inspection queries
- `strip_forbidden_tokens()` sanitises ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT before returning
- FR/EN response pools — never raw tuple, never placeholder
- V1.4.12A module imported when available; safe local fallback when not

## Freeze source

```
C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate\
  zip1_sandbox_mutable\ZIP1_X108_MUTABLE_20260508_183610\periphery\
  brody_obsidien_v1_4_12_code_paste_guard_dialogue\
```

Module path: `_V1412A_DIR` in adapter — imported read-only, not modified.

## Phase 4 test results

```
tests/api/test_brody_v1_4_12a_final_answer.py       12 tests — PASS
tests/api/test_brody_v1_4_12a_creator_boundary.py   21 tests — PASS
tests/api/test_brody_final_answer_response_md_split.py 24 tests — PASS
TOTAL: 57 tests — 57 PASS / 0 FAIL
```

sovereignty_invariants: readonly=true | emits_act=false | decision_authority=X108_ONLY
