# Oxygen R4.4 — Protocole de pré-enregistrement V1

**Statut :** PRE_REGISTERED  
**Date de pré-enregistrement :** 2026-10-23  
**Commit de référence (base) :** `35be12da` — fix(oxygen): restore R4-Core contract conformance G1-G4 and tests  
**Branche :** feat/claude-linguistic-repair-m42-v0  
**Auteur :** Etienne Aubin  
**Contraintes actives :** R4_4_BUILD=NO / BLIND_WITNESSES_GENERATION=NO / PUSH=0 / MERGE=0 / P_ALIGN=HOLD / CALIBRATION_TUNING=NO / PRIVATE_RED_ACCESS=NO

---

## 0. Objet et portée

Ce document est le pré-enregistrement obligatoire du protocole expérimental R4.4.
Il doit être commité et horodaté **avant** tout build R4.4, toute génération de
témoins aveugles, et toute mesure sur les données d'enseignement.

Toute modification ultérieure à ce document est interdite. Un addendum versionné
peut être ajouté sous `## ADDENDUM` avec date et raison.

**Ce document ne génère pas de témoins, ne déclenche aucun build, ne modifie aucun paramètre.**

---

## 1. Manifeste des sources — empreintes SHA-256

Les documents suivants ont fondé la conception de R4.4.
Chemin workbench : `OBSIDIA_R&D/11_Travail_En_Cours/Workbench_Jarvis/`

| Document | SHA-256 | Octets |
|---|---|---|
| R4_4_SPEC_DRAFT.md | `8354f404123ee8b7bdeaab6fe290f647cf108760541b95ca84df56e25ebb89dd` | 5 472 |
| R4_4_EVIDENCE_AND_CALIBRATION_CONTRACT.md | `a0095c225a5b41f377482a4f96c77190c66921fa1f867ef7cf0a073ccb228ebf` | 6 138 |
| R4_4_CONFORMANCE_PLAN.md | `415db48531b76e6bcf63caf0d5b81d24e411b70d4ca34df4d76912b6556bac20` | 5 760 |
| R4_4_VALIDATION_BOUNDARIES.md | `62ea7718b6fc67f8714b55c99753800b44fc80d1de6ceec618a502a330cacd08` | 5 972 |
| R4_4_C6_P5_RESOLUTION_PROPOSAL.md | `36f05605b930ada502a519f47d71e41104b3b166eeeab69c254056d13812c089` | 29 113 |
| R4_4_CONTRACT_GAPS_CLOSURE.md | `ee7d9d114051c0a1cadca053dd2aaef5b68185c3f6a9db70cb4614e00a991120` | 25 484 |
| R4_4_C1_FINAL_ARBITRATION.md | `649faff189020a7529bad0d6a16f5786ee9c2997ec36c19956c7e0146ac9f69b` | 13 541 |

---

## 2. Configurations expérimentales

| Config | Nom | Lemmatisation | Statut | Prérequis |
|---|---|---|---|---|
| **A** | R4-Core historique | non | ACTIVE (référence) | — |
| **B** | R4-Core post-G1-G4 (HEAD 35be12da) | non | ACTIVE | G1–G4 corrigés ✓ |
| **C** | R4.4 DEV — P5-L2 | non | HOLD | curriculum V0.4 (CV_DISJ_RED=PASS) + témoins aveugles |
| **D** | R4.4 CONTROLLED | oui | HOLD_INDEPENDENCE | A+B+C validés + relecteur indépendant |

### Config A — R4-Core historique

- Commit de référence : f4c64f05 et antérieurs
- Rôle : ligne de base non modifiable
- Résultat connu : couverture ≈ 0 sur V0 (2–3 exemples/sens)
- Tests associés : suite originale avant corrections G1–G4

### Config B — R4-Core post-conformité (active)

- Commit : **35be12da** (base de ce pré-enregistrement)
- Corrections intégrées :
  - G1 : ne…pas / ne…plus coupés à « ne » (pas au marqueur)
  - G2 : longueur ≥ 3 contractualisée (non paramètre de réglage)
  - G3 : `retrieve` expose statut SUSPENDU dans les corrections
  - G4 : journal des réinterprétations (ajout seul, rien effacé)
