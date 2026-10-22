# Oxygen — spécification du premier pilote d'apprentissage textuel (V0)

**Date :** 2026-10-17 · **Auteur :** Claude · **Statut : SPÉCIFICATION EXPÉRIMENTALE, non canonique.** Aucun code de pilote, aucune mutation mémoire, aucune naissance Oxygen, aucun raccord runtime. Ce document prépare des **tests RED isolés** ; leur écriture exige une autorisation.

Entrées : `OXYGEN_FOUNDER_CLARIFICATION_20261017.md`, `OXYGEN_EDUCATION_PRECONCEPTION_V0.md` (carte corrigée en V0.1).
Étiquettes : **[FV]** vision du fondateur · **[EC]** code existant · **[TE]** preuve de test · **[ER]** résultat expérimental · **[NP]** proposition nouvelle · **[UD]** décision ouverte.

## 0. Hypothèses de travail (V0.1, non canoniques)

| Hypothèse | Conséquence pour le pilote |
|---|---|
| B8 et B10 sont candidats à la réutilisation **en banc d'essai isolé** | aucun import depuis le runtime public ; base B10 temporaire, jetable |
| Brody reste **stateless** (D2) | le pilote ne modifie pas Brody ; l'« élève » est un composant de banc distinct |
| Oxygen reste une **entité future** | le pilote mesure une acquisition locale, pas une continuité d'Oxygen |
| Expérience et leçon ≠ connaissance validée | toute sortie reste candidate tant qu'un humain ne l'a pas attestée |
| **Aucune promotion automatique** | conforme à `MEMORY_PROMOTION_MANUAL_ONLY_V1` |
| Une validation B8 **n'autorise pas** une écriture B10 | B10 exige une autorisation Binder/KX108 (spec B10 §10), implémentée seulement structurellement : en banc isolé, l'autorisation est un **artefact de test explicite**, jamais présenté comme KX108 |
| Rôles séparés | **professeur**, **élève**, **examinateur** sont trois composants distincts, sans partage d'état hors des canaux définis |
| Conflits Claude / AGY | prérequis avant toute intégration partagée, pas avant un banc isolé |

## 1. Question scientifique

> Après un enseignement sur les sens du mot « force », l'élève **choisit-il le bon sens dans des phrases qu'il n'a jamais vues**, **conserve-t-il** ce choix après interruption et après un apprentissage concurrent, **transfère-t-il** à un nouveau registre, et **s'abstient-il** quand le contexte ne permet pas de trancher ?

Hypothèse nulle H0 : aucune différence significative entre T0 et T1–T4 au-delà de ce qu'explique la restitution des phrases d'enseignement.

Le pilote doit pouvoir **réfuter** une acquisition, pas seulement la constater.

## 2. Inventaire des sens

