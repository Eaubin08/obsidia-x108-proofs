# P86 — Consensus supermajorité 3/4

**Statut source :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés | Opératoire : Oui (Code actif)
**Statut normalisé :** STATUT_SOURCE
**Bloc principal :** Bloc 01 — Noyau Mathématique et Déterministe

## Formule / contenu mathématique
$$
\text{Consensus}(d_1, \ldots, d_4) : \text{Supermajorité} \geq 3/4
$$

## Code source extrait
```text
theorem aggregate4_act
  (d1 d2 d3 d4 : Decision3)
  (h : 3 <= countDec Decision3.ACT [d1, d2, d3, d4]) :
  aggregate4 d1 d2 d3 d4 = Decision3.ACT := by
  unfold aggregate4
  have htrue : decide (3 <= countDec Decision3.ACT [d1, d2, d3, d4]) = true := decide_eq_true h
  rw [htrue]; rfl
```

## Contrat V4
- Définition mathématique lisible.
- Statut cohérent dans le registre.
- Preuve ou test selon niveau exigé.
- Aucun passage en DONE sans évidence attachée.

## Contenu source complet extrait
**Statut :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés | **Opératoire :** Oui (Code actif)

**Formule mathématique :**

$$
\text{Consensus}(d_1, \ldots, d_4) : \text{Supermajorité} \geq 3/4
$$

**Code Lean 4 actif** (`Consensus.lean`) :

```lean
theorem aggregate4_act
  (d1 d2 d3 d4 : Decision3)
  (h : 3 <= countDec Decision3.ACT [d1, d2, d3, d4]) :
  aggregate4 d1 d2 d3 d4 = Decision3.ACT := by
  unfold aggregate4
  have htrue : decide (3 <= countDec Decision3.ACT [d1, d2, d3, d4]) = true := decide_eq_true h
  rw [htrue]; rfl
```

**Garantie formelle :** Supermajorité de 3/4 pour ACT → décision ACT certifiée.

---
