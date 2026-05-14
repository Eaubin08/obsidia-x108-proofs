# MIGRATION COMMIT_NOW — Brody Memory Pipeline
## Timestamp: 20260514

## Contexte

Le repo `obsidia-engine-proof-core` (core) a été utilisé comme workspace par erreur.
La source-of-truth corrigée est : `obsidia-x108-proofs`.

Cette migration ne reprend que le périmètre stabilisé (COMMIT_NOW).
Les blocs postérieurs (HOLD_LOCAL) restent dans core en attente.

## Ce que cette migration contient

16 dossiers d'audit stabilisés :
- LOW_MATERIAL_RESOLVED=true (patch + validation)
- TEXT_PREVIEW_MATERIAL_CONFIRMED=true
- MEMORY_PIPELINE_STABLE=true (42 BrodyImportedMemory)
- DECISION_AUTHORITY=KX108_ONLY
- NO_X108_MERGE=true

## Ce que cette migration ne fait PAS

- Aucun nettoyage core
- Aucun rewrite history
- Aucun X108 merge
- Aucun runtime binding
- Aucun Neo4j write
- Aucun Graphiti write
- Les 18 dossiers HOLD_LOCAL restent dans core (phase postérieure)
- Les 163 dossiers EXCLUDE ne sont pas migrés

## Fichiers

- MIGRATION_COMMIT_NOW_SOURCE_MAP.json
- MIGRATION_COMMIT_NOW_MANIFEST_SHA256.json
- MIGRATION_HOLD_LOCAL_INDEX.json
- MIGRATION_EXCLUDED_INDEX.json
- CURRENT_X108_BRODY_MEMORY_PIPELINE_COMMIT_NOW.txt
