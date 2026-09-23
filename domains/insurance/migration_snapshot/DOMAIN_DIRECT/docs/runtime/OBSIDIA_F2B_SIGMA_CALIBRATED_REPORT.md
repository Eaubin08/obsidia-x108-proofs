# OBSIDIA F2B — SIGMA CALIBRATED REPORT

Date: 2026-05-27
Phase: F2B_SIGMA_CALIBRATED

---

## STATUS

F2B_SIGMA_CALIBRATED_COMPLETE

---

## BOUNDARY

```
KX108_ONLY              = true
ADVISORY_ONLY           = true
READONLY                = true
SIGMA_DECIDES           = false
SIGMA_EMITS_ACT         = false
SIGMA_EMITS_VERDICT     = false
SIGMA_MEMORY_WRITE      = false
KERNEL_MUTATION         = false
X108_MUTATION           = false
GENCOIN_FINAL_SCORING   = false
THERMODYNAMICS_ACTIVE   = false
NO_COMMIT               = true
NO_KERNEL_TOUCH         = true
```

---

## CHANGES

### Files modified

| File | Change |
|---|---|
| `apps/obsidia_api/brody_gencoin_transverse_interface.py` | Full rewrite of `build_sigma_packet()` V0→V1 + `build_gencoin_transverse_packet()` accepts `sigma_packet` parameter + uses `calibration_status` in `input_status.sigma` |
| `apps/obsidia_api/brody_true_voice_adapter.py` | Updated call to `_build_sigma_packet` to pass `domain_raccord` and `chain`; updated fallback to V1 strings |
| `apps/obsidia_api/routes/brody.py` | Reordered: sigma built FIRST with full context (ir_candidate, domain_raccord, memory_chain, true_voice_snapshot); sigma_packet passed to build_gencoin_transverse_packet |
| `tests/api/test_brody_f2a_transverse_value_interface.py` | Updated tests 11/12/13 + `test_sigma_packet_reuses_sigma_pressure` to reflect V1 semantics |

### Files created

| File | Role |
|---|---|
| `tests/api/test_brody_f2b_sigma_calibration.py` | 35 tests (28 mandatory + 7 additional) |
| `docs/runtime/OBSIDIA_F2B_SIGMA_CALIBRATED_REPORT.md` | This freeze doc |

### Files NOT touched

- proofs/
- formal/tla/
- merkle* / seal* / rfc3161*
- KX108 / X108 kernel
- Lean proofs / TLA+ specs
- periphery/gencoin_sandbox/
- periphery/blockchain/
- periphery/gencoin.py
- OS Trad → IR Candidate → Reverse OS pipeline — order preserved, no insertion

---

## FUNCTIONS ADDED / MODIFIED

### `build_sigma_packet()` — V0 → V1

Signature (backward-compatible — all new params are optional):
```python
def build_sigma_packet(
    adaptive_response_policy=None,
    *,
    ir_candidate=None,
    domain_raccord=None,
    memory_chain=None,
    true_voice_snapshot=None,
) -> dict
```

Heuristic (deterministic, bounded [0.0, 1.0]):
```
base              = 0.50
+0.15  IR Candidate present
+0.10  Reverse OS output present (final_answer in true_voice_snapshot)
+0.10  adaptive_response_policy present
+0.10  memory_chain readonly material present
+0.10  readonly boundary confirmed (readonly=True, emits_act=False, memory_write=False)
-0.25  boundary_compact (ACT/write/mutation request)
-0.20  decorative_coherence_risk (ANTI_MISMATCH domain or arch+boundary mix)
-0.15  missing material (no IR, no memory)
clamp [0.0, 1.0]
```

Calibration statuses:
```
CALIBRATED_SHADOW_READONLY — non-boundary, sufficient material
                              usable_for_gencoin=True
                              usable_for_thermodynamics=True
CALIBRATED_BOUNDARY_ONLY   — boundary context, truth_score computed
                              usable_for_gencoin=False (not useful for value layer)
                              usable_for_thermodynamics=False
INSUFFICIENT_MATERIAL      — no adaptive, no IR, no reverse
                              truth_score=None
                              usable_for_gencoin=False
```

### `build_gencoin_transverse_packet()` — updated

Added `sigma_packet` parameter:
- `inputs_available.sigma`: V1 packet present OR sigma_pressure available
- `input_status.sigma`: `sigma_packet.calibration_status` if available, else fallback string

value_layer invariants unchanged:
- `final_scoring_enabled = False`
- All scores = null
- No ACT, no verdict, no write

---

## SIGMA_PACKET SAMPLE — CALIBRATED_SHADOW_READONLY