- Tests : 27/27 PASS à la date du pré-enregistrement
- Aucune nouvelle logique d'inférence vs A

### Config C — R4.4 DEV P5-L2 (HOLD)

Dépendances bloquantes :

- Curriculum V0.4 accepté : CV_DISJ_RED=PASS
  (actuellement FAIL sur v1.2.1 — recoupements lexicaux détectés)
- Témoins synthétiques aveugles : non générés (BLIND_WITNESSES_GENERATION=NO)
- P-CAL sur V0.4 : non mesuré
- CURRICULUM_V121 : DEV_EXPLORATORY_ONLY (non accepté pour DEV complet)

Cette configuration n'est pas déclenchée dans cette session.

### Config D — Controlled (HOLD_INDEPENDENCE)

- Ajoute lemmatisation et relecteur indépendant n'ayant pas participé à R4.3
- Dépend de C validé + curriculum séparé
- Hors scope de ce pré-enregistrement

---

## 3. Contrats R4.4 — état à la date du pré-enregistrement

### 3.1 Principes P1–P5 (décision fondateur)

| Principe | Énoncé résumé | Statut |
|---|---|---|
| **P1** | Aucune réponse fondée sur une unique classe non corroborée | DÉFINI |
| **P2** | Validation préalable des classes (N_c ≥ 1, LOO ≥ 1) | DÉFINI |
| **P3** | Trait discriminant ssi F(t,e) ≥ 2 ; seuil fixe non réglable | DÉFINI |
| **P4** | Hors domaine → PREUVE_INSUFFISANTE ; pas de règle compensatoire | DÉFINI |
| **P5** | Répondre quand ≥ 2 classes validées convergent sans contre-preuve | DÉFINI |

### 3.2 Corroboration P5-L2 (DEV_EXPLORATORY_ONLY)

Condition : deux classes C_i et C_j satisfaisant simultanément :

