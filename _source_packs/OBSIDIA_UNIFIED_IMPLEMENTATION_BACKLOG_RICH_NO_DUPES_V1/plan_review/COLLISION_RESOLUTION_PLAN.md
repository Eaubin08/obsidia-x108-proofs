# COLLISION_RESOLUTION_PLAN
# OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1

**Date :** 2026-06-02
**Mise à jour :** 2026-06-02 — Décisions D1-D4 validées par l'utilisateur
**Boundary :** `KX108_ONLY | NO_ACT | NO_RUNTIME_PATCH | SPEC_ONLY_FIRST`
**Statut :** `COLLISION_PLAN_READY_FOR_BRIDGE`

---

## 1. Résumé des collisions

| Type | Quantité | Gravité | Action principale |
|------|----------|---------|-------------------|
| Target paths dupliqués (XLSX) | 48 | FAIBLE — groupage de dossiers | Reclassification nécessaire |
| Fichiers QUARANTINE | 20 | MOYENNE — artefacts pytest | DO_NOT_IMPORT |
| Doublons internes Atlas | 92 | MOYENNE — snapshots versionnés | RAW_ARCHIVE_ONLY pour runtime_freezes |
| Doublons internes RGPD | 8 | FAIBLE — cross-pack + 1 vrai doublon | RICHER_VERSION_TO_KEEP |
| Collision avec `packages/` bloqué | 3 fichiers | HAUTE | DO_NOT_IMPORT — dossier interdit |

### Clarification critique sur les « 48 target paths dupliqués »

**Ces 48 entrées ne sont PAS 48 conflits de noms de fichiers.**

La colonne `target_location` du XLSX désigne un **dossier cible**, pas un chemin complet. Plusieurs fichiers différents qui partagent le même dossier cible font apparaître ce dossier comme « dupliqué » dans le décompte. C'est du **groupage normal** — chaque fichier a un nom distinct.

**Vrai problème restant :** parmi ces 48 dossiers cibles, **un seul est bloqué** : `packages/shared/packets/external_signals/` — car `packages/` est une interdiction absolue dans ce repo.

---

## 2. Classification des collisions

| Classe | Définition | Nb cas |
|--------|-----------|--------|
| **A. SAME_FILE_SAFE_DUPLICATE** | Même fichier pointant vers un dossier partagé — noms différents, safe | 45 sur 48 dossiers |
| **B. SAME_TARGET_DIFFERENT_SOURCE** | Même dossier, sources de packs différents — à vérifier | 0 (tous intra-pack) |
| **C. RICHER_VERSION_TO_KEEP** | Deux versions différentes — garder la plus riche | 1 (DPA_TEMPLATE.md) + runtime_freeze Atlas |
| **D. LEGACY_SOURCE_ONLY** | Version ancienne à garder comme archive uniquement | RSSI V1 dans RGPD pack |
| **E. QUARANTINE_DO_NOT_IMPORT** | Artefacts techniques à ne jamais importer | 20 fichiers pytest_cache |
| **F. HUMAN_REVIEW_REQUIRED** | Décision impossible sans lecture du contenu | 3 fichiers packets/ dans packages/ |

---

## 3. Analyse des 48 target paths dupliqués

### Groupe 1 — `docs/source_packs/external_signals/`
| Source | Fichier | Action | Classe |
|--------|---------|--------|--------|
| External Signals | `MERGE_INSTRUCTIONS.md` | IMPORT_DOC_AS_SPEC | A |
| External Signals | `README.md` | IMPORT_DOC_AS_SPEC | A |
| External Signals | `SHA256SUMS.txt` | KEEP_AS_EVIDENCE | A |
| External Signals | `VALIDATION_REPORT.yaml` | KEEP_AS_EVIDENCE | A |

**Décision :** SAFE — 4 fichiers distincts dans un même dossier. Aucun conflit de nom.
**Risque :** aucun
**Revue humaine :** false

---

### Groupe 2 — `specs/external_signals/component_specs/`
24 fichiers YAML (C459 à C482) — spécifications de composants temporels

| Exemple | Fichier | Action |
|---------|---------|--------|
| C459 | `C459_timeverse_temporal_sidecar.yaml` | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED |
| C460 | `C460_temporal_context_header.yaml` | idem |
| … | … (C461 → C482) | idem |

