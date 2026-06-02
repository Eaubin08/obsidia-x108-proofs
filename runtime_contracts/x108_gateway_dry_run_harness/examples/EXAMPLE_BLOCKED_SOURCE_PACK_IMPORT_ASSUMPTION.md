# EXAMPLE_BLOCKED_SOURCE_PACK_IMPORT_ASSUMPTION
# runtime_contracts/x108_gateway_dry_run_harness/examples/
# Plan 3 P3 — Exemple documentaire JSON — NO RUNTIME EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document illustre les patterns BLOQUÉS liés aux source packs non audités.
Aucune donnée réelle. Aucune exécution. Aucun tool call.
F78B est obligatoire avant tout import réel de ces packs.
```

---

## Exemple 1 : IntentEnvelope BLOQUÉ — Atlas assumed runtime-ready sans F78B

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-ATLAS-001",
  "source_module": "example_atlas_adapter_premature",
  "action_candidate_type": "READ",
  "target_domain": "branchable_atlas",
  "irreversibility_level": "REVERSIBLE",
  "criticality_level": "MEDIUM",
  "requires_x108": true,
  "context_packet_refs": [
    "CP-EXAMPLE-atlas-context-001"
  ],
  "_VIOLATION": "Atlas source pack non audité par F78B",
  "claim": "ATLAS_RUNTIME_READY",
  "_VIOLATION_CLAIM": "pack assumé extrait et intégré sans F78B validé",
  "dry_run": true
}
```

### ContextPacket Atlas (invalide — pack non extrait)

```json
{
  "context_id": "CP-EXAMPLE-atlas-context-001",
  "source_layer": "branchable_atlas",
  "source_module": "atlas_context_premature",
  "source_status": "COPIED_READONLY",
  "_REAL_STATUS": "COPIED_READONLY — non importé dans specs/ — F78B + F06 required",
  "advisory_only": true,
  "emits_verdict": false,
  "_VIOLATION": "atlas pack non audité — claim de contenu non vérifiable",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "source_pack_not_deep_diffed",
        "reason": "Atlas pack utilisé sans F78B validé",
        "gate_required": ["F78B", "F06"],
        "result": "fail_closed → block F06 until F78B",
        "suggested_decision": "HOLD",
        "priority": "HIGH"
      },
      {
        "code": "zip_content_assumed_imported",
        "reason": "Atlas zip assumé extrait sans vérification FILES_INTERNAL",
        "result": "source_review_required → fail_closed",
        "suggested_decision": "HOLD",
        "priority": "HIGH"
      },
      {
        "code": "pack_runtime_ready_claim_without_F78B",
        "reason": "claim ATLAS_RUNTIME_READY sans F78B validé",
        "boundary_violated": "ATLAS_READONLY_ADVISORY_ONLY",
        "result": "overauthority_flag → fail_closed",
        "suggested_decision": "BLOCK",
        "priority": "CRITICAL"
      }
    ],
    "aggregate_result": "BLOCK",
    "f78b_gate": "REQUIRED_BEFORE_UNBLOCK",
    "dry_run": true
  }
}
```

---

## Exemple 2 : IntentEnvelope BLOQUÉ — RSSI claim certifié sans F78B

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-RSSI-001",
  "source_module": "example_rssi_adapter_premature",
  "action_candidate_type": "EXECUTE",
  "target_domain": "security_layer",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "CRITICAL",
  "requires_x108": true,
  "_VIOLATION": "RSSI pack non audité par F78B + claim RSSI_CERTIFIED",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "rssi_certification_claim_attempted",
        "reason": "claim RSSI = sécurité certifiée sans audit F78B + F03",
        "boundary_violated": "RSSI_EVIDENCE_ONLY",
        "gate_required": ["F78B", "F03"],
        "result": "fail_closed",
        "suggested_decision": "BLOCK",
        "priority": "HIGH"
      },
      {
        "code": "source_pack_not_deep_diffed",
        "reason": "RSSI pack utilisé sans F78B validé",
        "result": "fail_closed → block F03",
        "suggested_decision": "BLOCK",
        "priority": "HIGH"
      }
    ],
    "aggregate_result": "BLOCK",
    "f78b_gate": "REQUIRED_BEFORE_UNBLOCK",
    "dry_run": true
  }
}
```

---

## Exemple 3 : IntentEnvelope BLOQUÉ — RGPD claim ISO conforme sans F78B

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-RGPD-001",
  "source_module": "example_rgpd_adapter_premature",
  "action_candidate_type": "WRITE",
  "target_domain": "compliance_layer",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "CRITICAL",
  "requires_x108": true,
  "_VIOLATION": "RGPD pack non audité par F78B + claim ISO_CERTIFIED",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "rgpd_compliance_claim_attempted",
        "reason": "claim RGPD = ISO conforme sans F78B + F03 + F10",
        "boundary_violated": "RGPD_COMPLIANCE_SCOPE_GUARD",
        "gate_required": ["F78B", "F03", "F10"],
        "result": "fail_closed",
        "suggested_decision": "BLOCK",
        "priority": "HIGH"
      }
    ],
    "aggregate_result": "BLOCK",
    "f78b_gate": "REQUIRED_BEFORE_UNBLOCK",
    "dry_run": true
  }
}
```

---

## Résumé des gates F78B pour chaque pack bloqué

| Source pack | F78B required | Then | Status actuel |
|-------------|--------------|------|---------------|
| RSSI Security (167 files) | ✅ OUI | F03 | COPIED_READONLY |
| RGPD ISO (280 files) | ✅ OUI | F03 + F10 | COPIED_READONLY |
| Branchable Atlas (1738 files) | ✅ OUI | F06 | COPIED_READONLY |
| Cognitive Reintegration (513 files) | ✅ OUI | F07 | COPIED_READONLY |

```
SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/ :
  Dossier présent en racine — amorcé par processus externe.
  Contenu non validé par P3.
  F78B doit être déclaré READY par un run dédié, séparément de P3.
```
