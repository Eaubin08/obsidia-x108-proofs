# Sigma Remainder Branching Audit — F66 to F73

**Date** : 2026-05-30  
**Mode** : READ_ONLY + TEST_RUN  
**Layer** : SIGMA  
**Scope** : Audit pré-patch complet de la chaîne Sigma F66→F73  
**Risk** : NONE  
**Files touched** : none (artefact local non-commité)

---

## 1. Current Worktree State

**HEAD** : `6511752` — `docs: add F59 bus layer final freeze index`  
**TAG attendu** : `BRODY_F59_BUS_LAYER_FINAL_FREEZE_INDEX_PALIER_20260530` ✅ présent

### Fichiers modifiés (staged ou non, pas encore commités)

| Fichier | Type | Origine |
|---|---|---|
| `apps/obsidia_api/bus/state_aggregator.py` | PATCHED | F65 — ajout `sigma_bridge_state` |
| `apps/obsidia_api/main.py` | PATCHED | F63 — montage `sigma_monitoring_router` |
| `sigma/evaluate.py` | PATCHED | F61 — dispatcher readonly |
| `sigma/registry.py` | PATCHED | F60 — registry repair |
| `sigma/tools/run_bank_enterprise_pack.py` | PATCHED | F60 tooling |
| `tests/api/test_f23a4_4_sigma_evaluate_dispatcher.py` | PATCHED | F62B — normalisation `x108_gate` dict |
| `tests/api/test_f23a6_2_sigma_evaluate_endpoint.py` | PATCHED | F62B — normalisation `x108_gate` dict |
| `.claude/settings.local.json` | PATCHED | side effect local (non-Sigma) |

### Fichiers non-trackés (untracked, créés pour F60–F65)

```
.runtime_freezes/F60_SIGMA_REGISTRY_REPAIR_20260530_000000/MANIFEST_SHA256.json
apps/obsidia_api/bus/sigma_bridge.py              ← F65
apps/obsidia_api/routes/sigma_monitoring.py       ← F63
docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md
docs/demo/OBSIDIA_F60_SIGMA_REGISTRY_READINESS.md
docs/runtime/OBSIDIA_F60_SIGMA_REGISTRY_REPAIR_20260530_000000.json
docs/runtime/OBSIDIA_F60_SIGMA_REGISTRY_REPAIR_20260530_000000.md
scripts/_f61_inspect.py
scripts/_f62_inspect.py
scripts/_f62b_inspect.py
scripts/_f63_inspect.py
sigma/connectors.py                               ← F64
sigma/packets.py                                  ← F62
tests/api/test_f63_sigma_monitoring_endpoints_readonly.py
tests/api/test_f65_sigma_bus_readonly_bridge.py
tests/sigma/test_f60_sigma_registry_repair.py
tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py
tests/sigma/test_f62_sigma_domain_packets_normalization.py
tests/sigma/test_f64_sigma_connectors_reconciliation.py
```

### Warning connu (non-bloquant)

`UserWarning: Duplicate Operation ID x108_status_api_x108_status_get` dans `apps/obsidia_api/routes/x108.py` — présent avant F60, ne pas toucher.

---

## 2. F60→F64 Confirmed Build Map

| Palier | Fichier source | Fichier test | Tests | Statut |
|---|---|---|---|---|
| F60 | `sigma/registry.py` | `tests/sigma/test_f60_sigma_registry_repair.py` | 110 | ✅ PASS |
| F61 | `sigma/evaluate.py` | `tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py` | 207 | ✅ PASS |
| F62/F62B | `sigma/packets.py` | `tests/sigma/test_f62_sigma_domain_packets_normalization.py` | 205 | ✅ PASS |
| F63 | `apps/obsidia_api/routes/sigma_monitoring.py` | `tests/api/test_f63_sigma_monitoring_endpoints_readonly.py` | 195 | ✅ PASS |
| F64 | `sigma/connectors.py` | `tests/sigma/test_f64_sigma_connectors_reconciliation.py` | 70 | ✅ PASS |

**Total F60→F64** : 787 tests PASS

