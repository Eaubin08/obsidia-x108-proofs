# P17 — Croissance du log d'audit

**Statut source :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés | Opératoire : Oui (Code actif)
**Statut normalisé :** STATUT_SOURCE
**Bloc principal :** Bloc 11 — Trace et Immuabilité (C10)

## Formule / contenu mathématique
$$
\text{AuditLog}(t+1) = \text{AuditLog}(t) \cup \{(i_t, d_t)\}
$$

## Code source extrait
```text
theorem P17_AuditGrowth (s : State) (i : Input) :
    (transition s i).2.auditLog.length = s.auditLog.length + 1 := by
  unfold transition
  simp [List.length_append]
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
\text{AuditLog}(t+1) = \text{AuditLog}(t) \cup \{(i_t, d_t)\}
$$

**Code Lean 4 actif** (`SystemModel.lean`) :

```lean
theorem P17_AuditGrowth (s : State) (i : Input) :
    (transition s i).2.auditLog.length = s.auditLog.length + 1 := by
  unfold transition
  simp [List.length_append]
```

**Garantie formelle :** Chaque transition ajoute exactement 1 entrée au log. Pas d'effacement possible.

---
