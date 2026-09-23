# OBSIDIA F3 — THERMODYNAMICS OPERATIONAL REPORT

Date: 2026-05-27
Phase: F3_THERMO_OPERATIONAL

---

## STATUS

F3_THERMO_OPERATIONAL_COMPLETE

---

## BOUNDARY

```
KX108_ONLY              = true
ADVISORY_ONLY           = true
READONLY                = true
THERMO_DECIDES          = false
THERMO_EMITS_ACT        = false
THERMO_EMITS_VERDICT    = false
THERMO_BLOCKS           = false
THERMO_MEMORY_WRITE     = false
KERNEL_MUTATION         = false
X108_MUTATION           = false
GENCOIN_FINAL_SCORING   = false
VALUE_LAYER_SCORES_NULL = true
NO_COMMIT               = true
NO_KERNEL_TOUCH         = true
OS_TRAD_IR_REVERSE_UNMODIFIED = true
```

---

## CHANGES

### Files created

| File | Role |
|---|---|
| `apps/obsidia_api/brody_thermodynamics_signal.py` | THERMODYNAMICS_PACKET_V1 module — 9 scores, stability_state, usable_for_gencoin |
| `tests/api/test_brody_f3_thermodynamics_operational.py` | 49 tests (38 mandatory + 11 additional) |
| `docs/runtime/OBSIDIA_F3_THERMO_OPERATIONAL_REPORT.md` | This freeze doc |

### Files modified

| File | Change |
|---|---|
| `apps/obsidia_api/brody_gencoin_transverse_interface.py` | `build_gencoin_transverse_packet()` accepts `thermodynamics_packet`; `inputs_available.thermodynamics` = True when THERMODYNAMICS_PACKET_V1 present; `input_status.thermodynamics` = stability_state; docstring updated |
| `apps/obsidia_api/routes/brody.py` | F2C 4-step pipeline extended to 5-step: step 4 = thermodynamics; step 5 = gencoin (receives thermodynamics_packet); `thermodynamics_packet` exposed in payload |

### Files NOT touched

- proofs/
- formal/tla/
- merkle* / seal* / rfc3161*
- KX108 / X108 kernel
- Lean proofs / TLA+ specs
- periphery/gencoin_sandbox/
- periphery/blockchain/
- periphery/gencoin.py
- periphery/energy_thermo.py (separate periphery concern — untouched)
- OS Trad → IR Candidate → Reverse OS pipeline — order preserved, no insertion
- brody_domain_raccord_adapter.py — THERMODYNAMICS domain textual detection unchanged
- brody_anti_mismatch_signal.py — unchanged
- brody_gencoin_transverse_interface.py:build_sigma_packet — unchanged

---

## FUNCTIONS ADDED / MODIFIED

### `build_thermodynamics_packet()` — NEW

```python
def build_thermodynamics_packet(
    *,
    sigma_packet=None,
    anti_mismatch_packet=None,
    ir_candidate=None,
    true_voice_snapshot=None,
    adaptive_response_policy=None,
    memory_chain=None,
    value_layer=None,
) -> dict
```

Returns `{"thermodynamics_packet": {...}}`.

Score computations (all deterministic, bounded [0.0, 1.0]):

```
entropy_score         = 1 - truth_score   (inverted sigma quality)
                      = 0.50              (if partial material, no truth_score)
                      = 1.0               (if insufficient)

mismatch_heat         = anti_mismatch_packet.mismatch_score  (or 0.0 if absent)

boundary_heat         = 0.40 if boundary_detected
                      + 0.30 if response_size==BOUNDARY_COMPACT (and not boundary_detected)
                      clamp [0.0, 1.0]

memory_friction       = 0.0  if USABLE_MATERIAL
                      = 0.25 if PARTIAL_MATERIAL
                      = 0.50 if absent or LOW

projection_cost       = 0.50 if answer_words > 800
                      = 0.30 if answer_words > 350
                      = 0.10 if answer_words < 80
                      = 0.0  otherwise (80..350)

pressure_load         = LOW → 0.20 | MEDIUM → 0.50 | HIGH → 0.80 | unknown → 0.30

dissipation_score     = mean(entropy, mismatch_heat, boundary_heat, memory_friction,
                             projection_cost, pressure_load)

instability_score     = max(mismatch_heat, boundary_heat, entropy_score)

coherence_temperature = mean(dissipation_score, instability_score, pressure_load)
```

