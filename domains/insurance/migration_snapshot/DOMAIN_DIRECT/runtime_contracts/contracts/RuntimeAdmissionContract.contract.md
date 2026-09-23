# RuntimeAdmissionContract
# runtime_contracts/contracts/RuntimeAdmissionContract.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Le RuntimeAdmissionContract définit les conditions minimales et exhaustives
qu'un module doit satisfaire pour passer du statut SPEC_ONLY au statut DRY_RUN,
et éventuellement au statut CONTRACT_READY puis à un runtime contrôlé.

Il garantit que aucun module ne peut être branché au runtime sans avoir passé
les gates de validation contractuelles, schémas, boundaries, tests, et preuves.

Il représente la "loi d'admission" du système — équivalent du péage X-108
appliqué à la progression des modules dans le cycle SPEC → DRY_RUN → PROD.

---

## 2. Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module_name` | string | OUI | Module concerné |
| `current_status` | enum | OUI | Statut actuel |
| `requested_next_status` | enum | OUI | Statut demandé |
| `required_contracts` | string[] | OUI | Contrats nécessaires |
| `required_schemas` | string[] | OUI | Schemas JSON validés |
| `required_boundaries` | string[] | OUI | Boundaries activées |
| `required_tests` | string[] | OUI | Tests futurs requis |
| `required_proofs` | string[] | OUI | Preuves requises (Python/Lean) |
| `forbidden_until_satisfied` | string[] | OUI | Actions interdites jusqu'à satisfaction |
| `admission_decision_source` | enum | OUI | Toujours `KX108_ONLY` |
| `human_gate_required` | boolean | OUI | Gate humain requis avant production |

---

## 3. Allowed Status Transitions

```
SPEC_ONLY       → CONTRACT_READY        (contrats + schemas validés)
CONTRACT_READY  → DRY_RUN_CANDIDATE     (boundaries + plan de tests)
DRY_RUN_CANDIDATE → DRY_RUN_ONLY       (tests de base exécutés)
```

---

## 4. Forbidden Status Transitions

```
SPEC_ONLY       → RUNTIME_ACTIVE        ← INTERDIT ABSOLU
SPEC_ONLY       → PRODUCTION            ← INTERDIT ABSOLU
DRY_RUN_ONLY    → ACT                   ← INTERDIT (dry-run ≠ action)
ANY             → PRODUCTION            sans audit humain + sécurité ← INTERDIT
```

---

## 5. Failure Mode

- `requested_next_status` interdit → `fail_closed` → Reject
- `required_contracts` manquants → Reject
- `required_tests` non exécutés → `DRY_RUN_CANDIDATE` bloqué
- `human_gate_required = true` non validé → Pas d'admission en PROD

---

## 6. JSON Example — NPL Module

```json
{
  "module_name": "narrative_provenance_layer",
  "current_status": "SPEC_ONLY",
  "requested_next_status": "CONTRACT_READY",
  "required_contracts": [
    "ContextPacket.contract.md",
    "BoundaryContract.contract.md",
    "PeripheralSignalPacket.contract.md"
  ],
  "required_schemas": [
    "context_packet.schema.json",
    "peripheral_signal_packet.schema.json"
  ],
  "required_boundaries": [
    "NPL_ADVISORY_ONLY.md",
    "READONLY_CONTEXT_ONLY.md",
    "NO_ACT_FROM_PERIPHERY.md"
  ],
  "required_tests": [
    "test_npl_no_decision_authority",
    "test_npl_packet_readonly",
    "test_npl_metrics_advisory"
  ],
  "required_proofs": [
    "Python test schema validation"
  ],
  "forbidden_until_satisfied": [
    "branching NPL to Graphiti write",
    "NPL emitting ALLOW/HOLD/BLOCK",
    "NPL writing memory"
  ],
  "admission_decision_source": "KX108_ONLY",
  "human_gate_required": true
}
```

---

## 7. Claim-Scope

**Autorisé :** "Le RuntimeAdmissionContract garantit qu'aucun module n'est branché sans validation préalable"
**Interdit :** "Le RuntimeAdmissionContract peut bypasser la gate humaine en production"

---

## 8. Tests Required Later

- `test_admission_contract_forbidden_transitions`
- `test_admission_contract_human_gate_required`
- `test_admission_contract_schema_valid`

---

## 9. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — P1 :** Ce contrat sera le premier à être validé
avant de démarrer tout import F03 (RSSI/RGPD), F06 (Atlas), F07 (Cognitive).
Les `required_boundaries` devront inclure les boundaries spécifiques manquantes.
