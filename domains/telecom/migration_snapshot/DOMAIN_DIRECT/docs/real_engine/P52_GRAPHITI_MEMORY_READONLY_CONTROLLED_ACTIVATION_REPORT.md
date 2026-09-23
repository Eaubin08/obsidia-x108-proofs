# P52 — Graphiti Memory Readonly Controlled Activation

**Date :** 2026-06-04
**Branche :** p43-unconnected-runtime-surface-audit
**Statut :** `P52_GRAPHITI_MEMORY_READONLY_CONTROLLED_ACTIVATION_READY`
**Basé sur :** P51 Brody Readonly + commits `d1dcbbf` + `e9e43e4`

> **Note de réconciliation :** P52 ne crée rien de nouveau. Il réconcilie les
> vrais composants déjà présents dans l'historique Git avec la matrice P50 et
> l'activation P51.

---

## Composants réels confirmés

| Composant | Path | Commit source | Statut live |
|-----------|------|--------------|------------|
| `graphiti_v20_readonly_client` | `apps/obsidia_api/graphiti_v20_readonly_client.py` | `d1dcbbf` | **ACTIF** (127.0.0.1:8011) |
| Routes Graphiti readonly | `apps/obsidia_api/routes/graphiti.py` | `d1dcbbf` | REAL_MODULE |
| `graphiti_readonly_records_v2.jsonl` | `_graphiti_readonly_indexes/.../graphiti_readonly_records_v2.jsonl` | `e9e43e4` | 3267 enregistrements |
| Memory real module | `apps/obsidia_api/routes/memory.py` | `e9e43e4` | REAL_MODULE |
| `brody_project_memory_adapter` | `apps/obsidia_api/brody_project_memory_adapter.py` | `e9e43e4` | PASS |
| `brody_session_memory_adapter` | `apps/obsidia_api/brody_session_memory_adapter.py` | `e9e43e4` | REAL_MODULE |

---

## Données Graphiti live

| Métrique | Valeur |
|---------|--------|
| Base URL | `http://127.0.0.1:8011` |
| Nœuds | **167** |
| Relations | **477** |
| Mode | FROZEN_READONLY |
| Endpoints actifs | `/frozen/status`, `/frozen/context`, `/frozen/search`, `/frozen/metrics`, `/frozen/readiness` |

---

## Ce qui est activé (LEVEL_1 READONLY_ACTIVE)

| Capacité | Valeur |
|----------|--------|
| `graphiti_read_enabled` | **true** |
| `memory_read_enabled` | **true** |
| `real_component_found` | **true** |
| `brody_can_use_graphiti_context` | **true** |
| `brody_can_use_memory_context` | **true** |
| `activation_level` | `LEVEL_1_READONLY_ACTIVE` |

---

## Ce qui reste bloqué — INVARIANTS

| Invariant | Valeur |
|-----------|--------|
| `graphiti_write_enabled` | **false** |
| `memory_write_enabled` | **false** |
| `neo4j_write` | false |
| `runtime_allowed_now` | false |
| `activation_allowed_now` | false |
| `emits_act` | false |
| `decision_authority` | KX108_ONLY |

---

## Preuve no Graphiti write

- `graphiti_write=False` dans `_readonly_envelope()` de `graphiti_v20_readonly_client.py`
- Aucune route `/api/graphiti/` n'expose de méthode POST/PUT/DELETE vers Neo4j
- `graphiti_write_enabled=False` dans l'activation contract
- Tests `tests/non_sovereignty/test_graphiti_no_write.py` existants et passants

---

## Preuve no memory write

- `memory_write=False` dans `routes/memory.py` (toutes les réponses)
- `auto_promotion=False`, `promotion_requires_human_review=True`
- `memory_write_enabled=False` dans l'activation contract
- Tests `tests/api/test_no_memory_write_api.py` existants

---

## Preuve no ACT

- `emits_act=False` dans tous les enregistrements JSONL (`3267/3267`)
- `allowed_to_decide=False` dans `graphiti_readonly_records_v2.jsonl`
- `runtime_allowed_now=False` — gateway non ouverte
- `decision_authority=KX108_ONLY` partout

---

## Index JSONL (e9e43e4)

```
_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/
  graphiti_readonly_records_v2.jsonl
    → 3267 enregistrements
    → readonly=True, emits_act=False, decision_authority=KX108_ONLY
    → source_kind: V164D_TAXONOMY_34_TO_8_ENRICHED
```

---

## Limites

1. **Graphiti HTTP dépend du serveur 8011** — si ObsidiaShell est arrêté, `graphiti_read_enabled` passe à `False` automatiquement. L'activation contract gère gracefully.
2. **JSONL index figé** — `graphiti_readonly_records_v2.jsonl` est un snapshot de `20260512`. Pas de mise à jour automatique.
3. **Memory write toujours bloqué** — la promotion mémoire reste humain-only.

---

## Prochain palier : P53

`P53_WORLD_ACTION_BUS_DRY_RUN_ACTIVATION`

P53 activera le world action bus en mode `DRY_RUN` (LEVEL_2) pour simuler les émissions d'actions sans effet réel, conformément à la matrice P50.

---

*NO ACT — NO WRITE — NO GRAPHITI WRITE — NO MEMORY WRITE — NO KERNEL MUTATION — KX108_ONLY*
*graphiti_read_enabled = true — memory_read_enabled = true — graphiti_write_enabled = false*
