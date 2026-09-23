# INTENT_TO_DECISION_TICKET_DRY_RUN_MAP
# runtime_contracts/x108_gateway_dry_run_harness/mapping/
# Plan 3 P3 — Mapping documentaire IntentEnvelope → DecisionTicket
# Date: 2026-06-02
# Status: HARNESS_DOCUMENTATION_ONLY / NO_RUNTIME_EXECUTION

---

## Règle globale

```
IntentEnvelope → X108 Gateway → DecisionTicket
                    ↑
  ContextPacket(s) ─┤
  PeripheralSignalPacket(s) ─┤ (tous advisory uniquement)
  OS3EvidenceTicket refs ───┤

∀ décision : seul X108 produit ALLOW/HOLD/BLOCK
∀ périphérie : advisory_only = true / emits_verdict = false
∀ failure : fail_closed / no_act
```

---

## Table de mapping principale

| Input object | Contract cible | Dry-run use | Forbidden use | Failure mode si violé |
|-------------|---------------|-------------|---------------|-----------------------|
| IntentEnvelope | IntentEnvelope.contract.md | Décrire l'intention candidate | émettre décision, bypass X108 | missing_intent_authority |
| ContextPacket (External Signals temporal) | ContextPacket + EXTERNAL_SIGNALS_SIGNAL_ONLY | enrichir contexte temporel | décider ALLOW/HOLD/BLOCK | external_signal_attempts_x108_override |
| ContextPacket (Graphiti readonly) | ContextPacket + READONLY_CONTEXT_ONLY | contexte graphe lecture seule | écriture, souveraineté | context_attempts_write |
| ContextPacket (Brody readonly) | ContextPacket + READONLY_CONTEXT_ONLY | contexte agents lecture seule | écriture, souveraineté | context_attempts_write |
| ContextPacket (NPL advisory) | ContextPacket + NPL_ADVISORY_ONLY | enrichir narrative context | prétendre verdict NPL | npl_attempts_verdict |
| ContextPacket (Atlas future) | ContextPacket + ATLAS_READONLY_ADVISORY_ONLY | contexte cartographique futur | runtime-ready claim, import sans F78B | source_pack_not_deep_diffed |
| ContextPacket (Cognitive future) | ContextPacket + COGNITIVE_REINTEGRATION_ADVISORY_ONLY | contexte cognitif futur | runtime-ready claim, import sans F78B | source_pack_not_deep_diffed |
| PeripheralSignalPacket (External Signals) | PeripheralSignalPacket + EXTERNAL_SIGNALS_SIGNAL_ONLY | signal temporel non souverain | décision directe, ACT | peripheral_signal_attempts_decision |
| PeripheralSignalPacket (P107/P161 advisory) | PeripheralSignalPacket + P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | métrique advisory python spec | claim LEAN_PROVEN, autorité runtime | p107_p161_proven_claim_attempted |
| PeripheralSignalPacket (Audio/Entropy) | ContextPacket + AUDIO_ENTROPY_ADVISORY_ONLY | source entropique candidate | claim loi physique certifiée | audio_entropy_law_claim_attempted |
| OS3EvidenceTicket (temporal_receipt) | OS3EvidenceTicket + X108_GATEWAY_REQUIRED | preuve temporelle théorique | décision directe, claim proof certifié | missing_os3_evidence_ref |
| OS3EvidenceTicket (RSSI future) | OS3EvidenceTicket + RSSI_EVIDENCE_ONLY | evidence sécurité future | claim RSSI_CERTIFIED, import sans F78B | rssi_certification_claim_attempted |
| BoundaryContract (RGPD future) | BoundaryContract + RGPD_COMPLIANCE_SCOPE_GUARD | guard conformité future | claim ISO_CERTIFIED, import sans F78B | rgpd_compliance_claim_attempted |

---

## Mapping détaillé — IntentEnvelope fields → X108 gate checks