**Décision :** SAFE — 24 fichiers distinctement nommés. Dossier `specs/external_signals/` n'existe pas encore dans le repo (Plan 2 a créé `specs/12_NARRATIVE_PROVENANCE_LAYER/` etc., mais pas `specs/external_signals/`).
**Risque :** aucun conflit — nouveau dossier
**Revue humaine :** false
**Note :** Ces specs doivent passer par `REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED` — ne PAS créer les adapters Python avant d'avoir la spec contractuelle validée.

---

### Groupe 3 — `specs/external_signals/family_specs/`
3 fichiers YAML (family_specs 46, 47, 48)

**Décision :** SAFE — 3 fichiers distincts, nouveau dossier.
**Risque :** `47_timeverse_temporal_sidecar.spec.yaml` pèse 37KB — fichier dense à relire avant import.
**Revue humaine :** false (mais lire avant import)

---

### Groupe 4 — `registry/appendices/external_signals/`
5 fichiers CSV/YAML/MD de merge

| Fichier | Type | Taille |
|---------|------|--------|
| `06_COMPONENT_INDEX_APPEND.csv` | CSV | 5.5 KB |
| `07_COMPONENT_SPEC_MATRIX_APPEND.csv` | CSV | 53 KB |
| `08_METRIC_DICTIONARY_APPEND.yaml` | YAML | 12 KB |
| `09_FORMULA_DICTIONARY_APPEND.md` | MD | 1 KB |
| `10_INVARIANTS_APPEND.md` | MD | <1 KB |

**Décision :** SAFE — dossier `registry/appendices/` n'existe pas dans le repo.
**Risque :** Le fichier CSV 53KB peut introduire des noms de composants non validés — relire avant merge.
**Revue humaine :** true pour 07_COMPONENT_SPEC_MATRIX_APPEND.csv (volume + contenu)

---

### Groupe 5 — `packages/shared/packets/external_signals/` ← BLOQUÉ
3 fichiers packets YAML

| Fichier | Action XLSX |
|---------|-------------|
| `51_temporal_context_header.packet.yaml` | IMPORT_CONTRACT_SCHEMA_PACKET |
| `52_temporal_receipt.packet.yaml` | IMPORT_CONTRACT_SCHEMA_PACKET |
| `53_consequence_boundary.packet.yaml` | IMPORT_CONTRACT_SCHEMA_PACKET |

**Décision :** DO_NOT_IMPORT dans `packages/` — **dossier interdit** dans ce repo.
**Raison :** `packages/` a été rollbacké et interdit lors du chantier précédent. La création de ce dossier n'est pas autorisée sans décision explicite.
**Action alternative :** Importer ces packets dans `specs/external_signals/packets/` à la place (même contenu, chemin différent).
**Classe :** F — HUMAN_REVIEW_REQUIRED pour décider du chemin de remplacement
**Revue humaine :** **true — décision sur packages/ requise**

---

### Groupes 6-48 — Autres dossiers cibles

Après analyse exhaustive du XLSX, les 43 autres entrées sont de classe A (SAME_FILE_SAFE_DUPLICATE) :
- Chaque dossier contient 2 à N fichiers aux noms distincts
- Aucun conflit de nom de fichier détecté
- Tous les dossiers cibles sont nouveaux (non présents dans le repo)

Exemples représentatifs :

| Target folder | Pack | Nb fichiers | Classe | Action |
|---------------|------|-------------|--------|--------|
| `docs/source_packs/rssi_security/` | RSSI Security | 8 | A | SAFE_NEW |
| `specs/rssi_security/` | RSSI Security | 12+ | A | SAFE_NEW |
| `docs/source_packs/rgpd_iso/` | RGPD ISO | 15+ | A | SAFE_NEW |
| `specs/compliance/` | RGPD ISO | 20+ | A | SAFE_NEW |
| `docs/source_packs/atlas/` | Atlas | 50+ | A | SAFE_NEW — lire QUARANTINE en premier |
| `docs/source_packs/cognitive/` | Cognitive | 30+ | A | SAFE_NEW |
| `specs/cognition/` | Cognitive | 50+ | A | SAFE_NEW |

---

## 4. Fichiers QUARANTINE (20 fichiers)

**Tous issus d'Atlas — dossier `.pytest_cache/`**

