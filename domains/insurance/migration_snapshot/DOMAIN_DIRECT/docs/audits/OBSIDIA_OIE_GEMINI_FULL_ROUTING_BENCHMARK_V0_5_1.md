# OBSIDIA OIE — Gemini Full Routing Benchmark V0.5.1

**Statut :** Protocole documenté — run réel non effectué (nécessite GEMINI_API_KEY + ALLOW_NETWORK)
**Date :** 2026-07-01
**Branche :** feat/path-brody-r02-thermo-mcp-closure
**Provider :** gemini_sdk (google-genai)
**Modèle :** gemini-2.0-flash-lite
**Autorité :** KX108_ONLY — OIE reste non souverain

---

## Positionnement central

> Obsidia is not compared as a larger model. Obsidia is compared as an inference-avoidance and governance layer.

Gemini est invoqué comme référence LLM général.
Obsidia est évalué sur sa capacité à éviter cet appel — par routing déterministe, Fast Path, ou bridge domaine.

---

## 1. Protocole

### Provider et modèle

| Paramètre | Valeur |
|---|---|
| `OIE_EXTERNAL_PROVIDER` | `gemini_sdk` |
| `OIE_EXTERNAL_MODEL_LABEL` | `gemini-2.0-flash-lite` |
| `benchmark_kind` | `ROUTING` (7 familles) |
| `repetitions` | 1 par tâche (smoke) |
| Réseau | `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1` requis |
| Clé | `GEMINI_API_KEY` ou `GOOGLE_API_KEY` depuis env uniquement |

### Activation du run réel

