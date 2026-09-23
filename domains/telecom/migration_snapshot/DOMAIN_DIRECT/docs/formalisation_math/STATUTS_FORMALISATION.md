# STATUTS DE FORMALISATION MATHÉMATIQUE — Pépites et Lois
**Source :** `CHECKPOINT_V1/09_FORMALISATIONS_MATH_A_VENIR.md` (2026-06-20)  
**Règle :** NE PAS LANCER LEAN. NE PAS LANCER TLA. CLASSIFICATION SEULEMENT.

---

## 1. DÉJÀ FORMALISÉ

### Pépites formalisées (FORMALISE ou ANCREE)

| Code | Titre | Statut |
|---|---|---|
| P1 | Mémoire ≠ stockage | FORMALISE |
| P2 | Mémoire fractale hiérarchique | FORMALISE |
| P3 | Oubli actif | FORMALISE |
| P4 | Mémoire comme condition d'éthique | FORMALISE |
| P5 | Mémoire humaine / mémoire système | FORMALISE |
| P6 | Mémoire comme récit vivant | FORMALISE |
| P7 | Mémoire comme garde-fou contre l'hallucination | FORMALISE |
| P8 | Mémoire transversale | FORMALISE |
| P9 | Sens ≠ information | FORMALISE |
| P10 | Cadre avant réponse | FORMALISE |
| P11 | Refus hors cadre | FORMALISE |
| P12 | Désambiguïsation contextuelle | FORMALISE |
| P13 | Immutabilité par sceau Merkle | ANCREE |
| P14 | Traduction humain/machine | FORMALISE |
| P15 | Immutabilité forte (Sensitivity) | ANCREE |
| P16 | Rupture data/sens | FORMALISE |
| P17 | Croissance du log d'audit | ANCREE |
| P18 | Sémantique avant calcul | FORMALISE |
| P19 | Pluralité des niveaux de sens | FORMALISE |
| P20 | Sens avant performance | FORMALISE |
| P21 | Sémantique transversale | FORMALISE |
| P22 | Le symbolique n'est pas décoratif | FORMALISE |
| P23 | Compression du sens | FORMALISE |
| P24 | Non-verbal comme vecteur | FORMALISE |
| P25 | Symboles comme passerelles | FORMALISE |
| P26 | Résonance plutôt que calcul | FORMALISE |
| P27 | Transmission implicite | FORMALISE |
| P28 | Récit comme structure | FORMALISE |
| P29 | Mythologie vivante | FORMALISE |
| P30 | Symbolique opératoire | FORMALISE |
| P31 | Archétype | FORMALISE |
| P32 | Rituel comme séquence symbolique | FORMALISE |
| P33 | Symbolique transversal | FORMALISE |
| P34 | Kernel = intersection des contraintes | FORMALISE |
| P35 | Preuve formelle sans sorry | FORMALISE |
| P37 | Formalisation : narratif vers math | FORMALISE |
| P38 | Filtre éthique chi(t) | FORMALISE |
| P39 | Invariant permanent | FORMALISE |
| P40 | Axiome non dérivable | FORMALISE |
| P41 | Déterminisme D1 | ANCREE |
| P42 | Seuil G1 : ACT si theta ≤ S | FORMALISE |
| P43 | Pas de BLOCK natif L11.3 | ANCREE |
| P44 | Verrou temporel X-108 | FORMALISE |
| P45 | Skew négatif vers HOLD | FORMALISE |
| P46 | Consensus fail-closed 4 agents | FORMALISE |
| P64 | Ordre = 1 - entropie normalisée | FORMALISE |
| P67 | Filtre éthique continu chi(t) | FORMALISE |
| P68 | Éthique intégrée sur le temps | FORMALISE |
| P69 | Responsabilité action/conséquence | FORMALISE |
| P70 | Consentement binaire | FORMALISE |
| P71 | Transparence universelle | FORMALISE |
| P72 | Équité epsilon-approchée | FORMALISE |
| P73 | Non-nuisance | FORMALISE |
| P74 | Bienfaisance maximale | FORMALISE |
| P75 | Justice proportionnelle | FORMALISE |
| P76 | Budget énergétique E_c(t) | FORMALISE |
| P77 | Flux énergétique dE/dt | FORMALISE |
| P78 | Réserve énergétique | FORMALISE |
| P79 | Régénération en repos | FORMALISE |
| P85 | Loi de réciprocité | FORMALISE |
| P86 | Consensus supermajorité 3/4 | ANCREE |
| P87 | Fail-closed sans supermajorité | ANCREE |
| P88 | Non-contradiction | FORMALISE |
| P89 | Complétude | FORMALISE |
| P90 | Cohérence | FORMALISE |
| P91 | Décidabilité | FORMALISE |
| P93 | P inclus dans NP | FORMALISE |
| P94 | Réductibilité | FORMALISE |

---

## 2. DOCUMENTÉ MAIS NON APPLIQUÉ

| Code | Titre | Note |
|---|---|---|
| P92 | Calculabilité (Turing) | REFERENCE_ONLY_NOT_BOUND — présent en référence, non lié au runtime |

---

## 3. À PROUVER (A_PROUVER)

| Code | Titre | Note |
|---|---|---|
| P36 | Quintuplet d'état canonique (S,I,L) | Fichier Lean existe — statut A_PROUVER |
| P107 | Stabilité de Lyapunov δ-ε (L(Φ(s)) ≤ L(s)) | Sandbox active — Solve Engine en cours |
| P161 | Calibration énergétique temporelle | Fichier Lean existe — à valider |

---

## 4. À FORMALISER (A_FORMALISER)

| Code | Titre | Domaine |
|---|---|---|
| P57 | Entropie de Shannon | Thermodynamique informationnelle |
| P58 | Néguentropie | Thermodynamique informationnelle |

---

## 5. PRÉVU MAIS NON FORMALISÉ

| Sujet | Note |
|---|---|
| Seuils par domaine (bank threshold, trading G1, GPS alerting) | NOT_YET_IMPLEMENTED |
| Formalisation multi-domaine P143 | Documentée, non formalisée |
| Spécialisation par domaine P142 | Documentée, non formalisée |
| Runtime ACT réel | Prévu en roadmap |
| Vue régulateur (audit trail formel) | Prévu |
| Tests adversariaux formels | Prévu |
| Machine-checking TLA+ en CI automatique | Possible (tla2tools.jar), non activé |

---

## 6. À RELIER PLUS TARD

| Sujet | Domaine cible | Note |
|---|---|---|
| P57 (Shannon) + P58 (Néguentropie) → Kernel | Énergie/Entropie kernel | À relier quand P57/P58 formalisés |
| 34 Arbres cognitifs → domaines bank/trading/GPS | Cognitive trees domain binding | 18 liés Brody, 16 non liés |
| Balance exponentielle → domaines formels | Pondération non-linéaire | Documentée, non reliée |
| Filtre éthique chi(t) → domaines | Éthique transversale | P38/P67/P68 formalisés, reliaison à faire |

---

## 7. À NE PAS RELIER MAINTENANT

| Sujet | Raison |
|---|---|
| Brody Education adapter → kernel | Rester séparé |
| Graphiti V20 live write → kernel | INTERDIT — DO_NOT_CONNECT_TO_KERNEL |
| CIC modules → kernel | Statut à statuer |
| Frontier Ledger → kernel | Statut à statuer |
| 3316 items REFERENCE_ONLY → runtime | Ne pas relier en masse sans décision Étienne |