Constat [EC] : le corpus lexical donne pour « force » 17 entrées : **une** définition Littré (force physique d'un être), une glose de traduction, et **15 groupes de synonymes** (thésaurus), dont **~8 distincts** après dédoublonnage (puissance / énergie ; vigueur ; volonté / courage ; résistance / endurance ; pouvoir / autorité ; violence / contrainte ; noblesse / sagesse). **L'inventaire ne peut pas être dérivé automatiquement du corpus.**

Inventaire **provisoire** [NP], à valider par un auteur humain [UD] :

| Id | Sens | Exemple d'enseignement (forme) |
|---|---|---|
| F1 | vigueur physique d'un être | « Il n'a plus la force de marcher. » |
| F2 | énergie morale, courage, volonté | « Elle a trouvé la force de pardonner. » |
| F3 | contrainte, violence | « Ils sont entrés de force. » |
| F4 | puissance d'un groupe, effectif (souvent au pluriel) | « les forces armées », « les forces de l'ordre » |
| F5 | grandeur physique (mécanique) | « une force de 10 newtons » |
| F6 | intensité, degré | « la force du vent », « la force d'un argument » |
| F7 | locutions : « à force de », « de toutes ses forces », « en force » | « À force de répéter, il a compris. » |

Mots de contrôle [NP] : **« chemin »** (concret / figuré), **« corriger »** (rectifier / punir), comme apprentissage concurrent (T3) ; **« table »** comme témoin quasi monosémique (aucun gain attendu). Hachette : **référence privée** de comparaison de l'inventaire, hors dépôt, jamais ingérée ni citée.

## 3. Matériaux, strictement séparés

| Jeu | Usage | Contenu | Interdit |
|---|---|---|---|
| **E — enseignement** | leçons du professeur | définitions, exemples, contre-exemples par sens | servir d'examen |
| **C — correction** | retours du professeur après erreurs | phrases + sens attendu + explication | réutilisé en validation ou examen |
| **V — validation** | décider ACCEPT / HOLD d'une révision | phrases inédites | utilisé en examen ; vu par l'élève avant décision |
| **X0…X4 — examens** | mesures T0–T4 | phrases inédites, jamais montrées avant leur épreuve | servir à décider quoi que ce soit |

Règles : disjonction vérifiée par empreinte de chaque phrase (aucune phrase commune entre jeux) ; le jeu **C** provient uniquement d'erreurs sur des **exercices tirés de E**, jamais de V ni des examens ; le nombre de décisions ACCEPT / HOLD prises sur **V** est **plafonné** et V est **renouvelé** au-delà, pour éviter l'adaptation au jeu de validation ; **examens rédigés par un auteur différent** ou un générateur **différent** de celui des leçons, pour éviter la même distribution (leçon tirée de P155) ; part fixe d'items **ambigus** (HOLD attendu) et de **contre-exemples** (sens trompeur par un mot-indice) dans chaque examen.

## 4. Épreuves

| Épreuve | Moment | Matériel | Ce qu'elle mesure |
|---|---|---|---|
| **T0** | avant tout enseignement | X0 | ligne de base |
| **T1** | après E + C | X1 | acquisition immédiate |
| **T2** | **nouveau processus**, état reconstruit depuis la base B10 seule, sans réinjection de E ni C | X2 | rétention après interruption |
| **T3** | après enseignement concurrent (« chemin », « corriger ») | X3 (items « force » + items concurrents) | résistance à l'oubli, interférence |
| **T4** | nouveau registre (littéraire, technique, oral familier) ou générateur différent | X4 | transfert, généralisation |

Ordre fixe ; T2 exécuté au minimum **dans un processus séparé** ; une variante à **jours différents** est recommandée [UD].

## 5. Mesures

| Mesure | Définition |
|---|---|
| Précision sémantique | sens correct / items où une réponse est attendue |
| Couverture | items répondus / items où une réponse est attendue |
| Abstention appropriée | HOLD sur items ambigus / items ambigus |
| Abstention injustifiée | HOLD sur items non ambigus / items non ambigus |
| Conservation | précision T2 et T3 par rapport à T1, **par sens** (référence figée = T1, pas l'état courant) |
| Erreurs nouvelles | items justes en T(n-1) devenus faux en T(n) |
| Transfert | précision T4 par rapport à T1 |
| Fidélité des explications | l'explication fournie cite le sens choisi et un indice réellement présent dans la phrase (contrôle humain sur échantillon) |
| Provenance | chaque réponse indique quelle leçon / correction / acquis l'a produite ; « aucune » est une valeur valide |

Toutes les mesures sont **rapportées séparément**. Aucun score agrégé n'est présenté comme preuve de compétence générale, de maturité ou de conscience.

## 6. Critères RED / GREEN [NP]

Les tests sont écrits **RED d'abord**, contre un élève vide (aucun acquis). **RED attendus** : acquisition, rétention, résistance à l'oubli, transfert, intégrité (tant qu'aucune signature n'existe) et abstention appropriée. **Pouvant être verts dès le départ** (contrôles) : témoin, isolement, et éventuellement abstention injustifiée. Le test statistique, la taille d'échantillon par sens et les seuils sont **fixés avant l'expérience** [UD] ; « différence significative » se lit au sens de ce test pré-enregistré.

| Critère | GREEN si | Échec scientifique (réfutation) si |
|---|---|---|
| Acquisition | précision T1 − T0 ≥ seuil fixé **avant** l'expérience [UD], sur au moins 5 des 7 sens | gain limité aux phrases proches de E (détecté par un sous-ensemble X1 « éloigné ») |
| Rétention | précision T2 ≥ T1 − tolérance, état reconstruit uniquement depuis B10, en processus séparé | T2 dépend d'un état en mémoire vive ou d'une réinjection |
| Résistance à l'oubli | aucun sens de « force » ne perd plus que la tolérance en T3, par rapport à T1 figé | dégradation cumulée, même petite, sur un sens (leçon P156) |
| Transfert | précision T4 > T0 et ≥ une fraction de T1 fixée d'avance | T4 ≈ T0 |
| Abstention | abstention appropriée ≥ seuil et abstention injustifiée ≤ seuil | l'élève « réussit » en s'abstenant partout, ou ne s'abstient jamais |
| Témoin | aucun gain significatif sur « table » | gain sur le témoin (signe de biais de mesure) |
| Intégrité | la base B10 rejette une révision falsifiée **ou** la falsification est détectée | une falsification avec empreinte recalculée passe inaperçue (leçon G1) — RED attendu tant qu'aucune signature n'existe [UD] |
| Isolement | aucun fichier écrit hors du répertoire du banc ; aucun import par le runtime public | toute écriture hors banc |

## 7. Comportement HOLD

L'élève répond HOLD quand : plusieurs sens restent compatibles avec la phrase ; aucun acquis ne couvre le cas ; une révision est en conflit non tranché ; la provenance de l'acquis n'est pas retrouvée après redémarrage. L'examinateur compte un HOLD juste comme une réussite d'abstention, jamais comme une réponse correcte.

## 8. Journal éducatif candidat (phase D) [NP]

**Compatibilité vérifiée** [EC] : le `MemoryCandidate` existant (`periphery/memory/memory_candidate.py`) ne porte que `candidate_id`, `source_id`, `source_type`, `content_hash`, `content_summary` (200 caractères), `status=CANDIDATE_ONLY`, `memory_write_allowed=False`, `auto_promotion_allowed=False`, `created_at`, `risk_flags`. B8 porte `KnowledgeClaim`, `EvidenceRef`, `VerificationRecord`, `HumanAttestation`, états et temps de validité ; B10 porte l'historique des révisions par slot.

**Proposition :** pas de nouveau registre. Une **entrée de journal** est un document d'enveloppe dont l'empreinte devient le `content_hash` d'un `MemoryCandidate` (statut `CANDIDATE_ONLY`) et qui **référence** les artefacts B8 / B10 par identifiant :

| Champ | Contenu | Référence existante |
|---|---|---|
| `entry_id`, `recorded_at`, `source` | identifiant, date, auteur ou composant | `MemoryCandidate.candidate_id`, `source_id`, `created_at` |
| `situation` | mot, phrase, registre, épreuve (T0–T4) | — |
| `initial_hypothesis` | sens prédit + indices invoqués | — |
| `observation` | sens attendu (après coup), réponse de l'examinateur | — |
| `error_or_contradiction` | type d'erreur, conflit avec un acquis | B8 `GapState`, `ReasonCode` |
| `human_intervention` | auteur, texte de correction | B8 `HumanAttestation` |
| `correction`, `new_hypothesis` | règle révisée | B8 `KnowledgeClaim` (état candidat) |
| `independent_trials` | identifiants d'épreuves et résultats | B8 `VerificationRecord` |
| `competence_status` | valeur réelle de B8 `ClaimState` (`CANDIDATE`, `HELD`, `REJECTED`, `SUPPORTED`, `VERIFIED`, `PROMOTED`, `CONTESTED`, `SUPERSEDED`, `INVALIDATED`, `STALE`) ; « attesté » n'est **pas** un état mais la présence d'une `HumanAttestation` liée | B8 `ClaimState`, `HumanAttestation` |
| `evidence_refs` | liens vers résultats d'épreuves | B8 `EvidenceRef` |
| `revision_history` | révisions successives | B10 historique de slot |

Le journal **ne décide rien**, **ne promeut rien** et n'est jamais lu comme une connaissance vraie.

## 8b. Exigences de récupération (ajout V0.2, d'après `OXYGEN_MEMORY_SEMANTIC_CROSSWALK_V0.md`) [NP]

Après enseignement, l'élève doit pouvoir **retrouver** ses acquis candidats, avec leur provenance :

| Clé | Exigence |
|---|---|
| par **sens** | `retrieve(word, sense)` ne renvoie que des acquis de ce sens |
| par **domaine** | `retrieve(word, domain)` renvoie les sens de ce domaine (ex. physique → F5) |
| par **contexte** | `retrieve(word, context)` classe en tête le sens compatible avec le contexte |
| par **temporalité** | `retrieve(..., as_of_revision=n)` renvoie ce qui était enregistré à la révision *n*, inchangé après une révision ultérieure (axe « révision », distinct de la validité dans le monde) |
| par **provenance** | `retrieve(word, provenance=id)` renvoie les acquis issus de cette leçon ou correction |

**Portée :** ces exigences concernent la récupération locale du pilote. Elles **ne** démontrent **pas** la mémoire multidimensionnelle (34 arbres, nuages de points, graphes, causalité, analogies), la frise du monde humain ni la chronologie éducative globale d'Oxygen (crosswalk §4).

## 9. Décisions réellement nécessaires du fondateur

1. Autoriser l'écriture de **tests RED isolés** du pilote (sans code de production) ; cela tranche **partiellement** la décision ouverte n° 1 de la préconception (réutiliser B8 / B10 en **banc isolé**, sans raccord runtime).
2. Valider (ou faire valider) l'**inventaire des sens** de « force » et désigner les **auteurs** des leçons et des examens.
3. Fixer **avant l'expérience** les seuils et tolérances du §6.
4. Exiger ou non l'**authenticité** de la base (signature) et désigner le propriétaire de la clé.
5. Accepter ou non une épreuve T2 à **jours différents**.

Les choix d'architecture (enveloppe de journal, banc isolé, rôles séparés) sont des propositions et ne nécessitent pas de décision préalable pour être discutés.

STOP avant implémentation.
