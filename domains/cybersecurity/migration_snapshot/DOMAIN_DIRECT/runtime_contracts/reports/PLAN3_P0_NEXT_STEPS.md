# PLAN3_P0_NEXT_STEPS
# runtime_contracts/reports/PLAN3_P0_NEXT_STEPS.md
# Date: 2026-06-02

---

## Contexte

Plan 3 P0 est terminé avec verdict `PLAN3_P0_RUNTIME_CONTRACT_SKELETON_READY`.
Ce document décrit les prochaines phases P1 → P7 et les prérequis manquants.

---

## P0 — Acquis (Plan 3 P0 — terminé)

```
✅ 31 fichiers runtime_contracts/ créés (densité maximale)
✅ 7 contrats documentaires
✅ 7 schemas JSON valides
✅ 9 boundaries (dont 5 dédiées aux sources auditées)
✅ 4 dry-run documentaires
✅ 3 rapports
✅ Baseline freeze créé (_backups/ — 254 fichiers)
✅ Backup guard actif — 0 violation
```

---

## P1_REQUIRED_BOUNDARIES — PRIORITÉ ABSOLUE

Avant tout passage en DRY_RUN_CANDIDATE, créer ces 4 boundaries manquantes :

| Boundary | Pour quel pack | XLSX Phase | Prérequis |
|----------|---------------|-----------|-----------|
| `COGNITIVE_REINTEGRATION_ADVISORY_ONLY` | Cognitive Reintegration (513 fichiers) | F07 | Audit Cognitive d'abord |
| `ATLAS_READONLY_ADVISORY_ONLY` | Branchable Atlas (1738 fichiers, 92 doublons) | F06 | Résolution doublons + Audit Atlas |
| `RSSI_EVIDENCE_ONLY` | RSSI Security (167 fichiers) | F03 | Audit RSSI claim-scope |
| `RGPD_COMPLIANCE_SCOPE_GUARD` | RGPD ISO (280 fichiers, 8 doublons) | F03/F10 | Audit RGPD compliance claims |

**Format de chaque boundary :** identique aux 9 boundaries existantes (11 sections obligatoires).

---

## P1_REQUIRED_SOURCE_AUDITS — AVANT F03/F06

Auditer les 4 markdowns raw non encore examinés :

| Fichier | Localisation | À auditer avant |
|---------|-------------|-----------------|
| `Fichier markdown (2)(3).md collé` | `_source_packs/raw/` | F03 |
| `Fichier markdown (3)(3).md collé` | `_source_packs/raw/` | F03 |
| `Fichier markdown (4)(1).md collé` | `_source_packs/raw/` | F06 |
| `Fichier markdown (5).md collé` | `_source_packs/raw/` | F06 |

---

## P1 — Packet Schema Validation

**Objectif :** Valider formellement les 7 schemas JSON contre des instances réelles.

Actions :
1. Parser les 7 schemas avec `jsonschema` Python
2. Créer des instances test valides pour chaque schema
3. Vérifier `required fields`, `additionalProperties: false`, `enums`, `boundary fields`
4. Créer les 4 boundaries manquantes (P1_REQUIRED_BOUNDARIES)
5. Créer `RSSI_EVIDENCE_ONLY`, `RGPD_COMPLIANCE_SCOPE_GUARD` après audit F03

**Prérequis :** Plan 3 P0 ✅
**Résultat attendu :** `PLAN3_P1_SCHEMA_VALIDATION_READY`

---

## P2 — External Signals Dry-Run Adapter SPEC

**Objectif :** Créer la spec d'adapter External Signals en dry-run — aucune action réelle.

Actions :
1. Créer `specs/external_signals/F04_DRY_RUN_ADAPTER_SPEC.md`
2. Définir comment C459-C482 alimentent les PeripheralSignalPackets
3. Tester `test_external_signal_cannot_authorize_act`
4. Tester `test_c473_wrapper_non_reauthoring`

**Interdit :** Aucun adapter Python créé — spec seulement.
**Prérequis :** P1 ✅
**Résultat attendu :** `PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_READY`

---

## P3 — X108 Gateway Dry-Run Harness

**Objectif :** Créer un harness dry-run exécutant la chaîne complète sans action réelle.

Actions :
1. Harness Python (NON dans packages/) dans `periphery/x108_dry_run/`
2. Exécuter la chaîne complète : ContextPacket → IntentEnvelope → X108 → DecisionTicket
3. `replay_status = NOT_RUN` en dry-run
4. Aucune action monde réel — return (ticket, evidence) pour audit

