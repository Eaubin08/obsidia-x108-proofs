# EDUCATION_BENCHMARK_FAILURE_MODES
# runtime_contracts/education_benchmark_dry_run/failure_modes/
# Plan 3 P7 Reconciliation Patch — Failure modes canoniques — 20 modes
# Date: 2026-06-02
# Status: FAILURE_MODES_SPEC_ONLY
# Refs: FAILURE_MODES_SPEC.md (10 modes initiaux — conservés)

---

## Règle globale

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f où adaptation critique : f → requires_x108_review
∀ failure mode f : f ↛ allow_by_default
```

---

## Catalog — 20 failure modes documentaires

| # | ID | Trigger | Response | fail_closed | no_act | x108_review | Critique |
|---|----|---------|---------|-----------|----|------------|---------|
| 1 | FM-CAT-01 | benchmark_claims_real_score | REFUSED | ✅ | ✅ | Non | Oui |
| 2 | FM-CAT-02 | benchmark_claims_real_comparison | REFUSED | ✅ | ✅ | Non | Non |
| 3 | FM-CAT-03 | benchmark_claims_student_grade | REFUSED | ✅ | ✅ | Non | Oui |
| 4 | FM-CAT-04 | benchmark_attempts_diagnosis | BLOCKED | ✅ | ✅ | Non | Oui |
| 5 | FM-CAT-05 | personal_data_collected | BLOCKED | ✅ | ✅ | Oui | Oui |
| 6 | FM-CAT-06 | memory_write_attempted | BLOCKED | ✅ | ✅ | Oui | Oui |
| 7 | FM-CAT-07 | graphiti_write_attempted | BLOCKED | ✅ | ✅ | Oui | Oui |
| 8 | FM-CAT-08 | brody_write_attempted | BLOCKED | ✅ | ✅ | Oui | Oui |
| 9 | FM-CAT-09 | tool_call_attempted | BLOCKED | ✅ | ✅ | Non | Oui |
| 10 | FM-CAT-10 | education_context_used_as_decision | REFUSED | ✅ | ✅ | Oui | Oui |
| 11 | FM-CAT-11 | benchmark_result_used_as_decision_ticket | REFUSED | ✅ | ✅ | Oui | Oui |
| 12 | FM-CAT-12 | missing_claim_scope | REJECTED | ✅ | ✅ | Non | Non |
| 13 | FM-CAT-13 | missing_os3_evidence_ref | FAIL_CLOSED (evidence) | ✅ | ✅ | Non | Non |
| 14 | FM-CAT-14 | x108_bypass_attempted | BLOCKED + BYPASS_DETECTED | ✅ | ✅ | Oui | Oui |
| 15 | FM-CAT-15 | NPL_used_as_learning_truth | REFUSED | ✅ | ✅ | Non | Non |
| 16 | FM-CAT-16 | cognitive_context_used_as_authority | REFUSED | ✅ | ✅ | Non | Non |
| 17 | FM-CAT-17 | atlas_context_used_as_reality_claim | REFUSED | ✅ | ✅ | Non | Non |
| 18 | FM-CAT-18 | source_pack_not_imported_claimed_active | REFUSED | ✅ | ✅ | Non | Non |
| 19 | FM-CAT-19 | metric_candidate_presented_as_real_metric | REFUSED | ✅ | ✅ | Non | Non |
| 20 | FM-CAT-20 | fail_open_on_education_boundary_violation | FAIL_CLOSED | ✅ | ✅ | Oui | Oui |

---

## Détail des 20 failure modes

### FM-CAT-01 — benchmark_claims_real_score

```yaml
failure_id: FM-CAT-01
trigger: "Benchmark tente de déclarer un score candidat comme score réel"
example: "score.is_real_score = true in P7 context"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: CANDIDATE_ONLY
fallback: "Retourner CANDIDATE_ONLY_ENFORCED"
never_allow_by_default: true
heritage: FM-03 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-02 — benchmark_claims_real_comparison

```yaml
failure_id: FM-CAT-02
trigger: "Benchmark compare ses résultats avec un autre système réel"
example: "claim: 'Obsidia est meilleur que X sur ce benchmark'"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: CANDIDATE_ONLY
fallback: "Retourner COMPARISON_NOT_AUTHORIZED_IN_P7"
never_allow_by_default: true
note: "Aucune comparaison réelle autorisée — aucun dataset réel disponible"
```

### FM-CAT-03 — benchmark_claims_student_grade

