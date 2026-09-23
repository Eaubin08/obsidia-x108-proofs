# WORKSPACE_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/` (15 dossiers)
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/` (20 dossiers)
- `_obsidia-local-workspace/` (données privées quarantinées)

Imported Facts:
- OBSIDIA_V4_STRUCTURED_FULL : 00_INDEX, 00_SOURCES, 01_REGISTRES_JSON, 02_BLOCS_17, 03_PEPITES_161, 04_SPECS_40, 05_MODULES_A1_A24, 06_GARDIENS_DE_FOND_T1_T12, 07_AGENTS_ET_ROLES, 08_PREUVES_LEAN_TLA, 09_TESTS_PY_TS_CHAOS_LOAD, 10_AUDITS_A_F, 11_CONTRATS_OS3_OS4_ADELE, 12_EXTENSIONS_R_D, 13_ENGINE_GATES, 14_REGROUPEMENTS_COHERENCE
- MMONDE : 20 sous-dossiers (00_INDEX à 20_DEMO_MINIMALE)
- obsidia-workspace standalone = ABSENT_LOCAL_REPO — workspace = intégré dans periphery/
- /domaines/ = ABSENT → `02_BLOCS_17/` + `04_SPECS_40/`
- /fondations/ = ABSENT → `06_GARDIENS_DE_FOND_T1_T12/`
- /agents/ = ABSENT → `07_AGENTS_ET_ROLES/`
- .xyz = BRANCHESXYZKLN.md dans `12_EXTENSIONS_R_D/` → SOURCE_FOUND_UNDER_DIFFERENT_NAME

What This Source Proves:
- Hub intellectuel V4 structuré présent dans periphery/
- Les noms Gemini (/domaines/, /fondations/, /agents/) correspondent à des sous-dossiers réels sous d'autres noms

What This Source Does NOT Prove:
- Que .xyz = BRANCHESXYZKLN.md (contenu à vérifier)
- Que obsidia-workspace existe comme repo standalone

Boundary:
- DOC_ONLY — structure documentaire, pas runtime

Claim-Scope:
- "Le workspace Obsidia V4 est intégré dans periphery/OBSIDIA_V4_STRUCTURED_FULL/" — AUTORISÉ
- "obsidia-workspace est un repo standalone" — INTERDIT (ABSENT)

Specs Depending On This Source:
- 02_INTERLAYER_CONSTITUTION/WORKSPACE_TO_RUNTIME_ADMISSION_SPEC.md
- 02_INTERLAYER_CONSTITUTION/XYZ_COMPILATION_PIPELINE_SPEC.md

Runtime Status: DOC_ONLY

Do Not Move Original Source: true
Authority: KX108_ONLY
