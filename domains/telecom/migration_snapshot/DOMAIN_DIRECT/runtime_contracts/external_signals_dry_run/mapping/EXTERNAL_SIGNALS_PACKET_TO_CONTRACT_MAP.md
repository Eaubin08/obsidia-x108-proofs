# EXTERNAL_SIGNALS_PACKET_TO_CONTRACT_MAP
# runtime_contracts/external_signals_dry_run/mapping/
# Plan 3 P2 — Mapping packets External Signals → contrats runtime_contracts/
# Date: 2026-06-02

---

## Règle globale

```
∀ packet External Signals p : p → ContextPacket | PeripheralSignalPacket | OS3EvidenceTicket
∀ packet External Signals p : p ↛ DecisionTicket (seul X-108 produit)
∀ packet External Signals p : p ↛ ALLOW / HOLD / BLOCK
decision_authority = KX108_ONLY
label obligatoire = EXTERNAL_SIGNAL_ONLY
```

---

## Table de mapping principale

| Source packet | Runtime contract target | Allowed use | Forbidden use | Failure mode |
|--------------|------------------------|-------------|---------------|--------------|
| `51_temporal_context_header` (C460) | **ContextPacket** (source_layer=external_signals) + **PeripheralSignalPacket** (signal_type=EXTERNAL_TEMPORAL) | Transporter tick, nonce, phase_window comme contexte temporal | Décider ALLOW/HOLD/BLOCK ; réautoriser X-108 | expires_at_tick dépassé → stale_risk_flag ; anti_replay_status=FAIL → fail_closed flag |
| `52_temporal_receipt` (C466/C467) | **OS3EvidenceTicket** (evidence_type=HASH_CHAIN) | Attacher receipt_id + action_intent_hash comme preuve temporelle à un DecisionTicket | Émettre DecisionTicket directement ; claim que receipt = ALLOW | replay_pointer manquant → evidence incomplet ; replay_status=FAIL → BLOCK candidat |
| `53_consequence_boundary` (C472) | **ContextPacket** (source_layer=external_signals, label=EXTERNAL_SIGNAL_ONLY) | Transporter executable_standing_status, continuation_legitimacy_status comme contexte de conséquence | Décider de la continuation directement ; bypass gate | continuation_legitimacy_status=INVALID → fail_closed candidat |

---

## Mapping détaillé — Packet 51 → ContextPacket

```yaml
# Input (51_temporal_context_header)
packet_id: temporal_context_header
fields:
  - day_index
  - phase_window
  - tick_index
  - cycle_anchor
  - temporal_nonce
  - issued_at_tick
  - expires_at_tick
  - source_agent
  - temporal_quality
  - signature_status
  - anti_replay_status
authority: context_signal_only
decision_authority: KX108_ONLY
can_emit_ACT: false

# Output → ContextPacket
context_packet:
  source_layer: external_signals
  source_module: temporal_context_header_C460
  readonly: true
  advisory_only: true
  labels: [EXTERNAL_SIGNAL_ONLY]
  decision_authority: KX108_ONLY
  emits_act: false
  emits_verdict: false
  source_status: SPEC_IMPORTED
  context_payload:
    temporal_context:
      tick_index: <tick_index>
      temporal_nonce: <temporal_nonce>
      expires_at_tick: <expires_at_tick>
      temporal_quality: <temporal_quality>
      anti_replay_status: PASS | FAIL
      signature_status: VALID | INVALID

# Output → PeripheralSignalPacket (pour anti_replay)
peripheral_signal:
  signal_type: EXTERNAL_TEMPORAL
  source_module: anti_replay_horizon_C463
  metric_name: anti_replay_check
  metric_value: PASS | FAIL
  metric_range: {enum: [PASS, FAIL, NOT_CHECKED]}
  label: EXTERNAL_SIGNAL_ONLY
  advisory_only: true
  emits_act: false
  emits_allow_hold_block: false
```

---

## Mapping détaillé — Packet 52 → OS3EvidenceTicket

