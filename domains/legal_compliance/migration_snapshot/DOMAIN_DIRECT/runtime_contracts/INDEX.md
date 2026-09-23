# INDEX — runtime_contracts/
# Plan3 Freeze Audit — Index canonique navigable
# Date: 2026-06-02
# Status: PLAN3_FREEZE_AUDIT_AND_INDEX_SYNC_READY

---

## 1. Status

```
runtime_contracts/ = contract/spec/freeze layer ONLY
Aucun runtime actif. Aucun pack branché. Aucun .py. Aucun benchmark exécuté.
Total fichiers : 116 (109 pré-audit + 7 freeze_audit)
Phases couvertes : P0→P7 + F78B/F78C
Tous les verdicts : FOUND_READY (12/12)
```

---

## 2. Purpose

`runtime_contracts/` est la couche de gouvernance documentaire du noyau X-108.
Elle définit les contrats, schémas, boundaries, et specs de toutes les interactions futures.

Elle **n'est pas** :
- Claim interdit : présenter runtime_contracts/ comme un runtime actif
- Un ensemble de packages installés
- Un benchmark exécuté
- Un système de notation ou de diagnostic

Elle **est** :
- Un squelette de contrats (P0)
- Des specs de dry-run (P2/P3)
- Des specs d'anti-bypass (P4)
- Des specs d'evidence (P5)
- Des specs de wrappers readonly (P6)
- Des specs de benchmark éducatif (P7)
- Un audit de source packs (F78B/F78C)

---

## 3. Global boundary

```
KX108_ONLY          — X108 seul droit de passage pour toute action critique
NO_ACT_FROM_PERIPHERY — Aucune action depuis la périphérie
READONLY_CONTEXT_ONLY — Graphiti/Brody/NPL = lecture seule
FAIL_CLOSED_PRIORITY  — Tout échec → fail_closed
NO_PACKAGES          — Aucun package installé
NO_RUNTIME_EXECUTION — Aucun runtime déclenché
DOCS_ONLY            — Cette couche = documentation uniquement
```

---

## 4. Plan 3 phase map

| Phase | Dossier | Verdict | Fichiers |
|-------|---------|---------|---------|
| P0 | `contracts/`, `boundaries/`, `schemas/`, `dry_run/`, `reports/` | READY | 32 |
| P1 | `schemas/`, `reports/` | READY | 11 |
| P2 | `external_signals_dry_run/` | READY | 8 |
| P2C | (dans P2) | READY | (inclus) |
| P3 | `x108_gateway_dry_run_harness/` | READY | 10 |
| F78B | `_source_discovery/F78B_*/` | READY | external |
| F78C | `_source_discovery/F78C_*/` | READY | external |
| P4 | `anti_bypass_tests_spec/` | READY | 8 |
| P5 | `os3_evidence_dry_run/` | READY | 11 |
| P6 | `readonly_wrappers_spec/` | READY | 14 |
| P7 | `education_benchmark_dry_run/` | READY | 19 |
| P7R | (dans P7) | READY | (inclus) |

---

## 5. P0 — Runtime contracts

Contrats fondamentaux définissant les types d'échange du noyau X-108.

| Fichier | Description |
|---------|-------------|
| `contracts/BoundaryContract.contract.md` | Contrat de boundary |
| `contracts/ContextPacket.contract.md` | Paquet de contexte contextuel |
| `contracts/DecisionTicket.contract.md` | Ticket de décision X108 |
| `contracts/IntentEnvelope.contract.md` | Enveloppe d'intention |
| `contracts/OS3EvidenceTicket.contract.md` | Ticket d'evidence OS3 |
| `contracts/PeripheralSignalPacket.contract.md` | Paquet de signal périphérique |
| `contracts/RuntimeAdmissionContract.contract.md` | Contrat d'admission runtime |
| `dry_run/DRY_RUN_PIPELINE.md` | Pipeline dry-run de base |
| `dry_run/DRY_RUN_FAILURE_MODES.md` | Modes d'échec dry-run |
| `dry_run/NO_WORLD_ACTION_EXECUTION.md` | Interdiction d'action réelle |
| `dry_run/X108_GATEWAY_DRY_RUN.md` | Gateway X108 dry-run |