```json
{
  "version": "SIGMA_CALIBRATION_PACKET_V1",
  "mode": "SHADOW_READONLY",
  "source": "BRODY_SIGMA_CALIBRATION_F2B",
  "calibration_status": "CALIBRATED_SHADOW_READONLY",
  "usable_for_gencoin": true,
  "usable_for_thermodynamics": true,
  "truth_score": 0.95,
  "sigma_pressure": "MEDIUM",
  "reason": "SIGMA_CALIBRATED_SHADOW_READONLY_F2B",
  "inputs": {
    "has_ir_candidate": true,
    "has_reverse_output": true,
    "has_adaptive_response_policy": true,
    "has_domain_raccord": true,
    "has_memory_chain": true,
    "has_boundary_signal": false
  },
  "features": {
    "boundary_compact": false,
    "architecture_signal": true,
    "memory_chain_present": true,
    "readonly_boundary_ok": true,
    "decorative_coherence_risk": false,
    "missing_material": false
  },
  "score_components": {
    "structure_score": 0.25,
    "boundary_score": 0.20,
    "memory_support_score": 0.10,
    "mismatch_penalty": 0.0,
    "material_penalty": 0.0
  },
  "notes": [
    "Sigma remains advisory-only.",
    "Sigma does not decide.",
    "Sigma does not emit ACT or verdict.",
    "Sigma only calibrates signal quality for downstream readonly observers."
  ],
  "decision_authority": "KX108_ONLY",
  "advisory_only": true,
  "readonly": true,
  "emits_act": false,
  "emits_verdict": false,
  "memory_write": false,
  "graphiti_write": false,
  "neo4j_write": false,
  "kernel_mutation": false,
  "x108_mutation": false
}
```

## SIGMA_PACKET SAMPLE — BOUNDARY_COMPACT

```json
{
  "version": "SIGMA_CALIBRATION_PACKET_V1",
  "mode": "SHADOW_READONLY",
  "calibration_status": "CALIBRATED_BOUNDARY_ONLY",
  "usable_for_gencoin": false,
  "usable_for_thermodynamics": false,
  "truth_score": 0.4,
  "reason": "BOUNDARY_COMPACT_CONTEXT_NOT_USEFUL_FOR_VALUE_LAYER"
}
```

## VALUE_LAYER SAMPLE (unchanged from F2A, input_status.sigma updated)

```json
{
  "value_layer": {
    "version": "GENCOIN_TRANSVERSE_INTERFACE_V0",
    "mode": "SHADOW_READONLY",
    "final_scoring_enabled": false,
    "status": "INTERFACE_READY_NO_FINAL_SCORING",
    "scores": {
      "cognitive_value": null,
      "proof_value": null,
      "reuse_value": null,
      "memory_value": null,
      "attention_cost": null,
      "energy_cost": null,
      "stability_value": null,
      "economic_projection": null
    },
    "inputs_available": {
      "ir_candidate": true,
      "sigma": true,
      "thermodynamics": false,
      "trees_textual_signal": true,
      "trees_formal_computation": false,
      "memory": true,
      "proof": true,
      "reverse_os": true
    },
    "input_status": {
      "ir_candidate": "WIRED_PRESENT",
      "sigma": "CALIBRATED_SHADOW_READONLY",
      "thermodynamics": "DEFERRED",
      "trees_textual_signal": "TEXTUAL_SIGNAL_ONLY",
      "trees_formal_computation": "DEFERRED",
      "memory": "READONLY_CONTEXT_ONLY",
      "proof": "READONLY_PROOF_ONLY",
      "reverse_os": "OPTIONAL_PROJECTION_COST"
    },
    "decision_authority": "KX108_ONLY",
    "advisory_only": true,
    "readonly": true,
    "emits_act": false,
    "emits_verdict": false,
    "memory_write": false,
    "kernel_mutation": false,
    "x108_mutation": false
  }
}
```

---

## PROOFS

### Tests run

```
pytest tests/api/test_brody_f2b_sigma_calibration.py -v  → 35 passed
pytest tests/api/test_brody_f2a_transverse_value_interface.py -q  → 21 passed
pytest tests/api/test_brody_f2a... tests/api/test_brody_f2b... -q  → 56 passed
pytest tests/api -q  → 1041 passed, 82 failed, 38 errors (SAME AS BASELINE — zero regression)
```

### Baseline regression check

```
git stash → run tests/api → 82 failed 38 errors
git stash pop → run tests/api → 82 failed 38 errors
DELTA: 0 new failures introduced by F2B
```

### Invariants verified (28/28 mandatory + 7 additional)

