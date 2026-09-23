# EDUCATION_BENCHMARK_PIPELINE_SPEC
# runtime_contracts/education_benchmark_dry_run/pipeline/
# Plan 3 P7 — Pipeline documentaire — NO EXECUTION
# Date: 2026-06-02
# Status: PIPELINE_SPEC_ONLY

---

## Status

```
Pipeline documentaire uniquement.
Aucun pipeline exécuté en P7.
Aucune donnée réelle traitée.
X108 = seul droit de passage pour adaptation critique.
```

---

## Vue d'ensemble

```
StudentTaskCandidate
  + LearningContextPacket
  + Graphiti/Brody/NPL readonly context (P6 spec)
  + Cognitive advisory context future (F07)
  + Atlas scenario context future (F06)
  + OS3EvidenceTicket theoretical binding (P5)
        ↓
  EducationBenchmarkDryRun SPEC (P7)
        ↓
  [Si adaptation critique]
  IntentEnvelope → X108 Gateway Dry-Run Harness (P3)
        ↓
  theoretical DecisionTicket
        ↓
  OS3EvidenceTicket theoretical
        ↓
  NO_REAL_STUDENT_ACTION
  NO_REAL_SCORE_CLAIM
```

---

## Étape 1 — Construction LearningContextPacket

```yaml
step: 1
name: "LearningContextPacket construction"
status: PIPELINE_SPEC_ONLY

inputs_candidate:
  - LearningTaskCandidate (no student data)
  - ContextPacket(npl_advisory, P6 wrapper)
  - ContextPacket(graphiti_readonly, P6 wrapper)
  - ContextPacket(brody_readonly, P6 wrapper)
  - ContextPacket(cognitive_advisory_future, F07)
  - ContextPacket(atlas_scenario_future, F06)

outputs_candidate:
  - LearningContextPacket enriched

boundaries:
  - NO_STUDENT_DATA
  - READONLY_CONTEXT_ONLY
  - NPL_ADVISORY_ONLY

failure_modes: [FM-01]
```

---

## Étape 2 — Reconstruction et métriques candidates

```yaml
step: 2
name: "Understanding reconstruction + metrics evaluation"
status: PIPELINE_SPEC_ONLY

inputs_candidate:
  - LearningContextPacket (étape 1)
  - LearningTaskCandidate

outputs_candidate:
  - UnderstandingReconstructionCandidate
  - CognitivePahtReconstructionCandidate
  - MetricsCandidate (scores hypothétiques)

boundaries:
  - NO_REAL_SCORE
  - NO_DIAGNOSIS
  - NO_GRADING_AUTHORITY
  - CANDIDATE_ONLY

failure_modes: [FM-03, FM-09]
```

---

## Étape 3 — Gate critique (conditionnel)

```yaml
step: 3
name: "Critical adaptation gate — X108 if required"
status: PIPELINE_SPEC_ONLY
condition: "criticality == HIGH OR irreversibility != REVERSIBLE"

inputs_candidate:
  - UnderstandingReconstructionCandidate
  - Adaptation request (si présente)

outputs_candidate:
  - IntentEnvelope (THEORETICAL_ONLY si adaptation critique)
  - X108 Gateway call (THEORETICAL_ONLY)
  - DecisionTicket (THEORETICAL_ONLY)

boundary: KX108_ONLY
failure_modes: [FM-02, FM-05, FM-10]
note: "Si pas d'adaptation critique → étape 3 skippée"
```

---

## Étape 4 — OS3 Evidence trace théorique

```yaml
step: 4
name: "OS3 evidence trace — theoretical"
status: PIPELINE_SPEC_ONLY

inputs_candidate:
  - EducationBenchmarkDryRun packet
  - DecisionTicket (si étape 3 exécutée)

outputs_candidate:
  - OS3EvidenceTicket (THEORETICAL_ONLY)

claim_scope: THEORETICAL_ONLY
failure_modes: [FM-08]
note: "P7: trace théorique uniquement — référence P5 spec"
```

---

## Étape 5 — Refus et boundaries

```yaml
step: 5
name: "Boundary enforcement — refusal and fail_closed"
status: PIPELINE_SPEC_ONLY
trigger: "Toute violation de boundary"

boundaries_enforced:
  - NO_ACT_FROM_PERIPHERY
  - NO_STUDENT_DATA
  - NO_PERSONAL_DATA
  - NO_DIAGNOSIS
  - NO_GRADING_AUTHORITY
  - KX108_ONLY (adaptation critique)
  - NO_WOR (écriture mémoire)
  - FAIL_CLOSED_PRIORITY

failure_modes: [FM-02, FM-03, FM-04, FM-06, FM-07, FM-10]
response: FAIL_CLOSED + log
```

---

## Non-executable status

```
❌ Ce pipeline n'est PAS exécutable en P7
❌ Aucun étudiant réel ne passe par ce pipeline
❌ Aucun score réel n'est produit par ce pipeline
❌ Aucune donnée personnelle n'est traitée
❌ Aucun diagnostic n'est posé
❌ Aucune notation réelle n'est effectuée

Le pipeline exécutable sera créé uniquement après :
  1. P7 spec validé (ce run)
  2. Gate humaine explicite
  3. F07 Cognitive + F06 Atlas imports validés
  4. F03 + F10 RGPD review
  5. Données synthétiques ou consenties disponibles
```

---

## Relation avec contrats existants

| Contrat | Rôle dans le pipeline |
|---------|----------------------|
| ContextPacket.contract.md | Étapes 1, 2, 3 |
| IntentEnvelope.contract.md | Étape 3 (conditionnel) |
| DecisionTicket.contract.md | Étape 3 (X108 output) |
| OS3EvidenceTicket.contract.md | Étape 4 |
| BoundaryContract.contract.md | Étape 5 |
| RuntimeAdmissionContract.contract.md | Gate d'admission SPEC→DRY_RUN |

---

## Relation avec P6

```
P6 ReadOnly Wrappers → fournissent les ContextPackets en étape 1
P6 wrappers = SPEC ONLY — aucun appel réel en P7
P7 décrit comment les wrappers P6 seront utilisés dans le pipeline futur
```
