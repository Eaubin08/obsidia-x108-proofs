# SOURCE_LEDGER.md
## Obsidia X-108 — Mémoire mathématique Obsidure (readonly)
## Rôle : traçabilité factuelle de chaque source lue. Sans extrapolation.
## Dernière mise à jour : 2026-06-25
## READONLY = True | kernel_mutation = False | decision_authority = KX108_ONLY

---

## Légende des statuts

| Statut | Signification |
|---|---|
| CANONICAL_CANDIDATE | Source lisible, formule extractable, validée par le registre pépites |
| PROVISIONAL | Source lisible, formule partielle ou dépendances manquantes |
| AMBIGUOUS | Contenu présent mais interprétation incertaine |
| MISSING_CONTEXT | Source illisible (binaire, .docx non exporté) ou concept non documenté lisiblement |
| DO_NOT_USE_YET | Trop peu de contexte pour axiomatiser sans risque d'erreur |

---

## Source 1 — P36

**Chemin :** `periphery/pepites_search_algo/P36__Quintuplet_detat_canonique_S_I_L.md`
**Type :** Pépite Markdown — définition de structure
**Concepts trouvés :**
- Quintuplet canonique `(S, Φ, I, τ, L)` : état d'admissibilité complet du domaine
- S = score courant (Float)
- Φ = fonction de transition d'état
- I = entrée courante
- τ = seuil temporel (Nat)
- L = fonction de Lyapunov / énergie
**Statut :** CANONICAL_CANDIDATE
**Résumé factuel :** La pépite P36 définit le quintuplet canonique d'état. C'est la structure de base référencée dans P100 et P107. La formule est `(S, Φ, I, τ, L)`. Aucune preuve Lean associée dans cette pépite — la structure est esquissée dans P161. Statut registre : À_PROUVER.

---

## Source 2 — P42

**Chemin :** `periphery/pepites_search_algo/P42__Seuil_G1_ACT_si_S.md`
**Type :** Pépite Markdown — loi de seuil
**Concepts trouvés :**
- Règle G1 : `θ ≤ m.S → ACT`
- θ = seuil de décision (Float/Rat)
- m.S = score du message/domaine courant
- Déclenchement de l'action si score sous le seuil
**Statut :** CANONICAL_CANDIDATE
**Résumé factuel :** P42 est marquée FORMALISÉ dans le registre — la preuve formelle G1 réside dans `proofs/lean/Obsidia/Basic.lean` (scellé, DO_NOT_TOUCH). La version périphérique est analogique uniquement. Ne pas reproduire la preuve formelle hors du kernel scellé.

---

## Source 3 — P88

**Chemin :** `periphery/pepites_search_algo/P88__Non_contradiction.md`
**Type :** Pépite Markdown — axiome logique
**Concepts trouvés :**
- Non-contradiction : `¬(A ∧ ¬A)`
- Théorème de logique classique, prouvable en Lean 4 core sans imports externes
**Statut :** CANONICAL_CANDIDATE
**Résumé factuel :** P88 est marquée FORMALISÉ dans le registre. Le théorème est directement prouvable en Lean 4 pur (`fun ⟨ha, hna⟩ => hna ha`). Pas de dépendances manquantes pour cette pépite.

---

## Source 4 — P100

**Chemin :** `periphery/pepites_search_algo/P100__Stabilite_de_Lyapunov_Ls_Ls.md`
**Type :** Pépite Markdown — propriété de stabilité
**Concepts trouvés :**
- Stabilité Lyapunov : `L(Φ(s)) ≤ L(s)`
- Définition de décroissance de la fonction d'énergie le long des trajectoires
**Statut :** CANONICAL_CANDIDATE
**Résumé factuel :** P100 est marquée FORMALISÉ (définition) dans le registre. La définition est claire. La preuve Lean concrète nécessite une définition explicite de L et Φ — dans la sandbox périphérique, cela est couvert par un axiome temporaire (HYPOTHESE_TEMPORAIRE) en attendant la formalisation complète.

---

## Source 5 — P107

**Chemin :** `periphery/pepites_search_algo/P107__Stabilite_Lyapunov.md`
**Type :** Pépite Markdown — stabilité δ-ε
**Concepts trouvés :**
- Stabilité au sens de Lyapunov : `∀ε>0, ∃δ>0: ‖x₀‖ < δ → ‖x(t)‖ < ε`
- Dépend de `norm` (norme sur l'espace d'état) et `iterate` (itération de Φ)
**Statut :** PROVISIONAL
**Résumé factuel :** P107 est marquée À_PROUVER dans le registre. La formulation δ-ε requiert une définition de `norm` sur `DomainState` et une fonction `iterate` — ni l'un ni l'autre n'est défini dans les sources lisibles. La preuve ne peut pas être complétée sans ces dépendances. Un scaffold axiomatique (HYPOTHESE_TEMPORAIRE) est fourni dans la sandbox périphérique.