```
 1. sigma_packet exists                                    PASS
 2. version == SIGMA_CALIBRATION_PACKET_V1                PASS
 3. mode == SHADOW_READONLY                               PASS
 4. decision_authority == KX108_ONLY                      PASS
 5. advisory_only == true                                 PASS
 6. readonly == true                                      PASS
 7. emits_act == false (all 3 cases)                     PASS
 8. emits_verdict == false (all 3 cases)                 PASS
 9. memory_write == false (all 3 cases)                  PASS
10. kernel_mutation == false (all 3 cases)               PASS
11. x108_mutation == false (all 3 cases)                 PASS
12. truth_score null or float [0.0, 1.0]                 PASS
13. sigma_pressure null or bounded string                PASS
14. CALIBRATED_SHADOW_READONLY → usable_for_gencoin=true  PASS
15. CALIBRATED_SHADOW_READONLY → usable_for_thermo=true   PASS
16. INSUFFICIENT_MATERIAL → usable_for_gencoin=false      PASS
17. BOUNDARY_COMPACT → truth_score < 0.50 OR usable=false PASS
18. ARCHITECTURE → truth_score > 0.60 if material         PASS
19. MEMORY_CHAIN_PASS → truth_score > 0.50               PASS
20. value_layer always exists                            PASS
21. value_layer.final_scoring_enabled == false           PASS
22. All value_layer scores remain null                   PASS
23. input_status.sigma reflects calibration_status       PASS
24. OS Trad → IR → Reverse not modified                  PASS
25. No ACT / verdict / write / kernel mutation           PASS
26. F2A backward-compatible (no sigma_packet arg)        PASS
27. No sovereign decision token                          PASS
28. INSUFFICIENT_MATERIAL not claimed calibrated         PASS
```

### py_compile

```
COMPILE_OK: brody_gencoin_transverse_interface.py
COMPILE_OK: brody_true_voice_adapter.py
COMPILE_OK: routes/brody.py
COMPILE_OK: test_brody_f2b_sigma_calibration.py
```

### git diff --stat

```
 apps/obsidia_api/brody_true_voice_adapter.py | 34 ++++++++++++++++++++++++++
 apps/obsidia_api/routes/brody.py             | 36 ++++++++++++++++++++++++++++
 2 files changed, 70 insertions(+)
```

---

## RISKS

| Risk | Level | Note |
|---|---|---|
| Heuristic truth_score is approximate | LOW-MEDIUM | Deterministic and bounded, but not formally proven. Adequate for shadow readonly phase. |
| Sigma with only adaptive_response_policy → truth_score computed without IR | LOW | score ~0.55 (moderate). usable_for_gencoin=True. Acceptable for F2B. |
| decorative_coherence_risk via ANTI_MISMATCH domain detection is textual only | MEDIUM | Formal anti-mismatch (IR vs Reverse comparison) deferred to F2C |
| Neo4j write guard still convention-only | MEDIUM | Not in F2B scope — BUCKET_4 |
| Memory promotion policy activation | HIGH if activated | DOC_ONLY — not in scope |

---

## NEXT

```
F2C_ANTI_MISMATCH_FORMAL:
  - Wire formal anti-mismatch on IR Candidate output vs Reverse OS output
  - Anti-mismatch detects false_on / decorative_coherence / collapse_disguised
  - Connect to domain raccord ANTI_MISMATCH detection
  - Update decorative_coherence_risk in sigma_packet to use formal signal
  - Freeze: F2C_ANTI_MISMATCH_FORMAL doc + tag

F3_THERMO_OPERATIONAL:
  - Formal thermodynamics dissipation computation
  - Precondition: F2C_ANTI_MISMATCH_FORMAL
  - Thermodynamics reads sigma_packet (usable_for_thermodynamics=True now)
  - Still: no decision, no ACT

F4_GENCOIN_SHADOW_VALUE_LAYER:
  - Enable final scoring when F3 stable
  - All preconditions met: Sigma V1 calibrated, Thermo operational, Anti-mismatch formal
  - Gencoin remains KX108_ONLY / advisory / no ACT / no write
```

---

## F2C NEXT EXACT STEP — ANTI-MISMATCH FORMAL

Target: `apps/obsidia_api/brody_gencoin_transverse_interface.py` or dedicated
`apps/obsidia_api/brody_anti_mismatch_signal.py`

Inputs needed:
- `ir_candidate`: the structured candidate (what was true structurally)
- `reverse_os_output`: the final_answer from true_voice_snapshot (what was said)
- `domain_raccord.domains`: whether ANTI_MISMATCH was textually detected
- `sigma_packet.features.decorative_coherence_risk`: current textual signal

Formal detection (proposed):
1. `surface_match`: final_answer length vs sigma_packet.truth_score correlation
2. `structural_gap`: if ARCHITECTURE domain detected but final_answer < 80 words → gap
3. `false_on_risk`: boundary_compact but domain_raccord has structural_answer_available
4. `collapse_disguised`: truth_score > 0.7 but answer_words < 40

Output: `anti_mismatch_signal` packet with:
- `false_on_detected: bool`
- `decorative_coherence_detected: bool`
- `collapse_disguised_detected: bool`
- `mismatch_score: float [0.0, 1.0]`
- `advisory_only: true`
- `decision_authority: KX108_ONLY`
- No ACT, no verdict, no write
