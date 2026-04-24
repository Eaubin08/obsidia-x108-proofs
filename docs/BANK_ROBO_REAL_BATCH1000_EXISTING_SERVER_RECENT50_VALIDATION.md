# BANK_ROBO_REAL_BATCH1000_EXISTING_SERVER_RECENT50_VALIDATION

## Statut

Validation réelle locale obtenue sur batch 1000 via le runner officiel en mode existing_server avec RecentLimit=50.

## Date

2026-04-24 09:55:17

## Run validé

`artifacts/bank_robo_real/batch_probe/20260424-014052`

## Chaîne validée

1. serveur `bank-robo` déjà vivant
2. mode `existing_server`
3. 1000 appels réels `banking.processTransaction`
4. 1000 relectures réelles `banking.getRecentTransactions` avec `RecentLimit = 50`
5. zéro erreur process
6. zéro erreur recent

## Résultat observé

- `process_ok_count = 1000`
- `process_error_count = 0`
- `recent_ok_count = 1000`
- `recent_error_count = 0`
- `recent_route_available = true`

## Distribution observée

- `AUTORISER = 537`
- `ANALYSER = 428`
- `BLOQUER = 35`

## Ce que cela prouve

Le runner officiel patché tient un batch 1000 en mode `existing_server` avec relecture bornée (`RecentLimit = 50`) sur chaque itération.

## Limite connue

La configuration `RecentLimit = 1200` à chaque itération n est pas validée dans ce palier.

## Base dédiée

`mysql://root:root_pw@localhost:3306/bank_robo`

## Env local dédié

`tools/bank_robo_real/local_env/.env.bank_robo.local`
