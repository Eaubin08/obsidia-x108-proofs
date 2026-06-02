# CONTEXT_SIGNAL_EVIDENCE_BINDING_MAP
# runtime_contracts/x108_gateway_dry_run_harness/mapping/
# Plan 3 P3 — Binding documentaire Context / Signal / Evidence
# Date: 2026-06-02
# Status: HARNESS_DOCUMENTATION_ONLY / NO_RUNTIME_EXECUTION

---

## Règle globale

```
ContextPacket     → enrichit IntentEnvelope (readonly / advisory)
PeripheralSignal  → influence reason_codes via X108 uniquement
OS3Evidence       → s'attache au DecisionTicket théorique
DecisionTicket    → seul X108 le produit réellement
Source packs      → COPIED_READONLY jusqu'à F78B validé
```

---

## 1. ContextPacket — binding rules

```yaml
context_packet_binding:
  nature: READONLY_ADVISORY
  can_write: false
  can_decide: false
  can_emit_act: false
  can_emit_verdict: false
  may_enrich_intent_envelope: true   # champs external_signal_flags, context_packet_refs

  allowed_operations:
    - transporter contexte readonly vers IntentEnvelope
    - enrichir external_signal_flags de l'IntentEnvelope
    - référencé dans context_packet_refs[]
    - influencer la confiance X108 (advisory)
    - contribuer à reason_codes via X108 uniquement

  forbidden_operations:
    - émettre ALLOW / HOLD / BLOCK
    - modifier un fichier existant
    - déclencher ACT
    - prétendre à la souveraineté
    - surpasser ou contourner X108

  sources_by_status:
    external_signals: SPEC_IMPORTED (40/40 specs — F04)
    graphiti:         READONLY_CONTEXT_ONLY / NO_WRITE
    brody:            READONLY_CONTEXT_ONLY / NO_WRITE
    npl:              NPL_ADVISORY_ONLY / ENRICHISSEMENT
    atlas:            COPIED_READONLY / F06_PENDING / F78B_REQUIRED
    cognitive:        COPIED_READONLY / F07_PENDING / F78B_REQUIRED
    audio_entropy:    SOURCE_PARTIAL / AUDIO_ENTROPY_ADVISORY_ONLY

  invariants:
    - readonly = true toujours
    - advisory_only = true toujours
    - claim_scope IN [CLAIMABLE_SPEC_ONLY, ADVISORY, COPIED_READONLY]
    - confidence MAX = 0.95 (jamais 1.0 depuis périphérie)
```

---

## 2. PeripheralSignalPacket — binding rules

```yaml
peripheral_signal_packet_binding:
  nature: SIGNAL_NON_SOUVERAIN
  can_decide: false
  can_emit_allow_hold_block: false
  can_emit_act: false
  emits_verdict: false
  sovereign: false
  decision_authority: KX108_ONLY

  allowed_operations:
    - transporter un signal unique non souverain
    - alimenter les reason_codes de X108 via PeripheralSignalPacket.metric_name
    - influencer le poids d'analyse X108 (advisory uniquement)
    - signaler un failure mode (fail_closed uniquement)

  forbidden_operations:
    - émettre ALLOW / HOLD / BLOCK directement
    - prétendre à LEAN_PROVEN (P107/P161)
    - prétendre à LAW_CERTIFIED (Audio/Entropy)
    - prétendre à RSSI_CERTIFIED
    - prétendre à RGPD_COMPLIANT
    - bypass X108
    - déclencher action monde réel

  sources_by_status:
    external_signals_anti_replay:  SPEC_IMPORTED / signal_type=EXTERNAL_TEMPORAL
    p107_lyapunov:                 PYTHON_SPEC_NOT_LEAN_PROVEN / advisory uniquement
    p161_energetic:                PYTHON_SPEC_NOT_LEAN_PROVEN / advisory uniquement
    audio_entropy:                 SOURCE_PARTIAL / advisory candidate
    npl_metrics:                   NPL_ADVISORY_ONLY / métriques narratives

  failure_on_sovereignty_claim:
    action: fail_closed
    reason: peripheral_signal_attempts_decision
    priority: CRITICAL
```

---

## 3. OS3EvidenceTicket — binding rules

