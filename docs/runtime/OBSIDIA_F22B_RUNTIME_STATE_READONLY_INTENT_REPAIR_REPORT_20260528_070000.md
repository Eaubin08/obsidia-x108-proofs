# OBSIDIA F22B — Runtime State Readonly Intent Repair Report

Date: 20260528_070000
CHECKPOINT: F22B_RUNTIME_STATE_READONLY_INTENT_REPAIR
MODE: APPLY (patch applied — awaiting commit validation)
STATUS: PASS_LOCAL_AWAITING_COMMIT

---

## F22A Root Cause Confirmed

Three independent false positives caused a readonly runtime description query to be
misclassified as a write/mutation request:

| # | Source file | Bug | Example trigger |
|---|-------------|-----|-----------------|
| 1 | `brody_domain_raccord_adapter.py::has_memory_write_request()` | `_has_any(low, write_terms)` — unguarded substring: `"decris"` contains `"ecris"` | "Décris les modules actifs" → MEMORY_WRITE_CANON_FREEZE |
| 2 | `routes/os_trad_ir_reverse.py::_risk_flags()` | `"act" in low` matches `"actifs"`, `"action"` | "modules actifs" → action_request |
| 3 | `brody_domain_raccord_adapter.py::build_domain_raccord_snapshot()` | No `RUNTIME_STATE_READONLY` category existed — readonly state queries fell through to PURE_RESPONSE, then domain raccord fired unchecked | no guard → MEMORY_WRITE_CANON_FREEZE added |

Secondary false positive (same root — substring match):
- `brody_v1_4_12a_final_answer_adapter.py::_QUERY_OVERRIDES` missing FR readonly terms ("decris", "etat", "statut") → `detect_critical_pressure()` misclassified readonly queries.

---

## F22A2 / F22A3 Integration

**F22A2** (git archaeology): Verbatia confirmed RUNTIME-MAPPED → NOT touched.
Continuum confirmed CODE-CONFIRMED-STUB → NOT touched.

**F22A3** (document source traceability): All 15 source documents analyzed.
- `readonly_context_guard.py` = `return True` (stub) → NOT reused (Option B blocked)
- LTO-16D D1/D16 "texte ≠ décision" → validates guard design (doctrinal basis)
- Doc08 "IA dans espace déjà sûr" → violated by the bug; restored by this fix
- RECOMMENDATION confirmed: OPTION C

---

## Why OPTION C

| Option | Verdict | Reason |
|--------|---------|--------|
| A — false positives only | INSUFFICIENT | No RUNTIME_STATE_READONLY category → domain raccord still routes incorrectly |
| B — reuse existing module | BLOCKED | `readonly_context_guard.py` body = `return True` — non-functional |
| C — guard minimal | **SELECTED** | 5 surgical changes, provably correct, no new ML dependencies |
| D — full refactor | FORBIDDEN | Explicitly excluded; unnecessary for substring fix |

---

## Why Not Clavage Now

Clavage (Doc05) requires JAX/XLA, cosine similarity on embedding vectors, and a full
ML pipeline (200+ lines). The F22B bug is a 3-line word-boundary regex fix. Clavage
is DEFERRED post-F22B. Its doctrinal role (watchdog syntaxique) is covered by the
minimal guard's word-boundary checks.

## Why Not Continuum Now

Continuum (`NodeContinuum` dataclass in `periphery/OBSIDIA_MMONDE.../03_MEMOIRE_MONDE_COSMOS_REFLEX/`)
is already covered by `session_memory_snapshot + temporal_context_snapshot` in the
cognitive modules registry (`COVERED_BY_EXISTING_MODULE, active=True`). No branching
needed for intent classification.

## Why Verbatia Was Not Touched

Verbatia = `FULLY_BRANCHED` = `brody_true_voice_adapter.py`. F22A2 confirmed it is
RUNTIME-MAPPED and active. The bug is upstream of Verbatia (in domain raccord + risk_flags,
before True Voice runs). Touching `brody_true_voice_adapter.py` would break the existing
True Voice pipeline.

---

## Files Modified

| File | Change | Type |
|------|--------|------|
| `apps/obsidia_api/brody_readonly_intent_guard.py` | New module — `detect_readonly_runtime_state_intent()` | **NEW** |
| `apps/obsidia_api/brody_domain_raccord_adapter.py` | `_has_any_word()` + word-boundary fix in `has_memory_write_request()` + guard integration in `build_domain_raccord_snapshot()` + RUNTIME_STATE_READONLY domain + text | **FIX** |
| `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py` | `_QUERY_OVERRIDES` expanded with FR readonly terms | **FIX** |
| `apps/obsidia_api/routes/os_trad_ir_reverse.py` | `import re` + `_risk_flags()` word-boundary for "act" + negation check for "ne propose aucune action" | **FIX** |
| `apps/obsidia_api/routes/brody.py` | Import guard + call `detect_readonly_runtime_state_intent()` + expose `readonly_intent_guard_packet` in response | **WIRE** |
| `tests/api/test_f22b_readonly_intent_guard.py` | 10 tests (9 unit + 1 live parity) | **NEW** |

