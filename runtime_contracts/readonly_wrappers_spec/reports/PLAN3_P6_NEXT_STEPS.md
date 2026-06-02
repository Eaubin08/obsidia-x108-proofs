# PLAN3_P6_NEXT_STEPS
# runtime_contracts/readonly_wrappers_spec/reports/
# Date: 2026-06-02

---

## Contexte

Plan 3 P6 est terminé : `PLAN3_P6_READONLY_WRAPPERS_SPEC_READY`.
14 fichiers créés. Aucun wrapper actif. Aucune écriture. Aucun runtime modifié.

---

## P7 — Education Benchmark Dry-Run SPEC

### Objectif
Documenter le benchmark éducatif Obsidia X-108 avec ContextPackets readonly comme enrichissement.

### Prérequis
- P6 ✅ — wrappers Graphiti/Brody/NPL spec validée
- F07 (Cognitive specs) pour composants apprentissage
- P5 OS3Evidence pour traçabilité des scénarios benchmark

### Lien P6
P7 pourra utiliser les wrappers Graphiti/Brody/NPL comme sources de ContextPackets
pour enrichir les scénarios éducatifs → IntentEnvelope → X108.

### Livrables attendus
```
runtime_contracts/education_benchmark_dry_run/
  specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md
  specs/BENCHMARK_SCENARIOS_SPEC.md
  mapping/BENCHMARK_CONTEXT_SOURCES_MAP.md  ← intègre P6 wrappers
  examples/EXAMPLE_BENCHMARK_SAFE.md
  examples/EXAMPLE_BENCHMARK_BLOCKED.md
  reports/PLAN3_P7_*.md
```

---

## F07 — Cognitive Import (PRIORITAIRE)

### Lien P6
Les component specs Cognitive (458 yaml) fourniront des ContextPackets advisory
similaires aux wrappers NPL → advisory uniquement → IntentEnvelope → X108.

### Gate
F78B ✅ + F78C ✅ + exclusion 5 packets packages/ → specs/cognitive/packets/
Boundary : COGNITIVE_REINTEGRATION_ADVISORY_ONLY

---

## F03 — RSSI + RGPD Import

### Lien P6
Les docs RSSI/RGPD fourniront des OS3EvidenceTickets futurs (RSSI_EVIDENCE_FUTURE / RGPD_EVIDENCE_FUTURE).
P6 failure modes FM-1 à FM-8 protègent aussi contre les claims RSSI/RGPD invalides.

### Gate
F78B ✅ + F78C ✅ + exclusion 39 .py + résoudre 8 dups RGPD

---

## F06 — Atlas Import

### Lien P6
Atlas deviendra une source CONTEXT_TRACE_FUTURE, similaire à Graphiti.
Wrapper spec future Atlas = extension de GRAPHITI_READONLY_WRAPPER_SPEC.md.

### Gate
F78B ✅ + F78C ✅ + exclusion 18 .py + .pytest_cache + .runtime_freezes

---

## F10 — RGPD Final Compliance

### Gate
F03 ✅ + review humaine
FM-8 BRODY_CONTEXT_CLAIMS_AUTHORITY reste actif.

---

## Future implementation wrappers actifs

```
P6 Spec ✅ (ce run)
  ↓
Gate humaine sur P6
  ↓
periphery/graphiti/ wrapper Python (readonly query adapter)
periphery/brody/ wrapper Python (readonly memory adapter)
periphery/npl/ wrapper Python (advisory extraction adapter)
  ↓
BoundaryContract + RuntimeAdmissionContract pour chaque wrapper
  ↓
Tests tests/readonly_wrappers/ (anti-bypass P4 + wrappers)
  ↓
Lean proofs graphiti_context_only + brody_context_only + npl_advisory_non_sovereign
```

---

## Séquence complète recommandée

```
P6 ✅ (ce run)
  │
  ├─ P7 — Education benchmark SPEC (avec P6 wrappers en contexte)
  │    ↓
  ├─ F07 — Cognitive import (advisory, 0 .py — PRIORITAIRE)
  │    ↓
  ├─ F03 — RSSI+RGPD import (exclure .py + résoudre dups)
  │    ↓
  ├─ F06 — Atlas import (sélectif + Atlas wrapper spec extension)
  │    ↓
  └─ F10 — RGPD final compliance
```

---

## Interdictions permanentes après P6

```
- Aucun wrapper Python actif avant gate humaine
- Graphiti/Brody : aucune écriture sans gate X108 ALLOW
- NPL : jamais verdict moral, jamais diagnostic, jamais proof_claim
- X108 reste seul droit de passage même avec tous les wrappers actifs
- Brody corpus ABSENT de Graphiti V20 — à ne pas confondre
```
