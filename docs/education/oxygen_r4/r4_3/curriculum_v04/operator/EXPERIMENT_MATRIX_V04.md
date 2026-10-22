# Matrice des conditions expérimentales (calibration × curriculum)

| Condition | Élève | Curriculum | Question isolée |
|---|---|---|---|
| **EXP-A** | R4-Core figé (`c9a3d861`) | V0 | référence (abstention à 100 % déjà observée en développement) |
| **EXP-A′** | R4-Core figé | **V0.4** | effet du **curriculum seul**, sans calibration |
| **EXP-B** | R4.3 calibré | V0 | effet de la **calibration seule** |
| **EXP-C** | R4.3 calibré | **V0.4** | effet combiné |
| REF-V0 | V0 (`dfef4f98`) | V0 | référence historique |
| REF-V0′ | V0 | V0.4 | V0 avec plus de leçons (facultatif) |

L'interface est compatible : R4-Core et V0 acceptent tout curriculum au format `learn` / `apply_correction`. Un adaptateur côté banc convertit le JSON V0.4 en items et corrections, **sans toucher à l'élève**.

**Attribution :**

| Effet | Calcul |
|---|---|
| calibration | EXP-B − EXP-A, et EXP-C − EXP-A′ |
| curriculum | EXP-A′ − EXP-A, et EXP-C − EXP-B |
| interaction | (EXP-C − EXP-A′) − (EXP-B − EXP-A) |

Une amélioration obtenue en donnant **plus de leçons** n'est **jamais** attribuée au seul algorithme.

**Mesures**, identiques pour toutes les conditions :
- exactitude ;
- couverture ;
- HOLD approprié et injustifié ;
- **erreurs assurées** (réponses fausses non abstenues) ;
- robustesse aux contradictions (exercice contesté) ;
- mémoire après redémarrage ;
- origines (`ACQUIS_LECON`, `CORRIGE`, `TRANSFERE`, `RAPPEL` exclu) ;
- effet de l'ajout de leçons (courbe à 2, 3 et 5 leçons par sens, sous-échantillons figés) ;
- **comportement sur les contextes sans rapport** : témoins synthétiques et items ambigus du curriculum.

**Bancs :**
- **porte P-CAL** : sur le curriculum (leave-one-out imbriqué), avant tout examen ;
- **développement** : RED V0.3, exploratoire et contaminé, déclaré comme tel ;
- **prospective** : nouveau jeu indépendant, seule preuve, HOLD_INDEPENDENCE.

Méthode, ordre et seuils sont **identiques** pour toutes les conditions comparées. Chaque condition passe **une seule fois** sur chaque jeu.
