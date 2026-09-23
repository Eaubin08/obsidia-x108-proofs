# OBSIDIA F39 — Operator Demo Pack Consolidation

**Timestamp:** 20260529_060816  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F39_OPERATOR_DEMO_PACK_CONSOLIDATION  
**Parent tag:** BRODY_F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## STATUS

```
F39_OPERATOR_DEMO_PACK_CONSOLIDATION_STATUS=PASS
CHAIN_COVERAGE=F32-F38
ROUTES_INDEXED=7
SMOKE_SCRIPTS_INDEXED=5
PROOFS_INDEXED=6
TESTS_PASS=103/103
BOUNDARY_KX108_ONLY=true
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## CHAÎNE PROUVÉE

```
F32 → F33 → F34 → F34B → F35 → F36 → F36B → F37 → F38
```

| Palier | Nom | Type | Proof |
|--------|-----|------|-------|
| F32 | Full Runtime Integration Readonly Packet | Module (7 surfaces) | TestClient — 17 tests |
| F33 | Brody Runtime Entrypoint Readonly | Module + HTTP route | TestClient — 12 tests |
| F34 | Live Route Smoke API Contract Proof | TestClient smoke | 73 checks PASS |
| F34B | True Live Uvicorn Server Smoke | Live uvicorn port 9010 | `REAL_BACKEND` · 73 checks PASS |
| F35 | Operator Demo Workbench Surfaces | 3 GET routes (C01/C02/C03) | TestClient — 12 tests |
| F36 | User Scenario Brody Workbench Controlled Response | Module + HTTP route | TestClient — 14 tests · 60 checks PASS |
| F36B | True Live Uvicorn User Scenario Smoke | Live uvicorn port 8011 | `LIVE_SERVER_8011` · 61 checks PASS |
| F37 | Multi-Domain User Scenarios Readonly | Module (4 domaines) | Direct call — 18 tests · 139 checks PASS |
| F38 | Multi-Domain Live Uvicorn API Smoke | HTTP route + live uvicorn | `LIVE_SERVER_8011` · 141 checks PASS |

---

## ROUTES API DISPONIBLES

### Routes Brody Runtime (POST)

```
POST /api/periphery/brody-runtime/f33/integration-packet
  → F33/F32 runtime entrypoint — 7 surfaces readonly
  → Boundary: KX108_ONLY · emits_act=false · kernel_mutation=false

POST /api/periphery/brody-runtime/f36/user-scenario
  → F36 user scenario — single domain advisory response
  → Payload: user_input, domain, sigma_payload, session_id, theta
  → Boundary: KX108_ONLY · can_decide=false · can_execute=false

POST /api/periphery/brody-runtime/f38/multi-domain-scenarios
  → F38/F37 multi-domain — 4 domains (bank/gps/trading/refusal)
  → Payload: theta, request_type (optional)
  → Boundary: KX108_ONLY · all_mutations_false=true
```

### Routes Opérateur / Démo / Workbench (GET)

```
GET /api/periphery/operator/runtime-panel
  → F35-C01 JSON — runtime readiness panel pour opérateur

GET /api/periphery/operator/runtime-panel.html
  → F35-C01 HTML — runtime readiness panel (rendu navigateur)

GET /api/periphery/demo/runtime-readiness
  → F35-C02 — demo/investor readiness packet

GET /api/periphery/workbench/runtime-connector
  → F35-C03 — workbench connector surface (F36 anchor)
```

---

## LANCER LE SERVEUR LOCAL

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

# Port 8011 (si 8000 occupé)
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011

# Vérifier que le serveur est prêt
Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing

# Vérifier la route F38
Invoke-WebRequest "http://127.0.0.1:8011/openapi.json" -UseBasicParsing |
  Select-String "f38/multi-domain-scenarios"
```

---

## SCRIPTS SMOKE DISPONIBLES

### Smoke TestClient (pas de serveur requis)

```powershell
# F34 — Route F33 smoke (73 checks)
python scripts\smoke_f34_live_route_contract_readonly.py

# F36 — Route F36 user scenario smoke (60 checks)
python scripts\smoke_f36_user_scenario_controlled_response.py

# F37 — Multi-domain module smoke (139 checks)
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
```

### Smoke Live Uvicorn (serveur requis)

```powershell
# Lancer uvicorn sur 8011 d'abord, puis :

# F36B — Route F36 live smoke (61 checks) — exige LIVE_SERVER
python scripts\smoke_f36b_true_live_uvicorn_user_scenario.py

# F38 — Route F38 multi-domain live smoke (141 checks) — exige LIVE_SERVER
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
```

### Payloads de démonstration

**F36 — Scénario bancaire :**
```json
{
  "user_input": "Je veux analyser une transaction bancaire avant paiement.",
  "domain": "bank",
  "sigma_payload": { "balance": 10000.0, "transactions": [{"amount": 100.0, "type": "debit", "recipient": "demo"}] }
}
```

**F36 — Scénario GPS :**
```json
{
  "user_input": "Je veux vérifier une trajectoire GPS sensible avant usage opérationnel.",
  "domain": "gps_defense_aviation",
  "sigma_payload": { "lat": 48.8566, "lon": 2.3522, "altitude_m": 10000.0 }
}
```

**F38 — Multi-domain (payload vide, tous les scénarios inclus) :**
```json
{}
```

---

## SUITE DE TESTS

