# OBSIDIA F2A — TRANSVERSE VALUE INTERFACE PREP REPORT

Date: 2026-05-27
Phase: F2A_TRANSVERSE_VALUE_INTERFACE_PREP

---

## STATUS

F2A_TRANSVERSE_VALUE_INTERFACE_PREP_COMPLETE

---

## BOUNDARY

```
KX108_ONLY              = true
ADVISORY_ONLY           = true
READONLY                = true
EMITS_ACT               = false
EMITS_VERDICT           = false
MEMORY_WRITE            = false
GRAPHITI_WRITE          = false
NEO4J_WRITE             = false
KERNEL_MUTATION         = false
X108_MUTATION           = false
FINAL_GENCOIN_SCORING   = false
NO_COMMIT               = true
NO_KERNEL_TOUCH         = true
```

---

## CHANGES

### Files created

| File | Role |
|---|---|
| `apps/obsidia_api/brody_gencoin_transverse_interface.py` | BLOC B — GENCOIN_TRANSVERSE_INTERFACE_V0 + SIGMA_CALIBRATION_PACKET_V0 |
| `tests/api/test_brody_f2a_transverse_value_interface.py` | 21 invariant tests (18 mandatory + 3 additional) |

### Files modified

| File | Change |
|---|---|
| `apps/obsidia_api/brody_true_voice_adapter.py` | +28 lines — import _build_sigma_packet, build sigma_packet after adaptive_response_policy, add sigma_packet to return dict |
| `apps/obsidia_api/routes/brody.py` | +30 lines — import build_gencoin_transverse_packet + build_sigma_packet, call via safe_call_snapshot, add value_layer + sigma_packet to final response |

### Files NOT touched

- proofs/
- formal/tla/
- merkle*
- seal*
- rfc3161*
- KX108
- X108 kernel
- Lean proofs
- TLA+ specs
- periphery/gencoin_sandbox/
- periphery/gencoin.py
- periphery/blockchain/

---

## FUNCTIONS ADDED

### `apps/obsidia_api/brody_gencoin_transverse_interface.py`

```python
build_sigma_packet(adaptive_response_policy=None) -> dict
```
- Reads sigma_pressure from adaptive_response_policy (never invents it).
- Returns SIGMA_CALIBRATION_PACKET_V0 with usable_for_gencoin=false,
  usable_for_thermodynamics=false, truth_score=null.

```python
build_gencoin_transverse_packet(
    *, ir_candidate, true_voice_snapshot, domain_raccord,
    trees_snap, memory_chain, has_proof_readonly, adaptive_response_policy
) -> dict
```
- Returns {"value_layer": {...}} with all scores=null, final_scoring_enabled=false.
- BLOC D hooks: sets inputs_available flags based on pipeline presence.
- Distinguishes trees_textual_signal (domain raccord text) from
  trees_formal_computation (always False/DEFERRED).

---

## POINTS DE BRANCHEMENT

```
routes/brody.py
  line ~202: after ir_candidate_payload built
  -> safe_call_snapshot("gencoin_transverse_interface", build_gencoin_transverse_packet, ...)
  -> safe_call_snapshot("sigma_packet", build_sigma_packet, ...)
  -> value_layer + sigma_packet added to final safe_backend_response()

brody_true_voice_adapter.py
  line ~42: import _build_sigma_packet (try/except)
  line ~497: sigma_packet built after adaptive_response_policy
  line ~549: sigma_packet added to return dict
```

---

## PAYLOAD EXAMPLES

