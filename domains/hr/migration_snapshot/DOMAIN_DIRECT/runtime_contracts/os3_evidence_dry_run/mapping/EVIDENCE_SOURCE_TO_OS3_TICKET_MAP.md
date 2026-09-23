# EVIDENCE_SOURCE_TO_OS3_TICKET_MAP
# runtime_contracts/os3_evidence_dry_run/mapping/
# Plan 3 P5 — Mapping documentaire — NO PROOF / NO EXECUTION
# Date: 2026-06-02
# Status: OS3_EVIDENCE_SPEC_ONLY

---

## Règle globale

```
∀ source s : OS3Evidence(s) ↛ décision
∀ source s : OS3Evidence(s) → trace uniquement
∀ source s : claim_scope(s) ≤ source_status(s)
∀ hash/seal/merkle en P5 : PLACEHOLDER_ONLY
```

---

## Table de mapping

| Evidence source | Source status | Allowed OS3 use | Forbidden use | Required boundary | Future proof/test |
|-----------------|--------------|-----------------|---------------|------------------|------------------|
| IntentEnvelope | SPEC_ONLY (P0) | Référencer l'intent dans evidence_id base | Décider, produire ACT | X108_GATEWAY_REQUIRED | test_intent_trace_in_evidence |
| ContextPacket | SPEC_ONLY (P0) | Contexte trace dans evidence_context | Écrire, décider, verdict | READONLY_CONTEXT_ONLY | test_context_trace_readonly |
| PeripheralSignalPacket | SPEC_ONLY (P0) | Signal trace dans evidence_signals | Décider, ACT | NO_ACT_FROM_PERIPHERY | test_signal_trace_advisory |
| External Signals temporal receipt (packet 52) | SPEC_IMPORTED (F04) | HASH_CHAIN source — receipt_id + action_intent_hash | Décider, ALLOW/HOLD/BLOCK | EXTERNAL_SIGNALS_SIGNAL_ONLY | test_temporal_receipt_hash_chain |
| X108 Gateway DecisionTicket | THEORETICAL_ONLY (P3) | DECISION_TRACE — linked_decision_ticket | Remplacer X108, produire ALLOW seul | X108_GATEWAY_REQUIRED | test_decision_trace_theoretical |
| Anti-bypass checks (P4) | SPEC_ONLY (P4) | BYPASS_AUDIT_TRACE — bypass_check_refs | Prouver bypass impossible (P5 seul) | NO_ACT_FROM_PERIPHERY | test_bypass_audit_trace |
| RSSI evidence (future F03) | COPIED_READONLY — F78B+F03 required | RSSI_EVIDENCE_TRACE (futur) | Certifier RSSI, émettre BLOCK | RSSI_EVIDENCE_ONLY | test_rssi_evidence_not_certification |
| RGPD readiness (future F03+F10) | COPIED_READONLY — F78B+F03+F10 required | RGPD_COMPLIANCE_TRACE (futur) | Certifier ISO/RGPD, prouver conformité | RGPD_COMPLIANCE_SCOPE_GUARD | test_rgpd_evidence_not_certification |
| F78B source-pack audit | AUDIT_READY | SOURCE_PACK_GATE_TRACE — audit gate evidence | Prétendre import fait | F78B gate | test_f78b_gate_trace |
| F78C XLSX reconciliation | AUDIT_READY | BACKLOG_GATE_TRACE — reconciliation evidence | Prétendre import autorisé | XLSX_AUDIT_ONLY | test_f78c_gate_trace |
| Graphiti (future P6) | READONLY — periphery existant | CONTEXT_TRACE — graphiti_context_trace | Écrire dans Graphiti, décider | READONLY_CONTEXT_ONLY | test_graphiti_readonly_trace |
| Brody (future P6) | READONLY — periphery existant | CONTEXT_TRACE — brody_context_trace | Écrire dans Brody | READONLY_CONTEXT_ONLY | test_brody_readonly_trace |
| NPL provenance (specs/12/) | SPEC_IMPORTED (F04) | PROVENANCE_TRACE — narrative_provenance | Verdict moral, diagnostic | NPL_ADVISORY_ONLY | test_npl_provenance_trace |
| P107/P161 advisory (specs/03/) | PYTHON_SPEC — NOT_LEAN_PROVEN | ADVISORY_METRIC_TRACE (futur) | Claim LEAN_PROVEN authority | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | test_p107_p161_advisory_only |
| Audio/Entropy advisory (specs/03/) | SOURCE_PARTIAL — advisory candidate | ENTROPY_METRIC_TRACE (futur) | Claim loi physique certifiée | AUDIO_ENTROPY_ADVISORY_ONLY | test_audio_entropy_advisory |