```yaml
# IntentEnvelope → X108 Gateway checks documentaires

intent_envelope_dry_run_checks:

  # Champ : source_module
  check_source_module:
    rule: "source_module != null AND source_module IN known_modules"
    failure: missing_intent_authority
    result_if_fail: fail_closed

  # Champ : action_candidate_type
  check_action_type:
    rule: "action_candidate_type IN [READ, WRITE, EXECUTE, COMMUNICATE, DECIDE]"
    failure: invalid_intent_type
    result_if_fail: fail_closed

  # Champ : irreversibility_level
  check_irreversibility:
    rule: "irreversibility_level IN [REVERSIBLE, PARTIALLY_REVERSIBLE, IRREVERSIBLE, CRITICAL]"
    failure: missing_irreversibility_level
    result_if_fail: fail_closed

  # Champ : criticality_level
  check_criticality:
    rule: "criticality_level IN [LOW, MEDIUM, HIGH, CRITICAL]"
    failure: missing_criticality_level
    result_if_fail: fail_closed

  # Champ : requires_x108
  check_x108_required:
    rule: "if criticality_level IN [HIGH, CRITICAL] THEN requires_x108 = true"
    failure: missing_x108_requirement
    result_if_fail: fail_closed

  # Champ : context_packet_refs
  check_context_refs:
    rule: "len(context_packet_refs) >= 1"
    failure: missing_context_packet
    result_if_fail: fail_closed

  # Champ : external_signal_flags
  check_external_signals:
    rule: "if external_signal_flags.anti_replay_check = FAIL → stale_risk"
    failure: stale_temporal_context
    result_if_fail: fail_closed + HOLD candidate

  # Champ : claim_scope
  check_claim_scope:
    rule: "claim_scope NOT IN [CLAIMABLE_FORMAL] unless LEAN_PROVEN evidence"
    failure: invalid_context_claim_scope
    result_if_fail: fail_closed + confidence penalty
```

---

## Mapping détaillé — ContextPacket sources → IntentEnvelope enrichissement

```yaml
context_sources_to_intent_enrichment:

  external_signals_temporal:
    packet_sources: [51_temporal_context_header, 53_consequence_boundary]
    contract: ContextPacket
    boundary: EXTERNAL_SIGNALS_SIGNAL_ONLY
    enrichment_fields:
      - temporal_context.tick_index
      - temporal_context.temporal_nonce
      - temporal_context.temporal_quality
      - consequence_context.executable_standing_status
      - consequence_context.continuation_legitimacy_status
    can_block_intent: false   # enrichissement uniquement
    can_allow_intent: false   # X108 décide seul
    advisory_only: true

  graphiti_brody_readonly:
    contract: ContextPacket
    boundary: READONLY_CONTEXT_ONLY
    enrichment_fields:
      - memory_graph_context
      - agent_interaction_history
    writes_allowed: false
    decision_authority: KX108_ONLY
    advisory_only: true

  npl_advisory:
    contract: ContextPacket
    boundary: NPL_ADVISORY_ONLY
    enrichment_fields:
      - narrative_enrichment
      - provenance_labels
    claim_max: ADVISORY
    cannot_claim: VERDICT / LEAN_PROOF / AUTHORITY

  atlas_future:
    contract: ContextPacket (future)
    boundary: ATLAS_READONLY_ADVISORY_ONLY
    status: COPIED_READONLY / F06_PENDING / F78B_REQUIRED
    enrichment_fields: [TBD — non extrait]
    import_gate: F78B + F06

  cognitive_future:
    contract: ContextPacket (future)
    boundary: COGNITIVE_REINTEGRATION_ADVISORY_ONLY
    status: COPIED_READONLY / F07_PENDING / F78B_REQUIRED
    enrichment_fields: [TBD — non extrait]
    import_gate: F78B + F07
```

---

## Mapping — Source packs deep diff gate F78B

```
∀ source pack p non extrait :
  p → block (F03 | F06 | F07 | F10)
  until F78B(p).VALIDATED = true

Packs non extraits actuellement :
  RSSI → F78B required → then F03
  RGPD → F78B required → then F03 + F10
  Atlas → F78B required → then F06
  Cognitive → F78B required → then F07

Seul pack extrait :
  External Signals → specs/external_signals/ (40/40 specs) ← SPEC_IMPORTED ✅
```

---

## Règles d'invalidation du mapping

| Condition | Violation | Action |
|-----------|-----------|--------|
| IntentEnvelope sans `requires_x108=true` pour CRITICAL | missing_x108_requirement | fail_closed |
| IntentEnvelope sans `irreversibility_level` | missing_irreversibility_level | fail_closed |
| ContextPacket avec `advisory_only=false` | boundary_violation | fail_closed |
| PeripheralSignalPacket avec `emits_verdict=true` | peripheral_signal_attempts_decision | fail_closed |
| Claim P107/P161 = LEAN_PROVEN | p107_p161_proven_claim_attempted | fail_closed |
| Claim RSSI = CERTIFIED | rssi_certification_claim_attempted | fail_closed |
| Claim RGPD = ISO_COMPLIANT | rgpd_compliance_claim_attempted | fail_closed |
| Import pack sans F78B | source_pack_not_deep_diffed | fail_closed |
| Zip assumé extrait sans vérification | zip_content_assumed_imported | fail_closed |
| DecisionTicket produit par périphérie | action_without_x108 | BLOCK absolu |
