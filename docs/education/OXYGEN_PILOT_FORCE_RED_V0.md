# Oxygen — pilote « force » : campagne RED isolée V0.3

**Date :** 2026-10-22 · **Auteur :** Claude · **Autorisation :** fondateur, `ISOLATED_RED_TESTS=YES`, `RED_BENCH_REPAIR=AUTHORIZED`, `RED_V03_REPAIR=GO` · **GREEN : interdit, non lancé.**
Spécification : `OXYGEN_TEXTUAL_LEARNING_PILOT_SPEC_V0.md` (§8b). Réconciliation mémoire : `OXYGEN_MEMORY_SEMANTIC_CROSSWALK_V0.md`.

## 0. Historique et rectifications

| Version | Audit indépendant | Cause |
|---|---|---|
| V0 | PARTIAL | RED passables par des élèves triviaux |
| V0.1 | **FAIL** | garde Python contournée (`_bench.D`, lecture disque) : un oracle passait 17 / 18. L'affirmation « Oracle 0 / 18 » du rapport V0.1 était **fausse** et est retirée. |
| V0.2 | **FAIL** | isolation Docker validée, mais **B1** l'ordre des questions = ordre des leçons (un oracle positionnel passait 4 RED d'acquisition sans apprendre) ; **B2** comparaison aux lignes de base *sens par sens* avec 1 item par sens : 6 RED impassables même par un élève parfait. Aussi : un `__pycache__` de V0.1 (ignoré par git) contenait les phrases d'examen ; témoin « table » toujours vrai. Les RED d'acquisition V0.2 n'étaient donc **pas valides** ; aucun de leurs échecs ne peut être compté comme capacité manquante. |
| V0.3 | (ce document) | corrections ci-dessous |

## 1. Sécurité et isolation (inchangée depuis V0.2, revalidée)

- **Élève :** conteneur Docker (`python:3.13-slim` épinglé par digest) lancé avec `--network none --read-only --user 65534 --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 256m` et une étiquette `oxygen_pilot_student=1`.
  - Il ne voit que `student_sandbox/` (lecture seule), son état temporaire et, pour les sondes, un répertoire `/extra` en lecture seule.
- **Examens et clés :** fichier privé **hors dépôt**, avec un canari.
  - En V0.3 : 8 items privés nouveaux et distincts (4 X1-far, 4 X3 « chemin » / « corriger »).
- **Sonde d'isolation :** elle parcourt tout le système de fichiers du conteneur et lit plus de 500 fichiers. Aucun canari, nom de fichier ni phrase d'examen n'y figure. Elle confirme aussi : réseau fermé, import du dépôt impossible, racine non inscriptible.
- **Fragments d'examen :** nouveau contrôle sur **tout le worktree**, fichiers suivis, non suivis et **ignorés** (caches Python compris) ; exclus : `.git`, `node_modules`, `.venv`, `venv` (risque résiduel faible). Résultat : zéro occurrence. Le `__pycache__` résiduel de V0.1 a été supprimé.
- **Ressources :**
  - les conteneurs étiquetés sont tués au début et à la fin de la session de tests ;
  - une seule campagne séquentielle par module (2 conteneurs successifs, jamais simultanés) ;
  - suite complète : 65 à 171 s selon la charge de la machine ; RED seuls 5 à 16 s.
- **Limites :**
  - la frontière repose sur Docker Desktop / WSL2 ;
  - les clés restent lisibles par le compte de l'opérateur-examinateur, ce qui est voulu.

## 2. Correction B1 — fuite par l'ordre

- **Mélange :** l'examinateur mélange chaque passation avec une graine privée (`secrets`), qui ne quitte jamais l'hôte. La réponse est rattachée côté hôte à l'identifiant interne de l'item.
- **Ce que reçoit l'élève :** contrôle `test_control_student_receives_only_word_and_sentence`. L'élève reçoit exactement `(mot, phrase)` : ni identifiant, ni numéro, ni domaine.
- **Contrôle positif :** `position_oracle_would_win_without_shuffling`. Dans l'ordre du fichier, l'oracle positionnel obtient 100 % sur X1 : la fuite B1 était réelle.
- **Contrôle négatif :** sur **200 permutations indépendantes**, l'oracle positionnel ne satisfait **aucun** critère d'acquisition.
  - Avant l'ajout d'items, il satisfaisait `t3_concurrent` dans 44 permutations sur 200 (2 items par mot) et `far_sentences` dans 1 sur 200. C'est ce qui a motivé les 8 items privés supplémentaires.
- **En conteneur :** l'élève `PositionOracle` échoue aux 10 RED.

## 3. Correction B2 — faisabilité mathématique