**Suites complémentaires validées** :
- Bus regression (F54/F56) : 103 PASS
- F47.1 `PROTECTED_RESPONSE_ENVELOPE` : PASS
- F47.2 `CONTROLLED_RESPONSE_SANITIZER` : PASS
- F47.3 `NESTED_SCAN_SCOPE` : PASS

---

## 3. F65 Status

**STATUS : COMPLETE_PASS**

| Artefact | Chemin | Statut |
|---|---|---|
| Module bridge | `apps/obsidia_api/bus/sigma_bridge.py` | ✅ DONE |
| Patch aggregator | `apps/obsidia_api/bus/state_aggregator.py:97` | ✅ DONE |
| Tests | `tests/api/test_f65_sigma_bus_readonly_bridge.py` | ✅ 55 tests PASS |

**Fonctions implémentées** :
- `build_sigma_bus_state()` — snapshot domains + connector_map (readonly, in-process)
- `validate_sigma_bus_bridge()` — agrège registry + dispatcher + connector validations
- `BRIDGE_VERSION = "F65"`

**Boundaries F65 confirmées** :
```python
decision_authority = "KX108_ONLY"
readonly           = True
advisory_only      = True
allowed_to_decide  = False
emits_act          = False
emits_verdict      = False
kernel_mutation    = False
x108_mutation      = False
neo4j_write        = False
graphiti_write     = False
memory_write       = False
brody_decision     = False
```

---

## 4. Dependency Graph

```
F59 (HEAD/TAG)
  └─ F60 (sigma/registry.py)
       └─ F61 (sigma/evaluate.py)
            └─ F62/F62B (sigma/packets.py)
                 └─ F63 (routes/sigma_monitoring.py)
                      └─ F64 (sigma/connectors.py)
                           └─ F65 (bus/sigma_bridge.py) ← COMPLETE
                                └─ F66 (sigma/orchestrator_preview.py) ← BUILD NEXT
                                     └─ F67 (scripts/smoke_f67_*.py + tests/api/test_f67_*.py)
                                          └─ F68 (FINAL FREEZE — commit + tag)
                                               ├─ F69 (test taxonomy — indépendant)
                                               ├─ F70 (Graphiti readonly bridge)
                                               ├─ F71 (34 trees activation)
                                               └─ F72 (OS Trad/IR/Reverse)
                                          └─ F73 (adversarial hardening — après F67)
```

---

## 5. File Touch Map

### Fichiers déjà touchés (F60→F65, à commiter ensemble en F68)

```
sigma/registry.py
sigma/evaluate.py
sigma/packets.py
sigma/connectors.py
sigma/tools/run_bank_enterprise_pack.py
apps/obsidia_api/routes/sigma_monitoring.py
apps/obsidia_api/bus/sigma_bridge.py
apps/obsidia_api/bus/state_aggregator.py
apps/obsidia_api/main.py
tests/sigma/test_f60_sigma_registry_repair.py
tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py
tests/sigma/test_f62_sigma_domain_packets_normalization.py
tests/sigma/test_f64_sigma_connectors_reconciliation.py
tests/api/test_f63_sigma_monitoring_endpoints_readonly.py
tests/api/test_f65_sigma_bus_readonly_bridge.py
tests/api/test_f23a4_4_sigma_evaluate_dispatcher.py (F62B fix)
tests/api/test_f23a6_2_sigma_evaluate_endpoint.py  (F62B fix)
```

### Fichiers à créer par palier

| Palier | Fichiers à créer |
|---|---|
| F66 | `sigma/orchestrator_preview.py`, `tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py` |
| F67 | `scripts/smoke_f67_sigma_live_smoke_api_audit.py`, `tests/api/test_f67_sigma_live_smoke_api_audit.py` |
| F68 | `docs/runtime/OBSIDIA_F68_SIGMA_READONLY_LAYER_FINAL_FREEZE_20260530.json`, `docs/runtime/OBSIDIA_F68_SIGMA_READONLY_LAYER_FINAL_FREEZE_20260530.md`, `docs/architecture/OBSIDIA_F68_SIGMA_READONLY_LAYER_CANONICAL_DOMAINS.md`, `docs/demo/OBSIDIA_F68_SIGMA_READONLY_LAYER_READINESS.md` |
| F69 | `docs/architecture/SIGMA_TEST_SUITE_TAXONOMY_F69.md` |
| F70 | `sigma/graphiti_readonly_bridge.py`, `tests/sigma/test_f70_graphiti_readonly_bridge.py` |
| F71 | `sigma/trees_activation_readonly.py`, `tests/sigma/test_f71_trees_activation_readonly.py` |
| F72 | `tests/api/test_f72_os_trad_ir_reverse_pipeline_audit.py` |
| F73 | `tests/sigma/test_f73_adversarial_boundary_advanced.py` |