**Prérequis :** P2 ✅ + audit humain gate
**Résultat attendu :** `PLAN3_P3_X108_GATEWAY_DRY_RUN_READY`

---

## P4 — Anti-Bypass Tests

**Objectif :** Tests exécutables vérifiant que personne ne contourne X-108.

Tests futurs :
- `test_no_act_from_periphery` (pattern 650+ existants)
- `test_intent_envelope_requires_x108`
- `test_bypass_x108_detected_block`
- `test_decision_ticket_only_from_x108`
- `test_peripheral_override_forbidden`

**Prérequis :** P3 ✅
**Résultat attendu :** `PLAN3_P4_ANTI_BYPASS_TESTS_READY`

---

## P5 — OS3 Evidence Ticket Dry-Run

**Objectif :** Intégrer le OS3EvidenceTicket complet avec sha256 chain et seal.

Actions :
1. Étendre `periphery/os3_ticket.py` pour inclure `evidence_type`, `seal_status`, `verification_status`
2. `replay_status = NOT_RUN` → transition vers PASS en phase production
3. `test_os3_evidence_hash_chain_valid`

**Prérequis :** P4 ✅
**Résultat attendu :** `PLAN3_P5_OS3_EVIDENCE_DRY_RUN_READY`

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers

**Objectif :** Créer des wrappers readonly pour ces 3 modules.

Actions :
1. `periphery/wrappers/graphiti_readonly_wrapper.py`
2. `periphery/wrappers/brody_readonly_wrapper.py`
3. NPL : spec d'implémentation Python (après audit COGNITIVE/ATLAS boundaries P1)
4. Tests : `test_graphiti_wrapper_no_write`, `test_brody_readonly_only`

**Prérequis :** P5 ✅ + NPL_TO_PLAN3_CONSTRAINTS.md ✅
**Résultat attendu :** `PLAN3_P6_READONLY_WRAPPERS_READY`

---

## P7 — Education Benchmark / Dashboards OS3

**Objectif :** Dry-run pour benchmarks éducation et dashboards OS3.

Actions :
1. Dashboard OS3 : affichage des DecisionTickets + OS3EvidenceTickets (lecture seule)
2. Benchmark éducation : simulation de flux d'intentions éducationnelles
3. Metrics candidate : utiliser L_value (P107), thermo_debt (P161) comme signaux advisory

**Prérequis :** P6 ✅

---

## Phases XLSX (F03, F06, F07) — À planifier après P1

| Phase | Pack | Action | Boundary requise | Prérequis |
|-------|------|--------|-----------------|----------|
| F03 | RSSI Security + RGPD ISO | Import specs + claim-scope guard | `RSSI_EVIDENCE_ONLY`, `RGPD_COMPLIANCE_SCOPE_GUARD` | P1_REQUIRED_SOURCE_AUDITS |
| F06 | Branchable Atlas (1738 fichiers, 92 doublons) | Résolution doublons + import + boundary | `ATLAS_READONLY_ADVISORY_ONLY` | P1 + résolution doublons |
| F07 | Cognitive Reintegration (513 fichiers) | Import specs + boundary | `COGNITIVE_REINTEGRATION_ADVISORY_ONLY` | P1 + audit Cognitive |

---

## Interdictions permanentes (jamais lever sans approbation humaine)

```
❌ "RSSI/RGPD sont conformes" / "ISO est certifié" — ne jamais écrire
❌ "Cognitive/Atlas sont runtime-ready" — non encore importés ni testés
❌ "tous les zips sont implémentés" — seul External Signals est SPEC_IMPORTED
❌ "Plan 3 P0 active le runtime" — documentation contractuelle uniquement
❌ "NPL prouve / P107/P161 sont Lean-proven" — INTERDIT
❌ "External Signals autorise X108" — INTERDIT C473
❌ packages/ — INTERDIT dans ce repo
```

---

## Résumé P1_REQUIRED au plus urgent

**Créer immédiatement en P1 :**
1. `runtime_contracts/boundaries/COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md`
2. `runtime_contracts/boundaries/ATLAS_READONLY_ADVISORY_ONLY.md`
3. `runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md`
4. `runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md`

**Auditer avant F03/F06 :**
- 4 markdowns raw dans `_source_packs/raw/`
