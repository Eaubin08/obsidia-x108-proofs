# Oxygen R4-Core — build expérimental isolé : rapport

**Date :** 2026-10-22 · **Base :** `acbcccfc` (checkpoint P-ALIGN) · **Contrats :** R4.1 + R4.2.2, avec `P_LEX=HOLD` et `P_ALIGN=HOLD` · **Statut :** expérimental, non canonique. Le banc de développement est contaminé : ses résultats ne valent **pas** validation.

## 1. Implémentation

**`tests/education_pilot/student_sandbox/r4_core_student.py`** (`R4CoreStudent`) :

| Aspect | Contenu |
|---|---|
| Dépendances | bibliothèque standard ; extracteur figé de V0 (`features.py`) |
| Lexique | export V1, s'il est monté en lecture seule sur `/extra` (configuration D), sinon formes repliées (configuration B) |
| Usage du lexique | **lemmatisation** et `MOT_INCONNU` uniquement ; aucune liste de synonymes lue |
| État | l'**ensemble** des événements reçus ; tout le dérivé est recalculé à partir de cet ensemble sur 𝓛 courant (statuts K2, `CONTESTÉ`, suspension F-A, veto D23, contrastes) |
| Classes de preuve | constructions et exemplaires (K6) ; contrastes (K6 / K2) |
| Décision | rétrécissement n_L/(n_L+2) (K4) ; concordance avec provenances disjointes (K3) ; précédence `MOT_INCONNU` > `CONFLIT` > `PREUVE_INSUFFISANTE` (K9) |
| Sortie | origines `TRANSFERE` / `CORRIGE` / `ACQUIS_LECON` (K7) |
| Mémoire | `retrieve`, `history`, fichier d'état canonique et `StateIntegrityError`, empreinte de la ressource lexicale vérifiée au rechargement |

**Écart déclaré :** la classe « alignement de la cible » (K1) n'existe pas dans le code (P-ALIGN en HOLD), donc la règle de veto D23 n'a aucun objet actif. Elle reste prise en compte dans les statuts.

**Ajustement fait avant toute mesure de banc :** représentation compacte des formes en mémoire, pour tenir dans les 256 Mo du conteneur (pic : 124 Mo). Il ne change aucune logique.

## 2. Tests unitaires (synthétiques, plus données d'enseignement) : 17 / 17