### Fichiers à modifier par palier

| Palier | Fichiers à modifier | Raison |
|---|---|---|
| F66 | AUCUN | module pur, pas de route |
| F67 | AUCUN | smoke externe + tests offline |
| F68 | AUCUN (freeze uniquement) | commit + tag |
| F70 | `apps/obsidia_api/routes/graphiti.py` (optionnel) | si endpoint preview Sigma→Graphiti voulu |
| F71 | AUCUN au départ | mapping Sigma → trees dans module dédié |
| F72 | AUCUN | tests uniquement sur routes existantes |
| F73 | AUCUN | tests uniquement |

---

## 6. F66 Plan — SIGMA_ORCHESTRATOR_PREVIEW_READONLY

### Objectif
Produire un snapshot readonly de l'état complet de la chaîne Sigma (registry + dispatcher + packets + connectors + bus bridge F65), sans route HTTP, sans décision, sans ACT.

### Candidats architecturaux identifiés

| Fichier | Classification | Rôle F66 |
|---|---|---|
| `apps/obsidia_api/brody_full_runtime_orchestrator.py` | ORCHESTRATOR_CANONICAL_CANDIDATE | BEST_FIT_F66 — probe all modules, boundary hardcoded, readonly=True, emits_act=False |
| `apps/obsidia_api/brody_automation_orchestrator.py` | FOUNDATION_LAYER | allowed_to_decide=False hardcoded, routing par request_type |
| `apps/obsidia_api/routes/sigma_monitoring.py` | SAFE_READONLY_PREVIEW_SOURCE | Sigma 6 GET endpoints (F63) |
| `apps/obsidia_api/bus/sigma_bridge.py` | SAFE_READONLY_PREVIEW_SOURCE | F65 bus bridge (COMPLETE) |

### Fichier à créer : `sigma/orchestrator_preview.py`

```python
# Imports autorisés uniquement :
from sigma.registry import list_sigma_domains, validate_sigma_registry
from sigma.evaluate import validate_sigma_dispatcher
from sigma.packets import build_domain_packet  # ou get_domain_packet_schema
from sigma.connectors import validate_sigma_connectors, get_sigma_connector_map
from apps.obsidia_api.bus.sigma_bridge import build_sigma_bus_state, validate_sigma_bus_bridge

PREVIEW_VERSION = "F66"

_BOUNDARY = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "neo4j_write": False,
    "graphiti_write": False,
    "memory_write": False,
    "brody_decision": False,
}

def build_sigma_orchestrator_preview() -> dict: ...
def validate_sigma_orchestrator_preview() -> dict: ...
```

### Tests à créer : `tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py`
- ~50 tests dans 8 classes
- Couverture : import surface, structure `build_*`, `validate_*` status=PASS, flags sovereignty, absence ACT/verdict/mutation, domaines canoniques présents

### Risque principal
Ne pas importer `brody_full_runtime_orchestrator.py` directement — il tire des dépendances lourdes (Graphiti probe, 12 modules periphery). Utiliser uniquement les modules Sigma purs.

### Critère PASS
`validate_sigma_orchestrator_preview()["status"] == "PASS"`, tous flags sovereignty False.

---

## 7. F67 Plan — SIGMA_LIVE_SMOKE_API_AUDIT

### Objectif
Valider toutes les routes Sigma/Bus par TestClient offline (always runnable) ET par smoke live uvicorn (optionnel, nécessite serveur). Vérifier l'absence de forbidden tokens et de mutations dans audit JSONL.

### Fichier de référence
`scripts/smoke_f38_multi_domain_live_uvicorn_api.py` — ports live : `[8000, 9010, 8011]`

### Routes à couvrir

