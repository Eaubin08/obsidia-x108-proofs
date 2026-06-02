# F78B_COLLISION_AND_DUPLICATE_REPORT
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## Résumé

| Type collision | Nb | Gravité | Action |
|---------------|-----|---------|--------|
| RSSI_EXT vs specs/external_signals (déjà importés) | 37 | LOW — désiré | NO_ACTION (déjà fait F04) |
| README.md collision (triviale) | 3 | TRIVIAL | NO_ACTION |
| Atlas .pytest_cache artefacts | 20+ entrées | HAUTE | QUARANTINE_DO_NOT_IMPORT |
| Atlas .runtime_freezes snapshots | Inclus dans 92 dups | MOYENNE | RAW_ARCHIVE_ONLY |
| Atlas 92 dups basenames | 92 | MOYENNE | Snapshots versionnés — RAW_ARCHIVE_ONLY |
| RGPD 8 dups basenames | 8 | FAIBLE | Garder version plus riche |
| packages/ collision XLSX | 3 fichiers | HAUTE | DO_NOT_IMPORT_ABSOLUTE |
| .py dans zips (RSSI/RGPD/Atlas) | 57 fichiers .py | CRITIQUE | DO_NOT_IMPORT_RUNTIME |

---

## Détail par type

### 1. RSSI_EXT — 37 collisions avec specs/external_signals/

**Nature :** Collisions DÉSIRÉES — ces fichiers ont été importés en F04.
Le zip contient exactement les mêmes fichiers qui sont maintenant dans `specs/external_signals/`.

**Action :** NO_REIMPORT. VALIDATION recommandée : comparer hash locaux vs zip.

Fichiers concernés (exemples) :
```
C459_timeverse_temporal_sidecar.yaml  → specs/external_signals/component_specs/
C466_temporal_receipt_metadata.yaml   → specs/external_signals/component_specs/
51_temporal_context_header.packet.yaml → specs/external_signals/packets/
52_temporal_receipt.packet.yaml        → specs/external_signals/packets/
53_consequence_boundary.packet.yaml    → specs/external_signals/packets/
48_consequence_boundary_enrichment.spec.yaml → specs/external_signals/family_specs/
```

---

### 2. README.md — collisions triviales (3 packs)

**Atlas, RSSI_SEC, RSSI_RGPD** ont chacun un `README.md` dans leur zip.
`specs/` contient aussi des `README.md`.
**Gravité : TRIVIAL** — les README sont distincts par contenu et contexte.
**Action :** RENAME lors de l'import (ajouter prefix du pack).

---

### 3. .pytest_cache — Atlas

**Chemin :** `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_5_DEEP_FINAL_AUDIT/.pytest_cache/`
**Nature :** Artefacts de tests Python — ne pas importer dans le repo.
**Action : QUARANTINE_DO_NOT_IMPORT**

```
Fichiers .pytest_cache identifiés :
  .pytest_cache/README.txt
  .pytest_cache/v/cache/lastfailed
  .pytest_cache/v/cache/nodeids
  .pytest_cache/v/cache/stepwise
  + autres artefacts pytest
```

---

### 4. Atlas .runtime_freezes — 92 doublons

**Nature :** Snapshots de runtime figés à différents points de version.
Ces fichiers documentent l'état de l'atlas à V0_3, V0_5, V0_6, V0_7.

**Doublons principaux :**
```
README.md               — dans chaque sous-dossier de version
MANIFEST_SHA256.json    — dans chaque version
audit_report.json       — dans chaque version
context_packets_snapshot.json  — dans chaque version
graphiti_nodes_snapshot.json   — dans chaque version
```

**Action :** `RAW_ARCHIVE_ONLY` pour `.runtime_freezes/` complet.
Pour les fichiers MD/JSON d'audit hors `.runtime_freezes/` : éligibles INTEGRATE_DOCS.

---

### 5. RGPD 8 doublons basenames

**Fichiers :**
```
MANIFEST_SHA256.json              — versions légèrement différentes dans sous-dossiers
rssi_file_registry_snapshot.json  — snapshots versionnés
rssi_control_registry_snapshot.json
rssi_risk_registry_snapshot.json
rssi_security_case_snapshot.json
rssi_file_registry_snapshot.json  (x2)
rssi_control_registry_snapshot.json (x2)
rssi_risk_registry_snapshot.json (x2)
```

**Action :** Pour chaque doublon, garder la version la plus récente/riche.
Identifier par contenu lors de F03. `RICHER_VERSION_TO_KEEP` (COLLISION_RESOLUTION_PLAN D3).

---

### 6. packages/ collision XLSX (3 fichiers)

**Selon COLLISION_RESOLUTION_PLAN :**
3 fichiers dans le XLSX ciblent `packages/shared/packets/external_signals/`.
`packages/` est une interdiction absolue dans ce repo.

**Action : DO_NOT_IMPORT_ABSOLUTE**
```
packages/shared/packets/external_signals/ → INTERDIT
Alternative : import dans specs/external_signals/packets/ (déjà fait F04)
```

---

### 7. .py dans zips — 57 fichiers Python — CRITIQUE

**Localisation :**
```
RSSI_SECURITY :  16 .py dans periphery/rssi_security_pack/
RSSI_RGPD    :  23 .py dans periphery/rssi_security_pack/
ATLAS        :  18 .py dans periphery/world_protocol_atlas/ + patches/
TOTAL        :  57 fichiers .py
```

**Risque :** Si ces .py sont importés dans le repo racine, ils créeraient un
adapter Python actif en violation de la boundary NO_PACKAGES_RUNTIME_BOUNDARY
et de l'interdiction absolue de créer des fichiers .py runtime en Plan 3.

**Action lors de F03/F06 :**
```
Import = DOCS_ONLY
Exclusions obligatoires :
  periphery/**/*.py    → DO_NOT_IMPORT
  patches/**/*.py      → DO_NOT_IMPORT
  .pytest_cache/       → QUARANTINE
  __pycache__/         → QUARANTINE
  .runtime_freezes/    → RAW_ARCHIVE_ONLY
```

---

## DPA_TEMPLATE.md — RICHER_VERSION_TO_KEEP

Selon COLLISION_RESOLUTION_PLAN D3 :
`DPA_TEMPLATE.md` existe en deux versions entre packs RSSI et RGPD.
**Action :** Lors de F03, comparer les deux versions et garder la plus riche.

---

## Recommandation globale

```
Avant F03 : résoudre les 8 dups RGPD + exclure periphery/.py + exclure .pytest_cache
Avant F06 : exclure periphery/.py + .runtime_freezes + .pytest_cache d'Atlas
Avant F07 : Cognitive est propre — import direct possible après F78B
F07 = cas le plus simple : 0 .py, 0 dups, structure claire
```
