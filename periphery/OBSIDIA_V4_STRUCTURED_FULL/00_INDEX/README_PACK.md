# OBSIDIA V4 — Pack structuré complet

## Organisation directe

- `02_BLOCS_17` : 17 fichiers, un par bloc, avec nom réel et pépites.
- `03_PEPITES_161` : 161 fichiers, un par pépite, avec nom réel, statut, bloc, formule/source.
- `04_SPECS_40` : 40 fichiers, un par spec, avec nom réel, statut, contenu source quand isolable.
- `05_MODULES_A1_A24` : 24 fichiers modules A, avec nom réel/protocole/test V4.
- `06_TESTS_T1_T12` : 12 fichiers tests T, avec nom réel/protocole/test V4.
- `07_AGENTS_ET_ROLES` : extraction automatique des agents/rôles trouvés dans les sources.
- `08_PREUVES_LEAN_TLA` : P36/P107/P161 structurés avec fichier Lean + evidence requise.
- `13_ENGINE_GATES` : moteur de gates et contrat d’evidence.

## Limite assumée

Les preuves mathématiques Lean complètes ne sont pas inventées. Les fichiers `.lean` sont des squelettes minimaux à remplacer par preuves réelles dans le repo. Le paquet organise et remplit la matière source, mais ne prétend pas que G1 est ouvert.

## Comptes
- Blocs : 17
- Pépites : 161
- Specs : 40
- Modules A/T : 36
- Agents/rôles détectés : 12


## Ajout V4.1 — regroupements

- `06_GARDIENS_DE_FOND_T1_T12` : relecture correcte des T1–T12 comme gardiens de fond.
- `07_AGENTS_ET_ROLES/AGENTS_CANONIQUES_ET_GARDIENS.md` : agents, rôles et gardiens consolidés.
- `12_EXTENSIONS_R_D/EXTENSIONS_INDEX_CLAIR.md` : extensions clarifiées, avec noms manquants signalés.
- `14_REGROUPEMENTS_COHERENCE` : regroupement transversal bloc + pépites + specs + modules + agents.
- `00_INDEX/AUDIT_COUVERTURE_SOURCES.md` : vérification de couverture des documents source.


## Ajout V4.2 — regroupements physiques complets

Le dossier `14_REGROUPEMENTS_COHERENCE` a été reconstruit.

Chaque groupe possède maintenant son propre dossier, et tous les fichiers liés sont copiés au même niveau dans ce dossier :
- blocs ;
- pépites ;
- specs ;
- modules A ;
- gardiens T ;
- agents/rôles ;
- audits ;
- contrats ;
- preuves ;
- tests ;
- extensions si concernées ;
- moteur de gate.

Les anciens fichiers `AgentRole_00x__...md` issus d’une extraction automatique brute ont été retirés du dossier `07_AGENTS_ET_ROLES`.
La lecture agents propre est dans `AGENTS_CANONIQUES_ET_GARDIENS.md` et `CANONIQUES/`.
