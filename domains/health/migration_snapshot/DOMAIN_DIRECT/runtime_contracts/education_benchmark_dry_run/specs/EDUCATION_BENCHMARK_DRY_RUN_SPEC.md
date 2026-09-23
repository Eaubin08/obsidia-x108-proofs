# EDUCATION_BENCHMARK_DRY_RUN_SPEC
# runtime_contracts/education_benchmark_dry_run/specs/
# Plan 3 P7 — Spec documentaire uniquement — NO BENCHMARK / NO SCORE / NO STUDENT DATA
# Date: 2026-06-02
# Status: EDUCATION_BENCHMARK_SPEC_ONLY / DRY_RUN_DOCUMENTATION_ONLY

---

## 1. Purpose

Ce document spécifie la structure documentaire du futur Education Benchmark Dry-Run d'Obsidia X-108.

L'Education Benchmark Dry-Run mesure, en mode documentaire, comment Obsidia peut structurer,
reconstruire, et tracer des chemins de compréhension et de raisonnement dans un contexte éducatif.

En P7, ce document décrit uniquement la **forme théorique** du benchmark.
Aucun score réel n'est produit. Aucun élève réel n'est évalué. Aucune donnée personnelle.
Aucun diagnostic. Aucune décision scolaire.

---

## 2. Status

```
Status:                     EDUCATION_BENCHMARK_SPEC_ONLY
Benchmark execution:        NO
Score réel:                 NO
Student data:               NO
Personal data:              NO
Diagnostic:                 NO
Grading authority:          NO
Memory write:               NO
Graphiti write:             NO
Brody write:                NO
Tool call:                  NO
Python files:               NO
Runtime execution:          NO
Test execution:             NO
Packages:                   NO
Commit:                     NO
Push:                       NO
```

---

## 3. Scope

| Dimension | Description | Status |
|-----------|-------------|--------|
| Compréhension structurée | Reconstruction de concept sans donnée réelle | SPEC_ONLY |
| Chemin de raisonnement | Trace de logique documentaire | SPEC_ONLY |
| Réduction cognitive | Simplification advisory documentaire | SPEC_ONLY |
| Pédagogie adaptative | Ajustement contextuel documentaire | SPEC_ONLY |
| Traçabilité OS3 | Evidence trace théorique | THEORETICAL_ONLY (P5) |
| Anti-bypass éducatif | Vérification que le benchmark ne bypasse pas X108 | SPEC_ONLY (P4) |
| Contexte Graphiti/Brody/NPL | Readonly context future | WRAPPER_SPEC_ONLY (P6) |
| Contexte Cognitive/Atlas | Future advisory context | COPIED_READONLY — F07/F06 |

---

## 4. Non-executable status

P7 crée uniquement :
- Fichiers `.md` documentaires
- Zéro fichier `.py`
- Zéro benchmark exécuté
- Zéro score calculé
- Zéro données étudiants collectées
- Zéro diagnostic posé
- Zéro notation réelle

Le futur benchmark exécutable sera créé uniquement après :
1. Plan 3 P7 Spec validé (ce run)
2. Gate humaine explicite
3. F07 Cognitive + F06 Atlas imports
4. Plan 3 P6 wrappers readonly actifs
5. Revue RGPD des données étudiants (F03+F10)

---

## 5. Education benchmark model

```
EducationBenchmarkDryRun = mesure documentaire candidate, non exécutée

Propriétés fondamentales :
  is_real_benchmark = false
  produces_real_score = false
  contains_student_data = false
  diagnostic_authority = NONE
  grading_authority = NONE
  memory_write = false
  graph_write = false
  decision_authority = KX108_ONLY (si adaptation critique)
  world_action = false
  advisory_only = true
  dry_run = true
```

---

## 6. Learning task candidate model

```yaml
learning_task_candidate:
  task_id: "EDU-TASK-<uuid>-CANDIDATE"
  task_type: "CONCEPT_EXPLANATION | REASONING_PATH | MISCONCEPTION | ADAPTIVE_HINT"
  subject_domain: "<domain_placeholder>"
  difficulty_level_candidate: "LOW | MEDIUM | HIGH"
  expected_reasoning_steps: [<step_1_doc>, <step_2_doc>]
  context_sources_required:
    - ContextPacket (NPL advisory future)
    - ContextPacket (Cognitive advisory future — F07)
    - ContextPacket (Atlas scenario future — F06)
  student_data: null   # JAMAIS en P7
  personal_data: null  # JAMAIS en P7
  claim_scope: CANDIDATE_ONLY
  dry_run: true
  is_real_task: false
```

