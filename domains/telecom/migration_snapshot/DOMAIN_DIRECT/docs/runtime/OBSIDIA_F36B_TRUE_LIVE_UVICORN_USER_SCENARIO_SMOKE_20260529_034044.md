# OBSIDIA F36B — True Live Uvicorn User Scenario Smoke

**Timestamp:** 20260529_034044  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE  
**Parent tag:** BRODY_F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=8011
ROUTE=POST /api/periphery/brody-runtime/f36/user-scenario
HTTP_STATUS=200
SOURCE=LIVE_SERVER_8011
SCENARIO_ID=F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE
RUNTIME_ENTRYPOINT_READY=True
WORKBENCH_SURFACE_READY=True
SURFACES_READY=7
CONTROLLED_RESPONSE_PRESENT=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
SMOKE_CHECKS=61/61 PASS
TESTS_PASS=65/65
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — FICHIERS CRÉÉS

| fichier | rôle |
|---------|------|
| `scripts/smoke_f36b_true_live_uvicorn_user_scenario.py` | Script smoke F36B live uniquement (pas de TestClient fallback) |
| `docs/runtime/F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_034044.json` | Preuve JSON capturée live (1 350 bytes) |
| `docs/runtime/OBSIDIA_F36B_..._20260529_034044.md` | ce rapport |
| `.runtime_freezes/F36B_.../MANIFEST_SHA256.json` | freeze manifest |

**Fichiers modifiés :** aucun (F36, F35, F34, F33, F32 intacts).

---

## SECTION 2 — CONTEXTE

### Situation port 8000

Le port 8000 était occupé par une autre instance. F36B a détecté la collision et utilisé le port **8011** (libre).

### Stratégie F36B

1. `port_check` → port 8000 = OCCUPIED, port 8011 = FREE
2. Lancement de `uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011` via `Start-Process -PassThru -WindowStyle Hidden`
3. Polling HTTP sur `/` — serveur prêt dès la 1ère seconde (PID 21820)
4. Vérification `/openapi.json` → route F36 présente (`brody-runtime/f36/user-scenario` trouvée)
5. Appel `POST http://127.0.0.1:8011/api/periphery/brody-runtime/f36/user-scenario`
6. Capture JSON complète → 61/61 checks PASS
7. Arrêt du processus uvicorn
8. Suite de régression 65/65 PASS

**Preuve de live :** `source=LIVE_SERVER_8011` dans la réponse (vs `TESTCLIENT_FALLBACK` de F36).

---

## SECTION 3 — RÉPONSE LIVE CAPTURÉE

```json
{
  "scenario_id": "F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE",
  "version": "F36_V1",
  "mode": "READONLY",
  "user_input": "Je veux analyser une transaction bancaire avant paiement.",
  "domain": "bank",
  "runtime_entrypoint": {
    "entrypoint_id": "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY",
    "integration_status": "READY_READONLY",
    "entrypoint_status": "ENTRYPOINT_READY_READONLY",
    "surfaces_ready": 7,
    "surfaces_missing": 0,
    "surfaces_total": 7
  },
  "workbench": {
    "surface_id": "F36_WORKBENCH_SUMMARY",
    "connector_status": "READY_READONLY",
    "surfaces_ready": 7,
    "integration_status": "READY_READONLY",
    "f35_c03_available": true
  },
  "controlled_response": {
    "response_kind": "contextual_explanation_only",
    "can_answer": true,
    "can_decide": false,
    "can_execute": false,
    "can_emit_act": false
  },
  "decision_authority": "KX108_ONLY",
  "readonly": true,
  "emits_act": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "source": "REAL_BACKEND"
}
```

### Checks par catégorie

| catégorie | checks | résultat |
|-----------|--------|---------|
| HTTP 200 + source LIVE (pas TestClient) | 2 | ✅ |
| Envelope (scenario_id, version, mode, user_input) | 4 | ✅ |
| Runtime entrypoint (F33 summary, 7 surfaces) | 4 | ✅ |
| Workbench summary (connector_status, surfaces_consulted) | 4 | ✅ |
| Controlled response (can_decide=False, can_execute=False, text) | 5 | ✅ |
| Forbidden tokens word-boundary (6 tokens) | 6 | ✅ |
| Top-level boundary (15 flags) | 15 | ✅ |
| Workbench boundary (11 flags) | 11 | ✅ |
| Controlled response boundary (11 flags) | 11 | ✅ |
| **TOTAL** | **61** | **61/61 ✅** |

### Surfaces confirmées READY

| surface | statut |
|---------|--------|
| `brody_runtime_context` | READY ✅ |
| `monitoring_adapters` | READY ✅ |
| `neo4j_guide_bridge` | READY ✅ |
| `operator_view_packet` | READY ✅ |
| `sigma_dispatcher` | READY ✅ |
| `tree_signal_packet` | READY ✅ |
| `workflow_governance_readonly` | READY ✅ |

---

## SECTION 4 — PREUVE JSON

**Fichier :** `docs/runtime/F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_034044.json`  
**SHA256 :** `A6FD4BC22B9EA7032E9AA325B193D8928BE969410DAE921A929A4DFF4A7592E4`  
**Taille :** 1 350 bytes  
**source :** `LIVE_SERVER_8011` ← confirm live HTTP, pas TestClient

---

## SECTION 5 — TESTS DE RÉGRESSION

```
tests/api/test_f36_user_scenario_brody_workbench_controlled_response.py — 14 passed (régression OK)
tests/api/test_f35_1_operator_demo_workbench_surfaces.py — 12 passed (régression OK)
tests/api/test_f34_live_route_contract_readonly.py — 14 passed (régression OK)
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed (régression OK)
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed (régression OK)
TOTAL=65/65 PASS
```

---

## SECTION 6 — NOTE PORT 8000

Le port 8000 était occupé par une instance Obsidia antérieure. **Ce serveur n'a pas été modifié.**
F36B a lancé un processus uvicorn indépendant sur le port 8011 depuis le HEAD courant (3a0e2ef)
et l'a arrêté après capture.

Pour que le port 8000 soit à jour (F36+), il faut redémarrer le serveur existant depuis ce répertoire.

---

## TERMINAL FINAL

```
F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=8011
ROUTE=POST /api/periphery/brody-runtime/f36/user-scenario
HTTP_STATUS=200
SOURCE=LIVE_SERVER_8011
SCENARIO_ID=F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE
RUNTIME_ENTRYPOINT_READY=True
WORKBENCH_SURFACE_READY=True
SURFACES_READY=7
CONTROLLED_RESPONSE_PRESENT=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=scripts/smoke_f36b_true_live_uvicorn_user_scenario.py,
              docs/runtime/F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_034044.json,
              docs/runtime/OBSIDIA_F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE_20260529_034044.md,
              .runtime_freezes/F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE_20260529_034044/MANIFEST_SHA256.json
FILES_MODIFIED=none
SMOKE_CHECKS=61/61 PASS
TESTS_PASS=65/65
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F36B → tag BRODY_F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE_PALIER_20260529
```
