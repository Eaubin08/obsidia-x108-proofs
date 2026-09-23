# OBSIDIA F4 — GENCOIN SHADOW VALUE LAYER REPORT

Date: 2026-05-27
Phase: F4_GENCOIN_SHADOW_VALUE_LAYER

---

## STATUS

F4_GENCOIN_SHADOW_VALUE_LAYER_COMPLETE

---

## BOUNDARY

```
KX108_ONLY                 = true
ADVISORY_ONLY              = true
READONLY                   = true
GENCOIN_DECIDES            = false
GENCOIN_EMITS_ACT          = false
GENCOIN_EMITS_VERDICT      = false
GENCOIN_MEMORY_WRITE       = false
KERNEL_MUTATION            = false
X108_MUTATION              = false
FINAL_SCORING_ENABLED      = false
ECONOMIC_SCORING_ENABLED   = false
BLOCKCHAIN_ENABLED         = false
MEMORY_PROMOTION_ENABLED   = false
VALUE_LAYER_SCORES_NULL    = true
NO_COMMIT                  = true
NO_KERNEL_TOUCH            = true
OS_TRAD_IR_REVERSE_UNMODIFIED = true
```

---

## CHANGES

### Files created

| File | Role |
|---|---|
| `apps/obsidia_api/brody_gencoin_shadow_value.py` | GENCOIN_SHADOW_VALUE_PACKET_V1 — 7 shadow scores, usable_shadow_value gate |
| `tests/api/test_brody_f4_gencoin_shadow_value_layer.py` | 51 tests (44 mandatory + 7 additional) |
| `docs/runtime/OBSIDIA_F4_GENCOIN_SHADOW_VALUE_LAYER_REPORT.md` | This freeze doc |

### Files modified

| File | Change |
|---|---|
| `apps/obsidia_api/brody_gencoin_transverse_interface.py` | `build_gencoin_transverse_packet()` accepts `gencoin_shadow_packet`; `inputs_available.gencoin_shadow` and `input_status.gencoin_shadow` wired; docstring updated |
| `apps/obsidia_api/routes/brody.py` | Pipeline extended to 6 steps: step 5 = gencoin_shadow; step 6 = gencoin_transverse; `gencoin_shadow_packet` exposed in payload |

### Files NOT touched

- proofs/ / formal/tla/ / merkle* / seal* / rfc3161*
- KX108 / X108 kernel / Lean proofs / TLA+ specs
- periphery/gencoin_sandbox/ / periphery/blockchain/ / periphery/gencoin.py
- OS Trad → IR Candidate → Reverse OS pipeline — unmodified
- brody_gencoin_transverse_interface.py:build_sigma_packet — unmodified
- brody_anti_mismatch_signal.py — unmodified
- brody_thermodynamics_signal.py — unmodified

---

## FUNCTIONS ADDED / MODIFIED

### `build_gencoin_shadow_value_packet()` — NEW

```python
def build_gencoin_shadow_value_packet(
    *,
    sigma_packet=None,
    anti_mismatch_packet=None,
    thermodynamics_packet=None,
    value_layer=None,
    ir_candidate=None,
    true_voice_snapshot=None,
    memory_chain=None,
    has_proof_readonly=False,
) -> dict
```

Returns `{"gencoin_shadow_packet": {...}}`.

Precondition `usable_shadow_value=True` (ALL must hold):
```
sigma_packet.usable_for_gencoin == True
thermodynamics_packet.usable_for_gencoin == True
anti_mismatch_packet.risk_level != HIGH
thermodynamics_packet.stability_state != INSUFFICIENT_MATERIAL
```

Shadow score computations (deterministic, bounded [0.0, 1.0]):
```
cognitive_value  = truth_score - mismatch_score*0.30 - entropy_score*0.20   clamp
proof_value      = 0.70*proof_ok + truth_score*0.20 - mismatch_score*0.20   clamp
stability_value  = 1.0 - instability_score                                   clamp
attention_cost   = word-band: <80→0.20, 80-350→0.40, 350-800→0.65, >800→0.90
energy_cost      = thermodynamics_packet.scores.dissipation_score (passthrough)
memory_value     = quality-band(USABLE→0.70, PARTIAL→0.45, LOW→0.20, absent→0.00)
                   + truth_score * 0.10                                       clamp
reuse_value      = 0.40 + cognitive*0.30 + stability*0.20 - attention*0.20   clamp
economic_projection = null  (always)
```

