# F76a — API Security Minimal
**Date** : 2026-05-30 | **Statut** : PASS items F76a | **Score F76** : 6/10 (était 2/10 CRITICAL)

---

## Résumé

F76a implémente la sécurité API minimale. Les 4 items structurels (CORS, APP_ENV guard, Dockerfile, health) sont résolus. Les 4 restants (rate-limit, auth, docker-compose, rollback plan) sont différés à F76b.

| Item | Avant F76a | Après F76a |
|---|---|---|
| CORS wildcard `["*"]` | FAIL — wildcard actif | **PASS** — env-based, dev localhost |
| CORS env var ALLOWED_ORIGINS | FAIL | **PASS** |
| Dockerfile | FAIL — MISSING | **PASS** — python:3.12-slim créé |
| APP_ENV guard /docs prod | FAIL | **PASS** — `APP_ENV=prod` → None |
| GET /health | PASS (status.py) | **PASS** — `/api/health` explicite |
| GET /readiness | FAIL | **PASS** — `/api/readiness` ajouté |
| Rate limiting | FAIL | DEFERRED → F76b |
| Auth | FAIL | DEFERRED → F76b |
| docker-compose.yml | FAIL | DEFERRED → F76b |
| ROLLBACK_PLAN.md | FAIL | DEFERRED → F76b |
| **Score F76** | **2/10 CRITICAL** | **6/10 PARTIAL** |
| **Score global** | **19/50** | **32/50** |

---

## Fichiers modifiés

### apps/obsidia_api/main.py

**Backup** : `apps/obsidia_api/main.py.bak_20260530_064339_CLAUDE_BEFORE_PATCH`

Changements minimaux (3 blocs ajoutés, 1 bloc remplacé) :
1. `import os` ajouté
2. `_APP_ENV` + docs guards (`_docs_url`, `_redoc_url`, `_openapi_url`)
3. `FastAPI(...)` avec `docs_url`, `redoc_url`, `openapi_url` conditionnels
4. `_ALLOWED_ORIGINS` depuis `ALLOWED_ORIGINS` env var (dev default: localhost)
5. `CORSMiddleware` avec `_ALLOWED_ORIGINS` (pas de wildcard)

### apps/obsidia_api/routes/status.py

**Backup** : `apps/obsidia_api/routes/status.py.bak_20260530_064448_CLAUDE_BEFORE_PATCH`

Ajout de 2 endpoints readonly en haut du fichier :
- `GET /api/health` → `{status: "ok", decision_authority: "KX108_ONLY", readonly: true, emits_act: false}`
- `GET /api/readiness` → `{status: "ready", mode: "READONLY_READY", decision_authority: "KX108_ONLY"}`

---

## Fichiers créés

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV APP_ENV=prod
ENV OBSIDIA_API_HOST=0.0.0.0
ENV OBSIDIA_API_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "apps.obsidia_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker build** : `obsidia-x108-api:f76a` — EXIT=0 en 26.7s

---

## Comportement CORS après patch

| Environnement | Valeur | Comportement |
|---|---|---|
| `ALLOWED_ORIGINS` non défini | — | Dev default : localhost:3000, 8000, 127.0.0.1:8000 |
| `ALLOWED_ORIGINS=https://app.example.com` | liste | Seule cette origine autorisée |
| Ancienne config | `["*"]` | **SUPPRIMÉE** — grep CORS_WILDCARD_REMOVED ✓ |

---

## Comportement APP_ENV guard

| `APP_ENV` | `/docs` | `/redoc` | `/openapi.json` |
|---|---|---|---|
| `dev` (défaut) | `/docs` | `/redoc` | `/openapi.json` |
| `development` | `/docs` | `/redoc` | `/openapi.json` |
| `prod` | `None` | `None` | `None` |
| Toute autre valeur | `None` | `None` | `None` |

Note : `app.openapi()` (Python method) fonctionne toujours — seul le endpoint HTTP est désactivé.

---

## Tests de régression

| Suite | Tests | Résultat |
|---|---|---|
| tests/sigma | 817 | ✅ PASS |
| tests/api F63+F65 | 280 | ✅ PASS |
| **Total régression** | **1097** | **✅ PASS** |

---

## Blockers restants → F76b

| Item | Priority | Action |
|---|---|---|
| Rate limiting | P0 prod | Ajouter `slowapi` ou middleware throttle |
| Auth (APIKey minimum) | P0 prod | Ajouter `Depends(get_api_key)` sur routes sensibles |
| docker-compose.yml | P1 | Créer docker-compose.yml avec service obsidia-api |
| ROLLBACK_PLAN.md | P1 | Créer docs/architecture/ROLLBACK_PLAN.md |

---

## Ce que F76a ne couvre pas

| Item | Palier | Raison |
|---|---|---|
| Rate limiting | F76b | Demande choix de lib et impact sur deps |
| Auth (APIKey/Bearer) | F76b | Demande contrat clair sur routes protégées |
| HTTPS/TLS | Infra | Hors scope repo — géré au niveau reverse proxy |
| Secrets management | Infra | `.env` non commité, `.env.example` template disponible |
| Pack externe | F77 | Hors scope F76 |

---

_F76a — API Security Minimal | 2026-05-30 | Aucun commit/tag/push | KX108_ONLY_