| Route | Méthode | Validation attendue |
|---|---|---|
| `/bus/stats` | GET | status=OK, no sigma_bridge_state |
| `/bus/bridge` | GET | sigma_bridge_state présent, bridge_version=F65 |
| `/bus/signal` | POST | 200, no sigma_bridge_state |
| `/api/periphery/monitoring/sigma/domains` | GET | liste 4 domaines canoniques |
| `/api/periphery/monitoring/sigma/evaluate` | GET | status=PASS, registry validé |
| `/api/periphery/monitoring/sigma/bank` | GET | domain=bank, readonly=True |
| `/api/periphery/monitoring/sigma/trading` | GET | domain=trading, readonly=True |
| `/api/periphery/monitoring/sigma/ecom` | GET | domain=ecom, readonly=True |
| `/api/periphery/monitoring/sigma/gps-defense-aviation` | GET | domain=gps_defense_aviation, readonly=True |

### Forbidden tokens (regex, word boundaries)
`\bALLOW\b`, `\bHOLD\b`, `\bBLOCK\b`, `\bACT\b`, `\bDECIDE\b`, `\bVERDICT\b`

### Audit JSONL
- Snapshot `audit/world_action_bus.jsonl` (taille) avant smoke
- Après smoke : vérifier que seuls des events `dry_run_only=true` ont été ajoutés
- Ne jamais écrire directement dans ce fichier

### Gestion serveurs fantômes (live smoke uniquement)
```bash
netstat -ano | findstr :8000  # vérifier port libre
uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000 &
# ... smoke ...
kill $PID  # stopper uniquement le processus lancé
```

### Critère PASS
Toutes routes 200, aucun forbidden token en réponse, aucun event bus non-`dry_run_only`.

---

## 8. F68 Final Freeze Plan

### Déclencheur
F65 + F66 + F67 tous PASS — tests F60→F67 tous verts.

### Fichiers runtime Sigma dans le manifest SHA256

```
sigma/registry.py
sigma/evaluate.py
sigma/packets.py
sigma/connectors.py
sigma/orchestrator_preview.py
apps/obsidia_api/bus/sigma_bridge.py
apps/obsidia_api/bus/state_aggregator.py
apps/obsidia_api/routes/sigma_monitoring.py
apps/obsidia_api/main.py
```

### Tests dans le manifest

```
tests/sigma/test_f60_sigma_registry_repair.py
tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py
tests/sigma/test_f62_sigma_domain_packets_normalization.py
tests/sigma/test_f64_sigma_connectors_reconciliation.py
tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py
tests/api/test_f63_sigma_monitoring_endpoints_readonly.py
tests/api/test_f65_sigma_bus_readonly_bridge.py
tests/api/test_f67_sigma_live_smoke_api_audit.py
tests/api/test_f23a4_4_sigma_evaluate_dispatcher.py
tests/api/test_f23a6_2_sigma_evaluate_endpoint.py
```

### Docs à créer (avant commit)

```
docs/runtime/OBSIDIA_F68_SIGMA_READONLY_LAYER_FINAL_FREEZE_20260530.json
docs/runtime/OBSIDIA_F68_SIGMA_READONLY_LAYER_FINAL_FREEZE_20260530.md
docs/architecture/OBSIDIA_F68_SIGMA_READONLY_LAYER_CANONICAL_DOMAINS.md
docs/demo/OBSIDIA_F68_SIGMA_READONLY_LAYER_READINESS.md
```

### Commit + tag

```bash
git add <tous les fichiers F60→F68>
git commit -m "feat: add F60-F68 Sigma readonly layer complete chain"
git tag BRODY_F68_SIGMA_READONLY_LAYER_FINAL_FREEZE_PALIER_20260530
```

**NE PAS créer encore.**

---

## 9. F69 Test Suite Taxonomy Plan

### Fichiers tests identifiés (~110 fichiers)

