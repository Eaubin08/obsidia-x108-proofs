# F54 — Bus/Bridge Minimal Route Implementation

**Artifact:** `OBSIDIA_F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION_20260529_213500`  
**Palier:** F54  
**Parent:** F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN  
**Status:** PASS  
**Parent tag:** BRODY_F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN_PALIER_20260529  
**Date:** 2026-05-29  

---

## Purpose

F54 implements `GET /bus/stats` and `GET /bus/bridge` — the minimal additive bus/bridge surface defined by F53.  
No decision logic added. No ACT emitted. No mutation. KX108_ONLY preserved.

---

## Scope

| Action | Fichier | Type |
|--------|---------|------|
| Créer le state aggregator | `apps/obsidia_api/bus/__init__.py` | Nouveau |
| Créer le state aggregator | `apps/obsidia_api/bus/state_aggregator.py` | Nouveau |
| Créer le router bus | `apps/obsidia_api/routes/bus.py` | Nouveau |
| Ajouter `include_router(bus_router)` | `apps/obsidia_api/main.py` | Modifié (1 import + 1 ligne) |
| Lever la quarantaine F52 | `tests/api/test_output_envelope_bus_stats.py` | Modifié |
| Lever la quarantaine F52 | `tests/api/test_output_envelope_bus_bridge.py` | Modifié |

**`output_envelope.py` et `safe_response.py` : inchangés.**

### Ce que F54 N'A PAS fait

- `POST /bus/signal` — **non implémenté** (F55+)
- Aucune logique de décision
- Aucune écriture Neo4j / Graphiti / mémoire
- Aucune mutation kernel ou X108

---

## Validation

### Tests bus (quarantaine F52 levée)

```
46/46 PASS
tests/api/test_output_envelope_bus_stats.py  — 23 tests
tests/api/test_output_envelope_bus_bridge.py — 23 tests
```

### OpenAPI

| Route | Présente |
|-------|----------|
| `GET /bus/stats` | true |
| `GET /bus/bridge` | true |
| `POST /bus/signal` | false (F55+) |

### F47 Scripts

| Script | Résultat |
|--------|----------|
| F47.1 — Sovereignty injection (13 flags) | **PASS** — KX108_ONLY préservé sur toutes les injections |
| F47.2 — Sanitizer (40 assertions) | **PASS** — 0 failure, 0 faux-positif |
| F47.3 — Nested scan (12 assertions) | **PASS** — champs internes préservés, cr.text sanitisé |

### Live smoke (127.0.0.1:8011)

| Route | HTTP | JSON | decision_authority | readonly | emits_act | kernel_mutation | neo4j_write |
|-------|------|------|--------------------|----------|-----------|-----------------|-------------|
| `GET /bus/stats` | 200 | OK | KX108_ONLY | true | false | false | false |
| `GET /bus/bridge` | 200 | OK | KX108_ONLY | true | false | false | false |

### Baseline Brody

```
2042 passed, 104 failed — PASS_WITH_PRE_EXISTING_FAILURES
```

**Classification des 104 failures :**  
Toutes pré-existantes à F54. Aucune failure causée par F54.

| Catégorie | Count | Classification |
|-----------|-------|----------------|
| test_brody_general_conversation_mode_readonly | 32 | Pré-existant — contrat brody chat |
| test_output_envelope_blockchain_fraud_check | 9 | Pré-existant |
| test_output_envelope_periphery_pipeline | 8 | Pré-existant |
| test_brody_semantic_advisory_utf8_runtime | 7 | Pré-existant |
| test_brody_payload_packetization | 7 | Pré-existant |
| test_recursive_manifest_schema | 6 | Pré-existant — manifests |
| test_bridge_connection | 6 | Pré-existant — periphery |
| test_recursive_manifest_excludes_forbidden | 5 | Pré-existant — manifests |
| test_http_audit_generated_output | 3 | Pré-existant |
| test_recursive_manifest_root_hash | 3 | Pré-existant — manifests |
| test_gencoin_bridge_brody_output | 3 | Pré-existant — integration |
| test_brody_routing_short_circuit_resolved | 3 | Pré-existant |
| Autres | 8 | Pré-existant brody API |

`legacy_root` exclu : `test_conscience.py` — erreur d'encodage UTF-8 source, pré-existante, hors-périmètre.

---

## Contrat de réponse live

### GET /bus/stats

```json
{
  "decision_authority": "KX108_ONLY",
  "emits_act": false,
  "emits_verdict": false,
  "memory_write": false,
  "graphiti_write": false,
  "neo4j_write": false,
  "kernel_mutation": false,
  "readonly": true,
  "source": "OBSIDIA_API",
  "route": "/bus/stats",
  "status": "OK",
  "compact": false,
  "debug": false,
  "runtime_state": {"python_version": "3.13.3", "app_available": true, "localhost_only": true},
  "proof_state": {"last_palier": "F54", "f54_minimal_ready": true},
  "audit_state": {"f51_debt_known": true, "f52_quarantine_done": true, "f53_contract_defined": true, "f54_routes_implemented": true},
  "readiness_state": {"bus_stats_route": true, "bus_bridge_route": true, "f54_minimal_ready": true},
  "debt_state": {"quarantined_tests_reactivated": true, "bus_signal_future": true, "post_bus_signal_status": "F55_plus"}
}
```

### GET /bus/bridge

```json
{
  "decision_authority": "KX108_ONLY",
  "emits_act": false,
  "emits_verdict": false,
  "memory_write": false,
  "graphiti_write": false,
  "neo4j_write": false,
  "kernel_mutation": false,
  "readonly": true,
  "source": "OBSIDIA_API",
  "route": "/bus/bridge",
  "status": "OK",
  "bridge_id": "f54-bus-bridge-readonly",
  "is_attached": true,
  "stats": {"emitted": 0, "dropped": 0},
  "memory_context_state": {"graphiti_status": "not_collected", "brody_context_status": "not_collected"},
  "external_signal_state": {"last_signal": "none", "signal_ingest_endpoint": "not_implemented", "post_bus_signal_status": "F55_plus"},
  "debt_state": {"quarantined_tests_reactivated": true, "bus_signal_future": true}
}
```

---

## Boundary Contract (F54)

| Flag | Valeur | Enforcement |
|------|--------|-------------|
| `decision_authority` | `KX108_ONLY` | `build_output_envelope()` |
| `allowed_to_decide` | `false` | Architectural invariant — aucune logique décisionnelle |
| `advisory_only` | `true` | Architectural invariant |
| `readonly` | `true` | `build_output_envelope()` |
| `emits_act` | `false` | `build_output_envelope()` |
| `emits_verdict` | `false` | `build_output_envelope()` |
| `kernel_mutation` | `false` | `build_output_envelope()` |
| `x108_mutation` | `false` | Architectural invariant |
| `neo4j_write` | `false` | `build_output_envelope()` |
| `brody_decision` | `false` | Architectural invariant |

---

## Git

```
COMMIT=NO
TAG=NO
PUSH=NO
STATUS=PENDING_USER_VALIDATION
```

---

## F55+ — Dette explicite

`POST /bus/signal` : non implémenté. Ingestion de signaux externes déférée à F55+.

---

*F54 · PASS · KX108_ONLY · 2026-05-29*
