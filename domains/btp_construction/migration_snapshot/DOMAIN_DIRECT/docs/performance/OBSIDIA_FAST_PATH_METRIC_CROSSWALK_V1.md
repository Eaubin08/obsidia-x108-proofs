# Obsidia Fast Path Metric Crosswalk V1

**Statut :** V1 — pont métriques Fast Path ↔ audit Obsidia / OIE
**Date :** 2026-07-01
**Branche :** feat/path-brody-r02-thermo-mcp-closure
**Autorité :** mesure uniquement — KX108_ONLY pour les décisions

---

## Objectif

Ce document établit la correspondance entre les micro-métriques brutes du Fast Path Runtime
(issues du Technical Note V0 et du benchmark V1) et les métriques auditables utilisées
dans les rapports Obsidia / OIE.

Il ne remplace pas les audits — il permet de lire les deux dans le même langage.

---

## Table de correspondance

| Métrique brute Fast Path | Métrique audit Obsidia/OIE | Bridge OIE | Signification |
|---|---|---|---|
| `graphiti_cold_ms` | latence de référence index froid | `obsidia_latency_ms` baseline | Coût d'un premier chargement JSONL — 277.718 ms mesuré V0 |
| `graphiti_warm_ms` | latence Fast Path index chaud | `obsidia_latency_ms` warm | Coût de cache hit JSONL — 0.3199 ms mesuré V0 |
| `graphiti_warm_gain_ratio` | `savings_ratio_vs_external` (analogue cache) | `savings_ratio` | Ratio cold/warm — 868.14x mesuré V0 |
| `graphiti_latency_reduction_pct` | `avoided_latency_ms` exprimée en % | `avoided_cost_eur_per_1m` (analogue) | Réduction latence index — 99.88% mesuré V0 |
| `runtime_context_build_ms` | latence assemblage contexte | `obsidia_latency_ms` contexte | Coût construction envelope — 0.0042 ms avg mesuré V0 |
| `runtime_loader_cold_ms` | latence chargement module froid | latence référence loader | Premier import modules — 47.6648 ms mesuré V0 |
| `runtime_loader_warm_ms` | latence chargement module chaud | `obsidia_latency_ms` warm | Warm import — 0.0042 ms mesuré V0 |
| `runtime_loader_warm_gain_ratio` | `savings_ratio` loader | `savings_ratio` | 11348.76x mesuré V0 |
| `route_accuracy` | `route_accuracy` | `route_accuracy` | Fraction runs où route ∈ expected_topics |
| `boundary_false_positive_count` | faux positifs ACTION_BOUNDARY | `boundary_safety_pass_rate` inverse | Requêtes French "act-" prefix mal routées |
| `action_boundary_precision` | `boundary_safety_pass_rate` | `boundary_safety_pass_rate` | Fraction runs où route ∉ forbidden_topics |
| `estimated_context_budget_delta_pct` | delta budget contexte | `external_cost_eur_per_1m` analogue | Réduction chars contexte Fast Path vs baseline |
| `model_call_avoided` | `model_call_avoided` | `model_call_avoided` | True si Fast Path n'invoque pas de LLM externe |
| `modules_skipped` | `modules_skipped` | `modules_skipped` | Modules non activés par Fast Path |
| `cache_hit_ratio` | `cache_hit_ratio` | `cache_hit_ratio` | Fraction runs utilisant le cache Graphiti chaud |
| `quality_pass_rate` | `quality_pass_rate` | `quality_pass_rate` | Fraction runs quality_score ≥ 1.0 |
| `emits_act` | `emits_act` | `EMITS_ACT=False` (governance) | Toujours False — non-souverain |
| `memory_write` | `memory_write` | `MEMORY_WRITE=False` (governance) | Toujours False — non-souverain |
| `decision_authority` | `decision_authority` | `DECISION_AUTHORITY=KX108_ONLY` | Kernel X-108 est la seule autorité d'action |

---

## Métriques dérivées non présentes dans V0 (calculées dans benchmark V1)

| Métrique benchmark V1 | Formule | Source |
|---|---|---|
| `latency_delta_pct` | `100 * (baseline_ms - fastpath_ms) / baseline_ms` | `compare_request()` |
| `internal_token_delta_pct` | `100 * (baseline_tokens - fastpath_tokens) / baseline_tokens` | `compare_request()` |
| `module_skip_pct` | `100 * modules_skipped / modules_considered` | `compare_request()` |
| `estimated_context_budget_delta_pct` | `100 * (baseline_context_chars - fp_context_chars) / baseline_context_chars` | `compare_request()` |
| `model_call_avoided_rate` | `model_call_avoided=True / total runs` | `summarize_mode()` |
| `route_accuracy` | `route_match=True / total runs` | `summarize_mode()` |
| `boundary_safety_pass_rate` | `boundary_ok=True / total runs` | `summarize_mode()` |

---

## Métriques V0 figées (frozen 73444cd / Technical Note V0)

Ces valeurs sont issues du microbenchmark V0 local et ne doivent pas être recalculées
sans un nouveau run complet sur la même machine avec la même base de code.

| Métrique | Valeur figée | Source |
|---|---|---|
| `graphiti_cold_ms` | 277.718 ms | Technical Note V0 §19.3 |
| `graphiti_warm_ms` | 0.3199 ms | Technical Note V0 §19.3 |
| `graphiti_warm_gain_ratio` | 868.14x | Technical Note V0 §19.3 |
| `graphiti_latency_reduction_pct` | 99.88% | Technical Note V0 §19.3 |
| `runtime_context_build_ms` (avg) | 0.0042 ms | Technical Note V0 §19.4 |
| `runtime_loader_cold_ms` | 47.6648 ms | Technical Note V0 §19.6 |
| `runtime_loader_warm_ms` (avg) | 0.0042 ms | Technical Note V0 §19.6 |
| `runtime_loader_warm_gain_ratio` | 11348.76x | Technical Note V0 §19.6 |

---

## Ce que ce crosswalk ne prouve pas

- Il ne prouve pas que Fast Path accélère le GPU, AMD ou ROCm.
- Il ne prouve pas une réduction de facturation provider externe (Anthropic, Fireworks).
- Il ne prouve pas une latence de production.
- Il ne prouve pas que Obsidia est plus rapide que tous les agents LLM.

---

## Positionnement final

> Fast Path does not accelerate compute. Fast Path reduces avoidable work before compute.

Les gains mesurés (868x cache, 11348x loader warm, 99.88% latence index) concernent
le travail **avant** l'appel LLM ou GPU — pas le calcul lui-même.

`model_call_avoided = True` est la métrique centrale : Fast Path supprime l'appel modèle
quand Obsidia peut répondre de façon déterministe (routing, context, cache).

---

## Gouvernance

| Propriété | Valeur |
|---|---|
| `emits_act` | False |
| `memory_write` | False |
| `decision_authority` | KX108_ONLY |
| `readonly` | True |
| `kernel_mutation` | False |
