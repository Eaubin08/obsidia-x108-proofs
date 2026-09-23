# BANK_ROBO_REAL_PATCH_DELTA

## Objet

Tracer les deltas locaux ajoutés côté proof-suite par rapport à l'upstream `bank-robo`.

## Delta identifié

Le routeur public upstream n'expose pas `getRecentTransactions`.
Cette route doit donc être traitée comme adaptation locale proof-side.

## Convention

- source amont conservée dans `docs/sources/bank-robo-real/`
- delta local conservé dans `patches/bank_robo_real/`
- scripts d'exploitation conservés dans `tools/bank_robo_real/`

## Patchs prévus

- `patches/bank_robo_real/routers.getRecentTransactions.patch`
- éventuellement `patches/bank_robo_real/routers.debugDbStatus.patch`