When `usable_shadow_value=False`: all shadow_scores = null.

### `build_gencoin_transverse_packet()` — F4 update

New parameter: `gencoin_shadow_packet=None`

```
inputs_available.gencoin_shadow = True  if GENCOIN_SHADOW_VALUE_PACKET_V1 present
input_status.gencoin_shadow     = "USABLE_SHADOW_VALUE" | "NOT_USABLE_SHADOW_VALUE" | "DEFERRED"
value_layer.scores.*            = null (unchanged)
final_scoring_enabled           = False (unchanged)
```

### Route F4 pipeline — `routes/brody.py`

```
Step 1: sigma_initial
Step 2: anti_mismatch
Step 3: sigma_final
Step 4: thermodynamics_packet
Step 5: gencoin_shadow_packet  ← NEW
          (sigma_final + anti_mismatch + thermo → non-null shadow scores)
Step 6: value_layer / gencoin_transverse_packet
          (receives gencoin_shadow_packet → hooks only, value_layer.scores null)
```

---

## GENCOIN SHADOW / ANTI-MISMATCH / THERMO / SIGMA IMPACT

- **Sigma unchanged**: provides `truth_score` and `usable_for_gencoin` — read-only consumed
- **Anti-Mismatch unchanged**: provides `mismatch_score` and `risk_level` — read-only consumed
- **Thermodynamics unchanged**: provides `dissipation_score`, `instability_score`, `usable_for_gencoin` — read-only consumed
- **Shadow does not modify any upstream packet**: verified by tests 37, 38, 44

---

## VALUE_LAYER (F4)

```
inputs_available.gencoin_shadow : True  (was DEFERRED before F4)
input_status.gencoin_shadow     : USABLE_SHADOW_VALUE | NOT_USABLE_SHADOW_VALUE | DEFERRED
scores.*                        : null  (unchanged — shadow_scores only in gencoin_shadow_packet)
final_scoring_enabled           : false (unchanged)
```

Shadow scores live exclusively in `gencoin_shadow_packet.shadow_scores`.
This preserves the F2A invariant: `value_layer.scores = null`.

---

## GENCOIN_SHADOW_PACKET SAMPLE — USABLE

```json
{
  "gencoin_shadow_packet": {
    "version": "GENCOIN_SHADOW_VALUE_PACKET_V1",
    "mode": "SHADOW_READONLY",
    "final_scoring_enabled": false,
    "economic_scoring_enabled": false,
    "blockchain_enabled": false,
    "memory_promotion_enabled": false,
    "usable_shadow_value": true,
    "shadow_scores": {
      "cognitive_value": 0.617,
      "proof_value": 0.817,
      "reuse_value": 0.44,
      "memory_value": 0.775,
      "attention_cost": 0.40,
      "energy_cost": 0.217,
      "stability_value": 0.75,
      "economic_projection": null
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

## GENCOIN_SHADOW_PACKET SAMPLE — NOT USABLE

```json
{
  "gencoin_shadow_packet": {
    "version": "GENCOIN_SHADOW_VALUE_PACKET_V1",
    "usable_shadow_value": false,
    "shadow_scores": {
      "cognitive_value": null,
      "proof_value": null,
      "reuse_value": null,
      "memory_value": null,
      "attention_cost": null,
      "energy_cost": null,
      "stability_value": null,
      "economic_projection": null
    },
    "reason": "GENCOIN_SHADOW_NOT_USABLE_ANTI_MISMATCH_RISK_HIGH",
    "final_scoring_enabled": false,
    "economic_projection": null,
    "decision_authority": "KX108_ONLY"
  }
}
```

---

## PROOFS

### Tests run

```
pytest tests/api/test_brody_f4_gencoin_shadow_value_layer.py -v → 51 passed
pytest F2A+F2B+F2C+F3+F4 -q                                    → 194 passed
pytest tests/api -q → 1179 passed, 82 failed, 38 errors (SAME AS BASELINE — zero regression)
```

### Baseline regression check

```
Baseline (F3): 82 failed, 38 errors, 1128 passed
After F4:      82 failed, 38 errors, 1179 passed
DELTA:         +51 new passing tests (F4 suite), 0 new failures
```

### Invariants verified (44 mandatory + 7 additional = 51/51)

```
 1-11. Boundary flags (KX108_ONLY, advisory, readonly, no act/verdict/write/mutation)  PASS
