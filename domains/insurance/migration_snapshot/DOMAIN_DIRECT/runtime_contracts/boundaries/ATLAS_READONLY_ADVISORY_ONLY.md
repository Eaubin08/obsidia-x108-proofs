# ATLAS_READONLY_ADVISORY_ONLY
# runtime_contracts/boundaries/ATLAS_READONLY_ADVISORY_ONLY.md
# Plan 3 P1 — Gap reporté depuis P0
# Status: CONTRACT_SKELETON_ONLY
# Source: _source_packs/.../raw/OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip
# Pack status: COPIED_READONLY — 1738 fichiers — 92 doublons internes — NON importé dans specs/ — à traiter en F06

---

## 1. Boundary Statement

```
Branchable Atlas = TERRITOIRE / CARTE / CONTEXTE / SCÉNARIO CANDIDAT
∀ entité atlas e : e ↛ ACT
∀ entité atlas e : e ↛ ALLOW / HOLD / BLOCK
∀ entité atlas e : e ↛ exécution directe
∀ agent atlas a : a ↛ agent exécutable directement
scenario_candidate ↛ action directe
full_doc_extraction ≠ runtime installé
open_source_project_card ≠ dépendance installée
external_actor_card ≠ information fraîche sans refresh
runtime_freeze/ → archivé seulement (92 doublons = snapshots versionnés)
∀ output atlas : output ∈ {ContextPacket}
decision_authority = KX108_ONLY
```

---

## 2. Applies To

Pack : `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` (1738 fichiers, ~36MB)

Contenu du pack :
- World/protocol atlas (territoires conceptuels)
- Branchable contexts (contextes branchables sur demande)
- Graphiti-ready content (contenu prêt pour Graphiti readonly)
- Open source project cards (fiches projets open-source)
- External actor cards (fiches acteurs externes)
- Scenario candidates (scénarios candidats)
- Full doc extraction (extraction documentaire complète)
- runtime_freezes/ (92 doublons — snapshots versionnés — ARCHIVE ONLY)

Contraintes spécifiques :
- 92 doublons internes → résolution avant import : runtime_freezes/ = RAW_ARCHIVE_ONLY
- 20 fichiers QUARANTINE identifiés (doublons artefacts) → DO_NOT_IMPORT
- Volume massif (36MB) → import partiel par priorité recommandé

---

## 3. Source Status

| Élément | Statut |
|---------|--------|
| Zip dans repo | ✅ `_source_packs/.../raw/` |
| Filelist extraite | ✅ `extracted_file_lists/` |
| Importé dans specs/ | ❌ NON — à traiter en F06 |
| 92 doublons résolus | ❌ EN ATTENTE — runtime_freeze = ARCHIVE_ONLY |
| Audité session | ✅ backlog audit + PLAN3_P0_INPUT_COVERAGE |
| Boundary dédiée P0 | ❌ NON — couvert par générique READONLY_CONTEXT_ONLY |
| Boundary dédiée P1 | ✅ CE FICHIER |
| Runtime branché | ❌ NON |
| Source status global | `COPIED_READONLY` |

---

## 4. Allowed

- Produire un ContextPacket avec `source_layer="atlas"`, `advisory_only=true`, `label="ATLAS_READONLY_FUTURE"`
- Fournir des cartes de territoire, de contexte, ou de scénario comme données de lecture
- Alimenter Graphiti en mode readonly avec du contenu Atlas (futur F06 — gate requise)
- Décrire des scenario_candidates comme candidats d'action dans un ContextPacket
- Référencer des fiches open-source ou acteurs externes comme contexte documentaire (avec note de fraîcheur)
- Permettre l'import futur du pack (partiellement) en `specs/atlas/` après résolution doublons et audit F06

---

## 5. Forbidden

```
❌ "Atlas est branché runtime" — COPIED_READONLY uniquement
❌ "Atlas sait décider" — jamais souverain
❌ "Les agents Atlas sont exécutables" — scenario_candidate ≠ action exécutée
❌ "Les projets open-source sont installés" — project_card ≠ dépendance active
❌ "Les acteurs externes sont à jour sans refresh"
❌ Les entités Atlas produisent ALLOW / HOLD / BLOCK
❌ Les entités Atlas produisent ACT
❌ Importer runtime_freeze/ dans specs/ (doublons snapshots — ARCHIVE_ONLY)
❌ Importer les 20 fichiers QUARANTINE
❌ Importer le pack sans résolution des 92 doublons
❌ Écrire dans Graphiti depuis Atlas sans gate humain + DecisionTicket
```