| # | Chemin source | Type | Raison quarantaine | Décision |
|---|---------------|------|---------------------|----------|
| 1 | `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_5_DEEP_FINAL_AUDIT/.pytest_cache/.gitignore` | gitignore | Artefact pytest — hors contenu atlas | DO_NOT_IMPORT |
| 2 | `.../.pytest_cache/CACHEDIR.TAG` | tag | Artefact pytest — marqueur cache | DO_NOT_IMPORT |
| 3 | `.../.pytest_cache/README.md` | md | README du cache pytest — pas du contenu atlas | DO_NOT_IMPORT |
| 4 | `.../.pytest_cache/v/cache/lastfailed` | binaire | Cache résultats tests — volatile | DO_NOT_IMPORT |
| 5 | `.../.pytest_cache/v/cache/nodeids` | binaire | Cache node IDs pytest — volatile | DO_NOT_IMPORT |
| 6-20 | Autres artefacts `.pytest_cache/v/` | mixte | Même famille — artefacts de test | DO_NOT_IMPORT |

**Analyse :**
Ces 20 fichiers proviennent du dossier `.pytest_cache/` d'une version antérieure de l'Atlas (`V0_5`). Ils ont été inclus par erreur dans le zip (git clean -X non appliqué avant packaging). Ils ne contiennent aucune logique Obsidia.

**Stratégie :**
```
QUARANTINE_DO_NOT_IMPLEMENT → DO_NOT_IMPORT
Raison : artefacts pytest volatils — aucune valeur de spec ou d'évidence
Action Plan 3 : NONE — ignorer définitivement
DELETE_FROM_PLAN_NOT_FROM_SOURCE
```

**Risque si importés :** Confusion des tests réels avec des caches tests — risk LOW mais pollution garantie.

---

## 5. Atlas — 92 doublons internes

### Nature des 92 doublons

Après analyse : les 92 doublons appartiennent à **2 familles distinctes**.

#### Famille A — Runtime freeze snapshots (versions multiples)
Les fichiers apparaissent dans plusieurs dossiers `.runtime_freezes/` :
- `WORLD_PROTOCOL_ATLAS_V0/` — version initiale
- `WORLD_PROTOCOL_ATLAS_FULL_V0/` — version complète
- `WORLD_PROTOCOL_ATLAS_FULL_V0_1_EXHAUSTIVE/` — version exhaustive

Fichiers concernés (non exhaustif) :
- `MANIFEST_SHA256.json` (3 copies, tailles différentes)
- `context_packets_snapshot.json` (2 copies, ~140KB chacune)
- `graphiti_nodes_snapshot.json` (2 copies, ~1MB chacune)
- `registry_snapshot.json` (2 copies, ~443KB)
- `scenario_candidates_snapshot.json` (2 copies, ~286KB)
- `audit_report.json` (2 copies, ~5KB)

**Classification :** `D. LEGACY_SOURCE_ONLY`
**Raison :** Ce sont des snapshots de versions successives du même Atlas. La version la plus récente (`WORLD_PROTOCOL_ATLAS_FULL_V0_1_EXHAUSTIVE`) est probablement la plus complète.
**Stratégie :**
```
NE PAS importer les runtime_freezes dans le repo runtime.
Conserver dans raw/ comme archive seulement.
Import recommandé : V0_1_EXHAUSTIVE uniquement si import décidé.
```
**Risque :** Si les deux versions sont importées, les registries peuvent se contredire.
**Revue humaine :** true pour décider quelle version est canonique

#### Famille B — Extraction croisée docs/ vs .runtime_freezes/
```
ALL_TABLES_RAW.json          : .runtime_freezes/V0_1_EXHAUSTIVE vs docs/full_doc_extraction
AUTO_AGENT_CANDIDATES_RAW.json : idem
AUTO_CARDS_CANDIDATES.json   : idem
```
Ces fichiers apparaissent dans deux contextes différents : une copie dans le freeze, une dans docs/. Les tailles sont légèrement différentes (extraction à des moments différents).

**Classification :** `C. RICHER_VERSION_TO_KEEP`
**Stratégie :** Garder `docs/full_doc_extraction/` (chemin docs — plus stable) comme source d'import. Ignorer `.runtime_freezes/` pour ces fichiers.

### Stratégie globale Atlas

```
REGISTRY_FIRST — ne pas importer le zip en masse
IMPORT_SEQUENCE :
  1. Importer uniquement les registres et schemas (docs/registries/, specs/, packets/)
  2. Garder les snapshots .runtime_freezes/ comme RAW_ARCHIVE_ONLY
  3. Ne jamais décompresser les .runtime_freezes/ dans le repo runtime
  4. Résoudre version V0 vs V0_1_EXHAUSTIVE avant tout import de snapshot
```