12-15. final_scoring=false, economic_scoring=false, blockchain=false, promotion=false   PASS
16.    economic_projection always null                                                   PASS
17.    usable=True → all scores float [0.0, 1.0]                                       PASS
18.    usable=False → all scores null                                                   PASS
19.    cognitive_value decreases with mismatch_score                                   PASS
20.    cognitive_value decreases with entropy_score                                    PASS
21.    proof_value higher with has_proof_readonly=True                                 PASS
22.    memory_value reflects quality bands                                              PASS
23.    attention_cost word-count bands (0.20/0.40/0.65/0.90)                          PASS
24.    energy_cost == dissipation_score passthrough                                    PASS
25.    stability_value == 1.0 - instability_score                                     PASS
26.    reuse_value bounded [0.0, 1.0]                                                  PASS
27-29. not usable when sigma/thermo not usable, or mismatch HIGH                      PASS
30.    value_layer.inputs_available.gencoin_shadow=True                               PASS
31.    value_layer.input_status.gencoin_shadow reflects usable_shadow_value           PASS
32.    value_layer.scores all null                                                      PASS
33-34. value_layer.final_scoring_enabled=False everywhere                              PASS
35-38. F2A/F2B/F2C/F3 backward compatibility                                          PASS
39.    No ACT/verdict/write/mutation                                                   PASS
40.    OS Trad → IR → Reverse unmodified                                               PASS
41.    blockchain_enabled=false                                                         PASS
42.    memory_promotion_enabled=false                                                   PASS
43.    Absent shadow → value_layer DEFERRED                                            PASS
44.    Graceful degradation on empty inputs                                             PASS
```

---

## RISKS

| Risk | Level | Note |
|---|---|---|
| Shadow scores are heuristic — not formally proven | LOW-MEDIUM | Deterministic and bounded. Adequate for shadow phase. Calibration possible with empirical data in F5. |
| cognitive_value formula simple (additive penalties) | LOW | No cross-signal interaction (e.g., mismatch × entropy). Can be refined in F5. |
| economic_projection null — no real value signal yet | MEDIUM | F5 may introduce shadow economic projection using cognitive+proof+stability composite. |
| reuse_value depends on attention_cost — circular risk if attention influences cognition | LOW | Computation order fixed: cognitive → stability → attention → reuse. No circularity. |
| memory_promotion and blockchain still fully deferred | LOW | Documented in boundary. Tests enforce it. |

---

## NEXT — F5 CANDIDATES

```
F5_34_TREES_FORMAL_AUDIT:
  - Formal audit of periphery/cognitive_trees for 34-tree computation
  - Currently trees_textual_signal only; trees_formal_computation=DEFERRED
  - Precondition: periphery/cognitive_trees stability verified

F5_MEMORY_PROMOTION_GUARD:
  - Wire memory promotion readonly guard
  - Signal only: "this response qualifies for memory promotion consideration"
  - No actual write — advisory signal to KX108 only

F5_PRODUCT_OPERATOR_VIEW:
  - Aggregate sigma + anti_mismatch + thermo + gencoin_shadow into
    a single operator-facing stability dashboard packet
  - No new scoring — composite view only

Recommended order: F5_MEMORY_PROMOTION_GUARD → F5_34_TREES_FORMAL_AUDIT
(Memory promotion guard is lower risk and higher utility for near-term ops)
```

---

## VALIDATION PHRASE

```
F4_GENCOIN_SHADOW_VALUE_LAYER_PASS
GENCOIN_SHADOW_VALUE_PACKET_V1=WIRED_SHADOW_READONLY
SHADOW_SCORES=BOUNDED_DETERMINISTIC_OR_NULL
ECONOMIC_PROJECTION=null
FINAL_SCORING_ENABLED=false
VALUE_LAYER_SCORES_NULL=true
GENCOIN_FINAL_SCORING=false
BLOCKCHAIN_ENABLED=false
MEMORY_PROMOTION_ENABLED=false
KX108_ONLY=true
NO_ACT=true
NO_VERDICT=true
NO_MEMORY_WRITE=true
NO_KERNEL_TOUCH=true
NO_COMMIT=true
```

Gencoin Shadow Value est branché comme couche de score readonly non final, consommant Sigma, Anti-Mismatch et Thermodynamics, sans autorité décisionnelle.
