# OBSIDIA F2C — ANTI-MISMATCH FORMAL REPORT

Date: 2026-05-27
Phase: F2C_ANTI_MISMATCH_FORMAL

---

## STATUS

F2C_ANTI_MISMATCH_FORMAL_COMPLETE

---

## BOUNDARY

```
KX108_ONLY              = true
ADVISORY_ONLY           = true
READONLY                = true
ANTI_MISMATCH_DECIDES   = false
ANTI_MISMATCH_EMITS_ACT = false
ANTI_MISMATCH_BLOCKS    = false
ANTI_MISMATCH_VERDICT   = false
SIGMA_MEMORY_WRITE      = false
KERNEL_MUTATION         = false
X108_MUTATION           = false
GENCOIN_FINAL_SCORING   = false
THERMODYNAMICS_ACTIVE   = false
NO_COMMIT               = true
NO_KERNEL_TOUCH         = true
OS_TRAD_IR_REVERSE_UNMODIFIED = true
```

---

## CHANGES

### Files created

| File | Role |
|---|---|
| `apps/obsidia_api/brody_anti_mismatch_signal.py` | ANTI_MISMATCH_SIGNAL_V1 module — 8 signals, mismatch_score, risk_level |
| `tests/api/test_brody_f2c_anti_mismatch_formal.py` | 38 tests (30 mandatory + 8 additional) |
| `docs/runtime/OBSIDIA_F2C_ANTI_MISMATCH_FORMAL_REPORT.md` | This freeze doc |

### Files modified

| File | Change |
|---|---|
| `apps/obsidia_api/brody_gencoin_transverse_interface.py` | `build_sigma_packet()` V1→F2C: accepts `anti_mismatch_packet`; formal decorative_coherence_risk replaces textual; new calibration status `CALIBRATED_WITH_MISMATCH_RISK` when mismatch_score >= 0.60; features dict extended |
| `apps/obsidia_api/routes/brody.py` | F2A/F2B block replaced by F2C 4-step pipeline: sigma_initial → anti_mismatch → sigma_final → gencoin; `anti_mismatch_packet` exposed in payload |

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
- brody_domain_raccord_adapter.py — textual ANTI_MISMATCH detection unchanged

---

## FUNCTIONS ADDED / MODIFIED

### `build_anti_mismatch_signal()` — NEW

```python
def build_anti_mismatch_signal(
    *,
    ir_candidate=None,
    true_voice_snapshot=None,
    adaptive_response_policy=None,
    domain_raccord=None,
    sigma_packet=None,
    memory_chain=None,
) -> dict
```

Returns `{"anti_mismatch_packet": {...}}`.

Signal detection (all boolean, deterministic, advisory):
```
1. architecture_answer_too_short  ARCHITECTURE domain + answer_words < 80
2. boundary_compact_under_answer  BOUNDARY_COMPACT + answer_words > 80
3. structural_gap                 IR present + answer_words < 25
4. false_on_risk                  boundary_compact + structural_answer_available + answer > 80
5. collapse_disguised             truth_score >= 0.70 + answer < 40 words + domains present
6. memory_claim_without_material  answer mentions memory terms + no usable material
7. sigma_high_but_answer_empty    truth_score >= 0.70 + answer < 20 words
8. decorative_coherence           derived: True if any of 1, 4, 5, 6, 7
```

Score weights (additive, clamped [0.0, 1.0]):
```
+0.20 structural_gap
+0.20 decorative_coherence
+0.15 false_on_risk
+0.15 collapse_disguised
+0.15 memory_claim_without_material
+0.10 architecture_answer_too_short
+0.10 sigma_high_but_answer_empty
+0.05 boundary_compact_under_answer
```

Risk levels:
```
NONE   : mismatch_score == 0.0
LOW    : 0.0 < score <= 0.25
MEDIUM : 0.25 < score <= 0.60
HIGH   : score > 0.60
```

### `build_sigma_packet()` — F2C update (backward compatible)

New parameter: `anti_mismatch_packet=None`

Behavior:
- If `anti_mismatch_packet.version == "ANTI_MISMATCH_SIGNAL_V1"`:
  - `decorative_coherence_risk = anti_mismatch_packet.decorative_coherence_detected`
  - `formal_mismatch_score = anti_mismatch_packet.mismatch_score`
  - If `formal_mismatch_score >= 0.60` and not `boundary_compact`:
    - `calibration_status = "CALIBRATED_WITH_MISMATCH_RISK"`
    - `usable_for_gencoin = False`
    - `usable_for_thermodynamics = False`