---

## 6. RGPD ISO — 8 doublons internes

### Nature des 8 doublons

Deux familles :

#### Famille A — Runtime freeze cross-pack (7 fichiers)
Le pack RGPD V2 contient les runtime_freezes du pack RSSI Security V1 **et** ses propres freezes.

```
.runtime_freezes/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1/  ← RSSI V1 freeze (inclus par dépendance)
.runtime_freezes/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2/     ← RGPD V2 freeze propre
```

Fichiers concernés :
- `rssi_file_registry_snapshot.json` : RSSI V1 = 409KB vs RGPD V2 = 5.5KB → **versions TRÈS différentes**
- `rssi_control_registry_snapshot.json` : 89KB vs 5.6KB
- `rssi_risk_registry_snapshot.json` : 51KB vs 5.5KB
- `rssi_security_case_snapshot.json` : 51KB vs 5.5KB
- `rssi_evidence_snapshot.json` : 47KB vs 5.5KB
- `rssi_audit_report_snapshot.json` : 10KB vs 5.5KB

**Analyse :** Les versions RGPD V2 à 5.5KB sont des **stubs de démarrage** — le pack RSSI V1 contient les données complètes. La différence de taille est significative.

**Classification :** `D. LEGACY_SOURCE_ONLY` pour RGPD V2 stubs
**Stratégie :**
```
GARDER : .runtime_freezes/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1/ (données complètes)
IGNORER : .runtime_freezes/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2/ pour ces 6 fichiers (stubs)
NE PAS importer les runtime_freezes dans le repo runtime
```
**Risque :** Importer les stubs de 5.5KB en pensant avoir les données complètes — diagnostic faux.
**Revue humaine :** false (règle claire : garder la plus grande)

#### Famille B — DPA_TEMPLATE.md (1 fichier)
```
rgpd/DPA_TEMPLATE.md   (6928 bytes)
legal/DPA_TEMPLATE.md  (6969 bytes)
```
Deux versions légèrement différentes du même template DPA.

**Analyse :** Le template `legal/` est marginalement plus grand (+41 bytes). Les deux sont des documents RGPD légitimes.

**Classification :** `C. RICHER_VERSION_TO_KEEP`
**Stratégie :**
```
GARDER : legal/DPA_TEMPLATE.md (6969 bytes — légèrement plus complet)
SOURCE_ONLY : rgpd/DPA_TEMPLATE.md → archiver dans raw seulement
```
**Risque :** Importer les deux risque d'avoir deux versions contradictoires du DPA.
**Revue humaine :** true — lire les 41 bytes de différence avant de décider

### Stratégie globale RGPD

```
IMPORT_V2_COMPLIANCE_EXTENSION :
  1. Ne PAS écraser les registres RSSI V1 avec les stubs RGPD V2
  2. Importer uniquement le contenu RGPD propre (hors .runtime_freezes/)
  3. DPA_TEMPLATE : garder legal/ — archiver rgpd/ comme SOURCE_ONLY
  4. MANIFEST_SHA256.json : garder V2 freeze (freeze le plus récent)
```

---

## 7. Tableau de résolution — actions par collision