| Dossier | Count | Catégorie recommandée |
|---|---|---|
| `tests/sigma/test_f60_*.py` → `test_f66_*.py` | 6 | `ACTIVE_SIGMA_READONLY` |
| `tests/api/test_f63_*.py`, `test_f65_*.py`, `test_f67_*.py` | 3 | `ACTIVE_SIGMA_READONLY` |
| `tests/api/test_brody_*.py` | ~40 | `ACTIVE_BRODY_V1` |
| `tests/api/test_output_envelope_*.py` | 3 | `ACTIVE_BRODY_V1` |
| `tests/non_sovereignty/` | ~20 | `NON_SOVEREIGNTY` |
| `tests/integration/` | ~15 | `INTEGRATION` |
| `tests/legacy_root/` | 4 | `LEGACY_ROOT` |
| `sigma/tests/test_bank_*.py`, `test_gps_*.py`, etc. | ~20 | `ACTIVE_SIGMA_READONLY` |
| `tests/api/test_f23a4_*.py`, `test_f23a6_*.py` | 2 | `ACTIVE_SIGMA_READONLY` (F62B fix appliqué) |
| Smoke scripts (`scripts/smoke_*.py`) | ~3 | `REQUIRES_EXTERNAL_SERVICE` |

### Catégories de dette

- `ACTIVE_BRODY_V1` : doivent toujours passer
- `ACTIVE_SIGMA_READONLY` : F60→F67 chain, critiques
- `LEGACY_ROOT` : état uncertain, à évaluer
- `NON_SOVEREIGNTY` : boundary checks, critiques
- `INTEGRATION` : full-stack readonly, peuvent nécessiter serveur
- `FUTURE_CONTRACT` : tests F70/F71/F72/F73 à créer
- `REQUIRES_EXTERNAL_SERVICE` : uvicorn live, Neo4j — pas dans CI standard
- `ENCODING_ISSUE` : UTF-8/mojibake tests
- `BROKEN_REAL` : à identifier lors de la taxonomy run complète

**Ne pas patcher les tests pendant cet audit.**

---

## 10. F70 Memory Deep Plan

### Infrastructure existante

| Fichier | Type | Rôle |
|---|---|---|
| `apps/obsidia_api/routes/graphiti.py` | ROUTE | 5 GET endpoints : `/context`, `/metrics`, `/readiness`, `/search`, `/status` |
| `apps/obsidia_api/brody_full_runtime_orchestrator.py` | MODULE | `_probe_graphiti()` — probe port 8011, aucune écriture |
| `tests/non_sovereignty/test_graphiti_no_write.py` | TEST | Vérifie absence écriture Graphiti |
| `tests/non_sovereignty/test_graphiti_bridge_readonly_only.py` | TEST | Bridge readonly only |

### Ce qui manque pour F70

- `sigma/graphiti_readonly_bridge.py` : pont Sigma packet → Graphiti query (GET /search uniquement)
- Fonctions : `build_sigma_graphiti_readonly_query()`, `validate_sigma_graphiti_bridge()`
- Boundaries identiques F65 + `neo4j_write=False`, `graphiti_write=False`

### Risque principal
Port Neo4j 7688 — si ouvert, écriture théoriquement possible. Vérifier que port fermé avant tout test F70. ObsidiaShell Graphiti = port 8011 (frozen readonly).

### Statut recommandé : AUDIT maintenant, BUILD après F68

---

## 11. F71 34 Trees Plan

### Infrastructure existante

| Fichier | Type | Rôle |
|---|---|---|
| `apps/obsidia_api/routes/periphery_ops.py` | ROUTE | endpoints cognitive trees |
| `apps/obsidia_api/brody_tree_signal_packet.py` | MODULE | packet signal arbres |
| `apps/obsidia_api/brody_automation_orchestrator.py` | MODULE | routing tree policy |
| `apps/obsidia_api/routes/brody_monitoring.py` | ROUTE | monitoring trees |
| `tests/api/test_brody_tree_policy.py` | TEST | tree policy existant |

### Ce qui manque pour F71

- `sigma/trees_activation_readonly.py` : mapping Sigma domains → arbres actifs
- Fonctions : `build_sigma_trees_activation()`, `validate_sigma_trees_activation()`
- `dominance_threshold` : à documenter depuis `brody_automation_orchestrator.py`
- Boundaries : idem F65, `allowed_to_decide=False`

### Statut recommandé : AUDIT maintenant, BUILD après F68

---

## 12. F72 OS Trad / IR / Reverse Plan

### Infrastructure existante (déjà implémentée Phase 9B2)

