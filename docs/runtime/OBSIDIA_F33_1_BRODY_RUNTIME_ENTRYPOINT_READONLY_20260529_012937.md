# OBSIDIA F33.1 — BRODY RUNTIME ENTRYPOINT READONLY

**Timestamp:** 20260529_012937  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F33_BRODY_RUNTIME_ENTRYPOINT_READONLY  
**Parent tag:** BRODY_F32_FULL_RUNTIME_INTEGRATION_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F33_RUNTIME_ENTRYPOINT_READONLY_STATUS=PASS
TESTS_PASS=12/12
REGRESSION_F32=17/17 PASS
REGRESSION_F29=4/4 PASS
API_TESTS_COLLECTED=1499
ENTRYPOINT_TYPE=ADAPTER_MODULE + API_ROUTE
INTEGRATION_STATUS=READY_READONLY
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

## SECTION 1 — FICHIERS CRÉÉS / MODIFIÉS

| fichier | rôle | sha256 |
|---------|------|--------|
| `periphery/brody_runtime/f33_runtime_entrypoint_readonly.py` | module F33 entrypoint | 4B8CAE5... |
| `tests/api/test_f33_brody_runtime_entrypoint_readonly.py` | tests F33 | 07E669D... |
| `docs/runtime/OBSIDIA_F33_1_..._20260529_012937.md` | ce rapport | — |
| `.runtime_freezes/F33_.../MANIFEST_SHA256.json` | freeze manifest | — |

**Fichiers modifiés :**

| fichier | changement |
|---------|-----------|
| `apps/obsidia_api/routes/periphery_ops.py` | Ajout `F33EntrypointPayload` + `POST /brody-runtime/f33/integration-packet` (lignes 1203–1250) |

---

## SECTION 2 — ARCHITECTURE DU MODULE F33

**Module :** `periphery/brody_runtime/f33_runtime_entrypoint_readonly.py`

### Fonction publique

```python
call_brody_runtime_entrypoint(
    *,
    domain: str = "bank",
    sigma_payload: dict | None = None,
    sop_text: str = ...,
    title: str = "F33 entrypoint readonly",
    session_id: str = "f33-entrypoint",
    signal_id: str = "f33-tree-signal",
    activations: list[float] | None = None,
    theta: float = 0.15,
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict
```

### Constantes exportées

| nom | valeur |
|-----|--------|
| `ENTRYPOINT_ID` | `"F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"` |
| `VERSION` | `"F33_V1"` |
| `PROOF_STATUS` | `"RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN"` |
| `BOUNDARY` | dict complet 15 flags |

### Enveloppe de retour

```json
{
  "entrypoint_id": "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY",
  "version": "F33_V1",
  "called_at": "<ISO timestamp>",
  "proof_status": "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN",
  "entrypoint_status": "ENTRYPOINT_READY_READONLY",
  "integration_status": "READY_READONLY",
  "surfaces_ready": 7,
  "surfaces_missing": 0,
  "surfaces_total": 7,
  "f32_packet": { ...F32 complet 7 surfaces... },
  ...BOUNDARY (15 flags)
}
```

### Import lazy

`build_f32_full_runtime_integration_packet` est importé à l'intérieur de `call_brody_runtime_entrypoint()`. Aucun import au niveau module en dehors de stdlib. Aucun import circulaire.

---

## SECTION 3 — ROUTE API

**Route ajoutée dans `apps/obsidia_api/routes/periphery_ops.py` :**

```
POST /api/periphery/brody-runtime/f33/integration-packet
```

