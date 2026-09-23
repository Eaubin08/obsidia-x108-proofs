# FAILURE_MODES_SPEC
# runtime_contracts/education_benchmark_dry_run/failure_modes/
# Plan 3 P7 — Modes d'échec — FAIL_CLOSED par défaut
# Date: 2026-06-02
# Status: SPEC_ONLY

---

## Règle globale

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f ↛ allow_by_default
```

Tout échec non catégorisé → FAIL_CLOSED automatique.

---

## FM-01 — ContextPacket absent ou invalide

```yaml
failure_id: FM-01
trigger: "ContextPacket manquant ou invalide"
consequence_candidate: "Enrichissement contextuel impossible"
response: FAIL_CLOSED
action_taken: NONE
fallback: "Retourner CONTEXT_UNAVAILABLE"
x108_notify: false  # pas d'action critique
allow_partial_run: false
note: "Ne PAS tenter de raisonner sans contexte valide"
```

---

## FM-02 — IntentEnvelope absente sur action critique

```yaml
failure_id: FM-02
trigger: "Action critique détectée sans IntentEnvelope"
consequence_candidate: "Bypass potentiel de X108"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner INTENT_ENVELOPE_REQUIRED"
x108_notify: true
anti_bypass: true
boundary_enforced: KX108_ONLY
note: "CRITIQUE — toute adaptation curriculaire irréversible requiert IntentEnvelope"
```

---

## FM-03 — Claim scope insuffisant

```yaml
failure_id: FM-03
trigger: "Action demandée dépasse le claim scope autorisé (ex: GRADE_STUDENT_OFFICIALLY)"
consequence_candidate: "Autorité non détenue par le benchmark"
response: REFUSED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner CLAIM_SCOPE_INSUFFICIENT"
x108_notify: false
note: "P7 ne possède aucune autorité de notation, diagnostic, ou décision scolaire réelle"
```

---

## FM-04 — Données personnelles détectées dans l'input

```yaml
failure_id: FM-04
trigger: "Données personnelles ou données étudiant réelles détectées dans l'input"
consequence_candidate: "Violation RGPD potentielle"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner PERSONAL_DATA_DETECTED — requiert revue F03+F10"
x108_notify: true
rgpd_critical: true
note: "P7 ne traite JAMAIS de données personnelles réelles"
```

---

## FM-05 — X108 gateway timeout ou refus

```yaml
failure_id: FM-05
trigger: "X108 ne répond pas ou retourne refus sur adaptation critique"
consequence_candidate: "Adaptation ne peut pas être autorisée"
response: FAIL_CLOSED
action_taken: NONE
fallback: "Retourner X108_REFUSED_OR_TIMEOUT — adaptation bloquée"
x108_notify: false  # X108 lui-même a répondu
note: "Timeout X108 ≠ autorisation implicite — toujours fail_closed"
```

---

## FM-06 — Tentative d'écriture mémoire depuis benchmark

```yaml
failure_id: FM-06
trigger: "Benchmark tente d'écrire en mémoire (Graphiti/Brody/NPL)"
consequence_candidate: "Violation boundary NO_WOR"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner MEMORY_WRITE_BLOCKED"
boundary_enforced: NO_WOR
note: "Les wrappers P6 sont READONLY — toute écriture est interdite"
```

---

## FM-07 — Tentative d'exécution de benchmark réel

```yaml
failure_id: FM-07
trigger: "Appel vers benchmark exécutable en P7"
consequence_candidate: "Violation de scope P7"
response: BLOCKED + FAIL_CLOSED
action_taken: NONE
fallback: "Retourner BENCHMARK_NOT_EXECUTABLE_IN_P7"
note: "P7 = SPEC_ONLY — aucun benchmark exécuté"
```

---

## FM-08 — OS3EvidenceTicket invalide ou hash mismatch

```yaml
failure_id: FM-08
trigger: "OS3EvidenceTicket théorique mal formé ou hash placeholder invalide"
consequence_candidate: "Trace d'audit incomplète"
response: FAIL_CLOSED (on evidence)
action_taken: NONE
fallback: "Retourner OS3_EVIDENCE_INCOMPLETE — log théorique"
note: "P7: tickets OS3 sont THEORETICAL_ONLY — erreur = log, pas blocage d'action"
```

---

## FM-09 — Score candidat hors plage

```yaml
failure_id: FM-09
trigger: "Métrique candidate hors plage 0.0-1.0"
consequence_candidate: "Métrique invalide"
response: REJECT_METRIC
action_taken: NONE — métrique ignorée
fallback: "Retourner METRIC_OUT_OF_RANGE"
note: "Ne PAS utiliser une métrique invalide comme score réel"
```

---

## FM-10 — Anti-bypass éducatif non respecté

```yaml
failure_id: FM-10
trigger: "Flux éducatif contourne la boundary KX108_ONLY"
consequence_candidate: "Bypass de gouvernance"
response: BLOCKED + FAIL_CLOSED + BYPASS_DETECTED
action_taken: NONE
boundary_enforced: KX108_ONLY
x108_notify: true
anti_bypass: true
note: "CRITIQUE — voir SCE-06 pour le scénario complet"
```

---

## Résumé des failure modes

| ID | Trigger | Réponse | Anti-bypass | RGPD | Critique |
|----|---------|---------|-------------|------|---------|
| FM-01 | ContextPacket absent | FAIL_CLOSED | Non | Non | Non |
| FM-02 | IntentEnvelope absente | BLOCKED + FAIL_CLOSED | Oui | Non | Oui |
| FM-03 | Claim scope insuffisant | REFUSED + FAIL_CLOSED | Non | Non | Non |
| FM-04 | Données personnelles détectées | BLOCKED + FAIL_CLOSED | Non | Oui | Oui |
| FM-05 | X108 timeout/refus | FAIL_CLOSED | Non | Non | Oui |
| FM-06 | Écriture mémoire tentée | BLOCKED + FAIL_CLOSED | Oui | Non | Oui |
| FM-07 | Benchmark exécutable appelé | BLOCKED + FAIL_CLOSED | Non | Non | Non |
| FM-08 | OS3Evidence invalide | FAIL_CLOSED (evidence) | Non | Non | Non |
| FM-09 | Métrique hors plage | REJECT_METRIC | Non | Non | Non |
| FM-10 | Anti-bypass non respecté | BLOCKED + BYPASS_DETECTED | Oui | Non | Oui |

**Total : 10 failure modes — règle globale : FAIL_CLOSED — 0 allow_by_default**
