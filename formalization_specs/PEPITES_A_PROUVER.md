# PEPITES_A_PROUVER.md
## Cahier des charges formel — Pépites à prouver ou à axiomatiser
## Obsidia X-108 — Périphérie sandbox
## READONLY = True (ce fichier) | kernel_mutation = False
## Date : 2026-06-25

---

## Règles générales

1. Un item "À_PROUVER" dans ce registre ne peut être marqué "PROUVÉ" que si une preuve Lean 4 sans sorry/admit/axiome non marqué HYPOTHESE_TEMPORAIRE existe dans `proofs/lean/peripheral/`.
2. Un axiome HYPOTHESE_TEMPORAIRE n'est pas une preuve — il bloque l'item en PROVISIONAL.
3. BALMA et SYRIQ ne figurent pas dans les cibles formelles — leurs sources sont illisibles.

---

## P36 — Quintuplet d'état canonique

| Champ | Valeur |
|---|---|
| Identifiant | P36 |
| Formule | `(S, Φ, I, τ, L)` |
| Type cible | `structure DomainState` |
| Statut actuel | CANONICAL_CANDIDATE — À_PROUVER |
| Preuve requise | Montrer que la structure est bien fondée et cohérente |
| Dépendances | Définition de `Metrics` hors du kernel scellé |
| Fichier sandbox | `proofs/lean/peripheral/Obsidia_Peripheral_Axioms.lean` |
| Priorité | HAUTE — utilisée comme base de P100 et P107 |
| Condition de validation | Structure Lean sans axiome, compilant en core Lean 4 |
| Interdit | Modifier Basic.lean ou importer depuis Basic.lean |

---

## P42 — Seuil d'admissibilité G1

| Champ | Valeur |
|---|---|
| Identifiant | P42 |
| Formule | `θ ≤ m.S → ACT` |
| Type cible | `def admissible + theorem admissible_self` |
| Statut actuel | CANONICAL_CANDIDATE — version formelle dans kernel scellé |
| Preuve requise | Version périphérique Float : triviale (déjà faite dans sandbox) |
| Dépendances | Aucune pour la version périphérique |
| Fichier sandbox | `proofs/lean/peripheral/Obsidia_Peripheral_Axioms.lean` |
| Priorité | MOYENNE (preuve kernel existe) |
| Condition de validation | `admissible_self` compile sans sorry |
| Interdit | Reproduire la preuve G1 formelle hors de Basic.lean scellé |

---

## P88 — Non-contradiction

| Champ | Valeur |
|---|---|
| Identifiant | P88 |
| Formule | `¬(A ∧ ¬A)` |
| Type cible | `theorem non_contradiction (A : Prop) : ¬(A ∧ ¬A)` |
| Statut actuel | CANONICAL_CANDIDATE — PROUVABLE MAINTENANT |
| Preuve requise | `fun ⟨ha, hna⟩ => hna ha` — Lean 4 pur |
| Dépendances | Aucune |
| Fichier sandbox | `proofs/lean/peripheral/Obsidia_Peripheral_Axioms.lean` |
| Priorité | BASSE (trivial) |
| Condition de validation | Compile sans imports externes |
| Interdit | Utiliser sorry |

---

## P100 — Stabilité de Lyapunov (décroissance)

| Champ | Valeur |
|---|---|
| Identifiant | P100 |
| Formule | `L(Φ(s)) ≤ L(s)` |
| Type cible | Theorem `lyapunov_non_growth` (actuellement axiome HYPOTHESE_TEMPORAIRE) |
| Statut actuel | CANONICAL_CANDIDATE — axiome temporaire dans sandbox |
| Preuve requise | Définir `level` et `step` concrets, puis prouver la décroissance |
| Dépendances | `level : Nat → Float` concret ; `step : Nat → Nat` concret |
| Fichier sandbox | `proofs/lean/peripheral/Obsidia_Peripheral_Axioms.lean` |
| Priorité | HAUTE |
| Condition de validation | `lyapunov_non_growth` prouvé sans axiome, avec level et step définis |
| Interdit | Laisser l'axiome sans marquage HYPOTHESE_TEMPORAIRE |

---

## P107 — Stabilité Lyapunov δ-ε

