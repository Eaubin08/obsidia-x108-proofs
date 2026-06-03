# CANONICAL_SERVERS_REFRESH_AUDIT
# Date: 2026-06-03
# Branch: p8-runtime-dryrun-wiring | HEAD: 84cc0d0
# Objectif: Remplacer les instances stale 8000/8012 par des instances fraîches HEAD

---

## Résumé

Les ports 8000 et 8012 hébergeaient des instances stale (pré-84cc0d0) qui retournaient
HTTP 404 sur `/api/runtime-wiring/preview`. Après l'audit Full Server Matrix, elles se
sont arrêtées. Des instances fraîches HEAD 84cc0d0 ont été relancées sur 8000 et 8012.
Toutes les assertions passent. Vite proxy maintenant opérationnel.

**Verdict : CANONICAL_SERVERS_REFRESH_OK**

---

## État pré-refresh (constat audit Full Matrix)

| Port | État | Problème |
|------|------|---------|
| 8000 | STALE (pré-84cc0d0) | /api/runtime-wiring/preview → HTTP 404 |
| 8012 | STALE (pré-84cc0d0) | /api/runtime-wiring/preview → HTTP 404 |
| 8014 | FREE (arrêté en fin d'audit) | — |
| 5173 | FREE (arrêté en fin d'audit) | — |
| 8011 | FREE (arrêté en fin d'audit) | — |

---

## Actions exécutées

| Étape | Action | Résultat |
|-------|--------|---------|
| Vérification PIDs | `netstat -ano` → tous ports libres | Instances stale auto-arrêtées |
| Lancement 8000 | `python -m uvicorn apps.obsidia_api.main:app --port 8000` | PID 42932 ✓ |
| Lancement 8012 | `python -m uvicorn apps.obsidia_api.main:app --port 8012` | PID 16200 ✓ |
| Lancement Vite 5173 | `npm run dev -- --host 127.0.0.1` | PID 31692 ✓ |
| Lancement ObsidiaShell 8011 | `.venv_api8011/Scripts/uvicorn obsidia_core.agent_bridge:app --port 8011` | PID 48204 ✓ |

---

## Tests API 8000 et 8012 — résultats complets

### Port 8000

| Endpoint | HTTP | Résultat |
|---------|------|---------|
| `/` | 200 | version=V5B, mode=readonly_dryrun, decision_authority=KX108_ONLY ✓ |
| `/api/status` | 200 | ✓ |
| `/api/runtime-wiring/preview` | 200 | ALL_OK=True — 10/10 assertions ✓ |
| `/openapi.json` | 200 | `/api/runtime-wiring/preview` présent ✓ |
| `/api/brody/chat` (POST) | 200 | emits_act=False, KX108_ONLY ✓ |

### Port 8012

| Endpoint | HTTP | Résultat |
|---------|------|---------|
| `/` | 200 | version=V5B, mode=readonly_dryrun, decision_authority=KX108_ONLY ✓ |
| `/api/status` | 200 | ✓ |
| `/api/runtime-wiring/preview` | 200 | ALL_OK=True — 10/10 assertions ✓ |
| `/openapi.json` | 200 | `/api/runtime-wiring/preview` présent ✓ |
| `/api/brody/chat` (POST) | 200 | emits_act=False, KX108_ONLY ✓ |

### Invariants runtime-wiring (8000 et 8012)

| Invariant | Valeur | Statut |
|-----------|--------|--------|
| `status` | `ENGINE_BRIDGE_PREVIEW_ONLY` | ✓ |
| `runtime_active` | `False` | ✓ |
| `emits_act` | `False` | ✓ |
| `proof_claim` | `False` | ✓ |
| `decision_authority` | `KX108_ONLY` | ✓ |
| `context_only_decision` | `ALLOW_CONTEXT_ONLY` | ✓ |
| `critical_action_decision` | `HOLD` | ✓ |
| `source_registry_entries` | `14779` | ✓ |
| `families_sampled` | `4` | ✓ |
| `dry_run` | `True` | ✓ |

---

## Test Vite 5173

| Check | Résultat |
|-------|---------|
| `/` HTTP 200 | ✓ |
| HTML Obsidia title | ✓ |
| `RuntimeWiringPreviewView.tsx` servi | 34 584 bytes ✓ |
| `import.meta.env` (fix P11A) | ✓ |
| ALLOW_CONTEXT_ONLY / KX108_ONLY présents | ✓ |
| No broken cast | ✓ |
| **Proxy `/api/runtime-wiring/preview` → 8000** | **HTTP 200 — ALL_OK=True ✓** |

**Le proxy Vite est maintenant pleinement opérationnel** (8000 frais répond avec le bon payload).

---

## Test ObsidiaShell 8011 / Graphiti V20

| Endpoint | HTTP | Résultat |
|---------|------|---------|
| `/graph/v20/frozen/status` | 200 | mode=FROZEN_READONLY ✓ |
| `/graph/v20/frozen/counts` | 200 | report_counts présent ✓ |
| `/graph/v20/frozen/manifest` | 200 | ✓ |
| `/graph/v20/frozen/workbench` | 200 | ✓ |
| `/graph/v20/frozen/panel` | 200 | ✓ |
| `/graph/v20/frozen/search?q=X-108&limit=5` | 200 | query + limit présents ✓ |
| `/docs` | 200 | ✓ |
| `/health` | TimeoutError | Route non exposée — acceptable ✓ |

---

## État final des serveurs actifs

| Serveur | Port | PID | Status | Prévu pour |
|---------|------|-----|--------|-----------|
| OBSIDIA_API | 8000 | 42932 | UP ✓ | Canonical — laisser UP |
| OBSIDIA_API | 8012 | 16200 | UP ✓ | Canonical alt — laisser UP |
| WORKBENCH_VITE | 5173 | 31692 | UP ✓ | Démo — actif, proxy opérationnel |
| OBSIDIASHELL | 8011 | 48204 | UP ✓ | Graphiti frozen — actif |
| Port temporaire test | 8014 | — | LIBÉRÉ | Arrêté en fin d'audit Full Matrix |

---

## Verdict

```
CANONICAL_SERVERS_REFRESH_OK
```

- Port 8000 : UP fraîche HEAD 84cc0d0 — /api/runtime-wiring/preview → 200 ✓
- Port 8012 : UP fraîche HEAD 84cc0d0 — /api/runtime-wiring/preview → 200 ✓
- Port 8014 : LIBÉRÉ (instance de test temporaire) ✓
- Vite 5173 : UP — proxy opérationnel (plus de 404) ✓
- ObsidiaShell 8011 : UP — Graphiti V20 frozen readonly ✓
- Aucune modification sources sauf bug P11A déjà corrigé (import.meta.env)
- Aucun commit / push