**Modèle Pydantic :** `F33EntrypointPayload`  
**Handler :** `f33_brody_runtime_entrypoint(payload)`  
**Import :** lazy (`from periphery.brody_runtime.f33_runtime_entrypoint_readonly import call_brody_runtime_entrypoint` à l'intérieur du handler)

### Choix de convention

| convention inspectée | décision |
|---------------------|---------|
| `periphery_ops.py` héberge F23A6.2 (`/sigma/evaluate`), F28.2 (`/operator/governed-runtime`), F30.4 (`/workflow-governance/packet`) | ✅ F33 suit la même pattern |
| `brody_full_runtime_orchestrator.py` est pour orchestration message-driven (chat) | ❌ Pas applicable à F33 (packet structurel) |
| Nouvelle route dédiée (nouveau fichier) | ❌ Hors convention — `periphery_ops.py` est le registre établi |

---

## SECTION 4 — TESTS

### Résultats

```
tests/api/test_f33_brody_runtime_entrypoint_readonly.py — 12 passed in 0.32s
```

| test | objet | résultat |
|------|-------|---------|
| test_f33_entrypoint_returns_envelope | entrypoint_id, version, proof_status, called_at | ✅ |
| test_f33_entrypoint_status_ready | ENTRYPOINT_READY_READONLY, surfaces_ready=7, missing=0 | ✅ |
| test_f33_entrypoint_embeds_f32_packet | f32_packet présent, READY_READONLY, 7 surfaces | ✅ |
| test_f33_entrypoint_top_level_boundary | 15 flags boundary sur l'enveloppe F33 | ✅ |
| test_f33_entrypoint_f32_packet_boundary | 15 flags boundary sur f32_packet | ✅ |
| test_f33_entrypoint_all_seven_surfaces_ready | 7 surfaces READY dans f32_packet.surfaces | ✅ |
| test_f33_entrypoint_no_mutation_flags | kernel/x108/neo4j/memory/emits_act False partout | ✅ |
| test_f33_entrypoint_trading_domain | domain=trading, sigma result.domain=trading | ✅ |
| test_f33_entrypoint_graceful_degradation_unsupported_domain | UNSUPPORTED_DOMAIN, packet complet | ✅ |
| test_f33_entrypoint_proof_status | RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN, mode=READONLY | ✅ |
| test_f33_entrypoint_called_at_is_iso_string | called_at est une string ISO 8601 | ✅ |
| test_f33_boundary_module_constant_correct | BOUNDARY constant module-level exact | ✅ |

### Régression

```
tests/api/test_f32_brody_full_runtime_integration_readonly_packet.py — 17 passed (régression OK)
tests/api/test_f29_1_neo4j_manual_write_surface_guard.py — 4 passed (régression OK)
tests/api/ collect — 1499 tests (12 nouveaux F33 inclus, 0 erreurs)
```

---

## SECTION 5 — FREEZE MANIFEST

```
.runtime_freezes/F33_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937/
  MANIFEST_SHA256.json  ← 2 fichiers hashés (F33 module + tests), résultat tests, boundary
```

---

## SECTION 6 — LEGACY COLLECTION ERROR (non-bloquant)

```
tests/legacy_root/brody_api/test_conscience.py — SyntaxError (UTF-8 decode 0xe7)
```
Préexistant depuis avant F31. Non corrigé dans F33 (scope hors mission). Ne bloque pas les 1499 tests `tests/api/`.

---

## SECTION 7 — NEXT

```
NEXT=commit F33 (2 fichiers créés + 1 modifié + freeze manifest + rapport) via :
  git add periphery/brody_runtime/f33_runtime_entrypoint_readonly.py
  git add tests/api/test_f33_brody_runtime_entrypoint_readonly.py
  git add apps/obsidia_api/routes/periphery_ops.py
  git add .runtime_freezes/F33_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937/
  git add docs/runtime/OBSIDIA_F33_1_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937.md
  git commit -m "feat: checkpoint F33 brody runtime entrypoint readonly"
  git tag BRODY_F33_RUNTIME_ENTRYPOINT_READONLY_PALIER_20260529
  git push && git push --tags
```

---

## TERMINAL FINAL

```
F33_RUNTIME_ENTRYPOINT_READONLY_STATUS=PASS
ENTRYPOINT_TYPE=ADAPTER_MODULE + API_ROUTE
FILES_CREATED=periphery/brody_runtime/f33_runtime_entrypoint_readonly.py,
              tests/api/test_f33_brody_runtime_entrypoint_readonly.py,
              docs/runtime/OBSIDIA_F33_1_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937.md,
              .runtime_freezes/F33_.../MANIFEST_SHA256.json
FILES_MODIFIED=apps/obsidia_api/routes/periphery_ops.py
TESTS_RUN=12 (F33) + 17 (F32 regression) + 4 (F29 regression)
TESTS_PASS=33/33
API_TESTS_COLLECTED=1499
BOUNDARY_KX108_ONLY=true
FORBIDDEN_TOKENS_FOUND=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F33 (f33 module + tests + periphery_ops.py + freeze manifest + rapport) → tag BRODY_F33_RUNTIME_ENTRYPOINT_READONLY_PALIER_20260529
```