---

## 6. P1 — Schemas + Boundaries

Schémas JSON pour validation des contrats et boundaries de gouvernance.

| Fichier | Description |
|---------|-------------|
| `schemas/context_packet.schema.json` | Schéma ContextPacket |
| `schemas/intent_envelope.schema.json` | Schéma IntentEnvelope |
| `schemas/decision_ticket.schema.json` | Schéma DecisionTicket |
| `schemas/os3_evidence_ticket.schema.json` | Schéma OS3EvidenceTicket |
| `schemas/peripheral_signal_packet.schema.json` | Schéma PeripheralSignalPacket |
| `schemas/boundary_contract.schema.json` | Schéma BoundaryContract |
| `schemas/runtime_admission_contract.schema.json` | Schéma RuntimeAdmissionContract |
| `boundaries/` (13 fichiers) | Boundaries de gouvernance |

---

## 7. P2 — External Signals dry-run spec

Spec documentaire des signaux externes (NPL, Cognitive, Atlas, Audio/Entropy).

| Fichier clé | Description |
|-------------|-------------|
| `external_signals_dry_run/specs/EXTERNAL_SIGNALS_DRY_RUN_ADAPTER_SPEC.md` | Spec adapter |
| `external_signals_dry_run/specs/EXTERNAL_SIGNALS_TO_X108_DRY_RUN_PIPELINE.md` | Pipeline P2→X108 |
| `external_signals_dry_run/reports/PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_REPORT.md` | Rapport |

---

## 8. P3 — X108 Gateway dry-run harness spec

Spec documentaire du harnais de test de la gateway X108.

| Fichier clé | Description |
|-------------|-------------|
| `x108_gateway_dry_run_harness/specs/X108_GATEWAY_DRY_RUN_HARNESS_SPEC.md` | Spec principale |
| `x108_gateway_dry_run_harness/mapping/INTENT_TO_DECISION_TICKET_DRY_RUN_MAP.md` | Map IntentEnvelope→DecisionTicket |
| `x108_gateway_dry_run_harness/reports/PLAN3_P3_X108_GATEWAY_DRY_RUN_HARNESS_SPEC_REPORT.md` | Rapport |

---

## 9. P4 — Anti-bypass tests spec

Spec documentaire des tests anti-bypass pour toute la couche periphery→X108.

| Fichier clé | Description |
|-------------|-------------|
| `anti_bypass_tests_spec/ANTI_BYPASS_TESTS_SPEC.md` | Spec principale |
| `anti_bypass_tests_spec/matrices/ANTI_BYPASS_TEST_MATRIX.md` | Matrice de tests |
| `anti_bypass_tests_spec/scenarios/BYPASS_SCENARIO_CATALOG.md` | Catalog scénarios |
| `anti_bypass_tests_spec/reports/PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_REPORT.md` | Rapport |

---

## 10. P5 — OS3 Evidence dry-run spec

