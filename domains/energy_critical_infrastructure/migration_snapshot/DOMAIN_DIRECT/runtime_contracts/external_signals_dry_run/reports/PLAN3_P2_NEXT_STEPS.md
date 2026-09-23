# PLAN3_P2_NEXT_STEPS
# runtime_contracts/external_signals_dry_run/reports/PLAN3_P2_NEXT_STEPS.md
# Plan 3 P2 — Prochaines étapes
# Date: 2026-06-02

---

## Contexte

Plan 3 P2 est terminé avec verdict `PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_READY`.
7/7 fichiers créés. Aucun adapter actif. Aucun runtime modifié.

Ce document propose les prochaines phases P3 → P7 selon la séquence contractuelle.

---

## P3 — X108 Gateway Dry-Run Harness SPEC ONLY

### Objectif
Documenter le futur harness de test documentaire du gateway X-108.
Aucun code exécutable. Spec only.

### Prérequis
- P0 : runtime_contracts/dry_run/X108_GATEWAY_DRY_RUN.md ✅
- P0 : runtime_contracts/dry_run/DRY_RUN_PIPELINE.md ✅
- P2 : EXTERNAL_SIGNALS_TO_X108_DRY_RUN_PIPELINE.md ✅

### Livrables attendus
```
runtime_contracts/x108_gateway_dry_run/
  specs/X108_GATEWAY_HARNESS_SPEC.md
  specs/X108_GATEWAY_ADMISSION_FLOW.md
  specs/X108_GATEWAY_TAU_VALIDATION_SPEC.md
  mapping/INTENT_ENVELOPE_TO_DECISION_TICKET_MAP.md
  failure_modes/X108_GATEWAY_FAILURE_MODES.md
  reports/PLAN3_P3_SCOPE_VERIFICATION.md
  reports/PLAN3_P3_NEXT_STEPS.md
```

### Boundary
KX108_ONLY / FAIL_CLOSED / NO_RUNTIME_EXECUTION / SPEC_ONLY

---

## P4 — Anti-bypass Tests SPEC before executable tests

### Objectif
Documenter les tests anti-bypass AVANT de les rendre exécutables.
Prouver sur papier qu'aucun module périphérique ne peut contourner X108.

### Prérequis
- P3 : X108 Gateway Harness Spec ✅ (futur)
- P0 : boundaries NO_ACT_FROM_PERIPHERY, X108_GATEWAY_REQUIRED ✅
- P1 : EXTERNAL_SIGNALS_SIGNAL_ONLY, NPL_ADVISORY_ONLY ✅

### Livrables attendus
```
runtime_contracts/anti_bypass_tests/
  specs/ANTI_BYPASS_TEST_SPEC.md
  specs/PERIPHERY_SOVEREIGNTY_VIOLATION_SPEC.md
  mapping/BYPASS_VECTORS_TO_BOUNDARIES_MAP.md
  reports/PLAN3_P4_SCOPE_VERIFICATION.md
  reports/PLAN3_P4_NEXT_STEPS.md
```

### Boundary
NO_ACT_FROM_PERIPHERY / X108_GATEWAY_REQUIRED / FAIL_CLOSED / SPEC_ONLY

---

## P5 — OS3 Evidence Ticket Dry-Run SPEC

### Objectif
Documenter le futur flux OS3EvidenceTicket attaché à chaque DecisionTicket.
Prouver que chaque décision est traçable, hashable, et auditable.

### Prérequis
- P0 : contracts/OS3EvidenceTicket.contract.md ✅
- P0 : schemas/os3_evidence_ticket.schema.json ✅

### Livrables attendus
```
runtime_contracts/os3_evidence_dry_run/
  specs/OS3_EVIDENCE_DRY_RUN_SPEC.md
  specs/MERKLE_SEAL_REPLAY_SPEC.md
  mapping/DECISION_TICKET_TO_EVIDENCE_MAP.md
  reports/PLAN3_P5_SCOPE_VERIFICATION.md
  reports/PLAN3_P5_NEXT_STEPS.md
```

