# F78B_ZIP_INTERNAL_INVENTORY
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## Résumé global

| Pack | Fichiers total | Dirs | .py | .md | .yaml | .json | Vides | Dups basenames |
|------|---------------|------|-----|-----|-------|-------|-------|----------------|
| RSSI_EXTERNAL_SIGNALS | 41 | 0 | 0 | 6 | 33 | 0 | 0 | 0 |
| RSSI_SECURITY | 167 | 0 | **16** | 132 | 0 | 18 | 0 | 0 |
| RSSI_RGPD_ISO | 311 | 0 | **23** | 229 | 0 | 26 | 0 | **8** |
| BRANCHABLE_ATLAS | 1738 | 0 | **18** | 1241 | 0 | 453 | 0 | **92** |
| COGNITIVE | 519 | 0 | 0 | 12 | **490** | 8 | 0 | 0 |
| **TOTAL** | **2776** | | **57** | **1620** | **523** | **505** | 0 | **100** |

---

## Pack 1 — RSSI_EXTERNAL_SIGNALS_PATCH_V1

```
Source: OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip
Root:   OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1/
Total:  41 fichiers
.py:    0
```

### Structure racine

| Chemin | Type | Contenu |
|--------|------|---------|
| MERGE_INSTRUCTIONS.md | doc | Instructions de merge dans le repo existant |
| README.md | doc | Description du pack |
| SHA256SUMS.txt | integrity | Checksums des fichiers |
| VALIDATION_REPORT.yaml | validation | Rapport de validation du pack |
| component_specs/ | dir | C459-C482 (24 fichiers yaml) |
| family_specs/ | dir | Familles 46-48 (3 fichiers yaml) |
| merge_appendices/ | dir | Appendices CSV/YAML/MD pour merge |
| packets/ | dir | Packets 51-53 (3 fichiers yaml) |
| proof/ | dir | Artefacts de preuve (1 fichier) |
| tests/ | dir | Matrice de tests (1 fichier) |

### Statut local

**37/41 fichiers déjà importés** dans `specs/external_signals/` via F04.
Fichiers potentiellement manquants localement : `merge_appendices/` (6 fichiers).

---

## Pack 2 — RSSI_SECURITY_PRESENTATION_PACK_V1

```
Source: OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip
Root:   OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1/
Total:  167 fichiers
.py:    16 — IMPORTANT
```

### Structure racine

| Chemin | Type | Contenu |
|--------|------|---------|
| README.md | doc | Description |
| periphery/ | **dir PYTHON** | `rssi_security_pack/` — 16 fichiers .py |
| src/ | dir | Sources spec RSSI |
| docs/ | dir | Documentation RSSI |
| specs/ | dir | Specs RSSI security |
| audit/ | dir | Audit evidence |

### .py identifiés (16 fichiers)

```
periphery/rssi_security_pack/__init__.py
periphery/rssi_security_pack/audit_questions.py
periphery/rssi_security_pack/evidence_registry.py
periphery/rssi_security_pack/control_registry.py
periphery/rssi_security_pack/risk_registry.py
periphery/rssi_security_pack/security_case.py
periphery/rssi_security_pack/rssi_types.py
periphery/rssi_security_pack/readonly_boundary.py
periphery/rssi_security_pack/export_helpers.py
... (7 autres)
```

### Décision Python

```
periphery/.py → DO_NOT_IMPORT_RUNTIME
Import F03 = docs/specs/audit/ uniquement
periphery/ = QUARANTINE pour import
```

---

## Pack 3 — RSSI_RGPD_ISO_READINESS_PACK_V2

```
Source: OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip
Root:   OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2/
Total:  311 fichiers
.py:    23 — IMPORTANT
Dups:   8 noms (manifests et snapshots versionnés)
```

### .py identifiés (23 fichiers)

