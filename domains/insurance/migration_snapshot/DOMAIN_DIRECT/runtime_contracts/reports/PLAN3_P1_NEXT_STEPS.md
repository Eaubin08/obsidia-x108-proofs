# PLAN3_P1_NEXT_STEPS
# runtime_contracts/reports/PLAN3_P1_NEXT_STEPS.md
# Date: 2026-06-02

---

## Contexte

Plan 3 P1 est terminé avec verdict `PLAN3_P1_PACKET_SCHEMA_AND_BOUNDARIES_READY`.
Ce document décrit les prochaines phases P2 → P7.

---

## Acquis P1 (terminé)

```
✅ 7/7 schemas JSON validés (VALID + alignment contract)
✅ 4 boundaries spécifiques créées (Cognitive, Atlas, RSSI, RGPD)
✅ 4 rapports P1 créés
✅ 13 boundaries totales dans runtime_contracts/boundaries/
✅ Backup guard : 0 violations
```

---

## P2 — External Signals Dry-Run Adapter SPEC ONLY

**Objectif :** Créer la spec d'adapter External Signals en dry-run — aucune action réelle.

```
À créer :
  specs/external_signals/F04_DRY_RUN_ADAPTER_SPEC.md
  runtime_contracts/contracts/ExternalSignalsAdapterSpec.contract.md (optionnel)

Actions :
  - Définir comment C459-C482 alimentent les PeripheralSignalPackets
  - Spécifier la chaîne anti-replay → X108
  - Spécifier la chaîne stale_execution → X108
  - Documenter le mapping temporal_receipt → OS3EvidenceTicket

Tests requis (pas exécutés en P2 — spec seulement) :
  - test_external_signal_cannot_authorize_act
  - test_c473_wrapper_non_reauthoring
  - test_anti_replay_fail_closes

Interdit : aucun adapter Python créé — spec seulement.
```

**Prérequis :** P1 ✅
**Résultat attendu :** `PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_READY`

---

## P3 — X108 Gateway Dry-Run Harness

**Objectif :** Créer un harness dry-run exécutant la chaîne complète sans action réelle.

```
À créer :
  periphery/x108_dry_run/dry_run_harness.py (NON dans packages/)
  periphery/x108_dry_run/README.md

Pipeline dry-run :
  ContextPacket(s) + PeripheralSignalPacket(s)
  → IntentEnvelope
  → x108_gateway.evaluate_dry_run()
  → DecisionTicket (replay_status=NOT_RUN)
  → OS3EvidenceTicket (verification_status=UNVERIFIED)
  → LOG — NO WORLD ACTION

Tests :
  - test_dry_run_no_world_action
  - test_x108_gateway_dry_run_produces_ticket
  - test_decision_ticket_from_x108_only
```

**Prérequis :** P2 ✅ + audit humain gate
**Résultat attendu :** `PLAN3_P3_X108_GATEWAY_DRY_RUN_READY`

---

## P4 — Anti-Bypass Tests

**Objectif :** Tests exécutables vérifiant qu'aucun module ne contourne X-108.

```
Tests à créer :
  - test_no_act_from_all_peripheries (étendre 650+ existants)
  - test_intent_envelope_requires_x108
  - test_bypass_x108_detected_block
  - test_decision_ticket_only_from_x108
  - test_peripheral_override_forbidden
  - test_cognitive_agent_no_decision_authority (F07)
  - test_atlas_no_decision (F06)
  - test_rssi_no_auto_remediation (F03)
  - test_rgpd_template_advisory_only (F03/F10)
```

**Prérequis :** P3 ✅
**Résultat attendu :** `PLAN3_P4_ANTI_BYPASS_TESTS_READY`

---

## P5 — OS3 Evidence Ticket Dry-Run

**Objectif :** Intégrer le OS3EvidenceTicket complet avec sha256 chain.

```
Actions :
  - Étendre periphery/os3_ticket.py pour inclure :
    evidence_type, seal_status, verification_status
  - replay_status = NOT_RUN → transition PASS en production
  - Tests : test_os3_evidence_hash_chain_valid
  - RFC3161 anchor : spec seulement (futur production)
```

**Prérequis :** P4 ✅

---

## P6 — Graphiti/Brody/NPL Readonly Wrappers

**Objectif :** Créer des wrappers readonly pour ces 3 modules.

```
Actions :
  - periphery/wrappers/graphiti_readonly_wrapper.py
  - periphery/wrappers/brody_readonly_wrapper.py
  - NPL : spec d'implémentation Python
  - Tests : test_graphiti_wrapper_no_write, test_brody_readonly_only
  - Labels NPL_ADVISORY_NOT_SOVEREIGN dans tous les ContextPackets NPL
```

**Prérequis :** P5 ✅ + NPL specs Plan 2

---

## P7 — Education Benchmark / Dashboards OS3

**Objectif :** Dry-run pour benchmarks éducation et dashboards OS3.

---

## Phases XLSX à planifier après P2

| Phase | Pack | Boundary requise | Condition préalable |
|-------|------|-----------------|---------------------|
| F03 | RSSI Security + RGPD ISO | ✅ RSSI_EVIDENCE_ONLY + RGPD_COMPLIANCE_SCOPE_GUARD | Auditer 4 markdowns raw avant |
| F06 | Branchable Atlas | ✅ ATLAS_READONLY_ADVISORY_ONLY | Résolution 92 doublons + audit F06 |
| F07 | Cognitive Reintegration | ✅ COGNITIVE_REINTEGRATION_ADVISORY_ONLY | Exclusion 20 QUARANTINE + audit F07 |
| F10 | RGPD (phase légale) | ✅ RGPD_COMPLIANCE_SCOPE_GUARD | Gate légale/DPO requise |

---

## Source Audits restants (à traiter avant F03/F06)

```
P1_REQUIRED_SOURCE_AUDITS (4 markdowns raw) :
  - _source_packs/raw/Fichier markdown (2)(3).md collé
  - _source_packs/raw/Fichier markdown (3)(3).md collé
  - _source_packs/raw/Fichier markdown (4)(1).md collé
  - _source_packs/raw/Fichier markdown (5).md collé

Action : lire + auditer claim-scope avant import F03/F06
```

---

## Interdictions permanentes (à maintenir à travers toutes les phases)

```
❌ "tous les packs sont branchés" — External Signals seul est SPEC_IMPORTED
❌ "Cognitive/Atlas/RSSI/RGPD sont runtime-ready" — COPIED_READONLY uniquement
❌ "conforme RGPD / certifié ISO" — readiness ≠ conformité
❌ "consciousness prouvée" — specs cognitives ≠ preuves
❌ "Atlas agents exécutables" — scenario_candidate ≠ action
❌ packages/ — INTERDIT dans ce repo
❌ NPL/P107/P161 Lean-proven — FUTURE_FORMAL_TARGET Plan 4+
❌ External Signals autorise X108 — C473 non-réautorisation
```