| # | Type | Élément | Classification | Action | Risque | Revue humaine |
|---|------|---------|---------------|--------|--------|---------------|
| 1 | Target dup | `docs/source_packs/external_signals/` (4 fichiers) | A | SAFE_NEW_SOURCE | aucun | false |
| 2 | Target dup | `specs/external_signals/component_specs/` (24 specs C459-C482) | A | SAFE_NEW_SOURCE — REGISTER_SPEC_FIRST | spec avant adapter | false |
| 3 | Target dup | `specs/external_signals/family_specs/` (3 specs) | A | SAFE_NEW_SOURCE | lire 47_timeverse (37KB) | false |
| 4 | Target dup | `registry/appendices/external_signals/` (5 fichiers) | A | SAFE_NEW_SOURCE | CSV 53KB à valider | true (CSV volume) |
| 5 | **Target dup** | **`packages/shared/packets/external_signals/`** | **F** | **DO_NOT_IMPORT dans packages/ — rediriger vers specs/** | **HAUTE — packages/ interdit** | **true** |
| 6-48 | Target dup | Autres dossiers cibles (43 groupes) | A | SAFE_NEW_SOURCE | aucun | false |
| Q1-Q20 | Quarantine | `.pytest_cache/` (20 fichiers Atlas) | E | DO_NOT_IMPORT — DELETE_FROM_PLAN | pollution tests | false |
| A1-A75 | Atlas dup | Runtime freeze snapshots V0 vs V0_1 | D | RAW_ARCHIVE_ONLY — ne pas importer dans runtime | versions contradictoires | true |
| A76-A92 | Atlas dup | docs/full_doc_extraction vs .runtime_freezes | C | Garder docs/ — ignorer .runtime_freezes/ | taille différente | false |
| R1-R6 | RGPD dup | Runtime freeze RSSI V1 stubs (6 fichiers) | D | Garder RSSI V1 (plus grand) — ignorer RGPD V2 stubs | diagnostic faux | false |
| R7 | RGPD dup | DPA_TEMPLATE.md (rgpd/ vs legal/) | C | Garder legal/ (6969 bytes) — archiver rgpd/ | version contradictoire | true |
| R8 | RGPD dup | MANIFEST_SHA256.json (V1 vs V2) | C | Garder V2 (le plus récent) | aucun | false |

---

## 8. Décisions D1-D4 — Validées par l'utilisateur (2026-06-02)

### D1 — `packages/shared/packets/external_signals/` ✅ VALIDÉ

**Décision :** Rediriger les 3 fichiers packets YAML vers `specs/external_signals/packets/`.
Aucun dossier `packages/` ne doit être créé.

| Champ | Valeur |
|-------|--------|
| Statut | `SPEC_ONLY_PACKET_CONTRACT` |
| Chemin original XLSX | `packages/shared/packets/external_signals/` |
| Chemin corrigé | `specs/external_signals/packets/` |
| Fichiers concernés | `51_temporal_context_header.packet.yaml`, `52_temporal_receipt.packet.yaml`, `53_consequence_boundary.packet.yaml` |
| Action | `IMPORT_CONTRACT_SCHEMA_PACKET` dans `specs/` uniquement |
| Invariant | `packages/` reste ABSENT — interdit dans ce repo |

---

### D2 — Atlas — version canonique ✅ VALIDÉ

**Décision :** Atlas V0_1_EXHAUSTIVE = source canon documentaire. V0 = LEGACY_ARCHIVE_ONLY. Aucun import runtime Atlas.

| Champ | Valeur |
|-------|--------|
| Version canon | `WORLD_PROTOCOL_ATLAS_FULL_V0_1_EXHAUSTIVE` |
| Version legacy | `WORLD_PROTOCOL_ATLAS_FULL_V0` et `WORLD_PROTOCOL_ATLAS_V0` → `LEGACY_ARCHIVE_ONLY` |
| Import runtime | INTERDIT — `NO_RUNTIME_IMPORT` |
| Snapshots V0 | `RAW_ARCHIVE_ONLY` dans `_source_packs/raw/` — ne pas décompresser dans repo |
| Snapshots V0_1 | `RAW_ARCHIVE_ONLY` idem — import docs/ uniquement si décidé en Plan 3+ |

---

### D3 — DPA_TEMPLATE.md ✅ VALIDÉ

**Décision :** `legal/DPA_TEMPLATE.md` (6969 bytes) = canon principal. `rgpd/DPA_TEMPLATE.md` (6928 bytes) = référence secondaire. Ne pas écraser sans diff.

| Champ | Valeur |
|-------|--------|
| Canon | `legal/DPA_TEMPLATE.md` → statut `CANONICAL_DPA` |
| Secondaire | `rgpd/DPA_TEMPLATE.md` → statut `SECONDARY_RGPD_REFERENCE` |
| Règle d'import | Ne jamais écraser `legal/` par `rgpd/` sans diff préalable |
| Risque résiduel | 41 bytes de différence non analysés — diff humain requis si modification future |

---

### D4 — `07_COMPONENT_SPEC_MATRIX_APPEND.csv` ✅ VALIDÉ

**Décision :** Ne pas merger maintenant. Garder en `SOURCE_REGISTRY_APPEND_PENDING_REVIEW`. Aucun merge registry automatique.

| Champ | Valeur |
|-------|--------|
| Statut | `SOURCE_REGISTRY_APPEND_PENDING_REVIEW` |
| Action Plan 2 | NONE — garder dans `_source_packs/raw/` uniquement |
| Action Plan 3 | Lire + valider contenu avant tout merge dans registry/ |
| Raison | Volume 53KB — vérification humaine des paths cibles avant merge |

---

### Actions non bloquantes — résolues

| Action | Résolution |
|--------|-----------|
| 20 fichiers pytest_cache | DO_NOT_IMPORT — définitivement ignorés |
| RSSI V1 stubs dans RGPD V2 | Garder les grandes versions RSSI V1 — ignorer stubs V2 |
| Atlas docs/ vs .runtime_freezes/ extraction | Garder docs/full_doc_extraction/ — ignorer .runtime_freezes/ |
| 45 groupes SAFE_NEW_SOURCE | Import possible en suivant F04 → F03 → F06 → F07 |

---

## 9. Arbo cible corrigée (après résolution)

```
docs/source_packs/
├── external_signals/          ← 4 docs (SAFE — F04)
├── rssi_security/             ← 167 fichiers RSSI Security (F03)
└── rgpd_iso/                  ← 280 fichiers RGPD V2, hors stubs (F03/F10)

specs/
├── external_signals/
│   ├── component_specs/       ← C459-C482 (24 specs YAML)
│   ├── family_specs/          ← 3 family specs
│   └── packets/               ← 3 packets YAML [REDIRIGÉ depuis packages/]
├── compliance/                ← RGPD ISO specs
└── (autres domaines Plan 2 existants)

registry/appendices/
└── external_signals/          ← 5 fichiers de merge (CSV/YAML)

[BLOCKED] packages/            ← NE PAS CRÉER sans décision explicite
```

---

## 10. Verdict

```
COLLISION_PLAN_READY_FOR_BRIDGE
```

**Justification :**

- 45/48 groupes de target paths → SAFE_NEW_SOURCE — aucun conflit réel
- 20 QUARANTINE → résolus (DO_NOT_IMPORT — pytest_cache)
- 92 Atlas dups → résolus (V0_1_EXHAUSTIVE = canon, V0 = LEGACY_ARCHIVE_ONLY, aucun import runtime)
- 8 RGPD dups → résolus (RSSI V1 > stubs V2, legal/DPA = canon, rgpd/DPA = secondaire)
- **D1 :** `packages/` → `specs/external_signals/packets/` — SPEC_ONLY_PACKET_CONTRACT ✅
- **D2 :** Atlas V0_1_EXHAUSTIVE = canon documentaire ✅
- **D3 :** legal/DPA_TEMPLATE = canon principal, rgpd/ = SECONDARY_RGPD_REFERENCE ✅
- **D4 :** 07_COMPONENT_SPEC_MATRIX_APPEND.csv → SOURCE_REGISTRY_APPEND_PENDING_REVIEW ✅

**Toutes les décisions bloquantes sont levées.**
**Aucun runtime patché. Aucun packages/ créé. Aucun commit.**

---

## 11. Prochaine étape — Bridge vers F04 External Signals

D1-D4 étant tranchées, la voie est libre pour :

**→ F04 External Signals** — premier import effectif

Import recommandé dans cet ordre :
1. `docs/source_packs/external_signals/` — 4 docs de présentation
2. `specs/external_signals/component_specs/` — 24 specs C459-C482 (REGISTER_SPEC_FIRST)
3. `specs/external_signals/family_specs/` — 3 specs famille
4. **`specs/external_signals/packets/`** — 3 packets YAML *(chemin D1 corrigé)*
5. `registry/appendices/external_signals/` — 4 fichiers (hors CSV D4 pending)

**Ce qui reste bloqué :**
- `packages/` → ABSENT — interdit
- `07_COMPONENT_SPEC_MATRIX_APPEND.csv` → SOURCE_REGISTRY_APPEND_PENDING_REVIEW
- Atlas runtime_freezes → RAW_ARCHIVE_ONLY
- Tout import runtime → NO_RUNTIME_PATCH

**Plan 3 runtime contracts skeleton :**
→ Peut démarrer après F04 External Signals importé et specs validées.

### Commande de vérification

```bash
git status --short | grep -v "^?? _source_discovery\|^?? specs\|^?? _source_packs"
# (vide = CLEAN)
test -d packages && echo "VIOLATION" || echo "packages ABSENT OK"
```