### value_layer (GENCOIN_TRANSVERSE_INTERFACE_V0)

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
      "sigma": "PARTIAL_NOT_FORMALLY_CALIBRATED",
      "thermodynamics": "DEFERRED",
      "trees_textual_signal": "TEXTUAL_SIGNAL_ONLY",
      "trees_formal_computation": "DEFERRED",
      "memory": "READONLY_CONTEXT_ONLY",
      "proof": "READONLY_PROOF_ONLY",
      "reverse_os": "OPTIONAL_PROJECTION_COST"
    },
    "notes": [
      "Gencoin final scoring is disabled.",
      "This packet exists only to avoid future recabling.",
      "No value emitted here can trigger action, verdict, write, memory promotion, kernel mutation, or X108 mutation."
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
}
```

### sigma_packet (SIGMA_CALIBRATION_PACKET_V0)

```json
{
  "version": "SIGMA_CALIBRATION_PACKET_V0",
  "mode": "SHADOW_READONLY",
  "source": "BRODY_ADAPTIVE_RESPONSE_POLICY_V1",
  "calibration_status": "PARTIAL_NOT_FORMALLY_CALIBRATED",
  "usable_for_gencoin": false,
  "usable_for_thermodynamics": false,
  "truth_score": null,
  "sigma_pressure": "LOW",
  "reason": "SIGMA_NOT_FORMALLY_CALIBRATED",
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

---

## PROOFS

### Tests run

```
pytest tests/api/test_brody_f2a_transverse_value_interface.py -v
```

### Smoke output

```
platform win32 -- Python 3.13.3, pytest-9.0.3
collected 21 items

test_01_value_layer_exists                       PASSED
test_02_value_layer_mode_shadow_readonly         PASSED
test_03_final_scoring_disabled                   PASSED
test_04_all_scores_null                          PASSED
test_05_decision_authority_kx108_only            PASSED
test_06_emits_act_false                          PASSED
test_07_emits_verdict_false                      PASSED
test_08_memory_write_false                       PASSED
test_09_kernel_mutation_false                    PASSED
test_10_x108_mutation_false                      PASSED
test_11_sigma_packet_exists                      PASSED
test_12_sigma_packet_usable_for_gencoin_false    PASSED
test_13_sigma_packet_usable_for_thermodynamics_false  PASSED
test_14_no_act_verdict_allow_block               PASSED
test_15_inputs_available_hooks                   PASSED
test_16_trees_distinction                        PASSED
test_17_trees_formal_computation_always_deferred PASSED
test_18_graceful_degradation_no_crash            PASSED
test_sigma_packet_reuses_sigma_pressure          PASSED
test_sigma_packet_no_sigma_pressure_stays_none   PASSED
test_memory_hook_false_when_no_chain             PASSED

21 passed in 0.09s
```

### py_compile

```
COMPILE_OK: brody_gencoin_transverse_interface
COMPILE_OK: brody_true_voice_adapter
COMPILE_OK: routes/brody
COMPILE_OK: test_f2a
```

### Invariants verified (18/18 mandatory + 3 additional)

```
 1. value_layer exists in packet                          PASS
 2. value_layer.mode == SHADOW_READONLY                   PASS
 3. value_layer.final_scoring_enabled == false            PASS
 4. All Gencoin scores remain null                        PASS
 5. decision_authority == KX108_ONLY                      PASS
 6. emits_act == false                                    PASS
 7. emits_verdict == false                                PASS
 8. memory_write == false                                 PASS
 9. kernel_mutation == false                              PASS
10. x108_mutation == false                                PASS
11. sigma_packet exists when built                        PASS
12. sigma_packet.usable_for_gencoin == false              PASS
13. sigma_packet.usable_for_thermodynamics == false       PASS
14. No ACT/ALLOW/BLOCK/VERDICT emitted                    PASS
15. inputs_available reflects pipeline presence           PASS
16. 34 arbres textual and formal computation distinguished PASS
17. trees_formal_computation always False/DEFERRED        PASS
18. Graceful degradation on bad input                     PASS
```

### git diff --stat

```
 apps/obsidia_api/brody_true_voice_adapter.py | 28 ++++++++++++++++++++++++++
 apps/obsidia_api/routes/brody.py             | 30 ++++++++++++++++++++++++++++
 2 files changed, 58 insertions(+)
```

### git status -sb (F2A scope)

```
 M apps/obsidia_api/brody_true_voice_adapter.py
 M apps/obsidia_api/routes/brody.py
?? apps/obsidia_api/brody_gencoin_transverse_interface.py
?? tests/api/test_brody_f2a_transverse_value_interface.py
?? docs/runtime/OBSIDIA_F2A_TRANSVERSE_VALUE_INTERFACE_PREP_REPORT.md
```

---

## REMAINING RISKS

| Risk | Level | Note |
|---|---|---|
| Neo4j write guard is convention-only | MEDIUM | Addressed in BUCKET_4 — not in F2A scope |
| Sigma calcul non formel | MEDIUM | sigma_pressure is used but not formally calibrated — usable_for_gencoin=false enforced |
| 34 Arbres textual/formal mix | ADDRESSED | Explicit distinction in value_layer.inputs_available |
| safe_call_snapshot silent degradation | LOW | Test 18 confirms graceful degradation |
| memory promotion policy activation | HIGH if activated | Not in F2A scope — stays DOC_ONLY |

---

## NEXT

```
F2B_SIGMA_CALIBRATED:
  - Define formal truth_score computation (IR Candidate quality metric)
  - Validate sigma_pressure calibration rules
  - Update SIGMA_CALIBRATION_PACKET_V0 to usable_for_gencoin=true
  - Freeze: sigma calibration doc + F2_SIGMA_CALIBRATED tag

F2C_ANTI_MISMATCH_FORMAL:
  - Wire formal anti-mismatch computation on IR + Reverse OS outputs
  - Add to domain raccord ANTI_MISMATCH domain with real signal

F3_THERMO_OPERATIONAL:
  - Formal thermodynamics dissipation computation on Sigma output
  - Precondition: F2_SIGMA_CALIBRATED

F4_GENCOIN_SHADOW_VALUE_LAYER:
  - Enable final scoring when all preconditions met
  - Precondition: F3_THERMO_OPERATIONAL
  - Gencoin remains KX108_ONLY / advisory / no ACT / no write
```

---

## F2B NEXT EXACT STEP — SIGMA CALIBRATION

Sigma calibration target:

1. Define `truth_score` computation function in `brody_gencoin_transverse_interface.py`
   or a dedicated `brody_sigma_calibration.py`.

2. Inputs:
   - `ir_candidate.intent_type` (complexity signal)
   - `adaptive_response_policy.sigma_pressure` (existing pressure)
   - `domain_raccord.domains` (domain count as complexity factor)
   - `memory_chain.material_quality` (evidence quality)

3. Formula (proposed, NOT active yet — needs validation):
   ```
   base = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.9}.get(sigma_pressure, 0.5)
   domain_factor = min(len(domains) * 0.05, 0.15)
   memory_factor = 0.1 if material_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL") else 0.0
   truth_score_candidate = round(base + domain_factor + memory_factor, 3)
   ```

4. Calibration criteria (to be validated by KX108):
   - BOUNDARY_COMPACT -> truth_score < 0.5 always
   - ARCHITECTURE -> truth_score > 0.6
   - MEMORY_CHAIN_PASS -> truth_score > 0.5
   - Never used as decision input

5. When calibrated: set usable_for_gencoin=true, usable_for_thermodynamics=true.
   Create F2_SIGMA_CALIBRATED freeze doc.
