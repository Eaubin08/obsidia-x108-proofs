# OBSIDIA F34B — TRUE LIVE UVICORN SERVER SMOKE

**Timestamp:** 20260529_024438  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE  
**Parent tag:** BRODY_F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=9010
ROUTE=POST /api/periphery/brody-runtime/f33/integration-packet
HTTP_STATUS=200
SOURCE_IN_RESPONSE=REAL_BACKEND
SMOKE_CHECKS=73/73 PASS
TESTS_PASS=47/47
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

| fichier | rôle |
|---------|------|
| `docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json` | preuve JSON capturée (562 KB) |
| `docs/runtime/OBSIDIA_F34B_..._20260529_024438.md` | ce rapport |
| `.runtime_freezes/F34B_.../MANIFEST_SHA256.json` | freeze manifest |

**Fichiers modifiés :** aucun.

---

## SECTION 2 — CONTEXTE

### Situation port 8000
Un serveur Obsidia V5B pré-F33 occupait le port 8000 (134 routes, sans
`/api/periphery/brody-runtime/f33/integration-packet`). Ce serveur a été
détecté et ignoré.

### Stratégie F34B
1. Détection du port 8000 occupé (`port_check → OCCUPIED`)
2. Lancement d'un nouveau `uvicorn` sur port **9010** (libre), depuis le HEAD actuel `d6cb713`
3. Attente de démarrage via polling HTTP (`/` health check — prêt dès la 1ère seconde)
4. Appel `POST http://127.0.0.1:9010/api/periphery/brody-runtime/f33/integration-packet`
5. Vérification que la route apparaît dans `/openapi.json` (135 routes totales)
6. Capture de la réponse JSON complète (562 KB)
7. Arrêt du processus uvicorn (PID 23208)

**Preuve de live :** `source=REAL_BACKEND` dans la réponse (vs `TESTCLIENT_FALLBACK` de F34).

---

## SECTION 3 — RÉSULTATS DU SMOKE (73/73)

### Réponse live capturée

```json
{
  "entrypoint_id": "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY",
  "version": "F33_V1",
  "called_at": "2026-05-29T02:43:31.230015+00:00",
  "entrypoint_status": "ENTRYPOINT_READY_READONLY",
  "integration_status": "READY_READONLY",
  "surfaces_ready": 7,
  "surfaces_missing": 0,
  "surfaces_total": 7,
  "decision_authority": "KX108_ONLY",
  "readonly": true,
  "emits_act": false,
  "emits_verdict": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "proof_status": "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN",
  "source": "REAL_BACKEND"
}
```

### Checks par catégorie

| catégorie | checks | résultat |
|-----------|--------|---------|
| HTTP 200 + envelope F33 | 7 | ✅ |
| F32 packet + 7 surfaces READY | 4 | ✅ |
| Boundary top-level (15 flags) | 15 | ✅ |
| Boundary f32_packet (11 flags) | 11 | ✅ |
| KX108_ONLY par surface (7) | 7 | ✅ |
| Flags mutation par surface (4×7) | 28 | ✅ |
| **TOTAL** | **73** | **73/73 ✅** |

### Surfaces confirmées READY

| surface | statut |
|---------|--------|
| `sigma_dispatcher` | READY ✅ |
| `tree_signal_packet` | READY ✅ |
| `monitoring_adapters` | READY ✅ |
| `operator_view_packet` | READY ✅ |
| `brody_runtime_context` | READY ✅ |
| `workflow_governance_readonly` | READY ✅ |
| `neo4j_guide_bridge` | READY ✅ |

---

## SECTION 4 — PREUVE JSON

**Fichier :** `docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json`  
**SHA256 :** `20A27188043C198CEDD66819196CD9C67041E0B97E46CEC963CA11EDEF472997`  
**Taille :** 562 007 bytes  
**called_at :** `2026-05-29T02:43:31.230015+00:00`  
**source :** `REAL_BACKEND` ← confirm live HTTP, pas TestClient

---

## SECTION 5 — TESTS DE RÉGRESSION

```
tests/api/test_f34_live_route_contract_readonly.py — 14 passed (régression OK)
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed (régression OK)
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed (régression OK)
TOTAL=47/47 PASS
```

---

## SECTION 6 — NOTE: PORT 8000 PRÉ-F33

Le serveur occupant le port 8000 est une version antérieure à F33 (134 routes).
La route `/api/periphery/brody-runtime/f33/integration-packet` est absente de ce serveur.
**Ce serveur n'a pas été modifié.** F34B a lancé un processus uvicorn indépendant
sur le port 9010 depuis le HEAD actuel et l'a arrêté après la capture.

Pour que le port 8000 soit à jour (F33+), il faut redémarrer le serveur existant
depuis le répertoire courant.

---

## SECTION 7 — NEXT

```
NEXT=commit F34B (proof JSON + manifest + rapport) via :
  git add docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json
  git add .runtime_freezes/F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438/
  git add docs/runtime/OBSIDIA_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438.md
  git commit -m "test: checkpoint F34B true live uvicorn server smoke proof"
  git tag BRODY_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_PALIER_20260529
  git push && git push --tags
```

---

## TERMINAL FINAL

```
F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=9010
ROUTE=POST /api/periphery/brody-runtime/f33/integration-packet
HTTP_STATUS=200
SOURCE_IN_RESPONSE=REAL_BACKEND
SMOKE_CHECKS=73/73
BOUNDARY_KX108_ONLY=true
FORBIDDEN_TOKENS_FOUND=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json,
              docs/runtime/OBSIDIA_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438.md,
              .runtime_freezes/F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438/MANIFEST_SHA256.json
FILES_MODIFIED=none
TESTS_RUN=14 (F34) + 12 (F33) + 17 (F32) + 4 (F29)
TESTS_PASS=47/47
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F34B → tag BRODY_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_PALIER_20260529
```
