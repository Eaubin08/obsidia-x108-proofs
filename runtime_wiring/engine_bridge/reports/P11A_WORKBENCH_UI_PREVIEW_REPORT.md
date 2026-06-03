# P11A_WORKBENCH_UI_PREVIEW_REPORT

**Status:** P11A_WORKBENCH_UI_PREVIEW_READY  
**Branche:** p8-runtime-dryrun-wiring  
**Phase:** P11A  
**Date:** 2026-06-03

---

## Summary

Surface UI preview complète pour le runtime wiring dry-run.  
Option 1 : React view `RuntimeWiringPreviewView.tsx` + HTML standalone.  
92 tests passés au total. API + UI testés sur serveurs locaux.

---

## Fichiers créés / modifiés

| Fichier | Action |
|---------|--------|
| `apps/obsidia-workbench/src/views/RuntimeWiringPreviewView.tsx` | **Créé** — vue React |
| `apps/obsidia-workbench/runtime_wiring_preview.html` | **Créé** — HTML standalone |
| `apps/obsidia-workbench/src/components/LeftSidebar.tsx` | **Modifié** — ViewId + groupe WIRING |
| `apps/obsidia-workbench/src/App.tsx` | **Modifié** — import + rendu vue |
| `apps/obsidia-workbench/vite.config.ts` | **Modifié** — proxy `/api/runtime-wiring` |
| `tests/test_workbench_runtime_wiring_preview_p11a.py` | **Créé** — 17 tests |
| `runtime_wiring/engine_bridge/reports/P11A_WORKBENCH_UI_PREVIEW_REPORT.md` | **Créé** — ce fichier |
| `_runtime_wiring_preflight/P11A_WORKBENCH_UI_PREVIEW_RESULTS.md` | **Créé** |
| `_runtime_wiring_preflight/P11A_SERVER_LOGS_SUMMARY.md` | **Créé** |
| `_runtime_wiring_preflight/P11A_API_RESPONSE.json` | **Créé** |
| `_runtime_wiring_preflight/P11A_UI_RESPONSE.html` | **Créé** |

---

## Stratégie d'intégration

**Option 1 choisie** — surface duale :
1. `RuntimeWiringPreviewView.tsx` — composant React natif dans le workbench, accessible depuis la sidebar via le groupe **WIRING / RT WIRING**
2. `runtime_wiring_preview.html` — page standalone, testable immédiatement via `python -m http.server`, sans build step

**Proxy vite** — `/api/runtime-wiring` → `http://127.0.0.1:8000` (configurable via env)  
**React ENGINE_BASE** — `VITE_ENGINE_API_BASE` env var, défaut `http://127.0.0.1:8000`

---

## Blocs UI affichés

| Bloc | Données |
|------|---------|
| Source Registry | `source_registry_entries` (14 779), `families_sampled` (4), `context_packets_count` |
| Adapter Routing | `status` (ENGINE_BRIDGE_PREVIEW_ONLY), `dry_run` (true) |
| X108 Dry-Run Decisions | `context_only_decision` (ALLOW_CONTEXT_ONLY), `critical_action_decision` (HOLD), `decision_authority` (KX108_ONLY) |
| Engine Bridge Preview | `runtime_active` (false), `emits_act` (false), `proof_claim` (false) |
| Safety Locks | `zip_extraction`, `source_pack_import`, `world_action`, `memory_write`, `graph_write`, `packages_created` (all false) |

---

## Tests

```
python -m pytest tests/test_api_runtime_wiring_preview_p10d.py \
  tests/test_workbench_runtime_wiring_preview_p11a.py -q
34 passed in 1.10s

python -m pytest tests/ (P8C+P9B+P10C+P10D+P11A) -q
92 passed in 1.71s
```

| Suite | Tests | Résultat |
|-------|-------|---------|
| P8C | 14 | PASS ✓ |
| P9B | 20 | PASS ✓ |
| P10C | 24 | PASS ✓ |
| P10D | 17 | PASS ✓ |
| P11A | 17 | PASS ✓ |
| **Total** | **92** | **PASS ✓** |

---

## Tests serveurs locaux

| Serveur | Commande | Port | PID |
|---------|----------|------|-----|
| API (uvicorn) | `python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8013` | 8013 | 19268 |
| UI (http.server) | `python -m http.server 9090 --bind 127.0.0.1` | 9090 | 42328 |

**API — 10/10 assertions :**

| Clé | Valeur | Statut |
|-----|--------|--------|
| `status` | `ENGINE_BRIDGE_PREVIEW_ONLY` | ✓ |
| `runtime_active` | `false` | ✓ |
| `emits_act` | `false` | ✓ |
| `proof_claim` | `false` | ✓ |
| `decision_authority` | `KX108_ONLY` | ✓ |
| `context_only_decision` | `ALLOW_CONTEXT_ONLY` | ✓ |
| `critical_action_decision` | `HOLD` | ✓ |
| `source_registry_entries` | `14779` | ✓ |
| `families_sampled` | `4` | ✓ |
| `dry_run` | `true` | ✓ |

**UI HTML — 9/9 assertions :** KX108_ONLY ✓, No ACT ✓, runtime_active ✓, ALLOW_CONTEXT_ONLY ✓, HOLD ✓, zip_extraction ✓, source_pack_import ✓, /api/runtime-wiring/preview ✓, no runtime_active:true ✓

**Arrêt :** API (PID 19268) + UI (PID 42328) stoppés via PowerShell. Ports 8013 + 9090 libérés ✓

---

## Safety

| Invariant | Valeur |
|-----------|--------|
| No ACT | confirmé HTML + TSX |
| No runtime activation | `runtime_active=false` partout |
| No source_pack_import | 0 référence dans UI files |
| No zip extraction | `zip_extraction=false` affiché |
| No apps/periphery modification interdite | periphery/ intact |
| No packages | absent |

---

## Prochain chantier

**P11B — Commit Preflight** : lister fichiers P11A, préparer message commit, valider allowlist/blocklist, attendre validation humaine.
