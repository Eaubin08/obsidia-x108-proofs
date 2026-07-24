# OBSIDIA_OPERATOR_DOCTRINE

**Version :** V0
**Statut :** Référence doctrinale canonique
**Authority :** KX108_ONLY
**Scope :** Toutes les couches et sessions de travail Obsidia
**Decision authority :** Aucune — document de référence uniquement

---

## 1. Purpose

Ce document définit les règles doctrinales d'opération de l'architecture Obsidia X-108.

Il décrit qui fait quoi, ce que chaque couche peut et ne peut pas faire, et les règles qui ne changent pas quelle que soit la session, le scope ou le mode de travail.

La doctrine est **non exécutable**. Elle ne décide pas. Elle ne remplace pas X108. Elle ne bloque pas à la place d'une gate. Elle sert de référence pour détecter une confusion de rôle.

---

## 2. Core Authority Map

```
DÉCISION FINALE        → X108 uniquement
GUIDANCE / RAPPORT     → Sigma (recommande, ne décide pas)
CONSTRUCTION / PREUVE  → Obsidure (propose, ne décide pas)
RÉPONSE / NAVIGATION   → Brody (explique, ne décide pas)
MESURE / ÉCONOMIE      → OIE (mesure, ne décide pas)
MÉMOIRE / TRACE        → Trace causale (observe, non-souveraine)
```

**Aucune couche autre que X108 n'émet ACT, ALLOW ou BLOCK.**

---

## 3. Layer Roles

| Couche | Rôle principal | Type de sortie |
|---|---|---|
| **X108** | Décision finale souveraine | ALLOW / HOLD / BLOCK |
| **Sigma** | Guidance, introspection, rapport | SigmaGuidanceReport (recommandation) |
| **Obsidure** | Construction, preuve, mutation Lean sous protocole | ProposalReport (proposition) |
| **Brody** | Réponse, navigation, formulation | BrodyResponse (texte structuré) |
| **OIE** | Mesure de l'économie d'inférence | BenchmarkResult (mesure) |
| **Trace causale** | Observation du chemin de décision | CausalTrace (lecture seule) |
| **Mémoire** | Contexte persistant readonly | ContextPack (lecture seule) |
| **Protocoles** | Standardisation du travail | Référence non exécutable |
| **Gates** | Vérification des limites | PASS / FAIL (exit 0/1) |

---

## 4. Allowed / Forbidden by Layer

### X108
| Autorisé | Interdit |
|---|---|
| Émettre ALLOW / HOLD / BLOCK | Déléguer la décision finale à une autre couche |
| Recevoir des rapports Sigma, Obsidure, OIE | Exécuter automatiquement sans trace |
| Définir l'autorité de décision | Modifier Sigma Core ou Obsidure sans protocole |

### Sigma
| Autorisé | Interdit |
|---|---|
| Recommander HOLD_RECOMMENDED, STOP_UNKNOWN, REQUEST_PROOF, RELAUNCH_LAYER | Émettre ACT, ALLOW, BLOCK |
| Produire `SigmaGuidanceReport` | Décider à la place de X108 |
| Relancer une couche sous condition | Écrire en mémoire |
| Inspecter les couches en mode readonly | Modifier Kernel, X108, Sigma Core |

### Obsidure
| Autorisé | Interdit |
|---|---|
| Proposer un théorème Lean sous protocole OBSIDURE_APPLY_PROTOCOL | Écrire `sorry`, `admit`, `axiom`, `unsafe` |
| Produire un rapport de proposition pour approbation KX108 | Décider de l'approbation d'un théorème |
| Utiliser les 4 stratégies génératives (BOUNDARY, CODE_SURVEILLANCE, MEMORY_INVARIANT, DOMAIN_KERNEL_INVARIANT) | Modifier `proofs/lean/Obsidia/Basic.lean`, `TemporalKernel.lean`, `merkle_seal.json` |
| Vérifier via `lake env lean` | Appliquer un théorème sans approbation humaine |

### Brody
| Autorisé | Interdit |
|---|---|
| Formuler et structurer une réponse | Décider d'une action (ACT) |
| Naviguer entre les domaines | Écrire en mémoire canonique |
| Synthétiser des rapports en langage naturel | Modifier Kernel, X108, Sigma Core |
| Consulter le contexte de session (readonly) | Créer une autonomie de réponse non supervisée |

### OIE (Obsidia Inference Economy)
| Autorisé | Interdit |
|---|---|
| Mesurer les métriques d'inférence | Décider de la route de production |
| Comparer des benchmarks | Modifier les routes en fonction des résultats |
| Produire des rapports dans `docs/audits/` | Prendre une décision sans validation humaine |

### Mémoire / Trace Causale
| Autorisé | Interdit |
|---|---|
| Fournir un contexte readonly aux couches | Écrire sans protocole explicite |
| Observer le chemin de décision | Se substituer à X108 |
| Indexer des artefacts approuvés | Modifier Kernel ou Sigma Core |

---

## 5. Sigma Non-Sovereignty

Sigma est une couche d'**orientation**, pas de décision.

Les invariants de non-souveraineté Sigma sont immuables :

```
decision_authority = KX108_ONLY
readonly           = True
emits_act          = False
kernel_mutation    = False
```

**`HOLD_RECOMMENDED` est une recommandation Sigma.**
**`HOLD` est une décision X108.**

Ces deux termes ne doivent jamais être confondus. `HOLD_RECOMMENDED` ne produit aucun effet de blocage par lui-même — il informe X108 qui décide.

Les actions que Sigma ne peut **jamais** produire :