```powershell
# Suite complète F29 + F32→F38
python -m pytest `
  tests\api\test_f38_multi_domain_live_api_route_readonly.py `
  tests\api\test_f37_multi_domain_user_scenarios_readonly.py `
  tests\api\test_f36_user_scenario_brody_workbench_controlled_response.py `
  tests\api\test_f35_1_operator_demo_workbench_surfaces.py `
  tests\api\test_f34_live_route_contract_readonly.py `
  tests\api\test_f33_brody_runtime_entrypoint_readonly.py `
  tests\api\test_f32_brody_full_runtime_integration_readonly_packet.py `
  tests\api\test_f29_1_neo4j_manual_write_surface_guard.py `
  -v
```

**Résultat attendu :** 103/103 PASS

---

## TAGS GIT

| Tag | Palier |
|-----|--------|
| `BRODY_F32_FULL_RUNTIME_INTEGRATION_PALIER_20260529` | F32 |
| `BRODY_F33_RUNTIME_ENTRYPOINT_READONLY_PALIER_20260529` | F33 |
| `BRODY_F34_LIVE_ROUTE_SMOKE_API_CONTRACT_PALIER_20260529` | F34 |
| `BRODY_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_PALIER_20260529` | F34B |
| `BRODY_F35_OPERATOR_DEMO_WORKBENCH_SURFACES_PALIER_20260529` | F35 |
| `BRODY_F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_PALIER_20260529` | F36 |
| `BRODY_F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE_PALIER_20260529` | F36B |
| `BRODY_F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_PALIER_20260529` | F37 |
| `BRODY_F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_PALIER_20260529` | F38 |

---

## PREUVES JSON CAPTURÉES

| Fichier | Palier | Source | SHA256 |
|---------|--------|--------|--------|
| `F34_LIVE_ROUTE_PROOF_20260529_015212.json` | F34 | TESTCLIENT_FALLBACK | — |
| `F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json` | F34B | REAL_BACKEND | `20A27188...` |
| `F36_USER_SCENARIO_PROOF_20260529_033111.json` | F36 | TESTCLIENT_FALLBACK | `FEA50112...` |
| `F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_034044.json` | F36B | LIVE_SERVER_8011 | `A6FD4BC2...` |
| `F37_MULTI_DOMAIN_PROOF_20260529_035506.json` | F37 | direct | `FE241362...` |
| `F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json` | F38 | LIVE_SERVER_8011 | `746621E5...` |

---

## BOUNDARY CONTRACT (toute la chaîne F32→F38)

```
decision_authority  = KX108_ONLY   ✅ (enforced at every layer)
allowed_to_decide   = False        ✅
readonly            = True         ✅
advisory_only       = True         ✅
context_signal_only = True         ✅
can_decide          = False        ✅
can_emit_act        = False        ✅
emits_act           = False        ✅
emits_verdict       = False        ✅
memory_write        = False        ✅
graphiti_write      = False        ✅
neo4j_write         = False        ✅
kernel_mutation     = False        ✅
x108_mutation       = False        ✅
runtime_execute     = False        ✅
```

**Tokens interdits dans toutes les réponses :**  
`ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT` (vérification par borne de mot)

**Tokens autorisés :**  
`autorité réservée · contexte disponible · inspection opérateur · réponse informative · aucune exécution · aucune mutation`

---

## LIMITES READONLY — RAPPEL

| Ce que Brody PEUT faire | Ce que Brody NE PEUT PAS faire |
|-------------------------|-------------------------------|
| Consulter les 7 surfaces runtime | Décider (KX108_ONLY décide) |
| Construire une réponse informative | Émettre un ACT |
| Analyser un contexte multi-domaines | Muter le kernel ou X108 |
| Présenter les données à l'opérateur | Écrire en Neo4j / Graphiti / mémoire |
| Refuser une demande hors périmètre | Exécuter une action irréversible |

---

## MODULES PYTHON F32→F38

| Module | Chemin |
|--------|--------|
| F32 packet | `periphery/brody_runtime/f32_full_runtime_integration_readonly_packet.py` |
| F33 entrypoint | `periphery/brody_runtime/f33_runtime_entrypoint_readonly.py` |
| F36 user scenario | `periphery/brody_runtime/f36_user_scenario_controlled_response.py` |
| F37 multi-domain | `periphery/brody_runtime/f37_multi_domain_user_scenarios_readonly.py` |
| Routes HTTP (F33/F35/F36/F38) | `apps/obsidia_api/routes/periphery_ops.py` |

---

## TERMINAL FINAL

```
F39_OPERATOR_DEMO_PACK_CONSOLIDATION_STATUS=PASS
CHAIN_COVERAGE=F32-F38
ROUTES_INDEXED=7
SMOKE_SCRIPTS_INDEXED=5
PROOFS_INDEXED=6
BOUNDARY_KX108_ONLY=true
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=docs/runtime/OBSIDIA_F39_OPERATOR_DEMO_PACK_CONSOLIDATION_20260529_060816.md,
              docs/runtime/OBSIDIA_F39_OPERATOR_DEMO_PACK_INDEX_20260529_060816.json,
              docs/demo/OBSIDIA_OPERATOR_DEMO_README_F39.md,
              .runtime_freezes/F39_OPERATOR_DEMO_PACK_CONSOLIDATION_20260529_060816/MANIFEST_SHA256.json
FILES_MODIFIED=none
TESTS_PASS=103/103
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F39 → tag BRODY_F39_OPERATOR_DEMO_PACK_CONSOLIDATION_PALIER_20260529
```
