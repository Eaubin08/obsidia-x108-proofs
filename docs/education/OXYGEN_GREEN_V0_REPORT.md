# Oxygen — pilote « force » : GREEN technique isolé V0 — rapport

**Date :** 2026-10-22 · **Auteur :** Claude · **Autorisation :** fondateur, `ISOLATED_GREEN_BUILD=GO` · **Intégration runtime : NON.**
Conception verrouillée : `OXYGEN_GREEN_DESIGN_V0.md` R3 (sha256 `01df067f1b0075db17cc0d86de1a81b844c6e670a4cbcfaef42e3a56e19632d5`), pré-enregistrement `OXYGEN_GREEN_PREREGISTRATION_V0.md`, commit documentaire `24fa978b`.

> **Avertissement.** Les résultats ci-dessous sont obtenus sur le **banc de développement RED V0.3**, dont les examens ont été lus par l'auteur. Ils ne constituent **pas** une validation indépendante de l'apprentissage. Seule l'évaluation prospective sur un jeu indépendant (pré-enregistrement §3) pourra en tenir lieu.

## 1. Implémentation

| Fichier | Rôle |
|---|---|
| `tests/education_pilot/student_sandbox/features.py` | extracteurs de traits génériques, identiques pour tout mot : positions `P±n`, n-grammes contenant la cible, forme de surface, déterminant précédent, mots pleins, trigrammes de caractères |
| `tests/education_pilot/student_sandbox/exemplar_student.py` | `ExemplarSenseStudent` : exemples, Naive Bayes pondéré (Laplace 1,0), vote k-NN (k = 3, Jaccard pondéré), bonus de cue (+2,0), softmax, abstention (τ 0,5 ; δ 0,15 ; trait non trivial vu), corrections (sens = `ex[3]`, segment « » comme cue, retrait sans effacement), révisions (une par appel), `retrieve` / `history`, fichier d'état unique canonique avec sha256 |
| `tests/education_pilot/test_exemplar_student_unit.py` | 16 tests côté hôte, sans examens |

Paramètres strictement ceux du tableau R3 ; aucun n'a été modifié après observation.
Le banc RED V0.3 (`_bench.py`, `_criteria.py`, `conftest.py`, `test_pilot_force_*.py`, `_pilot_data.py`, examens privés) est **inchangé** ; seul `OXYGEN_PILOT_STUDENT=exemplar_student:ExemplarSenseStudent` change.

**Interprétations d'implémentation**, fixées avant tout passage sur les examens :
- l'identifiant d'un exemplaire est celui de la phrase enseignée ; les identifiants de correction (C-n, C-X) figurent dans sa `provenance` pour `retrieve` et `history` ;
- `answer` ne cite que des identifiants d'items enseignés, jamais de correction. C'est ce qui garantit que C-X n'apparaît jamais dans une provenance de réponse, sans règle propre à C-X ;
- l'occurrence du mot cible est repérée par préfixe générique (`max(4, len − 2)` caractères repliés) ;
- les seules listes lexicales sont des classes grammaticales fermées : déterminants, possessifs, quantifieurs, mots-outils.

**Interprétations relevées par l'audit (non déclarées avant, conservées telles quelles, sans modification du code après observation) :**
- le trait de forme de surface (SURF), sans poids dans la table R3, reçoit 1,0, comme les traits de la cible ;
- un cue est reconnu comme sous-chaîne de la phrase repliée, sans frontière de mot ;
- les cues ne sont jamais retirés (`rev_retired` reste vide) et ne sont pas filtrés par `as_of_revision` ; c'est incomplet par rapport au schéma R3 et sans effet sur les tests actuels ;
- une même phrase reçue deux fois par `learn` retire sa première occurrence (même règle que pour les corrections).

Toute correction de ces points exige une révision R4 relue, évaluée sur un jeu indépendant.

**Écho de contamination « sa » :** R3 cite « sa » comme exemple de déterminant. Cette forme est absente de l'enseignement et présente dans les examens privés. Elle n'a **aucun traitement spécial** : c'est un membre de la classe fermée des possessifs, comme les autres. C'est consigné dans `features.py` et dans le pré-enregistrement §7.

**Correction de mon propre test unitaire :** le test « aucun mot de l'enseignement dans les littéraux » échouait sur « toutes », qui appartient à la liste fermée des quantifieurs. La définition du test exclut désormais ces classes grammaticales fermées. Le banc RED n'est pas touché.

## 2. Tests unitaires (hôte, sans examens) : 16 / 16

- **Code source :** aucun identifiant de sens comme jeton ; uniquement des imports de la bibliothèque standard et du bac à sable ; aucun mot de contenu de l'enseignement dans les littéraux.
- **Apprentissage :** l'élève vide n'a aucun sens et répond HOLD partout ; `learn` construit l'état, un appel = une révision ; un mot non enseigné donne HOLD.
- **Corrections et mémoire :**
  - sens = `ex[3]` ; l'exemplaire précédent est retiré, non effacé ; cues = segments « » ;
  - `history.content == retrieve(as_of_revision)` ; `as_of_revision` reste stable après révision ;
  - la provenance d'`answer` ne cite que des items enseignés du sens répondu.