| Fichier | Type | Routes |
|---|---|---|
| `apps/obsidia_api/routes/os_trad_ir_reverse.py` | ROUTE | POST `/ir/candidate`, `/os-reverse/project`, `/os-trad/translate` |
| `apps/obsidia_api/brody_existing_reverse_os_bridge.py` | MODULE | Bridge reverse OS existant |
| `periphery/reverse_os/action_projection_readonly.py` | MODULE | Projection d'action readonly (try/except import) |
| `periphery/reverse_os/audience_projection.py` | MODULE | Projection audience (try/except import) |
| `apps/obsidia_api/routes/translation.py` | ROUTE | POST `/translation/trace` |
| `tests/api/test_brody_os_trad_ir_reverse_discovery.py` | TEST | Discovery test existant |

### Ce qui manque pour F72

- Tests approfondis pipeline : input → IR → projection → response readonly
- Validation boundary sur `/ir/candidate` et `/os-reverse/project`
- Lien Sigma packet → enrichissement IR (domain enrichment)
- `tests/api/test_f72_os_trad_ir_reverse_pipeline_audit.py`

### Liens Sigma
Sigma packet (domain=bank/trading/ecom) → enrichissement IR → réponse readonly. Jamais de décision.

### Statut recommandé : AUDIT maintenant, BUILD/TESTS après F68

---

## 13. F73 Advanced Hardening Plan

### Infrastructure existante

| Fichier | Tests |
|---|---|
| `sigma/tests/test_bank_adversarial_pack.py` | Adversarial bank existant |
| `sigma/tests/test_bank_security_fuzz_pack.py` | Fuzz security |
| `sigma/tests/test_bank_security_fuzz_extended_pack.py` | Extended fuzz |
| `sigma/tests/test_bank_fuzz_scale_pack.py` | Scale fuzz |
| `scripts/_f47_test_sanitizer.py` | Sanitizer F47 (PASS) |

### Tests avancés à créer : `tests/sigma/test_f73_adversarial_boundary_advanced.py`

| Classe | Cas de test |
|---|---|
| `TestF73UnicodeHomoglyphes` | domaine "bаnk" (а cyrillique), "trаding" non-ASCII |
| `TestF73CasingVariations` | "BANK", "Bank", "bAnK", "BaNk" |
| `TestF73NestedJSON` | `{"domain": {"nested": "bank"}}` au lieu de string |
| `TestF73LargePayloads` | champ domain > 10 000 chars |
| `TestF73MalformedPayload` | JSON invalide, champs manquants, types incorrects |
| `TestF73ForbiddenTokenSubstring` | "ACT" dans "CONTACT" ne déclenche pas, "ACTOR" safe |
| `TestF73SchemaBypass` | extra fields, type coercion, injection JSON |
| `TestF73RouteInjection` | path traversal dans domain name (`../../etc/passwd`) |
| `TestF73FakeDecisionAuthority` | `{"decision_authority": "BRODY"}` ignoré, KX108_ONLY forcé |

### Critère PASS
Tous cas retournent 400/422 ou refus propre. Aucun forbidden token en sortie. `decision_authority` toujours `KX108_ONLY`.

### Statut recommandé : BUILD après F67

---

## 14. Forbidden Files / No-Touch List

```
proofs/                                    # Lean proofs — IMMUTABLE
formal/                                    # TLA+ specs — IMMUTABLE
merkle*/                                   # Merkle trees — SEALED
seal*/                                     # RFC3161 seals — SEALED
rfc3161*/                                  # RFC3161 — SEALED
V18_*/                                     # Versioned kernel — FROZEN
apps/obsidia_api/main.py                  # Ne plus modifier (F63 dernier patch)
audit/world_action_bus.jsonl              # Append-only, lecture seule
sigma/contracts.broken-ragnarok.py       # Intentionnellement cassé — NE PAS TOUCHER
.runtime_freezes/                         # Archives freeze — IMMUTABLE
sigma/contracts.py                        # Contrats Sigma stables
sigma/base.py, sigma/guard.py             # Infrastructure core Sigma stable
sigma/obsidia_sigma_v130.py               # Version pinnée Sigma
```

---

## 15. Recommended Execution Order

