# Oxygen — préconception de l'éducation textuelle et cognitive (V0)

**Date :** 2026-10-17 · **Auteur :** Claude, worktree `obsidia-claude-linguistique`, branche `feat/claude-linguistic-repair-m42-v0`.
**Statut : PRÉCONCEPTION — non canonique.** Aucun contrat à brancher, aucune naissance effective, aucune mutation mémoire, aucune implémentation. Toute architecture canonique exige une décision explicite du fondateur.

Entrées : `OXYGEN_FOUNDER_CLARIFICATION_20261017.md` (orientation du fondateur) ; `EDUCATION_GENESIS_FORENSIC_PARTIAL_20261017.md` v3 (histoire, statut PARTIAL).

Étiquettes : **[FV]** FOUNDERS_VISION · **[AF]** ASSISTANT_FORMALIZATION · **[EC]** EXISTING_CODE · **[TE]** TEST_EVIDENCE · **[ER]** EXPERIMENTAL_RESULT · **[NP]** NEW_PROPOSAL · **[UD]** UNRESOLVED_DECISION.

Invariants transversaux (non négociables dans tout ce document) : **KX108_ONLY** pour toute autorité ; l'éducation ne crée **aucun** droit d'action ; aucune promotion mémoire automatique (`MEMORY_PROMOTION_MANUAL_ONLY_V1`) ; un score n'est ni une compétence, ni une maturité, ni une conscience.

---

## A. Carte de l'organisme éducatif

Statuts : **BRANCHÉ** = importé par le chemin public `apps/obsidia_api/routes/brody.py` (y compris import paresseux) ; **HORS CHEMIN BRODY** = importé par une autre route API seulement ; **ISOLÉ** = code et tests présents, aucun import runtime ; **PROTOTYPE** = laboratoire hors dépôt principal ; **DOC** = concept documentaire seulement.