Stability states:
```
INSUFFICIENT_MATERIAL — sigma absent or truth_score null
STABLE                — coherence_temperature < 0.30
WARM                  — 0.30 <= coherence_temperature < 0.50
HOT                   — 0.50 <= coherence_temperature < 0.70
UNSTABLE              — coherence_temperature >= 0.70
```

`usable_for_gencoin = True` only if:
- `thermodynamics_active = True`
- `sigma_packet.usable_for_thermodynamics = True`
- `anti_mismatch_risk_level != HIGH`
- `stability_state != INSUFFICIENT_MATERIAL`

`usable_for_gencoin = True` does **NOT** activate Gencoin final scoring.
It signals only that thermodynamics data is available for future readonly consumption.

### `build_gencoin_transverse_packet()` — updated

New parameter: `thermodynamics_packet=None`

Behavior:
- `inputs_available.thermodynamics = True` if `thermodynamics_packet.version == "THERMODYNAMICS_PACKET_V1"`
- `input_status.thermodynamics = thermodynamics_packet.stability_state` if present
- Else: `inputs_available.thermodynamics = False`, `input_status.thermodynamics = "DEFERRED"`
- `scores.energy_cost` remains `null`
- `final_scoring_enabled` remains `False`

### Route F3 pipeline — `routes/brody.py`

```
Step 1: sigma_initial = build_sigma_packet(...without anti_mismatch...)
Step 2: anti_mismatch = build_anti_mismatch_signal(...sigma_packet=sigma_initial...)
Step 3: sigma_final   = build_sigma_packet(...anti_mismatch_packet=anti_mismatch_packet...)
Step 4: thermodynamics = build_thermodynamics_packet(
            sigma_packet=sigma_final,
            anti_mismatch_packet=anti_mismatch_packet,
            ir_candidate, true_voice_snapshot, adaptive_response_policy, memory_chain)
Step 5: gencoin/value_layer = build_gencoin_transverse_packet(
            ...sigma_packet=sigma_final,
               thermodynamics_packet=thermodynamics_packet...)
```

---

## SIGMA / ANTI-MISMATCH IMPACT

- **Sigma unchanged as metric**: `build_sigma_packet` not modified for F3. It provides `truth_score` and `usable_for_thermodynamics` which thermodynamics reads.
- **Anti-Mismatch unchanged as signal**: `build_anti_mismatch_signal` not modified. It provides `mismatch_score` and `risk_level` which thermodynamics reads as `mismatch_heat`.
- **Thermodynamics reads both without modifying them**: Pure readonly consumer. Verified by test 34 and test 38.

---

## VALUE_LAYER

```
inputs_available.thermodynamics : True  (was always False/DEFERRED before F3)
input_status.thermodynamics     : stability_state (STABLE/WARM/HOT/UNSTABLE/INSUFFICIENT_MATERIAL)
scores.energy_cost              : null  (unchanged — no final scoring)
final_scoring_enabled           : false (unchanged)
All other scores                : null  (unchanged)
```

---

## THERMODYNAMICS_PACKET SAMPLE — STABLE