---

## Tests Executed

### F22B test suite
```
tests/api/test_f22b_readonly_intent_guard.py  —  10/10 PASS
```

Tests:
- `test_decris_does_not_match_ecris_write` — PASS
- `test_actifs_does_not_match_act_action` — PASS
- `test_runtime_state_readonly_intent_detected` — PASS
- `test_graphiti_mention_readonly_not_graphiti_write` — PASS
- `test_memory_mention_readonly_not_memory_write` — PASS
- `test_freeze_dashboard_mention_not_freeze_promotion` — PASS
- `test_explicit_write_memory_still_triggers_boundary` — PASS
- `test_explicit_graphiti_write_still_triggers_boundary` — PASS
- `test_explicit_canon_promotion_still_triggers_boundary` — PASS
- `test_8000_8012_parity_runtime_state_intent` (live) — PASS

### Regression suite
```
tests/api/test_f21b_runtime_freeze_dashboard.py     — PASS
tests/api/test_f20b_gencoin_cognitive_ledger.py     — PASS
tests/cli/test_f20c_terminal_gencoin_ledger_display.py — PASS
tests/api/test_f19b_thermo_coherence_time_unified.py — PASS
tests/api/test_f18b_existing_reverse_os_wiring.py   — PASS
tests/api/test_f17b_graphiti_v20_frozen_reconnect.py — PASS
tests/api/test_f17c_brody_source_label.py           — PASS
tests/api/test_f16_live_sources.py                  — PASS
tests/api/test_brody_f12c_domain_raccord_priority.py — PASS
tests/api/test_brody_f10c_existing_command_packet_reconnect.py — PASS
tests/cli/  (all)                                   — PASS
tests/ui/   (all)                                   — PASS
Total regression: 55 API + 44 CLI/UI = 99 tests — 0 failures
```

### Frontend build
```
npm run build → ✓ built in 1.56s (0 TypeScript errors, 0 Vite errors)
```

---

## Runtime Validation — 8000 / 8012

Canonical test prompt:
```
"Décris ton état système actuel en lecture seule : modules actifs, mémoire, Graphiti,
IR, Reverse OS, Thermo, Gencoin, Dashboard runtime. Ne propose aucune action."
```

### Port 8000

| Field | Before F22B | After F22B |
|-------|-------------|------------|
| `readonly_intent_guard_packet.status` | (absent) | `RUNTIME_STATE_READONLY_INTENT_PASS` |
| `domain_raccord_snapshot.domains` | `["MEMORY_WRITE_CANON_FREEZE", ...]` | `["ARCHITECTURE_EXPLANATION", "RUNTIME_STATE_READONLY"]` |
| `domain_raccord_snapshot.write_boundary_required` | `true` | `false` |
| `domain_raccord_snapshot.voice_mode` | `DOMAIN_RACCORD_BOUNDARY` | `DOMAIN_RACCORD_READONLY_STATE` |
| `decision_authority` | `KX108_ONLY` ✓ | `KX108_ONLY` ✓ |
| `readonly` | `true` ✓ | `true` ✓ |
| `emits_act` | `false` ✓ | `false` ✓ |
| `memory_write` | `false` ✓ | `false` ✓ |
| `graphiti_write` | `false` ✓ | `false` ✓ |
| `kernel_mutation` | `false` ✓ | `false` ✓ |
| `x108_mutation` | `false` ✓ | `false` ✓ |

### Port 8012

Same results as 8000 — full parity confirmed.

Evidence files:
- `docs/runtime/F22B_RUNTIME_STATE_READONLY_8000.json`
- `docs/runtime/F22B_RUNTIME_STATE_READONLY_8012.json`
- `docs/runtime/F22B_TERMINAL_RUNTIME_STATE_READONLY_8000.txt`
- `docs/runtime/F22B_TERMINAL_RUNTIME_STATE_READONLY_8012.txt`

---

## Boundary — KX108_ONLY Maintained

```
KX108_ONLY=true
readonly=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
kernel_mutation=false
x108_mutation=false
```

The F22B patch does NOT:
- Write to memory, Graphiti, or Neo4j
- Emit ACT or verdict tokens
- Modify the kernel or X108 proofs
- Touch Lean / TLA+ / seal / RFC3161
- Refactor beyond the 5 specified changes

---

## Non-Regression F17→F21

All 55 regression tests from F17B through F21B pass without modification.
The guard is additive (new field `readonly_intent_guard_packet` in response),
not destructive. All 20 pre-existing top-level packets remain intact.

---

## STATUS: PASS_LOCAL_AWAITING_COMMIT

F22B patch is complete and verified locally.
No automatic commit.
Awaiting operator validation before `git commit`.
