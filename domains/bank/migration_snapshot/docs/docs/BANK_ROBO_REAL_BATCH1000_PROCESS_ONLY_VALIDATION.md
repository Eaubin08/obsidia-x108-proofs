# BANK_ROBO_REAL_BATCH1000_PROCESS_ONLY_VALIDATION

## Statut

Validation réelle locale obtenue sur batch 1000 côté client en mode process-only, serveur bank-robo vivant.

## Date

2026-04-24 01:40:33

## Run validé

`artifacts/bank_robo_real/manual_client_batch1000_process_only/20260424-005818`

## Chaîne validée

1. serveur `bank-robo` vivant
2. MySQL dédiée `bank_robo`
3. 1000 appels réels `banking.processTransaction`
4. 0 erreur process
5. 1 relecture réelle finale `banking.getRecentTransactions`

## Résultat observé

- `process_ok_count = 1000`
- `process_error_count = 0`
- `recent_ok = true`
- `recent_count = 50`

## Ce que cela prouve

Le runtime réel local bank-robo tient 1000 écritures client consécutives avec relecture finale positive.
Le point non validé reste la relecture répétée à chaque itération sous forte charge.

## Hors périmètre

- relecture `recent` à chaque itération sur 1000
- fault injection
- endurance prolongée
- OAuth réel
- Gemini réel
- correction UTF-8 des messages

## Base dédiée

`mysql://root:root_pw@localhost:3306/bank_robo`

## Env local dédié

`tools/bank_robo_real/local_env/.env.bank_robo.local`
