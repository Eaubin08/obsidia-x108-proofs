# runtime_contracts/
# PLAN 3 P0 — MAXIMAL RUNTIME CONTRACT SKELETON
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION
# Date: 2026-06-02
# Authority: KX108_ONLY

---

## 1. Objet de ce dossier

`runtime_contracts/` est l'ossature contractuelle documentaire de Plan 3 P0.
Il définit les contrats, schemas, boundaries et dry-run documentaires qui encadrent
toute future implémentation runtime dans Obsidia X-108.

Ce dossier N'est PAS un runtime. Il N'exécute RIEN.
Il n'adapte aucun module réel, ne branche aucun Graphiti, Brody, NPL ou Atlas.

---

## 2. Statut global

```
CONTRACT_SKELETON_ONLY
NO_RUNTIME_EXECUTION
KX108_ONLY
NO_ACT
NO_WORLD_ACTION
NO_TOOL_CALL
NO_MEMORY_WRITE
NO_GRAPHITI_WRITE
NO_ADAPTER_ACTIVE
DRY_RUN_ONLY (documentaire)
FAIL_CLOSED
PERIPHERY_NON_SOVEREIGN
SPEC_TO_RUNTIME_BRIDGE_ONLY
```

---

## 3. Pourquoi ce dossier existe

Plan 2 a gelé 163+ specs contractuelles dans `specs/` (compartiments 00-12).
Plan 3 P0 crée le pont entre les specs documentaires et les futurs runtimes contrôlés.

Ce pont se compose de :
- **Contrats** : définissent les structures d'échange admissibles
- **Schemas** : valident ces structures en JSON
- **Boundaries** : verrouillent les limites de chaque couche
- **Dry-run** : documentent la future chaîne d'exécution sans l'activer

---

## 4. Ce que ce dossier autorise

- Définir la structure d'un IntentEnvelope avant soumission à X-108
- Définir la structure d'un ContextPacket readonly
- Définir la structure d'un PeripheralSignalPacket non souverain
- Définir la structure du DecisionTicket (seule sortie X-108)
- Définir la structure de l'OS3EvidenceTicket (preuve + replay + seal)
- Définir les droits d'un module via BoundaryContract
- Définir les conditions d'admission SPEC_ONLY → DRY_RUN
- Documenter la chaîne dry-run sans l'exécuter

---

## 5. Ce que ce dossier interdit (absolu)

```
❌ Exécuter ACT
❌ Exécuter ALLOW / HOLD / BLOCK depuis ce dossier
❌ Créer des adapters Graphiti / Brody / NPL / Atlas / Cognitive
❌ Écrire en mémoire ou en graphe
❌ Appeler des outils ou des APIs
❌ Créer packages/
❌ Créer des fichiers .py
❌ Créer des tests exécutables
❌ Modifier periphery/, apps/, sigma/, connectors/, proofs/, formal/, tests/
❌ Committer ou pusher
❌ Prétendre qu'un contrat = un runtime
```

---

## 6. Liste des contrats

| Contrat | Rôle | Seul contrat à émettre ACT/ALLOW/HOLD/BLOCK ? |
|---------|------|----------------------------------------------|
| `IntentEnvelope.contract.md` | Intention structurée avant X-108 | NON |
| `ContextPacket.contract.md` | Contexte readonly toutes périphéries | NON |
| `PeripheralSignalPacket.contract.md` | Signal non souverain | NON |
| `DecisionTicket.contract.md` | Sortie X-108 (ALLOW/HOLD/BLOCK) | **OUI — seul** |
| `OS3EvidenceTicket.contract.md` | Preuve / trace / replay / seal | NON |
| `BoundaryContract.contract.md` | Droits d'un module | NON |
| `RuntimeAdmissionContract.contract.md` | Conditions SPEC_ONLY → DRY_RUN | NON |

---

## 7. Liste des schemas JSON

| Schema | Contrat associé |
|--------|----------------|
| `intent_envelope.schema.json` | IntentEnvelope |
| `context_packet.schema.json` | ContextPacket |
| `peripheral_signal_packet.schema.json` | PeripheralSignalPacket |
| `decision_ticket.schema.json` | DecisionTicket |
| `os3_evidence_ticket.schema.json` | OS3EvidenceTicket |
| `boundary_contract.schema.json` | BoundaryContract |
| `runtime_admission_contract.schema.json` | RuntimeAdmissionContract |

---

## 8. Liste des boundaries

| Boundary | Portée |
|----------|--------|
| `NO_ACT_FROM_PERIPHERY.md` | Toutes périphéries — jamais ACT |
| `X108_GATEWAY_REQUIRED.md` | Toute intention critique — gate obligatoire |
| `FAIL_CLOSED_PRIORITY.md` | BLOCK > HOLD > ALLOW — fail-closed universel |
| `READONLY_CONTEXT_ONLY.md` | Graphiti / Brody / NPL / Atlas / Cognitive — lecture seule |
| `EXTERNAL_SIGNALS_SIGNAL_ONLY.md` | F04 — temporal prefilter uniquement |
| `NPL_ADVISORY_ONLY.md` | NPL — hypothèse de provenance, jamais décision |
| `P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY.md` | Lyapunov/Calibration — DOC_ONLY / FUTURE_FORMAL_TARGET |
| `AUDIO_ENTROPY_ADVISORY_ONLY.md` | Audio/Entropy — métaphore architecturale candidate |
| `NO_PACKAGES_RUNTIME_BOUNDARY.md` | packages/ interdit dans ce repo |

