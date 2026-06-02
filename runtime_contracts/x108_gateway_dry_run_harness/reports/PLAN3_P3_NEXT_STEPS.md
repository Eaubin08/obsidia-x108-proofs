# PLAN3_P3_NEXT_STEPS
# runtime_contracts/x108_gateway_dry_run_harness/reports/
# Date: 2026-06-02

---

## Contexte

Plan 3 P3 est terminé avec verdict `PLAN3_P3_X108_GATEWAY_DRY_RUN_HARNESS_SPEC_READY`.
10/10 fichiers créés. Aucun harness actif. Aucun runtime modifié.

---

## PRIORITÉ ABSOLUE — F78B SOURCE_PACKS_DEEP_DIFF_AUDIT

```
F78B DOIT être déclaré READY avant F03/F06/F07/F10.

Statut actuel :
  SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/ — amorcé par processus externe
  Contenu : non validé par P3

F78B doit produire pour chaque zip source :
  ZIP_SOURCE           — chemin exact
  FILES_INTERNAL       — liste complète des fichiers
  ALREADY_EXTRACTED?   — partiellement ou totalement
  LOCAL_PATH?          — chemin local si extrait
  KEEP?                — à conserver
  INTEGRATE?           — à intégrer dans specs/
  ARCHIVE_ONLY?        — archive uniquement
  COLLISION?           — conflits avec specs/ existants
  CLAIM_SCOPE?         — scope admissible
  BOUNDARY_REQUIRED?   — boundary spécifique nécessaire

Packs concernés :
  RSSI Security (167 fichiers) → then F03
  RGPD ISO (280 fichiers)     → then F03 + F10
  Branchable Atlas (1738)     → then F06
  Cognitive (513)             → then F07

Interdiction jusqu'à F78B validé :
  Aucun import dans specs/
  Aucun adapter actif
  Aucun claim runtime-ready
```

---

## P4 — Anti-bypass Tests SPEC before executable tests

### Objectif
Documenter les tests anti-bypass AVANT de les rendre exécutables.
Prouver sur papier qu'aucune périphérie ne peut contourner X108.

### Prérequis
- P3 ✅ (X108 Gateway Harness Spec)
- boundaries NO_ACT_FROM_PERIPHERY, X108_GATEWAY_REQUIRED ✅
- 23 failure modes harness P3 ✅

### Livrables attendus
```
runtime_contracts/anti_bypass_tests/
  specs/ANTI_BYPASS_TEST_SPEC.md
  specs/PERIPHERY_SOVEREIGNTY_VIOLATION_SPEC.md
  specs/P107_P161_OVERAUTHORITY_TEST_SPEC.md
  specs/SOURCE_PACK_IMPORT_GUARD_TEST_SPEC.md
  mapping/BYPASS_VECTORS_TO_BOUNDARIES_MAP.md
  failure_modes/ANTI_BYPASS_TEST_FAILURE_MODES.md
  reports/PLAN3_P4_SCOPE_VERIFICATION.md
  reports/PLAN3_P4_NEXT_STEPS.md
```

### Boundary
NO_ACT_FROM_PERIPHERY / X108_GATEWAY_REQUIRED / FAIL_CLOSED / SPEC_ONLY

---

## P5 — OS3 Evidence Ticket Dry-Run SPEC

### Objectif
Documenter le flux complet OS3EvidenceTicket attaché à chaque DecisionTicket.
Prouver que chaque décision est traçable, hashable, et auditable.

### Prérequis
- P3 ✅ (theoretical OS3EvidenceTicket binding documenté)
- schemas/os3_evidence_ticket.schema.json ✅
- contracts/OS3EvidenceTicket.contract.md ✅
- P2 : temporal_receipt → OS3EvidenceTicket mapping ✅

### Livrables attendus
```
runtime_contracts/os3_evidence_dry_run/
  specs/OS3_EVIDENCE_DRY_RUN_SPEC.md
  specs/MERKLE_SEAL_REPLAY_SPEC.md
  specs/HASH_CHAIN_BINDING_SPEC.md
  mapping/DECISION_TICKET_TO_EVIDENCE_MAP.md
  failure_modes/OS3_EVIDENCE_FAILURE_MODES.md
  reports/PLAN3_P5_SCOPE_VERIFICATION.md
  reports/PLAN3_P5_NEXT_STEPS.md
```

### Invariants
P13_Immutability / merkleRoot_change_if_leaf_change / P17_AuditGrowth

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers SPEC

### Objectif
Documenter les wrappers readonly pour Graphiti, Brody, et NPL.
Aucun de ces modules ne doit pouvoir écrire ou décider.

### Prérequis
- P3 ✅ (binding map ContextPacket sources documentée)
- boundary READONLY_CONTEXT_ONLY ✅
- boundary NPL_ADVISORY_ONLY ✅
- Note : corpus Brody absent de Graphiti V20 (confirmé audit P0)

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
Documenter le benchmark éducatif Obsidia X-108.
Scénarios tests documentaires uniquement. Aucun déclenchement réel.

### Livrables attendus
```
runtime_contracts/education_benchmark_dry_run/
  specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md
  specs/BENCHMARK_SCENARIOS_SPEC.md
  examples/EXAMPLE_BENCHMARK_SAFE.md
  examples/EXAMPLE_BENCHMARK_BLOCKED.md
  reports/PLAN3_P7_SCOPE_VERIFICATION.md
  reports/PLAN3_P7_NEXT_STEPS.md
```

---

## Séquence recommandée

```
F78B SOURCE_PACKS_DEEP_DIFF_AUDIT (OBLIGATOIRE — run dédié)
  │
  ├── P4 Anti-bypass tests SPEC
  │     ↓
  │   P5 OS3 Evidence dry-run SPEC
  │     ↓
  │   P6 Graphiti/Brody/NPL wrappers SPEC
  │     ↓
  │   P7 Education benchmark SPEC
  │
  ├── F03 RSSI + RGPD import (après F78B ✅)
  │     ↓
  │   F10 RGPD final compliance
  │
  ├── F06 Atlas import (après F78B ✅)
  │
  └── F07 Cognitive import (après F78B ✅)
```

---

## Interdictions permanentes

```
- Ne pas importer les zips sans F78B validé
- Ne pas créer d'adapter Python actif avant P4+F78B
- Ne pas présenter External Signals comme autorité
- Ne pas prétendre RSSI/RGPD/Atlas/Cognitive runtime-ready
- Ne pas prétendre P107/P161 Lean-prouvés
- Ne pas modifier le runtime existant
- Ne pas commit/push sans validation explicite
```

---

## Gaps F-series toujours ouverts

| Gap | Description | Gate | Phase cible |
|-----|-------------|------|-------------|
| F78B | Source packs deep diff audit | — | Run dédié |
| F03 | RSSI + RGPD import | F78B ✅ | Après F78B |
| F06 | Atlas import | F78B ✅ | Après F78B |
| F07 | Cognitive import | F78B ✅ | Après F78B |
| F10 | RGPD final compliance | F03 ✅ | Après F03 |
