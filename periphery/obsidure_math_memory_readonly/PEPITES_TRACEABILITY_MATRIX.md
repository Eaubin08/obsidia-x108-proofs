# PEPITES_TRACEABILITY_MATRIX.md
## Obsidia X-108 — Matrice de traçabilité des pépites et lois
## READONLY = True | kernel_mutation = False | decision_authority = KX108_ONLY
## Date : 2026-06-25

---

| Pépite/Loi/Métrique | Source locale | Définition humaine | Usage Obsidure | Usage Kernel/Sigma/Guard | Signature Lean | Axiomatisable ? | Prouvable maintenant ? | Métrique ? | Dépendances manquantes | Statut | Condition de blocage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **P36** Quintuplet canonique | `periphery/pepites_search_algo/P36__Quintuplet_detat_canonique_S_I_L.md` | `(S, Φ, I, τ, L)` — état d'admissibilité | OUI — structure de base | NON (kernel scellé) | `structure DomainState where score step input tau level` | OUI (structure) | NON (À_PROUVER) | NON | `Metrics` dans sandbox ; `Basic.lean` scellé | CANONICAL_CANDIDATE | Définition formelle de Metrics en dehors du kernel |
| **P42** Seuil G1 | `periphery/pepites_search_algo/P42__Seuil_G1_ACT_si_S.md` | `θ ≤ m.S → ACT` | OUI (analogique) | OUI — preuve dans `Basic.lean` scellé | `def admissible (score theta : Float) : Bool` | OUI (def + théorème trivial) | OUI (version périphérique Float) | NON | Aucune pour la version périphérique | CANONICAL_CANDIDATE | Néant pour version analogique ; kernel scellé pour preuve formelle |
| **P88** Non-contradiction | `periphery/pepites_search_algo/P88__Non_contradiction.md` | `¬(A ∧ ¬A)` | OUI | OUI (logique de base) | `theorem non_contradiction (A : Prop) : ¬(A ∧ ¬A)` | OUI | OUI (Lean 4 pur) | NON | Aucune | CANONICAL_CANDIDATE | Néant — prouvable immédiatement |
| **P100** Stabilité Lyapunov def | `periphery/pepites_search_algo/P100__Stabilite_de_Lyapunov_Ls_Ls.md` | `L(Φ(s)) ≤ L(s)` | OUI | NON (kernel scellé) | `axiom lyapunov_non_growth (ds : DomainState) (s : Nat) : ds.level (ds.step s) ≤ ds.level s` | OUI (axiome HYPOTHESE_TEMPORAIRE) | NON (L et Phi non concrets) | OUI (L) | Définition concrète de L et Phi | CANONICAL_CANDIDATE | Fournir L : Nat → Float et Phi concrets |
| **P107** Stabilité δ-ε | `periphery/pepites_search_algo/P107__Stabilite_Lyapunov.md` | `∀ε>0, ∃δ>0: ‖x₀‖ < δ → ‖x(t)‖ < ε` | NON | NON | `axiom P107_lyapunov_delta_epsilon ...` | OUI (scaffold axiomatique HYPOTHESE_TEMPORAIRE) | NON | NON | `norm : DomainState → Float` ; `iterate : DomainState → Nat → Nat` | PROVISIONAL | Définir norm et iterate dans sandbox périphérique |
| **P161** Coût énergétique | `periphery/pepites_search_algo/P161__Calibration_energetique_temporelle_loi_finale.md` | `Coût(A,t) = f(M(t), Rc(t), dM/dt, contexte_humain(t))` | OUI (structure) | NON | `structure CanonicalState where S Phi I tau L` | PARTIEL (structure seulement) | NON | OUI (Cout) | `Time`, `Memory`, `Rc(t)`, `dM/dt` | PROVISIONAL | Formaliser les types temporels et de ressources |
| **Balance_math** | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md` | `B_Etienne(n) = équilibre(grandeur, écart, ratio, structure)` | OUI (recherche) | NON — hors décisionnel X-108 | `def B_Etienne : Nat → Float` | OUI (définition simple) | NON (composantes non définies) | OUI (B_Etienne) | `grandeur(n)`, `écart(n)`, `ratio(n)`, `structure(n)` | PROVISIONAL | Définir les 4 composantes |
| **PrimePartitionLab** | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md` | `Part(n) = partitions de n`, `p(n) = \|Part(n)\|` | OUI (recherche) | NON | `def Part : Nat → List (List Nat)` | OUI | NON (algorithme manquant) | OUI (p_n) | Algorithme de partition ; preuve de terminaison | PROVISIONAL | Implémenter l'algorithme de partition récursif |
| **LTCU+** | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md` | `L_u = Σ(L_s, L_m, L_e, L_t, L_r)` | NON | NON | — | NON | NON | NON | Définition des 5 couches L_s..L_r | DO_NOT_USE_YET | Définir les 5 couches sémantiques |
| **λ(t)** calibrateur | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md` | `λ(t)` — calibrateur temporel | NON | NON | — | NON | NON | OUI (lambda_t) | Formule complète ; domaine et codomaine | DO_NOT_USE_YET | Obtenir la formule dans une source lisible |
| **BALMA** | — (sources illisibles) | MISSING_CONTEXT | NON | NON | — | NON | NON | NON | Export .docx → .md (v1cano.docx, formalisermath.docx) | MISSING_CONTEXT | NE PAS INVENTER — exporter les sources .docx |
| **SYRIQ** | — (sources illisibles) | MISSING_CONTEXT | NON | NON | — | NON | NON | NON | Export .docx → .md | MISSING_CONTEXT | NE PAS INVENTER — exporter les sources .docx |

---

## Règle de lecture

- **"Prouvable maintenant ?"** = peut être prouvé en Lean 4 sandbox périphérique SANS sorry SANS axiome non marqué HYPOTHESE_TEMPORAIRE
- **"Axiomatisable ?"** = peut être posé comme axiome HYPOTHESE_TEMPORAIRE dans `Obsidia_Peripheral_Axioms.lean` sans risque de contradiction connue
- **"Usage Obsidure"** = Obsidure peut citer ou utiliser cet item dans ses réponses et mappings
- **"Usage Kernel/Sigma/Guard"** = utilisable dans les couches protégées — toujours via le kernel scellé, jamais via cette sandbox