1. étiquette(C_i) = étiquette(C_j) = e
2. Dispositif(C_i) ≠ Dispositif(C_j) : SYNTAXIQUE vs LEXICAL (séparation par dispositif)
3. argmax_item(C_i) ≠ argmax_item(C_j) : items Jaccard distincts (séparation d'événement)
4. N_c(C_i) ≥ 1 ∧ TP_c(C_i) ≥ 1 (P2)
5. N_c(C_j) ≥ 1 ∧ TP_c(C_j) ≥ 1 (P2)
6. Aucune contre-preuve : ¬∃ t, F(t,¬e) ≥ 2 ∧ t ∈ contexte(m) (C2)
7. F(t,e) ≥ 2 pour tous les traits contributeurs (P3)

Code retour : CORROBORATION_NIVEAU_2
Classe : DEV_EXPLORATORY_ONLY

**Résolution §C.6 :** constructions et exemplaires partagent les mêmes items
d'enseignement → K3 (provenances disjointes) n'est jamais satisfiable entre eux
sans K1 actif. P5-L2 résout cela par dispositif + événement au lieu de K3.

### 3.3 Corroboration P5-L3 (HOLD)

K3 strict (provenances réellement disjointes) + K1 actif (P-ALIGN passé).
Code retour : CORROBORATION_NIVEAU_3 / CONTROLLED-EVALUATION
**Statut :** HOLD — P-ALIGN=HOLD, K1 jamais exécuté

### 3.4 Définitions formelles N_c / TP_c

Pour une classe c et un ensemble d'enseignement de taille M :

- **LOO-CAL** : M itérations leave-one-out, item i retiré → M' = M - 1
  - C1 et P3 recalculés sur M' (pas globalement) pour éviter la fuite
- **N_c** = nombre d'itérations LOO où la classe c est non muette
  (exclut : aucun trait P3 actif, items CONTESTÉ ou SUSPENDU exclus)
- **TP_c** = nombre d'itérations LOO où l'étiquette prédite = étiquette correcte
- N_c = 0 → r_c = 1/2 (a priori Beta(1,1)) → P2 bloque
- Estimateur : r_c = (TP_c + 1) / (N_c + 2) [Option C, Beta(1,1)]

### 3.5 Double LOO — séparation stricte

| Protocole | But | Statut |
|---|---|---|
| **LOO-CAL** | Estimer r_c par classe ; porte P2 | ACTIF |
| **LOO-ALIGN** | Porte K1 (P-ALIGN) ; alignement exemplaires | HOLD |

Ces deux protocoles ne se composent pas. LOO-ALIGN ne contribue pas à N_c/TP_c.

### 3.6 Filtre C1 — décision fondateur

- **Seuil :** F > M/2 (strict ; F = M/2 exactement → trait CONSERVÉ)
- **Périmètre :** traits LEXICAUX uniquement
- **Constructions (POS/NG/DET/SURF) :** C1 non appliqué automatiquement ; filtrées par P3 seul
- **Corpus petit M ≤ 1 :** C1 bypassé (BYPASS_IF_M_LE_1)
- **LOO :** C1 et P3 recalculés localement sur M' = M-1 à chaque itération

Divergences par rapport à l'Option C historique :

- **D1** (catégorie B) : seuil F > M/2 (strict) vs F ≥ M/2 (historique)
  — cas limite F = M/2 : trait conservé sous décision fondateur, exclu sous historique
- **D2** (catégorie B) : périmètre lexical seulement vs constructions incluses (historique)
  — les constructions sont traitées par P3, non par C1

### 3.7 Filtre P3 — relation avec C1

Ordre d'application :

1. **C1** : F > M/2 sur traits lexicaux → supprime les traits fréquents non discriminants
2. **P3** : F(t,e) ≥ 2 sur label e → retient les traits répétés par classe

C1 est global (tous labels confondus) ; P3 est par label.
Les traits constructions passent directement à P3.

### 3.8 RAPPEL

Définition exacte :

- Séquence de tokens identique à une leçon active (non CONTESTÉE, non SUSPENDUE)
- Identité après : suppression de la ponctuation finale + pliage accent + minuscules
  + normalisation espaces
- Code retour : RAPPEL, priorité absolue sur P1–P5
- Non contributoire à N_c / TP_c
- Exclu des métriques de couverture et précision

---

## 4. Critères de mesure — porte P-CAL

Les seuils P-CAL sont inchangés par rapport à R4.3. Ils sont déclarés ici
avant toute mesure et ne peuvent être modifiés sans invalider la mesure (STOP_TUNE).

| Critère | Seuil | Modifiable ? |
|---|---|---|
| Couverture | ≥ 0,20 (≥ 4 réponses sur 20 items minimum) | NON |
| Précision | ≥ 0,60 | NON |
| Témoins négatifs synthétiques | Aucun violé (0 réponse sur cas NEG) | NON |

**Si P-CAL échoue :** STOP_PCAL → révision du curriculum, pas révision des seuils.

**Prérequis P-CAL pour config C :**
- Curriculum V0.4 accepté (CV_DISJ_RED=PASS)
- Témoins synthétiques aveugles figés par SHA-256 avant la mesure
- Relecteur des témoins n'ayant pas vu R4.3

---

## 5. Prévisions falsifiables

Les hypothèses suivantes sont déclarées avant toute mesure. Elles sont
testables et réfutables par les données.

### H0 — Couverture nulle sur V0

**Prévision :** Config B (R4-Core post-G1-G4) sur corpus V0 (2–3 exemples/sens)
→ couverture ≈ 0 (aucune réponse hors RAPPEL)
**Raison :** P1 + P2 + P3 avec corpus aussi pauvre → aucune corroboration multi-classe possible
**Réfutation :** si couverture > 0 sur V0, vérifier si items déclenchés sont des RAPPEL ou
si le contrat P2 est mal implémenté

### H1 — Couverture positive sur V0.4 accepté

**Prévision :** Config C sur curriculum V0.4 (CV_DISJ_RED=PASS)
→ couverture > 0,20 (seuil P-CAL)
**Condition :** curriculum doit avoir ≥ 5 exemples/sens diversifiés
**Réfutation :** si P-CAL échoue → révision curriculum (STOP_PCAL), pas des seuils

### H2 — Précision conforme

**Prévision :** quand une réponse est émise en Config C
→ précision ≥ 0,60
**Réfutation :** si précision < 0,60 sur le jeu de mesure → STOP_PCAL

### H3 — Témoins négatifs absents de réponse

**Prévision :** tous les témoins synthétiques négatifs (NEG-UNREL, NEG-MIX-BAL,
NEG-MIX-UNBAL, ADV-3-like, T-MONO-CLASS, T-PROVENANCE)
→ HOLD systématique (aucune réponse)
**Réfutation :** si une réponse est émise sur un témoin négatif → STOP_NEG, build interrompu

### H4 — Stabilité RAPPEL

**Prévision :** tout item RAPPEL (phrase identique à leçon active)
→ code RAPPEL, non contributoire aux métriques
**Réfutation :** si un RAPPEL est traité comme inférence normale → défaut K9/P1

---

## 6. Familles de témoins et frontières

Tous les témoins listés ici doivent être écrits **avant** toute exécution R4.4,
par un relecteur n'ayant pas participé à R4.3, et figés par SHA-256.

**Statut actuel :** BLIND_WITNESSES_GENERATION=NO (non générés)

| Famille | Description | Résultat attendu | Règle si violé |
|---|---|---|---|
| **T-POS-COR** | ≥ 2 classes validées, dispositifs différents, argmax distincts, même étiquette | Réponse correcte (P5-L2) | règle trop restrictive si HOLD |
| **T-NEG-UNREL** | Mot sans lien sémantique avec l'enseignement | HOLD (MOT_INCONNU ou PREUVE_INSUFFISANTE) | STOP_NEG si réponse |
| **T-NEG-MIX-BAL** | Items mélangés équilibrés entre 2 sens | HOLD (P1 ou CONFLIT) | STOP_NEG si réponse |
| **T-NEG-MIX-UNBAL** | Items mélangés déséquilibrés (1 sens dominant) | HOLD | STOP_NEG si réponse |
| **T-ADV3-LIKE** | Trait présent dans 1 seul exemplaire (F=1 < 2) | HOLD (P3 bloque) | STOP_NEG si réponse |
| **T-MONO-CLASS** | Un seul sens enseigné, une seule classe validée | HOLD (P1 : voie mono-classe interdite) | STOP_NEG si réponse |
| **T-PROVENANCE** | Deux classes à exemplaires chevauchants (K3 violé) | HOLD (P5 non satisfait) | STOP_NEG si réponse |
| **T-RAPPEL** | Phrase identique à une leçon active | Code RAPPEL, exclu des métriques | STOP_NEG si étiqueté comme inférence |
| **T-CONTRA** | Exercice contesté (CONTESTÉ) | N_c ne compte pas cet item | défaut LOO-CAL si compté |
| **T-SUSPENDU** | Correction suspendue | Visible dans retrieve, non-contributoire | défaut G3 si absent |
| **T-NEG-MARK** | Négations ne…pas et ne…plus | Coupure à « ne » (G1) | défaut G1 si coupure tardive |
| **T-K9-1** | CONFLIT (deux classes validées, étiquettes différentes) | CONFLIT | défaut K9 |
| **T-K9-2** | MOT_INCONNU | MOT_INCONNU | défaut K9 |
| **T-K9-3** | PREUVE_INSUFFISANTE | PREUVE_INSUFFISANTE | défaut K9 |
| **T-BETA** | Estimateur r_c = (TP+1)/(N+2) pour (0,0),(2,2),(1,3) | 0.5 / 0.75 / 0.4 | défaut K4 |
| **T-SMALL-N** | Corpus M ≤ 1 pour classe c | C1 bypassé | défaut C1 bypass |
| **T-RAPPEL-REPEAT** | Même phrase rappelée deux fois | RAPPEL aux deux occurrences | défaut si inférence la 2e fois |
| **T-NO-CORPUS** | Classe sans aucune leçon active | N_c = 0, r_c = 0.5, P2 bloque | défaut P2 si réponse |

### 6.1 Contraintes de rédaction des témoins

- Les phrases de tests ne répètent jamais une phrase de leçon
- Le mot cible dans les témoins synthétiques est inventé (ex. « zorp », ou terme R4.4)
- L'empreinte SHA-256 de chaque fichier de tests est enregistrée avant la première exécution
- Le relecteur des témoins n'a pas vu les examens RED V0.3 / V0.4

### 6.2 Témoins consommés — interdits pour valider R4.4

| Témoin | SHA (partiel) | Raison |
|---|---|---|
| Témoins R4.3.1 | c3626447… | Utilisés pour développer R4.3 ; CONSOMMÉS |
| Témoins R4.3.2 | a4b0c28d… | Utilisés pour critiquer R4.3 ; CONSOMMÉS |
| RED V0.3 | — | Opérateur a vu les données ; EXPLORATOIRE CONTAMINÉ |
| V0.4-DEV v1.2.1 | — | CV_DISJ_RED=FAIL ; DEV_EXPLORATORY_ONLY |

---

## 7. Règles d'arrêt (stop rules)

### STOP_NEG

Déclencheur : un témoin négatif synthétique produit une réponse étiquetée
(non HOLD, non RAPPEL, non MOT_INCONNU, non PREUVE_INSUFFISANTE, non CONFLIT).

Conséquence : la règle est réfutée sur ce cas. Build interrompu immédiatement.
Aucune mesure de couverture/précision valide.

### STOP_TUNE

Déclencheur : un paramètre (seuil P-CAL, seuil P3, formule estimateur)
est modifié après observation d'un score sur les données d'enseignement ou le RED.

Conséquence : la mesure associée est invalidée. Toute révision doit être
documentée et relue avant tout nouveau build.

### STOP_PCAL

Déclencheur : P-CAL échoue sur le curriculum V0.4 accepté
(couverture < 0,20 ou précision < 0,60).

Conséquence : révision du curriculum, pas révision des seuils.
Retour à la révision du curriculum (STOP_CURRICULUM).

### STOP_CORROBORATION

Déclencheur : deux classes validées désignent la même étiquette mais un biais
commun est détecté (même registre, même auteur, même domaine).

Conséquence : corroboration déclarée superficielle. La réponse n'est pas émise.

### STOP_INDEPENDENCE

Déclencheur : le relecteur des témoins synthétiques a eu accès aux témoins R4.3
ou aux examens RED.

Conséquence : les témoins sont contaminés. Ils doivent être réécrits par
une personne différente.

---

## 8. Dépendances et état des prérequis

| Dépendance | Statut au pré-enregistrement | Bloquante pour |
|---|---|---|
| G1–G4 corrigés dans r4_core_student.py | DONE (HEAD 35be12da) | Config B |
| G5 tests de conformité (27/27 PASS) | DONE | Config B |
| Curriculum V0.4 accepté (CV_DISJ_RED=PASS) | HOLD — v1.2.1 FAIL | Config C |
| Témoins synthétiques aveugles R4.4 | NOT_CREATED | Config C |
| P-CAL sur V0.4 | NOT_MEASURED | Config C |
| P_ALIGN / LOO-ALIGN / K1 | HOLD | Config C (P5-L2 partiel) + Config D |
| Relecteur indépendant R4.4 | NOT_ASSIGNED | Config D |
| Corpus prospectif indépendant | NOT_CREATED | Config D |

### 8.1 Conditions d'autorisation du build R4.4

Le build R4.4 (Config C) est autorisé quand **toutes** les conditions suivantes
sont réunies :

1. Ce pré-enregistrement est commité et horodaté
2. Curriculum V0.4 accepté : CV_DISJ_RED=PASS
3. Témoins synthétiques aveugles figés par SHA-256
4. Contrats de réfutation CR-1 à CR-5 publiés
5. Seuils P-CAL déclarés (inchangés)
6. Prévision de couverture déclarée avant mesure (voir §5)

Ces conditions sont cumulatives. Aucune n'est négociable.

---

## 9. État R4-Core à la date du pré-enregistrement

### 9.1 Fichiers modifiés (conformité G1–G4)

| Fichier | Nature de la modification |
|---|---|
| `tests/education_pilot/student_sandbox/r4_core_student.py` | G1 (ne…pas/plus), G2 (len≥3), G3 (SUSPENDU), G4 (journal) |
| `tests/education_pilot/test_r4_core_student_unit.py` | G5 tests + correction assertion G3 |

### 9.2 Détail des corrections

**G1 — Marqueurs de négation :**
```python
for i, tok in enumerate(t):
    if tok == 'ne' and any(x in ('pas', 'plus') for x in t[i + 1:i + 5]):
        cut = min(cut, i)
```

**G2 — Déclaration contractuelle longueur ≥ 3 :**
```python
# G2 (K5 / R4.2): content word = not a function word AND length >= 3
```

**G3 — Exposition statut SUSPENDU dans retrieve :**
```python
'corrections': [{'id': cid, 'status': R4CoreStudent._eff_status(d['parsed'][cid])}
                for cid in sorted(...)]
```

**G4 — Journal des réinterprétations (ajout seul) :**
Méthode `reinterpretation_journal()` dérivée des événements. Rien effacé.

### 9.3 Suite de tests

| Test | Famille | Statut |
|---|---|---|
| test_t_neg_mark_ne_pas_cuts_at_ne | T-NEG-MARK | PASS |
| test_t_neg_mark_ne_plus_cuts_at_ne | T-NEG-MARK | PASS |
| test_t_neg_mark_isolated_ne_does_not_cut | T-NEG-MARK | PASS |
| test_t_retrieve_status_corrections_expose_suspendu | T-RETRIEVE-STATUS | PASS |
| test_t_retrieve_status_before_contest_k1_is_ok | T-RETRIEVE-STATUS | PASS |
| test_t_journal_records_status_transitions | T-JOURNAL | PASS |
| test_t_journal_entries_are_never_erased | T-JOURNAL | PASS |
| test_t_glose_excludes_labels_and_cue_segment | T-GLOSE | PASS |
| test_t_k9_2_mot_inconnu | T-K9 | PASS |
| test_t_k9_3_preuve_insuffisante | T-K9 | PASS |
| (17 tests hérités) | divers | PASS |
| **TOTAL** | | **27/27 PASS** |

---

## 10. Limitations et qualifications

Ce document est une conception expérimentale.

### 10.1 Ce que ce pré-enregistrement ne garantit pas

- Le cloisonnement avec R4.3 n'est pas encore démontré
- L'indépendance du relecteur des témoins n'est pas vérifiée
- La qualification PREUVE passe à CONCEPTION_EXPERIMENTALE
  jusqu'à démonstration du cloisonnement

### 10.2 Statuts interdits à ce stade

- CURRICULUM_V121 = DEV_EXPLORATORY_ONLY (pas DEV complet)
- CV_DISJ_RED = FAIL (curriculum rejeté)
- INDEPENDENT_VALIDATION = NO
- P_ALIGN = HOLD
- BLIND_WITNESSES = NOT_CREATED
- R4_4_BUILD = NO

### 10.3 Contaminations déclarées

| Source | Type de contamination | Impact |
|---|---|---|
| RED V0.3 | opérateur a vu les données | ne peut pas valider R4.4 |
| V0.4-DEV v1.2.1 | curriculum vu par l'auteur ; CV_DISJ_RED=FAIL | DEV_EXPLORATORY_ONLY |
| Témoins R4.3.1/R4.3.2 | utilisés pour développer R4.3 | CONSOMMÉS |
| Données V0 enseignement | publiques dans le dépôt | autorisées (développement) |

---

## 11. Historique des révisions de ce document

| Version | Date | Auteur | Nature |
|---|---|---|---|
| V1 | 2026-10-23 | Etienne Aubin | Création initiale avant premier build R4.4 |

---

*Ce document est figé à la date de commit. Toute modification ultérieure doit*
*être documentée sous `## ADDENDUM` avec date, raison et signature.*

*Pré-enregistrement obligatoire — R4.4 Oxygen / Obsidia X-108 governance kernel.*