```json
{
  "thermodynamics_packet": {
    "version": "THERMODYNAMICS_PACKET_V1",
    "mode": "SHADOW_READONLY",
    "thermodynamics_active": true,
    "usable_for_gencoin": true,
    "usable_for_value_layer": true,
    "scores": {
      "entropy_score": 0.25,
      "dissipation_score": 0.217,
      "instability_score": 0.25,
      "coherence_temperature": 0.239,
      "pressure_load": 0.50,
      "mismatch_heat": 0.10,
      "boundary_heat": 0.0,
      "memory_friction": 0.0,
      "projection_cost": 0.0
    },
    "stability_state": "STABLE",
    "evidence": {
      "sigma_truth_score": 0.75,
      "sigma_calibration_status": "CALIBRATED_SHADOW_READONLY",
      "sigma_usable_for_thermodynamics": true,
      "mismatch_score": 0.10,
      "anti_mismatch_risk_level": "LOW",
      "boundary_detected": false,
      "answer_length_words": 150,
      "memory_material_quality": "USABLE_MATERIAL"
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

## THERMODYNAMICS_PACKET SAMPLE — INSUFFICIENT_MATERIAL

```json
{
  "thermodynamics_packet": {
    "version": "THERMODYNAMICS_PACKET_V1",
    "stability_state": "INSUFFICIENT_MATERIAL",
    "usable_for_gencoin": false,
    "usable_for_value_layer": false,
    "reason": "THERMO_INSUFFICIENT_SIGMA_ABSENT",
    "decision_authority": "KX108_ONLY",
    "emits_act": false
  }
}
```

## VALUE_LAYER SAMPLE (F3 — thermodynamics wired)

```json
{
  "value_layer": {
    "version": "GENCOIN_TRANSVERSE_INTERFACE_V0",
    "mode": "SHADOW_READONLY",
    "final_scoring_enabled": false,
    "scores": {
      "cognitive_value": null,
      "proof_value": null,
      "energy_cost": null,
      "economic_projection": null
    },
    "inputs_available": {
      "thermodynamics": true,
      "sigma": true,
      "ir_candidate": true
    },
    "input_status": {
      "thermodynamics": "STABLE",
      "sigma": "CALIBRATED_SHADOW_READONLY"
    },
    "decision_authority": "KX108_ONLY",
    "advisory_only": true,
    "readonly": true,
    "emits_act": false
  }
}
```

---

## PROOFS

### Tests run

```
pytest tests/api/test_brody_f3_thermodynamics_operational.py -v → 49 passed
pytest tests/api/test_brody_f2a... f2b... f2c... f3... -q       → 143 passed
pytest tests/api -q → 1128 passed, 82 failed, 38 errors (SAME AS BASELINE — zero regression)
```

### Baseline regression check

```
Baseline (F2C): 82 failed, 38 errors, 1079 passed
After F3:       82 failed, 38 errors, 1128 passed
DELTA:          +49 new passing tests (F3 suite), 0 new failures
```

### Invariants verified (38 mandatory + 11 additional = 49/49)

```
 1. thermodynamics_packet exists                                   PASS
 2. version == THERMODYNAMICS_PACKET_V1                            PASS
 3. mode == SHADOW_READONLY                                        PASS
 4. decision_authority == KX108_ONLY                               PASS
 5. advisory_only == true                                          PASS
 6. readonly == true                                               PASS
 7. emits_act == false                                             PASS
 8. emits_verdict == false                                         PASS
 9. memory_write == false                                          PASS
