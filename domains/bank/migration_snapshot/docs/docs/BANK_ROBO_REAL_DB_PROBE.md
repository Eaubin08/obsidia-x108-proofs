# BANK_ROBO_REAL_DB_PROBE

## Objet

Ce document sépare les niveaux de validation du raccord réel bank-robo.

## Niveaux

### 1. Boot
Le serveur démarre réellement et reste observable.

### 2. API
Les routes répondent réellement sur le port actif.

### 3. Logique métier
`processTransaction` retourne une décision cohérente.

### 4. Persistance
`db.insert(transactions)` s'exécute réellement.

### 5. Relecture
`getRecentTransactions` relit réellement les écritures.

## Distinction stricte

Une API peut être vivante sans DB.
Une logique métier peut être vivante sans persistance.
Une persistance peut être tentée sans être relue.

## Scripts liés

- `tools/bank_robo_real/probe_bank_robo_db_status.ps1`
- `tools/bank_robo_real/probe_bank_robo_process_transaction.ps1`
- `tools/bank_robo_real/probe_bank_robo_recent_transactions.ps1`