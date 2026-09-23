# EXAMPLE_INVALID_PROOF_CLAIM_BLOCK
# runtime_contracts/os3_evidence_dry_run/examples/
# Plan 3 P5 — Exemple documentaire — NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document illustre des claims invalides sur hash/seal/merkle/replay/RSSI/RGPD.
Aucune exécution. Aucune donnée réelle. Aucune preuve.
```

---

## Exemple 1 — OS3Evidence claim hash=VERIFIED sans calcul

```json
{
  "evidence_id": "EV-EXAMPLE-INVALID-HASH",
  "linked_decision_ticket": "DT-EXAMPLE-001",
  "evidence_type": "HASH_CHAIN",
  "hash": "a1b2c3d4e5f6789...",
  "hash_status": "VERIFIED",
  "_VIOLATION": "hash_status=VERIFIED sans calcul réel — NON ADMISSIBLE en P5",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "hash_claim_without_hash",
      "trigger": "hash_status=VERIFIED sans calcul réel",
      "boundary": "NO_REAL_HASH_CLAIM",
      "fail_closed": true,
      "suggested_decision": "HOLD",
      "priority": "HIGH",
      "correct_value": "hash_status = PLACEHOLDER_ONLY"
    },
    {
      "failure_code": "verification_claim_without_verification",
      "trigger": "verification implicite via hash_status=VERIFIED",
      "fail_closed": true,
      "suggested_decision": "HOLD"
    }
  ],
  "aggregate_result": "HOLD — claim refusé",
  "dry_run": true
}
```

---

## Exemple 2 — RSSI evidence claim RSSI_CERTIFIED

```json
{
  "evidence_id": "EV-EXAMPLE-RSSI-CERTIFIED",
  "linked_decision_ticket": "DT-EXAMPLE-003",
  "evidence_type": "RSSI_EVIDENCE_FUTURE",
  "source": "OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1",
  "source_status": "COPIED_READONLY",
  "rssi_certification_claim": "RSSI_CERTIFIED",
  "_VIOLATION": "claim RSSI_CERTIFIED sans F78B+F03 validés",
  "_VIOLATION_2": "RSSI = evidence uniquement, jamais certification",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "rssi_evidence_claims_certification",
      "trigger": "rssi_certification_claim=RSSI_CERTIFIED",
      "boundary_violated": "RSSI_EVIDENCE_ONLY",
      "gate_required": ["F78B", "F03"],
      "fail_closed": true,
      "suggested_decision": "BLOCK — claim refusé",
      "priority": "HIGH",
      "correct_formulation": "RSSI = evidence/audit docs — jamais certification réelle"
    },
    {
      "failure_code": "source_pack_evidence_without_F78B",
      "trigger": "RSSI pack utilisé comme OS3 source sans F78B+F03",
      "fail_closed": true,
      "suggested_decision": "import bloqué"
    }
  ],
  "aggregate_result": "BLOCK — claim refusé + import bloqué",
  "dry_run": true
}
```

---

## Exemple 3 — RGPD evidence claim ISO_CERTIFIED + seal=SEALED sans seal

```json
{
  "evidence_id": "EV-EXAMPLE-RGPD-INVALID",
  "linked_decision_ticket": "DT-EXAMPLE-004",
  "evidence_type": "RGPD_EVIDENCE_FUTURE",
  "source": "OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2",
  "source_status": "COPIED_READONLY",
  "rgpd_compliance_claim": "ISO_27001_CERTIFIED",
  "seal_status": "SEALED",
  "_VIOLATION": "ISO_27001_CERTIFIED claim sans certification réelle",
  "_VIOLATION_2": "seal_status=SEALED sans seal réel",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "rgpd_evidence_claims_compliance",
      "trigger": "rgpd_compliance_claim=ISO_27001_CERTIFIED",
      "boundary_violated": "RGPD_COMPLIANCE_SCOPE_GUARD",
      "gate_required": ["F78B", "F03", "F10"],
      "fail_closed": true,
      "suggested_decision": "BLOCK — claim refusé",
      "priority": "HIGH",
      "correct_formulation": "RGPD = readiness docs — jamais certification légale"
    },
    {
      "failure_code": "seal_claim_without_seal",
      "trigger": "seal_status=SEALED sans seal réel en P5",
      "boundary": "NO_REAL_SEAL_CLAIM",
      "fail_closed": true,
      "suggested_decision": "HOLD — claim refusé",
      "correct_value": "seal_status = PLACEHOLDER_ONLY"
    }
  ],
  "aggregate_result": "BLOCK",
  "dry_run": true
}
```

---

## Exemple 4 — OS3Evidence tentant d'override X108 (C473)

```json
{
  "evidence_id": "EV-EXAMPLE-OVERRIDE-ATTEMPT",
  "linked_decision_ticket": "DT-EXAMPLE-BLOCK-001",
  "evidence_type": "OVERRIDE_ATTEMPT",
  "_VIOLATION": "X108 a produit BLOCK — OS3Evidence tente de réautoriser",
  "override_x108_decision": "ALLOW",
  "wrapper_reauthoring": true,
  "_VIOLATION_2": "wrapper_reauthoring=true — violation C473 absolue",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "evidence_overrides_x108",
      "trigger": "override_x108_decision=ALLOW après BLOCK X108",
      "boundary_violated": "C473 law + EXTERNAL_SIGNALS_SIGNAL_ONLY",
      "fail_closed": true,
      "suggested_decision": "BLOCK absolu + audit critique",
      "priority": "CRITICAL"
    }
  ],
  "aggregate_result": "BLOCK absolu",
  "note": "C473 (Wrapper Non-Reauthoring Law) — violation absolue — jamais réautorisable",
  "dry_run": true
}
```
