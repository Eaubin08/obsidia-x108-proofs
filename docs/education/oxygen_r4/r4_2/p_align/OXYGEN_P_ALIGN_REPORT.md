# Oxygen R4 — porte de faisabilité P-ALIGN : rapport

**Date :** 2026-10-22 · **Base :** `c9d582a7` (contrats R4.2.2) · **Statut :** mesure technique sur les **seules leçons**. Ce n'est pas une preuve de généralisation. Aucun examen n'a été lu.

## 0. Contrôle du dernier delta (avant mesure)

La contre-vérification ciblée des ajouts postérieurs au tour 4 rend **PASS_WITH_NB** :
- D23 est restrictive (elle ne fait qu'ajouter des groupes `AMBIGU`) et cohérente avec F-A, B4, K3 et K9 ;
- l'état final reste une fonction de l'ensemble des leçons et corrections (vérifié sur C-4 → C-X, C-X → C-4 et C-X avant la leçon F5) ;
- la définition de 𝓛 est cohérente ; les passages barrés ne cachent aucune règle nouvelle.

Remarques consignées ici, **R4.2.2 non modifiée** :
- NB-1 : la ligne 360 (Finalisation NB-2) dit encore « et exclusivité », qui est remplacé par D23 ;
- NB-2 : la granularité des permutations de T-ORDRE-REEL est à fixer (item par item) ;
- NB-3 : le jeu de données et l'assertion de T-VETO (veto F6 **et** F5) sont à préciser.

## 1. Protocole exécuté

**Script :** `tests/education_pilot/r4_p_align_measure.py` (non suivi, sha256 `4d9be4773e8eace7893e50771374708d19a0017afd3ba824a4938a18cb62e4df`).

**Exécution :**
- une seule exécution de mesure. Un premier lancement a échoué **avant tout calcul**, sur un chemin d'export mal formé dans ma ligne de commande ; aucune donnée n'a été produite ;
- résultat brut : `p_align_result.json` (sha256 `9495694f68d28b20ffcbe5a2fdf41734f6e8c0498cb6678818dd64e162e8f43c`).

**Entrées :**
- `_pilot_data.py` : 18 items étiquetés de « force », 4 corrections et la contradiction ;
- export V1 en lecture seule, empreintes vérifiées par le script : `thes_fr` `378e4809…`, Morphalou `9e6e60da…`.

**Règles appliquées :** K1 et R4.2.1 B1–B5, F-A, R4.2.2 (reconnaissance dans 𝓛 seulement) et clôture (𝓛 = items reçus ; veto D23). Leave-one-out : on retire l'item, ses corrections (gloses et contrastes) et la contradiction si elle le vise.

**Seuils :** support ≥ 6, précision ≥ 0,50, **inchangés**.

## 2. Résultats

| Lemme | Items | Non muets | TP | FP | Muets (FN) | TN | Précision | Rappel | Couverture |
|---|---|---|---|---|---|---|---|---|---|
| **force** (porte) | 18 | **1** | 0 | 1 | 17 | non défini (aucun item négatif) | **0,00** | 0,00 | 0,056 |
| chemin (descriptif) | 2 | 0 | 0 | 0 | 2 | — | — | 0,00 | 0,00 |
| corriger (descriptif) | 2 | 0 | 0 | 0 | 2 | — | — | 0,00 | 0,00 |

- **17 items sur 18** n'évoquent **aucun** groupe de « force » : les phrases de leçon ne contiennent presque jamais de synonyme direct du mot cible.
- **Seul item non muet : E-F5-1 (F5).**
  - Le mot « ressort » a deux lemmes candidats (*ressort*, *ressortir*), soit un poids de 0,5.
  - Il évoque deux groupes, liés à F1 par la glose « vigueur » de C-1.
  - La prédiction est F1 : **faux positif**.
- **État appris complet :**
  - C-1 à C-4 sont interprétées normalement ; C-X met EX-F6 en `CONTESTÉ` (étiquette contestataire F5) ;
  - 7 liens, tous issus de **gloses** de correction ;
  - 2 groupes `AMBIGU`, évoqués par F1 et par F5 (veto D23).
- **Formes ambiguës :** 3 à 7 par item. Elles n'ont influé que sur E-F5-1.
- **« chemin » et « corriger » :** un seul groupe chacun, comme prévu, et aucune évocation.

## 3. Verdict automatique

**P_ALIGN = HOLD** : support 1 au lieu de 6, précision 0,00 au lieu de 0,50. La classe « alignement de la cible » est **désactivée**. P-LEX reste interdit.

## 4. Recalcul indépendant : **CONCORDANT**

Un relecteur technique a écrit sa propre implémentation, avant de lire mon script. Il retrouve des totaux et des issues par item **identiques**.

**Divergence de détail, sans effet :** mon script range les groupes par lemme **replié** (sans accents). Le groupe du lemme *forcé* (`thes_fr_15822`) est donc rattaché à tort à « force » : 16 groupes au lieu de 15. EX-F3 évoque ce groupe, mais il n'est lié à rien, et l'issue reste muette. **Le défaut est consigné, le script n'est pas corrigé** : le corriger imposerait une seconde mesure, et le résultat est identique selon le recalcul conforme.

**Autres points :**
- les marqueurs `ne … pas` et `ne … plus` sont absents de mon script, sans effet (aucun « ne » dans les corrections) ;
- quatre interprétations alternatives raisonnables, sans changer les seuils, laissent toutes le support à 1 au plus et la précision à 0. **Aucune ambiguïté décisive.**

**Contrôles :** leave-one-out étanche ; aucun voisinage ni transitivité ; `sense_id` jamais utilisé comme clé entre lemmes ; export et dépôt non modifiés.

## 5. Conséquences (phase 5)

**Fonctions restantes du corpus dans R4 :**
- lemmatisation (classe exemplaires : ensembles de lemmes candidats) ;
- détection `MOT_INCONNU` (K5) ;
- provenance des lemmes ;
- hypothèses non étiquetées « groupes évoqués » (K10). Elles restent calculables, mais sont presque toujours vides sur ce matériau.

**Plus aucune classe de preuve sémantique n'est tirée du corpus** (P-LEX et P-ALIGN en HOLD).

**Configurations A, B, C, D :**
- **définies et comparables**, mais leur **portée est réduite** ;
- D − B mesure désormais l'effet de la **lemmatisation** et de `MOT_INCONNU`, plus aucun apport sémantique du corpus ;
- C_mappée reste définie (table externe), mais elle sera presque toujours HOLD, puisque les questions évoquent rarement des groupes ;
- **pas de METRIC_HOLD** ; ce changement d'interprétation doit être déclaré dans tout rapport A, B, C, D.

**Hypothèses et ablations :**
- H3 (« le gain vient du corpus ») ne peut plus porter que sur la lemmatisation ;
- H3b, **M-CIBLE** et **SANS-CUE-CIBLE** deviennent **sans objet** : il n'y a plus de classe d'alignement de la cible à masquer ;
- l'**export V2** (prévu pour M-CIBLE) n'a donc **plus d'objet** dans l'état actuel.

**Aucun mécanisme de remplacement n'est activé.** Une autre heuristique exigerait une nouvelle révision architecturale relue.

## 6. Checkpoint proposé (non réalisé)

Commit borné à `tests/education_pilot/r4_p_align_measure.py` et à ce rapport, plus le résultat brut, copiés dans `docs/education/oxygen_r4/r4_2/p_align/`, après autorisation.