| Champ | Valeur |
|---|---|
| Identifiant | P107 |
| Formule | `∀ε>0, ∃δ>0: ‖x₀‖ < δ → ∀t, ‖x(t)‖ < ε` |
| Type cible | Theorem (axiome scaffold pour l'instant) |
| Statut actuel | PROVISIONAL — scaffold axiomatique HYPOTHESE_TEMPORAIRE |
| Preuve requise | Définir norm, iterate, puis prouver la stabilité δ-ε depuis P100 |
| Dépendances | `norm_state : DomainState → Float` ; `iterate_step : DomainState → Nat → Nat` ; propriétés de norme ; lien quantitatif L ↔ norm |
| Fichier sandbox | `proofs/lean/peripheral/P107_Lyapunov_delta_epsilon_scaffold.lean` |
| Priorité | HAUTE (À_PROUVER dans le registre) |
| Condition de validation | Theorem prouvé sans axiome ; norm et iterate définis avec leurs propriétés |
| Interdit | Présenter le scaffold axiomatique comme une preuve |

---

## P161 — Calibration énergétique temporelle

| Champ | Valeur |
|---|---|
| Identifiant | P161 |
| Formule | `Coût(A,t) = f(M(t), Rc(t), dM/dt, contexte_humain(t))` |
| Type cible | Structure `CanonicalState` + fonction `cost` |
| Statut actuel | PROVISIONAL — structure esquissée, types manquants |
| Preuve requise | Définir Time, Memory, Rc ; formaliser la fonction de coût |
| Dépendances | `Time`, `Memory`, `Rc : Time → Float`, `dM/dt` (dérivée discrète ou continue) |
| Fichier sandbox | À créer dans `proofs/lean/peripheral/` |
| Priorité | MOYENNE |
| Condition de validation | Signature de `cost` typée ; les types dépendants sont définis |
| Interdit | Utiliser des types implicitement continus sans les définir |

---

## Balance_math — Opérateur de balance

| Champ | Valeur |
|---|---|
| Identifiant | Balance_math |
| Formule | `B_Etienne(n) = équilibre(grandeur(n), écart(n), ratio(n), structure(n))` |
| Type cible | `def B_Etienne : Nat → Float` |
| Statut actuel | PROVISIONAL |
| Preuve requise | Définir les 4 composantes ; montrer que le résultat est dans [0,1] (si applicable) |
| Dépendances | `grandeur`, `écart`, `ratio`, `structure` — non définis |
| Domaine | RECHERCHE MATH uniquement — PAS dans le décisionnel X-108 |
| Priorité | BASSE (hors kernel) |
| Condition de validation | Définitions des 4 composantes fournies |
| Interdit | Intégrer au décisionnel X-108 |

---

## PrimePartitionLab — Partitions entières

| Champ | Valeur |
|---|---|
| Identifiant | PrimePartitionLab |
| Formule | `Part(n) = {partitions de n}`, `p(n) = \|Part(n)\|` |
| Type cible | `def Part : Nat → List (List Nat)` + `def p : Nat → Nat` |
| Statut actuel | PROVISIONAL |
| Preuve requise | Algorithme de partition récursif ; preuve de terminaison ; `p(n) = (Part n).length` |
| Dépendances | Algorithme de génération des partitions |
| Domaine | RECHERCHE MATH — lab nombres premiers |
| Priorité | BASSE (hors kernel) |
| Condition de validation | `Part n` génère toutes les partitions de n ; terminaison prouvée |
| Interdit | Utiliser `sorry` |

---

## BALMA

| Champ | Valeur |
|---|---|
| Identifiant | BALMA |
| Statut | MISSING_CONTEXT |
| Source | Fichiers .docx illisibles |
| Formalisation possible ? | NON — pas de source lisible |
| Action requise | Étienne exporte la source en .md/.txt |
| Interdit | Inventer BALMA |

---

## SYRIQ

| Champ | Valeur |
|---|---|
| Identifiant | SYRIQ |
| Statut | MISSING_CONTEXT |
| Source | Fichiers .docx illisibles |
| Formalisation possible ? | NON — pas de source lisible |
| Action requise | Étienne exporte la source en .md/.txt |
| Interdit | Inventer SYRIQ |