```yaml
os3_evidence_ticket_binding:
  nature: EVIDENCE_ONLY
  can_decide: false
  can_emit_act: false
  decision_authority: KX108_ONLY

  allowed_operations:
    - s'attacher à un DecisionTicket (après décision X108)
    - transporter receipt_id + hash + replay_pointer
    - référencer temporal_receipt (packet 52)
    - prouver immuabilité avec merkleRoot (futur P5)
    - servir de base à OS3ProofTicket kernel (futur)

  forbidden_operations:
    - produire ALLOW / HOLD / BLOCK
    - constituer une décision seul
    - prétendre que replay_status = VERIFIED sans vérification réelle
    - prétendre que seal_status = SEALED sans seal réel

  current_status_p3:
    replay_status: NOT_RUN   # P3 ne rejoue pas
    verification_status: UNVERIFIED   # honnête
    seal_status: NOT_SEALED  # P3 ne scelle pas
    claim_scope: THEORETICAL_ONLY

  binding_to_decision_ticket:
    linked_decision_ticket: THEORETICAL_ONLY (P3)
    binding_direction: OS3Evidence → attaches_to → DecisionTicket
    binding_condition: only_after_X108_decision

  future_invariants:
    - P13_Immutability (hash ne change pas)
    - merkleRoot_change_if_leaf_change
    - P17_AuditGrowth (audit trail croissant)
```

---

## 4. DecisionTicket — binding rules

```yaml
decision_ticket_binding:
  nature: SEULE_SORTIE_DECISIONNELLE
  sole_producer: X108_KERNEL
  values: [ALLOW, HOLD, BLOCK]
  priority: "BLOCK > HOLD > ALLOW"

  dry_run_p3_status:
    ticket_type: THEORETICAL_ONLY
    emitted_by: NONE_IN_P3  # X108 seul, jamais le harness
    real_decision: false
    world_action: false

  binding_inputs:
    - IntentEnvelope (requis)
    - ContextPacket(s) (requis ≥1)
    - PeripheralSignalPacket(s) (optionnel, advisory)
    - Tau status (requis si irréversible)
    - OS3EvidenceTicket refs (requis si CRITICAL)

  forbidden_producers:
    - tout module périphérique
    - External Signals
    - NPL
    - P107/P161
    - Audio/Entropy
    - Cognitive
    - Atlas
    - RSSI
    - RGPD
    - Graphiti
    - Brody
    - harness P3 lui-même

  invariants:
    - D1_DETERMINISM: même input → même output
    - E2_NO_ACT: pas d'ACT sans ALLOW explicite de X108
    - aggregate4_fail_closed: BLOCK > HOLD > ALLOW
    - X108_NO_ACT_BEFORE_TAU: irréversible → tau check obligatoire
```

---

## 5. Source packs — binding rules (non extraits)

```yaml
source_packs_binding:

  external_signals:
    status: SPEC_IMPORTED
    path: specs/external_signals/
    files: 40/40
    boundary: EXTERNAL_SIGNALS_SIGNAL_ONLY
    harness_eligible: true (P2 + P3)
    comment: seul pack branché dans harness P3

  rssi_security:
    status: COPIED_READONLY
    path: _source_packs/raw/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip
    files_internal: 167
    boundary: RSSI_EVIDENCE_ONLY
    harness_eligible: false  # F78B + F03 required
    import_gate: [F78B, F03]
    forbidden_claim: RSSI_CERTIFIED / SECURITY_PROVEN

  rgpd_iso:
    status: COPIED_READONLY
    path: _source_packs/raw/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip
    files_internal: 280
    boundary: RGPD_COMPLIANCE_SCOPE_GUARD
    harness_eligible: false  # F78B + F03 + F10 required
    import_gate: [F78B, F03, F10]
    forbidden_claim: ISO_CERTIFIED / RGPD_COMPLIANT

  branchable_atlas:
    status: COPIED_READONLY
    path: _source_packs/raw/OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip
    files_internal: 1738
    boundary: ATLAS_READONLY_ADVISORY_ONLY
    harness_eligible: false  # F78B + F06 required
    import_gate: [F78B, F06]
    forbidden_claim: ATLAS_RUNTIME_READY

  cognitive_reintegration:
    status: COPIED_READONLY
    path: _source_packs/raw/OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip
    files_internal: 513
    boundary: COGNITIVE_REINTEGRATION_ADVISORY_ONLY
    harness_eligible: false  # F78B + F07 required
    import_gate: [F78B, F07]
    forbidden_claim: COGNITIVE_RUNTIME_READY

  f78b_gate_status:
    directory: SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/
    status: AMORCÉ_PAR_PROCESSUS_EXTERNE / NON_VALIDÉ_P3
    content: non inspecté par P3
    note: P3 ne valide pas ce contenu — F78B doit être déclaré READY séparément
```
