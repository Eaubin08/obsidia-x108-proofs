# OBSIDIA OIE Power Metrics — Protocole V0.7

> Gemini is inference power. Obsidia is routing, governance, proof, and inference avoidance power.

> Obsidia is not benchmarked as a larger model; it is benchmarked as a constrained decision and work-avoidance layer.

---

## 1. Cout mesure vs cout proxy

- `obsidia_cost_basis = LOCAL_PROXY_UNCALIBRATED`
  Le cout Obsidia est une estimation proxy basee sur l'architecture.
  Il ne correspond pas a une facture provider reelle.
  Formula : obsidia_cost_proxy_per_1m_est * obsidia_estimated_total_tokens / 1_000_000
- `gemini_cost_basis = SDK_USAGE_MEASURED` en mode REAL avec usage SDK.
- `cost_comparison_claimable = False` tant que les deux bases sont differentes.
- Warning : Obsidia cost is a local proxy estimate, not a measured provider bill.

---

## 2. Economie d'inference

- `model_call_avoided = True` : Obsidia route sans appel LLM.
- `available_surface` : familles ou Obsidia fonctionne sans ADAPTER_MISSING.
  Familles : ['BANK', 'FAST_PATH', 'GPS', 'TRADING']
- `adapter_missing_families` : ['BRODY', 'LEAN', 'OBSIDURE']
  Ces familles sont EXCLUES des victoires fonctionnelles.
- `external_dependency_reduction_score = 1.0` si model_call_avoided=True.

---

## 3. Economie intellectuelle (CALIBRATION_ONLY)

- `intellectual_economy_basis = CALIBRATION_ONLY`
- Scores calibration : cognitive_value, proof_quality, stability_value,
  reusability, governance_value, risk_reduction, friction_reduction,
  external_dependency_reduction, auditability, debt.
- Formule CV (PROVISIONAL_CALIBRATION_ONLY) :
  CV = wN*novelty + wU*utility + wC*coherence + wR*risk_reduction
       + wReuse*reusability + wP*proof_quality - debt
  Poids source : PROVISIONAL_CALIBRATION_ONLY
  Reference code : apps/obsidia_api/brody_gencoin_cognitive_ledger.py
- V(x) ∝ 1/(L(x) + epsilon) : doctrine uniquement, non implementee.

---

## 4. Gencoin — CALIBRATION_ONLY

- `gencoin_mode = CALIBRATION_ONLY`
- Aucune emission. Aucun token reel. Aucune valeur de marche.
- Aucune distribution. Aucun wallet. Aucune blockchain.
- `gencoin_emission_allowed = False` — invariant.
- `gencoin_emission_amount = 0` — toujours zero.
- `gencoin_distribution_mode = NONE_CALIBRATION_ONLY`
- Source law : non satisfaite en calibration benchmark.

---

## 5. Source law

- Source law est satisfaite uniquement si :
  - Preuve disponible (non ADAPTER_MISSING)
  - Gouvernance propre (emits_act=False, memory_write=False)
  - coherence_score >= 0.8
  - utility_score > 0.5
  - Mode REEL (non calibration)
- En benchmark CALIBRATION_ONLY : source_law_satisfied = False toujours.

---

## 6. Debt

- `debt_score` augmente si :
  - ADAPTER_MISSING : +0.50
  - Cout proxy non calibre : +0.20 (toujours dans benchmark)
  - Preuve manquante (ADAPTER_MISSING) : +0.20

---

## 7. Available surface

- Familles disponibles : ['BANK', 'FAST_PATH', 'GPS', 'TRADING']
- Familles ADAPTER_MISSING : ['BRODY', 'LEAN', 'OBSIDURE']
- BRODY, OBSIDURE, LEAN doivent etre exclues des victoires fonctionnelles.
- `adapter_missing_excluded_from_functional_victory = True`

---

## 8. Energie — proxy uniquement

> Energy values are proxy estimates unless hardware/provider telemetry is supplied.

- Variables env : OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS,
  OIE_LOCAL_POWER_W, OIE_CARBON_GCO2_PER_KWH.
- Sans ces variables : energy_source = ENERGY_PROXY_UNAVAILABLE.

---

## 9. Claims invalides

- INTERDIT : "Obsidia is smarter than Gemini"
- INTERDIT : "Obsidia is faster than all LLMs"
- INTERDIT : "Obsidia is a better language model"
- INTERDIT : "Obsidia produces better outputs than Gemini"
- INTERDIT : Ce benchmark prouve que Obsidia est moins cher en production.
- INTERDIT : Le cout Obsidia est mesure.
- INTERDIT : Gencoin a emis des tokens dans ce benchmark.

---

## 10. Rapports runtime

- Rapports runtime : `.local_reports/OIE_POWER_BENCHMARK_V0_7_1_<timestamp>/`
  - `results.json` — rows comparaison par famille
  - `summary.json` — summary global
  - `internal_economy.json` — scores economie intellectuelle
  - `gencoin_calibration.json` — layer Gencoin calibration
  - `summary.md` — rapport lisible
- Ce document est le seul fichier statique dans docs/audits.