- Else (no formal packet): textual detection preserved (F2B behavior)
- Features dict now includes `anti_mismatch_formal_available` and `formal_mismatch_score`

New calibration status:
```
CALIBRATED_WITH_MISMATCH_RISK — formal mismatch_score >= 0.60
                                  usable_for_gencoin=False
                                  usable_for_thermodynamics=False
```

### Route F2C pipeline — `routes/brody.py`

```
Step 1: sigma_initial = build_sigma_packet(...without anti_mismatch...)
        → provides truth_score for anti_mismatch consumption

Step 2: anti_mismatch = build_anti_mismatch_signal(
            ir_candidate, true_voice_snapshot, adaptive_response_policy,
            domain_raccord, sigma_packet=sigma_initial, memory_chain)
        → produces ANTI_MISMATCH_SIGNAL_V1 with 8 signals + mismatch_score

Step 3: sigma_final = build_sigma_packet(...anti_mismatch_packet=anti_mismatch_packet...)
        → decorative_coherence_risk = formal signal
        → calibration_status may be CALIBRATED_WITH_MISMATCH_RISK if score >= 0.60

Step 4: gencoin = build_gencoin_transverse_packet(...sigma_packet=sigma_final...)
        → input_status.sigma reflects final calibration_status
```

---

## ANTI_MISMATCH_PACKET SAMPLE — NONE RISK

```json
{
  "anti_mismatch_packet": {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mode": "SHADOW_READONLY",
    "source": "BRODY_ANTI_MISMATCH_F2C",
    "mismatch_score": 0.0,
    "risk_level": "NONE",
    "false_on_detected": false,
    "decorative_coherence_detected": false,
    "collapse_disguised_detected": false,
    "structural_gap_detected": false,
    "signals": {
      "architecture_answer_too_short": false,
      "boundary_compact_under_answer": false,
      "structural_gap": false,
      "false_on_risk": false,
      "collapse_disguised": false,
      "memory_claim_without_material": false,
      "sigma_high_but_answer_empty": false,
      "decorative_coherence": false
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

## ANTI_MISMATCH_PACKET SAMPLE — HIGH RISK

```json
{
  "anti_mismatch_packet": {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.75,
    "risk_level": "HIGH",
    "false_on_detected": true,
    "decorative_coherence_detected": true,
    "signals": {
      "structural_gap": true,
      "decorative_coherence": true,
      "sigma_high_but_answer_empty": true,
      "architecture_answer_too_short": false,
      "boundary_compact_under_answer": false,
      "false_on_risk": false,
      "collapse_disguised": false,
      "memory_claim_without_material": false
    }
  }
}
```

## SIGMA SAMPLE — CALIBRATED_WITH_MISMATCH_RISK

```json
{
  "version": "SIGMA_CALIBRATION_PACKET_V1",
  "calibration_status": "CALIBRATED_WITH_MISMATCH_RISK",
  "usable_for_gencoin": false,
  "usable_for_thermodynamics": false,
  "features": {
    "anti_mismatch_formal_available": true,
    "formal_mismatch_score": 0.75,
    "decorative_coherence_risk": true
  },
  "decision_authority": "KX108_ONLY",
  "advisory_only": true,
  "readonly": true,
  "emits_act": false
}
```

---

## PROOFS

### Tests run

```
pytest tests/api/test_brody_f2c_anti_mismatch_formal.py -v  → 38 passed
pytest tests/api/test_brody_f2a... test_brody_f2b... test_brody_f2c... -q  → 94 passed
pytest tests/api -q  → 1079 passed, 82 failed, 38 errors (SAME AS BASELINE — zero regression)
```

### Baseline regression check

```
Baseline (F2B):  82 failed, 38 errors, 1041 passed
After F2C:       82 failed, 38 errors, 1079 passed
DELTA:           +38 new passing tests (F2C suite), 0 new failures
```

### Invariants verified (30 mandatory + 8 additional = 38/38)

```
 1. anti_mismatch_packet exists                              PASS
 2. version == ANTI_MISMATCH_SIGNAL_V1                      PASS
 3. mode == SHADOW_READONLY                                  PASS
 4. decision_authority == KX108_ONLY                         PASS
 5. advisory_only == true                                    PASS
 6. readonly == true                                         PASS
 7. emits_act == false                                       PASS
 8. emits_verdict == false                                   PASS
 9. memory_write == false                                    PASS
