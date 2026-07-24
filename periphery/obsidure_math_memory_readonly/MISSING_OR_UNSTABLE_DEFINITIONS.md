# MISSING_OR_UNSTABLE_DEFINITIONS.md
## Obsidia X-108 — Définitions manquantes ou instables
## READONLY = True | kernel_mutation = False
## Date : 2026-06-25

Ce fichier recense toutes les définitions qui bloquent une preuve ou une axiomatisation.
Il est la référence pour comprendre pourquoi un item est PROVISIONAL ou MISSING_CONTEXT.

---

## 1. BALMA

**Origine déclarée :** v1cano.docx, formalisermath.docx (dans `C:\Users\User\Desktop\Obsidia Master\obsidia\`)
**Statut :** MISSING_CONTEXT
**Raison :** Ces fichiers sont au format .docx binaire. La machine ne peut pas en lire le contenu.
**Condition de levée :** Étienne exporte le fichier en .md ou .txt et le dépose dans `periphery/source_exports/`.
**Interdiction absolue :** Ne JAMAIS inventer BALMA. Toute définition de BALMA sans source lisible est une hallucination non autorisée.

---

## 2. SYRIQ

**Origine déclarée :** Même sources que BALMA (fichiers .docx illisibles)
**Statut :** MISSING_CONTEXT
**Raison :** Idem BALMA — source binaire non lisible.
**Condition de levée :** Export .docx → .md par Étienne.
**Interdiction absolue :** Ne JAMAIS inventer SYRIQ.

---

## 3. `norm` pour P107

**Contexte :** P107 formule `∀ε>0, ∃δ>0: ‖x₀‖ < δ → ‖x(t)‖ < ε`
**Définition requise :** `norm : DomainState → Float` — une norme sur l'espace d'état
**Statut dans les sources lisibles :** ABSENT — aucune source lisible ne définit comment mesurer la distance entre états
**Impacte :** Sans `norm`, la quantité `‖x₀‖` n'est pas calculable. La preuve δ-ε est impossible à formaliser.
**Condition de levée :** Définir explicitement `norm_state : DomainState → Float` avec les propriétés de norme (positivité, triangulaire, homogénéité) et les prouver dans la sandbox.

---

## 4. `iterate` pour P107

**Contexte :** P107 parle de `x(t)` = état après t itérations de Φ
**Définition requise :** `iterate : (Nat → Nat) → Nat → Nat → Nat` — application répétée de la transition
**Statut dans les sources lisibles :** ABSENT — la fonction de composition répétée n'est pas définie
**Impacte :** Sans `iterate`, `‖x(t)‖` pour t > 1 n'est pas exprimable. La quantification ∀t est bloquée.
**Condition de levée :** Définir `iterate f 0 s = s` et `iterate f (n+1) s = f (iterate f n s)` et prouver la terminaison.

---

## 5. `Time` type pour P161

**Contexte :** P161 : `Coût(A,t) = f(M(t), Rc(t), dM/dt, contexte_humain(t))` — t est un paramètre temporel
**Définition requise :** Un type `Time` — entier, réel, ou flot continu ?
**Statut dans les sources lisibles :** ABSENT — aucune précision sur le domaine de t
**Impacte :** Sans savoir si t : Nat, Float, ou un type continu, la signature de Coût est ambiguë.
**Condition de levée :** Choisir et documenter `Time := Nat` (temps discret) ou `Time := Float` (continu) selon le contexte de P161.

---

## 6. `Memory` type pour P161

**Contexte :** P161 : `M(t)` = mémoire au temps t
**Définition requise :** Type `Memory` et sa dépendance à t
**Statut dans les sources lisibles :** ABSENT — `M(t)` est cité sans définition de la structure de mémoire
**Impacte :** Sans Memory défini, `M(t)` est une variable libre. La loi P161 n'est pas formalisable.
**Condition de levée :** Définir Memory comme un enregistrement (ressource cognitive ? état interne ?) dans la sandbox.

---

## 7. `Rc(t)` pour P161

**Contexte :** P161 : `Rc(t)` = ressource cognitive au temps t
**Définition requise :** Type et sémantique de Rc — charge cognitive ? budget d'attention ?
**Statut dans les sources lisibles :** ABSENT
**Impacte :** Sans Rc, la contribution cognitive au coût n'est pas quantifiable.
**Condition de levée :** Définir `Rc : Time → Float` et sa relation avec M(t).

---

## 8. `Metrics` dans la sandbox périphérique

**Contexte :** La structure P36 `(S, Φ, I, τ, L)` utilise le type `Metrics` pour S dans l'esquisse de P161
**Problème :** `Basic.lean` (scellé, DO_NOT_TOUCH) contient la définition canonique de Metrics dans le kernel
**Statut :** BLOQUÉ — ne pas lire ni copier depuis Basic.lean
**Solution dans la sandbox :** La sandbox périphérique utilise `Float` pour S directement dans `DomainState`, sans référencer Metrics. C'est une approximation périphérique, pas une preuve kernel.
**Condition de levée :** Si une définition de Metrics est nécessaire hors du kernel, la redéfinir de façon indépendante dans `peripheral/` sans importer Basic.lean.

---

## 9. ADeLe — 18 axes de calibration

**Origine :** `extracted_text_all.md` mentionne ADeLe avec "18 axes de calibration"
**Statut :** AMBIGUOUS (mentionné sans détail)
**Raison :** Les 18 axes ne sont pas listés dans les sources lisibles. Le terme est présent mais non développé.
**Impacte :** ADeLe ne peut pas être axiomatisé ou utilisé sans la liste des 18 axes.
**Condition de levée :** Obtenir la liste des 18 axes dans une source lisible.

---

## 10. Pourquoi P107 ne peut pas être prouvé pleinement maintenant

P107 énonce : `∀ε>0, ∃δ>0: ‖x₀‖ < δ → ∀t, ‖x(t)‖ < ε`

Pour prouver ce théorème en Lean 4, il faut :

1. **Un type d'espace d'état muni d'une norme** : `DomainState` n'a pas de norme définie. Sans `norm_state : DomainState → Float` prouvée être une vraie norme (positivité, triangulaire), l'expression `‖x₀‖` n'existe pas.

2. **La fonction `iterate`** : `x(t)` = `(iterate ds.step t s₀)` requiert une définition récursive de l'itération de `ds.step`. Sans elle, `x(t)` pour t arbitraire n'est pas exprimable.

3. **Un lien entre la décroissance de L et la norme** : La propriété `L(Φ(s)) ≤ L(s)` (P100) ne suffit pas seule à conclure la stabilité δ-ε. Il faut en plus une hypothèse de type "L(s) ≥ c · norm(s)" pour extraire le contrôle de la norme depuis L. Cette hypothèse n'est pas dans les sources.

4. **La preuve est existentielle** : `∃δ>0` — trouver δ explicitement en fonction de ε requiert une construction quantitative qui dépend de la structure concrète de L et Φ.

**Conclusion :** P107 reste PROVISIONAL. Le scaffold axiomatique dans `P107_Lyapunov_delta_epsilon_scaffold.lean` est honnête : il pose le statement comme axiome HYPOTHESE_TEMPORAIRE en attendant que les 4 conditions ci-dessus soient satisfaites.
