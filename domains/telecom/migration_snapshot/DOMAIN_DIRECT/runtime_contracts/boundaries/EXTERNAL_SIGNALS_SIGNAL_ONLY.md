# EXTERNAL_SIGNALS_SIGNAL_ONLY
# runtime_contracts/boundaries/EXTERNAL_SIGNALS_SIGNAL_ONLY.md
# Status: CONTRACT_SKELETON_ONLY
# Source: specs/external_signals/F04_EXTERNAL_SIGNALS_BOUNDARY.md
# Pack importé: OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip (40/40 specs → specs/external_signals/)

---

## 1. Boundary Statement

```
External Signals = TEMPORAL_PREFILTER_ONLY
External Signals ↛ ALLOW
External Signals ↛ HOLD
External Signals ↛ BLOCK
External Signals ↛ ACT
External Signals ↛ réautorisation X108
∀ composant C459-C482 : emits_act = false
∀ composant C459-C482 : emits_decision = false
```

---

## 2. Applies To

Tous les composants du pack F04 (40 specs importées dans specs/external_signals/) :
- C459 Timeverse Temporal Sidecar
- C460 Temporal Context Header
- C461 Tick Canonical Validation
- C462 No-Float Temporal Math
- C463 Anti-Replay Horizon
- C464 Temporal Challenge
- C465 Time-Bounded Tool Call Check
- C466 Temporal Receipt Metadata
- C467 TSAE Receipt Model
- C468 Receipt Anchor Hash
- C469 Stale Execution Detection
- C470 Temporal Zero-Trust Positioning
- C471 Gateway-Before-Endpoint Prefilter
- C472 Consequence Boundary Enrichment
- C473 Wrapper Non-Reauthoring Law
- C474 Law-State-Input Replay Triplet
- C475 Corridor Packaging Registry
- C476 Refusal Preserves Structure
- C477 Protected Consequence Could-Not-Bind
- C478 Executable Standing Check
- C479 Continuation Legitimacy Check
- C480 Consequence Binding Status Extended
- C481 Visible Enforcement Surface
- C482 Intent-Effect-Receipt Separation
- Family specs 46, 47, 48
- Packets 51 (TemporalContextHeader), 52 (TemporalReceipt), 53 (ConsequenceBoundary)

---

## 3. Allowed

| Signal produit | Description | Boundary |
|---------------|-------------|---------|
| `temporal_context` | Contexte temporel (timestamp, tick, corridor) | CONTEXT_ONLY |
| `anti_replay_signal` | Détection de rejeu d'action déjà exécutée | SIGNAL_ONLY |
| `stale_execution_signal` | Exécution périmée (délai > seuil) | SIGNAL_ONLY |
| `temporal_receipt_metadata` | Métadonnées reçu temporel pour audit | EVIDENCE_ONLY |
| `consequence_boundary_context` | Contexte boundary de conséquence | CONTEXT_ONLY |

---

## 4. Forbidden

```
❌ Produire ALLOW depuis External Signals
❌ Produire HOLD depuis External Signals
❌ Produire BLOCK depuis External Signals
❌ Produire ACT depuis External Signals
❌ Réautoriser X108 (C473 Wrapper Non-Reauthoring Law)
❌ Émettre un verdict moral, culturel, de vérité
❌ Modifier l'état machine
```

**Note critique (C473) :** Un wrapper External Signals ne peut jamais "réautoriser" une action que X-108 a refusée. Si X-108 dit BLOCK, External Signals ne peut pas overrider.

---

## 5. Failure Mode

- `anti_replay_check = FAIL` → stale_risk flag → X108 évalue avec pénalité
- `stale_execution_check = FAIL` → fail_closed candidat
- Signal External Signals manquant pour action CRITICAL → flag `external_validation_missing`
- `emits_decision = true` depuis External Signals → violation

---

## 6. Required Contract Fields

- `label: "EXTERNAL_SIGNAL_ONLY"` dans PeripheralSignalPacket
- `anti_replay_check` et `stale_execution_check` dans external_signal_flags

---

## 7. Required Future Tests

- `test_external_signal_cannot_authorize_act` (à créer en P2)
- `test_external_signal_anti_replay_fail_closes`
- `test_c473_wrapper_non_reauthoring`

---

## 8. Proof Expectation

- `skew_negative_implies_hold` : Lean-proven (TemporalBridge.lean) — skew → HOLD
- `X108_no_act_before_tau` : Lean-proven — gate temporelle incompressible
- C463 Anti-Replay Horizon : Python spec (specs/external_signals/component_specs/)

---

## 9. Claim-Scope

**Autorisé :**
- "External Signals F04 est importé (40/40 specs dans specs/external_signals/)"
- "External Signals fournit un préfiltre temporel — jamais une autorisation"
- "anti_replay, stale_execution, temporal_receipt = signaux contextuels uniquement"

**Interdit :**
- "External Signals peut autoriser X-108" — INTERDIT ABSOLU (C473)
- "External Signals émet ALLOW" — INTERDIT
- "External Signals est Lean-prouvé" — PYTHON_SPEC (40 specs YAML)

---

## 10. Example Violation

```python
# VIOLATION
if temporal_receipt.valid and stale_check == "PASS":
    return "ALLOW"  # ← External Signals ne peut pas émettre ALLOW
```

---

## 11. Correct Handling

```python
# CORRECT
signal = PeripheralSignalPacket(
    signal_type="EXTERNAL_TEMPORAL",
    metric_name="anti_replay_check",
    metric_value="PASS",
    label="EXTERNAL_SIGNAL_ONLY",
    emits_act=False,
    emits_allow_hold_block=False
)
# → X108 reçoit ce signal comme contexte et décide ALLOW/HOLD/BLOCK
```
