# METRICS_CANDIDATES.md
## Obsidia X-108 — Candidats métriques de la mémoire mathématique
## READONLY = True | kernel_mutation = False
## Date : 2026-06-25

---

## Règle de lecture

- **Type Lean** = type proposé pour la sandbox périphérique (pas le kernel)
- **Usage** = où cette métrique peut être utilisée sans risque
- **Statut** = hérité de l'item source dans MATH_MEMORY_INDEX.json

---

## S — Score d'admissibilité

| Champ | Valeur |
|---|---|
| Symbole | S |
| Type Lean (sandbox) | `Float` |
| Sources | P36, P42 |
| Définition humaine | Score courant d'admissibilité d'un état ou d'une action |
| Usage Obsidure | OUI — lecture et comparaison |
| Usage Guard | OUI — seuil G1 (`θ ≤ S → ACT`) |
| Usage Kernel | Via `Basic.lean` scellé uniquement |
| Statut | CANONICAL_CANDIDATE |
| Notes | Dans `DomainState.score : Float`. Le type kernel (`Metrics`) est dans Basic.lean scellé. |

---

## L — Fonction d'énergie / Lyapunov

| Champ | Valeur |
|---|---|
| Symbole | L |
| Type Lean (sandbox) | `Nat → Float` |
| Sources | P100, P107, P36 |
| Définition humaine | Fonction mesurant l'énergie ou le risque d'un état — doit être décroissante |
| Usage Obsidure | OUI — vérification de stabilité |
| Usage Lean | OUI — axiome `lyapunov_non_growth` dans `Obsidia_Peripheral_Axioms.lean` |
| Usage Kernel | Propriété scellée dans le kernel |
| Statut | CANONICAL_CANDIDATE (définition) / PROVISIONAL (preuve concrète) |
| Notes | `DomainState.level : Nat → Float`. La preuve de décroissance réelle est bloquée par l'absence de L et Phi concrets. |

---

## τ — Seuil temporel

| Champ | Valeur |
|---|---|
| Symbole | τ (tau) |
| Type Lean (sandbox) | `Nat` |
| Sources | P36, `proofs/lean/Obsidia/TemporalKernel.lean` (scellé) |
| Définition humaine | Seuil temporel — délai maximal pour une décision ou une transition |
| Usage Obsidure | OUI — condition temporelle |
| Usage Kernel | Via TemporalKernel.lean scellé uniquement |
| Statut | CANONICAL_CANDIDATE |
| Notes | `DomainState.tau : Nat`. Ne pas modifier TemporalKernel.lean. |

---

## θ — Seuil de décision

| Champ | Valeur |
|---|---|
| Symbole | θ (theta) |
| Type Lean (sandbox) | `Float` (approximation périphérique) |
| Sources | P42 |
| Définition humaine | Seuil de déclenchement de l'action : si S ≤ θ alors ACT |
| Usage Obsidure | OUI — condition de déclenchement |
| Usage Guard | OUI — logique de seuil |
| Usage Kernel | Via Basic.lean scellé |
| Statut | CANONICAL_CANDIDATE |
| Notes | Type `Rat` ou `Float` selon le niveau de précision requis. La sandbox utilise Float. |

---

## Part(n) — Partitions entières

| Champ | Valeur |
|---|---|
| Symbole | Part(n), p(n) |
| Type Lean (sandbox) | `Nat → List (List Nat)` et `Nat → Nat` |
| Sources | PrimePartitionLab (extracted_text_all.md) |
| Définition humaine | `Part(n)` = ensemble des partitions entières de n ; `p(n) = \|Part(n)\|` |
| Usage Obsidure | OUI — domaine recherche math |
| Usage Kernel | NON |
| Statut | PROVISIONAL |
| Notes | Algorithme de génération des partitions non fourni dans les sources. Preuve de terminaison requise. |

---

## B_Etienne(n) — Opérateur de balance

| Champ | Valeur |
|---|---|
| Symbole | B_Etienne(n) |
| Type Lean (sandbox) | `Nat → Float` |
| Sources | Balance_math (extracted_text_all.md) |
| Définition humaine | `B_Etienne(n) = équilibre(grandeur(n), écart(n), ratio(n), structure(n))` |
| Usage Obsidure | OUI — domaine recherche / moteur exploratoire UNIQUEMENT |
| Usage Kernel | NON — hors décisionnel X-108 |
| Statut | PROVISIONAL |
| Notes | Les 4 composantes ne sont pas définies dans les sources. Ne pas intégrer au décisionnel. |

---

## Coût(A,t) — Coût énergétique d'une action

| Champ | Valeur |
|---|---|
| Symbole | Coût, Cout |
| Type Lean (sandbox) | `Action → Time → Float` (approximation) |
| Sources | P161 |
| Définition humaine | `Coût(A,t) = f(M(t), Rc(t), dM/dt, contexte_humain(t))` |
| Usage Obsidure | OUI — évaluation d'action |
| Usage Kernel | NON (types Time, Memory, Rc non définis) |
| Statut | PROVISIONAL |
| Notes | Les types Time, Memory, Rc(t) sont manquants. La signature complète ne peut pas être formalisée. Voir MISSING_OR_UNSTABLE_DEFINITIONS.md §5,6,7. |

---

## λ(t) — Calibrateur temporel

| Champ | Valeur |
|---|---|
| Symbole | lambda_t |
| Type Lean (sandbox) | inconnu |
| Sources | extracted_text_all.md (mention sans formule) |
| Définition humaine | Calibrateur temporel — rôle non précisé |
| Usage Obsidure | NON |
| Usage Kernel | NON |
| Statut | DO_NOT_USE_YET |
| Notes | Formule absente des sources lisibles. Relation avec τ non établie. Ne pas utiliser tant que la formule n'est pas documentée. |
