# P66 — SRL Readonly Memory Layer

**Audit ID :** P66  
**Statut :** `P66_SRL_READONLY_MEMORY_LAYER_READY`  
**Mode :** `AUDIT_AND_READONLY_CANONIZATION`  
**Branche :** `p66-srl-readonly-memory-layer`  
**Date :** 2026-06-07

---

## Phrase verrou P66

> "La couche SRL est périphérique, readonly, non-décisionnelle. Elle produit des fiches, index, traces et context reload packs. Elle ne décide pas. Elle ne modifie pas le kernel. Elle ne write pas Graphiti. Elle ne write pas la mémoire canonique. Elle ne produit pas d'ACT. Autorité : KX108_ONLY."

---

## SRL — Session Registry Layer

Le SRL (Session Registry Layer) est la couche mémoire/session périphérique d'Obsidia. Il classe les sessions en zones taxonomiques, produit des fiches de contexte, et prépare les reload packs pour l'opérateur. Il ne prend aucune décision souveraine.

**Statut :** `FOUNDATION_PRESENT_PRECANONICAL_READY`

La fondation SRL est présente dans `periphery/brody_memory_readonly/`. La canonisation V0 a été complétée en P66.

---

## Composants SRL identifiés

| Composant | Chemin | Statut |
|---|---|---|
| `project_intake_capture_buffer` | `project_intake_capture_buffer_readonly/` | PRÉSENT |
| `session_presave_buffer` | `session_presave_buffer_readonly/` | PRÉSENT |
| `session_memory_ledger_v2` | `session_memory_ledger_readonly/` (v2 interne) | PRÉSENT_V2 |
| `auto_triage_memory_intake` | `auto_triage_memory_intake_readonly/` | PRÉSENT — BOUNDARY CORRIGÉ P66 |
| `candidate_export_for_graphiti` | `candidate_export_for_graphiti_readonly/` | PRÉSENT |
| `graphiti_candidate_review_gate` | `graphiti_candidate_review_gate_readonly/` | PRÉSENT |
| `graphiti_import_apply_guarded_manual_only` | `graphiti_import_apply_guarded_manual_only/` | **QUARANTAINE — HORS SRL READONLY** |
| `graphiti_guarded_manual_apply_...` | `graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/` | **QUARANTAINE — HORS SRL READONLY** |
| `memory_replay_query_regression` | `memory_replay_query_regression_readonly/` | PRÉSENT |
| `session_close_human_validation_gate` | `session_close_human_validation_gate_readonly/` | PRÉSENT |
| `session_close_decision_apply` | `session_close_decision_apply_readonly/` | PRÉSENT |
| `post_human_review_memory_triage` | `post_human_review_memory_triage_readonly/` | PRÉSENT — COUNT CORRIGÉ P66 |
| `brody_session_memory_adapter` | `apps/obsidia_api/brody_session_memory_adapter.py` | PRÉSENT |
| `brody_session_memory_runtime` | `apps/obsidia_api/brody_session_memory_runtime.py` | PRÉSENT |

---

## Problèmes corrigés

### P0 — Boundary mismatch auto_triage

**Fichier :** `auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py`

**Avant :**
```python
"emits_allow_hold_block": True,  # RÉACTIVATION DE LA SÉCURITÉ ACTIVE
"emits_verdict": True,            # VERDICT AUTORISÉ SUR L'INTÉGRITÉ
```

**Après :**
```python
"emits_allow_hold_block": False,   # SRL readonly ne décide pas
"emits_verdict": False,            # pas de verdict décisionnel
"emits_boundary_alert": True,      # alerte non-décisionnelle uniquement
"emits_reflex_alert": True,        # alerte reflex non-décisionnelle uniquement
```

`MANDATORY_HOLD_IMMEDIATE_BLOCK` → `BOUNDARY_ALERT_NON_DECISIONAL`  
`zone = "MANDATORY_HOLD"` → `zone = "BOUNDARY_ALERT"`

---

### P0 — Runner auto_triage incomplet

**Fichier :** `run_brody_auto_triage_memory_intake_readonly_v1.ps1`

Runner bloqué — ne lance pas le script Python. Ajout de `# TODO: AUTO_TRIAGE_RUNNER_INCOMPLETE`. Aucune exécution automatique ajoutée.

---

### P0 — Neo4j fallback admin1234

**Fichier :** `neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py`

**Avant :**
```python
password = os.environ.get("NEO4J_PASSWORD", "admin1234") # Fallback de secours courant
```

**Après :**
```python
password = os.environ.get("NEO4J_PASSWORD")
if not password:
    raise RuntimeError("NEO4J_PASSWORD_NOT_SET")
```

---

### P1 — Hardcode decision_count = 51