```
ÉTAPE  | PALIER | TYPE   | Durée | Dépend de
-------|--------|--------|-------|----------
  1    | AUDIT  | TEST   | 5min  | — (maintenant, DONE ✅)
  2    | F66    | BUILD  | ~1h   | F65 COMPLETE
  3    | F67    | BUILD  | ~1h   | F63, F65, F66
  4    | F68    | FREEZE | ~30m  | F65+F66+F67 PASS
  5    | F69    | AUDIT  | ~30m  | Indépendant (parallélisable)
  6    | F70    | AUDIT  | ~30m  | F68 (après freeze)
  7    | F71    | AUDIT  | ~30m  | F68 (après freeze)
  8    | F72    | AUDIT  | ~30m  | F68 (après freeze)
  9    | F73    | BUILD  | ~1h   | F67 PASS
```

---

## 16. Exact Next Prompt To Run

```
MODE AGENT BUILD — TERMINAL-FIRST — F66_SIGMA_ORCHESTRATOR_PREVIEW_READONLY

OBJECTIF : Créer sigma/orchestrator_preview.py et son test suite.

FICHIER À CRÉER : sigma/orchestrator_preview.py
- PREVIEW_VERSION = "F66"
- build_sigma_orchestrator_preview() : lit registry (list_sigma_domains, validate_sigma_registry),
  dispatcher (validate_sigma_dispatcher), connectors (validate_sigma_connectors,
  get_sigma_connector_map), bus bridge (build_sigma_bus_state, validate_sigma_bus_bridge).
  Retourne dict avec tous les états agrégés + boundary dict.
- validate_sigma_orchestrator_preview() : appelle validate_sigma_registry,
  validate_sigma_dispatcher, validate_sigma_connectors, validate_sigma_bus_bridge.
  Retourne {"status": "PASS"/"FAIL", "preview_version": "F66", "errors": [...], **boundary}.
- Imports UNIQUEMENT depuis sigma.* et apps.obsidia_api.bus.sigma_bridge
- PAS d'import depuis brody_full_runtime_orchestrator
- PAS de route HTTP
- PAS de modification main.py
- Boundaries : decision_authority=KX108_ONLY, readonly=True, tous les flags False

FICHIER À CRÉER : tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py
- ~50 tests, ~8 classes
- Couvrir : import surface, structure build_*, validate_* PASS, flags sovereignty, domaines canoniques,
  absence ACT/verdict/mutation, preview_version="F66"

APRÈS BUILD :
- Relancer F60→F65 + bus regression + F47 pour vérifier aucune régression
- Critère PASS : validate_sigma_orchestrator_preview()["status"] == "PASS", tous flags False

CONTRAINTES :
- Pas de modification de main.py
- Pas de route HTTP
- Pas de modification kernel, proof, seal, merkle
- Ne pas commit
```

---

## Sortie d'audit

```
SIGMA_REMAINDER_BRANCHING_AUDIT_STATUS=PASS
F65_STATUS=COMPLETE_PASS
F66_BRANCH_TARGET=sigma/orchestrator_preview.py
F67_LIVE_SMOKE_PLAN_READY=true
F68_FINAL_FREEZE_PLAN_READY=true
F69_TEST_TAXONOMY_PLAN_READY=true
F70_MEMORY_PLAN_READY=true
F71_TREES_PLAN_READY=true
F72_IR_REVERSE_PLAN_READY=true
F73_HARDENING_PLAN_READY=true
FILES_TO_CREATE_BY_PALIER=sigma/orchestrator_preview.py|tests/sigma/test_f66_*.py|scripts/smoke_f67_*.py|tests/api/test_f67_*.py|tests/sigma/test_f73_*.py
FILES_TO_MODIFY_BY_PALIER=AUCUN (F66 module pur; F67/F73 tests only)
FILES_FORBIDDEN=main.py|kernel/*|proof/*|seal/*|merkle*|V18_*|.runtime_freezes/*|sigma/contracts.broken-ragnarok.py
TESTS_TO_RUN_BY_PALIER=F60→F65+bus_regression+F47 (DONE ✅)|F66 tests après build|F67 offline+smoke après build
DEPENDENCY_GRAPH_READY=true
KX108_ONLY_PRESERVED=true
COMMIT=NO
TAG=NO
PUSH=NO
FREEZE=NO
NEXT=BUILD F66 — sigma/orchestrator_preview.py
```