---

## 7. Understanding reconstruction model

```yaml
understanding_reconstruction_candidate:
  reconstruction_id: "RECON-<uuid>-CANDIDATE"
  source_task: "<task_id>-CANDIDATE"
  reconstructed_concept: "<concept_placeholder>"
  reasoning_trace_candidate: [<step_1>, <step_2>]
  completeness_candidate: 0.0-1.0   # score hypothétique non réel
  coherence_candidate: 0.0-1.0
  is_verified: false
  is_real_score: false
  claim_scope: CANDIDATE_ONLY
  dry_run: true
  note: "Score hypothétique uniquement — aucune évaluation réelle en P7"
```

---

## 8. Cognitive path reconstruction model

```yaml
cognitive_path_reconstruction_candidate:
  path_id: "PATH-<uuid>-CANDIDATE"
  source_reconstruction: "<recon_id>-CANDIDATE"
  steps_candidate:
    - step: 1
      description: "<step_doc_placeholder>"
      context_refs: ["CP-NPL-ADVISORY", "CP-COGNITIVE-FUTURE"]
      expected_reasoning: "<expected_placeholder>"
      actual_reasoning: null   # pas d'exécution en P7
  path_coherence_candidate: 0.0-1.0   # hypothétique
  reduction_quality_candidate: 0.0-1.0
  is_executable: false
  dry_run: true
```

---

## 9. Metrics candidate model

Voir `metrics/EDUCATION_METRICS_CANDIDATE_SPEC.md` pour le détail.

Règle : tous les scores sont CANDIDATE_ONLY — aucun score réel en P7.

```
understanding_reconstruction_score_candidate:  0.0-1.0 (hypothétique)
reasoning_path_coherence_candidate:           0.0-1.0
explanation_trace_completeness_candidate:     0.0-1.0
misconception_signal_quality_candidate:       0.0-1.0
cognitive_reduction_quality_candidate:        0.0-1.0
context_grounding_quality_candidate:          0.0-1.0
refusal_correctness_candidate:                0.0-1.0
evidence_trace_completeness_candidate:        0.0-1.0
benchmark_replayability_candidate:            0.0-1.0
X108_boundary_respect_candidate:              0.0-1.0 (CRITIQUE)
```

---

## 10. Required contracts

| Contrat | Rôle dans P7 |
|---------|-------------|
| ContextPacket.contract.md | Sources Graphiti/Brody/NPL/Cognitive/Atlas |
| PeripheralSignalPacket.contract.md | Métriques advisory NPL/Cognitive |
| IntentEnvelope.contract.md | Si adaptation critique → X108 gate |
| DecisionTicket.contract.md | X108 si adaptation irréversible |
| OS3EvidenceTicket.contract.md | Evidence trace théorique future |
| BoundaryContract.contract.md | Droits du benchmark |
| RuntimeAdmissionContract.contract.md | Admission SPEC→DRY_RUN |

---

## 11. Required schemas

| Schema | Usage |
|--------|-------|
| context_packet.schema.json | Validation ContextPackets éducatifs |
| peripheral_signal_packet.schema.json | Métriques advisory |
| intent_envelope.schema.json | Si adaptation critique |
| os3_evidence_ticket.schema.json | Evidence trace théorique |

---

## 12. Required boundaries

| Boundary | Rôle |
|----------|------|
| X108_GATEWAY_REQUIRED | Si adaptation critique → X108 obligatoire |
| NO_ACT_FROM_PERIPHERY | Benchmark ne déclenche aucun ACT |
| READONLY_CONTEXT_ONLY | Graphiti/Brody = lecture seule |
| NPL_ADVISORY_ONLY | NPL = advisory uniquement |
| COGNITIVE_REINTEGRATION_ADVISORY_ONLY | Cognitive = advisory future |
| ATLAS_READONLY_ADVISORY_ONLY | Atlas = readonly advisory future |
| FAIL_CLOSED_PRIORITY | Failure → fail_closed |
| RGPD_COMPLIANCE_SCOPE_GUARD | Données étudiants = RGPD protégé |

---

## 13. Link to ContextPacket