**Fichier :** `post_human_review_memory_triage_readonly/brody_post_human_review_memory_triage_readonly_v1.py`

**Avant :**
```python
if len(decisions) != 51:
    raise RuntimeError(f"BAD_DECISION_COUNT={len(decisions)}")
```

**Après :** Remplacé par `# BLOCKED_DYNAMIC_DECISION_COUNT_REQUIRED (P66)` — count dynamique délégué à l'opérateur humain KX108_ONLY.

---

## Modules Graphiti write — Quarantaine

Les modules suivants sont **hors du chemin SRL readonly**. Ils ne sont ni supprimés, ni exécutés, ni branchés dans le chemin P66.

| Module | Classification |
|---|---|
| `graphiti_import_apply_guarded_manual_only` | `OUT_OF_SRL_READONLY` / `MANUAL_GRAPHITI_WRITE_ZONE` / `HUMAN_OPERATOR_ONLY` / `QUARANTINE_FOR_SRL_PATH` |
| `graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only` | `OUT_OF_SRL_READONLY` / `MANUAL_GRAPHITI_WRITE_ZONE` / `HUMAN_OPERATOR_ONLY` / `QUARANTINE_FOR_SRL_PATH` |

---

## Taxonomie SRL V0

| Zone SRL | Description | Ancien label |
|---|---|---|
| `ACTIVE` | Session en cours — interaction opérateur active | `CRISTAL` |
| `SEMI_ACTIVE` | Session récente — activité partielle, candidat reload | `TRANSITION` |
| `COLD` | Session ancienne — archive, reload possible | — |
| `GHOST` | Session inactive / rejetée — ne pas charger par défaut | `NEANT` / `NEANT_REJECTED` → `GHOST_SIDE_TABLE` |
| `REFLEX_ALERT` | Alerte reflex non-décisionnelle | `REFLEX` |
| `BOUNDARY_ALERT` | Alerte boundary non-décisionnelle | `MANDATORY_HOLD` → `BOUNDARY_ALERT_NON_DECISIONAL` |

---

## Canon SRL créé

```
periphery/brody_memory_readonly/srl_session_registry_layer_readonly/
├── __init__.py                              (DRY_RUN_ONLY=True)
├── srl_taxonomy_readonly_v0.py              (zones, mapping, canonical_zone)
├── srl_boundary_readonly_v0.py              (SRL_BOUNDARY, validate_boundary)
├── srl_component_matrix_readonly_v0.py      (matrice composants, quarantaine)
├── srl_session_card_schema_readonly_v0.json (schéma fiche session)
└── srl_context_reload_pack_schema_readonly_v0.json (schéma reload pack)
```

---

## Métriques SRL formalisées

```
SRL_ACTIVE_COUNT          SRL_SEMI_ACTIVE_COUNT       SRL_COLD_COUNT
SRL_GHOST_COUNT           SRL_REFLEX_ALERT_COUNT      SRL_BOUNDARY_ALERT_COUNT
SRL_CONTEXT_RELOAD_PACK_CREATED
SRL_RELOAD_ACTIVE_COUNT   SRL_RELOAD_COLD_COUNT       SRL_RELOAD_GHOST_COUNT
SRL_DEEP_RECALL_USED      SRL_BOUNDARY_CONSISTENCY_PASS
SRL_READONLY_TRUE         SRL_MEMORY_DECISION_FALSE
SRL_GRAPHITI_WRITE_FALSE  SRL_NEO4J_WRITE_FALSE
SRL_X108_MERGE_FALSE      SRL_KERNEL_MUTATION_FALSE
SRL_DECISION_AUTHORITY_KX108_ONLY
```

---

## Matrice de sécurité P66

| Surface | Modifiée |
|---|---|
| `sigma/` | NON |
| `runtime_wiring/` | NON |
| `apps/obsidia_api/routes/` | NON |
| `proofs/V18_3_1/` | NON |
| `engine_runtime / engine_final / kernel` | NON IMPORTÉS |
| ACT activé | NON |
| memory_write activé | NON |
| graphiti_write activé | NON |
| neo4j_write activé | NON |
| kernel_mutation activé | NON |
| x108_merge activé | NON |

---

## Items bloqués (documentés, non supprimés)

| Item | Sévérité |
|---|---|
| `AUTO_TRIAGE_RUNNER_INCOMPLETE` | P0 — documenté |
| `BLOCKED_DYNAMIC_DECISION_COUNT_REQUIRED` | P1 — documenté |
| `DETECTED_PREEXISTING_MANIFEST_DRIFT` | Préexistant P65 |

---

## Palier suivant

**P67 — BOUNDARY_SEMANTIC_SPLIT_AUDIT**

---

**Verdict :** `P66_SRL_READONLY_MEMORY_LAYER_READY`
