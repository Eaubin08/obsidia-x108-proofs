# F53 — Bus/Bridge : Décision d'implémentation F54

**Artifact:** `OBSIDIA_F53_BUS_BRIDGE_F54_IMPLEMENTATION_DECISION`  
**Palier:** F53  
**Date:** 2026-05-29  

---

## Décision

F53 confirme que bus/bridge est une surface architecturale réelle, définie, et implémentable.

**F54 = F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION**

F54 implémentera `GET /bus/stats` et `GET /bus/bridge`. Ni plus, ni moins.

---

## Périmètre F54 (minimal, sans dérive)

### Ce que F54 DOIT faire

| Action | Fichier | Type |
|--------|---------|------|
| Créer le state aggregator | `apps/obsidia_api/bus/state_aggregator.py` | Nouveau fichier |
| Créer le router bus | `apps/obsidia_api/routes/bus.py` | Nouveau fichier |
| Ajouter `include_router(bus_router)` | `apps/obsidia_api/main.py` | Modification minimale |
| Réactiver les tests quarantinés | `tests/api/test_output_envelope_bus_stats.py` | Suppression du pytestmark skip |
| Réactiver les tests quarantinés | `tests/api/test_output_envelope_bus_bridge.py` | Suppression du pytestmark skip |

### Ce que F54 NE DOIT PAS faire

- Implémenter `POST /bus/signal` (F55+)
- Modifier `output_envelope.py` (déjà correct)
- Modifier `safe_response.py` (déjà correct)
- Ajouter de la logique de décision
- Écrire dans Neo4j, Graphiti, ou la mémoire
- Muter le kernel ou X108

---

## Architecture cible F54

```
apps/obsidia_api/
├── bus/
│   ├── __init__.py
│   └── state_aggregator.py   ← NEW (F54)
│       - aggregate_runtime_state()
│       - aggregate_proof_state()
│       - aggregate_audit_state()
│       - aggregate_route_state()
│       - aggregate_readiness_state()
│       - aggregate_debt_state()
│       - build_bus_stats_payload()
│       - build_bus_bridge_payload()
├── output_envelope.py         ← EXISTS (unchanged)
├── routes/
│   └── bus.py                ← NEW (F54)
│       GET /bus/stats  → build_output_envelope(build_bus_stats_payload(), ...)
│       GET /bus/bridge → build_output_envelope(build_bus_bridge_payload(), ...)
└── main.py                    ← MODIFIED: + include_router(bus_router)
```

---

## Contrat de réponse minimum F54

### GET /bus/stats (default mode)

```json
{
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "readonly": true,
  "source": "OBSIDIA_API",
  "route": "/bus/stats",
  "timestamp": "...",
  "compact": false,
  "debug": false,
  "status": "OK",
  "runtime_state": { "active_routes": 120, "uvicorn_status": "UP" },
  "proof_state": { "last_palier": "F54", "current_head": "..." },
  "audit_state": { "last_audit_status": "PASS", "baseline_result": "103/103" },
  "route_state": { "route_count": 120, "boundary_coverage": "HIGH" },
  "readiness_state": { "demo_ready": true, "baseline_passing": true },
  "debt_state": { "open_debts": [], "quarantined_tests": 0 },
  "emits_act": false,
  "emits_verdict": false,
  "kernel_mutation": false,
  "neo4j_write": false,
  "brody_decision": false
}
```

---

## Critères de succès F54

| Critère | Mesure |
|---------|--------|
| `GET /bus/stats` → HTTP 200 | pytest |
| `GET /bus/bridge` → HTTP 200 | pytest |
| Tous les flags boundary présents | test_bus_stats_boundary_all_flags |
| 46 tests quarantinés F52 → PASS | réactivation complète |
| F50 baseline toujours PASS | régression check |
| Aucune route existante cassée | full route smoke |
| `decision_authority=KX108_ONLY` sur toutes les réponses bus | test |
| Compact mode : deep fields absents | test_bus_stats_compact_mode |
| Debug mode : tous les champs présents | test_bus_stats_debug_mode |

---

## POST /bus/signal — F55+ seulement

`POST /bus/signal` n'entre PAS dans F54. Sa logique d'ingestion de signaux externes est plus complexe et mérite un palier dédié (F55) après validation complète de F54.

---

## Risque F54

**FAIBLE.** L'implémentation est **uniquement additive** :
- `output_envelope.py` existe et est correct
- `safe_response.py` et `_SOVEREIGNTY_PROTECTED` restent inchangés
- Les 8 routes F50 ne sont pas touchées
- La seule modification sur un fichier existant = `main.py` (1 ligne `include_router`)

---

*F53 · DÉCISION F54 · PLAN ONLY · KX108_ONLY · 2026-05-29*
