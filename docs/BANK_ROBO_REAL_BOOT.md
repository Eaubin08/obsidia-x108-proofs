# BANK_ROBO_REAL_BOOT

## Objet

Ce document décrit le boot réel observable de `bank-robo` depuis `server/_core/index.ts`.

## Réalité structurelle

Le boot utile part de :

- `server/_core/index.ts`
- `server/_core/env.ts`
- `server/db.ts`
- `server/routers.ts`
- `server/bankingEngine.ts`
- `drizzle.config.ts`
- `drizzle/schema.ts`

## Ce que le boot doit prouver

1. l'entrypoint s'exécute réellement
2. `PORT` est pris en compte
3. le port réel est observable
4. stdout/stderr sont capturés
5. le process reste vivant assez longtemps pour sonder l'API

## Règle opératoire

Ne pas considérer un boot comme valide si on n'a pas au moins l'un des signaux suivants :

- `Server running on http://localhost:<port>/`
- une erreur explicite en stderr
- un listener réseau détecté
- un probe HTTP positif

## Scripts liés

- `tools/bank_robo_real/run_bank_robo_foreground.ps1`
- `tools/bank_robo_real/run_bank_robo_foreground.sh`
- `tools/bank_robo_real/runtime_autopsy.ps1`