- **Critères :** ce sont des fonctions pures (`tests/education_pilot/_criteria.py`). Elles sont évaluées de la même manière pour l'élève, pour la référence parfaite et pour les stratégies triviales.
- **Comparaison aux lignes de base :** elle porte sur l'**exactitude agrégée** d'un examen (ou d'un mot pour « chemin » / « corriger »), plus jamais sens par sens. La marge est de 0,25.
- **Plafond réalisable :** contrôlé. Pour chaque examen, la meilleure ligne de base plus la marge reste ≤ 1,0.
  - Meilleures lignes de base V0.3 : X1 0,57 ; X1-far 0,50 (0,75 en V0.2) ; X2 0,57 ; X3 0,29 ; X4 0,57 ; « chemin » 0,50 ; « corriger » 0,75. « corriger » exige donc 1,0 : la marge est réalisable mais sans tolérance.
- **Référence parfaite :** elle reste détenue côté examinateur et n'est **jamais** transmise à l'élève. Elle donne la clé exacte sur les mots enseignés après l'enseignement, et HOLD avant ou sur les mots non enseignés. Elle **satisfait les 10 critères** (`test_control_perfect_reference_satisfies_every_acquisition_criterion`). Un échec ici serait un `INVALID_TEST`.
- **Discrimination :** **aucun** des 10 critères n'est satisfait par :
  - les cinq lignes de base ;
  - HOLD partout ;
  - les sept réponses constantes F1 à F7 ;
  - ni l'oracle positionnel.
  
  Une stratégie triviale qui en satisferait un serait un `INVALID_DISCRIMINATION`.
- **Campagne :** une seule campagne en conteneur, dans cet ordre :
  1. X0 ;
  2. enseignement et corrections ;
  3. X1, X1-far et X4 ;
  4. sauvegarde, puis **nouveau conteneur** chargé depuis l'état seul ;
  5. X2 ;
  6. leçons concurrentes ;
  7. X3.

## 4. Témoin « table » (réfutable)

`witness_stable` exige que l'élève ne réponde rien d'autre que HOLD sur le mot **non enseigné** « table », à T0 comme à T1. Ce critère fait partie de `t1_acquisition`.
Le contrôle prouve qu'il peut échouer :
- un gain synthétique sur « table » est détecté ;
- une référence parfaite qui « devinerait » « table » perd T1.

Il ne dépend pas de l'élève sous test.

**Écart assumé (audit NB2) :** la clé privée étiquette « table » en T1 (meuble), mais le critère exige HOLD, car « table » n'est **jamais enseigné** : toute réponse non-HOLD sur ce mot signale une connaissance d'origine extérieure à l'enseignement. Un élève qui répondrait la clé brute, y compris T1 sur « table », perd donc `t1_acquisition` et les critères qui en dépendent ; c'est voulu.

## 5. Résultats (2026-10-22)

**Audit indépendant V0.3 : PASS_WITH_NB.** 12 élèves sans la clé, dont 2 sondes originales de l'auditeur (vote d'ensemble, trigramme à seuil d'abstention) : 0 / 10. Un élève détenant la clé en conteneur et répondant HOLD sur les mots non enseignés : 10 / 10 (faisabilité confirmée hors référence hôte).

**Élève vide de référence :** 22 contrôles verts ; 18 tests rouges (10 d'acquisition, 7 d'interface, 1 invariant B10), tous des `AssertionError` ; aucun conteneur résiduel ; worktree inchangé par le banc.

Sondes de l'auteur, en conteneur (**non indépendantes**) :

| Sonde | RED d'acquisition passés (10) |
|---|---|
| Constant | 0 |
| MajoritySense | 0 |
| Keyword | 0 |
| Trigram | 0 |
| NearestLesson | 0 |
| PositionOracle | 0 |
| OracleImport | 0 |
| OracleDisk | 0 (rien trouvé) |
| OracleIndirect | 0 |

**Tests d'interface mémoire (requalifiés) :** ils ne prouvent pas l'acquisition. Un simple stockage fidèle des leçons passe la récupération par sens, domaine, provenance et contexte (constaté en V0.2 : 3 à 4 tests selon l'élève). C'est assumé.
**Invariant B10 de falsification avec empreinte recalculée :** rouge par conception tant qu'aucune signature n'existe (décision ouverte).

## 6. Limites de l'échantillon

- **Taille :** la campagne reste **technique**.
  - X1, X2 et X4 : 1 item par sens de « force » ;
  - X1-far : 8 items ;
  - X3 : 2 items par sens de « chemin » / « corriger » ;
  - 1 item HOLD par examen, donc l'abstention ne vaut que 0 ou 1.
- **Hasard :** la discrimination est vérifiée contre des stratégies **définies**. Un élève qui réussirait par chance reste possible avec si peu d'items ; aucune conclusion statistique n'est permise.
- **Inventaire :** F1–F7 restent un inventaire provisoire.
- **Campagne scientifique future :** au moins 20 items par sens et par examen. Avant toute campagne confirmatoire, il faudra **figer et pré-enregistrer** :
  - les seuils (`PROVISIONAL`) ;
  - les tests statistiques, par exemple un test binomial exact contre la meilleure ligne de base, avec correction de Holm.

## 7. Capacités de mémoire non démontrées

Aucune n'est démontrée :
- acquisition ;
- rétention après redémarrage ;
- absence d'oubli ;
- transfert ;
- abstention appropriée ;
- provenance ;
- historique révisé ;
- intégrité de l'état de l'élève ;
- authenticité B10.

Le banc décrit **ce qu'il faudrait démontrer**. Aucun GREEN n'est autorisé.

## 8. Hors périmètre

- **Aucune intégration :** pas de raccordement MMonde, Native Memory, Graphiti, frise, 34 arbres, Continuum, ni B8/B10 réels. Le crosswalk reste un document.
- **Aucune modification** de B8, B9, B10, Brody ou SENS.
- **Autorisation :** celle du banc n'est jamais KX108.
- **Intégration partagée :** les six conflits Claude/AGY restent bloquants.
