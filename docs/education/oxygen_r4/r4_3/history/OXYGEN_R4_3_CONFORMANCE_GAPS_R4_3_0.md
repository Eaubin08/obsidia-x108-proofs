# Oxygen R4.3 — écarts de conformité de R4-Core (`c9a3d861`)

Aucun écart n'est réputé non bloquant d'office. Le classement ci-dessous dit, pour chacun, s'il bloque un futur build R4.3.

| # | Écart | Nature | Bloquant pour R4.3 ? | Correction définie | Test de non-régression |
|---|---|---|---|---|---|
| G1 | Marqueurs de négation : « ne … plus » absent ; « ne … pas » coupé sur « pas » au lieu de « ne » | **défaut de code** (K2 R4.2.0) | **oui** : non-conformité contractuelle, même si elle est sans effet sur les corrections réelles | ajouter « ne … plus » et faire commencer le segment négatif au **premier « ne »** suivi de « pas » ou « plus » dans les 4 tokens ; sinon au marqueur seul | **T-NEG-MARK** : « X (L1), ne … pas Y (L2) » et « X (L1), ne … plus Y (L2) » donnent tous deux le contraste (L1, L2) ; un « ne » isolé ne coupe rien |
| G2 | Filtre `len > 2` sur les mots pleins (K5, exemplaires) | **lacune de contrat** (le filtre vient de la convention de V0 et n'est pas dans R4.2) | **oui** : un paramètre caché | **le déclarer dans R4.3** (mots pleins = hors liste fermée de mots-outils **et** longueur ≥ 3), sans le changer, puisqu'il est déjà appliqué et audité | **T-CONTENT** : un mot de 2 lettres hors liste n'est jamais voisin déterminant ni lemme d'exemplaire |
| G3 | `retrieve` n'expose pas `SUSPENDU` (F-A §2) | **défaut de code** | **oui** | chaque entrée de `retrieve` porte `corrections: [{id, statut}]`, statut ∈ {OK, SUSPENDU, CONTESTÉ, MALFORMÉ, NON_RECONNU} | **T-RETRIEVE-STATUS** : après C-4 puis C-X, l'entrée EX-F6 montre C-4 = SUSPENDU et C-X = CONTESTÉ ; avant C-X, C-4 = OK |
| G4 | Journal des réinterprétations (Clôture NB-F) non implémenté | **défaut de code** | **oui** | entrée en ajout seul à chaque mise à jour : {révision, événement déclencheur, changements (correction → ancien statut → nouveau statut), éléments suspendus ou réactivés} ; exposé par une méthode de lecture | **T-JOURNAL** : la séquence C-X avant la leçon F5, puis la leçon F5, produit une entrée NON_RECONNU → CONTESTÉ pour C-X et OK → SUSPENDU pour C-4 ; aucune entrée effacée |
| G5a | T-GLOSE absent | **défaut de test** | **oui** | test : les gloses n'incluent ni étiquettes ni segment « » | T-GLOSE |
| G5b | Valeurs de K4 (n = 0 à 3) non testées | **défaut de test** ; **devient sans objet** si l'option C est adoptée (le rétrécissement passe sur les comptes) | oui sous R4-Core ; remplacé sous C | sous C : **T-BETA** : r = (TP + 1)/(N + 2) pour (0, 0), (2, 2), (1, 3) | T-BETA |
| G5c | Pas de cas par motif K9, en particulier `CONFLIT` | **défaut de test** | **oui** | synthétique : deux classes désignant deux étiquettes différentes avec provenances disjointes → `CONFLIT` ; mot non enseigné → `MOT_INCONNU` ; preuve faible → `PREUVE_INSUFFISANTE` | T-K9-1/2/3 |
| G5d | T-VETO contractuel | **élément désactivé** (K1 en HOLD) | non | déclaré non applicable | — |
| G5e | T-MULTI | **élément désactivé** (aucun synonyme lu) | non | déclaré non applicable | — |

**Synthèse :**
- G1, G3, G4, G5a et G5c sont des **corrections de code ou de tests**, obligatoires avant tout passage du futur build R4.3 ;
- G2 est une **précision contractuelle** à intégrer dans R4.3 ;
- G5b dépend de l'option retenue ;
- G5d et G5e sont non applicables.