---

## Source 6 — P161

**Chemin :** `periphery/pepites_search_algo/P161__Calibration_energetique_temporelle_loi_finale.md`
**Type :** Pépite Markdown — loi de coût énergétique
**Concepts trouvés :**
- Loi de coût : `Coût(A,t) = f(M(t), Rc(t), dM/dt, contexte_humain(t))`
- Structure Lean esquissée : `CanonicalState` avec champs S, Phi, I, tau, L
- M(t) = mémoire au temps t, Rc(t) = ressource cognitive au temps t
**Statut :** PROVISIONAL
**Résumé factuel :** P161 est marquée À_PROUVER. La structure `CanonicalState` esquissée est la base de `DomainState` dans la sandbox. Les types `Time`, `Memory`, `Rc` ne sont pas définis dans les sources lisibles. Le terme `dM/dt` implique une dérivée non formalisée. L'axiomatisation complète est bloquée sur ces dépendances.

---

## Source 7 — extracted_text_all.md

**Chemin :** `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md`
**Type :** Markdown d'extraction — texte composite de sources variées
**Concepts trouvés :**
- **Balance_math** : `B_Etienne(n) = équilibre(grandeur(n), écart(n), ratio(n), structure(n))` — opérateur de lecture des grandeurs mathématiques. Domaine : Recherche math / moteur exploratoire. PAS dans X-108 décisionnel.
- **PrimePartitionLab** : `Part(n) = ensemble des partitions entières de n`, `p(n) = |Part(n)|` — lab nombres premiers et partitions
- **LTCU+** : `L_u = Σ(L_s, L_m, L_e, L_t, L_r)` — pont sémantique 5 couches
- **Balance_exp** : balance exponentielle — régule les flux (peu détaillée)
- **λ(t)** : calibrateur temporel — formule non précisée dans la source
- **ADeLe** : 18 axes de calibration — listés mais non détaillés dans cette source
**Statut :** PROVISIONAL (Balance_math, PrimePartitionLab) / DO_NOT_USE_YET (LTCU+, λ(t))
**Résumé factuel :** Source composite. Les formules Balance_math et PrimePartitionLab sont lisibles et extractables. LTCU+ et λ(t) ont des formules partielles insuffisantes pour une axiomatisation sûre. ADeLe est mentionné sans détail.

---

## Source 8 — formalisation_math (desktop)

**Chemin :** `C:\Users\User\Desktop\formalisation_math\`
**Type :** Dossier — fichiers générés (INDEX.md, FILE_DE_PREUVE.md, et 5 autres)
**Concepts trouvés :** Dépend du contenu des 7 fichiers — référencés comme base de la mémoire mathématique
**Statut :** PROVISIONAL (contenu non relu dans cette session — référence déclarative)
**Résumé factuel :** Ce dossier contient les fichiers générés qui constituent la source primaire de la mémoire Obsidure. Il est déclaré comme `source_root` dans MATH_MEMORY_INDEX.json. Son contenu exact doit être relu à chaque mise à jour de la mémoire.

---

## Source 9 — SECTION_V_Maths_Verite.docx

**Chemin :** `C:\Users\User\Desktop\Obsidia Master\OBSIDIA_SECTIONS_I_VII\SECTION_V_Maths_Verite.docx`
**Type :** Document Word binaire — ILLISIBLE PAR LA MACHINE
**Concepts trouvés :** Aucun extractable directement
**Statut :** MISSING_CONTEXT
**Résumé factuel :** Ce fichier est au format .docx binaire. La machine ne peut pas en lire le contenu sans conversion préalable. Tout concept cité comme provenant de ce fichier est MISSING_CONTEXT jusqu'à export en .md ou .txt par Étienne.

---

## Source 10 — obsidia/ (contenu .docx)

**Chemin :** `C:\Users\User\Desktop\Obsidia Master\obsidia\`
**Type :** Dossier contenant des fichiers .docx — ILLISIBLES PAR LA MACHINE
**Concepts trouvés :** Aucun extractable (inclut v1cano.docx, formalisermath.docx, et autres)
**Statut :** MISSING_CONTEXT
**Résumé factuel :** Tous les fichiers .docx de ce dossier sont illisibles par la machine. BALMA et SYRIQ sont mentionnés comme provenant de ces sources — ils restent MISSING_CONTEXT. Ne pas inventer leur contenu.

---

## Note de clôture

Ce ledger est en lecture seule. Il ne constitue pas une preuve. Il trace les sources telles qu'elles ont été lues, sans extrapolation ni invention. Toute source MISSING_CONTEXT doit être exportée par Étienne avant d'être utilisée.