```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
$env:OIE_EXTERNAL_BENCHMARK_FULL          = "1"
$env:OIE_EXTERNAL_PROVIDER                = "gemini_sdk"
$env:OIE_EXTERNAL_MODEL_LABEL             = "gemini-2.0-flash-lite"
$env:GEMINI_API_KEY                       = "<cle_non_committée>"
# Optionnel — pour savings_ratio et avoided_cost :
$env:OIE_EXTERNAL_INPUT_COST_PER_1M       = "0.036"
$env:OIE_EXTERNAL_OUTPUT_COST_PER_1M      = "0.144"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

---

## 2. Familles de tâches routing (7)

| task_id | task_family | expected_route | obsidia_cost_EUR/1M | obsidia_model_call |
|---|---|---|---:|---|
| `fastpath_route_selection_smoke` | fast_path_vs_llm_simple | FAST_PATH | 0.0015 | False |
| `brody_route_selection` | brody_vs_assistant | BRODY | 0.20 | True |
| `bank_route_selection` | bank_vs_domain_llm | BANK | 0.70 | False |
| `trading_route_selection` | trading_vs_domain_llm | TRADING | 0.84 | False |
| `gps_route_selection` | gps_aviation_vs_domain_llm | GPS | 0.91 | False |
| `obsidure_route_selection` | obsidure_vs_code_agent | OBSIDURE | 23.92 | True |
| `lean_route_selection` | lean_proof_vs_long_reasoning | OBSIDURE | 13.29 | True |

---

## 3. Métriques attendues par receipt

Chaque receipt doit contenir :

| Champ | Source |
|---|---|
| `expected_route` | tâche |
| `external_detected_route` | extraction regex depuis output Gemini |
| `route_match` | `detected == expected` |
| `external_success` | appel SDK réussi |
| `external_latency_ms` | temps perf_counter |
| `external_input_tokens` | `interaction.usage.total_input_tokens` |
| `external_output_tokens` | `interaction.usage.total_output_tokens` |
| `external_total_tokens` | `interaction.usage.total_tokens` |
| `cost_source` | `SDK_USAGE_MEASURED` si prix fournis |
| `external_cost_eur_measured` | `compute_measured_sdk_cost()` |
| `external_cost_eur_per_1m_measured` | idem |
| `savings_ratio_vs_external` | `external_cost / obsidia_cost` |
| `avoided_cost_eur_per_1m` | `external_cost - obsidia_cost` |
| `model_call_avoided` | `external_model_call_required AND NOT obsidia_model_call_required` |
| `quality_score` | `evaluate_route_quality()` |
| `quality_penalty` | `1 - quality_score` |
| `external_failure_type` | `detect_failure_type()` ou `NONE` |
| `comparison_axis` | axe OIE de la tâche |
| `emits_act` | toujours False |
| `memory_write` | toujours False |
| `decision_authority` | toujours KX108_ONLY |
| `secrets_redacted` | toujours True |

---

## 4. Smoke Gemini observé (V0.5 — run réel)

Run partiel observé avec `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1` (routing smoke, 1 tâche) :

| Champ | Valeur observée |
|---|---|
| provider | gemini_sdk |
| model | gemini-2.0-flash-lite |
| external_success | True |
| external_usage_available | True |
| external_input_tokens | 34 |
| external_output_tokens | 3 |
| external_total_tokens | 37 |
| route_match | True |
| quality_score | 1.0 |
| cost_source (avant fix) | USAGE_UNAVAILABLE (bug) |
| cost_source (après fix V0.5.1) | SDK_USAGE_MEASURED si prix fournis |

**Bug corrigé en V0.5.1** : `build_real_receipt` vérifiait `provider == PROVIDER_SDK` au lieu de `provider in (PROVIDER_SDK, PROVIDER_GEMINI)`. Le chemin Gemini tombait dans `elif cost_estimate_enabled` qui requiert `OIE_EXTERNAL_COST_ESTIMATE=1`. Corrigé : les deux providers SDK appellent `compute_measured_sdk_cost()` dès que `usage_available=True`, indépendamment de `OIE_EXTERNAL_COST_ESTIMATE`.

---

## A. Summary metrics (attendus — full routing 7 tâches)

| Métrique | Valeur attendue | Condition |
|---|---|---|
| `tasks_run` | 7 | `FULL=1` |
| `external_success_count` | 7 | si réseau OK |
| `route_match_count` | ≥ 5 / 7 | estimé |
| `usage_available_count` | 7 | SDK retourne usage |
| `model_call_avoided_count` | 4 | Fast Path, Bank, Trading, GPS |
| `cost_source` | SDK_USAGE_MEASURED | si prix fournis |
| `savings_ratio` | calculable | si SDK_USAGE_MEASURED |
| `emits_act` | False | toujours |
| `memory_write` | False | toujours |

---

## B. Per-family comparison (template)

| task_id | expected_route | detected_route | match | latency_ms | in_tok | out_tok | cost_src | savings_ratio | model_call_avoided |
|---|---|---|---|---:|---:|---:|---|---:|---|
| fastpath_route_selection_smoke | FAST_PATH | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | True |
| brody_route_selection | BRODY | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | False |
| bank_route_selection | BANK | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | True |
| trading_route_selection | TRADING | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | True |
| gps_route_selection | GPS | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | True |
| obsidure_route_selection | OBSIDURE | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | False |
| lean_route_selection | OBSIDURE | ? | ? | ? | ? | ? | SDK_USAGE_MEASURED | ? | False |

_À remplir lors du run réel._

---

## C. Cost / tokens table (template)

| task_id | obsidia_EUR/1M | gemini_EUR/1M | avoided_EUR/1M | savings_ratio |
|---|---:|---:|---:|---:|
| fastpath_route_selection_smoke | 0.0015 | ? | ? | ? |
| brody_route_selection | 0.20 | ? | ? | ? |
| bank_route_selection | 0.70 | ? | ? | ? |
| trading_route_selection | 0.84 | ? | ? | ? |
| gps_route_selection | 0.91 | ? | ? | ? |
| obsidure_route_selection | 23.92 | ? | ? | ? |
| lean_route_selection | 13.29 | ? | ? | ? |

Prix de référence OIE (figés 73444cd) : OSCA=38241x, OAPI=47143x, ODPI=30612x.
Ces ratios seront comparés aux `savings_ratio` Gemini mesurés.

---

## D. Latency table (template)

| task_id | obsidia_latency_ms | gemini_latency_ms | avoided_latency_ms | latency_ratio |
|---|---:|---:|---:|---:|
| fastpath_route_selection_smoke | ~0.004 | ? | ? | ? |
| brody_route_selection | ~200 | ? | ? | ? |
| bank_route_selection | ~50 | ? | ? | ? |
| trading_route_selection | ~50 | ? | ? | ? |
| gps_route_selection | ~50 | ? | ? | ? |
| obsidure_route_selection | ~500 | ? | ? | ? |
| lean_route_selection | ~200 | ? | ? | ? |

---

## E. Route quality table (template)

| task_id | expected_route | detected_route | route_match | quality_score | quality_penalty | error_type |
|---|---|---|---|---:|---:|---|
| fastpath_route_selection_smoke | FAST_PATH | ? | ? | ? | ? | ? |
| brody_route_selection | BRODY | ? | ? | ? | ? | ? |
| bank_route_selection | BANK | ? | ? | ? | ? | ? |
| trading_route_selection | TRADING | ? | ? | ? | ? | ? |
| gps_route_selection | GPS | ? | ? | ? | ? | ? |
| obsidure_route_selection | OBSIDURE | ? | ? | ? | ? | ? |
| lean_route_selection | OBSIDURE | ? | ? | ? | ? | ? |

---

## F. OIE differential table (template)

| task_id | comparison_axis | model_call_avoided | cost_source | comparison_status |
|---|---|---|---|---|
| fastpath_route_selection_smoke | FAST_PATH | True | SDK_USAGE_MEASURED | OK |
| brody_route_selection | BRODY_RESPONSE | False | SDK_USAGE_MEASURED | OK |
| bank_route_selection | DOMAIN_DECISION | True | SDK_USAGE_MEASURED | OK |
| trading_route_selection | DOMAIN_DECISION | True | SDK_USAGE_MEASURED | OK |
| gps_route_selection | DOMAIN_DECISION | True | SDK_USAGE_MEASURED | OK |
| obsidure_route_selection | CODE_PROOF | False | SDK_USAGE_MEASURED | OK |
| lean_route_selection | CODE_PROOF | False | SDK_USAGE_MEASURED | OK |

---

## G. Governance table

| Propriété | Valeur | Immuable |
|---|---|---|
| `emits_act` | False | Oui — `__post_init__` |
| `memory_write` | False | Oui — `__post_init__` |
| `kernel_mutation` | False | Oui — `__post_init__` |
| `graphiti_write` | False | Oui — `__post_init__` |
| `neo4j_write` | False | Oui — `__post_init__` |
| `readonly` | True | Oui — `__post_init__` |
| `secrets_redacted` | True | Oui — `__post_init__` |
| `decision_authority` | KX108_ONLY | Oui — `__post_init__` |

La clé `GEMINI_API_KEY` / `GOOGLE_API_KEY` n'est jamais écrite dans les receipts, les logs, ou les JSON produits.

---

## H. Valid claim / invalid claims

### Valid claim

> Obsidia Fast Path and deterministic bridge layers avoid external LLM inference for routing tasks where decisions are deterministic. For tasks where Obsidia invokes a model (Brody, Obsidure, Lean), the comparison measures cost and latency of the Gemini alternative.

### Invalid claims

- Obsidia est un modèle plus grand ou plus capable que Gemini.
- Obsidia produit de meilleures sorties LLM que Gemini Flash.
- Le benchmark prouve une latence de production.
- Le benchmark prouve une réduction de facturation Gemini tierce.
- Gemini est plus lent que Obsidia sur toutes les tâches.

### Règle d'interprétation

`model_call_avoided = True` → Obsidia décide sans appel LLM → `savings_ratio` est le ratio coût Gemini / coût Obsidia déterministe.

`model_call_avoided = False` → Obsidia et Gemini font tous deux un appel modèle → la comparaison porte sur la qualité de routage, pas sur l'évitement d'inférence.

---

## Statut

- Smoke observé : 1 tâche, `route_match=True`, `usage_available=True`, `quality_score=1.0`
- Bug coût corrigé en V0.5.1 : Gemini SDK tokens → `compute_measured_sdk_cost()` sans dépendance à `OIE_EXTERNAL_COST_ESTIMATE`
- Full routing (7 tâches) : protocole documenté, run réel à effectuer avec `FULL=1` + `GEMINI_API_KEY`
- Commit : non effectué (politique no-auto-commit)
