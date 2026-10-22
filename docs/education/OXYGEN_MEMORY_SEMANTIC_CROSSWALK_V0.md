# Oxygen — crosswalk mémoire et récupération sémantique (V0)

**Date :** 2026-10-17 · **Auteur :** Claude · **Statut : RÉCONCILIATION DOCUMENTAIRE, non canonique.** Aucun nouveau moteur mémoire, aucune intégration runtime, aucun changement AGY.

Objet : rapprocher l'architecture mémoire historique (sources d'assistant retrouvées par l'audit Gmail/Drive) de ce qui existe réellement dans le code, avant de figer le pilote « force ».

Étiquettes : **[FV]** vision du fondateur · **[AF]** formulation historique d'assistant · **[EC]** code existant · **[TE]** tests · **[RT]** appelé sur le chemin public `brody_chat` (trace dynamique) · **[NP]** proposition · **[UD]** décision ouverte · **[NR]** source identifiée, **non lue par Claude**.

## 0. Sources

| Source | Statut |
|---|---|
| Drive « math formlisation memoir eect » `14pzHsqoZ-sU7NMOlSTNTCDK0M41GWC-WQFsxrSbU2Ss` | **[NR]** — absente du pack, aucun accès Drive |
| Drive « monde memoire ect » `1gLu3ssnDfiCl7wnhGEAfqS_14cGeQxxR--8FYhMKtnU` | lu (export 03 du pack, SHA-256 vérifié) — audit d'assistant [AF] |
| Gmail 5 mai `19df5b3103df6234`, `19df5b354dc107d1` ; 8 mai `19e064efcd44f01b` ; 25 septembre `1a0d5d135172abf9` | **[NR]** — aucun accès Gmail ; synthèses d'assistant, jamais citées comme paroles du fondateur |
| Code local | worktree `8137f8e6` ; traces dynamiques sur de vrais appels `brody_chat` (journaux isolés, aucune écriture) |

## 1. Correspondances

| # | Notion historique | Ce que disent les sources lues | Code existant | Statut réel | Écart |
|---|---|---|---|---|---|
| 1 | **Frise chronologique du monde humain** et **chronologie éducative d'Oxygen** | doc 03 L424–L438, L683 : mémoire chronologique, causalité [AF] | Native Memory : **aucun champ de date** (enregistrements : `source_ref`, `source_sha256`, `tree_id`, `taxonomy`, `tags`, `text_excerpt`…) ; B8 : temps de validité (`ValidTimeInterval`, `overlaps`, `contains`) ; B10 : révisions par slot | Native Memory [EC][RT] ; B8 / B10 [EC][TE], isolés | aucune frise ni chronologie éducative implémentée ; deux chronologies **distinctes** à ne pas confondre : temps du monde (quand c'est vrai) et temps d'apprentissage (quand Oxygen l'a appris) |
| 2 | **34 arbres** comme axes cognitifs multidimensionnels | doc 06 : projection spectrale sur 34 arbres [AF] | `periphery/cognitive_trees/` : `tree_registry` (34 arbres, R^34, provenance), `shazam_cognitif`, `tree_activation_vector`, `dominant_trees`, `memory_world_mapper`, `tree_signal_packet` ; tests `tests/periphery`, `tests/api`, `tests/non_sovereignty` | **[RT] appelés à chaque requête Brody** : `shazam_cognitif` ×2, `build_activation_vector`, `find_dominant_trees`, `map_memory_world`, `build_tree_signal_packet` | signal de contexte seulement (« never a decision ») ; aucun lien avec un sens lexical ou une leçon |
| 2b | Classification **34 → 8 familles** | `docs/EDUCATION.md` (curriculum 8 familles) [AF] | `periphery/brody_memory_readonly/brody_taxonomy_mapper_34_8_readonly_v1_6_4d.py` déclare **contourner** la réduction 34→8 (« Bypasses the 34-to-8 dimension reduction ») | [EC] ; **non appelé** sur le chemin Brody (trace) | la réduction 8 familles n'est pas active ; R^34 est la seule dimension utilisée |
| 3 | **Domaines spécialisés**, indépendants des arbres | domaines Obsidia (bank, trading, GPS…) | `memory_world_mapper` porte un contrat de domaine (`tests/periphery/test_memory_world_mapper_domain_contract.py`) ; domaines de Brody | [EC][RT] (mapper) | l'indépendance domaine ↔ arbre n'est pas formalisée pour l'éducation |
| 4 | **Mot → sens → contexte → concept → relations**, polysémie, ambiguïté | doc 03 : polysémie / ambiguïté (L1449, L4283–L4350) [AF] | corpus lexical (`periphery/language`) : formes, définitions, groupes de synonymes, gloses, typés par `kind` ; SENS (scellé) : cadres d'énoncés, ambiguïtés | corpus [EC][RT] ; SENS [EC][RT] | **pas de niveau « concept »** ni de relations entre sens ; un groupe de synonymes n'est pas un sens ; l'inventaire de sens de « force » n'est pas dérivable du corpus |
| 5 | **Nuages de points, graphes, causalité, analogies, calibration** | doc 03 L484 (nuages), L756–L792 (Graphiti, graphe temporel), causalité (163 occurrences), analogie L3267 [AF] | point cloud 21D (`brody_point_cloud_21d_selector`), micro-core / balance ; `runtime_loader` charge `graphiti_readonly_bridge` | point cloud [EC] (branché selon la doc `EDUCATION.md`, non retracé ici) ; Graphiti **chargé** (statut), retrait Graphiti / Neo4j déclaré dans `ETAT_REEL_2026_09_15` | aucun graphe sémantique des sens ni relation causale apprise |
| 6 | **Continuum, chemins de raisonnement, expériences, révisions, supersession** | doc 03 L763–L768 (T1 hypothèse → T2 observation → T3 révision) [AF] | B9 chemins cognitifs ; B8 états (`SUPERSEDED`, `CONTESTED`, `INVALIDATED`, `STALE`) et bundles de supersession ; B10 historique de slot ; ledger de candidats | [EC][TE], **isolés** (B8 / B9 / B10) ; ledger [EC] hors chemin Brody | la mécanique de révision existe mais n'est raccordée à rien |
| 7 | **Recherche historique** : ce qui était connu à une date donnée, sans effacer | doc 03 L756–L759 : « une information devenue obsolète peut être invalidée sans que son historique disparaisse » [AF] | B10 `get_artifacts_at_or_before(slot, revision)`, `get_slot_history` ; B8 temps de validité | [EC][TE], **isolés** | Native Memory ne permet **pas** une requête « à la date D » ; deux axes à distinguer : révision (quand on l'a enregistré) et validité (quand c'était vrai) |
| 8 | **Native Memory, SENS, MMonde, B8 / B9 / B10, promotion manuelle** | `docs/EDUCATION.md`, `MEMORY_PROMOTION_MANUAL_ONLY_V1` | Native Memory (lecture seule, 3 267 enregistrements, [RT] `build_native_memory_retrieval_snapshot`) ; SENS [RT] ; MMonde (M41 `app/world_model` chargé à la demande) ; B8 / B9 / B10 isolés ; promotion **manuelle** ; validation B8 ≠ autorisation d'écriture B10 | voir `OXYGEN_EDUCATION_PRECONCEPTION_V0.md` (carte V0.1) | aucune écriture d'expérience ; aucune promotion automatique |

