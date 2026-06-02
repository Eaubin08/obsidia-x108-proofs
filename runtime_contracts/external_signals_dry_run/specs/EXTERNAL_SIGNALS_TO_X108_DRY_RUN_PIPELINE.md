# EXTERNAL_SIGNALS_TO_X108_DRY_RUN_PIPELINE
# runtime_contracts/external_signals_dry_run/specs/
# Plan 3 P2 — Pipeline documentaire uniquement — NO RUNTIME EXECUTION
# Date: 2026-06-02

---

## Statut

```
SPEC_ONLY — DRY_RUN_DOCUMENTATION
Aucun code Python. Aucun adapter actif. Aucune action réelle.
Ce pipeline sera implémenté en P3 (X108 Gateway Dry-Run Harness).
```

---

## Pipeline complet — 12 étapes

---

### Étape 1 — Receive External Temporal Signal

**Input :** Signal brut depuis composant C459 (Timeverse Temporal Sidecar)

```yaml
input:
  - agent_request (IntentEnvelope candidat)
  - system_clock_context (tick, phase)
  - policy_version
  - source_agent_id

output:
  - temporal_context_header_raw (C460 structure)

allowed:
  - Recevoir les champs temporels bruts (tick, nonce, expires_at_tick)
  - Identifier le source_agent_id

forbidden:
  - Décider de l'action
  - Émettre ACT ou ALLOW

fail_closed:
  - Si tick absent → missing_temporal_context → fail_closed
  - Si policy_version inconnue → unknown_policy → fail_closed
```

---

### Étape 2 — Validate Source Status

**Input :** temporal_context_header_raw

```yaml
input:
  - temporal_context_header_raw

output:
  - source_status = SPEC_IMPORTED | PYTHON_SPEC | UNKNOWN_SOURCE

allowed:
  - Vérifier que la source est connue et dans le registre

forbidden:
  - Accepter source UNKNOWN_SOURCE sans flag

fail_closed:
  - Si source_status = UNKNOWN_SOURCE → unknown_source_flag = true → X108 pénalisera
```

---

### Étape 3 — Validate Temporal Context Header

**Input :** temporal_context_header_raw

```yaml
input:
  - day_index, phase_window, tick_index, cycle_anchor
  - temporal_nonce, issued_at_tick, expires_at_tick
  - temporal_quality, signature_status

output:
  - validated_temporal_header (C460 validé)

allowed:
  - Valider que expires_at_tick > current_tick
  - Valider que signature_status = VALID
  - Calculer temporal_quality

forbidden:
  - Accepter un header expiré sans flag
  - Accepter signature_status = INVALID sans flag

fail_closed:
  - expires_at_tick <= current_tick → invalid_tick → stale_risk_flag
  - signature_status = INVALID → signature_invalid → fail_closed
  - temporal_quality = low → low_quality_flag (X108 pénalise)
```

---

### Étape 4 — Validate Anti-Replay Horizon

**Input :** temporal_nonce, horizon bounds (C463)

```yaml
input:
  - nonce_id
  - signature_hash
  - horizon_start_tick, horizon_end_tick
  - replay_seen, replay_count

output:
  - anti_replay_status = PASS | FAIL
  - replay_count_updated

allowed:
  - Vérifier que le nonce n'a pas été vu dans l'horizon
  - Logger le nonce vérifié

forbidden:
  - Émettre ALLOW si anti_replay = PASS (X108 décide)
  - Émettre BLOCK si anti_replay = FAIL (X108 décide)
  - Modifier l'état machine directement

fail_closed:
  - replay_seen = true → anti_replay_status = FAIL → fail_closed flag + X108 flag
  - horizon dépassé → anti_replay_horizon_exceeded → fail_closed
```

---

### Étape 5 — Validate Stale Execution Status

**Input :** action_id, ticks (C469)

```yaml
input:
  - action_id
  - tick_at_request
  - tick_at_evaluation
  - stale_threshold_ticks

output:
  - stale_execution_status = PASS | FAIL
  - stale_detected: boolean

allowed:
  - Calculer tick_at_evaluation - tick_at_request
  - Comparer à stale_threshold_ticks

forbidden:
  - Émettre HOLD si stale_detected = true (X108 décide)
  - Annuler l'action directement

fail_closed:
  - stale_detected = true → stale_execution_signal = FAIL → fail_closed flag
  - X108 recevra stale_execution_check = FAIL et décidera HOLD ou BLOCK
```

---

### Étape 6 — Build PeripheralSignalPacket

**Input :** Résultats des étapes 3-5

```yaml
input:
  - anti_replay_status
  - stale_execution_status
  - temporal_quality
  - source_status

output:
  - PeripheralSignalPacket(signal_type=EXTERNAL_TEMPORAL)

struct:
  signal_id: uuid()
  signal_type: EXTERNAL_TEMPORAL
  source_module: external_signals_adapter
  source_status: SPEC_IMPORTED
  metric_name: anti_replay_check | stale_execution_check | temporal_quality
  metric_value: PASS | FAIL | high | medium | low
  metric_range: {enum: [PASS, FAIL, NOT_CHECKED]} | {enum: [high, medium, low]}
  advisory_only: true
  decision_authority: KX108_ONLY
  emits_act: false
  emits_allow_hold_block: false
  label: EXTERNAL_SIGNAL_ONLY
  timestamp_or_tick: current_tick

fail_closed:
  - metric_value hors range → out_of_range_flag
```

