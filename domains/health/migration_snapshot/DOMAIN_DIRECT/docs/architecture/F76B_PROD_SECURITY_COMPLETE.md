# F76b — Prod Security Complete
**Date** : 2026-05-30 | **Statut** : PASS | **F76 score** : 10/10

---

## Résumé

F76b complète la sécurité API minimale. F76 est maintenant **10/10 PASS**.

| Item | Avant F76b | Après F76b |
|---|---|---|
| Rate limiting | FAIL | **PASS** — `_RateLimitMiddleware` dans `main.py` |
| Auth APIKey | FAIL | **PASS** — `require_api_key` sur `/api/brody/chat` |
| docker-compose.yml | FAIL | **PASS** — créé avec guard OBSIDIA_API_KEY |
| ROLLBACK_PLAN.md | FAIL | **PASS** — créé |
| **F76 total** | **6/10 PARTIAL** | **10/10 PASS** |
| **Score global** | **32/50** | **36/50** |

---

## Auth — Comportement par environnement

| Condition | Comportement |
|---|---|
| `APP_ENV=dev` (défaut) | Pass-through — aucun check |
| `OBSIDIA_AUTH_ENABLED=false` | Pass-through |
| `OBSIDIA_AUTH_ENABLED=true` + `OBSIDIA_API_KEY=""` | **503 AUTH_MISCONFIGURED** — jamais de bypass silencieux |
| `APP_ENV=prod` + `OBSIDIA_API_KEY=""` | **503 AUTH_MISCONFIGURED** |
| Auth activée + mauvaise clé | **401 INVALID_API_KEY** |
| Auth activée + bonne clé | **pass** |

**Ligne rouge respectée** : aucun bypass silencieux en prod sans clé.

Toutes les réponses d'erreur contiennent `decision_authority=KX108_ONLY`, `emits_act=False`.

---

## Rate Limit

| Condition | Comportement |
|---|---|
| `APP_ENV=dev` | Middleware no-op (bypass immédiat) |
| `OBSIDIA_RATE_LIMIT_ENABLED=false` | no-op |
| `OBSIDIA_RATE_LIMIT_ENABLED=true` ou `APP_ENV=prod` | Actif — 60 req/min par IP par défaut |
| Réponse 429 | `error=rate_limit_exceeded`, `KX108_ONLY`, `readonly=True`, `emits_act=False` |

Chemins exemptés : `/api/health`, `/api/readiness`, `/api/status`, `/`.
Zéro dépendance externe — `BaseHTTPMiddleware` est dans starlette.

---

## Endpoints protégés vs publics

| Endpoint | Protection |
|---|---|
| `POST /api/brody/chat` | `require_api_key` (prod only) |
| `GET /api/health` | public |
| `GET /api/readiness` | public |
| `GET /api/status` | public |
| `GET /bus/*`, `GET /api/periphery/monitoring/sigma/*` | public |
| `POST /api/x108/*` | différé F76c |

---

## Tests passés

| Suite | Tests | Résultat |
|---|---|---|
| Régression sigma+F63+F65+brody | 1103 | ✅ PASS |
| F76b ciblés (auth + rate-limit) | 14 | ✅ PASS |

---

## Docker compose

`docker-compose.yml` utilise `${OBSIDIA_API_KEY:?OBSIDIA_API_KEY is required in production}` — le démarrage échoue explicitement si la clé est manquante en prod.

---

## Blockers restants → F76c (optionnel)

| Item | Priority | Action |
|---|---|---|
| Auth sur `POST /api/x108/*` | P1 | Analyser routes x108 avant protection |
| Redis-backed rate limit (multi-process) | P2 | Si scaling nécessaire |
| Logs d'accès structurés | P2 | Audit middleware existant à enrichir |

---

_F76b — Prod Security Complete | 2026-05-30 | Aucun commit/tag/push | KX108_ONLY_
