# F78C_XLSX_QUARANTINE_REVIEW
# Date: 2026-06-02 — Status: XLSX_AUDIT_ONLY / READONLY

---

## Résumé

| Catégorie | Lignes | Pack | Décision |
|-----------|--------|------|----------|
| QUARANTINE_DO_NOT_IMPLEMENT (.pytest_cache) | 20 | BRANCHABLE_ATLAS | KEEP_QUARANTINE |
| packages/ conflicts (périphériques) | 8 | EXTERNAL_SIGNALS + COGNITIVE | DO_NOT_IMPORT |
| .py runtime files | 57 | ATLAS + RSSI + RGPD | DO_NOT_IMPORT (exclusion F03/F06) |
| .runtime_freezes | 45 | BRANCHABLE_ATLAS | ARCHIVE_ONLY |

---

## 1. QUARANTINE_DO_NOT_IMPLEMENT — 20 lignes .pytest_cache

### Source
Pack BRANCHABLE_ATLAS — artefacts pytest de la suite de tests Atlas.

### Fichiers quarantinés (20)

| Chemin | target_location | Priorité |
|--------|-----------------|----------|
| .pytest_cache/.gitignore | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| .pytest_cache/CACHEDIR.TAG | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| .pytest_cache/README.md | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| .pytest_cache/v/cache/lastfailed | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| .pytest_cache/v/cache/nodeids | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| .pytest_cache/v/cache/stepwise | archive/quarantine/generated_cache/ | P5_QUARANTINE |
| + 14 autres artefacts .pytest_cache | archive/quarantine/generated_cache/ | P5_QUARANTINE |

### Décision : KEEP_QUARANTINE

Ces fichiers sont déjà marqués `QUARANTINE_DO_NOT_IMPLEMENT` dans le XLSX.
Le target_location `archive/quarantine/generated_cache/` confirme l'intention de ne pas les importer.
Ils ne doivent pas être copiés dans `specs/` ou `runtime_contracts/` sous aucun prétexte.

**Action F06 :** Lors de l'import Atlas, exclure explicitement `.pytest_cache/**`.

---

## 2. packages/ conflicts — 8 lignes

### Explication
Ces 8 fichiers ciblent `packages/shared/` — dossier interdit dans ce repo.

**Décision : DO_NOT_IMPORT**

Voir F78C_XLSX_TARGET_PATH_DUPLICATES.md pour le détail.

Alternative pour les 5 packets COGNITIVE :
- Import dans `specs/cognitive/packets/` lors de F07 (cible alternative safe).
Alternative pour les 3 packets EXTERNAL_SIGNALS :
- Déjà importés dans `specs/external_signals/packets/` (F04). Aucune action requise.

---

## 3. .py runtime files — 57 fichiers

### Répartition

| Pack | .py count | Chemin dans zip | Target XLSX |
|------|-----------|-----------------|------------|
| RSSI_SECURITY | 16 | periphery/rssi_security_pack/*.py | security/rssi/modules/ |
| RGPD_ISO | 23 | periphery/rssi_security_pack/*.py | (mixed targets) |
| BRANCHABLE_ATLAS | 18 | periphery/world_protocol_atlas/*.py + patches/*.py | atlas/world_protocol_atlas/ |

**Note :** Le XLSX assigne certains de ces .py au groupe `periphery/rssi_security_pack`
et `periphery/world_protocol_atlas`. Ces groupes correspondent à des dossiers `periphery/`
existants dans le repo racine — dossier qui NE DOIT PAS recevoir ces imports.

**Décision : DO_NOT_IMPORT_RUNTIME pour tous les .py**
Action F03/F06 : exclure `*.py` de tous les imports de packs.

Décision granulaire :
- `periphery/rssi_security_pack/*.py` : DO_NOT_IMPORT (ne pas toucher periphery/ existant)
- `periphery/world_protocol_atlas/*.py` : DO_NOT_IMPORT
- `patches/periphery_ops_world_atlas_routes_SNIPPET_NOT_APPLIED.py` : DO_NOT_IMPORT (SNIPPET_NOT_APPLIED)

---

## 4. .runtime_freezes — 45 lignes

### Localisation
Pack BRANCHABLE_ATLAS — snapshots d'états runtime figés à différentes versions (V0, V0_1, V0_3, ...).

### Groupes .runtime_freezes dans le XLSX

| Group | Lignes |
|-------|--------|
| .runtime_freezes/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1 | 14 |
| .runtime_freezes/WORLD_PROTOCOL_ATLAS_FULL_V0_1_EXHAUSTIVE | 12 |
| .runtime_freezes/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2 | 7 |
| .runtime_freezes/WORLD_PROTOCOL_ATLAS_FULL_V0 | 6 |
| .runtime_freezes/WORLD_PROTOCOL_ATLAS_V0 | 6 |

**Décision : ARCHIVE_ONLY**
Ces fichiers documentent des états de runtime figés — valeur historique/audit uniquement.
Ne pas importer dans `specs/` ou `runtime_contracts/`.
Garder dans le zip source comme archives.

---

## Récapitulatif décisions quarantaine

| Catégorie | Nb | Décision | Action gate |
|-----------|-----|----------|------------|
| .pytest_cache | 20 | KEEP_QUARANTINE | F06 — exclure .pytest_cache/** |
| packages/ conflicts | 8 | DO_NOT_IMPORT | Résolu — alternative specs/ pour F07 |
| .py runtime | 57 | DO_NOT_IMPORT_RUNTIME | F03/F06 — exclure *.py |
| .runtime_freezes | 45 | ARCHIVE_ONLY | F06 — ne pas importer dans specs/ |
| **Total à exclure** | **130** | | |
