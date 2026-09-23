# PLAN3_P5_NEXT_STEPS
# runtime_contracts/os3_evidence_dry_run/reports/
# Date: 2026-06-02

---

## Contexte

Plan 3 P5 est terminé avec verdict `PLAN3_P5_OS3_EVIDENCE_DRY_RUN_SPEC_READY`.
11 fichiers créés. Aucune preuve réelle. Aucun runtime modifié.

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers SPEC

### Objectif
Documenter les wrappers readonly pour Graphiti, Brody, et NPL.
Ces sources fournissent des ContextPackets à l'OS3EvidenceTicket futur
(CONTEXT_TRACE_FUTURE, PROVENANCE_TRACE).

### Prérequis
- P5 ✅ — OS3Evidence spec validée
- boundary READONLY_CONTEXT_ONLY ✅
- boundary NPL_ADVISORY_ONLY ✅
- P5 mapping : Graphiti/Brody → CONTEXT_TRACE_FUTURE, NPL → PROVENANCE_TRACE

### Lien P5
P5 a documenté Graphiti/Brody/NPL comme sources OS3Evidence futures.
P6 spécifiera les wrappers readonly qui alimenteront ces traces.

### Livrables attendus
```
runtime_contracts/graphiti_brody_npl_wrappers/
  specs/GRAPHITI_READONLY_WRAPPER_SPEC.md
  specs/BRODY_READONLY_WRAPPER_SPEC.md
  specs/NPL_ADVISORY_WRAPPER_SPEC.md
  mapping/CONTEXT_SOURCES_TO_CONTEXT_PACKET_MAP.md
  mapping/CONTEXT_TO_OS3_EVIDENCE_TRACE_MAP.md  ← nouveau lien P5→P6
  reports/PLAN3_P6_*.md
```

---

## P7 — Education Benchmark Dry-Run SPEC

### Objectif
Documenter le benchmark éducatif avec OS3Evidence comme trace d'audit.

### Prérequis
- P6 ✅ (ou parallèle)
- F07 Cognitive specs importées

### Lien P5
P7 pourra référencer OS3EvidenceTicket pour tracer les décisions du benchmark.

---

## Imports packs (après F78B ✅ + F78C ✅)

### F07 — Cognitive Import (PRIORITAIRE)

**Lien P5 :** Les 458 component specs Cognitive deviendront des sources d'evidence
BYPASS_AUDIT_TRACE via leurs advisory metrics.
**Gate :** F78B ✅ + F78C ✅ + exclusion 5 packets packages/
**Boundary :** COGNITIVE_REINTEGRATION_ADVISORY_ONLY

### F03 — RSSI + RGPD Import

**Lien P5 :** FM-14 (rssi_evidence_claims_certification) et FM-15 (rgpd_evidence_claims_compliance)
protègent contre les claims invalides lors de F03.
**Gate :** F78B ✅ + F78C ✅ + exclusion 39 .py + résoudre 8 dups RGPD

### F06 — Atlas Import

**Lien P5 :** Atlas deviendra source CONTEXT_TRACE_FUTURE dans l'OS3Evidence.
**Gate :** F78B ✅ + F78C ✅ + exclusion 18 .py + .pytest_cache + .runtime_freezes

### F10 — RGPD Final Compliance

**Gate :** F03 ✅ + review humaine
FM-15 (rgpd_evidence_claims_compliance) reste actif après F03.

---

## Future implementation : hash/seal/merkle/replay réels

### Séquence technique

```
P5 Spec ✅ (ce run)
  ↓
Gate humaine sur P5
  ↓
Kernel OS3 Python implémenté (tests/anti_bypass/ après P4 gate)
  ↓
sha256 hash réel calculé
  ↓
RFC3161 seal intégré
  ↓
Merkle tree construit
  ↓
Replay exécutable
  ↓
Lean proof P13_Immutability
  ↓
Lean proof P17_AuditGrowth
```

---

## Séquence complète recommandée

```
P5 ✅ (ce run)
  │
  ├─ P6 — Graphiti/Brody/NPL wrappers SPEC
  │    (alimente OS3Evidence CONTEXT_TRACE_FUTURE)
  │    ↓
  ├─ F07 — Cognitive import (0 .py, 0 dups — PRIORITAIRE)
  │    ↓
  ├─ P7 — Education benchmark SPEC (avec OS3Evidence trace)
  │    ↓
  ├─ F03 — RSSI+RGPD import (FM-14/15 protègent les claims)
  │    ↓
  ├─ F06 — Atlas import (sélectif)
  │    ↓
  └─ F10 — RGPD final compliance
```

---

## Interdictions permanentes après P5

```
- Jamais affirmer hash/seal/merkle réels avant kernel OS3 implémenté
- Jamais OS3Evidence comme source de décision
- Jamais RSSI/RGPD certifiés via evidence seule
- X108 reste seul droit de passage, même avec OS3Evidence complet
```
