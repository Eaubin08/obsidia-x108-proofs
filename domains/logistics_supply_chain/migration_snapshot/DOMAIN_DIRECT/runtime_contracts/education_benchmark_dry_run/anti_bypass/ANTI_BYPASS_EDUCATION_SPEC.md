# ANTI_BYPASS_EDUCATION_SPEC
# runtime_contracts/education_benchmark_dry_run/anti_bypass/
# Plan 3 P7 — Anti-bypass éducatif — SPEC_ONLY
# Date: 2026-06-02
# Status: ANTI_BYPASS_SPEC_ONLY

---

## Contexte

Le benchmark éducatif présente des vecteurs de bypass spécifiques car :
1. Les flux éducatifs semblent "doux" (explication, advisory) → risque de contournement X108
2. La notation / diagnostic peuvent être glissés dans un flux advisory
3. Les données étudiants peuvent être incluses dans un ContextPacket sans détection

Ce document spécifie les barrières anti-bypass pour le futur benchmark éducatif.

---

## ABP-01 — Bypass via advisory qui décide

```yaml
bypass_id: ABP-01
name: "Advisory qui prend une décision réelle"
vector: "Un flux advisory retourne implicitement une décision curriculaire"
detection_candidate:
  - advisory.is_real_decision == true → BLOCKED
  - advisory.action_type includes IRREVERSIBLE → IntentEnvelope required
boundary: "NO_ACT_FROM_PERIPHERY"
response: FAIL_CLOSED
failure_mode: FM-02
```

---

## ABP-02 — Bypass via ContextPacket contenant données personnelles

```yaml
bypass_id: ABP-02
name: "Données personnelles encodées dans ContextPacket"
vector: "Données étudiant réelles passées dans ContextPacket sous un label neutre"
detection_candidate:
  - context_packet.contains_personal_data == true → BLOCKED
  - context_packet.student_id != null → BLOCKED
boundary: "NO_STUDENT_DATA / NO_PERSONAL_DATA"
response: BLOCKED + FAIL_CLOSED
failure_mode: FM-04
```

---

## ABP-03 — Bypass via score candidat présenté comme réel

```yaml
bypass_id: ABP-03
name: "Score candidat présenté comme score officiel"
vector: "Score hypothétique promu en note officielle sans gate humaine"
detection_candidate:
  - score.is_real == true AND P7_active → BLOCKED
  - score.claim_scope != CANDIDATE_ONLY → REJECTED
boundary: "CANDIDATE_ONLY"
response: REFUSED + FAIL_CLOSED
failure_mode: FM-03
```

---

## ABP-04 — Bypass via écriture mémoire depuis flux éducatif

```yaml
bypass_id: ABP-04
name: "Écriture mémoire depuis le benchmark"
vector: "Benchmark tente de stocker des résultats dans Graphiti/Brody/NPL"
detection_candidate:
  - memory_write_attempted == true → BLOCKED
  - graphiti_write_attempted == true → BLOCKED
boundary: "NO_WOR / READONLY_CONTEXT_ONLY"
response: BLOCKED + FAIL_CLOSED
failure_mode: FM-06
```

---

## ABP-05 — Bypass via adaptation directe sans IntentEnvelope

```yaml
bypass_id: ABP-05
name: "Adaptation curriculaire directe sans gate X108"
vector: "Action curriculaire irréversible déclenchée sans passer par IntentEnvelope + X108"
detection_candidate:
  - action.criticality == HIGH AND intent_envelope == null → BLOCKED
  - action.irreversibility != REVERSIBLE AND x108_consulted == false → BLOCKED
boundary: "KX108_ONLY"
response: BLOCKED + BYPASS_DETECTED + FAIL_CLOSED
failure_mode: FM-10
anti_bypass_critical: true
```

---

## ABP-06 — Bypass via benchmark exécutable en P7

```yaml
bypass_id: ABP-06
name: "Tentative d'exécuter le benchmark en mode P7"
vector: "Appel d'un benchmark exécutable alors que P7 = SPEC_ONLY"
detection_candidate:
  - benchmark.is_executable == true AND P7_mode == true → BLOCKED
boundary: "NO_RUNTIME_EXECUTION"
response: BLOCKED + FAIL_CLOSED
failure_mode: FM-07
```

---

## ABP-07 — Bypass via misconception→diagnostic non autorisé

```yaml
bypass_id: ABP-07
name: "Misconception signal promu en diagnostic éducatif réel"
vector: "Signal de misconception advisory converti en diagnostic officiel"
detection_candidate:
  - misconception_signal.diagnostic_authority != NONE → BLOCKED
  - misconception_signal.claim_scope != ADVISORY_ONLY → REFUSED
boundary: "NO_DIAGNOSIS"
response: REFUSED + FAIL_CLOSED
failure_mode: FM-03
```

---

## Résumé anti-bypass

| ID | Vecteur | Boundary | Critique |
|----|---------|---------|---------|
| ABP-01 | Advisory→décision réelle | NO_ACT_FROM_PERIPHERY | Oui |
| ABP-02 | Données perso dans ContextPacket | NO_STUDENT_DATA | Oui |
| ABP-03 | Score candidat→officiel | CANDIDATE_ONLY | Non |
| ABP-04 | Écriture mémoire | NO_WOR | Oui |
| ABP-05 | Adaptation directe sans X108 | KX108_ONLY | Oui |
| ABP-06 | Benchmark exécutable en P7 | NO_RUNTIME_EXECUTION | Non |
| ABP-07 | Misconception→diagnostic | NO_DIAGNOSIS | Non |

**Total : 7 vecteurs anti-bypass — 4 critiques — 0 allow_by_default**

---

## Lien avec P4

```
P4 (PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_READY) définit les tests anti-bypass globaux.
P7 ABP-01..07 spécifie les vecteurs SPÉCIFIQUES au contexte éducatif.
Les tests futurs pour le benchmark éducatif référenceront P4 + ce document.
```
