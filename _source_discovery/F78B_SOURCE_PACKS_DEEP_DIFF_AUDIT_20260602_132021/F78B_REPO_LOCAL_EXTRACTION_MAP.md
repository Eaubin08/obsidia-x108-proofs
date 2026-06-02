# F78B_REPO_LOCAL_EXTRACTION_MAP
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## Carte du repo local — état F78B

| Local path | Source family inferred | Status | Canon level | Notes |
|-----------|----------------------|--------|-------------|-------|
| specs/external_signals/ | RSSI_EXTERNAL_SIGNALS_PATCH_V1 | SPEC_IMPORTED (F04) | SPEC_IMPORTED | 3 racine + 4 sous-dossiers (component_specs, family_specs, packets, appendices) |
| specs/12_NARRATIVE_PROVENANCE_LAYER/ | NPL (zip absent) | SPEC_IMPORTED (F04) | SPEC_IMPORTED | 34 fichiers — NPL zip source absent de raw/ |
| specs/00_SCOPE_DISCIPLINE/ | Multi-source | SPEC_LOCKED | CANON | 9 fichiers — scope discipline |
| specs/01_X108_AUTHORITY/ | Multi-source | SPEC_LOCKED | CANON | 7 fichiers |
| specs/02_INTERLAYER_CONSTITUTION/ | Multi-source | SPEC_LOCKED | CANON | 8 fichiers |
| specs/03_ENTROPY_DISCIPLINE/ | Multi-source (Audio/P107/P161) | SPEC_LOCKED | SPEC_CANDIDATE | 11 fichiers — PYTHON_SPEC_NOT_LEAN_PROVEN pour P107/P161 |
| specs/04_AGI_TREE34_FLUX/ | Multi-source | SPEC_LOCKED | CANON | 5 fichiers |
| specs/05_BALANCE_BUV_GEOMETRIES/ | Multi-source | SPEC_LOCKED | CANON | 9 fichiers |
| specs/06_HIGH_PERIPHERY_SYSTEMS/ | Multi-source | SPEC_LOCKED | CANON | 7 fichiers |
| specs/07_AGENTS_CONNECTORS_MCP/ | Multi-source | SPEC_LOCKED | CANON | 10 fichiers |
| specs/08_MEMORY_BRODY_GRAPHITI/ | Multi-source | SPEC_LOCKED | CANON | 7 fichiers — Brody corpus absent Graphiti V20 |
| specs/09_CRITICAL_WORLDS/ | Multi-source | SPEC_LOCKED | CANON | 14 fichiers |
| specs/10_VALUE_GENCOIN_JCOIN/ | Multi-source | SPEC_LOCKED | CANON | 11 fichiers |
| specs/11_PROOF_REPLAY_OS3/ | Multi-source | SPEC_LOCKED | CANON | 9 fichiers |
| specs/_imports_readonly/ | Multi-source | READONLY | READONLY | 17 fichiers |
| specs/_invariant_graph/ | Kernel | SPEC_LOCKED | CANON | 2 fichiers |
| specs/_source_index/ | Index | SPEC_LOCKED | INDEX | 7 fichiers |
| runtime_contracts/ | Plan 3 P0-P3 | DOCS_ONLY | CONTRACT_SKELETON | 57 fichiers — aucun runtime |
| _source_packs/OBSIDIA_UNIFIED_.../raw/ | Source zips | COPIED_READONLY | RAW | 5 zips + 1 xlsx |
| _source_discovery/ | Audits | AUDIT_ONLY | AUDIT | Plans 0-F78B |
| _backups/ | Baseline freeze | BACKUP | BACKUP | Plan 3 P0 baseline |
| docs/source_packs/ | Documentation packs | DOCS | DOCS | — |

---

## Packs non encore extraits localement

| Pack | Zip | Chemin zip | Statut local |
|------|-----|-----------|-------------|
| RSSI Security | OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip | raw/ | ABSENT de specs/ |
| RSSI RGPD | OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip | raw/ | ABSENT de specs/ |
| Branchable Atlas | OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip | raw/ | ABSENT de specs/ |
| Cognitive | OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip | raw/ | ABSENT de specs/ |

---

## External Signals — état d'extraction partielle

### Dans specs/external_signals/ (présent)

```
specs/external_signals/
  F04_EXTERNAL_SIGNALS_BOUNDARY.md
  F04_EXTERNAL_SIGNALS_IMPORT_REPORT.md
  PLAN2_DELTA_EXTERNAL_SIGNALS_UPDATE.md
  appendices/          (merge_appendices importés)
  component_specs/     (C459-C482 yaml)
  family_specs/        (familles 46-48 yaml)
  packets/             (packets 51-53 yaml)
```

### Dans zip mais potentiellement manquant local

```
proof/53_EXTERNAL_SIGNALS_PROOF_ARTIFACTS.md  → à vérifier
tests/52_EXTERNAL_SIGNALS_TEST_MATRIX.md      → à vérifier F04
VALIDATION_REPORT.yaml                         → à vérifier
```

### Overlap calculé

37/41 noms de fichiers du zip = présents dans specs/
4 fichiers potentiellement non importés : voir ci-dessus

---

## Fichiers racine non-committés (processus externe)

| Fichier/Dossier | Nature | Créé par |
|----------------|--------|----------|
| SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/ | Ancien run F78B incomplet | Processus externe (zips non inspectés) |
| OBSIDIA_COMPONENT_GROUP_REGISTRY_20260602_125346.csv | Registre composants | Processus externe |
| OBSIDIA_COMPONENT_GROUP_REGISTRY_V2_20260602_125604/ | Registre composants V2 | Processus externe |
| OBSIDIA_COMPONENT_SPLIT_V3_20260602_125929/ | Split composants V3 | Processus externe |
| OBSIDIA_CANONICAL_COMPONENT_CORPUS_MAP_V4_*.csv | Carte corpus composants | Processus externe |
| LOCAL_ONLY_MATTER_*.md | Réconciliation matière | Processus externe |
| .local_audits/ | Audits locaux | Processus externe (PREEXISTING) |

Ces fichiers sont **hors périmètre F78B** — non modifiés par ce run.