- **Persistance :** sauvegarde et rechargement donnent des réponses identiques ; un espace ajouté, un poids modifié ou une révision modifiée lèvent `StateIntegrityError`.
- **Leave-one-out sur l'enseignement**, en vérification seule et sans aucun réglage : **7 / 18 justes, 5 HOLD**.

## 3. Banc RED V0.3 en conteneur, élève GREEN

Une campagne complète : 22 contrôles verts, 7 / 7 tests d'interface verts, invariant B10 rouge, 0 / 10 critères d'acquisition, aucun conteneur résiduel.
Une seconde exécution, **avec le même code**, a servi uniquement à relever les exactitudes agrégées ci-dessous. Elle compte dans le budget d'itérations : 1 build, 2 passages sur le banc de développement. **Ce tableau n'a pas été vérifié indépendamment :** l'auditeur, resté non contaminé, ne pouvait pas le recalculer sans lire les examens. Il a confirmé les verdicts par test (0 / 10, 7 / 7, invariant rouge, 22 contrôles verts).

| Épreuve | Exactitude « force » | Meilleure ligne de base | HOLD approprié | HOLD injustifié | Sens à 100 % |
|---|---|---|---|---|---|
| **T0** (X0, avant enseignement) | 0,00 | — | 1,00 | 1,00 | aucun |
| **T1** (X1) | 0,57 | 0,57 | 1,00 | 0,29 | 4 / 7 |
| T1 far (X1-far) | 0,50 | 0,50 | 1,00 | 0,50 | 4 / 7 |
| **T2** (X2, nouveau conteneur, état seul) | 0,43 | 0,57 | 1,00 | 0,14 | 3 / 7 |
| **T3** (X3, après leçons concurrentes) | 0,57 | 0,29 | 1,00 | 0,29 | 4 / 7 |
| T3 « chemin » | 0,00 | 0,50 | — | — | — |
| T3 « corriger » | 0,25 | 0,75 | — | — | — |
| **T4** (X4, transfert) | 0,29 | 0,57 | 1,00 | 0,29 | 2 / 7 |

Témoin « table » : stable (HOLD à T0 et à T1).

| Famille | Résultat |
|---|---|
| **Acquisition (10 critères)** | **0 / 10** |
| T1 | gain réel de 0 à 0,57, mais **égalité** avec la ligne de base trigramme ; la marge de 0,25 n'est pas atteinte |
| T2 | le rechargement est exact (tests unitaires : réponses identiques), mais l'exactitude sur X2 (0,43) est sous la ligne de base. T2 dépend aussi de T1. |
| T3 | l'acquis sur « force » n'est pas perdu (0,57, au-dessus de la ligne de base de 0,29). Le critère dépend de T1 et échoue donc. « chemin » et « corriger » ne sont pas appris (une seule leçon par sens). |
| T4 | 0,29, sous la ligne de base |
| **ABSTENTION** | HOLD approprié = 1,00 partout ; HOLD injustifié entre 0,14 et 0,50, au-dessus du plafond de 0,2 sur la plupart des examens |
| **RETRIEVAL** (sens, domaine, provenance, contexte) | 4 / 4 |
| **HISTORY** (révision, contradiction) | 2 / 2 |
| **INTEGRITY** (état de l'élève altéré) | 1 / 1 |
| **Invariant B10** (authenticité) | rouge par conception, non contourné |

## 4. Lecture

- **L'apprentissage modifie réellement l'état :** T0 = 0, puis T1 = 0,57 après enseignement. Mais sur ce banc, l'élève ne se distingue pas d'une ligne de base triviale : il l'égale en T1 et reste en dessous en T2 et en T4.
- **Les échecs sont des limites d'apprentissage, pas des défauts de protocole :** la référence parfaite satisfait les 10 critères, et le banc est inchangé.
- **Causes plausibles,** non testées puisqu'un réglage est interdit :
  - 14 leçons et 4 exercices seulement, avec 1 leçon par sens pour « chemin » et « corriger » ;
  - un bayésien naïf qui domine le vote k-NN, ce qui est un effet d'échelle des scores ;
  - une abstention trop fréquente sur les items décidables.
- Ces pistes **ne doivent pas** être exploitées sur ce banc. Toute modification exige une révision R4 avec relecture, et serait évaluée sur un nouveau jeu indépendant.

## 5. Audit indépendant

**PASS_WITH_NB** : conformité à R3, absence de spécialisation sur les examens (« sa » sans traitement spécial), état réellement modifié, révisions, provenance, redémarrage, isolation, aucune mutation réelle, banc RED inchangé (diff vide). Les cinq remarques non bloquantes sont intégrées au §1 et au §3. L'auditeur **n'a pas lu les examens** : il reste éligible comme rédacteur du jeu prospectif.

## 6. Ce qui n'est pas démontré

Aucune acquisition au-delà des lignes de base, aucun transfert, aucune compréhension. La mémoire d'interface (récupération, historique, intégrité locale) fonctionne, mais ce n'est **ni** une mémoire candidate B8, **ni** une connaissance validée, **ni** la naissance d'Oxygen. Aucune écriture en mémoire réelle ; B8, B9 et B10 sont intacts.
