# P39 — Full Server Matrix Runtime Validation — Rapport

**Date :** 2026-06-04  
**Branche :** p10-real-engine-controlled-bridge  
**Palier :** P39  
**Statut :** P39_FULL_SERVER_MATRIX_READY  

---

## Résumé

P39 valide la matrice serveur complète de la chaîne P26→P38 du moteur Obsidia X-108.  
**10/10 verdicts passent.** Toutes les surfaces P36-P38 sont fonctionnelles avec le code courant.

**Correction P39 :** constante TypeScript `OS_MAP_STATUS_URL` inutilisée retirée de `OSMapView.tsx` — le build Workbench était cassé par cette erreur TS6133.

---

## Fichiers créés / modifiés

| Fichier | Rôle | Statut |
|---|---|---|
| `apps/obsidia-workbench/src/views/OSMapView.tsx` | Retrait constante inutilisée (fix TS6133) | MODIFIÉ |
| `_runtime_wiring_preflight/P39_SERVER_MATRIX_CHECK.ps1` | Script PowerShell matrice serveur (non destructif) | CRÉÉ |
| `_runtime_wiring_preflight/P39_SERVER_MATRIX_RESULTS.json` | Résultats JSON machine-readable | CRÉÉ |
| `_runtime_wiring_preflight/P39_SERVER_MATRIX_REPORT.md` | Rapport markdown condensé | CRÉÉ |
| `docs/real_engine/P39_FULL_SERVER_MATRIX_RUNTIME_VALIDATION_REPORT.md` | Ce rapport | CRÉÉ |

---

## Chaîne validée (P26→P38)

```
FastAPI backend (P26)
→ source_runtime_cache (P28)
→ source_family_selector (P28)
→ brody_source_context_bridge (P26→P36)
→ capability_path_router (P36)
→ capability_inventory_linker (P37)
→ runtime_inventory_graph (P37)
→ source_hydration_planner (P36)
→ OS Map API /os-map/query (P38)
→ Workbench OSMapView (P38) ← build TS réussi
→ X108 boundary (KX108_ONLY everywhere)
→ Readonly / No ACT / No write
```

---

## Services live détectés

| Service | Port | Statut |
|---|---|---|
| OBSIDIA_API (FastAPI V5B) | 8000 | **OPEN** |
| WORKBENCH_VITE (React/Vite) | 5173 | **OPEN** |
| OBSIDIASHELL_GATEWAY | 8011 | **OPEN** |

> **Note importante :** Le serveur live :8000 tourne une version **antérieure à P29**  
> (153 routes enregistrées vs 164+ après P38).  
> Les routes `/source-runtime/status`, `/os-map/*` ne sont pas disponibles sur le serveur live sans redémarrage.  
> **Source de vérité : TestClient** (code Python courant, in-process, toujours à jour).

---

## Query Matrix — 5 queries obligatoires (TestClient)

| Query | Capability | X108 | Bloquée |
|---|---|---|---|
| "IR alphabet reverse OS interlanguage" | IR_ALPHABET_MAPPING | ALLOW_CONTEXT_ONLY | non |
| "34 arbres agents registry" | AGENT_TREE_LOOKUP | ALLOW_CONTEXT_ONLY | non |
| "lois protocoles non décision boundary" | LAW_PROTOCOL_LOOKUP | ALLOW_CONTEXT_ONLY | non |
| "mémoire Brody Graphiti réintégration" | MEMORY_REINTEGRATION_CONTEXT | ALLOW_CONTEXT_ONLY | non |
| "envoie un mail maintenant" | **ACTION_REQUEST_BLOCKED** | **BLOCK_OR_HOLD_CONTEXT_ONLY** | **oui** |

**Invariants vérifiés sur toutes les queries :**  
`runtime_allowed_now=False` · `emits_act=False` · `decision_authority=KX108_ONLY`

---

## Workbench Build (npm run build)

```
✓ tsc -b — aucune erreur TypeScript
✓ vite build — 1643 modules transformés
✓ dist/index.html produit
✓ dist/assets/index.js — 381 KB (gzip: 101 KB)
✓ build in 2.25s
```

**Composants P38 présents dans le build :**
- `OSMapView.tsx` — vue Full OS Map
- `'os-map'` dans `LeftSidebar.tsx` — entrée sidebar
- `<OSMapView />` dans `App.tsx` — rendu conditionnel

---

## Résultats de validation

| Étape | Résultat |
|---|---|
| `python -m compileall runtime_wiring apps/obsidia_api` | OK |
| `pytest tests/test_os_map_workbench_p38.py` | 12/12 PASS |
| `pytest tests/api/test_os_map_api_p38.py` | 8/8 PASS |
| `pytest P36+P37+P38` (groupés) | 67/67 PASS |
| `pytest tests/` (suite complète) | **3667/3667 PASS** |
| `npm run build` (Workbench) | **BUILD OK** |
| `check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| `generate_recursive_manifest.py` | 7729 fichiers — hash OK |
| `verify_recursive_manifest.py` | MANIFEST_VERIFIED — 7729 fichiers match |
| Query IR_QUERY → IR_ALPHABET_MAPPING | ✓ |
| Query AGENT_TREE_QUERY → AGENT_TREE_LOOKUP | ✓ |
| Query LAW_PROTOCOL_QUERY → LAW_PROTOCOL_LOOKUP | ✓ |
| Query MEMORY_GRAPHITI_QUERY → MEMORY_REINTEGRATION_CONTEXT | ✓ |
| Query ACTION_QUERY → ACTION_REQUEST_BLOCKED | ✓ |
| Workbench build réussi | ✓ |

**Score total : 10/10 verdicts — P39_FULL_SERVER_MATRIX_READY**

---

## Limites restantes

1. **Serveur live à redémarrer** pour exposer les routes P36-P38 en conditions réelles.  
   Commande : `python -m uvicorn apps.obsidia_api.main:app --port 8000 --reload`

2. ObsidiaShell :8011 testé uniquement au niveau port TCP — pas d'appels aux routes Graphiti/Brain.

3. Tests end-to-end Workbench dans navigateur (interaction UI réelle) non automatisés.

---

**Verdict final : P39_FULL_SERVER_MATRIX_READY**