### Boundaries spécifiques à créer en P1 (gaps identifiés)

- `COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md` → F07
- `ATLAS_READONLY_ADVISORY_ONLY.md` → F06
- `RSSI_EVIDENCE_ONLY.md` → F03
- `RGPD_COMPLIANCE_SCOPE_GUARD.md` → F03/F10

---

## 9. Dry-run documentaires

| Fichier | Rôle |
|---------|------|
| `X108_GATEWAY_DRY_RUN.md` | Chaîne complète ContextPacket → X108 → DecisionTicket (documentaire) |
| `DRY_RUN_PIPELINE.md` | Pipeline 8 étapes future |
| `NO_WORLD_ACTION_EXECUTION.md` | Verrou global dry-run ≠ action réelle |
| `DRY_RUN_FAILURE_MODES.md` | 12 failure modes → fail_closed |

---

## 10. Claim-scope global

```
Kernel X-108 (28 théorèmes) = LEAN_PROVEN — seule autorité formelle
NPL (37 métriques) = ADVISORY_ONLY — enrichissement ContextPacket uniquement
P107 Lyapunov = FUTURE_FORMAL_TARGET / DOC_ONLY — signal advisory avec label
P161 Calibration = FUTURE_FORMAL_TARGET / DOC_ONLY — signal advisory avec label
Audio/Entropy = SOURCE_PARTIAL — métaphore architecturale / candidat métrique
External Signals F04 = SIGNAL_ONLY / TEMPORAL_PREFILTER — jamais autorité
Cognitive/Atlas = COPIED_READONLY — futures boundaries en P1/F06/F07
RSSI/RGPD = COPIED_READONLY — future claim-scope guard en P1/F03
DecisionTicket = seule sortie décisionnelle admissible
X-108 = seul droit de passage pour ACT / ALLOW / HOLD / BLOCK
```

---

## 11. Invariants Lean-proven utilisés comme fondation

| Invariant | Théorème | Implication contractuelle |
|-----------|---------|--------------------------|
| D1_DETERMINISM | `D1_determinism` | La décision est déterministe — pas d'ambiguïté dans DecisionTicket |
| E2_NO_ACT | `E2_no_act_below_threshold` | Pas d'ACT sous seuil θ |
| X108_NO_ACT_BEFORE_TAU | `X108_no_act_before_tau` | Gate temporelle obligatoire pour irréversible |
| REFINEMENT.X108_NEVER_BLOCKS | `Refinement.x108_never_blocks` | Tout module périphérique est extensible sans bloquer X108 |
| FAIL_CLOSED | `aggregate4_fail_closed` | Priorité BLOCK > HOLD > ALLOW |
| MERKLE | `merkleRoot_change_if_leaf_change` | Toute trace modifiée est détectable |
| SEAL | `P13_Immutability` / `P15_Immutability_Strong` | OS3 ticket seal = immuable |
| CONSENSUS | `aggregate4_unanimous` | Consensus 4-agent nécessaire pour ALLOW critique |
| TEMPORAL_BRIDGE | `skew_negative_implies_hold` | Skew négatif → HOLD — External Signals boundary |
| AUDIT_GROWTH | `P17_AuditGrowth` | L'audit ne peut que croître — jamais supprimer trace |

---

## 12. Plan de passage futur

| Phase | Action | Prérequis |
|-------|--------|-----------|
| P1 | Packet Schema Validation + 4 boundaries manquantes | Ce dossier P0 |
| P2 | External Signals Dry-Run Adapter SPEC | P1 validé |
| P3 | X108 Gateway Dry-Run Harness | P2 validé |
| P4 | Anti-bypass tests exécutables | P3 validé |
| P5 | OS3 Evidence Ticket dry-run | P4 validé |
| P6 | Graphiti/Brody/NPL readonly wrappers | P5 validé |
| P7 | Education benchmark / Dashboards OS3 | P6 validé |
| F06 | Branchable Atlas import + ATLAS_READONLY boundary | P1 + Atlas audit |
| F07 | Cognitive Reintegration import + COGNITIVE boundary | P1 + Cognitive audit |
| F03 | RSSI + RGPD import + claim-scope guards | P1 + audits F03 |

---

## 13. Interdiction de confondre contrat et runtime

```
contrat.md  ≠  code Python
contrat.md  ≠  adapter actif
contrat.md  ≠  test exécutable
contrat.md  ≠  action monde réel
contrat.md  =  documentation contractuelle non exécutable
```

---

## 14. Rappels baseline

- Baseline freeze créé avant Plan 3 : `_backups/PLAN3_BASELINE_BEFORE_RUNTIME_CONTRACTS_20260602_091037/`
- 254 fichiers indexés avec SHA256
- Backup guard actif : tout fichier existant modifié = backup préalable obligatoire
- Aucun `packages/` créé
- Aucun fichier `.py` créé
- Aucun commit, aucun push
