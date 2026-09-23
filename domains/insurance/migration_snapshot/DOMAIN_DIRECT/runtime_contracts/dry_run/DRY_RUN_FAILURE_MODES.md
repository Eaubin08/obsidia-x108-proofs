# DRY_RUN_FAILURE_MODES
# runtime_contracts/dry_run/DRY_RUN_FAILURE_MODES.md
# Status: DRY_RUN_DOCUMENTAIRE / NO_RUNTIME_EXECUTION

---

## Principe

Tout failure mode dans le dry-run doit aboutir à `fail_closed` ou `no_act`.
Jamais à `allow_by_default`. Invariant : `aggregate4_fail_closed`.

---

## Table complète des failure modes

| # | Failure Mode | Déclencheur | Comportement fail_closed | Invariant |
|---|-------------|-------------|--------------------------|-----------|
| 1 | Missing authority | `authority ≠ KX108_ONLY` dans IntentEnvelope | Reject → fail_closed | KX108_ONLY_AUTHORITY_SPEC |
| 2 | Unknown source | `source_status = UNKNOWN_SOURCE` | `unknown_source_flag = true` → HOLD candidat | FAIL_CLOSED_PRIORITY |
| 3 | Stale temporal context | `stale_execution_check = FAIL` (External Signals C469) | fail_closed → HOLD candidat | `skew_negative_implies_hold` |
| 4 | NPL verdict attempted | `emits_verdict = true` depuis NPL | Reject → PLAN3_BACKUP_GUARD_VIOLATION | NPL_ADVISORY_ONLY |
| 5 | P107/P161 proof claim | L_value présenté comme Lean-proven | `overauthority_flag` → CLAIM_FORBIDDEN | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY |
| 6 | External Signal decision | External Signals émet ALLOW/HOLD/BLOCK | Reject → violation + BLOCK | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| 7 | Direct ACT attempted | `emits_act = true` depuis périphérie | Reject → fail_closed → BLOCK | NO_ACT_FROM_PERIPHERY |
| 8 | Missing evidence | `evidence_ticket_refs` absent pour CRITICAL | HOLD ou BLOCK selon criticality | X108_GATEWAY_REQUIRED |
| 9 | Missing tau | `tau_status` absent pour IRREVERSIBLE | HOLD — `X108_no_act_before_tau` | `X108_no_act_before_tau` |
| 10 | Conflicting decision | Deux DecisionTickets contradictoires | BLOCK — `aggregate4_fail_closed` | `aggregate4_fail_closed` |
| 11 | Schema invalid | Schema JSON invalide | Reject → fail_closed | FAIL_CLOSED_PRIORITY |
| 12 | Cognitive/Atlas/RSSI/RGPD boundary missing | Module F06/F07/F03 sans boundary dédiée | `boundary_missing_flag` → advisory only — défaut READONLY_CONTEXT_ONLY | NO_ACT_FROM_PERIPHERY (générique) |
| 13 | Hash chain broken | `merkle_root` invalide ou incohérent | BLOCK — `merkleRoot_change_if_leaf_change` | `P13_Immutability` |
| 14 | Replay failure | `replay_status = FAIL` | BLOCK — action compromise | OS3EvidenceTicket |
| 15 | Peripheral override attempted | `peripheral_override` dans DecisionTicket | BLOCK + violation majeure | X108_GATEWAY_REQUIRED |
| 16 | Overconfidence detected | `confidence = 1.0` sans LEAN_PROVEN | `overconfidence_flag` → poids réduit → X108 pénalise | FAIL_CLOSED_PRIORITY |
| 17 | Anti-replay failure | `anti_replay_check = FAIL` (C463) | fail_closed flag → X108 évalue avec pénalité | External Signals C463 |
| 18 | packages/ detected | `packages/` créé | PLAN3_BACKUP_GUARD_VIOLATION | NO_PACKAGES_RUNTIME_BOUNDARY |
| 19 | Label missing | Label de claim-scope absent selon source_layer | `label_missing_flag` → X108 pénalise | Claims enforcement |
| 20 | IRREVERSIBLE without context | IRREVERSIBLE + contexte vide | HOLD — insuffisant pour décider | X108_GATEWAY_REQUIRED |

---

## Sortie systématique de chaque failure mode

```
fail_closed_output = {
    "decision": "HOLD" | "BLOCK",
    "reason_codes": [failure_code],
    "x108_gate_status": "X108_FAIL_CLOSED",
    "fail_closed_candidate": true,
    "no_act": true
}
```

---

## Failure modes spécifiques aux gros packs (Cognitive/Atlas/RSSI/RGPD)

**Failure mode 12 détaillé :**

Ces 4 packs (RSSI Security, RGPD ISO, Cognitive Reintegration, Branchable Atlas)
n'ont pas encore de boundary dédiée dans Plan 3 P0. En attendant P1 :

- Les modules de ces packs sont couverts par les boundaries génériques :
  `NO_ACT_FROM_PERIPHERY` + `READONLY_CONTEXT_ONLY` + `FAIL_CLOSED_PRIORITY`
- Si un signal de ces modules arrive sans boundary dédiée →
  `boundary_specific_missing_flag = true` → advisory only par défaut
- Claim-scope de ces modules : `CLAIMABLE_SPEC_ONLY` au mieux, pas `CLAIMABLE_FORMAL`

**Résolution en P1 :** créer les 4 boundaries manquantes :
- `COGNITIVE_REINTEGRATION_ADVISORY_ONLY`
- `ATLAS_READONLY_ADVISORY_ONLY`
- `RSSI_EVIDENCE_ONLY`
- `RGPD_COMPLIANCE_SCOPE_GUARD`

---

## Tests futurs à créer (P1)

- `test_fail_closed_on_missing_authority`
- `test_fail_closed_on_unknown_source`
- `test_fail_closed_on_stale_execution`
- `test_fail_closed_on_schema_invalid`
- `test_fail_closed_on_conflict`
- `test_no_act_on_all_failure_modes`