```
periphery/rssi_security_pack/__init__.py
periphery/rssi_security_pack/rssi_types.py
periphery/rssi_security_pack/readonly_boundary.py
periphery/rssi_security_pack/control_registry.py
periphery/rssi_security_pack/risk_registry.py
... (18 autres dans periphery/)
```

### 8 noms dupliqués (snapshots versionnés)

```
MANIFEST_SHA256.json          — plusieurs versions dans sous-dossiers
rssi_file_registry_snapshot.json
rssi_control_registry_snapshot.json
rssi_risk_registry_snapshot.json
rssi_security_case_snapshot.json
rssi_file_registry_snapshot.json
rssi_control_registry_snapshot.json
rssi_risk_registry_snapshot.json
```

Note : dups documentés dans COLLISION_RESOLUTION_PLAN = snapshots versionnés, pas de
vrais conflits. Décision : garder la version la plus riche.

---

## Pack 4 — BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS

```
Source: OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip
Root:   OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_5_DEEP_FINAL_AUDIT/
Total:  1738 fichiers
.py:    18 — IMPORTANT
Dups:   92 noms (snapshots versionnés + audit files)
```

### Structure racine

| Chemin | Type | Contenu |
|--------|------|---------|
| *.json, *.md | Audit docs | COMPLETION_AUDIT, DEEP_FINAL_AUDIT, FINAL_PASS_AUDIT (V0_3 à V0_7) |
| .pytest_cache/ | **QUARANTINE** | Artefacts pytest — DO_NOT_IMPORT |
| .runtime_freezes/ | **ARCHIVE_ONLY** | Snapshots runtime figés |
| periphery/ | **dir PYTHON** | `world_protocol_atlas/` — 18 fichiers .py |
| patches/ | **dir PYTHON** | `periphery_ops_world_atlas_routes_SNIPPET_NOT_APPLIED.py` |

### .py identifiés (18 fichiers)

```
periphery/world_protocol_atlas/__init__.py
periphery/world_protocol_atlas/a_modules_registry.py
periphery/world_protocol_atlas/world_atlas_ops.py
periphery/world_protocol_atlas/atlas_route_matcher.py
patches/periphery_ops_world_atlas_routes_SNIPPET_NOT_APPLIED.py
... (13 autres)
```

Note : le patch est marqué `SNIPPET_NOT_APPLIED` — confirm non intégré.

### 92 doublons basenames

Principalement : `README.md`, `MANIFEST_SHA256.json`, `audit_report.json`,
`context_packets_snapshot.json`, `graphiti_nodes_snapshot.json`.
Ces doublons sont des snapshots versionnés dans des sous-dossiers d'audit.
Décision : RAW_ARCHIVE_ONLY pour `.runtime_freezes/`, AUDIT_DOCS pour les autres.

---

## Pack 5 — COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL

```
Source: OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip
Root:   (fichiers racine directs — pas de sous-dossier principal)
Total:  519 fichiers (513 fichiers + dirs)
.py:    0 ← PROPRE
Dups:   0 ← PROPRE
```

### Structure racine (6 fichiers MD + sous-dossiers)

```
01_README.md
02_SCOPE_AND_DECISION.md
03_SOURCE_INVENTORY.md
04_CANON_MAP.md
05_LEGACY_TO_KERNEL_BOUNDARY.md
[sous-dossiers yaml]
```

### Extensions

- yaml : 490 (corps principal des specs)
- md : 12 (documentation)
- json : 8 (manifests)
- csv : 2
- sha256 : 1 (checksum)

**Pack le plus propre** : 0 .py, 0 dups, structure claire.
Candidat prioritaire pour import F07.

---

## Sources non zippées

### NPL (déjà importé)

Zip source absent de `raw/` mais contenu importé :
- `specs/12_NARRATIVE_PROVENANCE_LAYER/` : 34 fichiers

### XLSX Implementation Plan

```
OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx
Rôle : backlog file-by-file principal
Usage : référence planning / séquencement (SOURCE_ONLY)
Import : NON — tableur binaire, pas de specs
```