| Composant | Emplacement (code identique à `b859d5bf` et `48b650f8`, sauf mention) | Statut | Rôle éducatif possible | Étiquette |
|---|---|---|---|---|
| SENS / treillis sémantique | `app/semantic/lattice/` (scellé) via `app/harness/state_explicit/sens_adapter` | BRANCHÉ | représentation du sens d'un énoncé ; ~55 verbes, français seul | [EC] |
| Corpus lexical FR/EN | `periphery/language/lexical_corpus.py`, `native_realization.py` | BRANCHÉ (provenance publique fermée à `4016db99`) | vocabulaire, définitions, synonymes, gloses, polysémie | [EC][TE] |
| OS Trad | `periphery/language/language_router.py` | BRANCHÉ (import dynamique de `detect_language` et `has_authority_claim` via `apps/obsidia_api/runtime_loader.py` L38–L39, chargé par `routes/brody.py` L38) ; aussi routes `os_trad_ir_reverse.py`, `periphery_ops.py` | détection de langue, signal de revendication d'autorité ; traduction / normalisation | [EC] |
| Brody (organe d'intégration) | `apps/obsidia_api/brody_*` (≈ 50 adaptateurs importés) | BRANCHÉ | contexte, réponse, enseignant/élève textuel | [EC] |
| B7 cognition (détection d'inconnues) | `app/cognition/b7/` | BRANCHÉ (findings sentinel historiques) | marquer ce qui n'est pas résolu → HOLD | [EC][TE] |
| B9 chemin cognitif | `app/cognition/b9/contracts.py` | ISOLÉ | tracer le chemin d'un raisonnement | [EC] |
| B8 promotion de connaissance | `app/knowledge/b8/` (affirmation, preuve, vérification, attestation humaine, états, porte T1–T12) | ISOLÉ, sans persistance | **acquis validé** : passer de candidat à connaissance par une porte typée | [EC][TE] |
| B10 mémoire durable | `app/knowledge/b10/persistence.py` (SQLite, historique de révisions par slot, `recover_after_restart`, chaîne d'autorisation d'écriture, empreinte sha256 sans signature) | ISOLÉ | **conservation** et **reprise après interruption** des acquis | [EC][TE] |
| M41 modèle du monde | `app/world_model/` | BRANCHÉ (import paresseux conditionnel, `routes/brody.py` L966, ombre B7/M41), transitoire, non souverain | hypothèses sur le monde, non souveraines | [EC] |
| Native Memory | `apps/obsidia_api/brody_obsidia_native_memory.py`, index V1 | BRANCHÉ, lecture seule, statique | contexte de projet ; **pas** d'écriture d'expérience | [EC] |
| Mémoire de session | `brody_session_memory_adapter.py` + ledger `_local_audits/brody_sessions` | BRANCHÉ | continuité de conversation (pas d'acquis) | [EC] |
| Ledger de candidats | `periphery/memory/memory_candidate_ledger.py` | HORS CHEMIN BRODY (route `apps/obsidia_api/routes/x108.py`) | mémoire candidate append-only | [EC][TE] |
| Construction de candidats mémoire | `periphery/memory/memory_candidate.py` (`build_memory_candidate_v2`) | BRANCHÉ (import dynamique via `runtime_loader.py`) | forme d'un candidat mémoire | [EC] |
| Politique de promotion mémoire | `periphery/memory/memory_promotion_policy.py` (`evaluate_promotion_policy`) | BRANCHÉ (import dynamique via `runtime_loader.py`) | évaluation de promotion (sans écriture) | [EC] |
| Leçons candidates | `brody_memory_education_packet.py` | BRANCHÉ (lecture) | candidat → leçon typée (8 types) | [EC][TE] |
| Garde de promotion mémoire | `brody_memory_promotion_guard.py` | BRANCHÉ | interdit la promotion implicite | [EC] |
| Pack éducatif V1 | `brody_education_pack_v1_readonly_adapter.py` | BRANCHÉ mais `PACK_MISSING` localement | contexte éducatif figé | [EC] |
| Score éducatif | `periphery/education/education_score.py` | HORS CHEMIN BRODY (`routes/periphery_ops.py`) | indicateur, **pas** une preuve | [EC] |
| AVDR | `periphery/avdr.py` | HORS CHEMIN BRODY (`routes/periphery_ops.py`) | boucle Analyse → Validation → Diffusion → Réciprocité | [EC][AF] |
| ARM (M33) | `docs/architecture/M33_ARM_*` | DOC | reconstruction | [AF] |
| FSO | Drive (doc 01) | DOC | cadre scolaire (cours, exercices, évaluation) | [FV] vision / [AF] formalisation |
| Agents spécialisés / versions 9×9 | Drive (docs 02, 05) | DOC | exploration de compétences ; **pas** d'identités | [FV][AF] |
| World Foundry | Drive (docs 03, 04) ; **aucun code dans ce dépôt** | DOC | environnement d'épreuves | [AF] |
| Brody World Physique | `brody-world-physique` `exp/p2…` `966df622` | PROTOTYPE | porte de rétention P155, rejeu P156, mémoire scellée G1 | [ER] |
| GuardX108 / KX108 | `scripts/kernel/kx108_*`, preuves Lean | autorité (hors éducation) | frontière : aucune action issue de l'éducation | [EC] |

**Constat :** le noyau d'un apprentissage gouverné existe (candidat → B8 → B10), mais il n'est **pas raccordé** entre ses parties ni au chemin public. Un premier cycle exige des **raccords**, un **protocole**, et quelques **composants nouveaux limités** (section G : générateur d'items et d'examens disjoints, exécution en processus séparés, signature si l'authenticité est exigée).

---

## B. Premier cycle d'éducation textuelle [NP]

Chaque étape : entrée → sortie, provenance, critère de succès, comportement HOLD.

| # | Étape | Entrée | Sortie | Provenance | Succès | HOLD si |
|---|---|---|---|---|---|---|
| 1 | Enseignement initial | leçon humaine (concept, sens, exemples, contre-exemples) | leçon enregistrée comme **source** | auteur, date, version | leçon complète et sourcée | source absente ou contradictoire |
| 2 | Représentation du sens | énoncés de la leçon | cadres SENS + sens lexicaux | SENS, corpus | chaque énoncé représenté sans perte | cadre incomplet (B7 inconnues) |
| 3 | Hypothèse | représentation | règle candidate (« ce mot a ce sens dans ce contexte ») | dérivation tracée (B9) | règle explicite et réfutable | ambiguïté non levée |
| 4 | Exercice | items **non vus** du même concept | réponses | générateur d'items, séparé de la leçon | — | item hors couverture |
| 5 | Observation | réponses + corrigé caché | écarts | évaluateur indépendant | écarts mesurés | corrigé absent |
| 6 | Erreur | écarts | typologie d'erreurs | évaluateur | erreurs classées | non classable |
| 7 | Correction | erreurs + intervention humaine | règle révisée | humain identifié | correction tracée | correction contradictoire |
| 8 | Reconstruction | règle révisée | nouvelle explication de la règle | Brody (formulation déclarée) | explication cohérente avec la leçon | divergence |
| 9 | Évaluation indépendante | examen **disjoint** (jamais utilisé pour décider) | score + abstentions | banc d'examen séparé | gain sans régression | gain non significatif → HOLD (modèle P155) |
| 10 | Mémoire candidate | règle + preuves | entrée au ledger de candidats | ledger | candidat complet | preuve manquante |
| 11 | Réutilisation | nouvel item, **autre session** | réponse | B10 (après promotion) | réussite sans réinjection de la leçon | acquis non retrouvé |
| 12 | Transfert | autre contexte / autre concept lié | réponse | — | réussite au-delà du même générateur | hors distribution non couverte |
| 13 | Révision | contradiction validée | règle révisée, ancienne conservée en historique | B10 (révision de slot) | ancienne et nouvelle traçables | conflit non tranché → HOLD |

Une réponse correcte isolée **n'est pas** une compétence : une compétence exige au minimum les étapes 9, 11 et 12 réussies.

---

## C. Mémoire éducative [NP sur la base de [EC]]

Comparaison avant tout nouveau registre :

| Besoin | Mécanisme existant | Suffisant ? |
|---|---|---|
| expérience brute, contexte, chronologie | ledger de candidats (append-only) + journal de session | oui pour la trace ; pas de lien typé à une leçon |
| interprétation produite | leçon candidate (`brody_memory_education_packet`) | partiel (8 types, ≤ 1024 octets) |
| erreurs et contradictions | B7 (inconnues) ; B8 `GapState`, `ReasonCode` | partiel |
| corrections humaines | B8 `HumanAttestation` | oui (typé) |
| preuves | B8 `EvidenceRef`, `VerificationRecord` | oui |
| compétence candidate → acquis | B8 `ClaimState` + porte | oui (isolé) |
| conditions de validité, temps | B8 temporel (« valid-time ») | oui |
| révisions ultérieures | B10 historique de révisions par slot | oui (isolé) |
| reprise après redémarrage | B10 `recover_after_restart` | à éprouver en processus séparé |
| authenticité | B10 : empreinte sha256 **sans signature** | **non** — à ajouter si exigé [UD] |

**Proposition minimale :** ne pas créer de registre ; raccorder **candidat (ledger) → B8 (porte) → B10 (persistance)** pour un domaine pilote textuel, avec promotion **manuelle** conformément au contrat existant. Une expérience, un souvenir ou un triplet RDF n'est jamais en soi une connaissance vraie.

---

## D. Consolidation des apprentissages spécialisés [NP]

Sources : organes, modèles, versions expérimentales, environnements (P155/P156, futurs).

1. **Attribution** : chaque résultat porte sa source (organe, version, environnement, commit, seed).
2. **Comparaison** : résultats concurrents sur le même examen disjoint.
3. **Qualification** : statut B8 (candidat, vérifié, attesté, rejeté) ; jamais de fusion par moyenne.
4. **Conservation des divergences** : un désaccord est un état légitime (pas effacé), conservé dans l'historique B10.
5. **Intégration dans Oxygen** [UD] : mécanisme non décidé ; les versions ne coopèrent pas directement entre elles (règle du fondateur), l'intégration passe par la porte, pas par un échange entre versions.
6. **Reconstruction après interruption** : l'état d'Oxygen doit pouvoir être reconstruit à partir de B10 seul, puis audité.

---

## E. Progression et maturation [NP]

| Axe | Proposition | Ne pas confondre avec |
|---|---|---|
| Progression locale | par compétence : réussite à l'examen disjoint + rétention après interruption + transfert | un score global |
| Maturation transversale (hypothèse) | indicateurs **séparés** : étendue des domaines couverts, taux d'abstention correcte, qualité des révisions après contradiction, cohérence de l'histoire reconstruite | une performance locale ; une conscience |
| Transfert entre domaines | épreuves croisées (ex. concept appris en texte, testé en relation ou en image) | succès sur le même générateur |
| Conservation et révision | épreuves différées et après apprentissage concurrent | absence d'erreur immédiate |

**Enfant / adolescent / adulte** : à traiter, si le fondateur le souhaite, comme **profils pédagogiques** (types de leçons, autonomie, exigences de preuve), jamais comme âges ou capacités supposées. Aucun seuil n'est fixé ici [UD].

---

## F. Épreuves scientifiques [NP, d'après [ER] P155 / P156 / G1]

| Épreuve | Leçon tirée des prototypes | Exigence |
|---|---|---|
| Cours ≠ examen | P155 : flux séparés, examen jamais utilisé pour décider ([ER] reproduit) | conserver ; **plus** des items d'examen d'un **autre générateur** |
| Oubli cumulatif | P156 : règle figée meilleure sur 6/24 tâches ; tolérance relative à l'état courant | mesurer l'oubli par rapport à la **base figée**, par tâche |
| Situations nouvelles | P155/P156 : même distribution | examens hors distribution explicites |
| Redémarrage indépendant | G1 : même processus, verdict constant | redémarrage en **processus séparé**, puis à **jours différents** |
| Falsification / divergence | G1 : sha256 sans clé accepte une falsification | signature (clé) ou chaîne d'audit ; test de falsification obligatoire |
| Transfert entre leçons | — | leçon B évaluée après leçon A et inversement |
| Abstention correcte | B7 / HOLD | mesurer les abstentions justifiées et injustifiées |

---

## G. Premier prototype candidat [NP]

**Le plus petit démonstrateur :** un domaine pilote de **polysémie française** (une dizaine de mots, plusieurs sens chacun), avec leçons humaines, items générés et examen disjoint.

| Mesure | Condition |
|---|---|
| AVANT ENSEIGNEMENT | examen disjoint sans leçon (ligne de base) |
| APRÈS ENSEIGNEMENT | même examen après leçons + corrections |
| APRÈS INTERRUPTION | nouveau processus, état reconstruit depuis B10 seul, sans réinjection des leçons |
| APRÈS APPRENTISSAGE CONCURRENT | après une seconde série de mots, re-mesure de la première (oubli) |
| APRÈS NOUVEAU CONTEXTE | mêmes sens dans des phrases d'un autre registre ou d'un autre générateur (transfert) |

Matériaux : corpus lexical existant (définitions, synonymes, gloses séparés). **Hachette** : référence d'évaluation **privée** (comparaison hors dépôt), **jamais** ingérée ni publiée.

Composants réutilisés : SENS, corpus lexical, B7, ledger de candidats, leçons candidates, B8, B10, garde de promotion. **Composants nouveaux** : un générateur d'items et d'examens disjoints, un protocole d'exécution en processus séparés, une signature de l'état B10 si l'authenticité est exigée.

---

## Décisions ouvertes [UD]

1. Raccorder B8 et B10 (isolés) au parcours éducatif : autorisation et périmètre.
2. Exception gouvernée à la croyance D2 pour permettre une continuité éducative.
3. Mécanisme d'intégration dans Oxygen des acquis d'organes et de versions.
4. Exigence d'authenticité de la mémoire (signature) et propriétaire de la clé.
5. Profils pédagogiques (enfant / adolescent / adulte ou autres) et indicateurs de maturation.
6. Domaine pilote et auteurs humains des leçons et corrections.
7. Réconciliation des contrats Claude / AGY (`docs/semantic/CLAUDE_AGY_CONTRACT_CONFLICTS.md`) avant tout raccord runtime.

STOP avant le build.
