# F55 — Bus/Signal : Décision d'implémentation F56

**Artifact:** `OBSIDIA_F55_F56_IMPLEMENTATION_DECISION`  
**Palier:** F55  
**Date:** 2026-05-30  

---

## Décision

F55 confirme que `POST /bus/signal` est une surface architecturale réelle, définie, et implémentable.

**F56 = F56_BUS_SIGNAL_MINIMAL_READONLY_ROUTE_IMPLEMENTATION**

F56 implémentera `POST /bus/signal`. Ni plus, ni moins.

---

## Périmètre F56 (minimal, sans dérive)

### Ce que F56 DOIT faire

| Action | Fichier | Type |
|--------|---------|------|
| Créer le modèle Pydantic d'entrée signal | `apps/obsidia_api/bus/signal_model.py` | Nouveau fichier |
| Créer le signal packager | `apps/obsidia_api/bus/signal_packager.py` | Nouveau fichier |
| Ajouter `POST /bus/signal` au bus router | `apps/obsidia_api/routes/bus.py` | Modification minimale |
| Créer les tests F56 | `tests/api/test_output_envelope_bus_signal.py` | Nouveau fichier |

### Ce que F56 NE DOIT PAS faire

- Modifier `main.py` (bus router déjà inclus depuis F54)
- Modifier `output_envelope.py` (déjà correct)
- Modifier `safe_response.py` (déjà correct)
- Modifier `state_aggregator.py` (bus/stats et bus/bridge non concernés)
- Implémenter du stockage persistant (option A — no storage — est le défaut)
- Ajouter de la logique de décision
- Écrire dans Neo4j, Graphiti, ou la mémoire
- Muter le kernel ou X108

---

## Architecture cible F56

```
apps/obsidia_api/
├── bus/
│   ├── __init__.py
│   ├── state_aggregator.py   ← EXISTS (unchanged)
│   ├── signal_model.py       ← NEW (F56)
│   │   - SignalInput (Pydantic BaseModel)
│   │   - SignalType (enum)
│   │   - RiskHint (enum)
│   │   - SignalObservationPacket (output dataclass)
│   └── signal_packager.py    ← NEW (F56)
│       - classify_signal_type(signal_type) → str
│       - build_signal_observation_packet(signal: SignalInput) → dict
│       - package_as_readonly_observation(signal: SignalInput) → dict
├── output_envelope.py         ← EXISTS (unchanged)
├── routes/
│   └── bus.py                ← MODIFIED: + POST /bus/signal
│       GET /bus/stats  → unchanged
│       GET /bus/bridge → unchanged
│       POST /bus/signal → build_output_envelope(
│                             package_as_readonly_observation(signal),
│                             route="/bus/signal"
│                          )
└── main.py                    ← UNCHANGED (bus_router already included)
```

---

## Contrat de réponse minimum F56

### POST /bus/signal (signal type: audit_request)

```json
{
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "advisory_only": true,
  "readonly": true,
  "emits_act": false,
  "emits_verdict": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "brody_decision": false,
  "memory_write": false,
  "graphiti_write": false,
  "source": "OBSIDIA_API",
  "route": "/bus/signal",
  "timestamp": "...",
  "compact": false,
  "debug": false,
  "status": "OK",
  "signal_observation_packet": {
    "signal_id": "...",
    "signal_type": "audit_request",
    "signal_origin": "CI_pipeline",
    "signal_timestamp": "...",
    "classified_signal_type": "audit_request",
    "accepted_as_observation": true,
    "interpreted_as_command": false,
    "routed_to_decision": false,
    "emitted_act": false,
    "mutation_performed": false,
    "signal_content_readonly": "...",
    "forbidden_tokens_found": false,
    "sanitized": true,
    "truncated": false,
    "risk_hint": "LOW",
    "source_layer": "CI",
    "correlation_id": null
  }
}
```

---

## Option de stockage F56 — Décision

**Option A retenue : aucun stockage.**

`POST /bus/signal` retourne le packet directement. Il ne stocke rien.

Conséquence : `GET /bus/bridge` continue à retourner `last_signal: "none"` après F56.

La population de `last_signal` dans `/bus/bridge` est une dette F57+ explicite, conditionnelle à l'acceptation de l'option B (mémoire volatile in-process).

| Option | F56 ? | Risque | Décision |
|--------|-------|--------|---------|
| A — No storage | OUI | FAIBLE | **RETENU** |
| B — In-memory volatile | NON (F57+) | FAIBLE si accepté | Déféré |
| C — Persistent log | NON | MOYEN | Nécessite approbation explicite |

---

## Critères de succès F56

| Critère | Mesure |
|---------|--------|
| `POST /bus/signal` → HTTP 200 | pytest |
| `signal_observation_packet` présent | test_bus_signal_audit_request_returns_observation |
| `accepted_as_observation=true` | systématique |
| `interpreted_as_command=false` | systématique |
| `routed_to_decision=false` | systématique |
| `emitted_act=false` | systématique |
| Tokens `ACT/DECIDE/VERDICT` neutralisés | test_bus_signal_*_token_neutralized |
| `decision_authority=KX108_ONLY` | systématique |
| Missing signal_type → HTTP 422 | test_bus_signal_missing_type_returns_422 |
| 46 tests F54 toujours PASS | régression |
| F47.1/F47.2/F47.3 toujours PASS | régression |
| GET /bus/stats non affecté | régression |
| GET /bus/bridge non affecté | régression |
| `main.py` non modifié | diff check |

---

## Risque F56

**FAIBLE.** L'implémentation est **minimalement additive** :
- `main.py` déjà configuré depuis F54 — aucune modification
- `routes/bus.py` : ajout d'un seul endpoint POST
- `output_envelope.py` et `safe_response.py` : inchangés
- Aucun stockage : option A retenue
- Les routes F54 (`GET /bus/stats`, `GET /bus/bridge`) ne sont pas touchées

---

## Dette explicite F57+

- `last_signal` dans `/bus/bridge` reste `"none"` après F56 (option A)
- Option B (mémoire volatile) : déféré à F57 avec approbation explicite
- Audit trail du signal : déféré à F57+

---

*F55 · DÉCISION F56 · PLAN ONLY · KX108_ONLY · 2026-05-30*
