# Cartographie des sources — sémantique, mémoire, causalité (V0)

Statut : **audit forensique en lecture seule**, branche expérimentale
`exp/semantic-grammar-cognitive-lattice-v0`. Aucun fichier du dépôt de
référence Obsidia (`obsidia-jarvis-advanced-integration-v0`) n'a été modifié.

Échelle de maturité utilisée :

| Code | Sens |
|------|------|
| M0 | Placeholder / stub vide (fonction qui renvoie `{}` ou `[]`, schéma sans propriétés) |
| M1 | Concept documenté seulement (prompt d'agent, note de vision) |
| M2 | Implémentation heuristique (mots-clés / regex), non structurée |
| M3 | Implémentation structurée et testée, bornée |
| M4 | Contrat public canonique utilisé en production (routeur, gates) |

---

## 1. AMD (dépôt de travail, ce worktree)

| Concept | Implémentation | Maturité | Réutilisable ? | Manque | Conflit |
|---|---|---|---|---|---|
| UnifiedInputIR | `app/ir/unified_ir.py::build_ir` | M4 | Oui — reste le **résumé gouvernable** | Aucune structure prédicative ; sacs de mots | — |
| Négation composée (prototype 5E-2B-R) | `unified_ir.py` (regex `negated_execution_patterns`) | M2 | Non en l'état | Portée propositionnelle | **Régression de sécurité** : `sans … lance`, `ne … lance … pas` capturent un verbe hors de leur proposition (voir §4) |
| Gates DENY/HOLD/CLARIFY/ALLOW | `app/gates/gates.py` | M4 | Oui, intouchable sur le fond | Les infinitifs (`lancer`, `exécuter`) ne déclenchent pas HOLD (lacune antérieure) | Télémétrie `matched` peut pointer le verbe nié |
| Décision d'inférence | `app/router/decision.py` | M4 | Oui | — | — |
| TaskKind indépendant | `app/semantic/task_kind.py` | M3 | Oui (contrôle croisé) | Anglais surtout | — |
| `SemanticFrame` / `SemanticRelation` (solveurs) | `app/semantic/frame.py` | M3 | Oui **pour les solveurs locaux** (math/logique) | Pas de polarité par prédicat, pas de pragmatique, pas de temps | **Collision de noms** avec la proposition « SemanticFrame » du brief → les nouvelles primitives doivent porter d'autres noms |
| ConstraintGraph | `app/semantic/constraints.py` | M3 | Partiellement (BEFORE/AFTER/IMPLIES/REQUIRES existent déjà) | Domaine fini seulement | — |
| ClosureCertificate | `app/semantic/closure.py` | M3 | Oui : `closure_safe = not (unknowns or contradictions)` est exactement la sémantique de clôture voulue | — | — |
| human_needs | `app/semantic/human_needs.py` | M3 | Modèle de provenance / contradictions / `missing_information` réutilisable | — | — |
| Besoin de preuve du monde courant | `unified_ir.py` (`current_world_evidence`) + `decision.py` (`evidence_required`) | M3 | Oui, à préserver tel quel | Détection lexicale bornée | — |
| Topic router | `app/router/semantic_topics.py` | M2 | Oui | — | — |
| Clôture sémantique historique | `decision.py` (CLARIFY → ALLOW si ANSWER_TASK) | M3 | Oui | — | — |

## 2. Obsidia (référence, lecture seule)

| Concept | Implémentation / document | Maturité | Réutilisable ? | Manque / remarque |
|---|---|---|---|---|
| OS Trad | `apps/obsidia_api/routes/os_trad_ir_reverse.py` (`_intent`, `_risk_flags`, `_alphabet_units`) | M2 | Frontière (`KX108_ONLY`, `ACTION_REQUEST_FORCED_TO_READONLY_PROJECTION`) oui ; analyse non | Détection par **sous-chaînes** (`"lance" in low` matche aussi `balance`) ; les « alphabet units » sont des métadonnées, pas des unités linguistiques |
| Reverse OS | `apps/obsidia_api/brody_existing_reverse_os_bridge.py`, `periphery/reverse_os.py`, `SSRProjection` | M2 | Idée de **projection inverse** (structure → texte/UI/voix) | Projection de sortie, pas d'analyse d'entrée |
| Pré-raisonnement Brody | `periphery/language/pre_reasoning_calibrator.py`, `apps/obsidia_api/brody_pre_reasoning_adapter.py` | M2–M3 | Contrats de non-souveraineté | Heuristiques lexicales |
| Qualification des inconnues | `periphery/language/unknown_qualifier.py` (`BRODY_UNKNOWN_QUALIFICATION_V1`) | M3 | **Oui** : distinction « mot de surface » vs « inconnue causale » ; seules les `unresolved_unknowns` deviennent dette causale | Lexique plat |
| Clôture sémantique causale / suffisance | `scripts/obsidia_cognitive_ingress_v0.py::_evaluate_brody_sufficiency` | M3 | Oui : `closure_critical_missing`, `EVIDENCE_REQUIRED` comme état épistémique ouvert | — |
| ContextPacket | `periphery/common_types.py::ContextPacket` (+ 369 fichiers) | M3 | Oui : `events`, `activated_trees`, `calibrated_links`, `confidence`, `non_decision=True` | `calibrated_links: List[Any]` non typé |
| Mémoire native | `apps/obsidia_api/brody_obsidia_native_memory.py`, index `OBSIDIA_NATIVE_MEMORY_INDEX_V1` (3267 records) | M3 | Oui : provenance (`source_sha256`, `text_sha256`, chemin d'origine), frontière stricte | **Index plat scoré par mots-clés** ; aucune relation, aucune coordonnée temporelle, aucun graphe |
| Candidats / promotion mémoire | `periphery/memory/memory_candidate*.py`, `memory_promotion_policy.py` | M3 | **Oui** : cycle `CAPTURED → … → PROMOTED_MANUAL_ONLY`, jamais d'auto-promotion ⇒ modèle de consolidation | Pas de supersession / versionnement |
| 34 arbres cognitifs (superposition) | `periphery/cognitive_trees/*`, `TreeSpace34`, `ActivationVector`, `…/04_ARBRES_34_TENSOR_MATRIX` | M2–M3 | Oui comme **axes de projection** (vecteur d'appartenance simultanée) | Activation par mots-clés |
| Nuage de points 21D | `apps/obsidia_api/brody_point_cloud_21d_selector.py` | M2 | Oui comme **inventaire d'axes** (domaine, autorité, réversibilité, preuve, temporalité, source, trajectoire, projection, mémoire, symbolique…) | Axes calculés par regex ; sert à sélectionner des couches, pas à positionner des objets |
| Graphe de relations / path finder / projection Φ / distance / similarité | `periphery/relation_graph.py`, `path_finder.py`, `projection_phi.py`, `distance_structured.py`, `similarity_search.py` (+ copies dans `13_GRAPHES_NUAGE_POINTS`) | **M0** | — | **Stubs vides** : `build_graph → {}`, `find_path → []`, `Link.schema.json` et `LinkType.enum.json` vides |
| Timeline / Event / NodeContinuum | `periphery/event_model.py`, `continuum_node.py`, `…/03_MEMOIRE_MONDE_COSMOS_REFLEX/timeline.py` | M0–M1 | Noms seulement | `Timeline` = liste ; `Mmonde_FORMAL_SPEC.md` = « Placeholder » |
| Chaîne causale | `periphery/math_core/causal_chain.py` | M3 | Oui pour la **gouvernance** (contexte → perception → invariant → ticket → décision → action → bilan, propriétés A1–A3) | C'est une causalité **procédurale** (pipeline), pas une causalité **du discours / du monde** |
| Provenance | `periphery/provenance_gate.py` (`PROVENANCE_WEAK`, `FAKE_PROVENANCE`) ; mémoire native | M2–M3 | Oui | — |
| Contradictions | `CONTRADICTION_HUNTER` (prompt) ; `check_incoherence.py` (2 lignes) ; `human_needs` | M1–M2 | Taxonomie oui : « vraie contradiction / tension productive / malentendu terminologique » ; « contradiction temporelle » | Pas d'implémentation générale |
| Calibration des liens | Prompt `CALIBRATION_PROCEDURALE` (sources extraites, l.1784-1809) | M1 | **Oui, directement** : Force (FORT/MOYEN/FAIBLE) × Type (CAUSAL/STRUCTUREL/ANALOGIQUE/TEMPOREL/HYPOTHÉTIQUE) × Direction (DIRECT/INDIRECT/BIDIRECTIONNEL) ; « un lien analogique n'est pas un lien causal » ; « un lien tout → tout est un lien nul » | Non codé |
| Frise chronologique | Prompt `FRISE_HUMAINE` (RUPTURE / CONTINUITÉ / RÉINTÉGRATION) | M1 | Vocabulaire oui | Non codé |
| Mémoire comme état causal / mémoire de contraintes (COSMOS) | Sources extraites l.2375-2490 | M1 | **Doctrine clé** : « la mémoire extrait les contraintes qui rendent le prochain état possible ou impossible » ; « L2 observe les contraintes, L1 tranche » | Non codé |
| Graphe multidimensionnel / Nœud Continuum | Sources extraites l.38-39, 450, 529, 537 | M1 | **Confirme l'hypothèse multidimensionnelle de l'utilisateur** : « chaque donnée (Nœud Continuum) n'appartient pas à un seul arbre mais possède un vecteur d'appartenance à plusieurs arbres simultanément » | Non codé (pseudo-code numpy seulement) |
| Trajectoires | `periphery/timeverse.py` (divergence de trajectoire, dérive de contexte → HOLD) | M2 | Mesures scalaires | Pas de chemin dans un graphe |
| Éducation | `apps/obsidia_api/brody_memory_education_packet.py`, `periphery/education/education_score.py` | M2–M3 | Types de leçons (invariant, frontière, fastpath, rejet adversarial) | — |
| World model | aucun module | — | — | Seul l'agent « Réalité Physique » (vitesse × temps) est décrit (M1) |
| Hypergraphe | aucune occurrence | — | — | — |

## 3. Lecture transversale

1. **Le concept multidimensionnel existe depuis l'origine** (superposition des
   34 arbres, Nœud Continuum, nuage de points, calibration des liens), mais
   **toute la couche relationnelle est au stade M0/M1** : graphe, path finder,
   liens typés, timeline et projection Φ sont des stubs.
2. Ce qui est réellement mûr est la **frontière** (non-souveraineté,
   `KX108_ONLY`, promotion manuelle, provenance hachée) et la **clôture**
   (`closure_safe = not (unknowns or contradictions)`, `EVIDENCE_REQUIRED`).
3. Il n'existe **aucune** représentation prédicative du langage (prédicat +
   arguments + polarité + portée). Toutes les couches linguistiques auditées
   (OS Trad, IR, pré-raisonnement, topic router) sont des sacs de mots.
4. Deux « causalités » distinctes coexistent et **ne doivent pas être fusionnées** :
   causalité **procédurale** de gouvernance (`causal_chain.py`) et causalité
   **énoncée** dans le discours (« car », « donc », « parce que »).

## 4. Défaut de sécurité trouvé dans le prototype de départ (HEAD 8068261)

Mesuré avec `decide()` sur HEAD et sur le commit précédent `0b348ab` :

| Entrée | 0b348ab | 8068261 (prototype) |
|---|---|---|
| `sans attendre, lance le script` | HOLD | **ALLOW → fireworks** |
| `sans hésiter, execute le script` | HOLD | **ALLOW → fireworks** |
| `ne t'inquiète pas, lance le script, pas besoin de confirmer` | HOLD | **ALLOW → fireworks** |

Cause : les motifs `\bsans\b.{0,40}?\b(lance)\b` et
`\bne\b.{0,40}?\b(lance)\b.{0,24}?\bpas\b` ne respectent pas la portée
grammaticale (« sans » ne régit que son infinitif ; « ne … pas » ne franchit
pas une frontière de proposition). Le verbe positif est effacé du signal
d'action **et** la gate l'exempte (`no_execute` + `action_type != act_request`).

Lacune antérieure (déjà présente en 0b348ab) : `lancer le script`,
`tu peux lancer le test ?`, `peux-tu exécuter le script ?` → ALLOW/fireworks,
car seules les formes exactes `lance` / `execute` / `run` sont des mots-clés HOLD.
