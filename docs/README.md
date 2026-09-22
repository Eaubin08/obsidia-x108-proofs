# Guide des documents Obsidia

> Index généré le 2026-09-15 à partir de `main` (5d27d003). **Aucun document n'a été déplacé** : ce guide les organise par couche et chaque lien pointe vers l'emplacement actuel du fichier.

## Commencer ici

| Guide | Pour comprendre |
|---|---|
| **[Comprendre Obsidia](COMPRENDRE_OBSIDIA.md)** | ce qu'est Obsidia, d'où il vient, à quoi il répond, sa philosophie, ce qu'il ne prétend pas |
| **[Trajets de la donnée](TRAJETS.md)** | comment Brody répond, comment le savoir devient mémoire, comment une action est autorisée, comment fonctionnent OS Trad, le corpus math et les signaux physiques |
| **[Entraînement, éducation, naissance](EDUCATION.md)** | Oxygen et « une seule naissance », organes et micro-agents, du savoir au réflexe, pack éducatif, curriculum, corpus mathématique, état réel |
| **[Sécurité](SECURITE.md)** | les couches de sécurité, de l'autorité isolée au scan de secrets |
| **[État réel 2026-09-15](ETAT_REEL_2026_09_15.md)** | reprise d'audit multi-worktrees : M4D4 staged, Native Memory, retrait Graphiti/Neo4j, GPS/RF, corpus math, Oxygen futur |

Ce guide-ci répond à trois questions : **comment une demande traverse Obsidia**, **quelle couche fait quoi**, et **où trouver les documents et le code de chaque couche**.

> **Deux lignes de code.** Une partie de la stack actuelle (mémoire native, MEMZUM, calibration du langage, jonction cognitive) vit sur la branche `integration/harness-runtime-binder-v1`, pas encore fusionnée dans `main`. L'audit du 2026-09-15 indique aussi que le cutover le plus avancé Native Memory / retrait Graphiti-Neo4j est dans le worktree M4D4 `obsidia-main-direct-20260914`, référence `5d27d003 + index staged`. Les liens marqués **(H)** pointent vers Binder tant que M4D4 n'est pas publié proprement.

## Parcours de lecture recommandé

| Si tu veux... | Lis |
|---|---|
| comprendre l'idee sans entrer dans le code | [Comprendre Obsidia](COMPRENDRE_OBSIDIA.md) |
| voir comment une entree devient contexte, reponse, action ou preuve | [Trajets de la donnée](TRAJETS.md) |
| comprendre pourquoi Brody fonctionne deja sans naissance d'Oxygen | [Entraînement, éducation, naissance](EDUCATION.md) puis [Trajets § 7](TRAJETS.md#7-pourquoi-ça-fonctionne-sans-entraînement) |
| savoir ce qui est actif, staged, partiel, futur ou legacy | [État réel 2026-09-15](ETAT_REEL_2026_09_15.md) |
| verifier pourquoi une proposition ne peut pas devenir action automatiquement | [Sécurité](SECURITE.md) |
| retrouver les couches et les dossiers | ce guide, puis les fichiers dans [couches/](couches/) |

Le fil commun est toujours le meme :

```text
source -> representation -> contexte -> cognition -> proposition
-> verification -> autorite -> action eventuelle -> receipt
```

Chaque page doit etre lue avec deux niveaux : le recit explique la machine a quelqu'un qui decouvre Obsidia ; les encarts techniques disent ce qui est code, staged, teste, partiel ou futur.

## Obsidia en une phrase

Obsidia est un système d'exploitation cognitif gouverné : l'intelligence est distribuée entre des organes spécialisés, **l'autorité reste isolée dans le noyau X-108**. Source : [README](../README.md#1-obsidia-en-une-phrase).

```text
Cognition → Intention → Décision → Action → Preuve
Règle d'autorité : KX108_ONLY
```

## Le trajet d'une demande, étape par étape