```
ACT, ALLOW, BLOCK, WRITE_MEMORY, MUTATE_KERNEL, AUTO_APPLY
```

Référence code : `sigma/sigma_guidance.py` — `FORBIDDEN_ACTIONS`.

---

## 6. X108 Authority

X108 est la **seule** autorité de décision finale dans l'architecture Obsidia.

Règles absolues :

- Toute décision de production (ACT / ALLOW / BLOCK) passe par X108.
- Aucune couche ne peut contourner X108 en émettant directement une action.
- Les gates CI (`check_protected_files.py`, `.github/workflows/x108-periphery-ci.yml`) protègent X108 Core — elles ne remplacent pas X108.
- Les protocoles de ce répertoire ne constituent pas une autorité X108.
- `X108Gate.ALLOW`, `X108Gate.HOLD`, `X108Gate.BLOCK` sont des décisions X108 — référence : `sigma/contracts.py`.

---

## 7. Obsidure Build Role

Obsidure est la couche de **construction formelle**.

Séquence doctrinale :

```
Obsidure PROPOSE → Lean VÉRIFIE → KX108 DÉCIDE
```

Claude orchestre. Obsidure propose. Lean vérifie. KX108 décide. **Claude n'écrit jamais de contenu Lean directement.**

Référence protocole : `docs/protocols/OBSIDURE_APPLY_PROTOCOL.md` (à venir — Apply 2).

Invariants de construction :

- Zéro `sorry` / `admit` / `axiom` / `unsafe`.
- Chaque théorème est dans un namespace isolé.
- L'agrégateur `GeneratedPeripheral.lean` est la seule entrée d'un théorème officialisé.
- Le manifest `proofs/LEAN_PROOF_SURFACE_MANIFEST.json` est l'autorité de référence.

---

## 8. Brody Response Role

Brody est la couche de **formulation et de navigation**.

Brody :
- lit les rapports des autres couches,
- formule des réponses en langage naturel ou structuré,
- navigue entre domaines et contextes,
- ne décide pas,
- ne bloque pas,
- n'émet pas d'ACT.

Brody peut suggérer une action à l'opérateur. Seul l'opérateur (KX108 humain) valide.

La mémoire Brody est **readonly** — invariant absolu : `memory_write=False`, aucune exception.

---

## 9. Causal Trace / OIE / Path / Domain Relation

```
Domain (bank/trading/gps/ecom)
  ↓ input
Path (route sélectionnée par Sigma)
  ↓ exécution
OIE (mesure du coût d'inférence de cette exécution)
  ↓ rapport
Causal Trace (enregistrement du chemin complet)
  ↓ lecture seule
X108 (décision finale sur base du rapport)
```

- OIE mesure, ne décide pas.
- La trace causale observe, ne décide pas.
- Le Path est une route — pas une décision.
- Le domaine fournit l'état — pas l'autorité.

---

## 10. Stop Conditions

Un opérateur **doit s'arrêter** si :

| Condition | Raison |
|---|---|
| `staged != 0` avant un APPLY | Risque de contamination du commit |
| Un fichier protégé est dans le scope d'un APPLY | Violation de boundary Kernel/X108/Lean |
| `Sigma recommande STOP_UNKNOWN` | Aucune couche disponible pour relancer utilement |
| `required_human_authorized_template = True` non approuvé | Action nécessitant approbation humaine |
| `x108_required = True` non transmis à X108 | Escalade obligatoire |
| `lake env lean` échoue sur un fichier candidat | Théorème invalide — ne pas officialiser |
| Un verifier retourne exit 1 | Ne pas commit avant résolution |
| `git diff --check` retourne des erreurs | Whitespace/encoding non conforme |

---

## 11. Commit Doctrine

Un commit est autorisé si et seulement si :

1. `staged = 0` avant l'APPLY (confirmé en PHASE 0).
2. Tous les checks du `OBSIDIA_VERIFICATION_LOOP_PROTOCOL` passent.
3. Le scope du commit correspond exactement aux fichiers autorisés.
4. Aucun fichier PRE_EXISTING_DIRTY n'est stagé.
5. Aucun fichier protégé n'est dans le diff.
6. Message de commit au format `<type>(<scope>): <description>` (50 car max sujet).

Types autorisés : `feat`, `fix`, `test`, `proof`, `agent`, `docs`, `chore`.

Un commit ne doit jamais être amendé pour contourner un hook.

---

## 12. Forbidden Confusions

Ces confusions sont des erreurs doctrinales — les corriger immédiatement si détectées :

| Confusion | Correction |
|---|---|
| Sigma émet ALLOW → décision prise | Sigma émet uniquement des recommandations. X108 décide. |
| HOLD_RECOMMENDED = blocage réel | HOLD_RECOMMENDED est une recommandation. HOLD est la décision X108. |
| Un protocole remplace X108 | Un protocole standardise le travail — il ne décide pas. |
| Une gate est une décision souveraine | Une gate retourne PASS/FAIL (exit 0/1). Elle ne remplace pas X108. |
| Obsidure décide si un théorème est valide | Lean vérifie. KX108 décide. Obsidure propose seulement. |
| Brody mémorise une décision | `memory_write=False` — invariant absolu, aucune exception. |
| OIE optimise la route de production | OIE mesure. L'opérateur décide du changement de route. |
| L'outillage externe (Claude, IDE) fait partie de l'architecture Obsidia | L'architecture Obsidia est dans le repo. L'outillage est externe et non souverain. |
| Un preflight peut modifier des fichiers | Un preflight est READ_ONLY. Toujours. |
| Un APPLY peut être auto-committé | Aucun auto-commit. L'opérateur valide et commite. |
