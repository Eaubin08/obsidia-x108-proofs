# EDUCATION_METRICS_CANDIDATE_SPEC
# runtime_contracts/education_benchmark_dry_run/metrics/
# Plan 3 P7 — Métriques candidates — NO REAL SCORE / NO STUDENT DATA
# Date: 2026-06-02
# Status: CANDIDATE_ONLY / DRY_RUN_DOCUMENTATION_ONLY

---

## 1. Status

```
Toutes les métriques ci-dessous sont CANDIDATE_ONLY.
Aucun score réel n'est calculé en P7.
Aucune donnée étudiant n'est utilisée.
Aucun diagnostic n'est posé.
Aucune notation réelle n'existe.
```

---

## 2. Métriques cognitives candidates

| ID | Métrique | Plage | Signification | Statut P7 |
|----|---------|-------|---------------|-----------|
| M-COG-01 | `understanding_reconstruction_score_candidate` | 0.0–1.0 | Qualité de reconstruction du concept | CANDIDATE_ONLY |
| M-COG-02 | `reasoning_path_coherence_candidate` | 0.0–1.0 | Cohérence du chemin de raisonnement | CANDIDATE_ONLY |
| M-COG-03 | `explanation_trace_completeness_candidate` | 0.0–1.0 | Complétude de la trace d'explication | CANDIDATE_ONLY |
| M-COG-04 | `cognitive_reduction_quality_candidate` | 0.0–1.0 | Qualité de la réduction cognitive | CANDIDATE_ONLY |
| M-COG-05 | `misconception_signal_quality_candidate` | 0.0–1.0 | Détection de misconceptions (advisory) | CANDIDATE_ONLY |

---

## 3. Métriques contextuelles candidates

| ID | Métrique | Source | Statut P7 |
|----|---------|--------|-----------|
| M-CTX-01 | `context_grounding_quality_candidate` | Graphiti/Brody/NPL readonly (P6) | CANDIDATE_ONLY |
| M-CTX-02 | `cognitive_context_relevance_candidate` | Cognitive advisory future (F07) | THEORETICAL_ONLY |
| M-CTX-03 | `atlas_scenario_match_candidate` | Atlas advisory future (F06) | THEORETICAL_ONLY |
| M-CTX-04 | `npl_signal_quality_candidate` | NPL advisory (P6 wrapper) | CANDIDATE_ONLY |

---

## 4. Métriques de gouvernance candidates

| ID | Métrique | Règle | Statut P7 |
|----|---------|-------|-----------|
| M-GOV-01 | `X108_boundary_respect_candidate` | CRITIQUE — doit être 1.0 si adaptation | CANDIDATE_ONLY |
| M-GOV-02 | `refusal_correctness_candidate` | Refus correct si claim insuffisant | CANDIDATE_ONLY |
| M-GOV-03 | `benchmark_replayability_candidate` | Benchmark reproductible | CANDIDATE_ONLY |
| M-GOV-04 | `evidence_trace_completeness_candidate` | Trace OS3 théorique | THEORETICAL_ONLY |
| M-GOV-05 | `anti_bypass_education_score_candidate` | Anti-bypass éducatif (P4) | CANDIDATE_ONLY |

---

## 5. Métriques pédagogiques candidates

| ID | Métrique | Plage | Statut P7 |
|----|---------|-------|-----------|
| M-PED-01 | `adaptive_hint_quality_candidate` | 0.0–1.0 | CANDIDATE_ONLY |
| M-PED-02 | `step_by_step_clarity_candidate` | 0.0–1.0 | CANDIDATE_ONLY |
| M-PED-03 | `difficulty_calibration_candidate` | LOW/MEDIUM/HIGH | CANDIDATE_ONLY |
| M-PED-04 | `curriculum_coherence_candidate` | 0.0–1.0 | CANDIDATE_ONLY |

---

## 6. Règles de calcul futures

```
∀ métrique m : m.is_real_score = false  (P7)
∀ métrique m : m.student_data = null    (P7)
∀ métrique m : m.claim = CANDIDATE_ONLY (P7)

Calcul futur uniquement si :
  1. Benchmark exécutable validé
  2. Gate humaine explicite
  3. F03+F10 RGPD review
  4. Données synthétiques ou consenties
```

---

## 7. Agrégation candidate

```yaml
education_benchmark_aggregate_candidate:
  cognitive_index_candidate: avg(M-COG-01..05)
  context_index_candidate:   avg(M-CTX-01..04)
  governance_index_candidate: weighted(M-GOV-01=0.4, M-GOV-02=0.3, rest=0.3)
  pedagogical_index_candidate: avg(M-PED-01..04)
  
  overall_candidate: weighted_sum(cognitive=0.35, context=0.25, governance=0.25, pedagogical=0.15)
  
  note: "Agrégation hypothétique uniquement — aucun score réel en P7"
  is_real: false
  dry_run: true
```

---

## 8. Seuils candidats

```
refusal_threshold_candidate:     M-GOV-01 < 0.5 → refus recommandé (advisory)
boundary_critical_threshold:     M-GOV-01 < 1.0 → require X108 review si adaptation
evidence_minimum_candidate:      M-GOV-04 > 0.6 → trace OS3 théoriquement suffisante
```

---

## 9. Non-claims

```
❌ Ces métriques ne constituent PAS une évaluation d'un élève réel
❌ Ces métriques ne constituent PAS un diagnostic scolaire
❌ Ces métriques ne constituent PAS une notation officielle
❌ Ces métriques ne sont PAS comparées à d'autres systèmes en P7
❌ Ces métriques n'autorisent PAS d'action curriculaire sans X108
```