Spec documentaire des OS3EvidenceTickets (traces d'audit théoriques).

| Fichier clé | Description |
|-------------|-------------|
| `os3_evidence_dry_run/specs/OS3_EVIDENCE_TICKET_DRY_RUN_SPEC.md` | Spec principale |
| `os3_evidence_dry_run/specs/REPLAY_HASH_SEAL_MERKLE_PLACEHOLDER_MODEL.md` | Modèle hash/Merkle placeholder |
| `os3_evidence_dry_run/reports/PLAN3_P5_OS3_EVIDENCE_DRY_RUN_SPEC_REPORT.md` | Rapport |

---

## 11. P6 — Graphiti/Brody/NPL readonly wrappers spec

Spec documentaire des wrappers readonly pour Graphiti, Brody, et NPL.

| Fichier clé | Description |
|-------------|-------------|
| `readonly_wrappers_spec/specs/READONLY_WRAPPERS_SPEC.md` | Spec principale |
| `readonly_wrappers_spec/specs/GRAPHITI_READONLY_WRAPPER_SPEC.md` | Wrapper Graphiti |
| `readonly_wrappers_spec/specs/BRODY_READONLY_WRAPPER_SPEC.md` | Wrapper Brody |
| `readonly_wrappers_spec/specs/NPL_READONLY_WRAPPER_SPEC.md` | Wrapper NPL |
| `readonly_wrappers_spec/reports/PLAN3_P6_READONLY_WRAPPERS_SPEC_REPORT.md` | Rapport |

---

## 12. P7 — Education benchmark dry-run spec

Spec documentaire du futur benchmark éducatif Obsidia.

| Fichier clé | Description |
|-------------|-------------|
| `education_benchmark_dry_run/specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md` | Spec principale |
| `education_benchmark_dry_run/scenarios/EDUCATION_BENCHMARK_SCENARIO_CATALOG.md` | 20 scénarios |
| `education_benchmark_dry_run/failure_modes/EDUCATION_BENCHMARK_FAILURE_MODES.md` | 20 failure modes |
| `education_benchmark_dry_run/metrics/EDUCATION_METRICS_CANDIDATE_SPEC.md` | 18 métriques candidates |
| `education_benchmark_dry_run/reports/PLAN3_P7_EDUCATION_BENCHMARK_DRY_RUN_SPEC_REPORT.md` | Rapport |
| `education_benchmark_dry_run/reports/PLAN3_P7_RECONCILIATION_PATCH_REPORT.md` | Patch reconciliation |

---

## 13. F78B/F78C gates

| Gate | Emplacement | Statut | Type |
|------|------------|--------|------|
| F78B | `_source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/` | READY | SOURCE_AUDIT_ONLY |
| F78C | `_source_discovery/F78C_XLSX_IMPLEMENTATION_PLAN_RECONCILIATION_20260602_133600/` | READY | XLSX_AUDIT_ONLY |

Note : F78B et F78C sont des audits readonly. Aucun zip importé. Aucun pack branché.

---

## 14. Claim-scope locks

Voir `freeze_audit/PLAN3_CLAIM_SCOPE_LOCKS.md` pour le détail complet.

Résumé :
- ❌ Ne pas dire "runtime actif"
- ❌ Ne pas dire "packs branchés"
- ❌ Ne pas dire "zips importés"
- ❌ Ne pas dire "benchmark exécuté"
- ❌ Ne pas dire "score réel"
- ✅ Dire "docs-only", "contract skeleton", "dry-run spec"
- ✅ Dire "readonly wrapper spec", "X108 remains sole passage"

---

## 15. What is allowed

```
✅ Lire les fichiers docs
✅ Proposer des modifications via gate humaine
✅ Créer de nouveaux fichiers docs dans runtime_contracts/
✅ Référencer les contrats dans d'autres specs
✅ Enrichir avec F03/F06/F07/F10 après validation
✅ Utiliser les boundaries comme référence normative
```

---

## 16. What is forbidden

```
❌ Exécuter un runtime depuis runtime_contracts/
❌ Créer des packages dans packages/
❌ Créer des fichiers .py
❌ Brancher des packs sans gate
❌ Modifier proofs/, formal/, tests/, sigma/
❌ Committer ou pousser sans validation humaine
❌ Déclarer des claims au-delà du scope docs-only
```

---

## 17. Next phases

| Ordre | Phase | Prérequis |
|-------|-------|-----------|
| 1 | PLAN3_LOCAL_FREEZE_TAG_OR_ARCHIVE_PREP | Ce freeze ✅ |
| 2 | F07 Cognitive import audit | Freeze + gate humaine |
| 3 | F03 RSSI/RGPD import audit | Freeze + DPO |
| 4 | F06 Atlas import audit | Freeze + gate humaine |
| 5 | F10 Compliance audit | F03 + Freeze |

Voir `freeze_audit/PLAN3_NEXT_PHASE_GATE.md`.

---

## 18. Freeze verdict

```
PLAN3_FREEZE_AUDIT_AND_INDEX_SYNC_READY

12/12 phases auditées = FOUND_READY
109 fichiers inventoriés + hashés
Aucun runtime actif
Aucun package créé
Aucun .py
Aucun commit
Backup guard : NO VIOLATION
```