```yaml
failure_id: FM-CAT-03
trigger: "Benchmark émet une note officielle pour un étudiant"
example: "grade_official = '15/20'"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: NO_GRADING_AUTHORITY
fallback: "Retourner NO_GRADING_AUTHORITY_ENFORCED"
never_allow_by_default: true
heritage: FM-03 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-04 — benchmark_attempts_diagnosis

```yaml
failure_id: FM-CAT-04
trigger: "Benchmark pose un diagnostic éducatif, médical, ou scolaire"
example: "diagnosis = 'dyslexie détectée'"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: NO_DIAGNOSIS
fallback: "Retourner NO_DIAGNOSIS_AUTHORITY"
never_allow_by_default: true
```

### FM-CAT-05 — personal_data_collected

```yaml
failure_id: FM-CAT-05
trigger: "Données personnelles ou PII étudiant détectées dans l'input"
example: "input.student_id != null OR input.name != null"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: NO_STUDENT_DATA + NO_PERSONAL_DATA
rgpd_critical: true
x108_notify: true
fallback: "Retourner PERSONAL_DATA_DETECTED — requis F03+F10"
never_allow_by_default: true
heritage: FM-04 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-06 — memory_write_attempted

```yaml
failure_id: FM-CAT-06
trigger: "Tentative d'écriture générique en mémoire depuis le benchmark"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: NO_WOR
x108_notify: true
fallback: "Retourner MEMORY_WRITE_BLOCKED"
never_allow_by_default: true
heritage: FM-06 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-07 — graphiti_write_attempted

```yaml
failure_id: FM-CAT-07
trigger: "Tentative d'écriture spécifique dans Graphiti"
example: "graphiti.put(node, data)"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: READONLY_CONTEXT_ONLY + NO_WOR
x108_notify: true
fallback: "Retourner GRAPHITI_WRITE_BLOCKED"
never_allow_by_default: true
heritage: FM-06 (FAILURE_MODES_SPEC.md) — spécialisé Graphiti
```

### FM-CAT-08 — brody_write_attempted

```yaml
failure_id: FM-CAT-08
trigger: "Tentative d'écriture spécifique dans Brody"
example: "brody.post(entry, data)"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: READONLY_CONTEXT_ONLY + NO_WOR
x108_notify: true
fallback: "Retourner BRODY_WRITE_BLOCKED"
never_allow_by_default: true
heritage: FM-06 (FAILURE_MODES_SPEC.md) — spécialisé Brody
```

### FM-CAT-09 — tool_call_attempted

```yaml
failure_id: FM-CAT-09
trigger: "Appel d'outil actif (non-readonly) depuis le contexte éducatif"
example: "call_tool(write_db, ...)"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
boundary: NO_ACT_FROM_PERIPHERY
fallback: "Retourner TOOL_CALL_FORBIDDEN_FROM_PERIPHERY"
never_allow_by_default: true
```

### FM-CAT-10 — education_context_used_as_decision

```yaml
failure_id: FM-CAT-10
trigger: "Un ContextPacket éducatif est utilisé pour prendre une décision irréversible sans X108"
example: "context_packet → curriculum_change direct"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: KX108_ONLY + NO_ACT_FROM_PERIPHERY
x108_notify: true
fallback: "Retourner CONTEXT_CANNOT_DECIDE"
never_allow_by_default: true
heritage: FM-02 (FAILURE_MODES_SPEC.md) — étendu
```

### FM-CAT-11 — benchmark_result_used_as_decision_ticket

```yaml
failure_id: FM-CAT-11
trigger: "Résultat du benchmark présenté directement comme DecisionTicket X108"
example: "benchmark_result.promote_to_decision_ticket()"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: KX108_ONLY
x108_notify: true
fallback: "Retourner BENCHMARK_CANNOT_ISSUE_DECISION_TICKET"
never_allow_by_default: true
note: "Seul X108 peut émettre un DecisionTicket"
```

### FM-CAT-12 — missing_claim_scope

```yaml
failure_id: FM-CAT-12
trigger: "Objet produit sans champ claim_scope explicite"
example: "score_object.claim_scope == null"
response: REJECTED
action_taken: NONE — objet ignoré
boundary: CANDIDATE_ONLY
fallback: "Retourner CLAIM_SCOPE_MISSING"
never_allow_by_default: true
heritage: FM-09 (FAILURE_MODES_SPEC.md) — généralisé
```

### FM-CAT-13 — missing_os3_evidence_ref

```yaml
failure_id: FM-CAT-13
trigger: "Trace d'audit critique sans référence OS3EvidenceTicket"
example: "critical_learning_trace.os3_ref == null"
response: FAIL_CLOSED (sur la trace)
action_taken: NONE — trace marquée INCOMPLETE
boundary: OS3_EVIDENCE_REQUIRED_IF_CRITICAL
fallback: "Retourner OS3_EVIDENCE_REF_MISSING"
never_allow_by_default: true
heritage: FM-08 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-14 — x108_bypass_attempted