```yaml
# Input (52_temporal_receipt)
packet_id: temporal_receipt
fields:
  - receipt_id
  - action_intent_hash
  - kx108_decision        ← valeur POST-décision X-108 — jamais pré-décision
  - tick_window
  - temporal_challenge_id
  - anti_replay_status
  - policy_version
  - signature_status
  - replay_pointer
effect_receipt_rule: effect_receipt_only_after_ACT
decision_authority: KX108_ONLY

# Output → OS3EvidenceTicket
os3_evidence:
  evidence_type: HASH_CHAIN
  source: temporal_receipt_metadata_C466
  linked_decision_ticket: <TBD — produit après X-108 decide>
  hash: sha256(receipt_id + action_intent_hash + tick_window)
  replay_status: NOT_RUN
  verification_status: UNVERIFIED  # honnête — pas encore validé
  claim_scope: CLAIMABLE_SPEC_ONLY
  # kx108_decision dans receipt = reflet de la décision X-108, pas une autorisation
  # effect_receipt_rule = receipt existe UNIQUEMENT après ACT autorisé par X-108
```

**Note critique :** `kx108_decision` dans le packet 52 est un champ **post-décision** —
il reflète la décision que X-108 a déjà prise. Ce n'est pas une autorisation.
L'adapter External Signals ne lit ce champ qu'après la décision X-108, pour traçabilité.

---

## Mapping détaillé — Packet 53 → ContextPacket

```yaml
# Input (53_consequence_boundary)
packet_id: consequence_boundary
fields:
  - executable_standing_status   # VALID | INVALID | PENDING
  - continuation_legitimacy_status  # VALID | INVALID | EXPIRED
  - consequence_binding_status    # BOUND | UNBOUND | DISPUTED
  - intent_receipt_id
  - effect_receipt_id
  - parent_receipt_hash
  - protected_consequence
  - wrapper_reauthoring_forbidden  # toujours true — C473
decision_authority: KX108_ONLY
can_emit_ACT: false

# Output → ContextPacket
context_packet:
  source_layer: external_signals
  source_module: consequence_boundary_enrichment_C472
  readonly: true
  advisory_only: true
  labels: [EXTERNAL_SIGNAL_ONLY]
  emits_act: false
  emits_verdict: false
  context_payload:
    consequence_context:
      executable_standing_status: <value>
      continuation_legitimacy_status: <value>
      consequence_binding_status: <value>
      wrapper_reauthoring_forbidden: true  # TOUJOURS — C473
      # → X-108 utilise ce contexte pour enrichir sa décision
      # → jamais pour bypass ou réautorisation
```

---

## Mapping des composants → IntentEnvelope.external_signal_flags

```yaml
# IntentEnvelope.external_signal_flags (champ optionnel enrichi)
external_signal_flags:
  temporal_receipt: <receipt_id de 52_temporal_receipt>
  anti_replay_check: PASS | FAIL  # depuis C463
  stale_execution_check: PASS | FAIL  # depuis C469
  temporal_quality: high | medium | low  # depuis C460
  consequence_standing: VALID | INVALID  # depuis C472/53
  # Ces flags alimentent X-108 — jamais une décision directe
```

---

## Composants C459-C482 — Mapping résumé

| Composant | Type | Mapping contrat | Boundary |
|-----------|------|----------------|---------|
| C459 Timeverse Temporal Sidecar | module | BoundaryContract (module rights) | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| C460 Temporal Context Header | packet | ContextPacket + PeripheralSignalPacket | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| C463 Anti-Replay Horizon | guard | PeripheralSignalPacket (anti_replay_check) | FAIL_CLOSED_PRIORITY |
| C465 Time-Bounded Tool Call Check | check | PeripheralSignalPacket (tool_call_within_window) | X108_GATEWAY_REQUIRED |
| C466 Temporal Receipt Metadata | metadata | OS3EvidenceTicket | X108_GATEWAY_REQUIRED |
| C469 Stale Execution Detection | detector | PeripheralSignalPacket (stale_execution_check) | FAIL_CLOSED_PRIORITY |
| C472 Consequence Boundary Enrichment | enricher | ContextPacket (consequence context) | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| C473 Wrapper Non-Reauthoring Law | law | **Interdit runtime** — encode dans boundary | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| C482 Intent-Effect-Receipt Separation | separator | OS3EvidenceTicket (séparation intent/effect/receipt) | X108_GATEWAY_REQUIRED |
