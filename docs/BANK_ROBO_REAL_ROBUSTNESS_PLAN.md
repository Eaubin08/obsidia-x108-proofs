# BANK_ROBO_REAL_ROBUSTNESS_PLAN

## Objet

Passer de la preuve de raccord à la preuve de robustesse bank sur :

- `processTransaction`
- `getRecentTransactions` (delta proof-side)
- `DATABASE_URL` / MySQL réel
- boot observable via `server/_core/index.ts`

## Précondition locale

Env dédiée à prioriser :

`tools/bank_robo_real/local_env/.env.bank_robo.local`

Base dédiée :

`mysql://root:root_pw@localhost:3306/bank_robo`

## Paliers

### Palier A — cohérence mono-run
- réponse API `processTransaction`
- lecture `getRecentTransactions`
- DB réelle si accessible

### Palier B — batch 100
- erreurs HTTP
- cohérence décision / actualGate
- présence des appels récents
- divergence éventuelle API / recent / DB

### Palier C — batch 1k
Même logique avec charge supérieure.

### Palier D — fault injection v1
- `DB_MISSING_ENV`
- `DB_INVALID_URL`
- `OAUTH_MISSING`
- `GEMINI_MISSING`
- `PORT_OCCUPIED`

### Palier E — consistency report
- `total`
- `match`
- `mismatch`
- classes d’erreur
- disponibilité route recent
- disponibilité DB

## Invariants

- `decision` persistée = `decision` API
- `actualGate` suit :
  - `AUTORISER -> ALLOW`
  - `ANALYSER -> HOLD`
  - `BLOQUER -> BLOCK`
- les lignes récentes contiennent les derniers appels
- `limit = N` renvoie au plus `N`
- zéro `500` en série nominale