---

## Mapping détaillé — External Signals temporal receipt

```yaml
evidence_mapping_temporal_receipt:
  source: "52_temporal_receipt.packet.yaml"
  source_status: "SPEC_IMPORTED (F04)"
  
  mapping:
    receipt_id       → OS3EvidenceTicket.evidence_id_base
    action_intent_hash → OS3EvidenceTicket.hash_ref (PLACEHOLDER)
    tick_window      → OS3EvidenceTicket.temporal_context
    anti_replay_status → OS3EvidenceTicket.replay_integrity_flag
    replay_pointer   → OS3EvidenceTicket.replay_ref (NOT_AVAILABLE_P5)
    kx108_decision   → OS3EvidenceTicket.decision_trace_ref (post-X108 only)
    policy_version   → OS3EvidenceTicket.policy_evidence_ref
    
  evidence_type: "HASH_CHAIN"
  hash_status: "PLACEHOLDER_ONLY"
  boundary: "EXTERNAL_SIGNALS_SIGNAL_ONLY"
  claim_scope: "THEORETICAL_ONLY"
```

---

## Mapping détaillé — Anti-bypass checks (P4)

```yaml
evidence_mapping_anti_bypass:
  source: "runtime_contracts/anti_bypass_tests_spec/"
  source_status: "SPEC_ONLY (P4)"
  
  mapping:
    TB-01 to TB-60 (test scenarios) → OS3EvidenceTicket.bypass_check_refs
    ANTI_BYPASS_FAILURE_MODES.md    → OS3EvidenceTicket.failure_audit_trace
    scenario_results (future)       → OS3EvidenceTicket.bypass_audit_evidence
    
  evidence_type: "BYPASS_AUDIT_TRACE"
  source_status: "SPEC_ONLY — tests not yet executable"
  future_gate: "gate humaine + F03/F06/F07 selon pack"
  boundary: "NO_ACT_FROM_PERIPHERY + X108_GATEWAY_REQUIRED"
```

---

## Mapping détaillé — RSSI / RGPD (future)

```yaml
evidence_mapping_rssi_future:
  source: "_source_packs/raw/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip"
  source_status: "COPIED_READONLY — F78B+F03 required"
  
  allowed_future_mapping:
    rssi_audit_narrative → OS3EvidenceTicket.rssi_audit_trace
    rssi_controls       → OS3EvidenceTicket.control_evidence_ref
    rssi_evidence       → OS3EvidenceTicket.security_evidence_ref
    
  forbidden_mapping:
    rssi_certification_claim → INTERDIT (RSSI_EVIDENCE_ONLY)
    auto_block_from_rssi     → INTERDIT (X108_GATEWAY_REQUIRED)
    
  evidence_type: "RSSI_EVIDENCE_FUTURE"
  claim_scope: "EVIDENCE_ONLY — jamais certification"

evidence_mapping_rgpd_future:
  source: "_source_packs/raw/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip"
  source_status: "COPIED_READONLY — F78B+F03+F10 required"
  
  allowed_future_mapping:
    rgpd_readiness_docs → OS3EvidenceTicket.rgpd_trace
    iso27001_controls   → OS3EvidenceTicket.iso_control_trace
    dpia_screening      → OS3EvidenceTicket.dpia_evidence_ref
    
  forbidden_mapping:
    iso_certification_claim → INTERDIT (RGPD_COMPLIANCE_SCOPE_GUARD)
    legal_compliance_claim  → INTERDIT
    
  evidence_type: "RGPD_EVIDENCE_FUTURE"
  claim_scope: "COMPLIANCE_SCOPE_GUARD — jamais conformité légale"
```