Toutes les demandes ne parcourent pas toute la chaîne. Une consultation en lecture seule peut s'arrêter avant X-108, alors qu'une action critique doit franchir toutes les frontières. Source : [README § 16](../README.md#16-larchitecture-générale).

| Étape | Ce qui se passe | Couches |
|---|---|---|
| **1 · Entrée** | Une demande arrive : message humain, code, document, donnée, événement ou signal externe. | [15 Atlas et signaux externes](couches/15_ATLAS_EXTERNAL_SIGNALS.md)<br>[13 Connecteurs, outils, MCP](couches/13_MCP_TOOLS_CONNECTORS.md) |
| **2 · Traduction et compréhension** | OS Trad et Unified Input IR la traduisent dans le langage d'Obsidia, avec son contexte, puis la routent. | [12 Langage : OS Trad et IR](couches/12_LANGUAGE_OS_TRAD_IR.md)<br>[14 Mémoire, contexte, éducation](couches/14_CONTEXT_MEMORY_EDUCATION.md) |
| **3 · Plan et capacités** | Le runtime construit le plan actif, consulte le Capability Graph et le Corpus Resolver, et choisit les organes à mobiliser. | [18 Runtime, capacités, API](couches/18_RUNTIME_CAPABILITIES_API.md) |
| **4 · Organes spécialisés** | Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas. | [10 Système cognitif : Brody, Obsidure, agents](couches/10_COGNITIVE_SYSTEM.md)<br>[14 Mémoire, contexte, éducation](couches/14_CONTEXT_MEMORY_EDUCATION.md)<br>[20 Domaines critiques : GPS, Bank, Trading](couches/20_DOMAINS_CRITICAL_WORLDS.md)<br>[11 Haute périphérie : Sigma et Peripheral Mesh](couches/11_HIGH_PERIPHERY_MACHINERY.md)<br>[09 Tree34 et flux AGI](couches/09_AGI_TREE34_FLUX.md)<br>[06 Entropie et thermodynamique](couches/06_ENTROPY_THERMODYNAMICS_POG.md)<br>[21 Valeur : Gencoin et Jcoin](couches/21_VALUE_GENCOIN_JCOIN.md)<br>[22 Blockchain et sécurité de chaîne](couches/22_BLOCKCHAIN_SECURITY.md) |
| **5 · Preuves et gouvernance** | Tests, replay, Lean, ProofKit, receipts et checkpoints établissent ce qui est prouvé, avant tout passage au réel. | [26 Tests, QA, reproductibilité](couches/26_TEST_QA_REPRODUCIBILITY.md)<br>[24 Méthodes formelles : Lean et TLA+](couches/24_FORMAL_METHODS.md)<br>[25 Preuve, replay, attestation (OS3)](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md)<br>[27 Audits et preuves d'exécution](couches/27_AUDIT_EVIDENCE_ARTIFACTS.md) |
| **6 · Frontière** | Les gardes d'ingress vérifient que seul un envelope valide atteint le noyau. | [17 Frontières d'action et ingress](couches/17_BOUNDARIES_ACTION_INGRESS.md) |
| **7 · Décision X-108** | Le noyau, seule autorité (KX108_ONLY), rend ACT, HOLD ou BLOCK. Il juge avant l'exécution et bloque en cas de doute (fail-closed). | [16 Noyau d'autorité X-108](couches/16_X108_AUTHORITY_KERNEL.md) |
| **8 · Action contrôlée et trace** | Si c'est autorisé, l'action part par une frontière bornée. Elle est mesurée, scellée et rejouable, et reste visible dans le Workbench et le Terminal. | [17 Frontières d'action et ingress](couches/17_BOUNDARIES_ACTION_INGRESS.md)<br>[25 Preuve, replay, attestation (OS3)](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md)<br>[19 Interface : Workbench et Terminal](couches/19_INTERFACE_WORKBENCH_VISUALIZATION.md) |

```text
Entrée ─▶ Traduction (OS Trad / IR) ─▶ Plan & capacités ─▶ Organes (Brody, mémoire, domaines, Sigma…)
      ─▶ Preuves (tests, Lean, replay) ─▶ Frontière ─▶ X-108 : ACT | HOLD | BLOCK ─▶ Action bornée + sceau
```

### Ce que produit chaque grande étape

| Étape | Reçoit | Produit | Limite |
|---|---|---|---|
| Entrée | texte, fichier, signal, événement | source située avec provenance et temporalité | une source n'est pas encore une vérité |
| OS Trad / IR | langage humain ou technique | intention, entités, relations, unknowns, représentation intermédiaire | ne décide pas et ne prouve pas |
| Contexte | mémoire, corpus, source packs, session | fragments hydratés, statuts, références | le contexte n'autorise rien |
| Brody | représentation + contexte | réponse structurée, proposition ou clarification | pas d'ACT, pas d'écriture canonique |
| Domaines | objets métier ou physiques | contraintes, risques, traductions domaine | le domaine ne crée pas sa loi |
| Sigma / preuves | sortie candidate, tests, traces | contradictions, preuves bornées, manques | une preuve n'est pas une autorisation |
| X-108 | envelope admissible | `ACT`, `HOLD` ou `BLOCK` | autorité unique, fail-closed |
| Receipts | action ou décision | trace vérifiable et rejouable | ne transforme pas une action en succès métier automatiquement |

### Qui a le droit de faire quoi

| Organe | Peut | Ne peut pas |
|---|---|---|
| Brody | comprendre, relier, reformuler, consulter la mémoire, utiliser des outils bornés | décider, être la mémoire |
| Mémoire native + MEMZUM | MEMZUM dit s'il faut de la mémoire ; la mémoire native restitue ce qui a été validé | écrire pendant une conversation, devenir automatiquement une vérité canonique |
| Oxygen *(vision)* | porter l'identité, la naissance, la biographie et la mémoire éducative | agir, décider : l'autorité reste à X-108 |
| Micro-agents | chercher, comparer, filtrer, tester, produire un receipt dans leur périmètre | posséder une identité, une biographie ou une souveraineté |
| Sigma | détecter contradictions et dérives, guider, expliquer | trancher à la place de X-108 |
| Obsidure | inspecter, proposer un patch, tester en sandbox, produire une preuve | commit, push ou promouvoir seul |
| Domaines | comprendre leur terrain et le traduire | créer leur propre loi, être l'autorité finale |
| Lean / ProofKit | prouver des propriétés bornées, produire des artefacts | prendre une décision métier |
| **X-108** | **rendre ACT, HOLD ou BLOCK avant exécution** | déléguer son autorité |

Source : [README § 17](../README.md#17-les-principaux-organes).

## Comment circule la donnée : savoir, cognition, action

Le trajet ci-dessus est la vue d'ensemble. Le guide **[TRAJETS.md](TRAJETS.md)** détaille, fichier par fichier, les trois circulations réelles :

- **[La cognition](TRAJETS.md#1-le-trajet-de-la-cognition--comment-brody-répond)** : ce que fait `/brody/chat`, du filtre de secrets à la réponse True Voice, en lecture seule ;
- **[Le savoir](TRAJETS.md#2-le-trajet-du-savoir--comment-une-information-devient-mémoire)** : capture, tri, **validation humaine**, essai à blanc, écriture manuelle gardée, vérification, relecture ;
- **[L'action](TRAJETS.md#3-le-trajet-de-laction--comment-une-proposition-touche-le-réel)** : possible, admissible, autorisé par X-108, puis réel.
- **[Les mathématiques](TRAJETS.md#5-le-trajet-mathématique--comment-le-corpus-guide-une-réponse)** : corpus, retrieval, statuts, context pack et distinction entre piste, calcul, test et preuve ;
- **[Le monde physique](TRAJETS.md#6-le-trajet-physique--comment-un-signal-entre-dans-obsidia)** : GPS/RF, timestamps, provenance, anti-replay, causalité non automatique ;

Et surtout : **[pourquoi ça fonctionne déjà sans entraînement](TRAJETS.md#7-pourquoi-ça-fonctionne-sans-entraînement)**. Dans le chemin M4D4 audité, Brody répond sans appel LLM externe : le savoir vient des fichiers validés, de Native Memory, des corpus, des règles, des scores, du micro-core, des balances, du point cloud 21D, de MEMZUM, des adapters, du moteur local et de True Voice.

## Les domaines

Un domaine (GPS, Bank, Trading, Gencoin, blockchain…) comprend son terrain : objets, règles, risques, preuves. Il le traduit vers la gouvernance commune. **Le domaine traduit, X-108 tranche.**

- [20 · Domaines critiques : GPS, Bank, Trading](couches/20_DOMAINS_CRITICAL_WORLDS.md)
- [21 · Valeur : Gencoin, Jcoin](couches/21_VALUE_GENCOIN_JCOIN.md)
- [22 · Blockchain](couches/22_BLOCKCHAIN_SECURITY.md)

Source : [README § 18](../README.md#18-les-domaines-et-les-possibilités-dextension).

## Toutes les couches

| Couche | Rôle | Docs | Code |
|---|---|---:|---:|
| [00_SCOPE_DISCIPLINE](couches/00_SCOPE_DISCIPLINE.md) | Périmètre et discipline | 34 | 48 |
| [01_FOUNDATIONS_PHILOSOPHY](couches/01_FOUNDATIONS_PHILOSOPHY.md) | Fondations et philosophie | 2 | 13 |
| [02_ONTOLOGY_SEMANTICS](couches/02_ONTOLOGY_SEMANTICS.md) | Ontologie et sémantique | 1 | 10 |
| [03_COSMOS_MMONDE_WORLD](couches/03_COSMOS_MMONDE_WORLD.md) | Cosmos, MMonde, monde | 0 | 657 |
| [04_NARRATIVE_PROVENANCE_NPL](couches/04_NARRATIVE_PROVENANCE_NPL.md) | Narratif et provenance (NPL) | 0 | 43 |
| [05_MATHEMATICS](couches/05_MATHEMATICS.md) | Mathématiques | 2 | 55 |
| [06_ENTROPY_THERMODYNAMICS_POG](couches/06_ENTROPY_THERMODYNAMICS_POG.md) | Entropie et thermodynamique | 14 | 42 |
| [07_BALANCE_BUV_GEOMETRIES](couches/07_BALANCE_BUV_GEOMETRIES.md) | Balance BUV et géométries | 0 | 7 |
| [08_CONSTITUTION_STRUCTURAL_LAWS](couches/08_CONSTITUTION_STRUCTURAL_LAWS.md) | Constitution et lois structurelles | 27 | 20 |
| [09_AGI_TREE34_FLUX](couches/09_AGI_TREE34_FLUX.md) | Tree34 et flux AGI | 0 | 13 |
| [10_COGNITIVE_SYSTEM](couches/10_COGNITIVE_SYSTEM.md) | Système cognitif : Brody, Obsidure, agents | 87 | 821 |
| [11_HIGH_PERIPHERY_MACHINERY](couches/11_HIGH_PERIPHERY_MACHINERY.md) | Haute périphérie : Sigma et Peripheral Mesh | 30 | 44 |
| [12_LANGUAGE_OS_TRAD_IR](couches/12_LANGUAGE_OS_TRAD_IR.md) | Langage : OS Trad et IR | 15 | 30 |
| [13_MCP_TOOLS_CONNECTORS](couches/13_MCP_TOOLS_CONNECTORS.md) | Connecteurs, outils, MCP | 4 | 39 |
| [14_CONTEXT_MEMORY_EDUCATION](couches/14_CONTEXT_MEMORY_EDUCATION.md) | Mémoire, contexte, éducation | 51 | 89 |
| [15_ATLAS_EXTERNAL_SIGNALS](couches/15_ATLAS_EXTERNAL_SIGNALS.md) | Atlas et signaux externes | 4 | 61 |
| [16_X108_AUTHORITY_KERNEL](couches/16_X108_AUTHORITY_KERNEL.md) | Noyau d'autorité X-108 | 15 | 13 |
| [17_BOUNDARIES_ACTION_INGRESS](couches/17_BOUNDARIES_ACTION_INGRESS.md) | Frontières d'action et ingress | 24 | 16 |
| [18_RUNTIME_CAPABILITIES_API](couches/18_RUNTIME_CAPABILITIES_API.md) | Runtime, capacités, API | 254 | 149 |
| [19_INTERFACE_WORKBENCH_VISUALIZATION](couches/19_INTERFACE_WORKBENCH_VISUALIZATION.md) | Interface : Workbench et Terminal | 89 | 69 |
| [20_DOMAINS_CRITICAL_WORLDS](couches/20_DOMAINS_CRITICAL_WORLDS.md) | Domaines critiques : GPS, Bank, Trading | 54 | 112 |
| [21_VALUE_GENCOIN_JCOIN](couches/21_VALUE_GENCOIN_JCOIN.md) | Valeur : Gencoin et Jcoin | 42 | 30 |
| [22_BLOCKCHAIN_SECURITY](couches/22_BLOCKCHAIN_SECURITY.md) | Blockchain et sécurité de chaîne | 13 | 20 |
| [23_SECURITY_COMPLIANCE](couches/23_SECURITY_COMPLIANCE.md) | Sécurité et conformité | 15 | 33 |
| [24_FORMAL_METHODS](couches/24_FORMAL_METHODS.md) | Méthodes formelles : Lean et TLA+ | 21 | 325 |
| [25_OS3_PROOF_REPLAY_ATTESTATION](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md) | Preuve, replay, attestation (OS3) | 47 | 90 |
| [26_TEST_QA_REPRODUCIBILITY](couches/26_TEST_QA_REPRODUCIBILITY.md) | Tests, QA, reproductibilité | 19 | 564 |
| [27_AUDIT_EVIDENCE_ARTIFACTS](couches/27_AUDIT_EVIDENCE_ARTIFACTS.md) | Audits et preuves d'exécution | 82 | 159 |
| [28_FREEZE_CANON_REGISTRIES](couches/28_FREEZE_CANON_REGISTRIES.md) | Freeze, canon, registres | 73 | 52 |
| [29_RESEARCH_PEPITES_EVOLUTION](couches/29_RESEARCH_PEPITES_EVOLUTION.md) | Recherche et pépites | 3 | 309 |
| [30_DEV_TOOLING_CI_STAGING](couches/30_DEV_TOOLING_CI_STAGING.md) | Outillage, CI, staging | 5 | 262 |
| [99_ARCHIVE_PROVENANCE](couches/99_ARCHIVE_PROVENANCE.md) | Archives et provenance | 15 | 32 |

La colonne *Code* vient du registre V3, qui est partiel (832 fichiers non classés, 304 absents) : chaque guide de couche liste aussi ses points d'entrée connus.

Les couches **01 à 08** sont conceptuelles (vocabulaire, lois). Les couches **00, 23, 28, 29, 30 et 99** sont transverses.

## Comment lire le statut d'un document

| Statut | Signification |
|---|---|
| référence | document actuel : spec, contrat, guide, README |
| référence probable | semble actuel, à confirmer |
| rapport / preuve d'exécution | audit, smoke test, capture, résultat |
| phase passée | rapport d'une phase terminée (PHASE12, F17, P56…) |
| archive | ancien, legacy, recovery |
| preuve scellée | artefact de preuve protégé : ne jamais modifier |

## Par où commencer

- **Découvrir le projet** : [README](../README.md), puis [état public](status/PUBLIC_STATUS.md) s'il existe.
- **Comprendre le noyau** : [KERNEL_OVERVIEW.md](KERNEL_OVERVIEW.md), puis [couche 16](couches/16_X108_AUTHORITY_KERNEL.md).
- **Auditer les preuves** : [START_HERE](../START_HERE.md), [couche 24](couches/24_FORMAL_METHODS.md) et [couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md).
- **Comprendre Brody et Obsidure** : [couche 10](couches/10_COGNITIVE_SYSTEM.md).
- **Limites et vocabulaire** : [LIMITS.md](LIMITS.md) et [GLOSSAIRE.md](GLOSSAIRE.md).

## Important : ne pas déplacer ces dossiers

Des programmes lisent directement certains dossiers de `docs/`. Les déplacer casserait l'API, le Workbench ou des tests :

- `docs/runtime/` · lu par 73 fichier(s), par exemple `apps/obsidia-workbench/src/components/RightPanel.tsx`
- `docs/core_import/` · lu par 51 fichier(s), par exemple `scripts/audit_agents_complementary_reconciliation_p73.py`
- `docs/security/` · lu par 11 fichier(s), par exemple `scripts/audit_optional_publication_readiness_recheck.py`
- `docs/freeze/` · lu par 8 fichier(s), par exemple `apps/obsidia_api/brody_cognitive_modules_adapter.py`
- `docs/source_packs/` · lu par 7 fichier(s), par exemple `runtime_wiring/source_runtime/runtime_inventory_builder.py`
- `docs/proof/` · lu par 6 fichier(s), par exemple `scripts/audit_presentation_proof_public_private_split_p78.py`
- `docs/architecture/` · lu par 5 fichier(s), par exemple `periphery/workflow_governance_readonly/repo_aware/obsidia_x108_repo_map.py`
- `docs/public/` · lu par 5 fichier(s), par exemple `scripts/audit_presentation_proof_public_private_split_p78.py`
- `docs/protocols/` · lu par 5 fichier(s), par exemple `scripts/obsidia_cli.py`
- `docs/real_engine/` · lu par 4 fichier(s), par exemple `runtime_wiring/source_runtime/runtime_inventory_builder.py`
- `docs/demo/` · lu par 4 fichier(s), par exemple `scripts/audit_f45_canonical_observation_terminal_test_battery.py`

---
*1042 documents indexés. Classement automatique : carte du guide V3 (`FILE_RELOCATION_MAP.csv`, `FILE_TO_FUNCTIONALITY.csv`) et règles sur les noms de fichiers.*