---

## 6. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| Entité Atlas émet `emits_act=true` | PLAN3_P1_BACKUP_GUARD_VIOLATION → fail_closed |
| `scenario_candidate` déclenche action directe | Reject → fail_closed |
| `open_source_card` présentée comme dépendance installée | `overauthority_flag` |
| `external_actor_card` sans date de fraîcheur | `staleness_risk_flag` |
| Label `ATLAS_READONLY_FUTURE` manquant | `label_missing_flag` |
| Import runtime_freeze/ sans résolution doublons | Reject — COLLISION_RESOLUTION_PLAN |

---

## 7. Required Contract Fields

- `source_layer: "atlas"` dans ContextPacket si source = Atlas
- `label: "ATLAS_READONLY_FUTURE"` obligatoire sur tout output Atlas
- `advisory_only: true` + `emits_act: false` + `decision_authority: "KX108_ONLY"`
- `source_status: "COPIED_READONLY"` jusqu'à import F06

---

## 8. Required Future Tests (F06 / P2 après import)

- `test_atlas_no_decision_authority`
- `test_atlas_scenario_candidate_requires_intent_envelope`
- `test_atlas_graphiti_write_requires_gate`
- `test_atlas_external_actor_card_staleness_flagged`
- `test_atlas_runtime_freeze_not_imported`

---

## 9. Proof Expectation

- Aucune preuve Lean pour Atlas actuellement
- Python tests après import partiel F06
- `Refinement.x108_never_blocks` : Atlas extensible sans casser X-108

---

## 10. Claim-Scope

**Autorisé :**
- "Branchable Atlas est un pack copied-readonly en attente d'import F06"
- "Atlas fournit du contexte cartographique advisory — jamais des décisions"
- "scenario_candidate = candidat d'action soumis à X-108 via IntentEnvelope"
- "open_source_cards = fiches documentaires — pas des dépendances installées"
- "Les 92 doublons runtime_freeze sont des snapshots archivés — pas du runtime"

**Interdit :**
- ❌ "Atlas est branché runtime" — COPIED_READONLY
- ❌ "Les agents Atlas sont exécutables" — INTERDIT
- ❌ "Les projets open-source sont installés" — INTERDIT
- ❌ "Les acteurs externes sont à jour" — fraîcheur non garantie
- ❌ "Atlas décide" — INTERDIT

---

## 11. Example Violation

```python
# VIOLATION
atlas_agent.execute_scenario("world_correction")  # ← scenario_candidate ≠ action directe
```

---

## 12. Correct Handling

```python
# CORRECT
atlas_context = atlas.get_scenario_card("world_correction")
packet = ContextPacket(
    source_layer="atlas",
    advisory_only=True, emits_act=False,
    labels=["ATLAS_READONLY_FUTURE"],
    context_payload={
        "scenario_candidate": "world_correction",
        "scenario_confidence": 0.74,
        "_atlas_can_execute": False
    }
)
# → X108 reçoit le scénario comme contexte et décide
```

---

## 13. Future Runtime Admission Conditions (F06)

Avant de passer Atlas en `CONTRACT_READY` :
1. Résolution des 92 doublons internes (runtime_freezes → ARCHIVE_ONLY)
2. Identification et exclusion des fichiers QUARANTINE
3. Import partiel en `specs/atlas/` (par priorité — volume 36MB → import sélectif)
4. Audit claim-scope des external_actor_cards (fraîcheur + source vérification)
5. Tests : `test_atlas_no_decision_authority`
6. Gate humaine pour tout import Graphiti-ready content

---

## 14. Relation To X-108

```
Atlas → ContextPacket (advisory) → X108 → DecisionTicket
scenario_candidate → IntentEnvelope → X108 → DecisionTicket ALLOW (si applicable)
runtime_freeze/ → ARCHIVE_ONLY → jamais vers specs/ ou runtime_contracts/
```

Volume : 1738 fichiers à 36MB → import partiel et sélectif recommandé (COLLISION_RESOLUTION_PLAN.md).
