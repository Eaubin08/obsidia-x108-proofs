# OBSIDIA F38 — Multi-Domain Live Uvicorn API Smoke

**Timestamp:** 20260529_040328  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE  
**Parent tag:** BRODY_F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=8011
ROUTE=POST /api/periphery/brody-runtime/f38/multi-domain-scenarios
HTTP_STATUS=200
SOURCE=LIVE_SERVER_8011
PACKET_ID=F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY
SCENARIO_COUNT=4
BANK_READY=True
GPS_READY=True
TRADING_READY=True
UNKNOWN_REFUSAL_READY=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
SMOKE_CHECKS=141/141 PASS
TESTS_PASS=103/103
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — FICHIERS CRÉÉS / MODIFIÉS

| fichier | rôle |
|---------|------|
| `tests/api/test_f38_multi_domain_live_api_route_readonly.py` | 20 tests contrat F38 route |
| `scripts/smoke_f38_multi_domain_live_uvicorn_api.py` | Script smoke F38 live (141 checks) |
| `docs/runtime/F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json` | Preuve JSON capturée live (769 bytes) |
| `docs/runtime/OBSIDIA_F38_1_..._20260529_040328.md` | ce rapport |
| `.runtime_freezes/F38_.../MANIFEST_SHA256.json` | freeze manifest |

**Fichiers modifiés :**

| fichier | modification |
|---------|-------------|
| `apps/obsidia_api/routes/periphery_ops.py` | Route `POST /brody-runtime/f38/multi-domain-scenarios` ajoutée (F38MultiDomainPayload + handler) |

---

## SECTION 2 — CONTEXTE

### Palier F38

F38 expose le module F37 via HTTP et prouve la route via vrai serveur uvicorn.

| palier | rôle |
|--------|------|
| F37 | Orchestrateur multi-domaines (module pur, synchrone) |
| F38 | Route HTTP + preuve live uvicorn |

**Relation analogue :** F33 exposait F32 → F34 prouvait F33 live → F38 expose+prouve F37.

### Stratégie port

Port 8000 occupé. Uvicorn lancé sur port **8011** (libre), prêt dès la 1ère seconde (PID 16484).  
Route F38 confirmée présente dans `/openapi.json`.

---

## SECTION 3 — RÉPONSE LIVE (extrait)

```json
{
  "packet_id": "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY",
  "version": "F37_V1",
  "mode": "READONLY",
  "scenario_count": 4,
  "scenarios_run": 4,
  "global_status": "READY_READONLY",
  "all_mutations_false": true,
  "forbidden_tokens_found": false,
  "decision_authority": "KX108_ONLY",
  "readonly": true,
  "emits_act": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "source": "REAL_BACKEND"
}
```

### Résultats par domaine

| domaine | status | surfaces | can_decide | forbidden_tokens |
|---------|--------|----------|-----------|-----------------|
| `bank` | READY_READONLY ✅ | 7 | False ✅ | False ✅ |
| `gps_defense_aviation` | READY_READONLY ✅ | 7 | False ✅ | False ✅ |
| `trading` | READY_READONLY ✅ | 7 | False ✅ | False ✅ |
| `unknown_refusal` | REFUSAL_READONLY ✅ | 0 | False ✅ | False ✅ |

### Checks par catégorie

| catégorie | checks | résultat |
|-----------|--------|---------|
| source LIVE + HTTP 200 | 2 | ✅ |
| Envelope (packet_id, version, mode, counts, status) | 7 | ✅ |
| Domaines présents | 1 | ✅ |
| Par domaine (status/surfaces/cr/tokens/text) | 24 | ✅ |
| Boundary global (15 flags) | 15 | ✅ |
| Boundary per scenario (4 × 15) | 60 | ✅ |
| Boundary controlled_response (4 × 8) | 32 | ✅ |
| **TOTAL** | **141** | **141/141 ✅** |

---

## SECTION 4 — PREUVE JSON

**Fichier :** `docs/runtime/F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json`  
**SHA256 :** `746621E5EAE0F11795AB17B4A36E98CFA6F98AA0926CDCB35C2635A758D153CF`  
**Taille :** 769 bytes  
**source :** `LIVE_SERVER_8011` ← confirm live HTTP, pas TestClient

---

## SECTION 5 — TESTS DE RÉGRESSION

```
tests/api/test_f38_multi_domain_live_api_route_readonly.py — 20 passed ✅
tests/api/test_f37_multi_domain_user_scenarios_readonly.py — 18 passed ✅ (régression OK)
tests/api/test_f36_user_scenario_brody_workbench_controlled_response.py — 14 passed ✅ (régression OK)
tests/api/test_f35_1_operator_demo_workbench_surfaces.py — 12 passed ✅ (régression OK)
tests/api/test_f34_live_route_contract_readonly.py — 14 passed ✅ (régression OK)
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed ✅ (régression OK)
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed ✅ (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed ✅ (régression OK)
TOTAL=103/103 PASS ✅
```

---

## TERMINAL FINAL

```
F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=PASS
SERVER_MODE=LIVE_UVICORN
PORT=8011
ROUTE=POST /api/periphery/brody-runtime/f38/multi-domain-scenarios
HTTP_STATUS=200
SOURCE=LIVE_SERVER_8011
PACKET_ID=F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY
SCENARIO_COUNT=4
BANK_READY=True
GPS_READY=True
TRADING_READY=True
UNKNOWN_REFUSAL_READY=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=tests/api/test_f38_multi_domain_live_api_route_readonly.py,
              scripts/smoke_f38_multi_domain_live_uvicorn_api.py,
              docs/runtime/F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json,
              docs/runtime/OBSIDIA_F38_1_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_20260529_040328.md,
              .runtime_freezes/F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_20260529_040328/MANIFEST_SHA256.json
FILES_MODIFIED=apps/obsidia_api/routes/periphery_ops.py
SMOKE_CHECKS=141/141 PASS
TESTS_PASS=103/103
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F38 → tag BRODY_F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_PALIER_20260529
```
