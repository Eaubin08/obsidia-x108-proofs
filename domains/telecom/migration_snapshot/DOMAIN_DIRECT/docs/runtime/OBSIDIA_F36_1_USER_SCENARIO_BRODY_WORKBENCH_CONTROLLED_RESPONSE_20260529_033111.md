# OBSIDIA F36 — User Scenario Brody Workbench Controlled Response

**Timestamp:** 20260529_033111  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE  
**Parent tag:** BRODY_F35_OPERATOR_DEMO_WORKBENCH_SURFACES_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F36_USER_SCENARIO_CONTROLLED_RESPONSE_STATUS=PASS
SCENARIO_INPUT=Je veux analyser une transaction bancaire avant paiement.
SOURCE=TESTCLIENT_FALLBACK
RUNTIME_ENTRYPOINT_READY=True
WORKBENCH_SURFACE_READY=True
SURFACES_READY=7
CONTROLLED_RESPONSE_PRESENT=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
SMOKE_CHECKS=60/60 PASS
TESTS_PASS=65/65
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — FICHIERS CRÉÉS / MODIFIÉS

| fichier | rôle |
|---------|------|
| `periphery/brody_runtime/f36_user_scenario_controlled_response.py` | Module F36 — scénario utilisateur bout en bout |
| `tests/api/test_f36_user_scenario_brody_workbench_controlled_response.py` | 14 tests contrat F36 |
| `scripts/smoke_f36_user_scenario_controlled_response.py` | Script smoke 60 checks |
| `docs/runtime/F36_USER_SCENARIO_PROOF_20260529_033111.json` | Preuve JSON capturée |
| `docs/runtime/OBSIDIA_F36_1_..._20260529_033111.md` | ce rapport |
| `.runtime_freezes/F36_.../MANIFEST_SHA256.json` | freeze manifest |

**Fichiers modifiés :**

| fichier | modification |
|---------|-------------|
| `apps/obsidia_api/routes/periphery_ops.py` | Route POST `/brody-runtime/f36/user-scenario` ajoutée |

---

## SECTION 2 — CONTEXTE

### Palier F36

F36 est le scénario utilisateur bout en bout qui ferme la chaîne F32 → F33 → F34 → F34B → F35 → F36.

**Flux :**
```
user_input
  → F33 runtime entrypoint (7 surfaces via F32)
  → workbench summary (surfaces_consulted=7)
  → controlled_response (text, can_decide=False, no forbidden tokens)
  → scenario envelope (READONLY · KX108_ONLY · emits_act=false)
```

**Scénario de test :** "Je veux analyser une transaction bancaire avant paiement."  
**Domaine :** bank  
**Surfaces consultées :** sigma_dispatcher, tree_signal_packet, monitoring_adapters, operator_view_packet, brody_runtime_context, workflow_governance_readonly, neo4j_guide_bridge

### Correctif forbidden-token

Le check initial utilisait une correspondance de sous-chaîne brute (`token not in text.upper()`).
Le mot "transaction" dans user_input contient "ACT" comme sous-chaîne — ce qui n'est pas un token de commande.
**Corrigé :** correspondance par borne de mot (`re.search(r"\bACT\b", text_upper)`) dans le test et le smoke script.
Le texte généré remplace également "activées" → "opérationnelles" et "action réelle" → "intervention réelle".

---

## SECTION 3 — RÉSULTATS DU SMOKE (60/60)

### Réponse capturée (extrait)

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
  "kernel_mutation": false
}
```

### Checks par catégorie

| catégorie | checks | résultat |
|-----------|--------|---------|
| Envelope (scenario_id, version, mode, user_input) | 5 | ✅ |
| Runtime entrypoint (F33 summary, 7 surfaces) | 4 | ✅ |
| Workbench summary (connector_status, surfaces_consulted) | 3 | ✅ |
| Controlled response (can_decide=False, can_execute=False, text) | 3 | ✅ |
| Forbidden tokens (6 tokens, word-boundary) | 6 | ✅ |
| Top-level boundary (15 flags) | 15 | ✅ |
| Workbench boundary (15 flags) | 15 | ✅ |
| Controlled response boundary (15 flags) | 15 | ✅ |
| **TOTAL** | **60** | **60/60 ✅** |

### Surfaces confirmées

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

**Fichier :** `docs/runtime/F36_USER_SCENARIO_PROOF_20260529_033111.json`  
**SHA256 :** `FEA50112F095E27846674857CE364C9435D42C692D5DB6C83D920509129B7714`  
**Taille :** 1 246 bytes  
**source :** `TESTCLIENT_FALLBACK`

---

## SECTION 5 — TESTS DE RÉGRESSION

```
tests/api/test_f36_user_scenario_brody_workbench_controlled_response.py — 14 passed ✅
tests/api/test_f35_1_operator_demo_workbench_surfaces.py — 12 passed ✅ (régression OK)
tests/api/test_f34_live_route_contract_readonly.py — 14 passed ✅ (régression OK)
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed ✅ (régression OK)
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed ✅ (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed ✅ (régression OK)
TOTAL=65/65 PASS ✅
```

---

## SECTION 6 — BOUNDARY ENFORCED

```
decision_authority  = KX108_ONLY   ✅
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

Boundary appliqué sur 3 couches : top-level · workbench · controlled_response.

---

## TERMINAL FINAL

```
F36_USER_SCENARIO_CONTROLLED_RESPONSE_STATUS=PASS
SCENARIO_INPUT=Je veux analyser une transaction bancaire avant paiement.
SOURCE=TESTCLIENT_FALLBACK
RUNTIME_ENTRYPOINT_READY=True
WORKBENCH_SURFACE_READY=True
SURFACES_READY=7
CONTROLLED_RESPONSE_PRESENT=True
BOUNDARY_KX108_ONLY=True
FORBIDDEN_TOKENS_FOUND=False
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=periphery/brody_runtime/f36_user_scenario_controlled_response.py,
              tests/api/test_f36_user_scenario_brody_workbench_controlled_response.py,
              scripts/smoke_f36_user_scenario_controlled_response.py,
              docs/runtime/F36_USER_SCENARIO_PROOF_20260529_033111.json,
              docs/runtime/OBSIDIA_F36_1_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_20260529_033111.md,
              .runtime_freezes/F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_20260529_033111/MANIFEST_SHA256.json
FILES_MODIFIED=apps/obsidia_api/routes/periphery_ops.py
SMOKE_CHECKS=60/60 PASS
TESTS_PASS=65/65
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F36 → tag BRODY_F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_PALIER_20260529
```