10. kernel_mutation == false                                       PASS
11. x108_mutation == false                                         PASS
12. thermodynamics_active == true                                  PASS
13. All 9 scores are floats [0.0, 1.0]                            PASS
14. entropy_score inversely correlated with truth_score            PASS
15. mismatch_heat == anti_mismatch_packet.mismatch_score           PASS
16. boundary_heat increases with boundary signals                  PASS
17. memory_friction increases with lower material quality          PASS
18. projection_cost correct for short / normal / very long answer  PASS
19. pressure_load LOW→0.20 / MEDIUM→0.50 / HIGH→0.80              PASS
20. dissipation_score bounded                                      PASS
21. instability_score bounded                                      PASS
22. coherence_temperature bounded                                  PASS
23. stability_state ∈ {STABLE,WARM,HOT,UNSTABLE,INSUFFICIENT_MATERIAL} PASS
24. usable_for_gencoin=False when sigma not usable                 PASS
25. usable_for_gencoin=False when anti_mismatch risk HIGH          PASS
26. usable_for_gencoin=True when sigma usable + mismatch low       PASS
27. value_layer.inputs_available.thermodynamics=True               PASS
28. value_layer.input_status.thermodynamics = stability_state      PASS
29. value_layer.scores.energy_cost remains null                    PASS
30. value_layer.final_scoring_enabled == False                     PASS
31. All Gencoin scores remain null                                 PASS
32. F2A backward compat (gencoin without thermo still works)       PASS
33. F2B sigma unchanged by thermo                                  PASS
34. F2C anti_mismatch not mutated by thermo                        PASS
35. No ACT / verdict / write / kernel mutation                     PASS
36. OS Trad → IR → Reverse unmodified                              PASS
37. Absent thermo shows DEFERRED, not claimed usable               PASS
38. Thermo does not modify sigma or value_layer scores             PASS
```

### py_compile

```
COMPILE_OK: brody_thermodynamics_signal.py
COMPILE_OK: brody_gencoin_transverse_interface.py
COMPILE_OK: routes/brody.py
COMPILE_OK: test_brody_f3_thermodynamics_operational.py
```

### git diff --stat

```
 apps/obsidia_api/brody_true_voice_adapter.py | 34 +++++++++++  (F2A/F2B)
 apps/obsidia_api/routes/brody.py             | 86 +++++++++++  (F2A/F2B/F2C/F3)
 2 files changed, 120 insertions(+)
 + brody_thermodynamics_signal.py          (new ~200 lines)
 + test_brody_f3_thermodynamics_operational.py (new ~310 lines)
 + docs/runtime/OBSIDIA_F3_THERMO_OPERATIONAL_REPORT.md (this file)
```

---

## RISKS

| Risk | Level | Note |
|---|---|---|
| All 9 scores are heuristic (no formal proof of calibration) | LOW-MEDIUM | Deterministic and bounded. Adequate for shadow readonly phase. |
| coherence_temperature threshold boundaries (0.30/0.50/0.70) are fixed | LOW | Conservative values. Can be tuned empirically in F4 or F5 if calibration data available. |
| energy_cost still null — real thermodynamic energy computation deferred | MEDIUM | Only shadow dissipation measured. F4 can begin to compute energy_cost when Gencoin final scoring gates open. |
| usable_for_gencoin=True does not prevent forgetting to check it in F4 | LOW | Must be enforced at F4 gating. Document explicitly in F4 spec. |
| memory_friction and projection_cost are surface-level heuristics | MEDIUM | Formal computation (token-level attention cost, semantic depth) deferred post-F4. |

---

## NEXT

```
F4_GENCOIN_SHADOW_VALUE_LAYER:
  - Preconditions now met: Sigma V1, Anti-Mismatch V1, Thermodynamics V1
  - Begin shadow Gencoin value scoring using thermo + sigma + anti_mismatch signals
  - cognitive_value, proof_value, memory_value can begin shadow computation
  - energy_cost: shadow projection using thermodynamics_packet.scores.dissipation_score
  - final_scoring_enabled remains false until explicit F5 gate
  - Gencoin remains KX108_ONLY / advisory / no ACT / no write

POSSIBLE F3B (optional calibration):
  - Tune coherence_temperature thresholds using empirical response data
  - Replace word-count projection_cost with token-level attention cost estimate
  - Requires thermodynamics operational stability across N sessions
```

---

## VALIDATION PHRASE

```
F3_THERMO_OPERATIONAL_PASS
THERMODYNAMICS_PACKET_V1=WIRED_SHADOW_READONLY
THERMO_SCORES=BOUNDED_DETERMINISTIC
STABILITY_STATE=BOUNDED_ENUM
USABLE_FOR_GENCOIN=true_IF_SIGMA_AND_MISMATCH_AND_MATERIAL_OK_ELSE_false
GENCOIN_FINAL_SCORING=false
VALUE_LAYER_ENERGY_COST_NULL=true
VALUE_LAYER_SCORES_NULL=true
KX108_ONLY=true
NO_ACT=true
NO_VERDICT=true
NO_MEMORY_WRITE=true
NO_KERNEL_TOUCH=true
NO_COMMIT=true
```

Thermodynamics est branché en shadow readonly comme couche de mesure de dissipation/stabilité, consommable par les futures couches de valeur, sans autorité décisionnelle.
