# PLAN3_P7_NEXT_STEPS
# runtime_contracts/education_benchmark_dry_run/reports/
# Plan 3 P7 — Prochaines étapes canoniques
# Date: 2026-06-02
# Refs: REPORT_3_NEXT_STEPS.md (rapport initial — conservé)
# Status: NEXT_STEPS_CANONICAL

---

## Prochaines étapes — ordre recommandé

### 1. PLAN3_FREEZE_AUDIT (immédiat)

Objectif : Auditer les fichiers P7+patch pour vérifier leur statut de gel.

Actions :
- Vérifier que specs/ sont marqués SPEC_ONLY et protégés
- Vérifier cohérence avec PROTECTED_SCOPE.md
- Proposer mise à jour P1_FREEZE.md si applicable
- Confirmer que les 19 fichiers P7+patch sont non-exécutables

Prérequis : PLAN3_P7_RECONCILIATION_READY

---

### 2. PLAN3_RUNTIME_CONTRACTS_INDEX_SYNC (immédiat)

Objectif : Synchroniser l'index des runtime_contracts/ avec P7+patch.

Actions :
- Créer ou mettre à jour `runtime_contracts/INDEX.md`
- Référencer les 19 fichiers P7+patch
- Vérifier cohérence avec les 90 fichiers RC existants
- Confirmer que P0..P7 sont indexés

Prérequis : PLAN3_P7_RECONCILIATION_READY

---

### 3. F07 — Cognitive import audit (moyen terme)

Objectif : Importer le contexte Cognitive advisory.

Actions :
- Identifier composants Cognitive disponibles
- Créer ContextPacket(cognitive_advisory)
- Valider conformité B-EDU-05
- Activer SCE-CAT-05, SCE-CAT-11, SCE-CAT-04

Prérequis : PLAN3_P7 + PLAN3_FREEZE_AUDIT + gate humaine

---

### 4. F06 — Atlas import audit (moyen terme)

Objectif : Importer le contexte Atlas scenario.

Actions :
- Identifier scénarios Atlas éducatifs
- Créer ContextPacket(atlas_scenario)
- Valider conformité B-EDU-06
- Activer SCE-CAT-10

Prérequis : PLAN3_P7 + gate humaine

---

### 5. F03 — RSSI/RGPD import audit (avant toute donnée réelle)

Objectif : Auditer les contraintes RGPD pour données éducatives.

Actions :
- Définir cadre de consentement pour données étudiants
- Documenter obligations RGPD éducatives
- Valider B-EDU-08 + B-EDU-12 + B-EDU-13
- Lier à FM-CAT-05 (personal_data_collected)

Prérequis : PLAN3_P7 + avis RSSI/DPO

---

### 6. F10 — Compliance/data governance audit (avec F03)

Objectif : Auditer la data governance pour le benchmark éducatif.

Actions :
- Définir contraintes de rétention/accès
- Valider l'ensemble B-EDU-* boundaries
- Lier à F03

Prérequis : F03

---

### 7. Benchmark exécutable (long terme)

Prérequis bloquants :
```
PLAN3_P7 ✅
PLAN3_FREEZE_AUDIT
PLAN3_RUNTIME_CONTRACTS_INDEX_SYNC
F07 Cognitive ✅
F06 Atlas ✅
F03 RGPD ✅
F10 Compliance ✅
Gate humaine explicite
Données synthétiques ou consenties disponibles
→ Benchmark exécutable (futur)
```

---

## Dépendances visuelles

```
PLAN3_P7_RECONCILIATION_READY
  ├── PLAN3_FREEZE_AUDIT
  │     └── PLAN3_RUNTIME_CONTRACTS_INDEX_SYNC
  ├── F07 (Cognitive)
  ├── F06 (Atlas)
  ├── F03 (RGPD) ──┐
  └── F10 (Compliance) ──┘
              ↓
    [Gate humaine + données]
              ↓
    Benchmark exécutable (futur)
```
