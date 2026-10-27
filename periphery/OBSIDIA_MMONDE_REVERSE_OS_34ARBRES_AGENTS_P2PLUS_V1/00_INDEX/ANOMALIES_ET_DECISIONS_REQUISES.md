# Anomalies et décisions requises

Au cours de la génération du pack, plusieurs anomalies et points
d’incertitude ont été identifiés.  Ces éléments nécessitent une
décision humaine ou une clarification avant de pouvoir finaliser le
pack et le figer.  Cette liste n’est pas exhaustive et pourra être
complétée lors des prochaines itérations.

## Noms des fichiers de la constitution

Bien que les versions accentuées et avec tirets des fichiers O1–O8
aient été supprimées, certains doublons peuvent subsister ou
réapparaître en fonction de l’archivage ou du système de fichiers.
Une décision humaine est requise pour confirmer les noms définitifs
et supprimer définitivement les variantes accentuées ou comportant des
caractères spéciaux.  Les fichiers actuellement conservés sont :

```
O1_NON_ACTION_LEGITIME.md
O2_IRREVERSIBILITE_STRUCTURELLE.md
O3_EPREUVE_TEMPORELLE_X108.md
O4_NON_ARBITRAGE_SOUS_CONFLIT.md
O5_ELIMINATION_DECISIONNELLE.md
O6_MEMOIRE_NEGATIVE.md
O7_AUDITABILITE_NATIVE.md
O8_SEPARATION_COGNITION_ACTION.md
```

## 34 arbres – anomalies de numérotation

La comparaison entre le document « LES 34 ARBRES » et l’image
correspondante révèle des doublons et des numéros manquants.  Un
registre provisoire a été généré dans `04_ARBRES_34_TENSOR_MATRIX`,
mais certaines entrées restent marquées `NEEDS_HUMAN_VALIDATION`.
Les arbres dont le nom ou le numéro est incertain doivent être
examinés avec soin pour éviter les confusions.  Le fichier
`04_ARBRES_34_TENSOR_MATRIX/03_ANOMALIES_ET_DECISIONS.md` détaille
ces incohérences.

## Contenu des fichiers d’arbre

La majorité des fichiers dans les dossiers `ARBRE_XX__...` sont encore
des placeholders : définitions succinctes, règles d’activation vides,
vecteurs tensoriels à zéro, etc.  Une formalisation complète et une
consolidation des données (liaisons, exemples, risques) sont
nécéssaires pour que chaque arbre soit exploitable.

## Registre des agents

Le fichier `10_AGENTS_52/agents_52.registry.json` a été enrichi avec
de nombreux champs supplémentaires.  Cependant, certaines valeurs
restent génériques (comme "NEEDS_HUMAN_VALIDATION" ou des chaînes
vides).  Une revue humaine est indispensable pour renseigner
correctement les attributs de chaque agent : prompt système,
politiques de cloud, délimitation de frontière, etc.

## Extractions de texte et couverture source

La concaténation des documents source dans
`01_SOURCES/extracted_text_all.md` n’a pas encore été exploitée pour
remplir les audits et spécifications.  De même, le rapport de
couverture (`00_INDEX/SOURCE_COVERAGE_REPORT.md`) signale que la
majorité des sources sont encore considérées comme
`PARTIAL_SOURCE`.  Un travail de lecture et d’annotation est requis
pour transformer ces sources en descriptions et algorithmes complets.