Ils couvrent :
- état initial, apprentissage, abstention typée, provenance ;
- règle de négation, statuts `NON_RECONNU` / `MALFORMÉ` ;
- contestation et suspension, traces conservées ;
- **T-ORDRE-1 et 2**, **T-ORDRE-3**, **T-ORDRE-REEL** : 24 permutations des vrais événements d'enseignement, un état unique ;
- **exclusion d'une phrase contestée** de toutes les classes (B4 / NB-2). Le test portait d'abord le nom T-VETO, renommé après audit. Le **T-VETO contractuel** (D23, veto d'exclusivité K1) est **non applicable**, puisque K1 est désactivée ;
- `history = retrieve(as_of)` ;
- rechargement identique, altération détectée, changement de ressource détecté ;
- lemmes ambigus conservés ;
- invariants de code : aucun identifiant de sens, aucun import interdit, aucune liste de synonymes, ni `sense_id` ni proximité.

## 3. Banc RED V0.3 (inchangé), en conteneur

| Configuration | Contrôles | Interface | Invariant B10 | Acquisition |
|---|---|---|---|---|
| **D** (avec lemmatisation) | 22 / 22 | 6 / 7 | rouge (attendu) | 0 / 10 |
| **B** (sans corpus) | 22 / 22 | 6 / 7 | rouge (attendu) | 0 / 10 |

Le test d'interface en échec est `tampered_student_state` : sa précondition « nothing stored » n'est pas remplie, parce que l'élève **s'abstient même sur les phrases de ses propres exercices**.

**Mesures agrégées** (une campagne de plus par configuration, déclarée) :

| Exam | B | D | A (V0, rapport GREEN V0) |
|---|---|---|---|
| X0 | 0,00 | 0,00 | 0,00 |
| X1 | 0,00 | 0,00 | 0,57 |
| X1-far | 0,00 | 0,00 | 0,50 |
| X2 | 0,00 | 0,00 | 0,43 |
| X3 | 0,00 | 0,00 | 0,57 |
| X4 | 0,00 | 0,00 | 0,29 |

- B et D : HOLD approprié 1,00 et HOLD injustifié **1,00** partout.
- Motifs, sur 60 questions : `MOT_INCONNU` 11 (mot jamais enseigné ou question posée avant l'enseignement), `PREUVE_INSUFFISANTE` 49. **Aucune réponse.**

## 4. Cause (diagnostic sur l'enseignement seul)

Leave-one-out sur les 18 items de « force » :
- **0 réponse** ;
- **aucun item** n'a une seule classe concordante ;
- la voix rétrécie maximale vaut au plus **0,32** (seuil de concordance τ = 0,5).

**Mécanisme :**
- avec 2 ou 3 exemples par sens, le rétrécissement vaut 0,5 ou 0,6 ;
- il faudrait donc une similarité brute de 1,0 ou d'au moins 0,834 entre des phrases **différentes**, ce que la similarité de Jaccard sur constructions ou lemmes n'atteint pas ;
- même atteinte, la règle des provenances disjointes (K3) exigerait deux exemples distincts.

**Conclusion :** la combinaison **K4 (rétrécissement) + τ = 0,5 + K6 (Jaccard)**, toute pré-enregistrée, est **empiriquement infaisable sur ce matériau d'enseignement**. Ce n'est pas un défaut d'implémentation. Ce risque était déclaré (registre R4.2, NB4). **Aucun seuil n'a été modifié.**

## 5. Comparaisons

| Mesure | Valeur |
|---|---|
| Gain après leçons (B, D) | **nul** (0 → 0) |
| Apport propre de la lemmatisation (D − B) | **0** : comportement identique |
| Rétention | non mesurable (aucune connaissance exprimée) ; le rechargement est exact (tests unitaires) |
| Transfert, corrections | aucune réponse, donc aucune origine `TRANSFERE` ni `CORRIGE` observée |
| Erreurs | 0 erreur assurée, au prix de 100 % d'abstention |
| **C** (corpus seul) | **METRIC_HOLD** : pas de table externe groupe → sens, et P-ALIGN est en HOLD |
| D − C_mappée | METRIC_HOLD |
| D − A | négatif sur l'exactitude, mais les architectures diffèrent et ce n'est pas interprétable comme apprentissage |

## 6. Ce que cela ne démontre pas

Ni acquisition, ni compréhension, ni transfert. La mémoire et les révisions fonctionnent (6 tests d'interface sur 7, 17 tests unitaires), mais **stocker des leçons n'est pas les comprendre**.

## 7. Audit technique indépendant : **PASS_WITH_NB**

- Le code est conforme aux contrats et aux HOLD.
- Le diagnostic est **confirmé par un recalcul indépendant** : la voix rétrécie maximale vaut 0,269 et la similarité brute maximale 0,538, alors qu'il faudrait au moins 0,834. **L'infaisabilité vient du contrat, pas du code.**
- Des mutants sur l'ordre et sur la contestation sont tués par T-ORDRE-3, T-ORDRE-REEL et le test d'exclusion.

**Écarts de conformité déclarés.** Le code de l'élève **n'est pas modifié** après observation du banc ; ces écarts restent ouverts :

| # | Écart |
|---|---|
| NB1 | marqueurs de négation : « ne … plus » absent ; la coupure de « ne … pas » se fait sur « pas » (sans effet sur les corrections réelles, qui ne contiennent pas « ne ») |
| NB2 | filtre `len > 2` sur les mots pleins (convention de V0) appliqué en K5 et pour les exemplaires, hors contrat |
| NB3 | `retrieve` n'expose pas le statut `SUSPENDU` des corrections (seulement visible dans `derived_snapshot`) ; le **journal des réinterprétations** (Clôture NB-F) n'est **pas implémenté** |
| NB4 | T-VETO renommé ; le T-VETO contractuel est déclaré non applicable |
| NB5 | tests obligatoires absents : T-GLOSE ; valeurs de K4 pour n = 0 à 3 ; un cas par motif K9 (dont `CONFLIT`). T-MULTI est non applicable (aucun synonyme lu) |

Toute correction de NB1 à NB3 relèverait d'une nouvelle itération de build, à évaluer comme telle.
