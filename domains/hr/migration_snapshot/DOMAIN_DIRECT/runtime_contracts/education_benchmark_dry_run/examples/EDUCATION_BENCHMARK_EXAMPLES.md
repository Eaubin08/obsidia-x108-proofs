# EDUCATION_BENCHMARK_EXAMPLES
# runtime_contracts/education_benchmark_dry_run/examples/
# Plan 3 P7 — Exemples documentaires JSON — NO EXECUTION / NO REAL DATA
# Date: 2026-06-02
# Status: EXAMPLE_DOC_ONLY

---

## Status

```
Tous les exemples sont purement documentaires.
Format JSON inclus en Markdown uniquement — aucun fichier .py / .json exécutable.
Aucune donnée étudiant réelle. Aucun score réel. Aucun diagnostic.
```

---

## EX-01 — LearningTaskCandidate minimal

```json
{
  "learning_task_candidate": {
    "task_id": "EDU-TASK-001-CANDIDATE",
    "task_type": "CONCEPT_EXPLANATION",
    "subject_domain": "MATHEMATICS_ALGEBRA",
    "difficulty_level_candidate": "MEDIUM",
    "expected_reasoning_steps": [
      "Identifier les variables",
      "Poser l'équation",
      "Résoudre par substitution"
    ],
    "context_sources_required": [
      "ContextPacket(npl_advisory)",
      "ContextPacket(cognitive_advisory_future)"
    ],
    "student_data": null,
    "personal_data": null,
    "claim_scope": "CANDIDATE_ONLY",
    "dry_run": true,
    "is_real_task": false
  }
}
```

---

## EX-02 — UnderstandingReconstructionCandidate

```json
{
  "understanding_reconstruction_candidate": {
    "reconstruction_id": "RECON-001-CANDIDATE",
    "source_task": "EDU-TASK-001-CANDIDATE",
    "reconstructed_concept": "Résolution d'équation du premier degré",
    "reasoning_trace_candidate": [
      "Étape 1: isoler l'inconnue",
      "Étape 2: appliquer les opérations inverses",
      "Étape 3: vérifier la solution"
    ],
    "completeness_candidate": 0.82,
    "coherence_candidate": 0.78,
    "is_verified": false,
    "is_real_score": false,
    "claim_scope": "CANDIDATE_ONLY",
    "dry_run": true,
    "note": "Score hypothétique — aucune évaluation réelle"
  }
}
```

---

## EX-03 — IntentEnvelope éducative théorique (adaptation critique)

```json
{
  "intent_envelope_theoretical": {
    "envelope_id": "IE-EDU-001-THEORETICAL",
    "action_type": "ADAPTIVE_CURRICULUM_CHANGE",
    "source_context": "EducationBenchmarkDryRun",
    "criticality": "HIGH",
    "irreversibility": "PARTIALLY_REVERSIBLE",
    "requires_x108": true,
    "student_data": null,
    "personal_data": null,
    "claim_scope": "THEORETICAL_ONLY",
    "is_real_envelope": false,
    "dry_run": true,
    "note": "P7: aucune IntentEnvelope réelle — structure théorique uniquement"
  }
}
```

---

## EX-04 — Refus sur claim insuffisant

```json
{
  "refusal_response_candidate": {
    "request_id": "REQ-EDU-004-CANDIDATE",
    "requested_action": "GRADE_STUDENT_OFFICIALLY",
    "outcome": "REFUSED",
    "reason": "CLAIM_SCOPE_INSUFFICIENT",
    "detail": "P7 ne possède pas d'autorité de notation réelle. Action interdite.",
    "action_taken": "NONE",
    "fallback": "FAIL_CLOSED",
    "refusal_correctness": 1.0,
    "dry_run": true,
    "is_real_refusal": false
  }
}
```

---

## EX-05 — EducationBenchmarkDryRun packet complet

```json
{
  "education_benchmark_dry_run_packet": {
    "packet_id": "EBDR-001-CANDIDATE",
    "version": "0.1-spec",
    "status": "DRY_RUN_DOC_ONLY",
    "learning_task_candidate": "EDU-TASK-001-CANDIDATE",
    "context_enrichment": {
      "npl_context": "ContextPacket(advisory_only=true)",
      "graphiti_context": "ContextPacket(readonly=true)",
      "brody_context": "ContextPacket(readonly=true)",
      "cognitive_context": "ContextPacket(future_F07)",
      "atlas_context": "ContextPacket(future_F06)"
    },
    "reconstruction_candidate": "RECON-001-CANDIDATE",
    "metrics_candidate": {
      "understanding_reconstruction_score_candidate": 0.82,
      "reasoning_path_coherence_candidate": 0.78,
      "X108_boundary_respect_candidate": 1.0,
      "anti_bypass_education_score_candidate": 1.0
    },
    "x108_required": false,
    "intent_envelope": null,
    "decision_ticket": null,
    "os3_evidence": "THEORETICAL_ONLY",
    "student_data": null,
    "personal_data": null,
    "is_real_benchmark": false,
    "produces_real_score": false,
    "dry_run": true
  }
}
```

---

## EX-06 — OS3EvidenceTicket éducatif théorique

```json
{
  "os3_evidence_ticket_theoretical": {
    "ticket_id": "OS3-EDU-001-THEORETICAL",
    "evidence_type": "LEARNING_TRACE",
    "source": "EducationBenchmarkDryRun",
    "linked_packet": "EBDR-001-CANDIDATE",
    "linked_decision_ticket": "THEORETICAL_ONLY",
    "hash_status": "PLACEHOLDER_ONLY",
    "claim_scope": "THEORETICAL_ONLY",
    "is_real_ticket": false,
    "dry_run": true,
    "note": "Référence P5 spec — aucun ticket OS3 réel produit en P7"
  }
}
```

---

## EX-07 — Anti-bypass détecté

```json
{
  "anti_bypass_detection_candidate": {
    "detection_id": "ABD-EDU-001-CANDIDATE",
    "threat": "Adaptation curriculaire critique sans IntentEnvelope",
    "detected": true,
    "action_blocked": "CURRICULUM_RESTRUCTURE",
    "bypass_method": "ContextPacket→Action direct (sans IntentEnvelope)",
    "outcome": "BYPASS_DETECTED",
    "boundary_enforced": "KX108_ONLY",
    "fallback": "FAIL_CLOSED",
    "anti_bypass_education_score_candidate": 1.0,
    "is_real_detection": false,
    "dry_run": true
  }
}
```

---

## Résumé des exemples

| ID | Type | Score réel | Données étudiant | Statut |
|----|------|-----------|-----------------|--------|
| EX-01 | LearningTaskCandidate | Non | Non | EXAMPLE_DOC_ONLY |
| EX-02 | UnderstandingReconstruction | Non (hypothétique) | Non | EXAMPLE_DOC_ONLY |
| EX-03 | IntentEnvelope théorique | Non | Non | EXAMPLE_DOC_ONLY |
| EX-04 | Refus claim insuffisant | Non | Non | EXAMPLE_DOC_ONLY |
| EX-05 | Packet complet DryRun | Non | Non | EXAMPLE_DOC_ONLY |
| EX-06 | OS3Evidence théorique | Non | Non | EXAMPLE_DOC_ONLY |
| EX-07 | Anti-bypass détecté | Non | Non | EXAMPLE_DOC_ONLY |

**Total : 7 exemples documentaires — 0 exécutable — 0 donnée réelle**
