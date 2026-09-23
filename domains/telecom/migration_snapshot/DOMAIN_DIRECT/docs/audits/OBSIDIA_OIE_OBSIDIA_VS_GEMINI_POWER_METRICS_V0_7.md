# OBSIDIA OIE — Power Benchmark V0.7 : Obsidia vs Gemini

**Date :** 2026-07-01

**Version :** OIE_POWER_BENCHMARK_V0.7

**Statut :** dry-run (valeurs figees V0.5.1) — run reel necessite GEMINI_API_KEY + ALLOW_NETWORK

**Autorite :** KX108_ONLY — OIE non souverain

---

## 1. Executive Summary

> Gemini is inference power. Obsidia is routing, governance, proof, and inference avoidance power.



> Obsidia is not benchmarked as a larger model; it is benchmarked as a constrained decision and work-avoidance layer.



- Taches : 7 familles routing

- Obsidia route accuracy : 0.57

- Gemini route accuracy  : 0.43

- Model call avoided     : 4/7

- Governance clean       : True

---

## 2. Pourquoi les benchmarks precedents etaient insuffisants

Les benchmarks V0.2–V0.5.1 mesuraient principalement :

- `route_match` et `cost_source` par receipt individuel

- Pas de vision globale speed / energy / throughput / work avoidance

- Pas de `safe_decisions_per_second`, `decisions_per_wh`, `decisions_per_cost_unit`

- Pas de colonne `winner_*` par famille

- Pas de rapport energie / carbone

V0.7 reunit toutes ces dimensions dans une seule table comparative par famille.

---

## 3. Architecture : deux lanes sur les memes 7 familles

| Lane | Mode | Reseau | Modele |
| --- | --- | --- | --- |
| OBSIDIA_LOCAL_ACTUAL | FROZEN_V0_ESTIMATE / REAL_ADAPTER / ADAPTER_MISSING | Non | deterministe |
| GEMINI_SDK_EXTERNAL | DRY_RUN_MOCK / REAL_SDK | Optionnel | gemini-2.0-flash-lite |

> Energy values are proxy estimates unless hardware/provider telemetry is supplied.

---

## 4. Speed metrics

| family | obs_lat_ms | gem_lat_ms | lat_delta_pct | speedup_ratio | winner |
| --- | --- | --- | --- | --- | --- |
| FAST_PATH | 0.3199 | 312.0000 | 99.90 | 975.30 | OBSIDIA |
| BRODY | 85.0000 | 428.0000 | 80.14 | 5.04 | OBSIDIA |
| BANK | 42.0000 | 395.0000 | 89.37 | 9.40 | OBSIDIA |
| TRADING | 18.0000 | 382.0000 | 95.29 | 21.22 | OBSIDIA |
| GPS | 9.5000 | 404.0000 | 97.65 | 42.53 | OBSIDIA |
| OBSIDURE | 1200.0000 | 451.0000 | -166.08 | 0.38 | GEMINI |
| LEAN | 200.0000 | 388.0000 | 48.45 | 1.94 | OBSIDIA |

Moyenne speedup : 150.83x

Moyenne latency delta pct : 49.25%

---

## 5. Cost metrics

| family | obs_cost_req | gem_cost_req | avoided_cost | cost_sr | winner |
| --- | --- | --- | --- | --- | --- |
| FAST_PATH | 0.00000005 | N/A | N/A | N/A | UNKNOWN |
| BRODY | 0.00000800 | N/A | N/A | N/A | UNKNOWN |
| BANK | 0.00002730 | N/A | N/A | N/A | UNKNOWN |
| TRADING | 0.00003108 | N/A | N/A | N/A | UNKNOWN |
| GPS | 0.00003458 | N/A | N/A | N/A | UNKNOWN |
| OBSIDURE | 0.00095680 | N/A | N/A | N/A | UNKNOWN |
| LEAN | 0.00055818 | N/A | N/A | N/A | UNKNOWN |

Total cost Gemini : N/A EUR

Total cost Obsidia est : 0.00161599 EUR

Total avoided cost : N/A EUR

Note : cout Gemini mesure seulement si REAL mode + prix env fournis.

---

## 6. Energy metrics

| family | obs_wh | gem_wh | avoided_wh | energy_sr | winner |
| --- | --- | --- | --- | --- | --- |
| FAST_PATH | N/A | N/A | N/A | N/A | UNKNOWN |
| BRODY | N/A | N/A | N/A | N/A | UNKNOWN |
| BANK | N/A | N/A | N/A | N/A | UNKNOWN |
| TRADING | N/A | N/A | N/A | N/A | UNKNOWN |
| GPS | N/A | N/A | N/A | N/A | UNKNOWN |
| OBSIDURE | N/A | N/A | N/A | N/A | UNKNOWN |
| LEAN | N/A | N/A | N/A | N/A | UNKNOWN |