### Invariants
P13_Immutability / merkleRoot_change_if_leaf_change / P17_AuditGrowth

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers SPEC

### Objectif
Documenter les futurs wrappers readonly pour Graphiti, Brody, et NPL.
Aucun de ces modules ne doit pouvoir produire un DecisionTicket ou un ACT.

### Prérequis
- P0 : boundary READONLY_CONTEXT_ONLY ✅
- P1 : boundary NPL_ADVISORY_ONLY ✅
- Mémoire : corpus Brody absent de Graphiti V20 (confirmed P0 audit)

### Livrables attendus
```
runtime_contracts/graphiti_brody_npl_wrappers/
  specs/GRAPHITI_READONLY_WRAPPER_SPEC.md
  specs/BRODY_READONLY_WRAPPER_SPEC.md
  specs/NPL_ADVISORY_WRAPPER_SPEC.md
  mapping/CONTEXT_SOURCES_TO_CONTEXT_PACKET_MAP.md
  reports/PLAN3_P6_SCOPE_VERIFICATION.md
  reports/PLAN3_P6_NEXT_STEPS.md
```

### Boundary
READONLY_CONTEXT_ONLY / NPL_ADVISORY_ONLY / NO_ACT_FROM_PERIPHERY / SPEC_ONLY

---

## P7 — Education Benchmark Dry-Run SPEC

### Objectif
Documenter le futur benchmark éducatif Obsidia X-108.
Scénarios test documentaires uniquement. Aucun déclenchement réel.

### Livrables attendus
```
runtime_contracts/education_benchmark_dry_run/
  specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md
  specs/BENCHMARK_SCENARIOS_SPEC.md
  reports/PLAN3_P7_SCOPE_VERIFICATION.md
  reports/PLAN3_P7_NEXT_STEPS.md
```

---

## Gaps F-series toujours ouverts

| Gap | Description | Phase cible |
|-----|-------------|-------------|
| F03 | RSSI Security + RGPD ISO import depuis _source_packs/raw/ | Après P4 |
| F06 | Branchable Atlas import depuis _source_packs/raw/ | Après P6 |
| F07 | Cognitive Reintegration import depuis _source_packs/raw/ | Après P6 |
| F10 | RGPD ISO final compliance check | Après F03 |

Prérequis commun à F03/F06/F07/F10 :
- Audit markdown raw avant tout import
- Boundary spécifique validée (P1) ✅
- RuntimeAdmissionContract satisfait

---

## 4 boundaries P1 créées — branchement futur par pack

| Boundary | Pack | Phase branchement |
|----------|------|-------------------|
| COGNITIVE_REINTEGRATION_ADVISORY_ONLY | Cognitive Reintegration (513 files) | F07 |
| ATLAS_READONLY_ADVISORY_ONLY | Branchable Atlas (1738 files) | F06 |
| RSSI_EVIDENCE_ONLY | RSSI Security (167 files) | F03 |
| RGPD_COMPLIANCE_SCOPE_GUARD | RGPD ISO (280 files) | F03/F10 |

Chaque pack doit passer par RuntimeAdmissionContract avant import dans specs/.
Aucun pack n'est runtime-branché actuellement.

---

## Interdictions permanentes jusqu'à P3+

```
- Ne pas présenter External Signals comme autorité de décision
- Ne pas créer d'adapter Python actif
- Ne pas importer les zips sans audit préalable
- Ne pas rendre RSSI/RGPD/Cognitive/Atlas runtime-ready sans F03/F06/F07
- Ne pas modifier le runtime existant
- Ne pas commit/push sans validation explicite
```

---

## Séquence recommandée

```
P3 (X108 Gateway Harness)
  → P4 (Anti-bypass tests)
    → P5 (OS3 Evidence)
      → P6 (Graphiti/Brody/NPL)
        → P7 (Education benchmark)
          → F03 (RSSI+RGPD import)
            → F06 (Atlas import)
              → F07 (Cognitive import)
                → F10 (RGPD final compliance)
```