```yaml
education_context_sources:
  npl_context: ContextPacket(source_layer=npl, advisory_only=true)   # P6 spec
  graphiti_context: ContextPacket(source_layer=graphiti, readonly=true)  # P6 spec
  brody_context: ContextPacket(source_layer=brody, readonly=true)    # P6 spec
  cognitive_context: ContextPacket (future F07)   # COPIED_READONLY
  atlas_context: ContextPacket (future F06)       # COPIED_READONLY

  # Ces contextes enrichissent LearningTaskCandidate
  # Ils ne notent pas, ne diagnostiquent pas, ne décident pas
```

---

## 14. Link to IntentEnvelope

```yaml
intent_envelope_link:
  condition: "Si adaptation critique → gate X108 requise"
  example:
    action_type: "ADAPTIVE_CURRICULUM_CHANGE"
    irreversibility: "PARTIALLY_REVERSIBLE"
    criticality: "MEDIUM"
    requires_x108: true
  
  note_p7: "En P7 — aucune IntentEnvelope réelle produite — THEORETICAL_ONLY"
  note_no_grading: "La notation d'un élève n'est JAMAIS une IntentEnvelope en P7"
```

---

## 15. Link to X108 Gateway

```yaml
x108_gateway_link:
  trigger_condition: "adaptation/action curriculaire critique"
  non_trigger: "scoring, evaluation, context enrichment (ces opérations ne passent pas par X108)"
  
  claim_p7: "aucun appel X108 réel en P7 — THEORETICAL_ONLY"
  boundary: "X108_GATEWAY_REQUIRED pour toute action curriculaire irréversible"
```

---

## 16. Link to OS3EvidenceTicket

```yaml
os3_evidence_link:
  evidence_type: "LEARNING_TRACE | BENCHMARK_AUDIT_TRACE"
  source: "education_benchmark_dry_run (P7 SPEC_ONLY)"
  linked_decision_ticket: "THEORETICAL_ONLY"
  hash_status: "PLACEHOLDER_ONLY"
  claim_scope: "THEORETICAL_ONLY"
  dry_run: true
  note: "P7 référence P5 spec pour OS3Evidence. Aucun ticket réel produit."
```

---

## 17. Allowed operations (P7)

```
✅ Créer fichiers .md documentaires dans education_benchmark_dry_run/
✅ Décrire la forme théorique des tâches éducatives
✅ Documenter les métriques candidates (non réelles)
✅ Créer exemples JSON documentaires en Markdown
✅ Lier aux contrats et boundaries existants
✅ Documenter les scénarios anti-bypass éducatifs
```

---

## 18. Forbidden operations (P7)

```
❌ Benchmark exécutable
❌ Score réel d'un étudiant
❌ Donnée personnelle / étudiant
❌ Diagnostic éducatif
❌ Notation réelle
❌ Écriture mémoire
❌ Écriture Graphiti/Brody
❌ Fichier .py
❌ Comparaison réelle entre systèmes
❌ Claim "meilleur que X"
❌ Décision scolaire
❌ ACT
❌ Committer ou pousser
```

---

## 19. Failure handling

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f → requires_x108_review (si adaptation critique)
∀ failure mode f : f ↛ allow_by_default
```

---

## 20. Claim-scope

| Composant | Claim autorisé en P7 |
|-----------|---------------------|
| Scores | CANDIDATE_ONLY — non calculés |
| Benchmark | SPEC_ONLY — non exécuté |
| Diagnostic | JAMAIS — NO_DIAGNOSIS |
| Student data | JAMAIS — NO_STUDENT_DATA |
| Comparaisons | JAMAIS — pas de comparaison réelle |
| OS3Evidence | THEORETICAL_ONLY (P5) |

---

## 21. Future implementation gates

| Gate | Prérequis |
|------|-----------|
| Benchmark exécutable | P7 Spec ✅ + gate humaine + F07+F06 |
| Données étudiants | RGPD review (F03+F10) + consentement |
| Scores réels | Benchmark exécutable + validation humaine |
| Comparaison réelle | Scores réels + dataset validé |
| Lean proof benchmark | Post-benchmark + P13/P17 |

---

## 22. Tests required later

```
test_benchmark_no_student_data
test_benchmark_no_real_score
test_benchmark_no_diagnosis
test_benchmark_no_grading_authority
test_benchmark_cannot_write_memory
test_benchmark_anti_bypass_education
test_x108_gate_on_critical_adaptation
test_os3_evidence_education_trace
```

---

## 23. Proof expected later

```
Lean proofs attendus :
  benchmark_no_student_harm_proof
  education_non_sovereign_proof

TLA+ specs attendues :
  EducationBenchmarkInvariant.tla
  NoDiagnosisProperty.tla
```
