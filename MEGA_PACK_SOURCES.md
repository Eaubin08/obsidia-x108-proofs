# Sources consolidées

## Socle principal
- `OBSIDIA_WORKSPACE_FINAL.zip`

## Sources de vérité kernel / proofs
- `obsidia-x108-proofs-main.zip`
- snapshot copié sous `upstream/obsidia-x108-proofs-main/`

## Décisions de consolidation
- Les scripts/verifiers RFC/TLA/replay/provenance proviennent du workspace final.
- Les fichiers `formal/tla/*.cfg` ont été repris du repo `obsidia-x108-proofs-main`.
- `server/trpc/trpc.ts` a été ajouté comme alias depuis `server/_core/trpc.ts` pour aligner la structure attendue.