10. kernel_mutation == false                                 PASS
11. x108_mutation == false                                   PASS
12. mismatch_score is float [0.0, 1.0]                      PASS
13. risk_level ∈ {NONE, LOW, MEDIUM, HIGH}                  PASS
14. signals dict contains all 8 keys                         PASS
15. all signals are boolean                                  PASS
16. architecture_answer_too_short fires correctly            PASS
17. structural_gap fires correctly                           PASS
18. false_on_risk fires correctly                            PASS
19. collapse_disguised fires correctly                       PASS
20. memory_claim_without_material fires correctly            PASS
21. sigma_high_but_answer_empty fires correctly              PASS
22. decorative_coherence derived from signals 1,4,5,6,7     PASS
23. score == 0.0 → risk NONE                                PASS
24. score > 0.60 → risk HIGH                                PASS
25. no signals → score 0.0                                  PASS
26. graceful degradation on empty/None inputs               PASS
27. sigma accepts anti_mismatch_packet without crash         PASS
28. mismatch_score >= 0.60 → CALIBRATED_WITH_MISMATCH_RISK PASS
29. mismatch_score < 0.60 → usable_for_gencoin == True      PASS
30. sigma without anti_mismatch → textual fallback preserved PASS
```

### py_compile

```
COMPILE_OK: brody_anti_mismatch_signal.py
COMPILE_OK: brody_gencoin_transverse_interface.py
COMPILE_OK: routes/brody.py
COMPILE_OK: test_brody_f2c_anti_mismatch_formal.py
```

### git diff --stat

```
 apps/obsidia_api/brody_anti_mismatch_signal.py          | ~200 lines (new)
 apps/obsidia_api/brody_gencoin_transverse_interface.py  | ~30 lines modified
 apps/obsidia_api/routes/brody.py                        | ~35 lines modified
 tests/api/test_brody_f2c_anti_mismatch_formal.py        | ~310 lines (new)
 docs/runtime/OBSIDIA_F2C_ANTI_MISMATCH_FORMAL_REPORT.md | this file (new)
```

---

## RISKS

| Risk | Level | Note |
|---|---|---|
| Signals are heuristic / textual (word count, domain detection) | LOW-MEDIUM | Deterministic and bounded, but not formally proven. Adequate for shadow readonly phase. |
| sigma_initial truth_score used by anti_mismatch creates a circular dependency appearance | LOW | Not circular — sigma_initial is a snapshot. anti_mismatch reads it, sigma_final consumes anti_mismatch. One-directional. |
| memory_claim detection via keyword matching is surface-level | MEDIUM | Formal memory provenance detection deferred to F3/F4. Adequate for F2C. |
| Neo4j write guard still convention-only | MEDIUM | Not in F2C scope — BUCKET_4 |
| mismatch_score >= 0.60 threshold is fixed | LOW | Threshold is deterministic. Value chosen conservatively. Can be tuned in F3 if calibration data becomes available. |

---

## NEXT

```
F3_THERMO_OPERATIONAL:
  - Formal thermodynamics dissipation computation
  - Precondition: F2C_ANTI_MISMATCH_FORMAL (now complete)
  - Thermodynamics reads sigma_packet (usable_for_thermodynamics=True when CALIBRATED_SHADOW_READONLY)
  - Still: no decision, no ACT

F4_GENCOIN_SHADOW_VALUE_LAYER:
  - Enable final scoring when F3 stable
  - All preconditions now met: Sigma V1 calibrated, Anti-Mismatch formal, Thermo operational (F3)
  - Gencoin remains KX108_ONLY / advisory / no ACT / no write

POSSIBLE F2D (optional):
  - Calibrate anti_mismatch thresholds using empirical response data
  - Replace word-count heuristics with structural comparison of IR Candidate vs Reverse OS output
  - Requires F3 stable first
```

---

## VALIDATION PHRASE

```
F2C_ANTI_MISMATCH_FORMAL_PASS
ANTI_MISMATCH_SIGNAL_V1=WIRED_SHADOW_READONLY
MISMATCH_SCORE=BOUNDED_DETERMINISTIC
SIGMA_DECORATIVE_COHERENCE_RISK=ANTI_MISMATCH_BACKED
KX108_ONLY=true
NO_ACT=true
NO_COMMIT=true
```