## 2. Écarts réels

1. **Pas de dimension temporelle** dans Native Memory ; la recherche « à une date » n'existe que dans B8 / B10 isolés.
2. **Arbres actifs mais déconnectés du sens** : les 34 arbres produisent un signal à chaque requête, sans lien avec les sens lexicaux ni avec une leçon.
3. **Réduction 34 → 8 inactive** (contournée explicitement).
4. **Pas de niveau concept / relation** entre mot et connaissance ; la polysémie n'est représentée que par des listes de synonymes.
5. **Révision et supersession implémentées mais isolées** (B8 / B10).
6. **Sources mémoire historiques non lues** : Drive « math formlisation memoir eect » et quatre mails [NR].

## 3. Dépendances pour le pilote « force »

| Besoin du pilote | Dépendance | Disponible ? |
|---|---|---|
| sens d'un mot | inventaire humain + corpus lexical | partiel (inventaire humain requis) |
| contexte d'emploi | SENS + phrases du pilote | partiel |
| domaine | étiquette de domaine par item | à fournir par le pilote |
| temporalité (validité, révision) | B8 temps de validité + B10 révisions | oui, en banc isolé |
| provenance | `MemoryCandidate.source_id`, B8 `EvidenceRef` | oui, en banc isolé |
| arbres cognitifs | `tree_activation_vector` | disponible, **hors portée** du pilote V0 |

## 4. Portée du RED isolé

Le RED isolé V0 teste l'**acquisition locale de sens**, sa **conservation** et sa **récupération** par sens, domaine, contexte, temporalité et provenance, **dans un banc**. Il **ne teste pas** et ne démontre pas : la mémoire multidimensionnelle (arbres, nuages, graphes, causalité, analogies), la frise du monde humain, la chronologie éducative globale d'Oxygen, ni une intégration avec Native Memory.

## 5. Plan restant

1. Lecture de la Drive « math formlisation memoir eect » et des quatre mails (export ou accès fourni) ; mise à jour de ce crosswalk.
2. Décider si le pilote V1 doit croiser sens et arbres cognitifs (signal R^34) [UD].
3. Décider de la représentation « concept / relation » entre sens et connaissance [UD].
4. Aucune intégration runtime avant la réconciliation des six conflits Claude / AGY.

STOP avant toute intégration runtime.
