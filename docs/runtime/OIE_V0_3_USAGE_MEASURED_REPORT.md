# OIE V0.3 — Rapport d'usage réel MEASURED (première coupe)

**Date** : 2026-07-08
**Source** : `audit/obsidia_gateway_usage.jsonl` (append-only, accumulé en usage réel)
**Différence avec le benchmark** : ici ce ne sont pas des tâches de test —
c'est l'usage réel de l'opérateur pendant le build de cette session.
`cost_source = MEASURED` (chaque ligne est un événement réellement survenu).

## Chiffres

| Métrique | Valeur |
|---|---|
| Requêtes tracées | 24 |
| Appels LLM évités | **24 (100 %)** |
| Sources | gateway 20 · CLI pré-inférence 1 · MCP 3 |

## Répartition par route (0 token sauf mention)

| Route | N | Nature |
|---|---|---|
| semantic_memory_hit | 6 | mémoire par sens (34 arbres) |
| clarification_needed | 4 | CLARIFY moins cher qu'une inférence |
| brody | 3 | organe local (API 8000) |
| no_model_needed | 2 | structure locale |
| hold_commands_only | 2 | HOLD, pause humaine |
| kernel_bridge | 1 | verdict kernel X108 réel |
| obsidure_proposal | 1 | cycle AVDR réel, proposal-only |
| memory_hit / obsidure_route / MCP tools | 5 | divers, tous locaux |

## Lecture

- 100 % d'évitement sur cette coupe car les escalades Level 3 de la session
  sont passées par Claude Code interactif (non compté ici) — le chiffre
  descendra naturellement dès que `obsidia chat` escaladera en `claude -p`.
- La donnée s'enrichit toute seule : chaque usage de `obsidia>`, `obsidia
  chat` ou des outils MCP ajoute une ligne MEASURED.
- Complément benchmark (run live du 2026-07-08, obsidia-router) : baseline
  7431 tokens → obsidia 1740 (**77 % économisés**), violations de cadre
  baseline 2/8 vs obsidia 0/8. À re-figer après le re-run propre.

Régénérer : recalcul direct depuis le JSONL (script inline, voir git log).
`decision_authority = KX108_ONLY` — rapport d'observation, aucun verdict.
