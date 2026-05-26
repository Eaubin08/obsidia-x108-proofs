# P42 — Seuil G1 : ACT si θ ≤ S

**Statut source :** 🟦 FORMALISÉ — Objet mathématique défini dans v1cano.docx / formalisermath.docx
**Statut normalisé :** FORMALISÉ
**Bloc principal :** Bloc 01 — Noyau Mathématique et Déterministe

## Formule / contenu mathématique
$$
G_1 : \theta \leq m.S \Rightarrow \text{decision}(m, \theta) = \text{ACT}
$$

## Code source extrait
```text
theorem G1_act_above_threshold (m : Metrics) (theta : Rat)
    (h : theta <= m.S) :
    decision m theta = Decision.ACT := by
  unfold decision
  have htrue : decide (theta <= m.S) = true := decide_eq_true h
  rw [htrue]
```

## Contrat V4
- Définition mathématique lisible.
- Statut cohérent dans le registre.
- Preuve ou test selon niveau exigé.
- Aucun passage en DONE sans évidence attachée.

## Contenu source complet extrait
**Statut :** 🟦 FORMALISÉ — Objet mathématique défini dans `v1cano.docx` / `formalisermath.docx`

**Formule mathématique :**

$$
G_1 : \theta \leq m.S \Rightarrow \text{decision}(m, \theta) = \text{ACT}
$$

**Code Lean 4 actif** (`Basic.lean`) :

```lean
theorem G1_act_above_threshold (m : Metrics) (theta : Rat)
    (h : theta <= m.S) :
    decision m theta = Decision.ACT := by
  unfold decision
  have htrue : decide (theta <= m.S) = true := decide_eq_true h
  rw [htrue]
```

**Garantie formelle :** Si le score S dépasse le seuil θ, la décision est ACT — sans exception.

---