Source energie : ENERGY_PROXY_UNAVAILABLE

Activer avec : OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS + OIE_LOCAL_POWER_W + OIE_CARBON_GCO2_PER_KWH

---

## 7. Power / capacity metrics

| family | obs_safe_dps | gem_safe_dps | obs_dpc | gem_dpc |
| --- | --- | --- | --- | --- |
| FAST_PATH | 3125.977 | 3.205 | 19047619.05 | N/A |
| BRODY | N/A | 0.000 | 125000.00 | N/A |
| BANK | 23.809 | 2.532 | 36630.04 | N/A |
| TRADING | 55.556 | 0.000 | 32175.03 | N/A |
| GPS | 105.263 | 2.475 | 28918.45 | N/A |
| OBSIDURE | N/A | 0.000 | 1045.15 | N/A |
| LEAN | N/A | 0.000 | 1791.54 | N/A |

safe_decisions_per_second = throughput * quality_score * boundary_ok

decisions_per_cost_unit = 1 / cost_per_request

---

## 8. Context economy

| family | obs_tok | gem_tok | tok_delta_abs | tok_delta_pct | ext_dep_ratio |
| --- | --- | --- | --- | --- | --- |
| FAST_PATH | 35 | 42 | 7 | 16.67 | 1.20 |
| BRODY | 40 | 42 | 2 | 4.76 | 1.05 |
| BANK | 39 | 43 | 4 | 9.30 | 1.10 |
| TRADING | 37 | 43 | 6 | 13.95 | 1.16 |
| GPS | 38 | 42 | 4 | 9.52 | 1.11 |
| OBSIDURE | 40 | 41 | 1 | 2.44 | 1.02 |
| LEAN | 42 | 42 | 0 | 0.00 | 1.00 |

Total Obsidia tokens est : 271

Total Gemini tokens : 295

---

## 9. Work avoidance

| family | model_avoided | modules_skipped | cache_hit | obs_status |
| --- | --- | --- | --- | --- |
| FAST_PATH | True | 5 | True | FROZEN_V0_ESTIMATE |
| BRODY | False | 3 | False | ADAPTER_MISSING |
| BANK | True | 4 | False | FROZEN_V0_ESTIMATE |
| TRADING | True | 4 | False | FROZEN_V0_ESTIMATE |
| GPS | True | 4 | False | FROZEN_V0_ESTIMATE |
| OBSIDURE | False | 2 | False | ADAPTER_MISSING |
| LEAN | False | 2 | False | ADAPTER_MISSING |

model_call_avoided total : 4/7

model_call_avoided_rate : 0.57

modules_skipped total : 24

cache_hit_ratio : 0.14

Frozen V0 warm gains : graphiti=868.14x, loader=11348.76x

---

## 10. Inference avoidance

Familles ou Obsidia evite l'appel LLM (model_call_avoided=True) :

- **FAST_PATH** : Obsidia decide de facon deterministe.

- **BANK** : Obsidia decide de facon deterministe.

- **TRADING** : Obsidia decide de facon deterministe.

- **GPS** : Obsidia decide de facon deterministe.



Familles ou Obsidia doit aussi invoquer un modele (model_call_avoided=False) :

- **BRODY** (status=ADAPTER_MISSING) : comparaison latence/cout.

- **OBSIDURE** (status=ADAPTER_MISSING) : comparaison latence/cout.

- **LEAN** (status=ADAPTER_MISSING) : comparaison latence/cout.

---

## 11. Routing quality

| family | expected | obs_detected | gem_detected | obs_match | gem_match | q_delta | winner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FAST_PATH | FAST_PATH | FAST_PATH | FAST_PATH | True | True | 0.00 | TIE |
| BRODY | BRODY | ? | FAST_PATH | ? | False | N/A | NEITHER |
| BANK | BANK | BANK | BANK | True | True | 0.00 | TIE |
| TRADING | TRADING | TRADING | GPS | True | False | 1.00 | OBSIDIA |
| GPS | GPS | GPS | GPS | True | True | 0.00 | TIE |
| OBSIDURE | OBSIDURE | ? | BRODY | ? | False | N/A | NEITHER |
| LEAN | OBSIDURE | ? | BRODY | ? | False | N/A | NEITHER |

Obsidia quality avg : 1.00

Gemini quality avg  : 0.43

---

## 12. Governance / boundary safety

| Propriete | Valeur | Immutable |
| --- | --- | --- |
| emits_act | False | Oui |
| memory_write | False | Oui |
| kernel_mutation | False | Oui |
| graphiti_write | False | Oui |
| neo4j_write | False | Oui |
| secrets_redacted | True | Oui |
| decision_authority | KX108_ONLY | Oui |

