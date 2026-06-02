# EDUCATION_BOUNDARY_SPEC
# runtime_contracts/education_benchmark_dry_run/boundary/
# Plan 3 P7 — Boundaries éducatives — SPEC_ONLY
# Date: 2026-06-02
# Status: BOUNDARY_SPEC_ONLY

---

## Boundaries actives en P7

| ID | Boundary | Portée | Priorité |
|----|---------|--------|---------|
| B-EDU-01 | KX108_ONLY | Toute adaptation curriculaire critique | CRITIQUE |
| B-EDU-02 | NO_ACT_FROM_PERIPHERY | Benchmark ne déclenche aucun ACT | CRITIQUE |
| B-EDU-03 | READONLY_CONTEXT_ONLY | Graphiti/Brody/NPL = lecture seule | CRITIQUE |
| B-EDU-04 | NPL_ADVISORY_ONLY | NPL = advisory uniquement | HAUTE |
| B-EDU-05 | COGNITIVE_ADVISORY_ONLY | Cognitive future = advisory uniquement | HAUTE |
| B-EDU-06 | ATLAS_READONLY_ADVISORY | Atlas future = readonly advisory | HAUTE |
| B-EDU-07 | FAIL_CLOSED_PRIORITY | Failure → fail_closed | CRITIQUE |
| B-EDU-08 | RGPD_SCOPE_GUARD | Données étudiants = RGPD protégé | CRITIQUE |
| B-EDU-09 | NO_DIAGNOSIS | Aucun diagnostic éducatif autorisé | CRITIQUE |
| B-EDU-10 | NO_GRADING_AUTHORITY | Aucune notation officielle | CRITIQUE |
| B-EDU-11 | CANDIDATE_ONLY | Scores = hypothétiques uniquement | HAUTE |
| B-EDU-12 | NO_STUDENT_DATA | Données étudiant = interdites en P7 | CRITIQUE |
| B-EDU-13 | NO_PERSONAL_DATA | Données personnelles = interdites en P7 | CRITIQUE |
| B-EDU-14 | BENCHMARK_SPEC_ONLY | Aucun benchmark exécutable en P7 | HAUTE |
| B-EDU-15 | NON_SOVEREIGN_BENCHMARK | Benchmark ≠ certifié scolaire | CRITIQUE |

---

## B-EDU-01 — KX108_ONLY

```yaml
boundary_id: B-EDU-01
name: KX108_ONLY
scope: "Adaptation curriculaire critique, irréversible"
rule: "Toute adaptation critique DOIT passer par X108 Gateway"
trigger: "criticality=HIGH OR irreversibility!=REVERSIBLE"
fallback: FAIL_CLOSED
failure_mode: FM-02
anti_bypass: ABP-05
```

---

## B-EDU-09 — NO_DIAGNOSIS

```yaml
boundary_id: B-EDU-09
name: NO_DIAGNOSIS
scope: "Toute opération éducative"
rule: "Le benchmark n'est JAMAIS autorisé à poser un diagnostic éducatif, médical, ou scolaire"
examples_forbidden:
  - "Cet élève a un trouble de l'apprentissage"
  - "L'étudiant est en échec scolaire"
  - "Niveau de compréhension insuffisant pour passer en classe supérieure"
fallback: REFUSED + FAIL_CLOSED
failure_mode: FM-03
```

---

## B-EDU-10 — NO_GRADING_AUTHORITY

```yaml
boundary_id: B-EDU-10
name: NO_GRADING_AUTHORITY
scope: "Toute opération éducative"
rule: "Le benchmark n'est JAMAIS autorisé à émettre une note officielle"
examples_forbidden:
  - "Score final: 15/20"
  - "Mention: Bien"
  - "Validé pour l'UE"
fallback: REFUSED + FAIL_CLOSED
failure_mode: FM-03
```

---

## B-EDU-15 — NON_SOVEREIGN_BENCHMARK

```yaml
boundary_id: B-EDU-15
name: NON_SOVEREIGN_BENCHMARK
scope: "Toute utilisation du benchmark"
rule: "Le benchmark Obsidia ne possède AUCUNE souveraineté scolaire"
detail:
  - Ne remplace pas un enseignant
  - Ne remplace pas un jury d'examen
  - Ne remplace pas une institution scolaire
  - N'a aucune valeur légale
  - N'est pas certifié par un organisme d'accréditation
claim_scope: INTERNAL_AUDIT_ONLY
```

---

## Hiérarchie des boundaries

```
CRITIQUE (blocage immédiat) :
  B-EDU-01 KX108_ONLY
  B-EDU-02 NO_ACT_FROM_PERIPHERY
  B-EDU-03 READONLY_CONTEXT_ONLY
  B-EDU-07 FAIL_CLOSED_PRIORITY
  B-EDU-08 RGPD_SCOPE_GUARD
  B-EDU-09 NO_DIAGNOSIS
  B-EDU-10 NO_GRADING_AUTHORITY
  B-EDU-12 NO_STUDENT_DATA
  B-EDU-13 NO_PERSONAL_DATA
  B-EDU-15 NON_SOVEREIGN_BENCHMARK

HAUTE (refus + log) :
  B-EDU-04 NPL_ADVISORY_ONLY
  B-EDU-05 COGNITIVE_ADVISORY_ONLY
  B-EDU-06 ATLAS_READONLY_ADVISORY
  B-EDU-11 CANDIDATE_ONLY
  B-EDU-14 BENCHMARK_SPEC_ONLY
```
