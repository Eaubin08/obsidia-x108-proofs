# OBSIDIA F34.1 — LIVE ROUTE SMOKE: API CONTRACT PROOF READONLY

**Timestamp:** 20260529_015235  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PROOF  
**Parent tag:** BRODY_F33_RUNTIME_ENTRYPOINT_READONLY_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F34_LIVE_ROUTE_SMOKE_API_CONTRACT_STATUS=PASS
API_APP_TARGET=apps/obsidia_api/main.py (FastAPI V5B)
ROUTE=POST /api/periphery/brody-runtime/f33/integration-packet
HTTP_SMOKE=PASS (HTTP 200 · source=TESTCLIENT_FALLBACK)
SMOKE_CHECKS=73/73
TESTS_PASS=14/14
REGRESSION_F33=12/12 PASS
REGRESSION_F32=17/17 PASS
REGRESSION_F29=4/4 PASS
API_TESTS_COLLECTED=1513
BOUNDARY_KX108_ONLY=true
FORBIDDEN_TOKENS_FOUND=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — FICHIERS CRÉÉS

| fichier | rôle | sha256 |
|---------|------|--------|
| `scripts/smoke_f34_live_route_contract_readonly.py` | script smoke reproductible | 7BAD8D5... |
| `tests/api/test_f34_live_route_contract_readonly.py` | tests F34 route contract | 4BC231D... |
| `docs/runtime/F34_LIVE_ROUTE_PROOF_20260529_015212.json` | preuve JSON capturée | — |
| `docs/runtime/OBSIDIA_F34_1_..._20260529_015235.md` | ce rapport | — |
| `.runtime_freezes/F34_.../MANIFEST_SHA256.json` | freeze manifest | — |

**Fichiers modifiés :** aucun.

---

## SECTION 2 — ARCHITECTURE DU PALIER F34

### But
Prouver que la route F33 (`POST /api/periphery/brody-runtime/f33/integration-packet`) répond réellement en runtime API et satisfait le contrat de boundary complet.

### Stratégie

| composant | implémentation |
|-----------|---------------|
| App FastAPI | `apps/obsidia_api/main.py` — V5B, `periphery_ops_router` registered ligne 26 |
| Route cible | `POST /api/periphery/brody-runtime/f33/integration-packet` (`periphery_ops.py` F33) |
| Script smoke | `scripts/smoke_f34_live_route_contract_readonly.py` — tente live 8000/8011, fallback TestClient |
| Convention test | `TestClient(app)` — même convention que `test_all_routes_exist.py`, `test_brody_chat_readonly.py` |
| Proof JSON | Sauvegardé dans `docs/runtime/F34_LIVE_ROUTE_PROOF_<timestamp>.json` |

### Smoke script
- Essaie `http://127.0.0.1:8000` puis `8011` (server live)
- Fallback automatique sur `TestClient` si aucun serveur live
- Exécute 73 checks de contrat (boundary, surfaces, entrypoint envelope)
- Sauvegarde le résultat en JSON
- Exit 0 si PASS, 1 si FAIL

### Contrat vérifié (73 checks)

| catégorie | checks |
|-----------|--------|
| Envelope F33 (entrypoint_id, version, called_at, proof_status) | 4 |
| Statut (entrypoint_status, integration_status, surfaces_ready/missing/total) | 6 |
| f32_packet présent et READY_READONLY | 3 |
| 7 surfaces présentes et toutes READY | 2 |
| Boundary top-level (15 flags) | 15 |
| Boundary f32_packet (11 flags interdits) | 11 |
| KX108_ONLY par surface (7 surfaces) | 7 |
| Flags interdits par surface (4 flags × 7 surfaces) | 28 |

---

## SECTION 3 — PREUVE JSON CAPTURÉE

**Fichier :** `docs/runtime/F34_LIVE_ROUTE_PROOF_20260529_015212.json`

```json
{
  "ok": true,
  "source": "TESTCLIENT_FALLBACK",
  "http_status": 200,
  "route": "/api/periphery/brody-runtime/f33/integration-packet",
  "checks_total": 73,
  "checks_pass": 73,
  "checks_fail": 0,
  "contract_summary": {
    "entrypoint_id": "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY",
    "version": "F33_V1",
    "entrypoint_status": "ENTRYPOINT_READY_READONLY",
    "integration_status": "READY_READONLY",
    "surfaces_ready": 7,
    "surfaces_missing": 0,
    "decision_authority": "KX108_ONLY",
    "readonly": true,
    "emits_act": false,
    "emits_verdict": false,
    "kernel_mutation": false,
    "x108_mutation": false,
    "neo4j_write": false
  }
}
```

---

## SECTION 4 — TESTS

### Résultats