boundary_safety_pass_rate : 1.00

governance_clean (all tasks) : True

---

## 13. Confusion matrix

| Scenario | Count |
| --- | --- |
| Obsidia correct ET Gemini correct | 3 |
| Obsidia correct MAIS Gemini incorrect | 1 |
| Gemini correct MAIS Obsidia incorrect | 0 |
| Aucun correct | 3 |

Note : Obsidia ADAPTER_MISSING compte comme route inconnue, pas comme match.

---

## 14. Per-family comparison

### FAST_PATH — fastpath_power_smoke

- **Interpretation** : FAST_PATH: Obsidia routes deterministically — no LLM call. Gemini requires full inference. Work avoidance is the key metric.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : TIE

- Gov winner   : OBSIDIA

- Obsidia status : FROZEN_V0_ESTIMATE

- Gemini status  : DRY_RUN_MOCK

### BRODY — brody_power_route

- **Interpretation** : BRODY: Obsidia adapter not available for live run. Architecture cost estimate used. Gemini as reference inference cost.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : NEITHER

- Gov winner   : OBSIDIA

- Obsidia status : ADAPTER_MISSING

- Gemini status  : DRY_RUN_MOCK

### BANK — bank_power_route

- **Interpretation** : BANK: Obsidia routes deterministically — no LLM call. Gemini requires full inference. Work avoidance is the key metric.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : TIE

- Gov winner   : OBSIDIA

- Obsidia status : FROZEN_V0_ESTIMATE

- Gemini status  : DRY_RUN_MOCK

### TRADING — trading_power_route

- **Interpretation** : TRADING: Obsidia routes deterministically — no LLM call. Gemini requires full inference. Work avoidance is the key metric.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : OBSIDIA

- Gov winner   : OBSIDIA

- Obsidia status : FROZEN_V0_ESTIMATE

- Gemini status  : DRY_RUN_MOCK

### GPS — gps_power_route

- **Interpretation** : GPS: Obsidia routes deterministically — no LLM call. Gemini requires full inference. Work avoidance is the key metric.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : TIE

- Gov winner   : OBSIDIA

- Obsidia status : FROZEN_V0_ESTIMATE

- Gemini status  : DRY_RUN_MOCK

### OBSIDURE — obsidure_power_route

- **Interpretation** : OBSIDURE: Obsidia adapter not available for live run. Architecture cost estimate used. Gemini as reference inference cost.

- Speed winner : GEMINI

- Cost winner  : UNKNOWN

- Route winner : NEITHER

- Gov winner   : OBSIDIA

- Obsidia status : ADAPTER_MISSING

- Gemini status  : DRY_RUN_MOCK

### LEAN — lean_power_route

- **Interpretation** : LEAN: Obsidia adapter not available for live run. Architecture cost estimate used. Gemini as reference inference cost.

- Speed winner : OBSIDIA

- Cost winner  : UNKNOWN

- Route winner : NEITHER

- Gov winner   : OBSIDIA

- Obsidia status : ADAPTER_MISSING

- Gemini status  : DRY_RUN_MOCK

---

## 15. Valid claims

- Obsidia evite l'appel LLM pour FAST_PATH, BANK, TRADING, GPS (4/7 familles).

- Pour les 4 familles deterministes, Obsidia latence < 100ms vs 300-450ms Gemini.

- Obsidia governance garantit emits_act=False, memory_write=False pour toutes les taches.

- Le benchmark mesure l'avoidance d'inference, pas la qualite de generation LLM.

- Fast Path Graphiti warm path : 868x speedup cache vs cold (frozen V0).

- Loader warm path : 11348x speedup (frozen V0 Technical Note).

---

## 16. Invalid claims

- INTERDIT : "Obsidia is smarter than Gemini"

- INTERDIT : "Obsidia is faster than all LLMs"

- INTERDIT : "Obsidia is a better language model"

- INTERDIT : "Obsidia produces better outputs than Gemini"

- INTERDIT : Ce benchmark prouve que Obsidia est moins cher que Gemini en production.

- INTERDIT : Les valeurs energetiques sont des mesures hardware reelles.

- INTERDIT : Obsidia produit de meilleures reponses LLM que Gemini.

---

## 17. Next metrics V0.8

- Execution d'un run reel Gemini 7 familles + comparaison avec V0.7 dry-run.

- Telemetrie GPU/CPU reelle pour energy_source=HARDWARE_MEASURED.

- Repetitions (N=10) pour p50/p95/p99 reels.

- Integration sigma/contracts.py pour validation governance on-chain.

- Matrice domaine-output (ALLOW/HOLD/BLOCK) comparee Obsidia vs Gemini.

---
