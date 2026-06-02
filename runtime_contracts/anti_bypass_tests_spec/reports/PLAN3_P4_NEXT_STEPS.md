# PLAN3_P4_NEXT_STEPS
# runtime_contracts/anti_bypass_tests_spec/reports/
# Date: 2026-06-02

---

## Contexte

Plan 3 P4 est terminé avec verdict `PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_READY`.
8 fichiers créés. Aucun test exécutable. Aucun runtime modifié.

---

## P5 — OS3 Evidence Ticket Dry-Run SPEC

### Objectif
Documenter le flux complet OS3EvidenceTicket attaché à chaque DecisionTicket.
Prouver sur papier que chaque décision est traçable, hashable, et auditable.

### Prérequis
- P4 ✅ — spec anti-bypass validée
- contracts/OS3EvidenceTicket.contract.md ✅
- schemas/os3_evidence_ticket.schema.json ✅
- P2 temporal_receipt → OS3EvidenceTicket mapping ✅
- P4 tests TB-38, TB-39, TB-58, TB-60 → définissent les critères OS3

### Livrables attendus
```
runtime_contracts/os3_evidence_dry_run/
  specs/OS3_EVIDENCE_DRY_RUN_SPEC.md
  specs/MERKLE_SEAL_REPLAY_SPEC.md
  specs/HASH_CHAIN_BINDING_SPEC.md
  mapping/DECISION_TICKET_TO_EVIDENCE_MAP.md
  failure_modes/OS3_EVIDENCE_FAILURE_MODES.md
  reports/PLAN3_P5_*.md
```

### Invariants
P13_Immutability / merkleRoot_change_if_leaf_change / P17_AuditGrowth

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers SPEC

### Objectif
Documenter les wrappers readonly pour Graphiti, Brody, et NPL.

### Prérequis
- P5 ✅ (ou parallèle)
- P4 tests TB-09, TB-10, TB-15, TB-35 → définissent les critères readonly
- boundary READONLY_CONTEXT_ONLY ✅
- boundary NPL_ADVISORY_ONLY ✅
- Note : corpus Brody absent de Graphiti V20

### Livrables attendus
```
runtime_contracts/graphiti_brody_npl_wrappers/
  specs/GRAPHITI_READONLY_WRAPPER_SPEC.md
  specs/BRODY_READONLY_WRAPPER_SPEC.md
  specs/NPL_ADVISORY_WRAPPER_SPEC.md
  mapping/CONTEXT_SOURCES_TO_CONTEXT_PACKET_MAP.md
  reports/PLAN3_P6_*.md
```

---

## P7 — Education Benchmark Dry-Run SPEC

### Objectif
Documenter le benchmark éducatif Obsidia X-108 avec scénarios test documentaires.

### Prérequis
- P6 ✅
- F07 (Cognitive specs) pour les composants d'apprentissage

### Livrables attendus
```
runtime_contracts/education_benchmark_dry_run/
  specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md
  specs/BENCHMARK_SCENARIOS_SPEC.md
  examples/EXAMPLE_BENCHMARK_*.md
  reports/PLAN3_P7_*.md
```

---

## Imports packs (après F78B ✅ + F78C ✅)

### F07 — Cognitive Import (PRIORITAIRE)

**Pourquoi prioritaire :** Pack le plus propre (0 .py, 0 dups, 508 yaml specs).
**Gate :** F78B ✅ + F78C ✅ + exclusion 5 packets packages/ → specs/cognitive/packets/
**Boundary :** COGNITIVE_REINTEGRATION_ADVISORY_ONLY

Tests P4 qui couvrent ce gate : TB-26, TB-27, TB-28, TB-55

### F03 — RSSI + RGPD Import

**Gate :** F78B ✅ + F78C ✅ + exclusion 39 .py + résoudre 8 dups RGPD
**Boundary :** RSSI_EVIDENCE_ONLY + RGPD_COMPLIANCE_SCOPE_GUARD

Tests P4 qui couvrent ce gate : TB-31, TB-32, TB-33, TB-34, TB-47, TB-48, TB-53, TB-54

### F06 — Atlas Import

**Gate :** F78B ✅ + F78C ✅ + exclusion 18 .py + .pytest_cache + .runtime_freezes
**Boundary :** ATLAS_READONLY_ADVISORY_ONLY

Tests P4 qui couvrent ce gate : TB-29, TB-30, TB-50, TB-51, TB-55

### F10 — RGPD Final Compliance

**Gate :** F03 ✅ + review humaine
**Boundary :** RGPD_COMPLIANCE_SCOPE_GUARD

---

## Séquence recommandée

```
P4 ✅ (ce run)
  │
  ├─ P5 — OS3 Evidence SPEC (TB-38/39/58/60 couverts)
  │    ↓
  ├─ P6 — Graphiti/Brody/NPL wrappers SPEC
  │    ↓
  ├─ F07 — Cognitive import (pack propre — prioritaire)
  │    ↓
  ├─ F03 — RSSI + RGPD import (exclure .py + résoudre dups)
  │    ↓
  ├─ F06 — Atlas import (sélectif — le plus complexe)
  │    ↓
  └─ F10 — RGPD final compliance
```

---

## Interdictions permanentes

```
- Aucun test exécutable avant gate humaine + F03/F06/F07 selon le pack
- Aucun import .py depuis les zips
- Aucun packages/ créé
- XLSX ≠ autorisation d'écriture
- X108 reste seul droit de passage après tous les tests
- Aucun pack présenté comme runtime-ready avant son F0x respectif
```