---

### Étape 7 — Build ContextPacket

**Input :** temporal_context_header validé + consequence_boundary (C472/53)

```yaml
output:
  - ContextPacket(source_layer=external_signals)

struct:
  context_id: uuid()
  source_layer: external_signals
  source_module: external_signals_adapter_C459
  readonly: true
  advisory_only: true
  confidence: 0.85  # max par design — temporal context haute qualité si PASS
  claim_scope: CLAIMABLE_ADVISORY
  labels: [EXTERNAL_SIGNAL_ONLY]
  decision_authority: KX108_ONLY
  emits_act: false
  emits_verdict: false
  source_status: SPEC_IMPORTED
  timestamp_or_tick: current_tick
  context_payload:
    temporal_context:
      tick_index: <tick_index>
      anti_replay_check: PASS | FAIL
      stale_execution_check: PASS | FAIL
      temporal_quality: high | medium | low
      consequence_standing: VALID | INVALID
      wrapper_reauthoring_forbidden: true   # C473 — toujours
  external_signal_flags:
    anti_replay_check: PASS | FAIL
    stale_execution_check: PASS | FAIL
    temporal_receipt: <receipt_id si disponible>

fail_closed:
  - confidence = 1.0 → reject (confidence max = 0.95 pour External Signals)
```

---

### Étape 8 — Attach to IntentEnvelope Candidate

**Input :** ContextPacket + PeripheralSignalPacket(s)

```yaml
output:
  - IntentEnvelope mis à jour avec:
    context_packet_refs: [context_packet.id]
    peripheral_signal_refs: [psp_anti_replay.id, psp_stale.id]
    external_signal_flags:
      anti_replay_check: PASS | FAIL
      stale_execution_check: PASS | FAIL
      temporal_receipt: <ref>

allowed:
  - Ajouter context_packet_refs
  - Ajouter peripheral_signal_refs
  - Mettre à jour external_signal_flags

forbidden:
  - Modifier requires_x108 → toujours true
  - Modifier authority → toujours KX108_ONLY
  - Modifier emits_act → toujours false

fail_closed:
  - Si external_signal_flags.anti_replay_check = FAIL → fail_closed_candidate = true
  - Si external_signal_flags.stale_execution_check = FAIL → fail_closed_candidate = true
```

---

### Étape 9 — Submit to X108 Gateway Dry-Run (documentaire)

**Input :** IntentEnvelope complet

```
FUTUR P3 — non implémenté en P2
x108_gateway.evaluate_dry_run(intent_envelope)

X-108 reçoit :
  - ContextPacket (External Signals)
  - PeripheralSignalPacket(s) (anti_replay, stale, temporal_quality)
  - external_signal_flags
  
X-108 applique :
  - skew_negative_implies_hold (si stale → HOLD candidat)
  - X108_no_act_before_tau (gate temporelle)
  - aggregate4_fail_closed (BLOCK > HOLD > ALLOW)
  
X-108 est SEUL à décider ALLOW / HOLD / BLOCK
External Signals ne peut jamais override ce résultat (C473)
```

---

### Étape 10 — Produce DecisionTicket Through X108 Only

```
FUTUR P3 — documentaire en P2

DecisionTicket produit UNIQUEMENT par X-108 :
  decision: ALLOW | HOLD | BLOCK
  reason_codes: incluant temporal flags
  tau_status: selon irréversibilité
  input_hash: sha256(action_candidate)
  merkle_root: sha256([input_hash, output_hash, trace_hash])
```

---

### Étape 11 — Attach OS3EvidenceTicket

```
FUTUR P5 — documentaire en P2

OS3EvidenceTicket :
  evidence_type: HASH_CHAIN
  source: external_signals_adapter
  hash: sha256(temporal_receipt + context_packet + decision)
  replay_status: NOT_RUN
  verification_status: UNVERIFIED
  linked_decision_ticket: <ticket_id>
```

---

### Étape 12 — No World Execution

```
DRY-RUN ONLY — toujours valable en P2 et P3

Si decision = ALLOW (dry-run) :
  → LOG result
  → return (decision_ticket, os3_evidence)
  → NO ACTUATE

Si decision = HOLD → LOG HOLD + reason_codes
Si decision = BLOCK → LOG BLOCK + reason_codes

AUCUNE ACTION MONDE RÉELLE
AUCUNE ÉCRITURE MÉMOIRE
AUCUN APPEL OUTIL
```

---

## Statut par étape — Plan 3 P2

| Étape | Statut P2 | Statut cible |
|-------|-----------|-------------|
| 1. Receive signal | SPEC_ONLY | P3 (code dry-run) |
| 2. Validate source | SPEC_ONLY | P3 |
| 3. Validate header | SPEC_ONLY | P3 |
| 4. Anti-replay | SPEC_ONLY | P3 |
| 5. Stale detection | SPEC_ONLY | P3 |
| 6. Build PSP | SPEC_ONLY | P3 |
| 7. Build ContextPacket | SPEC_ONLY | P3 |
| 8. Attach IntentEnvelope | SPEC_ONLY | P3 |
| 9. X108 dry-run | FUTUR P3 | P3 harness |
| 10. DecisionTicket | FUTUR P3 | P3 harness |
| 11. OS3EvidenceTicket | FUTUR P5 | P5 |
| 12. No world execution | DOCUMENTAIRE P2 | Enforcement P3 |
