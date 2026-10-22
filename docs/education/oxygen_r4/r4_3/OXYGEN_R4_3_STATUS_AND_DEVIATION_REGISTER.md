# Oxygen R4.3 — statut, conformité et déviations (après la passe R4.3.1 / curriculum V0.4)

## 1. Généalogie de la calibration

| Révision | Relecture | Verdict | Cause |
|---|---|---|---|
| R4.3.0 | technique | PASS_WITH_NB | témoin mêlé déséquilibré accepté par le prototype du relecteur |
| R4.3.1 (marge δ par classe, filtre ≥ 50 %, définitions) | technique, témoins **réécrits** | **FAIL** | le filtre à 50 % supprime les traits discriminants quand les sens sont équilibrés (POS-COV 0/8) ; justification **fausse** ; cas « même provenance » non spécifié ; la prévision « 0/18 » de l'auteur était fausse (4/18 mesuré) |
| R4.3.2 (filtre informationnel C1, contre-preuve C2, même provenance C3, contrastes consultatifs C4) | technique, **jeu de témoins neuf** haché avant exécution (`a4b0c28d…`) | **HOLD_CALIBRATION** | positifs obligatoires OK (POS-COV 8/8, précision 1,0) ; **deux négatifs acceptés** : ADV-3 (trait grammatical exclusif **par accident** du curriculum → voie (b) sans indice de sens, en D et en B) et NEG-MIX-UNBAL en configuration B (C2 dépend de la lemmatisation) |

**Projection P-CAL (R4.3.2, enseignement seul, pour information) :** 3 réponses sur 18, toutes justes. Couverture 0,167, sous le seuil de 0,20 : **non satisfait**.

## 2. Décision appliquée

La règle du mandat s'applique : un témoin négatif reste accepté, donc **HOLD_CALIBRATION**.

**Aucun correctif R4.3.3 n'est produit dans cette passe.** Trois révisions successives ont chacune été corrigées **après** observation de témoins. Continuer à corriger règle par règle reviendrait à **régler sur les témoins** (STOP_TUNE).

**Analyse de cause commune (sans proposition de réglage) :**
- avec 2 à 5 exemples par sens, des traits deviennent exclusifs d'une étiquette **par accident**, ce qui pose un problème de taille d'échantillon ;
- la **voie (b)**, qui permet de répondre avec une seule classe de preuve, transforme ces accidents en réponses assurées ;
- la voie (a) est **peu exigeante** : p = 1 − ∏(1 − r) ≥ 0,5 dès que r ≥ 0,5, y compris avec l'a priori r = 0,5 d'une classe jamais vérifiée (N = 0) ;
- C2 est fragile sans lemmatisation (configuration B).

**Questions ouvertes pour une éventuelle R4.4**, à décider par le fondateur **avant** toute rédaction :
- supprimer la voie (b) ;
- exiger N_c ≥ 1 pour qu'une classe vote ;
- ne tester la calibration que sur un curriculum enrichi.

## 3. Conformité de R4-Core (G1 à G5), inchangée

| Écart | Statut |
|---|---|
| G1 (négation), G3 (`SUSPENDU` dans `retrieve`), G4 (journal des réinterprétations), G5a (T-GLOSE), G5c (cas K9) | **à corriger** avant toute implémentation déclarée conforme |
| G2 (filtre de longueur) | à déclarer dans le contrat |
| G5b | dépend de l'option retenue |
| G5d, G5e | non applicables |

Les corrections et leurs tests de non-régression sont définis dans `OXYGEN_R4_3_CONFORMANCE_GAPS.md`. **Aucun code n'a été modifié.**

## 4. Curriculum V0.4, indépendant de la calibration

Livrables dans `C:\Users\User\Documents\OBSIDIA_HANDOFF\oxygen_curriculum_v04\` :

| Fichier | Contenu |
|---|---|
| `WRITER_BRIEF_CURRICULUM_V04.md` | seul document remis au rédacteur : inventaire, au moins 5 leçons par sens, exercices, corrections au format K2, paires voisines, items ambigus, variété, progression, provenance ; aucun examen, aucune métrique, aucun code |
| `CURRICULUM_V04_SCHEMA.md` | schéma JSON ; distinction V0 / V0.4 / exercices / développement / prospectif ; recevabilité par l'opérateur (quotas, disjonction avec V0, **avec le RED V0.3 privé**, OK/KO seulement), CV-NO-TABLE, format des corrections, non-recopie, empreinte |
| `EXPERIMENT_MATRIX_V04.md` | conditions EXP-A, EXP-A′, EXP-B, EXP-C, REF-V0 et REF-V0′ ; attribution calibration / curriculum / interaction ; mesures identiques ; un seul passage par jeu |

**Indépendance du rédacteur.** Claude, auteur exposé aux examens, **ne rédige pas** le curriculum. Un agent lancé par Claude ne garantit pas une indépendance **vérifiable** : même compte Windows, retour de rapport, consignes écrites par Claude. Le dispositif crédible est le suivant :
- un **rédacteur humain**, ou une personne désignée par le fondateur, qui n'a jamais vu les examens ;
- un stockage hors de portée de Claude ;
- un **opérateur** distinct pour la recevabilité, qui seul confronte le curriculum au RED V0.3 privé.

**Statut : prêt pour la rédaction, dès que le rédacteur est désigné.**

## 5. Déviations par rapport à R4.2.2 (proposées, **non verrouillées**)

| Contrat | Déviation |
|---|---|
| K4 | rétrécissement appliqué aux **comptes de réussites** (Beta), et non aux similarités |
| K6 | voix = fiabilité de la classe, et non similarité |
| Condition 1 | ajout de la voie (b) (une classe, r ≥ 0,75) ; **c'est elle qui a produit ADV-3** |
| K7 | ajout de l'origine `RAPPEL` |
| K3 | précision « même provenance → une preuve » (C3) |
| Nouvelles garde-fous | filtre informationnel C1 ; contre-preuve C2 |

**Aucune de ces déviations n'est pré-enregistrée**, puisque la calibration est en HOLD.
