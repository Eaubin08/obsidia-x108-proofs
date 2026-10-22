# Oxygen R4.2 — rapport d'audit des contrats

**Nature :** contre-vérifications **techniques** par des agents distincts de l'auteur, sous le **même compte** Windows. Ce n'est **pas** une indépendance expérimentale complète. Aucun relecteur n'a lu les examens privés. P-ALIGN n'a pas été exécuté. Aucun code d'élève.

| Tour | Version | Verdict | Points |
|---|---|---|---|
| 1 | R4.2.0 | **HOLD** | 5 bloquants : poids 1/k inutilisé (K1) ; fuite possible du leave-one-out de P-ALIGN ; attribution des gloses négatives ; effet de `CONTESTÉ` ; « aucune » dans C_mappée. Faits vérifiés : 15 / 1 / 1 groupes ; 40 paires de groupes de « force » partagent des synonymes. |
| 2 | R4.2.1 | **HOLD** | 4 bloquants levés sur 5 ; restait F-A (contrastes et gloses d'un exercice contesté, dépendance à l'ordre). M-CIBLE : **2** expressions en plusieurs mots, vérifié empiriquement. |
| 3 | R4.2.2 | **PASS_WITH_NB** | F-A levé ; aucune contradiction entre R4.2.0, R4.2.1 et R4.2.2 ; les 5 textes réels sont interprétés de façon déterministe ; état final identique pour C-4 → C-X et C-X → C-4. 4 remarques non bloquantes, intégrées dans la finalisation R4.2.2. |

| 4 | Finalisation R4.2.2 | **PASS_WITH_NB** | recalcul sur 𝓛 courant validé (C-4 → C-X, C-X → C-4, C-X avant la leçon F5 : état identique) ; exclusion d'un exercice contesté cohérente ; plus aucune détection hors 𝓛 sur le fond ; invariants P-LEX, P-ALIGN, K1, K10 et M-CIBLE confirmés (2 expressions vérifiées dans V1). Remarques NB-A à NB-G. |

**Clôture :** les remarques NB-A à NB-G sont intégrées dans la section « Clôture R4.2.2 » de la spécification et dans le registre (D23 à D26). Ces ajouts appliquent les recommandations du tour 4 et **n'ont pas été relus séparément**. Le seul choix substantiel nouveau est D23 (veto conservé), qui suit l'option proposée par le relecteur.

**Contrats :**

| Contrat | Statut |
|---|---|
| K1 | **spécifié** : mécanisme nouveau et porte P-ALIGN |
| K2 | **spécifié** : réouverture de B3 ; reconnaissance limitée à 𝓛 ; `NON_RECONNU` |
| K3 | **spécifié** : provenances disjointes |
| K4 | **spécifié** |
| K5 | **spécifié** |
| K6 | **spécifié** |
| K7 | **spécifié** : redéfinition |
| K8 | **spécifié** : équivalent à la condition 2 |
| K9 | **spécifié** : précédence |
| K10 | **spécifié** : C_mappée, conditionnée à une table externe |
| M-CIBLE | **spécifié** : export V2 requis |

**Risques déclarés :**
- K1 est probablement fragile (40 paires de groupes partagent des synonymes, d'où une exclusivité sévère) ; P-ALIGN peut échouer ;
- la règle des provenances disjointes et le rétrécissement peuvent produire un HOLD massif (H5 en péril) ;
- C_mappée dépend d'un contrôleur humain et reste conservatrice.
