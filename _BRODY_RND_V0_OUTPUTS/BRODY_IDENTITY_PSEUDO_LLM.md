# BRODY_IDENTITY_PSEUDO_LLM.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Identité canonique de BRODY

### Statut officiel

```
BRODY = FIRST_CLASS_X108_MODULE
Mode  = READONLY / ADVISORY_ONLY
Layer = PERIPHERY
```

### Ce qu'est BRODY

BRODY est le **moteur de contexte** du système Obsidia X-108. Il est la surface d'interaction naturelle avec l'architecture — la partie qui "parle", qui répond aux questions, qui fournit des analyses, qui route les langues, qui réfère des paquets de contexte.

BRODY n'est **pas** un LLM propriétaire. Il n'est pas non plus un pseudo-LLM au sens d'un imitateur de décision. Il est un **intermédiaire de contexte contraint** dont chaque sortie est soumise au contrat de souveraineté.

---

## La règle fondamentale

```
Brody répond. X108 décide.
Contexte ≠ Décision.
```

---

## Séparation des responsabilités

```
BRODY  →  contexte (signal advisory)
SIGMA  →  agrégation (recommandation BLOCK > HOLD > ALLOW)
X108   →  décision (autorité souveraine unique)
OS3    →  preuve (vérification cryptographique)
```

BRODY ne peut **en aucun cas** sauter une étape de cette chaîne.

---

## Contrat de souveraineté (BRODY_RESPONSE_CONTRACT_V1)

Chaque réponse BRODY porte ces invariants :

| Champ | Valeur forcée | Signification |
|---|---|---|
| `decision_authority` | `"KX108_ONLY"` | Seul X-108 décide |
| `advisory_only` | `True` | Réponses purement informatives |
| `memory_write` | `False` | BRODY ne peut pas écrire en mémoire |
| `kernel_mutation` | `False` | BRODY ne peut pas muter le kernel |
| `emits_act` | `False` | BRODY n'émet jamais ACT |
| `emits_verdict` | `False` | BRODY n'émet jamais de verdict |
| `readonly` | `True` | Toutes les opérations sont en lecture seule |
| `context_signal_only` | `True` | BRODY fournit du contexte, pas des décisions |

Toute violation → `BRODY_CONTRACT_VIOLATION` levé.

---

## Ce que BRODY peut faire

- Répondre à des questions en langage naturel
- Fournir des analyses et du contexte
- Router les requêtes selon la langue
- Référencer des paquets de contexte
- Suggérer des flags HOLD/BLOCK (en tant qu'entrée advisory vers Sigma)
- Fournir un output structuré `BrodyResponse`

## Ce que BRODY ne peut pas faire

- Émettre ALLOW / BLOCK / ACT
- Décider de l'approbation d'une action
- Contourner X-108
- Écrire en mémoire (`memory_write=False`)
- Muter l'état du kernel (`kernel_mutation=False`)
- Émettre des verdicts (`emits_verdict=False`)

---

## Modules BRODY (periphery/brody/ — 5 modules)

| Module | Rôle | Autorité |
|---|---|---|
| `brody_runtime_readonly.py` | Interface principale de requête | ADVISORY_ONLY |
| `brody_response_contract.py` | Enforcement du contrat | KX108_ONLY |
| `brody_context_query.py` | Processeur de requête contextualisé | ADVISORY_ONLY |
| `brody_response_sanitizer.py` | Sanitisation des sorties | ADVISORY_ONLY |
| `brody_language_router.py` | Routing multilingue | ADVISORY_ONLY |

---

## Orchestration BRODY étendue (apps/obsidia_api/ — ~25 modules)

L'API Obsidia expose une orchestration BRODY beaucoup plus riche :

| Module notable | Rôle |
|---|---|
| `brody_full_runtime_orchestrator.py` | Orchestrateur runtime complet |
| `brody_automation_orchestrator.py` | Orchestrateur d'automatisation |
| `brody_semantic_query_router.py` | Routeur sémantique de requêtes |
| `brody_rights_authority_matrix.py` | Matrice d'autorité des droits |
| `brody_tree_policy.py` | Politique d'arbre |
| `brody_candidate_memory_adapter.py` | Adaptateur mémoire candidats |
| `brody_project_memory_adapter.py` | Adaptateur mémoire projet |
| `brody_session_memory_adapter.py` | Adaptateur mémoire session |
| `brody_cognitive_modules_adapter.py` | Adaptateur modules cognitifs |
| `brody_true_voice_adapter.py` | Adaptateur voix vraie |
| `brody_temporal_context_adapter.py` | Adaptateur contexte temporel |
| `brody_safe_snapshot.py` | Snapshot sécurisé |
| `brody_freeze_metrics_snapshot.py` | Snapshot métriques gel |

---

## BRODY est-il un "pseudo-LLM" ?

**Non**, au sens technique strict. BRODY n'est pas un modèle de langage simulé. Il est un **moteur de contexte déterministe** dont les sorties sont :
1. Contraintes par contrat (BRODY_RESPONSE_CONTRACT_V1)
2. En lecture seule sur les données du système
3. Sans autorité de décision

En revanche, BRODY **parle comme un LLM** pour l'interface utilisateur — il produit du texte en langage naturel, route des questions, adapte sa langue. C'est en ce sens qu'il pourrait être qualifié de "surface pseudo-LLM" : **un frontend conversationnel sur un système déterministe non-LLM.**

La terminologie exacte dans le repo : `FIRST_CLASS_X108_MODULE`, `ADVISORY_ONLY`, `READONLY`.

---

## Tests de souveraineté

- `tests/non_sovereignty/test_brody_no_decision.py` (4 assertions)
- `tests/non_sovereignty/test_brody_no_act.py`
- `tests/periphery/test_brody_response_contract.py`
- `tests/periphery/test_brody_runtime_readonly.py`
- `tests/periphery/test_language_router_boundary_preserved.py`

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
