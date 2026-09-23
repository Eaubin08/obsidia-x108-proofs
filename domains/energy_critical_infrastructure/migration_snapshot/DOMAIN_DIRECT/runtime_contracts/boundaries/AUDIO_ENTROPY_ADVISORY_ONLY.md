# AUDIO_ENTROPY_ADVISORY_ONLY
# runtime_contracts/boundaries/AUDIO_ENTROPY_ADVISORY_ONLY.md
# Status: CONTRACT_SKELETON_ONLY
# Source: specs/03_ENTROPY_DISCIPLINE/AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md

---

## 1. Boundary Statement

```
Audio/Entropy = SOURCE_PARTIAL / MÉTAPHORE ARCHITECTURALE / CANDIDAT MÉTRIQUE
Thermodynamique cognitive ↛ loi physique prouvée
Thermodynamique cognitive ↛ preuve formelle
Audio/Entropy ↛ runtime authority
Audio/Entropy ↛ psychological diagnosis
Audio/Entropy ↛ decision authority
Audio/Entropy ↛ ACT / ALLOW / HOLD / BLOCK source directe
```

---

## 2. Applies To

- Fichier audio transcrit : "Obsidia et la discipline de l'entropie" (AUDIO_AUDIT_PARTIAL)
- Concepts : Discipline de l'entropie, BUV, thermodynamique cognitive, chaleur sémantique
- Signaux Python : thermo_debt, delta_E, delta_C (couverts également par P161)

---

## 3. Statut des concepts clés

| Concept | Statut réel | Usage Plan 3 |
|---------|-------------|-------------|
| Discipline de l'entropie | MOTEUR (méthodologie) | Contrainte architecturale — pas signal runtime |
| BUV (Balance Universelle des Vérités) | Prototype Python sandbox | Score advisory [0,1] uniquement |
| Thermodynamique cognitive | THÉORIE — aucun runtime | Candidat métrique future |
| Chaleur sémantique | SPEC_TARGET_NOT_CREATED | Futur signal advisory |
| thermo_debt | PYTHON_SPEC_NOT_LEAN_PROVEN | Signal advisory P161 |
| Gencoin / utilité thermodynamique | Sandbox — smart contracts absents | Plan 4 séparé |

---

## 4. Allowed

- "Discipline de l'entropie" comme principe architectural d'isolation workspace/runtime
- thermo_debt et delta_E comme signaux advisory PYTHON_SPEC_NOT_LEAN_PROVEN
- Référencer la source audio comme contrainte documentaire dans AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md
- "Thermodynamique cognitive = métaphore architecturale en cours de formalisation"
- entropy_metric_candidate dans ContextPacket avec label `ENTROPY_ADVISORY_NOT_RUNTIME_AUTHORITY`

---

## 5. Forbidden

```
❌ "Thermodynamique cognitive est une loi prouvée"
❌ "Chaleur sémantique est mesurée activement" — aucun monitoring
❌ "Entropy → HOLD directement" — seul X108 décide
❌ "BUV est opérationnel" — sandbox uniquement
❌ "86 specs frozen" — Plan 2 en cours, pas terminé
❌ "Gencoin prêt marché" — smart contracts absents
❌ Psychological diagnosis via thermodynamique cognitive
❌ Energy law proven claim — entropie cognitive ≠ thermodynamique physique
❌ Hidden manipulation via scoring entropique
```

---

## 6. Claim-scope corrections obligatoires (issues de la source audio)

| Affirmation audio | Correction stricte |
|------------------|--------------------|
| "agi_subordination_spec.md localisé dans GitHub" | ABSENT_UNDER_THIS_NAME — spec créée en Plan 2 |
| "buv_master_spec.md localisé" | ABSENT_UNDER_THIS_NAME (pack NPL zip seulement) |
| "86 specs frozen" | Plan 2 en cours — NON terminé |
| "BUV = opérateur actif" | Prototype sandbox uniquement |

---

## 7. Required Future Tests

- `test_semantic_heat_metric_not_active` — aucun monitoring de chaleur sémantique
- `test_entropy_not_hold_without_x108` — entropie seule ne peut pas déclencher HOLD

---

## 8. Proof Expectation

- Aucune preuve formelle pour thermodynamique cognitive — THEORY_ONLY
- Plan 4+ : formalisation Lean éventuelle (SEMANTIC_HEAT_MONITORING_SPEC.md)

---

## 9. Claim-Scope

**Autorisé :** "Audio/Entropy = source de contraintes architecturales — signaux advisory candidates"
**Interdit :** Tout claim de loi physique, preuve formelle, ou autorité décisionnelle

---

## 10. Example Violation

```python
# VIOLATION
if entropy_cognitive > 0.9:
    return "HOLD"  # ← thermodynamique cognitive ne peut pas émettre HOLD
```

---

## 11. Correct Handling

```python
# CORRECT
signal = PeripheralSignalPacket(
    signal_type="ENTROPY_METRIC",
    metric_name="semantic_heat_estimate",
    metric_value=0.61,
    label="ENTROPY_ADVISORY_NOT_RUNTIME_AUTHORITY",
    emits_act=False, emits_allow_hold_block=False
)
# → X108 reçoit comme contexte et décide
```