```yaml
failure_id: FM-CAT-14
trigger: "Adaptation curriculaire critique déclenchée sans passer par X108"
example: "action.criticality=HIGH AND intent_envelope==null"
response: BLOCKED + BYPASS_DETECTED + FAIL_CLOSED
action_taken: NONE
boundary: KX108_ONLY
x108_notify: true
anti_bypass: true
fallback: "Retourner X108_BYPASS_DETECTED"
never_allow_by_default: true
heritage: FM-02 + FM-10 (FAILURE_MODES_SPEC.md)
```

### FM-CAT-15 — NPL_used_as_learning_truth

```yaml
failure_id: FM-CAT-15
trigger: "Signal NPL utilisé comme vérité scolaire absolue"
example: "npl_signal.is_ground_truth = true"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: NPL_ADVISORY_ONLY
fallback: "Retourner NPL_IS_ADVISORY_NOT_TRUTH"
never_allow_by_default: true
note: "NPL = advisory uniquement — jamais autorité de vérité"
```

### FM-CAT-16 — cognitive_context_used_as_authority

```yaml
failure_id: FM-CAT-16
trigger: "Contexte Cognitive advisory présenté comme autorité de décision"
example: "cognitive_context.authority_level = DECISION"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: COGNITIVE_ADVISORY_ONLY
fallback: "Retourner COGNITIVE_IS_ADVISORY_ONLY"
never_allow_by_default: true
note: "Cognitive = advisory futur (F07) — jamais autorité de décision"
```

### FM-CAT-17 — atlas_context_used_as_reality_claim

```yaml
failure_id: FM-CAT-17
trigger: "Scénario Atlas présenté comme réalité scolaire établie"
example: "atlas_scenario.is_real_situation = true"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: ATLAS_READONLY_ADVISORY
fallback: "Retourner ATLAS_IS_SCENARIO_NOT_REALITY"
never_allow_by_default: true
note: "Atlas = scénario advisory futur (F06) — pas de claim de réalité"
```

### FM-CAT-18 — source_pack_not_imported_claimed_active

```yaml
failure_id: FM-CAT-18
trigger: "Source pack référencé comme actif alors qu'il n'est pas importé"
example: "cognitive_context claimed active WITHOUT F07 import"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner SOURCE_PACK_NOT_ACTIVE — vérifier F07/F06"
never_allow_by_default: true
note: "Un source pack non importé ne peut pas être présenté comme actif"
```

### FM-CAT-19 — metric_candidate_presented_as_real_metric

```yaml
failure_id: FM-CAT-19
trigger: "Métrique candidate promue en métrique réelle officielle"
example: "understanding_reconstruction_score_candidate.promote_to_official()"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
boundary: CANDIDATE_ONLY
fallback: "Retourner METRIC_IS_CANDIDATE_ONLY"
never_allow_by_default: true
heritage: FM-CAT-01 (spécialisé métriques)
```

### FM-CAT-20 — fail_open_on_education_boundary_violation

```yaml
failure_id: FM-CAT-20
trigger: "Tentative de retourner allow=true sur une violation de boundary éducative"
example: "boundary_check.default = ALLOW (INTERDIT)"
response: FAIL_CLOSED forcé
action_taken: NONE
boundary: FAIL_CLOSED_PRIORITY
fallback: "Retourner FAIL_OPEN_FORBIDDEN — boundary_check.default = DENY"
never_allow_by_default: true
note: "CRITIQUE — fail_open est TOUJOURS interdit pour les boundaries éducatives"
```

---

## Résumé

| Catégorie | Failure modes | IDs |
|-----------|-------------|-----|
| Score / claim scope | 4 | FM-CAT-01..03, FM-CAT-12 |
| Données / RGPD | 1 | FM-CAT-05 |
| Écriture mémoire | 3 | FM-CAT-06..08 |
| Outil / action | 2 | FM-CAT-09, FM-CAT-20 |
| Décision / autorité | 4 | FM-CAT-10..11, FM-CAT-15..16 |
| Contexte mal utilisé | 3 | FM-CAT-17..19 |
| Anti-bypass | 2 | FM-CAT-14, FM-CAT-04 |
| Diagnostic / grading | 1 | FM-CAT-13 |
| **Total** | **20** | FM-CAT-01..20 |

```
Total failure modes canoniques : 20
Règle globale : FAIL_CLOSED — 0 allow_by_default
```
