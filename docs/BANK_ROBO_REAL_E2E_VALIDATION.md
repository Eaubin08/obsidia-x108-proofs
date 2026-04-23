# BANK_ROBO_REAL_E2E_VALIDATION

## Statut

Validation réelle locale obtenue.

## Chaîne validée

1. boot réel du serveur `bank-robo`
2. base MySQL dédiée `bank_robo`
3. schéma présent avec table `transactions`
4. appels réels `banking.processTransaction`
5. relecture réelle via `banking.getRecentTransactions`

## Résultat observé

- `PROCESS 1` : réponse métier valide
- `PROCESS 2` : réponse métier valide
- `RECENT` : retour non vide
- lignes relues : `id = 1`, `id = 2`
- `actualGate` remonte correctement (`ALLOW`, `HOLD`)

## Ce que cela prouve

Le raccord réel local `bank-robo -> MySQL -> route proof-side getRecentTransactions` fonctionne.

## Hors périmètre de cette validation

- OAuth réel
- Gemini réel
- correction UTF-8 des messages
- déploiement production
- endurance/stress runtime

## Base dédiée

`mysql://root:root_pw@localhost:3306/bank_robo`

## Env local dédié

`tools/bank_robo_real/local_env/.env.bank_robo.local`