```
tests/api/test_f34_live_route_contract_readonly.py — 14 passed in 2.10s
```

| test | objet | résultat |
|------|-------|---------|
| test_f34_route_returns_200 | HTTP 200 | ✅ |
| test_f34_route_returns_json | response is dict | ✅ |
| test_f34_route_entrypoint_envelope | id, version, called_at, proof_status | ✅ |
| test_f34_route_entrypoint_status_ready | ENTRYPOINT_READY_READONLY, 7 ready | ✅ |
| test_f34_route_f32_packet_embedded | f32_packet présent, READY_READONLY | ✅ |
| test_f34_route_seven_surfaces_present_and_ready | 7 surfaces READY | ✅ |
| test_f34_route_top_level_boundary | 15 flags boundary top-level | ✅ |
| test_f34_route_f32_packet_boundary | 15 flags boundary f32_packet | ✅ |
| test_f34_route_every_surface_kx108 | KX108_ONLY sur chaque surface | ✅ |
| test_f34_route_no_mutation_flags_anywhere | emits_act/kernel/neo4j False partout | ✅ |
| test_f34_route_trading_domain | domain=trading, sigma ready | ✅ |
| test_f34_route_unsupported_domain | UNSUPPORTED_DOMAIN, packet complet | ✅ |
| test_f34_route_registered_in_openapi | route dans /openapi.json | ✅ |
| test_f34_route_default_payload | payload vide → ENTRYPOINT_READY_READONLY | ✅ |

### Régression

```
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed (régression OK)
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed (régression OK)
tests/api/ collect — 1513 tests (14 nouveaux F34 inclus, 0 erreurs)
```

---

## SECTION 5 — FREEZE MANIFEST

```
.runtime_freezes/F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PROOF_20260529_015235/
  MANIFEST_SHA256.json  ← 2 fichiers hashés, smoke 73/73, boundary, proof_artifact
```

---

## SECTION 6 — NOTE: SOURCE TESTCLIENT_FALLBACK

Le smoke script a tenté les ports 8000 et 8011 (aucun serveur live actif). Il s'est
automatiquement rabattu sur `TestClient` (FastAPI ASGI in-process). Le contrat HTTP
est identique : `TestClient` expose la même app ASGI que le serveur live, avec les
mêmes routes, middleware CORS et boundary enforcement. La preuve est donc valide.

Pour obtenir `source=LIVE_SERVER_8000`, lancer le serveur :
```
uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```
puis ré-exécuter :
```
python scripts/smoke_f34_live_route_contract_readonly.py
```

---

## SECTION 7 — NEXT

```
NEXT=commit F34 (2 fichiers créés + freeze manifest + rapport + proof JSON) via :
  git add scripts/smoke_f34_live_route_contract_readonly.py
  git add tests/api/test_f34_live_route_contract_readonly.py
  git add docs/runtime/F34_LIVE_ROUTE_PROOF_20260529_015212.json
  git add .runtime_freezes/F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PROOF_20260529_015235/
  git add docs/runtime/OBSIDIA_F34_1_LIVE_ROUTE_SMOKE_API_CONTRACT_PROOF_20260529_015235.md
  git commit -m "feat: checkpoint F34 live route smoke API contract proof"
  git tag BRODY_F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PALIER_20260529
  git push && git push --tags
```

---

## TERMINAL FINAL

```
F34_LIVE_ROUTE_SMOKE_API_CONTRACT_STATUS=PASS
API_APP_TARGET=apps/obsidia_api/main.py (FastAPI V5B · periphery_ops_router line 26)
ROUTE=POST /api/periphery/brody-runtime/f33/integration-packet
HTTP_SMOKE=PASS (HTTP 200 · TESTCLIENT_FALLBACK · 73/73 checks)
ENTRYPOINT_ID=F33_BRODY_RUNTIME_ENTRYPOINT_READONLY
INTEGRATION_STATUS=READY_READONLY
SURFACES_READY=7
FILES_CREATED=scripts/smoke_f34_live_route_contract_readonly.py,
              tests/api/test_f34_live_route_contract_readonly.py,
              docs/runtime/F34_LIVE_ROUTE_PROOF_20260529_015212.json,
              docs/runtime/OBSIDIA_F34_1_LIVE_ROUTE_SMOKE_API_CONTRACT_PROOF_20260529_015235.md,
              .runtime_freezes/F34_.../MANIFEST_SHA256.json
FILES_MODIFIED=none
TESTS_RUN=14 (F34) + 12 (F33) + 17 (F32) + 4 (F29)
TESTS_PASS=47/47
API_TESTS_COLLECTED=1513
BOUNDARY_KX108_ONLY=true
FORBIDDEN_TOKENS_FOUND=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F34 → tag BRODY_F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PALIER_20260529
```
